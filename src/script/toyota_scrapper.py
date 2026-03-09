#!/usr/bin/env python3
"""
Red Deer Toyota Used Inventory Scraper - Enhanced Sale Price Extraction
Uses curl_cffi to impersonate Chrome TLS fingerprint and bypass Cloudflare.
"""

# curl_cffi impersonates Chrome's TLS fingerprint — this is what bypasses
# Cloudflare bot-detection. Plain `requests` has a distinctive handshake
# that Cloudflare blocks regardless of User-Agent or headers.
try:
    from curl_cffi import requests
except ImportError:
    raise SystemExit(
        "Missing dependency: pip install curl_cffi\n"
        "Add 'curl_cffi' to requirements.txt and re-run."
    )

from bs4 import BeautifulSoup
import csv
import time
import re
import logging
from datetime import datetime
import os
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class UniversalRedDeerToyotaScraper:
    def __init__(self):
        self.base_url = "https://www.reddeertoyota.com"
        self.target_url = "https://www.reddeertoyota.com/inventory/used/"
        # curl_cffi uses a plain dict for headers, not a Session object
        self.headers = {
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'max-age=0',
        }
        self.cookies = {}
        self.vehicles = []
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.car_makes = self._build_car_makes()
        self.debug_mode = True

    def _build_car_makes(self):
        return {
            'Toyota': {'Camry', 'RAV4', 'Highlander', 'Prius', 'Corolla', 'Corolla Cross',
                      'Tacoma', 'Tundra', 'Sienna', '4Runner', 'Sequoia', 'Avalon', 'C-HR',
                      'Venza', 'Land Cruiser', 'GR86', 'Supra', 'Yaris', 'Matrix', 'Crown'},
            'Honda': {'Civic', 'Accord', 'CR-V', 'HR-V', 'Pilot', 'Odyssey', 'Fit',
                     'Ridgeline', 'Passport'},
            'Ford': {'F-150', 'F-250', 'F-350', 'Escape', 'Explorer', 'Expedition', 'Edge',
                    'Fusion', 'Mustang', 'Bronco', 'Bronco Sport', 'Ranger', 'Maverick'},
            'Chevrolet': {'Silverado', 'Silverado 1500', 'Silverado 2500', 'Tahoe',
                         'Suburban', 'Equinox', 'Traverse', 'Malibu', 'Camaro', 'Colorado', 'Blazer'},
            'GMC': {'Sierra', 'Sierra 1500', 'Sierra 2500', 'Yukon', 'Acadia', 'Terrain', 'Canyon'},
            'Dodge': {'Charger', 'Challenger', 'Journey', 'Durango', 'Grand Caravan', 'Hornet'},
            'Ram': {'1500', '2500', '3500', 'ProMaster'},
            'Nissan': {'Altima', 'Sentra', 'Rogue', 'Murano', 'Pathfinder', 'Frontier', 'Titan', '370Z'},
            'Hyundai': {'Elantra', 'Sonata', 'Tucson', 'Santa Fe', 'Palisade', 'Kona'},
            'Kia': {'Forte', 'Sportage', 'Sorento', 'Telluride', 'Soul', 'Seltos'},
            'Mazda': {'Mazda3', 'Mazda6', 'CX-3', 'CX-5', 'CX-9', 'CX-30', 'CX-50'},
            'Subaru': {'Outback', 'Forester', 'Impreza', 'Legacy', 'Crosstrek', 'Ascent'},
            'Jeep': {'Wrangler', 'Grand Cherokee', 'Cherokee', 'Compass', 'Gladiator'},
            'Acura': {'MDX', 'RDX', 'TLX', 'ILX'},
            'Cadillac': {'XT4', 'XT5', 'XT6', 'Escalade'},
            'Buick': {'Enclave', 'Encore', 'Encore GX', 'Envision'},
            'Chrysler': {'300', 'Pacifica', 'Voyager'},
            'Scion': {'tC', 'xB', 'iA', 'iM', 'FR-S'},
            'Volkswagen': {'Jetta', 'Passat', 'Golf', 'Tiguan', 'Atlas', 'GTI'},
            'Audi': {'A3', 'A4', 'A6', 'Q3', 'Q5', 'Q7', 'Q8'},
            'Lincoln': {'Navigator', 'Aviator', 'Corsair', 'Nautilus'},
            'Gmc': {'Terrain'},
        }

    def get_trim_patterns(self):
        return {
            'Capstone': r'\bCapstone\b', 'Platinum': r'\bPlatinum\b', 'Limited': r'\bLimited\b',
            'XLE': r'\bXLE\b', 'XSE': r'\bXSE\b', 'LE': r'\bLE\b(?!\w)', 'SE': r'\bSE\b(?!\w)',
            'TRD Pro': r'\bTRD\s+Pro\b', 'TRD Off-Road': r'\bTRD\s+Off-?Road\b',
            'TRD Sport': r'\bTRD\s+Sport\b', 'TRD': r'\bTRD\b', 'SR5': r'\bSR5\b',
            'SR': r'\bSR\b(?!\d)', 'Hybrid': r'\bHybrid\b', 'Prime': r'\bPrime\b',
            'Nightshade': r'\bNightshade\b', 'Trail': r'\bTrail\b(?!\w)',
            'Adventure': r'\bAdventure\b', 'CrewMax': r'\bCrewMax\b',
            'Touring': r'\bTouring\b', 'EX-L': r'\bEX-L\b', 'EX': r'\bEX\b(?!\w)',
            'LX': r'\bLX\b(?!\w)', 'Type R': r'\bType\s+R\b', 'Si': r'\bSi\b',
            'TrailSport': r'\bTrailSport\b', 'Elite': r'\bElite\b',
            'Raptor': r'\bRaptor\b', 'King Ranch': r'\bKing\s+Ranch\b',
            'Lariat': r'\bLariat\b', 'XLT': r'\bXLT\b', 'XL': r'\bXL\b(?!\w)',
            'Tremor': r'\bTremor\b', 'Wildtrak': r'\bWildtrak\b', 'Badlands': r'\bBadlands\b',
            'ST': r'\bST\b(?!\w)', 'GT': r'\bGT\b(?!\w)', 'Shelby': r'\bShelby\b',
            'Hellcat': r'\bHellcat\b', 'SRT': r'\bSRT\b', 'Scat Pack': r'\bScat\s+Pack\b',
            'R/T': r'\bR/T\b', 'SXT': r'\bSXT\b', 'TRX': r'\bTRX\b', 'Rebel': r'\bRebel\b',
            'Laramie': r'\bLaramie\b', 'Longhorn': r'\bLonghorn\b', 'Big Horn': r'\bBig\s+Horn\b',
            'High Country': r'\bHigh\s+Country\b', 'LTZ': r'\bLTZ\b', 'LT': r'\bLT\b(?!\w)',
            'LS': r'\bLS\b(?!\w)', 'Z71': r'\bZ71\b', 'SS': r'\bSS\b(?!\w)',
            'Denali': r'\bDenali\b', 'AT4': r'\bAT4\b', 'SLT': r'\bSLT\b', 'SLE': r'\bSLE\b',
            'Pro-4X': r'\bPro-4X\b', 'Nismo': r'\bNismo\b', 'SL': r'\bSL\b(?!\w)',
            'SV': r'\bSV\b', 'Calligraphy': r'\bCalligraphy\b', 'Ultimate': r'\bUltimate\b',
            'Preferred': r'\bPreferred\b', 'N Line': r'\bN\s+Line\b',
            'Rubicon': r'\bRubicon\b', 'Sahara': r'\bSahara\b', 'Trailhawk': r'\bTrailhawk\b',
            'Overland': r'\bOverland\b', 'Summit': r'\bSummit\b', 'Mojave': r'\bMojave\b',
            'Willys': r'\bWillys\b', 'Sport': r'\bSport\b(?!\s+Utility)',
            'AWD': r'\bAWD\b', '4WD': r'\b4WD\b', 'Altitude': r'\bAltitude\b',
            'Big Bend': r'\bBig\s+Bend\b', 'Black Diamond': r'\bBlack\s+Diamond\b',
            'Essential': r'\bEssential\b', '2 DOOR': r'\b2\s+DOOR\b', 'IVT': r'\bIVT\b',
        }

    def _get(self, url):
        """Wrapper around curl_cffi get with Chrome impersonation and retry."""
        for attempt in range(1, 4):
            try:
                logger.info("GET {} (attempt {})".format(url, attempt))
                resp = requests.get(
                    url,
                    headers=self.headers,
                    cookies=self.cookies,
                    impersonate="chrome122",   # <-- the key fix: real Chrome TLS fingerprint
                    timeout=30,
                    allow_redirects=True,
                )
                # Persist any cookies the server sets (e.g. Cloudflare cf_clearance)
                self.cookies.update(resp.cookies)

                if resp.status_code == 403:
                    logger.warning("403 on attempt {} — waiting {}s".format(attempt, 3 * attempt))
                    time.sleep(3 * attempt)
                    continue

                resp.raise_for_status()
                logger.info("OK {} — {} bytes".format(resp.status_code, len(resp.content)))
                return resp

            except Exception as e:
                logger.error("Request error attempt {}: {}".format(attempt, e))
                if attempt < 3:
                    time.sleep(2 * attempt)

        return None

    def fetch_all_pages(self):
        all_soups = []
        page_num = 1
        max_pages = 10

        # Warm up: visit homepage first to collect any session/challenge cookies
        logger.info("Warming up session via homepage...")
        warmup = self._get(self.base_url)
        if warmup:
            logger.info("Homepage OK — cookies: {}".format(list(self.cookies.keys())))
        time.sleep(1.5)

        while page_num <= max_pages:
            url = "{}?page={}".format(self.target_url.rstrip('/'), page_num)

            # Add Referer for pages after the first
            if page_num > 1:
                self.headers['Referer'] = self.target_url
            else:
                self.headers['Referer'] = self.base_url + '/'

            resp = self._get(url)
            if resp is None:
                logger.info("Stopping at page {} — could not fetch".format(page_num))
                break

            soup = BeautifulSoup(resp.content, 'html.parser')

            if page_num == 1 and self.debug_mode:
                with open('debug_page1.html', 'w', encoding='utf-8') as f:
                    f.write(soup.prettify())
                logger.info("Saved debug_page1.html")

            page_text = soup.get_text()
            has_vehicles = bool(re.search(r'\b(19[89]\d|20[0-2]\d)\b', page_text))
            no_results = ('no vehicles found' in page_text.lower() or
                          'no results' in page_text.lower())

            if not has_vehicles or no_results:
                logger.info("Page {} has no vehicles — stopping".format(page_num))
                break

            all_soups.append((page_num, soup))
            page_num += 1
            time.sleep(1.0)

        logger.info("Fetched {} pages".format(len(all_soups)))
        return all_soups

    def extract_make_and_model(self, text):
        text = re.sub(r'\s+', ' ', text.strip())
        for make, models in self.car_makes.items():
            if re.search(r'\b{}\b'.format(re.escape(make)), text, re.IGNORECASE):
                for model in sorted(models, key=len, reverse=True):
                    if re.search(r'\b{}\b'.format(re.escape(model)), text, re.IGNORECASE):
                        return make, model
        return None, None

    def extract_trim(self, text, model):
        if not text:
            return ''
        for trim_name, pattern in self.get_trim_patterns().items():
            if re.search(pattern, text, re.IGNORECASE):
                if model and trim_name.lower() not in model.lower():
                    return trim_name
                elif not model:
                    return trim_name
        return ''

    def extract_prices_enhanced(self, element, vehicle_id="unknown"):
        regular_price = None
        sale_price = None

        for attr, value in element.attrs.items():
            attr_lower = attr.lower()
            if 'price' in attr_lower or 'msrp' in attr_lower:
                price_match = re.search(r'(\d{4,6})', str(value))
                if price_match:
                    price = int(price_match.group(1))
                    if 3000 <= price <= 300000:
                        if 'sale' in attr_lower or 'internet' in attr_lower or 'special' in attr_lower:
                            sale_price = price
                        elif 'msrp' in attr_lower or 'original' in attr_lower or 'regular' in attr_lower:
                            regular_price = price
                        elif not regular_price:
                            regular_price = price

        for script in element.find_all('script', type='application/ld+json'):
            try:
                data = json.loads(script.string)
                if isinstance(data, dict):
                    if 'offers' in data and isinstance(data['offers'], dict):
                        p = float(data['offers'].get('price', 0))
                        if 3000 <= p <= 300000:
                            regular_price = int(p)
                    if 'price' in data:
                        p = float(data['price'])
                        if 3000 <= p <= 300000:
                            regular_price = int(p)
            except:
                pass

        all_found_prices = []
        for els, source in [
            (element.find_all(class_=re.compile(r'(price|cost|amount)', re.I)), 'class'),
            (element.find_all(id=re.compile(r'(price|cost|amount)', re.I)), 'id'),
        ]:
            for el in els:
                el_text = el.get_text(strip=True)
                context = (el_text + ' ' + ' '.join(el.get('class', [])) +
                           (el.get('id') or '')).lower()
                for price_str in re.findall(r'\$?\s*([0-9]{1,3}(?:,\d{3})*)', el_text):
                    try:
                        price = int(price_str.replace(',', ''))
                        if 3000 <= price <= 300000:
                            is_sale = any(k in context for k in ['sale','special','internet','now','reduced','discount'])
                            is_msrp = any(k in context for k in ['msrp','was','original','regular','list','retail'])
                            has_strike = 'line-through' in el.get('style', '') or el.find(['s','strike','del']) is not None
                            all_found_prices.append({'price': price, 'is_sale': is_sale, 'is_msrp': is_msrp or has_strike})
                    except:
                        pass

        if not all_found_prices:
            text = element.get_text(separator=' ', strip=True)
            for match in re.finditer(r'\$\s*([0-9,]+)', text):
                try:
                    price = int(match.group(1).replace(',', ''))
                    if 3000 <= price <= 300000:
                        ctx = text[max(0, match.start()-100):match.end()+100].lower()
                        all_found_prices.append({
                            'price': price,
                            'is_sale': any(k in ctx for k in ['sale','internet','special','now']),
                            'is_msrp': any(k in ctx for k in ['msrp','was','original']),
                        })
                except:
                    pass

        if all_found_prices:
            deduped = {}
            for p in all_found_prices:
                if p['price'] not in deduped or p['is_sale'] or p['is_msrp']:
                    deduped[p['price']] = p
            prices = list(deduped.values())
            msrp = [p['price'] for p in prices if p['is_msrp']]
            sale = [p['price'] for p in prices if p['is_sale']]
            other = [p['price'] for p in prices if not p['is_msrp'] and not p['is_sale']]

            if msrp and sale:
                regular_price, sale_price = max(msrp), min(sale)
            elif msrp and other:
                regular_price = max(msrp)
                lower = [p for p in other if p < regular_price]
                if lower:
                    sale_price = max(lower)
            elif len(prices) >= 2:
                sp = sorted([p['price'] for p in prices], reverse=True)
                regular_price = sp[0]
                if sp[1] < sp[0]:
                    sale_price = sp[1]
            elif prices:
                regular_price = prices[0]['price']

        if regular_price and sale_price and sale_price >= regular_price:
            sale_price = None

        return regular_price, sale_price

    def extract_vehicle_data(self, element, element_index=0):
        vehicle = {
            'makeName': '', 'year': '', 'model': '', 'sub-model': '', 'trim': '',
            'mileage': '', 'value': '', 'sale_value': '', 'stock_number': '', 'engine': ''
        }
        try:
            text = re.sub(r'\s+', ' ', element.get_text(separator=' ', strip=True))

            m = re.search(r'\b(19[89]\d|20[0-2]\d)\b', text)
            if m:
                vehicle['year'] = m.group(1)

            make, model = self.extract_make_and_model(text)
            if make: vehicle['makeName'] = make
            if model: vehicle['model'] = model

            trim = self.extract_trim(text, model)
            if trim:
                vehicle['trim'] = trim
                vehicle['sub-model'] = trim

            for pat in [r'Stock[#:\s]*([A-Z0-9]{3,15})\b', r'#\s*([A-Z0-9]{3,15})\b']:
                m = re.search(pat, text, re.IGNORECASE)
                if m and m.group(1).isalnum() and len(m.group(1)) >= 3:
                    vehicle['stock_number'] = m.group(1)
                    break

            reg, sale = self.extract_prices_enhanced(element, vehicle.get('stock_number') or str(element_index))
            if reg: vehicle['value'] = str(reg)
            if sale: vehicle['sale_value'] = str(sale)

            for pat in [r'(\d{1,3}(?:,\d{3})*)\s*(?:km|kilometers?)\b',
                        r'(\d{1,3}(?:,\d{3})*)\s*(?:miles?|mi)\b']:
                m = re.search(pat, text, re.IGNORECASE)
                if m:
                    val = m.group(1).replace(',', '')
                    if 0 <= int(val) <= 500000:
                        vehicle['mileage'] = val
                        break

            for pat in [r'(\d\.\d+L\s*(?:V?\d+|I\d+))', r'(\d\.\d+L\s*Hybrid)', r'(\d\.\d+L\s*Turbo)']:
                m = re.search(pat, text, re.IGNORECASE)
                if m:
                    vehicle['engine'] = m.group(1).strip()
                    break

            for attr, value in element.attrs.items():
                if 'data-' not in attr.lower(): continue
                al, vs = attr.lower(), str(value)
                if 'year' in al and not vehicle['year'] and re.match(r'^(19[89]\d|20[0-2]\d)$', vs):
                    vehicle['year'] = vs
                elif 'make' in al and not vehicle['makeName']:
                    vehicle['makeName'] = vs.title()
                elif 'model' in al and not vehicle['model']:
                    vehicle['model'] = vs
                elif 'mileage' in al and not vehicle['mileage']:
                    clean = re.sub(r'[^\d]', '', vs)
                    if clean: vehicle['mileage'] = clean

        except Exception as e:
            logger.error("Error extracting vehicle {}: {}".format(element_index, e))
        return vehicle

    def is_valid_vehicle(self, vehicle):
        if not isinstance(vehicle, dict): return False
        if not (vehicle.get('year', '').strip() and vehicle.get('makeName', '').strip()):
            return False
        extras = ['model', 'value', 'sale_value', 'stock_number', 'mileage']
        return bool(vehicle.get('model', '').strip()) or \
               sum(1 for f in extras if vehicle.get(f, '').strip()) >= 2

    def find_vehicles(self, soup):
        vehicles = []
        seen = set()
        selectors = [
            '[data-vehicle-id]', '[data-stock-number]', '[data-vin]',
            '.vehicle-card', '.inventory-item', '.vehicle-listing',
            'article[class*="vehicle"]', 'div[class*="vehicle"]',
            'li[class*="vehicle"]', '.vehicle', 'article', 'li[class*="item"]'
        ]
        for selector in selectors:
            elements = soup.select(selector)
            if not elements: continue
            logger.info("Selector '{}' — {} elements".format(selector, len(elements)))
            count = 0
            for idx, el in enumerate(elements):
                eid = id(el)
                if eid in seen: continue
                v = self.extract_vehicle_data(el, idx)
                if self.is_valid_vehicle(v):
                    vehicles.append(v)
                    seen.add(eid)
                    count += 1
                    logger.info("  + {} {} {} ${}".format(v['year'], v['makeName'], v['model'], v.get('value','')))
            if count > 0:
                logger.info("Extracted {} vehicles with '{}'".format(count, selector))
                return vehicles

        logger.info("Trying broad fallback...")
        for idx, div in enumerate(soup.find_all(['div','section','article','li'])):
            eid = id(div)
            if eid in seen: continue
            txt = div.get_text(separator=' ', strip=True)
            if re.search(r'\b(19[89]\d|20[0-2]\d)\b', txt):
                for make in self.car_makes:
                    if re.search(r'\b' + re.escape(make) + r'\b', txt, re.IGNORECASE):
                        v = self.extract_vehicle_data(div, idx)
                        if self.is_valid_vehicle(v):
                            vehicles.append(v)
                            seen.add(eid)
                        break
        return vehicles

    def scrape_inventory(self):
        logger.info("=" * 80)
        logger.info("RED DEER TOYOTA SCRAPER - ENHANCED SALE PRICE EXTRACTION")
        logger.info("=" * 80)

        all_pages = self.fetch_all_pages()
        if not all_pages:
            logger.error("No pages fetched")
            return []

        all_vehicles = []
        for page_num, soup in all_pages:
            pv = self.find_vehicles(soup)
            logger.info("Page {} — {} vehicles".format(page_num, len(pv)))
            all_vehicles.extend(pv)

        unique, seen = [], set()
        for v in all_vehicles:
            stock = v.get('stock_number', '')
            y, mk, mo = v.get('year',''), v.get('makeName',''), v.get('model','')
            mil, pr, tr = v.get('mileage',''), v.get('value',''), v.get('trim','')
            if stock:             key = ('s', stock)
            elif y and mk and mo and mil: key = ('ymml', y, mk, mo, mil)
            elif y and mk and mo and tr and pr: key = ('ymmtp', y, mk, mo, tr, pr)
            elif y and mk and mo and pr: key = ('ymmp', y, mk, mo, pr)
            else:                 key = ('all', y, mk, mo, tr, mil, pr)
            if key not in seen:
                seen.add(key)
                unique.append(v)

        self.vehicles = unique
        logger.info("FINAL: {} unique vehicles".format(len(self.vehicles)))
        sale_count = sum(1 for v in self.vehicles if v.get('sale_value'))
        logger.info("With sale prices: {}".format(sale_count))
        return self.vehicles

    def save_to_csv(self, filename):
        fields = ['makeName','year','model','sub-model','trim','mileage',
                  'value','sale_value','stock_number','engine']
        if not self.vehicles:
            return False
        try:
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fields)
                writer.writeheader()
                for v in self.vehicles:
                    writer.writerow({field: v.get(field,'') for field in fields})
            logger.info("CSV saved: {}".format(filename))
            return True
        except Exception as e:
            logger.error("CSV error: {}".format(e))
            return False

    def print_results(self):
        print("\n" + "="*100)
        print("RED DEER TOYOTA USED INVENTORY")
        print("="*100)
        if not self.vehicles:
            print("No vehicles found")
            return
        print("Found {} vehicles".format(len(self.vehicles)))
        brands = {}
        for v in self.vehicles:
            b = v.get('makeName','Unknown')
            brands[b] = brands.get(b, 0) + 1
        for b, c in sorted(brands.items()):
            print("  {}: {}".format(b, c))
        print("\n{:<10} {:<6} {:<15} {:<10} {:<12} {:<12} {:<10}".format(
            'Make','Year','Model','Trim','Value','Sale Price','Stock#'))
        print("-"*85)
        for v in self.vehicles:
            print("{:<10} {:<6} {:<15} {:<10} {:<12} {:<12} {:<10}".format(
                v.get('makeName','')[:9], v.get('year',''), v.get('model','')[:14],
                v.get('trim','')[:9], v.get('value','')[:11],
                v.get('sale_value','')[:11], v.get('stock_number','')[:9]))


def main():
    scraper = UniversalRedDeerToyotaScraper()
    try:
        vehicles = scraper.scrape_inventory()
        scraper.print_results()

        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(script_dir, '..', '..'))
        csv_path = os.path.join(project_root, 'public', 'data', 'inventory.csv')

        if vehicles:
            scraper.save_to_csv(csv_path)
            print("\nCSV created: {}".format(csv_path))
        else:
            print("\nNo CSV created")
            if os.path.exists(csv_path):
                os.remove(csv_path)

        return 0 if vehicles else 1

    except Exception as e:
        logger.error("Scraper failed: {}".format(e))
        import traceback; traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
