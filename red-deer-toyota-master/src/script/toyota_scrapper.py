#!/usr/bin/env python3
"""
Red Deer Toyota Used Inventory Scraper - Universal Version
Extracts ONLY accurate data for ANY brand/model: makeName, year, model, sub-model, trim, mileage, value, stock_number, engine
NO sample data fallback - only real scraped data from any manufacturer
"""

import requests
from bs4 import BeautifulSoup
import json
import csv
import time
import re
import logging
from datetime import datetime
import os
from urllib.parse import urljoin

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class UniversalRedDeerToyotaScraper:
    def __init__(self):
        self.base_url = "https://www.reddeertoyota.com"
        self.target_url = "https://www.reddeertoyota.com/inventory/used/"
        self.session = requests.Session()
        
        # Full browser-like headers — matches what Chrome 122 actually sends
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        })
        
        self.vehicles = []
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Universal car makes and models
        self.car_makes = {
            'Toyota': {
                'Camry', 'RAV4', 'Highlander', 'Prius', 'Corolla', 'Corolla Cross', 'Tacoma',
                'Tundra', 'Sienna', '4Runner', 'Sequoia', 'Avalon', 'C-HR', 'Venza',
                'Land Cruiser', 'GR86', 'Supra', 'Yaris', 'Matrix', 'FJ Cruiser', 'Crown'
            },
            'Honda': {
                'Civic', 'Accord', 'CR-V', 'HR-V', 'Pilot', 'Odyssey', 'Fit',
                'Ridgeline', 'Passport', 'Element', 'Insight'
            },
            'Ford': {
                'F-150', 'F-250', 'F-350', 'Escape', 'Explorer', 'Expedition', 'Edge',
                'Fusion', 'Focus', 'Mustang', 'Bronco', 'Bronco Sport', 'Ranger', 'Maverick',
                'Taurus', 'Transit'
            },
            'Chevrolet': {
                'Silverado', 'Silverado 1500', 'Silverado 2500', 'Tahoe', 'Suburban',
                'Equinox', 'Traverse', 'Malibu', 'Cruze', 'Camaro', 'Colorado', 'Blazer', 'Trax'
            },
            'GMC': {
                'Sierra', 'Sierra 1500', 'Sierra 2500', 'Yukon', 'Acadia', 'Terrain', 'Canyon'
            },
            'Dodge': {
                'Charger', 'Challenger', 'Journey', 'Durango', 'Grand Caravan', 'Hornet'
            },
            'Ram': {'1500', '2500', '3500', 'ProMaster'},
            'Nissan': {
                'Altima', 'Sentra', 'Rogue', 'Murano', 'Pathfinder', 'Armada',
                'Titan', 'Frontier', '370Z', 'Leaf', 'Kicks', 'Versa'
            },
            'Hyundai': {
                'Elantra', 'Sonata', 'Tucson', 'Santa Fe', 'Palisade',
                'Accent', 'Veloster', 'Kona', 'Venue'
            },
            'Kia': {
                'Forte', 'Optima', 'Sportage', 'Sorento', 'Telluride',
                'Soul', 'Stinger', 'Rio', 'Sedona', 'Niro', 'Seltos'
            },
            'Mazda': {
                'Mazda3', 'Mazda6', 'CX-3', 'CX-5', 'CX-9', 'CX-30', 'CX-50', 'MX-5'
            },
            'Subaru': {
                'Outback', 'Forester', 'Impreza', 'Legacy', 'Crosstrek', 'Ascent', 'WRX', 'BRZ'
            },
            'Volkswagen': {
                'Jetta', 'Passat', 'Golf', 'Tiguan', 'Atlas', 'Beetle', 'GTI', 'Touareg'
            },
            'BMW': {'3 Series', '5 Series', '7 Series', 'X1', 'X3', 'X5', 'X7', 'Z4'},
            'Mercedes-Benz': {'C-Class', 'E-Class', 'S-Class', 'GLA', 'GLC', 'GLE', 'GLS', 'CLA'},
            'Audi': {'A3', 'A4', 'A6', 'A8', 'Q3', 'Q5', 'Q7', 'Q8', 'TT', 'R8'},
            'Lexus': {'ES', 'IS', 'GS', 'LS', 'NX', 'RX', 'GX', 'LX', 'UX'},
            'Acura': {'ILX', 'TLX', 'RDX', 'MDX', 'NSX'},
            'Jeep': {
                'Wrangler', 'Grand Cherokee', 'Cherokee', 'Compass', 'Renegade', 'Gladiator'
            },
            'Cadillac': {'Escalade', 'XT4', 'XT5', 'XT6', 'CT4', 'CT5'},
            'Buick': {'Enclave', 'Encore', 'Encore GX', 'Envision', 'LaCrosse'},
            'Lincoln': {'Navigator', 'Aviator', 'Corsair', 'Nautilus'},
            'Chrysler': {'300', 'Pacifica', 'Voyager'},
            'Scion': {'tC', 'xB', 'xD', 'iA', 'iM', 'FR-S'},
            'Infiniti': {'Q50', 'Q60', 'QX50', 'QX60', 'QX80'},
            'Gmc': {'Terrain'},  # lowercase variant the site sometimes uses
        }

    # ------------------------------------------------------------------
    # Session warm-up: visit homepage first to collect cookies & bypass
    # basic bot-detection that checks for a prior session.
    # ------------------------------------------------------------------
    def warm_up_session(self):
        """Visit the dealer homepage so we look like a real browser session."""
        try:
            logger.info("Warming up session via homepage: {}".format(self.base_url))
            resp = self.session.get(self.base_url, timeout=30)
            logger.info("Homepage status: {}".format(resp.status_code))
            time.sleep(1.5)  # brief pause — mimics human navigation speed
        except Exception as e:
            logger.warning("Session warm-up failed (non-fatal): {}".format(e))

    def fetch_page(self, url, attempt=1, max_attempts=3):
        """Fetch a single page with retry logic."""
        for attempt_num in range(1, max_attempts + 1):
            try:
                logger.info("Fetching (attempt {}/{}): {}".format(attempt_num, max_attempts, url))

                # After the first attempt add a Referer so subsequent requests look
                # like normal in-site navigation.
                if attempt_num > 1:
                    self.session.headers.update({'Referer': self.base_url + '/'})

                response = self.session.get(url, timeout=30)

                if response.status_code == 403:
                    logger.warning("403 on attempt {} — waiting before retry...".format(attempt_num))
                    time.sleep(3 * attempt_num)
                    continue

                response.raise_for_status()
                logger.info("OK {} — {} bytes".format(response.status_code, len(response.content)))
                return BeautifulSoup(response.content, 'html.parser')

            except requests.exceptions.HTTPError as e:
                logger.error("HTTP error: {}".format(e))
                if attempt_num < max_attempts:
                    time.sleep(2 * attempt_num)
                else:
                    return None
            except Exception as e:
                logger.error("Request failed: {}".format(e))
                if attempt_num < max_attempts:
                    time.sleep(2 * attempt_num)
                else:
                    return None
        return None

    def fetch_all_pages(self):
        """Fetch all paginated inventory pages."""
        # Warm up before hitting the inventory endpoint
        self.warm_up_session()

        all_soups = []
        page_num = 1
        max_pages = 10

        while page_num <= max_pages:
            url = "{}?page={}".format(self.target_url.rstrip('/'), page_num)
            soup = self.fetch_page(url)

            if not soup:
                logger.info("Stopping pagination — could not fetch page {}".format(page_num))
                break

            page_text = soup.get_text()
            has_vehicles = bool(re.search(r'\b(19[89]\d|20[0-2]\d)\b', page_text))
            no_results = ('no vehicles found' in page_text.lower() or
                          'no results' in page_text.lower())

            if not has_vehicles or no_results:
                logger.info("Page {} has no vehicles — stopping".format(page_num))
                break

            # Save first page HTML for debugging
            if page_num == 1:
                try:
                    with open('debug_page1.html', 'w', encoding='utf-8') as f:
                        f.write(soup.prettify())
                    logger.info("Saved debug_page1.html")
                except Exception:
                    pass

            all_soups.append((page_num, soup))
            page_num += 1
            time.sleep(1.0)   # polite crawl delay

        logger.info("Fetched {} pages total".format(len(all_soups)))
        return all_soups

    # ------------------------------------------------------------------
    # Extraction helpers (unchanged from original)
    # ------------------------------------------------------------------

    def extract_make_and_model(self, text):
        text = re.sub(r'\s+', ' ', text.strip())
        for make, models in self.car_makes.items():
            if re.search(r'\b{}\b'.format(re.escape(make)), text, re.IGNORECASE):
                for model in sorted(models, key=len, reverse=True):
                    if re.search(r'\b{}\b'.format(re.escape(model)), text, re.IGNORECASE):
                        return make, model
        return None, None

    def extract_clean_vehicle_data(self, element, element_index=0):
        vehicle = {
            'makeName': '', 'year': '', 'model': '', 'sub-model': '', 'trim': '',
            'mileage': '', 'value': '', 'sale_value': '', 'stock_number': '', 'engine': ''
        }

        try:
            element_text = re.sub(r'\s+', ' ', element.get_text(separator=' ', strip=True))

            year_match = re.search(r'\b(19[89]\d|20[0-2]\d)\b', element_text)
            if year_match:
                vehicle['year'] = year_match.group(1)

            make, model = self.extract_make_and_model(element_text)
            if make:
                vehicle['makeName'] = make
            if model:
                vehicle['model'] = model

            trim_patterns = {
                'Capstone': r'\bCapstone\b', 'Platinum': r'\bPlatinum\b',
                'Limited': r'\bLimited\b', 'XLE': r'\bXLE\b', 'XSE': r'\bXSE\b',
                'LE': r'\bLE\b(?!\w)', 'SE': r'\bSE\b(?!\w)',
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
                'Tremor': r'\bTremor\b', 'Wildtrak': r'\bWildtrak\b',
                'ST': r'\bST\b(?!\w)', 'GT': r'\bGT\b(?!\w)', 'Shelby': r'\bShelby\b',
                'Hellcat': r'\bHellcat\b', 'SRT': r'\bSRT\b', 'Scat Pack': r'\bScat\s+Pack\b',
                'R/T': r'\bR/T\b', 'SXT': r'\bSXT\b', 'TRX': r'\bTRX\b', 'Rebel': r'\bRebel\b',
                'Laramie': r'\bLaramie\b', 'Big Horn': r'\bBig\s+Horn\b',
                'High Country': r'\bHigh\s+Country\b', 'LTZ': r'\bLTZ\b',
                'LT': r'\bLT\b(?!\w)', 'LS': r'\bLS\b(?!\w)', 'Z71': r'\bZ71\b',
                'Denali': r'\bDenali\b', 'AT4': r'\bAT4\b', 'SLT': r'\bSLT\b',
                'SLE': r'\bSLE\b', 'Pro-4X': r'\bPro-4X\b', 'Nismo': r'\bNismo\b',
                'SL': r'\bSL\b(?!\w)', 'SV': r'\bSV\b',
                'Calligraphy': r'\bCalligraphy\b', 'Ultimate': r'\bUltimate\b',
                'Preferred': r'\bPreferred\b', 'N Line': r'\bN\s+Line\b',
                'Rubicon': r'\bRubicon\b', 'Sahara': r'\bSahara\b',
                'Overland': r'\bOverland\b', 'Summit': r'\bSummit\b',
                'Sport': r'\bSport\b(?!\s+Utility)',
                'AWD': r'\bAWD\b', '4WD': r'\b4WD\b',
                'Essential': r'\bEssential\b', 'IVT': r'\bIVT\b',
            }

            for trim_name, pattern in trim_patterns.items():
                if re.search(pattern, element_text, re.IGNORECASE):
                    vehicle['trim'] = trim_name
                    vehicle['sub-model'] = trim_name
                    break

            # Prices
            all_prices = []
            for match in re.finditer(r'\$\s*([0-9,]{4,})', element_text):
                try:
                    p = int(match.group(1).replace(',', ''))
                    if 3000 <= p <= 300000:
                        start = max(0, match.start() - 80)
                        ctx = element_text[start:match.end() + 80].lower()
                        is_sale = any(k in ctx for k in ['sale', 'special', 'internet', 'now', 'reduced'])
                        is_msrp = any(k in ctx for k in ['msrp', 'was', 'original', 'regular'])
                        all_prices.append({'price': p, 'is_sale': is_sale, 'is_msrp': is_msrp})
                except Exception:
                    pass

            if all_prices:
                msrp = [x['price'] for x in all_prices if x['is_msrp']]
                sale = [x['price'] for x in all_prices if x['is_sale']]
                other = [x['price'] for x in all_prices if not x['is_msrp'] and not x['is_sale']]

                if msrp and sale:
                    vehicle['value'] = str(max(msrp))
                    vehicle['sale_value'] = str(min(sale))
                elif len(all_prices) >= 2:
                    sorted_p = sorted([x['price'] for x in all_prices], reverse=True)
                    vehicle['value'] = str(sorted_p[0])
                    if sorted_p[1] < sorted_p[0]:
                        vehicle['sale_value'] = str(sorted_p[1])
                elif all_prices:
                    vehicle['value'] = str(all_prices[0]['price'])

            # Validate sale < regular
            if vehicle['value'] and vehicle['sale_value']:
                if int(vehicle['sale_value']) >= int(vehicle['value']):
                    vehicle['sale_value'] = ''

            # Mileage
            for pattern in [
                r'(\d{1,3}(?:,\d{3})*)\s*(?:km|kilometers?)\b',
                r'(\d{1,3}(?:,\d{3})*)\s*(?:miles?|mi)\b',
            ]:
                m = re.search(pattern, element_text, re.IGNORECASE)
                if m:
                    val = m.group(1).replace(',', '')
                    if 0 <= int(val) <= 500000:
                        vehicle['mileage'] = val
                        break

            # Stock number
            for pattern in [
                r'Stock[#:\s]*([A-Z0-9]{3,15})\b',
                r'#\s*([A-Z0-9]{3,15})\b',
            ]:
                m = re.search(pattern, element_text, re.IGNORECASE)
                if m and m.group(1).isalnum() and len(m.group(1)) >= 3:
                    vehicle['stock_number'] = m.group(1)
                    break

            # Engine
            for pattern in [
                r'(\d\.\d+L\s*(?:V?\d+|I\d+))',
                r'(\d\.\d+L\s*Hybrid)',
                r'(\d\.\d+L\s*Turbo)',
            ]:
                m = re.search(pattern, element_text, re.IGNORECASE)
                if m:
                    vehicle['engine'] = m.group(1).strip()
                    break

            # Data attributes
            for attr, value in element.attrs.items():
                al = attr.lower()
                if 'data-' not in al:
                    continue
                vs = str(value)
                if 'year' in al and not vehicle['year']:
                    if re.match(r'^(19[89]\d|20[0-2]\d)$', vs):
                        vehicle['year'] = vs
                elif 'make' in al and not vehicle['makeName']:
                    vehicle['makeName'] = vs.title()
                elif 'model' in al and not vehicle['model']:
                    vehicle['model'] = vs
                elif 'mileage' in al and not vehicle['mileage']:
                    clean = re.sub(r'[^\d]', '', vs)
                    if clean and clean.isdigit():
                        vehicle['mileage'] = clean

        except Exception as e:
            logger.debug("Extraction error (element {}): {}".format(element_index, e))

        return vehicle

    def is_complete_vehicle(self, vehicle):
        if not isinstance(vehicle, dict):
            return False
        has_year = bool(vehicle.get('year', '').strip())
        has_make = bool(vehicle.get('makeName', '').strip())
        if not (has_year and has_make):
            return False
        extras = ['model', 'value', 'sale_value', 'stock_number', 'mileage']
        return sum(1 for f in extras if vehicle.get(f, '').strip()) >= 1

    def find_vehicle_containers(self, soup):
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
            if not elements:
                continue

            logger.info("Trying selector '{}' — {} elements".format(selector, len(elements)))
            count = 0
            for idx, el in enumerate(elements):
                eid = id(el)
                if eid in seen:
                    continue
                v = self.extract_clean_vehicle_data(el, idx)
                if self.is_complete_vehicle(v):
                    vehicles.append(v)
                    seen.add(eid)
                    count += 1
                    logger.info("  ✓ {} {} {} — ${}".format(
                        v['year'], v['makeName'], v['model'], v.get('value', '?')))

            if count > 0:
                logger.info("Extracted {} vehicles with selector '{}'".format(count, selector))
                return vehicles

        # Broad fallback
        logger.info("No vehicles found with specific selectors — trying broad fallback")
        for idx, div in enumerate(soup.find_all(['div', 'section', 'article', 'li'])):
            eid = id(div)
            if eid in seen:
                continue
            txt = div.get_text(separator=' ', strip=True)
            if re.search(r'\b(19[89]\d|20[0-2]\d)\b', txt):
                for make in self.car_makes:
                    if re.search(r'\b' + re.escape(make) + r'\b', txt, re.IGNORECASE):
                        v = self.extract_clean_vehicle_data(div, idx)
                        if self.is_complete_vehicle(v):
                            vehicles.append(v)
                            seen.add(eid)
                        break

        return vehicles

    def scrape_inventory(self):
        logger.info("=" * 80)
        logger.info("UNIVERSAL RED DEER TOYOTA USED INVENTORY SCRAPER")
        logger.info("=" * 80)

        all_pages = self.fetch_all_pages()
        if not all_pages:
            logger.error("No pages fetched")
            return []

        all_vehicles = []
        for page_num, soup in all_pages:
            logger.info("Processing page {}".format(page_num))
            page_vehicles = self.find_vehicle_containers(soup)
            logger.info("Page {} — {} vehicles".format(page_num, len(page_vehicles)))
            all_vehicles.extend(page_vehicles)

        logger.info("Total before dedup: {}".format(len(all_vehicles)))

        # Deduplication
        unique, seen = [], set()
        for v in all_vehicles:
            stock = v.get('stock_number', '')
            year = v.get('year', '')
            make = v.get('makeName', '')
            model = v.get('model', '')
            mileage = v.get('mileage', '')
            price = v.get('value', '')
            trim = v.get('trim', '')

            if stock:
                key = ('stock', stock)
            elif year and make and model and mileage:
                key = ('ymml', year, make, model, mileage)
            elif year and make and model and trim and price:
                key = ('ymmtp', year, make, model, trim, price)
            elif year and make and model and price:
                key = ('ymmp', year, make, model, price)
            else:
                key = ('all', year, make, model, trim, mileage, price)

            if key not in seen:
                seen.add(key)
                unique.append(v)

        self.vehicles = unique
        logger.info("FINAL: {} unique vehicles".format(len(self.vehicles)))
        sale_count = sum(1 for v in self.vehicles if v.get('sale_value'))
        logger.info("Vehicles with sale prices: {}".format(sale_count))
        return self.vehicles

    def save_to_csv(self, filename):
        fields = ['makeName', 'year', 'model', 'sub-model', 'trim', 'mileage',
                  'value', 'sale_value', 'stock_number', 'engine']
        if not self.vehicles:
            logger.info("No vehicles — skipping CSV")
            return False
        try:
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fields)
                writer.writeheader()
                for v in self.vehicles:
                    writer.writerow({field: v.get(field, '') for field in fields})
            logger.info("CSV saved: {}".format(filename))
            return True
        except Exception as e:
            logger.error("CSV error: {}".format(e))
            return False

    def print_results(self):
        print("\n" + "=" * 100)
        print("RED DEER TOYOTA USED INVENTORY")
        print("=" * 100)
        if not self.vehicles:
            print("No vehicles found")
            return
        print("Found {} vehicles".format(len(self.vehicles)))
        brands = {}
        for v in self.vehicles:
            b = v.get('makeName', 'Unknown')
            brands[b] = brands.get(b, 0) + 1
        print("\nBrand Distribution:")
        for b, c in sorted(brands.items()):
            print("  {}: {}".format(b, c))
        print("\n{:<10} {:<6} {:<15} {:<10} {:<12} {:<12} {:<10}".format(
            'Make', 'Year', 'Model', 'Trim', 'Value', 'Sale Price', 'Stock#'))
        print("-" * 85)
        for v in self.vehicles:
            print("{:<10} {:<6} {:<15} {:<10} {:<12} {:<12} {:<10}".format(
                v.get('makeName', '')[:9], v.get('year', ''), v.get('model', '')[:14],
                v.get('trim', '')[:9], v.get('value', '')[:11],
                v.get('sale_value', '')[:11], v.get('stock_number', '')[:9]))


def main():
    scraper = UniversalRedDeerToyotaScraper()
    try:
        vehicles = scraper.scrape_inventory()
        scraper.print_results()

        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(script_dir, '..', '..'))
        public_data_dir = os.path.join(project_root, 'public', 'data')
        os.makedirs(public_data_dir, exist_ok=True)
        csv_path = os.path.join(public_data_dir, 'inventory.csv')

        if vehicles:
            scraper.save_to_csv(csv_path)
            print("\nCSV created: {}".format(csv_path))
            print("DEBUG: Check 'debug_page1.html' for raw HTML structure")
        else:
            print("\nNo CSV created")
            if os.path.exists(csv_path):
                os.remove(csv_path)

        return 0 if vehicles else 1

    except Exception as e:
        logger.error("Scraper failed: {}".format(e))
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
