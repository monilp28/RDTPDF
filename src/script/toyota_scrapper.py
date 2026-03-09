#!/usr/bin/env python3
"""
Red Deer Toyota Used Inventory Scraper
Uses Playwright (real Chromium) to bypass Cloudflare JS challenges.
"""

import csv
import time
import re
import logging
import os
import json
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
except ImportError:
    raise SystemExit(
        "Missing dependency: pip install playwright && playwright install chromium\n"
        "Add 'playwright' to requirements.txt and the install step to your workflow."
    )

from bs4 import BeautifulSoup


TARGET_URL = "https://www.reddeertoyota.com/inventory/used/"

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
    'Nightshade':r'\bNightshade\b','Trail':r'\bTrail\b(?!\w)',
    'Touring':r'\bTouring\b','EX-L':r'\bEX-L\b','EX':r'\bEX\b(?!\w)',
    'LX':r'\bLX\b(?!\w)','TrailSport':r'\bTrailSport\b','Elite':r'\bElite\b',
    'Raptor':r'\bRaptor\b','King Ranch':r'\bKing\s+Ranch\b',
    'Lariat':r'\bLariat\b','XLT':r'\bXLT\b','XL':r'\bXL\b(?!\w)',
    'Tremor':r'\bTremor\b','Wildtrak':r'\bWildtrak\b',
    'ST':r'\bST\b(?!\w)','GT':r'\bGT\b(?!\w)','Shelby':r'\bShelby\b',
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
    'Summit':r'\bSummit\b','Sport':r'\bSport\b(?!\s+Utility)',
    'AWD':r'\bAWD\b','4WD':r'\b4WD\b','Essential':r'\bEssential\b','IVT':r'\bIVT\b',
}


# ---------------------------------------------------------------------------
# Extraction helpers (pure Python, no network)
# ---------------------------------------------------------------------------

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


def extract_prices(element):
    """Return (regular_price, sale_price) as ints or None."""
    all_prices = []

    # data attributes
    for attr, value in element.attrs.items():
        al = attr.lower()
        if 'price' not in al and 'msrp' not in al:
            continue
        m = re.search(r'(\d{4,6})', str(value))
        if m:
            p = int(m.group(1))
            if 3000 <= p <= 300000:
                is_sale = any(k in al for k in ['sale','internet','special'])
                is_msrp = any(k in al for k in ['msrp','original','regular'])
                all_prices.append({'price': p, 'is_sale': is_sale, 'is_msrp': is_msrp})

    # JSON-LD
    for script in element.find_all('script', type='application/ld+json'):
        try:
            data = json.loads(script.string or '')
            for key in ['price']:
                if key in data:
                    p = float(data[key])
                    if 3000 <= p <= 300000:
                        all_prices.append({'price': int(p), 'is_sale': False, 'is_msrp': True})
            if 'offers' in data and isinstance(data['offers'], dict):
                p = float(data['offers'].get('price', 0))
                if 3000 <= p <= 300000:
                    all_prices.append({'price': int(p), 'is_sale': False, 'is_msrp': True})
        except Exception:
            pass

    # price-class elements
    for el in element.find_all(class_=re.compile(r'(price|cost|amount)', re.I)):
        el_text = el.get_text(strip=True)
        ctx = (el_text + ' ' + ' '.join(el.get('class', []))).lower()
        for ps in re.findall(r'\$?\s*([0-9]{1,3}(?:,\d{3})*)', el_text):
            try:
                p = int(ps.replace(',', ''))
                if 3000 <= p <= 300000:
                    is_sale = any(k in ctx for k in ['sale','special','internet','now','reduced','discount'])
                    is_msrp = any(k in ctx for k in ['msrp','was','original','regular','list','retail'])
                    has_strike = 'line-through' in el.get('style','') or bool(el.find(['s','strike','del']))
                    all_prices.append({'price': p, 'is_sale': is_sale, 'is_msrp': is_msrp or has_strike})
            except Exception:
                pass

    # raw text fallback
    if not all_prices:
        raw = element.get_text(separator=' ', strip=True)
        for m in re.finditer(r'\$\s*([0-9,]{4,})', raw):
            try:
                p = int(m.group(1).replace(',', ''))
                if 3000 <= p <= 300000:
                    ctx = raw[max(0, m.start()-80):m.end()+80].lower()
                    all_prices.append({
                        'price': p,
                        'is_sale': any(k in ctx for k in ['sale','internet','special','now']),
                        'is_msrp': any(k in ctx for k in ['msrp','was','original']),
                    })
            except Exception:
                pass

    if not all_prices:
        return None, None

    # deduplicate
    deduped = {}
    for p in all_prices:
        if p['price'] not in deduped or p['is_sale'] or p['is_msrp']:
            deduped[p['price']] = p
    prices = list(deduped.values())

    msrp  = [p['price'] for p in prices if p['is_msrp']]
    sale  = [p['price'] for p in prices if p['is_sale']]

    if msrp and sale:
        reg, sal = max(msrp), min(sale)
    elif len(prices) >= 2:
        sp = sorted([p['price'] for p in prices], reverse=True)
        reg, sal = sp[0], sp[1] if sp[1] < sp[0] else None
    else:
        reg, sal = prices[0]['price'], None

    if reg and sal and sal >= reg:
        sal = None

    return reg, sal


def parse_vehicle(element, idx=0):
    v = {
        'makeName':'','year':'','model':'','sub-model':'','trim':'',
        'mileage':'','value':'','sale_value':'','stock_number':'','engine':''
    }
    try:
        text = re.sub(r'\s+', ' ', element.get_text(separator=' ', strip=True))

        m = re.search(r'\b(19[89]\d|20[0-2]\d)\b', text)
        if m: v['year'] = m.group(1)

        make, model = extract_make_model(text)
        if make: v['makeName'] = make
        if model: v['model'] = model

        trim = extract_trim(text, model)
        if trim:
            v['trim'] = trim
            v['sub-model'] = trim

        for pat in [r'Stock[#:\s]*([A-Z0-9]{3,15})\b', r'#\s*([A-Z0-9]{3,15})\b']:
            m = re.search(pat, text, re.IGNORECASE)
            if m and m.group(1).isalnum() and len(m.group(1)) >= 3:
                v['stock_number'] = m.group(1)
                break

        reg, sal = extract_prices(element)
        if reg: v['value'] = str(reg)
        if sal: v['sale_value'] = str(sal)

        for pat in [r'(\d{1,3}(?:,\d{3})*)\s*(?:km|kilometers?)\b',
                    r'(\d{1,3}(?:,\d{3})*)\s*(?:miles?|mi)\b']:
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                val = m.group(1).replace(',','')
                if 0 <= int(val) <= 500000:
                    v['mileage'] = val
                    break

        for pat in [r'(\d\.\d+L\s*(?:V?\d+|I\d+))',r'(\d\.\d+L\s*Hybrid)',r'(\d\.\d+L\s*Turbo)']:
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                v['engine'] = m.group(1).strip()
                break

        # data-* attributes
        for attr, value in element.attrs.items():
            if 'data-' not in attr.lower(): continue
            al, vs = attr.lower(), str(value)
            if 'year' in al and not v['year'] and re.match(r'^(19[89]\d|20[0-2]\d)$', vs):
                v['year'] = vs
            elif 'make' in al and not v['makeName']:
                v['makeName'] = vs.title()
            elif 'model' in al and not v['model']:
                v['model'] = vs
            elif 'mileage' in al and not v['mileage']:
                clean = re.sub(r'[^\d]','',vs)
                if clean: v['mileage'] = clean

    except Exception as e:
        logger.debug("parse_vehicle error at {}: {}".format(idx, e))
    return v


def is_valid(v):
    if not (v.get('year','').strip() and v.get('makeName','').strip()):
        return False
    extras = ['model','value','sale_value','stock_number','mileage']
    return bool(v.get('model','').strip()) or sum(1 for f in extras if v.get(f,'').strip()) >= 2


def find_vehicles(html):
    soup = BeautifulSoup(html, 'html.parser')
    vehicles, seen = [], set()

    selectors = [
        '[data-vehicle-id]','[data-stock-number]','[data-vin]',
        '.vehicle-card','.inventory-item','.vehicle-listing',
        'article[class*="vehicle"]','div[class*="vehicle"]',
        'li[class*="vehicle"]','.vehicle','article','li[class*="item"]',
    ]
    for selector in selectors:
        elements = soup.select(selector)
        if not elements: continue
        count = 0
        for idx, el in enumerate(elements):
            eid = id(el)
            if eid in seen: continue
            v = parse_vehicle(el, idx)
            if is_valid(v):
                vehicles.append(v)
                seen.add(eid)
                count += 1
        if count:
            logger.info("Selector '{}' yielded {} vehicles".format(selector, count))
            return vehicles

    # broad fallback
    for idx, div in enumerate(soup.find_all(['div','section','article','li'])):
        eid = id(div)
        if eid in seen: continue
        txt = div.get_text(separator=' ', strip=True)
        if not re.search(r'\b(19[89]\d|20[0-2]\d)\b', txt): continue
        for make in CAR_MAKES:
            if re.search(r'\b' + re.escape(make) + r'\b', txt, re.IGNORECASE):
                v = parse_vehicle(div, idx)
                if is_valid(v):
                    vehicles.append(v)
                    seen.add(eid)
                break

    return vehicles


# ---------------------------------------------------------------------------
# Playwright scraper
# ---------------------------------------------------------------------------

def scrape_with_playwright():
    all_vehicles = []

    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-blink-features=AutomationControlled',
            ],
        )

        context = browser.new_context(
            user_agent=(
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/131.0.0.0 Safari/537.36'
            ),
            viewport={'width': 1366, 'height': 768},
            locale='en-US',
            timezone_id='America/Denver',
            # Tell the site JS that we are NOT a webdriver
            java_script_enabled=True,
        )

        # Mask automation signals in JS
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            Object.defineProperty(navigator, 'plugins', { get: () => [1,2,3,4,5] });
            Object.defineProperty(navigator, 'languages', { get: () => ['en-US','en'] });
            window.chrome = { runtime: {} };
        """)

        page = context.new_page()
        page_num = 1
        max_pages = 10

        while page_num <= max_pages:
            url = "{}?page={}".format(TARGET_URL.rstrip('/'), page_num)
            logger.info("Navigating to: {}".format(url))

            try:
                resp = page.goto(url, wait_until='domcontentloaded', timeout=45000)
                status = resp.status if resp else 0
                logger.info("HTTP status: {}".format(status))

                if status == 403:
                    logger.error("403 — Cloudflare is blocking this IP/environment")
                    break

                # Wait for inventory content to appear (JS-rendered pages)
                try:
                    page.wait_for_selector(
                        ', '.join([
                            '.vehicle-card', '.inventory-item', '.vehicle-listing',
                            '[data-vehicle-id]', 'article', '.srp-list-item',
                        ]),
                        timeout=15000,
                    )
                except PWTimeout:
                    logger.warning("Timed out waiting for vehicle selectors — parsing anyway")

                # Extra settle time for lazy-loaded content
                time.sleep(2)

                html = page.content()

                # Save first page for debugging
                if page_num == 1:
                    with open('debug_page1.html', 'w', encoding='utf-8') as f:
                        f.write(html)
                    logger.info("Saved debug_page1.html ({} bytes)".format(len(html)))

                page_vehicles = find_vehicles(html)
                logger.info("Page {} — {} vehicles extracted".format(page_num, len(page_vehicles)))

                if not page_vehicles:
                    logger.info("No vehicles on page {} — stopping".format(page_num))
                    break

                all_vehicles.extend(page_vehicles)
                page_num += 1
                time.sleep(1.5)

            except PWTimeout:
                logger.error("Page load timed out on page {}".format(page_num))
                break
            except Exception as e:
                logger.error("Error on page {}: {}".format(page_num, e))
                break

        browser.close()

    # Deduplicate
    unique, seen = [], set()
    for v in all_vehicles:
        stock = v.get('stock_number','')
        y,mk,mo = v.get('year',''), v.get('makeName',''), v.get('model','')
        mil,pr,tr = v.get('mileage',''), v.get('value',''), v.get('trim','')
        if stock:                     key = ('s', stock)
        elif y and mk and mo and mil: key = ('ymml', y, mk, mo, mil)
        elif y and mk and mo and tr and pr: key = ('ymmtp', y, mk, mo, tr, pr)
        elif y and mk and mo and pr: key = ('ymmp', y, mk, mo, pr)
        else:                         key = ('all', y, mk, mo, tr, mil, pr)
        if key not in seen:
            seen.add(key)
            unique.append(v)

    logger.info("FINAL: {} unique vehicles (removed {} dupes)".format(
        len(unique), len(all_vehicles) - len(unique)))
    return unique


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
    print("Found {} vehicles".format(len(vehicles)))
    brands = {}
    for v in vehicles:
        b = v.get('makeName','Unknown')
        brands[b] = brands.get(b, 0) + 1
    print("\nBrand Distribution:")
    for b, c in sorted(brands.items()):
        print("  {}: {}".format(b, c))
    sale_count = sum(1 for v in vehicles if v.get('sale_value'))
    print("Vehicles with sale prices: {}".format(sale_count))
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
    logger.info("RED DEER TOYOTA SCRAPER — Playwright/Chromium")
    logger.info("="*80)

    vehicles = scrape_with_playwright()
    print_results(vehicles)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, '..', '..'))
    csv_path = os.path.join(project_root, 'public', 'data', 'inventory.csv')

    if vehicles:
        save_csv(vehicles, csv_path)
        print("\nCSV created: {}".format(csv_path))
    else:
        print("\nNo CSV created — check debug_page1.html for the raw HTML")
        if os.path.exists(csv_path):
            os.remove(csv_path)

    return 0 if vehicles else 1


if __name__ == "__main__":
    exit(main())
