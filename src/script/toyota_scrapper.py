#!/usr/bin/env python3
"""
Red Deer Toyota Used Inventory Scraper
Strategy 1: Hit the dealer's hidden JSON API (no Cloudflare on API endpoints)
Strategy 2: Playwright headless browser fallback (works on residential IPs)

HOW TO FIND THE JSON API (one-time setup):
  1. Open Chrome and go to https://www.reddeertoyota.com/inventory/used/
  2. Press F12 → Network tab → click "Fetch/XHR" filter
  3. Reload the page and watch for requests that return JSON vehicle data
  4. Copy that URL and set it as JSON_API_URL below (or set env var TOYOTA_API_URL)
"""

import csv, time, re, logging, os, json
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------
# SET THIS after finding the API URL with Chrome DevTools (see above).
# Leave as empty string to run auto-discovery first.
# Can also be set via environment variable: TOYOTA_API_URL
# -----------------------------------------------------------------------
JSON_API_URL = os.environ.get("TOYOTA_API_URL", "")

import requests
from bs4 import BeautifulSoup

SESSION = requests.Session()
SESSION.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/html, */*',
    'Accept-Language': 'en-US,en;q=0.9',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'https://www.reddeertoyota.com/inventory/used/',
})

BASE = "https://www.reddeertoyota.com"
TARGET = "https://www.reddeertoyota.com/inventory/used/"

CAR_MAKES = {
    'Toyota': {'Camry','RAV4','Highlander','Prius','Corolla','Corolla Cross','Tacoma',
               'Tundra','Sienna','4Runner','Sequoia','Avalon','C-HR','Venza',
               'Land Cruiser','GR86','Supra','Yaris','Matrix','Crown'},
    'Honda': {'Civic','Accord','CR-V','HR-V','Pilot','Odyssey','Fit','Ridgeline','Passport'},
    'Ford': {'F-150','F-250','F-350','Escape','Explorer','Expedition','Edge',
             'Fusion','Mustang','Bronco','Bronco Sport','Ranger','Maverick'},
    'Chevrolet': {'Silverado','Silverado 1500','Silverado 2500','Tahoe','Suburban',
                  'Equinox','Traverse','Malibu','Camaro','Colorado','Blazer'},
    'GMC': {'Sierra','Sierra 1500','Sierra 2500','Yukon','Acadia','Terrain','Canyon'},
    'Dodge': {'Charger','Challenger','Journey','Durango','Grand Caravan','Hornet'},
    'Ram': {'1500','2500','3500','ProMaster'},
    'Nissan': {'Altima','Sentra','Rogue','Murano','Pathfinder','Frontier','Titan','370Z'},
    'Hyundai': {'Elantra','Sonata','Tucson','Santa Fe','Palisade','Kona'},
    'Kia': {'Forte','Sportage','Sorento','Telluride','Soul','Seltos'},
    'Mazda': {'Mazda3','Mazda6','CX-3','CX-5','CX-9','CX-30','CX-50'},
    'Subaru': {'Outback','Forester','Impreza','Legacy','Crosstrek','Ascent'},
    'Jeep': {'Wrangler','Grand Cherokee','Cherokee','Compass','Gladiator'},
    'Acura': {'MDX','RDX','TLX','ILX'},
    'Cadillac': {'XT4','XT5','XT6','Escalade'},
    'Buick': {'Enclave','Encore','Encore GX','Envision'},
    'Chrysler': {'300','Pacifica','Voyager'},
    'Scion': {'tC','xB','iA','iM','FR-S'},
    'Volkswagen': {'Jetta','Passat','Golf','Tiguan','Atlas','GTI'},
    'Audi': {'A3','A4','A6','Q3','Q5','Q7','Q8'},
    'Lincoln': {'Navigator','Aviator','Corsair','Nautilus'},
    'Gmc': {'Terrain'},
}

TRIM_PATTERNS = {
    'Capstone':r'\bCapstone\b','Platinum':r'\bPlatinum\b','Limited':r'\bLimited\b',
    'XLE':r'\bXLE\b','XSE':r'\bXSE\b','LE':r'\bLE\b(?!\w)','SE':r'\bSE\b(?!\w)',
    'TRD Pro':r'\bTRD\s+Pro\b','TRD Off-Road':r'\bTRD\s+Off-?Road\b',
    'TRD Sport':r'\bTRD\s+Sport\b','TRD':r'\bTRD\b','SR5':r'\bSR5\b',
    'SR':r'\bSR\b(?!\d)','Hybrid':r'\bHybrid\b','Prime':r'\bPrime\b',
    'Touring':r'\bTouring\b','EX-L':r'\bEX-L\b','EX':r'\bEX\b(?!\w)',
    'LX':r'\bLX\b(?!\w)','Raptor':r'\bRaptor\b','King Ranch':r'\bKing\s+Ranch\b',
    'Lariat':r'\bLariat\b','XLT':r'\bXLT\b','XL':r'\bXL\b(?!\w)',
    'Tremor':r'\bTremor\b','ST':r'\bST\b(?!\w)','GT':r'\bGT\b(?!\w)',
    'Hellcat':r'\bHellcat\b','SRT':r'\bSRT\b','Scat Pack':r'\bScat\s+Pack\b',
    'R/T':r'\bR/T\b','SXT':r'\bSXT\b','TRX':r'\bTRX\b','Rebel':r'\bRebel\b',
    'Laramie':r'\bLaramie\b','Big Horn':r'\bBig\s+Horn\b',
    'High Country':r'\bHigh\s+Country\b','LTZ':r'\bLTZ\b','LT':r'\bLT\b(?!\w)',
    'LS':r'\bLS\b(?!\w)','Z71':r'\bZ71\b','Denali':r'\bDenali\b',
    'AT4':r'\bAT4\b','SLT':r'\bSLT\b','SLE':r'\bSLE\b',
    'Pro-4X':r'\bPro-4X\b','Nismo':r'\bNismo\b','SL':r'\bSL\b(?!\w)',
    'SV':r'\bSV\b','Calligraphy':r'\bCalligraphy\b','Ultimate':r'\bUltimate\b',
    'Preferred':r'\bPreferred\b','N Line':r'\bN\s+Line\b',
    'Rubicon':r'\bRubicon\b','Sahara':r'\bSahara\b','Overland':r'\bOverland\b',
    'Sport':r'\bSport\b(?!\s+Utility)','AWD':r'\bAWD\b','4WD':r'\b4WD\b',
    'Essential':r'\bEssential\b','IVT':r'\bIVT\b',
}

# Common dealer platform API URL patterns to auto-discover
API_CANDIDATES = [
    # Dealer.com / Cox Automotive
    "/apis/widget/INVENTORY_LISTING_DEFAULT_AUTO_USED:inventory-data-bus1/getInventory",
    "/apis/widget/INVENTORY_LISTING_DEFAULT_AUTO_USED:inventory-data-bus1/getInventory?pageSize=100",
    "/apis/widget/INVENTORY_LISTING_DEFAULT_AUTO_ALL:inventory-data-bus1/getInventory?condition=used",
    # Generic REST patterns
    "/api/inventory/listings?condition=used&pageSize=100",
    "/api/inventory/search?condition=used",
    "/api/vehicles/used",
    "/inventory/api/used",
    "/inventory/used.json",
    "/_api/inventory?type=used",
    "/ajax/inventory?condition=used",
    # DealerSocket
    "/inventory/listing?type=used&format=json",
    "/inventory/search?format=json&type=used",
    # CDK / FortellaMedia
    "/vehicle/search?condition=used&format=json",
    "/api/search/vehicle?condition=used",
    # Autotrader/vAuto integrations
    "/api/srp/vehicles?condition=used",
    "/api/srp/listings?condition=used",
    # Toyota-specific platforms
    "/toyota/inventory/used",
    "/api/toyota/inventory?condition=used",
]


# -----------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------

def extract_make_model(text):
    text = re.sub(r'\s+', ' ', text.strip())
    for make, models in CAR_MAKES.items():
        if re.search(r'\b{}\b'.format(re.escape(make)), text, re.IGNORECASE):
            for model in sorted(models, key=len, reverse=True):
                if re.search(r'\b{}\b'.format(re.escape(model)), text, re.IGNORECASE):
                    return make, model
    return None, None


def extract_trim(text, model):
    for trim_name, pattern in TRIM_PATTERNS.items():
        if re.search(pattern, text, re.IGNORECASE):
            if model and trim_name.lower() not in model.lower():
                return trim_name
            elif not model:
                return trim_name
    return ''


def extract_prices_from_text(text):
    prices = []
    for m in re.finditer(r'\$\s*([0-9,]{4,})', text):
        try:
            p = int(m.group(1).replace(',',''))
            if 3000 <= p <= 300000:
                ctx = text[max(0,m.start()-80):m.end()+80].lower()
                prices.append({
                    'price': p,
                    'is_sale': any(k in ctx for k in ['sale','internet','special','now','reduced']),
                    'is_msrp': any(k in ctx for k in ['msrp','was','original','regular','list']),
                })
        except Exception:
            pass
    if not prices:
        return None, None
    deduped = {}
    for p in prices:
        if p['price'] not in deduped or p['is_sale'] or p['is_msrp']:
            deduped[p['price']] = p
    prices = list(deduped.values())
    msrp = [p['price'] for p in prices if p['is_msrp']]
    sale = [p['price'] for p in prices if p['is_sale']]
    if msrp and sale:
        reg, sal = max(msrp), min(sale)
    elif len(prices) >= 2:
        sp = sorted([p['price'] for p in prices], reverse=True)
        reg, sal = sp[0], (sp[1] if sp[1] < sp[0] else None)
    else:
        reg, sal = prices[0]['price'], None
    if reg and sal and sal >= reg:
        sal = None
    return reg, sal


def vehicle_from_json(item):
    """Map a JSON object from the dealer API to our standard vehicle dict."""
    v = {'makeName':'','year':'','model':'','sub-model':'','trim':'',
         'mileage':'','value':'','sale_value':'','stock_number':'','engine':''}

    # Try common field names used across dealer platforms
    field_map = {
        'makeName':   ['make','makeName','Make','manufacturer'],
        'year':       ['year','modelYear','Year','yr'],
        'model':      ['model','modelName','Model'],
        'trim':       ['trim','trimName','Trim','trimLevel','subModel'],
        'mileage':    ['mileage','odometer','miles','km','Mileage','Odometer'],
        'value':      ['price','listPrice','retailPrice','msrp','Price','salePrice',
                       'internetPrice','sellingPrice','askingPrice'],
        'sale_value': ['salePrice','internetPrice','specialPrice','discountPrice',
                       'webPrice','ourPrice'],
        'stock_number':['stockNumber','stock','stockNum','StockNumber','vin'],
        'engine':     ['engine','engineDescription','engineSize'],
    }

    for our_key, candidates in field_map.items():
        for c in candidates:
            val = item.get(c) or item.get(c.lower()) or item.get(c.upper())
            if val:
                v[our_key] = str(val).strip()
                break

    # Ensure sale < regular
    if v['value'] and v['sale_value']:
        try:
            if int(re.sub(r'[^\d]','',v['sale_value'])) >= int(re.sub(r'[^\d]','',v['value'])):
                v['sale_value'] = ''
        except Exception:
            pass

    v['sub-model'] = v['trim']
    return v


def parse_html_element(element, idx=0):
    v = {'makeName':'','year':'','model':'','sub-model':'','trim':'',
         'mileage':'','value':'','sale_value':'','stock_number':'','engine':''}
    try:
        text = re.sub(r'\s+', ' ', element.get_text(separator=' ', strip=True))
        m = re.search(r'\b(19[89]\d|20[0-2]\d)\b', text)
        if m: v['year'] = m.group(1)
        make, model = extract_make_model(text)
        if make: v['makeName'] = make
        if model: v['model'] = model
        trim = extract_trim(text, model)
        if trim: v['trim'] = trim; v['sub-model'] = trim
        for pat in [r'Stock[#:\s]*([A-Z0-9]{3,15})\b', r'#\s*([A-Z0-9]{3,15})\b']:
            m2 = re.search(pat, text, re.IGNORECASE)
            if m2 and m2.group(1).isalnum() and len(m2.group(1)) >= 3:
                v['stock_number'] = m2.group(1); break
        reg, sal = extract_prices_from_text(text)
        if reg: v['value'] = str(reg)
        if sal: v['sale_value'] = str(sal)
        for pat in [r'(\d{1,3}(?:,\d{3})*)\s*(?:km|kilometers?)\b',
                    r'(\d{1,3}(?:,\d{3})*)\s*(?:miles?|mi)\b']:
            m3 = re.search(pat, text, re.IGNORECASE)
            if m3:
                val = m3.group(1).replace(',','')
                if 0 <= int(val) <= 500000: v['mileage'] = val; break
        for pat in [r'(\d\.\d+L\s*(?:V?\d+|I\d+))',r'(\d\.\d+L\s*Hybrid)',r'(\d\.\d+L\s*Turbo)']:
            m4 = re.search(pat, text, re.IGNORECASE)
            if m4: v['engine'] = m4.group(1).strip(); break
    except Exception as e:
        logger.debug("HTML parse error {}: {}".format(idx, e))
    return v


def is_valid(v):
    if not (v.get('year','').strip() and v.get('makeName','').strip()):
        return False
    extras = ['model','value','sale_value','stock_number','mileage']
    return bool(v.get('model','').strip()) or sum(1 for f in extras if v.get(f,'').strip()) >= 2


def completeness(v):
    """Score a vehicle record by how complete it is (higher = better)."""
    fields = ['stock_number', 'mileage', 'engine', 'trim', 'value', 'sale_value']
    return sum(1 for f in fields if v.get(f, '').strip())


def dedup(vehicles):
    """
    Two-pass deduplication:
    Pass 1 — keep one entry per stock number (the most complete).
    Pass 2 — for entries without a stock number, drop them if a stocked entry
              already covers the same year+make+model+price combination.
    """
    # Pass 1: group by stock number, keep most complete per stock
    by_stock = {}   # stock -> best vehicle
    no_stock = []

    for v in vehicles:
        stock = v.get('stock_number', '').strip()
        if stock:
            if stock not in by_stock or completeness(v) > completeness(by_stock[stock]):
                by_stock[stock] = v
        else:
            no_stock.append(v)

    stocked = list(by_stock.values())

    # Build a lookup: (year, make, model, price) -> True for every stocked vehicle
    stocked_ymmp = set()
    for v in stocked:
        stocked_ymmp.add((
            v.get('year',''), v.get('makeName',''),
            v.get('model',''), v.get('value',''),
        ))

    # Pass 2: only keep no-stock entries that don't duplicate a stocked vehicle
    extra = []
    seen_extra = set()
    for v in no_stock:
        ymmp = (v.get('year',''), v.get('makeName',''), v.get('model',''), v.get('value',''))
        if ymmp in stocked_ymmp:
            continue          # a stocked entry already covers this
        if ymmp in seen_extra:
            continue          # duplicate within the no-stock group
        seen_extra.add(ymmp)
        extra.append(v)

    return stocked + extra


# -----------------------------------------------------------------------
# Strategy 1: JSON API
# -----------------------------------------------------------------------

def try_json_api(url):
    """Try fetching a JSON API endpoint. Returns list of vehicles or []."""
    try:
        resp = SESSION.get(url, timeout=15)
        if resp.status_code != 200:
            return []
        ct = resp.headers.get('Content-Type','')
        if 'json' not in ct and not resp.text.strip().startswith(('{','[')):
            return []
        data = resp.json()

        # Drill into common wrapper keys
        if isinstance(data, dict):
            for key in ['vehicles','inventory','listings','results','data',
                        'items','records','vehicles_list','vehicleList']:
                if key in data and isinstance(data[key], list):
                    data = data[key]
                    break
            if isinstance(data, dict):
                # Try one level deeper
                for v in data.values():
                    if isinstance(v, list) and len(v) > 0 and isinstance(v[0], dict):
                        data = v
                        break

        if not isinstance(data, list) or len(data) == 0:
            return []

        vehicles = []
        for item in data:
            if not isinstance(item, dict):
                continue
            v = vehicle_from_json(item)
            if is_valid(v):
                vehicles.append(v)

        logger.info("JSON API hit: {} — {} vehicles".format(url, len(vehicles)))
        return vehicles

    except Exception as e:
        logger.debug("JSON API failed {}: {}".format(url, e))
        return []


def discover_and_scrape_json():
    """Try the configured URL first, then auto-discover."""
    global JSON_API_URL

    if JSON_API_URL:
        vehicles = try_json_api(JSON_API_URL)
        if vehicles:
            return vehicles
        logger.warning("Configured JSON_API_URL returned no vehicles — trying auto-discovery")

    logger.info("Auto-discovering dealer JSON API ({} candidates)...".format(len(API_CANDIDATES)))
    for path in API_CANDIDATES:
        url = BASE + path
        vehicles = try_json_api(url)
        if vehicles:
            logger.info("SUCCESS: API found at {}".format(url))
            logger.info("TIP: Set TOYOTA_API_URL={} to skip discovery next time".format(url))
            return vehicles

    logger.info("No JSON API found via auto-discovery")
    return []


# -----------------------------------------------------------------------
# Strategy 2: HTML scraping (works from residential IPs / self-hosted runner)
# -----------------------------------------------------------------------

def scrape_html():
    all_vehicles = []
    page_num = 1

    logger.info("Falling back to HTML scraping (requires non-blocked IP)...")

    for page_num in range(1, 11):
        url = "{}?page={}".format(TARGET.rstrip('/'), page_num)
        try:
            resp = SESSION.get(url, timeout=30)
            if resp.status_code == 403:
                logger.error("403 Forbidden — this IP is blocked by Cloudflare.")
                logger.error("Run this scraper on your own machine or a self-hosted GitHub Actions runner.")
                break
            resp.raise_for_status()
        except Exception as e:
            logger.error("HTML fetch failed page {}: {}".format(page_num, e))
            break

        soup = BeautifulSoup(resp.content, 'html.parser')

        if page_num == 1:
            with open('debug_page1.html', 'w', encoding='utf-8') as f:
                f.write(soup.prettify())
            logger.info("Saved debug_page1.html")

        page_text = soup.get_text()
        if not re.search(r'\b(19[89]\d|20[0-2]\d)\b', page_text):
            break

        selectors = [
            '[data-vehicle-id]','[data-stock-number]','[data-vin]',
            '.vehicle-card','.inventory-item','.vehicle-listing',
            'article[class*="vehicle"]','div[class*="vehicle"]',
            'li[class*="vehicle"]','.vehicle','article','li[class*="item"]',
        ]

        page_vehicles, seen = [], set()
        for selector in selectors:
            elements = soup.select(selector)
            if not elements: continue
            count = 0
            for idx, el in enumerate(elements):
                eid = id(el)
                if eid in seen: continue
                v = parse_html_element(el, idx)
                if is_valid(v):
                    page_vehicles.append(v)
                    seen.add(eid)
                    count += 1
            if count:
                logger.info("Page {} selector '{}' — {} vehicles".format(page_num, selector, count))
                break

        if not page_vehicles:
            logger.info("No vehicles on page {} — stopping".format(page_num))
            break

        all_vehicles.extend(page_vehicles)
        time.sleep(1.0)

    return all_vehicles


# -----------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------

def save_csv(vehicles, path):
    fields = ['makeName','year','model','sub-model','trim','mileage',
              'value','sale_value','stock_number','engine']
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for v in vehicles:
            writer.writerow({field: v.get(field,'') for field in fields})
    logger.info("CSV saved: {} ({} rows)".format(path, len(vehicles)))


def print_results(vehicles):
    print("\n" + "="*100)
    print("RED DEER TOYOTA USED INVENTORY")
    print("="*100)
    if not vehicles:
        print("No vehicles found")
        return
    print("Found {} vehicles\n".format(len(vehicles)))
    brands = {}
    for v in vehicles:
        brands[v.get('makeName','Unknown')] = brands.get(v.get('makeName','Unknown'), 0) + 1
    for b, c in sorted(brands.items()):
        print("  {}: {}".format(b, c))
    sale_count = sum(1 for v in vehicles if v.get('sale_value'))
    print("\nWith sale prices: {}".format(sale_count))
    print("\n{:<10} {:<6} {:<16} {:<10} {:<12} {:<12} {:<10}".format(
        'Make','Year','Model','Trim','Value','Sale Price','Stock#'))
    print("-"*85)
    for v in vehicles:
        print("{:<10} {:<6} {:<16} {:<10} {:<12} {:<12} {:<10}".format(
            v.get('makeName','')[:9], v.get('year',''), v.get('model','')[:15],
            v.get('trim','')[:9], v.get('value','')[:11],
            v.get('sale_value','')[:11], v.get('stock_number','')[:9]))


def main():
    logger.info("="*80)
    logger.info("RED DEER TOYOTA SCRAPER")
    logger.info("="*80)

    # Strategy 1: JSON API (bypasses Cloudflare — works from any IP)
    vehicles = discover_and_scrape_json()

    # Strategy 2: HTML fallback (requires residential/self-hosted IP)
    if not vehicles:
        vehicles = scrape_html()

    vehicles = dedup(vehicles)
    logger.info("FINAL: {} unique vehicles".format(len(vehicles)))

    print_results(vehicles)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, '..', '..'))
    csv_path = os.path.join(project_root, 'public', 'data', 'inventory.csv')

    if vehicles:
        save_csv(vehicles, csv_path)
        print("\nCSV created: {}".format(csv_path))
    else:
        print("\nNo vehicles found.")
        print("\nNEXT STEPS — pick one:")
        print("  A) Find the JSON API: Open Chrome DevTools → Network → XHR/Fetch")
        print("     while loading https://www.reddeertoyota.com/inventory/used/")
        print("     Set the API URL as TOYOTA_API_URL env var in GitHub secrets.")
        print("")
        print("  B) Self-hosted runner: Run the GitHub Action on your own PC.")
        print("     See .github/workflows/daily-scrape.yml for instructions.")
        if os.path.exists(csv_path):
            os.remove(csv_path)

    return 0 if vehicles else 1


if __name__ == "__main__":
    exit(main())
