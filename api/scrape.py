#!/usr/bin/env python3
"""
Red Deer Toyota Used Inventory Scraper - Fixed Version
Extracts accurate data including sale prices for all brands/models
"""

import requests
from bs4 import BeautifulSoup
import csv
import time
import re
import logging
from datetime import datetime
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class UniversalRedDeerToyotaScraper:
    def __init__(self):
        self.base_url = "https://www.reddeertoyota.com"
        self.target_url = "https://www.reddeertoyota.com/inventory/used/"
        self.session = requests.Session()
        
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
        })
        
        self.vehicles = []
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.car_makes = self._build_car_makes()

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
                         'Suburban', 'Equinox', 'Traverse', 'Malibu', 'Camaro', 'Colorado'},
            'GMC': {'Sierra', 'Sierra 1500', 'Sierra 2500', 'Yukon', 'Acadia', 'Terrain', 'Canyon'},
            'Dodge': {'Charger', 'Challenger', 'Journey', 'Durango', 'Grand Caravan'},
            'Ram': {'1500', '2500', '3500', 'ProMaster'},
            'Nissan': {'Altima', 'Sentra', 'Rogue', 'Murano', 'Pathfinder', 'Frontier', 'Titan'},
            'Hyundai': {'Elantra', 'Sonata', 'Tucson', 'Santa Fe', 'Palisade', 'Kona'},
            'Kia': {'Forte', 'Sportage', 'Sorento', 'Telluride', 'Soul', 'Seltos'},
            'Mazda': {'Mazda3', 'Mazda6', 'CX-3', 'CX-5', 'CX-9', 'CX-30', 'CX-50'},
            'Subaru': {'Outback', 'Forester', 'Impreza', 'Legacy', 'Crosstrek', 'Ascent'},
            'Jeep': {'Wrangler', 'Grand Cherokee', 'Cherokee', 'Compass', 'Gladiator'},
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
            'AWD': r'\bAWD\b', '4WD': r'\b4WD\b',
        }

    def fetch_all_pages(self):
        all_soups = []
        page_num = 1
        max_pages = 10
        
        while page_num <= max_pages:
            url = "{}?page={}".format(self.target_url.rstrip('/'), page_num)
            
            try:
                logger.info("Fetching page {}: {}".format(page_num, url))
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                page_text = soup.get_text()
                
                has_vehicles = bool(re.search(r'\b(19[89]\d|20[0-2]\d)\b', page_text))
                no_results = 'no vehicles found' in page_text.lower() or 'no results' in page_text.lower()
                
                if not has_vehicles or no_results:
                    logger.info("Page {} has no vehicles, stopping".format(page_num))
                    break
                
                all_soups.append((page_num, soup))
                page_num += 1
                time.sleep(0.5)
                
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 404:
                    logger.info("Page {} returned 404".format(page_num))
                    break
                logger.error("HTTP error on page {}: {}".format(page_num, str(e)))
                break
            except Exception as e:
                logger.error("Failed to fetch page {}: {}".format(page_num, str(e)))
                break
        
        logger.info("Fetched {} pages".format(len(all_soups)))
        return all_soups

    def extract_make_and_model(self, text):
        text = re.sub(r'\s+', ' ', text.strip())
        
        for make, models in self.car_makes.items():
            make_pattern = r'\b{}\b'.format(re.escape(make))
            if re.search(make_pattern, text, re.IGNORECASE):
                sorted_models = sorted(models, key=len, reverse=True)
                for model in sorted_models:
                    model_pattern = r'\b{}\b'.format(re.escape(model))
                    if re.search(model_pattern, text, re.IGNORECASE):
                        return make, model
        return None, None

    def extract_trim(self, text, model):
        if not text:
            return ''
        
        trim_patterns = self.get_trim_patterns()
        for trim_name, pattern in trim_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                if model and trim_name.lower() not in model.lower():
                    return trim_name
                elif not model:
                    return trim_name
        return ''

    def extract_vehicle_data(self, element):
        vehicle = {
            'makeName': '', 'year': '', 'model': '', 'sub-model': '', 'trim': '',
            'mileage': '', 'value': '', 'sale_value': '', 'stock_number': '', 'engine': ''
        }
        
        try:
            text = element.get_text(separator=' ', strip=True)
            text = re.sub(r'\s+', ' ', text)
            
            # Extract year
            year_match = re.search(r'\b(19[89]\d|20[0-2]\d)\b', text)
            if year_match:
                vehicle['year'] = year_match.group(1)
            
            # Extract make and model
            make, model = self.extract_make_and_model(text)
            if make:
                vehicle['makeName'] = make
            if model:
                vehicle['model'] = model
            
            # Extract trim
            trim = self.extract_trim(text, model)
            if trim:
                vehicle['trim'] = trim
                vehicle['sub-model'] = trim
            
            # FIXED PRICE EXTRACTION
            all_prices = []
            price_contexts = {}
            
            # Find all dollar amounts with context
            for match in re.finditer(r'\$\s*([0-9,]+)', text):
                try:
                    price = int(match.group(1).replace(',', ''))
                    if 3000 <= price <= 300000:
                        # Get 100 chars before and after for context
                        start = max(0, match.start() - 100)
                        end = min(len(text), match.end() + 100)
                        context = text[start:end].lower()
                        
                        all_prices.append(price)
                        price_contexts[price] = context
                except:
                    pass
            
            # Look for prices in HTML attributes
            for attr, value in element.attrs.items():
                attr_lower = attr.lower()
                val_str = str(value)
                
                # Check for numeric values in attributes
                for num_match in re.finditer(r'(\d{4,6})', val_str):
                    try:
                        price = int(num_match.group(1))
                        if 3000 <= price <= 300000:
                            all_prices.append(price)
                            # Attribute context
                            context = attr_lower + '=' + val_str.lower()
                            price_contexts[price] = context
                    except:
                        pass
            
            # Categorize prices
            sale_prices = []
            original_prices = []
            
            sale_keywords = ['sale', 'special', 'internet', 'now', 'reduced', 'discount', 'offer', 'price']
            original_keywords = ['was', 'msrp', 'list', 'retail', 'original']
            
            for price in set(all_prices):
                context = price_contexts.get(price, '')
                
                # Check if this is a sale price
                has_sale_keyword = any(kw in context for kw in sale_keywords)
                has_original_keyword = any(kw in context for kw in original_keywords)
                
                if has_original_keyword:
                    original_prices.append(price)
                elif has_sale_keyword:
                    sale_prices.append(price)
            
            # Decision logic
            unique_prices = sorted(set(all_prices), reverse=True)
            
            if len(unique_prices) >= 2:
                # If we have categorized prices, use them
                if sale_prices and original_prices:
                    vehicle['sale_value'] = str(min(sale_prices))
                    vehicle['value'] = str(max(original_prices))
                elif sale_prices:
                    vehicle['sale_value'] = str(min(sale_prices))
                    # Look for a higher price as original
                    higher = [p for p in unique_prices if p > min(sale_prices)]
                    if higher:
                        vehicle['value'] = str(min(higher))
                elif original_prices:
                    vehicle['value'] = str(max(original_prices))
                    # Look for a lower price as sale
                    lower = [p for p in unique_prices if p < max(original_prices)]
                    if lower:
                        vehicle['sale_value'] = str(max(lower))
                else:
                    # No keywords - assume first is original, second is sale
                    vehicle['value'] = str(unique_prices[0])
                    vehicle['sale_value'] = str(unique_prices[1])
            elif len(unique_prices) == 1:
                vehicle['value'] = str(unique_prices[0])
            
            # Validate: sale should be lower than original
            if vehicle['value'] and vehicle['sale_value']:
                if int(vehicle['sale_value']) >= int(vehicle['value']):
                    vehicle['sale_value'] = ''
            
            # Extract mileage
            mileage_patterns = [
                r'(\d{1,3}(?:,\d{3})*)\s*(?:km|kilometers?)\b',
                r'(\d{1,3}(?:,\d{3})*)\s*(?:miles?|mi)\b',
            ]
            for pattern in mileage_patterns:
                m = re.search(pattern, text, re.IGNORECASE)
                if m:
                    val = m.group(1).replace(',', '')
                    try:
                        if 0 <= int(val) <= 500000:
                            vehicle['mileage'] = val
                            break
                    except:
                        pass
            
            # Extract stock number
            stock_patterns = [
                r'Stock[#:\s]*([A-Z0-9]{3,15})\b',
                r'#\s*([A-Z0-9]{3,15})\b',
            ]
            for pattern in stock_patterns:
                m = re.search(pattern, text, re.IGNORECASE)
                if m:
                    val = m.group(1)
                    if len(val) >= 3 and val.isalnum():
                        vehicle['stock_number'] = val
                        break
            
            # Extract engine
            engine_patterns = [
                r'(\d\.\d+L\s*(?:V?\d+|I\d+))',
                r'(\d\.\d+L\s*Hybrid)',
                r'(\d\.\d+L\s*Turbo)',
            ]
            for pattern in engine_patterns:
                m = re.search(pattern, text, re.IGNORECASE)
                if m:
                    vehicle['engine'] = m.group(1).strip()
                    break
            
            # Extract from data attributes
            for attr, value in element.attrs.items():
                if 'data-' not in attr.lower():
                    continue
                attr_lower = attr.lower()
                val_str = str(value)
                
                if 'year' in attr_lower and not vehicle['year']:
                    if re.match(r'^(19[89]\d|20[0-2]\d)$', val_str):
                        vehicle['year'] = val_str
                elif 'make' in attr_lower and not vehicle['makeName']:
                    vehicle['makeName'] = val_str.title()
                elif 'model' in attr_lower and not vehicle['model']:
                    vehicle['model'] = val_str
                elif 'stock' in attr_lower and not vehicle['stock_number']:
                    if len(val_str) >= 3:
                        vehicle['stock_number'] = val_str
                elif 'mileage' in attr_lower and not vehicle['mileage']:
                    clean = re.sub(r'[^\d]', '', val_str)
                    if clean and clean.isdigit():
                        vehicle['mileage'] = clean
            
            return vehicle
            
        except Exception as e:
            logger.debug("Error: {}".format(str(e)))
            return vehicle

    def is_valid_vehicle(self, vehicle):
        if not isinstance(vehicle, dict):
            return False
        
        has_year = bool(vehicle.get('year', '').strip())
        has_make = bool(vehicle.get('makeName', '').strip())
        
        if not (has_year and has_make):
            return False
        
        has_model = bool(vehicle.get('model', '').strip())
        has_price = bool(vehicle.get('value', '').strip() or vehicle.get('sale_value', '').strip())
        has_mileage = bool(vehicle.get('mileage', '').strip())
        has_stock = bool(vehicle.get('stock_number', '').strip())
        
        count = sum([has_price, has_mileage, has_stock])
        return has_model or count >= 2

    def find_vehicles(self, soup):
        vehicles = []
        
        selectors = [
            '[data-vehicle-id]', '[data-stock-number]', '[data-vin]',
            '.vehicle-card', '.inventory-item', '.vehicle-listing',
            'article[class*="vehicle"]', 'div[class*="vehicle"]',
            'li[class*="vehicle"]', '.vehicle', 'article', 'li[class*="item"]'
        ]
        
        for selector in selectors:
            elements = soup.select(selector)
            if elements:
                logger.info("Found {} elements: {}".format(len(elements), selector))
                
                for element in elements:
                    vehicle = self.extract_vehicle_data(element)
                    if self.is_valid_vehicle(vehicle):
                        vehicles.append(vehicle)
                        logger.info("Extracted: {} {} {} | Value: ${} | Sale: ${}".format(
                            vehicle['year'], vehicle['makeName'], 
                            vehicle['model'], vehicle.get('value', 'N/A'),
                            vehicle.get('sale_value', 'N/A')))
                
                if vehicles:
                    return vehicles
        
        # Fallback search
        all_divs = soup.find_all(['div', 'section', 'article', 'li'])
        for div in all_divs:
            text = div.get_text(separator=' ', strip=True)
            if re.search(r'\b(19[89]\d|20[0-2]\d)\b', text):
                for make in self.car_makes.keys():
                    if re.search(r'\b' + re.escape(make) + r'\b', text, re.IGNORECASE):
                        vehicle = self.extract_vehicle_data(div)
                        if self.is_valid_vehicle(vehicle):
                            vehicles.append(vehicle)
                            break
        
        return vehicles

    def scrape_inventory(self):
        logger.info("=" * 80)
        logger.info("UNIVERSAL RED DEER TOYOTA SCRAPER")
        logger.info("=" * 80)
        
        all_pages = self.fetch_all_pages()
        if not all_pages:
            logger.error("No pages fetched")
            return []
        
        all_vehicles = []
        
        for page_num, soup in all_pages:
            logger.info("Processing page {}".format(page_num))
            page_vehicles = self.find_vehicles(soup)
            logger.info("Page {} found {} vehicles".format(page_num, len(page_vehicles)))
            all_vehicles.extend(page_vehicles)
        
        logger.info("Total before dedup: {}".format(len(all_vehicles)))
        
        # Deduplicate
        unique = []
        seen = set()
        
        for v in all_vehicles:
            year = v.get('year', '')
            make = v.get('makeName', '')
            model = v.get('model', '')
            stock = v.get('stock_number', '')
            mileage = v.get('mileage', '')
            
            if stock:
                key = (year, make, model, stock)
            elif mileage:
                key = (year, make, model, mileage)
            else:
                key = (year, make, model, v.get('trim', ''))
            
            if key not in seen:
                seen.add(key)
                unique.append(v)
        
        self.vehicles = unique
        logger.info("FINAL: {} unique vehicles".format(len(self.vehicles)))
        logger.info("Removed {} duplicates".format(len(all_vehicles) - len(self.vehicles)))
        
        return self.vehicles

    def save_to_csv(self, filename):
        fields = ['makeName', 'year', 'model', 'sub-model', 'trim', 'mileage', 
                 'value', 'sale_value', 'stock_number', 'engine']
        
        if not self.vehicles:
            logger.info("No vehicles - not creating CSV")
            return False
        
        try:
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fields)
                writer.writeheader()
                for v in self.vehicles:
                    row = {field: v.get(field, '') for field in fields}
                    writer.writerow(row)
            
            logger.info("CSV saved: {}".format(filename))
            return True
        except Exception as e:
            logger.error("CSV error: {}".format(str(e)))
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
        sale_count = 0
        for v in self.vehicles:
            brand = v.get('makeName', 'Unknown')
            brands[brand] = brands.get(brand, 0) + 1
            if v.get('sale_value'):
                sale_count += 1
        
        print("\nBrand Distribution:")
        for brand, count in sorted(brands.items()):
            print("  {}: {}".format(brand, count))
        
        print("\nPricing Info:")
        print("  Vehicles with sale prices: {} ({:.1f}%)".format(
            sale_count, 100.0 * sale_count / len(self.vehicles) if self.vehicles else 0))
        
        print("\n{:<10} {:<6} {:<15} {:<10} {:<12} {:<12} {:<10}".format(
            'Make', 'Year', 'Model', 'Trim', 'Value', 'Sale Price', 'Stock#'))
        print("-" * 85)
        
        for v in self.vehicles:
            print("{:<10} {:<6} {:<15} {:<10} {:<12} {:<12} {:<10}".format(
                v.get('makeName', '')[:9],
                v.get('year', ''),
                v.get('model', '')[:14],
                v.get('trim', '')[:9],
                v.get('value', '')[:11],
                v.get('sale_value', '')[:11],
                v.get('stock_number', '')[:9]))

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
        else:
            print("\nNo CSV created")
            if os.path.exists(csv_path):
                os.remove(csv_path)
        
        return 0 if vehicles else 1
        
    except Exception as e:
        logger.error("Scraper failed: {}".format(str(e)))
        return 1

if __name__ == "__main__":
    exit(main())
