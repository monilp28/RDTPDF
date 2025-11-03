#!/usr/bin/env python3
"""
Red Deer Toyota Used Inventory Scraper - Universal Version
Extracts ONLY accurate data for ANY brand/model
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
            
            year_match = re.search(r'\b(19[89]\d|20[0-2]\d)\b', text)
            if year_match:
                vehicle['year'] = year_match.group(1)
            
            make, model = self.extract_make_and_model(text)
            if make:
                vehicle['makeName'] = make
            if model:
                vehicle['model'] = model
            
            trim = self.extract_trim(text, model)
            if trim:
                vehicle['trim'] = trim
                vehicle['sub-model'] = trim
            
            # COMPREHENSIVE PRICE EXTRACTION - NEW APPROACH
            all_prices = []
            price_contexts = []
            
            # Method 1: Find all dollar amounts with surrounding context
            for match in re.finditer(r'\$\s*([0-9,]+)', text):
                try:
                    price = int(match.group(1).replace(',', ''))
                    if 3000 <= price <= 300000:
                        start = max(0, match.start() - 100)
                        end = min(len(text), match.end() + 100)
                        context = text[start:end].lower()
                        all_prices.append(price)
                        price_contexts.append({
                            'price': price,
                            'context': context,
                            'position': match.start()
                        })
                except:
                    pass
            
            # Method 2: Look for specific span/div elements with price classes
            if hasattr(element, 'find_all'):
                for tag in element.find_all(['span', 'div', 'p', 'strong']):
                    tag_class = ' '.join(tag.get('class', [])).lower()
                    tag_text = tag.get_text().strip()
                    
                    # Check if element contains a price
                    price_match = re.search(r'\$?\s*([0-9,]+)', tag_text)
                    if price_match:
                        try:
                            price = int(price_match.group(1).replace(',', ''))
                            if 3000 <= price <= 300000:
                                all_prices.append(price)
                                price_contexts.append({
                                    'price': price,
                                    'context': tag_class + ' ' + tag_text.lower(),
                                    'position': -1,
                                    'element': tag.name,
                                    'class': tag_class
                                })
                        except:
                            pass
            
            # Method 3: Check ALL attributes for numeric values that could be prices
            for attr, value in element.attrs.items():
                attr_str = str(attr).lower()
                val_str = str(value).lower()
                
                # Look for numbers in attribute values
                for num_match in re.finditer(r'(\d{4,6})', val_str):
                    try:
                        price = int(num_match.group(1))
                        if 3000 <= price <= 300000:
                            all_prices.append(price)
                            price_contexts.append({
                                'price': price,
                                'context': attr_str + '=' + val_str,
                                'position': -1,
                                'source': 'attribute'
                            })
                    except:
                        pass
            
            # Remove duplicates while preserving context
            unique_prices = {}
            for ctx in price_contexts:
                price = ctx['price']
                if price not in unique_prices:
                    unique_prices[price] = ctx
            
            # Categorize prices based on context
            sale_prices = []
            original_prices = []
            
            sale_keywords = ['sale', 'special', 'internet', 'now', 'reduced', 'discount', 'clearance', 'offer']
            original_keywords = ['was', 'msrp', 'list', 'retail', 'original', 'before']
            
            for price, ctx in unique_prices.items():
                context = ctx['context']
                is_sale = any(kw in context for kw in sale_keywords)
                is_original = any(kw in context for kw in original_keywords)
                
                if is_sale:
                    sale_prices.append(price)
                    logger.debug("SALE: ${} | Context: {}".format(price, context[:80]))
                elif is_original:
                    original_prices.append(price)
                    logger.debug("ORIGINAL: ${} | Context: {}".format(price, context[:80]))
                else:
                    logger.debug("UNCATEGORIZED: ${} | Context: {}".format(price, context[:80]))
            
            # Decision logic
            final_value = None
            final_sale = None
            
            all_unique_prices = sorted(list(unique_prices.keys()), reverse=True)
            
            if sale_prices and original_prices:
                # We have both - use lowest sale and highest original
                final_sale = min(sale_prices)
                final_value = max(original_prices)
            elif sale_prices:
                # Only sale prices - use lowest as sale, find higher uncategorized as original
                final_sale = min(sale_prices)
                higher = [p for p in all_unique_prices if p > final_sale]
                if higher:
                    final_value = min(higher)
            elif original_prices:
                # Only original prices - use highest as original, find lower uncategorized as sale
                final_value = max(original_prices)
                lower = [p for p in all_unique_prices if p < final_value]
                if lower:
                    final_sale = max(lower)
            elif len(all_unique_prices) >= 2:
                # No keywords found - assume first two prices (highest is original, second is sale)
                final_value = all_unique_prices[0]
                final_sale = all_unique_prices[1]
            elif len(all_unique_prices) == 1:
                # Only one price
                final_value = all_unique_prices[0]
            
            # Final validation
            if final_value and final_sale:
                if final_sale >= final_value:
                    # Sale shouldn't be higher than original
                    final_sale = None
            
            if final_value:
                vehicle['value'] = str(final_value)
            if final_sale:
                vehicle['sale_value'] = str(final_sale)
            
            # Log final result
            if vehicle['makeName'] and vehicle['model']:
                logger.info("VEHICLE: {} {} {} | Value: ${} | Sale: ${}".format(
                    vehicle.get('year', '?'),
                    vehicle.get('makeName', '?'),
                    vehicle.get('model', '?'),
                    vehicle.get('value', 'NONE'),
                    vehicle.get('sale_value', 'NONE')
                ))
            
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
                    if re.match(r'^(19[89]\d|20[0-2]\d)
        vehicle = {
            'makeName': '', 'year': '', 'model': '', 'sub-model': '', 'trim': '',
            'mileage': '', 'value': '', 'sale_value': '', 'stock_number': '', 'engine': ''
        }
        
        try:
            text = element.get_text(separator=' ', strip=True)
            text = re.sub(r'\s+', ' ', text)
            
            # Get raw HTML to check for classes/attributes
            element_html = str(element)
            
            year_match = re.search(r'\b(19[89]\d|20[0-2]\d)\b', text)
            if year_match:
                vehicle['year'] = year_match.group(1)
            
            make, model = self.extract_make_and_model(text)
            if make:
                vehicle['makeName'] = make
            if model:
                vehicle['model'] = model
            
            trim = self.extract_trim(text, model)
            if trim:
                vehicle['trim'] = trim
                vehicle['sub-model'] = trim
            
            # ULTRA AGGRESSIVE PRICE EXTRACTION
            prices_found = {
                'sale': [],
                'original': [],
                'all': []
            }
            
            # Extract ALL prices from text with context
            price_pattern = r'(?:^|[^\d])(\$?\s*[0-9]{1,3}(?:,\d{3})+|\$?\s*[0-9]{5,6})(?:[^\d]|$)'
            for match in re.finditer(price_pattern, text):
                try:
                    price_str = match.group(1).replace('
        vehicle = {
            'makeName': '', 'year': '', 'model': '', 'sub-model': '', 'trim': '',
            'mileage': '', 'value': '', 'sale_value': '', 'stock_number': '', 'engine': ''
        }
        
        try:
            text = element.get_text(separator=' ', strip=True)
            text = re.sub(r'\s+', ' ', text)
            
            year_match = re.search(r'\b(19[89]\d|20[0-2]\d)\b', text)
            if year_match:
                vehicle['year'] = year_match.group(1)
            
            make, model = self.extract_make_and_model(text)
            if make:
                vehicle['makeName'] = make
            if model:
                vehicle['model'] = model
            
            trim = self.extract_trim(text, model)
            if trim:
                vehicle['trim'] = trim
                vehicle['sub-model'] = trim
            
            # ENHANCED PRICE EXTRACTION - Better sale price detection
            original_price = None
            sale_price = None
            
            # Pattern 1: Explicit sale/now price patterns
            sale_patterns = [
                r'(?:Sale\s*Price|Now|Special|Internet\s*Price)[:\s]*\$\s*([0-9,]+)',
                r'Sale[:\s]*\$\s*([0-9,]+)',
                r'Now[:\s]*\$\s*([0-9,]+)',
            ]
            
            for pattern in sale_patterns:
                m = re.search(pattern, text, re.IGNORECASE)
                if m:
                    try:
                        price = int(m.group(1).replace(',', ''))
                        if 3000 <= price <= 300000:
                            sale_price = price
                            break
                    except:
                        pass
            
            # Pattern 2: Was/List price patterns (original price)
            original_patterns = [
                r'(?:Was|List\s*Price|MSRP|Retail)[:\s]*\$\s*([0-9,]+)',
            ]
            
            for pattern in original_patterns:
                m = re.search(pattern, text, re.IGNORECASE)
                if m:
                    try:
                        price = int(m.group(1).replace(',', ''))
                        if 3000 <= price <= 300000:
                            original_price = price
                            break
                    except:
                        pass
            
            # Pattern 3: If no explicit patterns, find all prices
            if not sale_price and not original_price:
                all_prices = re.findall(r'\$\s*([0-9,]+)', text)
                valid_prices = []
                for price_str in all_prices:
                    try:
                        price = int(price_str.replace(',', ''))
                        if 3000 <= price <= 300000:
                            valid_prices.append(price)
                    except:
                        pass
                
                if len(valid_prices) >= 2:
                    # Sort prices - higher is likely original, lower is sale
                    valid_prices.sort(reverse=True)
                    original_price = valid_prices[0]
                    sale_price = valid_prices[1]
                elif len(valid_prices) == 1:
                    original_price = valid_prices[0]
            
            # Assign prices to vehicle dict
            if original_price:
                vehicle['value'] = str(original_price)
            if sale_price:
                vehicle['sale_value'] = str(sale_price)
            
            # If we have sale price but it's higher than original, swap them
            if vehicle['value'] and vehicle['sale_value']:
                if int(vehicle['sale_value']) > int(vehicle['value']):
                    vehicle['value'], vehicle['sale_value'] = vehicle['sale_value'], vehicle['value']
            
            mileage_patterns = [
                r'(\d{1,3}(?:,\d{3})*)\s*(?:km|kilometers?)\b',
                r'(\d{1,3}(?:,\d{3})*)\s*(?:miles?|mi)\b',
                r'(\d{1,3}(?:,\d{3})*)\s+km\b',
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
            
            for attr, value in element.attrs.items():
                if 'data-' not in attr.lower():
                    continue
                attr_lower = attr.lower()
                val_str = str(value)
                
                if 'year' in attr_lower and not vehicle['year']:
                    if re.match(r'^(19[89]\d|20[0-2]\d)

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
        
        first_element_saved = False
        
        for selector in selectors:
            elements = soup.select(selector)
            if elements:
                logger.info("Found {} elements: {}".format(len(elements), selector))
                
                for idx, element in enumerate(elements):
                    # Save first element HTML for debugging
                    if not first_element_saved:
                        try:
                            debug_file = os.path.join(os.getcwd(), 'debug_vehicle.html')
                            with open(debug_file, 'w', encoding='utf-8') as f:
                                f.write(str(element.prettify()))
                            logger.info("DEBUG: Saved first vehicle HTML to {}".format(debug_file))
                            first_element_saved = True
                        except:
                            pass
                    
                    vehicle = self.extract_vehicle_data(element)
                    if self.is_valid_vehicle(vehicle):
                        vehicles.append(vehicle)
                        logger.info("Extracted: {} {} {} {}".format(
                            vehicle['year'], vehicle['makeName'], 
                            vehicle['model'], vehicle.get('trim', '')))
                
                if vehicles:
                    return vehicles
        
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
        
        unique = []
        seen = set()
        
        for v in all_vehicles:
            year = v.get('year', '')
            make = v.get('makeName', '')
            model = v.get('model', '')
            stock = v.get('stock_number', '')
            mileage = v.get('mileage', '')
            price = v.get('value', '') or v.get('sale_value', '')
            
            if stock:
                key = (year, make, model, stock)
            elif mileage:
                key = (year, make, model, mileage)
            elif price:
                key = (year, make, model, price)
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
, val_str):
                        vehicle['year'] = val_str
                elif 'make' in attr_lower and not vehicle['makeName']:
                    vehicle['makeName'] = val_str.title()
                elif 'model' in attr_lower and not vehicle['model']:
                    vehicle['model'] = val_str
                elif 'trim' in attr_lower and not vehicle['trim']:
                    if vehicle['model'] and val_str.lower() not in vehicle['model'].lower():
                        vehicle['trim'] = val_str
                        vehicle['sub-model'] = val_str
                elif 'stock' in attr_lower and not vehicle['stock_number']:
                    if len(val_str) >= 3:
                        vehicle['stock_number'] = val_str
                elif 'mileage' in attr_lower and not vehicle['mileage']:
                    clean = re.sub(r'[^\d]', '', val_str)
                    if clean and clean.isdigit():
                        vehicle['mileage'] = clean
                elif 'sale' in attr_lower or 'special' in attr_lower:
                    clean = re.sub(r'[^\d]', '', val_str)
                    if clean and clean.isdigit() and 3000 <= int(clean) <= 300000:
                        if not vehicle['sale_value']:
                            vehicle['sale_value'] = clean
                elif 'price' in attr_lower and 'sale' not in attr_lower:
                    clean = re.sub(r'[^\d]', '', val_str)
                    if clean and clean.isdigit() and 3000 <= int(clean) <= 300000:
                        if not vehicle['value']:
                            vehicle['value'] = clean
            
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
                        logger.info("Extracted: {} {} {} {}".format(
                            vehicle['year'], vehicle['makeName'], 
                            vehicle['model'], vehicle.get('trim', '')))
                
                if vehicles:
                    return vehicles
        
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
        
        unique = []
        seen = set()
        
        for v in all_vehicles:
            year = v.get('year', '')
            make = v.get('makeName', '')
            model = v.get('model', '')
            stock = v.get('stock_number', '')
            mileage = v.get('mileage', '')
            price = v.get('value', '') or v.get('sale_value', '')
            
            if stock:
                key = (year, make, model, stock)
            elif mileage:
                key = (year, make, model, mileage)
            elif price:
                key = (year, make, model, price)
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
        for v in self.vehicles:
            brand = v.get('makeName', 'Unknown')
            brands[brand] = brands.get(brand, 0) + 1
        
        print("\nBrand Distribution:")
        for brand, count in sorted(brands.items()):
            print("  {}: {}".format(brand, count))
        
        print("\n{:<10} {:<6} {:<15} {:<10} {:<10} {:<10} {:<10}".format(
            'Make', 'Year', 'Model', 'Trim', 'Mileage', 'Value', 'Stock#'))
        print("-" * 80)
        
        for v in self.vehicles:
            print("{:<10} {:<6} {:<15} {:<10} {:<10} {:<10} {:<10}".format(
                v.get('makeName', '')[:9],
                v.get('year', ''),
                v.get('model', '')[:14],
                v.get('trim', '')[:9],
                v.get('mileage', '')[:9],
                v.get('value', '')[:9],
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
, '').replace(',', '').strip()
                    if price_str:
                        price = int(price_str)
                        if 3000 <= price <= 300000:
                            # Get context around price (50 chars before and after)
                            start = max(0, match.start() - 50)
                            end = min(len(text), match.end() + 50)
                            context = text[start:end].lower()
                            
                            prices_found['all'].append(price)
                            
                            # Categorize based on context
                            if any(word in context for word in ['sale', 'now', 'special', 'internet', 'discount', 'reduced', 'clearance']):
                                prices_found['sale'].append(price)
                                logger.debug("Found SALE price {} with context: ...{}...".format(price, context))
                            elif any(word in context for word in ['was', 'msrp', 'list', 'retail', 'original']):
                                prices_found['original'].append(price)
                                logger.debug("Found ORIGINAL price {} with context: ...{}...".format(price, context))
                except (ValueError, AttributeError):
                    pass
            
            # Check HTML for price-related classes and data attributes
            if hasattr(element, 'find_all'):
                # Look for elements with price-related classes
                for price_elem in element.find_all(class_=re.compile(r'price', re.I)):
                    elem_text = price_elem.get_text().strip()
                    elem_class = ' '.join(price_elem.get('class', [])).lower()
                    
                    price_match = re.search(r'[\$]?\s*([0-9,]+)', elem_text)
                    if price_match:
                        try:
                            price = int(price_match.group(1).replace(',', ''))
                            if 3000 <= price <= 300000:
                                if any(word in elem_class for word in ['sale', 'special', 'internet', 'now', 'discount']):
                                    prices_found['sale'].append(price)
                                    logger.debug("Found SALE price {} in class: {}".format(price, elem_class))
                                elif any(word in elem_class for word in ['msrp', 'list', 'retail', 'was', 'original']):
                                    prices_found['original'].append(price)
                                    logger.debug("Found ORIGINAL price {} in class: {}".format(price, elem_class))
                                else:
                                    prices_found['all'].append(price)
                        except:
                            pass
            
            # Check all data attributes
            for attr, value in element.attrs.items():
                attr_lower = attr.lower()
                val_str = str(value).lower()
                
                # Look for price in attribute value
                price_match = re.search(r'(\d+)', val_str)
                if price_match:
                    try:
                        price = int(price_match.group(1))
                        if 3000 <= price <= 300000:
                            if any(word in attr_lower for word in ['sale', 'special', 'internet', 'now', 'discount']):
                                prices_found['sale'].append(price)
                                logger.debug("Found SALE price {} in attr: {}".format(price, attr))
                            elif any(word in attr_lower for word in ['price', 'msrp', 'list', 'retail', 'was']):
                                if 'sale' not in attr_lower:
                                    prices_found['original'].append(price)
                                    logger.debug("Found ORIGINAL price {} in attr: {}".format(price, attr))
                    except:
                        pass
            
            # Deduplicate prices
            prices_found['sale'] = list(set(prices_found['sale']))
            prices_found['original'] = list(set(prices_found['original']))
            prices_found['all'] = list(set(prices_found['all']))
            
            logger.debug("All prices found - Sale: {}, Original: {}, All: {}".format(
                prices_found['sale'], prices_found['original'], prices_found['all']))
            
            # Decision logic for price assignment
            original_price = None
            sale_price = None
            
            # Case 1: We have both categorized sale and original prices
            if prices_found['sale'] and prices_found['original']:
                sale_price = min(prices_found['sale'])  # Lowest sale price
                original_price = max(prices_found['original'])  # Highest original price
                logger.debug("Case 1: Both found - Sale: {}, Original: {}".format(sale_price, original_price))
            
            # Case 2: Only sale prices found
            elif prices_found['sale']:
                sale_price = min(prices_found['sale'])
                # Try to find an original price from all prices that's higher
                higher_prices = [p for p in prices_found['all'] if p > sale_price]
                if higher_prices:
                    original_price = min(higher_prices)  # Use the smallest price that's higher than sale
                logger.debug("Case 2: Sale only - Sale: {}, Original: {}".format(sale_price, original_price))
            
            # Case 3: Only original prices found
            elif prices_found['original']:
                original_price = max(prices_found['original'])
                # Try to find a sale price from all prices that's lower
                lower_prices = [p for p in prices_found['all'] if p < original_price]
                if lower_prices:
                    sale_price = max(lower_prices)  # Use the highest price that's lower than original
                logger.debug("Case 3: Original only - Sale: {}, Original: {}".format(sale_price, original_price))
            
            # Case 4: No categorized prices, use all prices
            elif len(prices_found['all']) >= 2:
                sorted_prices = sorted(set(prices_found['all']), reverse=True)
                original_price = sorted_prices[0]
                sale_price = sorted_prices[1]
                logger.debug("Case 4: Multiple uncategorized - Sale: {}, Original: {}".format(sale_price, original_price))
            
            # Case 5: Only one price
            elif len(prices_found['all']) == 1:
                original_price = prices_found['all'][0]
                logger.debug("Case 5: Single price - Original: {}".format(original_price))
            
            # Validate: original should be higher than sale
            if original_price and sale_price:
                if sale_price >= original_price:
                    # If sale is same or higher, treat as single price
                    logger.debug("Sale >= Original, treating as single price")
                    sale_price = None
            
            # Assign to vehicle
            if original_price:
                vehicle['value'] = str(original_price)
            if sale_price:
                vehicle['sale_value'] = str(sale_price)
            
            logger.info("Final prices for {} {} {} - Value: ${}, Sale: ${}".format(
                vehicle.get('year', ''), vehicle.get('makeName', ''), vehicle.get('model', ''),
                vehicle.get('value', 'None'), vehicle.get('sale_value', 'None')))
            
            # Extract mileage
            mileage_patterns = [
                r'(\d{1,3}(?:,\d{3})*)\s*(?:km|kilometers?)\b',
                r'(\d{1,3}(?:,\d{3})*)\s*(?:miles?|mi)\b',
                r'(\d{1,3}(?:,\d{3})*)\s+km\b',
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
            
            # Extract from remaining data attributes
            for attr, value in element.attrs.items():
                if 'data-' not in attr.lower():
                    continue
                attr_lower = attr.lower()
                val_str = str(value)
                
                if 'year' in attr_lower and not vehicle['year']:
                    if re.match(r'^(19[89]\d|20[0-2]\d)
        vehicle = {
            'makeName': '', 'year': '', 'model': '', 'sub-model': '', 'trim': '',
            'mileage': '', 'value': '', 'sale_value': '', 'stock_number': '', 'engine': ''
        }
        
        try:
            text = element.get_text(separator=' ', strip=True)
            text = re.sub(r'\s+', ' ', text)
            
            year_match = re.search(r'\b(19[89]\d|20[0-2]\d)\b', text)
            if year_match:
                vehicle['year'] = year_match.group(1)
            
            make, model = self.extract_make_and_model(text)
            if make:
                vehicle['makeName'] = make
            if model:
                vehicle['model'] = model
            
            trim = self.extract_trim(text, model)
            if trim:
                vehicle['trim'] = trim
                vehicle['sub-model'] = trim
            
            # ENHANCED PRICE EXTRACTION - Better sale price detection
            original_price = None
            sale_price = None
            
            # Pattern 1: Explicit sale/now price patterns
            sale_patterns = [
                r'(?:Sale\s*Price|Now|Special|Internet\s*Price)[:\s]*\$\s*([0-9,]+)',
                r'Sale[:\s]*\$\s*([0-9,]+)',
                r'Now[:\s]*\$\s*([0-9,]+)',
            ]
            
            for pattern in sale_patterns:
                m = re.search(pattern, text, re.IGNORECASE)
                if m:
                    try:
                        price = int(m.group(1).replace(',', ''))
                        if 3000 <= price <= 300000:
                            sale_price = price
                            break
                    except:
                        pass
            
            # Pattern 2: Was/List price patterns (original price)
            original_patterns = [
                r'(?:Was|List\s*Price|MSRP|Retail)[:\s]*\$\s*([0-9,]+)',
            ]
            
            for pattern in original_patterns:
                m = re.search(pattern, text, re.IGNORECASE)
                if m:
                    try:
                        price = int(m.group(1).replace(',', ''))
                        if 3000 <= price <= 300000:
                            original_price = price
                            break
                    except:
                        pass
            
            # Pattern 3: If no explicit patterns, find all prices
            if not sale_price and not original_price:
                all_prices = re.findall(r'\$\s*([0-9,]+)', text)
                valid_prices = []
                for price_str in all_prices:
                    try:
                        price = int(price_str.replace(',', ''))
                        if 3000 <= price <= 300000:
                            valid_prices.append(price)
                    except:
                        pass
                
                if len(valid_prices) >= 2:
                    # Sort prices - higher is likely original, lower is sale
                    valid_prices.sort(reverse=True)
                    original_price = valid_prices[0]
                    sale_price = valid_prices[1]
                elif len(valid_prices) == 1:
                    original_price = valid_prices[0]
            
            # Assign prices to vehicle dict
            if original_price:
                vehicle['value'] = str(original_price)
            if sale_price:
                vehicle['sale_value'] = str(sale_price)
            
            # If we have sale price but it's higher than original, swap them
            if vehicle['value'] and vehicle['sale_value']:
                if int(vehicle['sale_value']) > int(vehicle['value']):
                    vehicle['value'], vehicle['sale_value'] = vehicle['sale_value'], vehicle['value']
            
            mileage_patterns = [
                r'(\d{1,3}(?:,\d{3})*)\s*(?:km|kilometers?)\b',
                r'(\d{1,3}(?:,\d{3})*)\s*(?:miles?|mi)\b',
                r'(\d{1,3}(?:,\d{3})*)\s+km\b',
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
            
            for attr, value in element.attrs.items():
                if 'data-' not in attr.lower():
                    continue
                attr_lower = attr.lower()
                val_str = str(value)
                
                if 'year' in attr_lower and not vehicle['year']:
                    if re.match(r'^(19[89]\d|20[0-2]\d)

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
                        logger.info("Extracted: {} {} {} {}".format(
                            vehicle['year'], vehicle['makeName'], 
                            vehicle['model'], vehicle.get('trim', '')))
                
                if vehicles:
                    return vehicles
        
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
        
        unique = []
        seen = set()
        
        for v in all_vehicles:
            year = v.get('year', '')
            make = v.get('makeName', '')
            model = v.get('model', '')
            stock = v.get('stock_number', '')
            mileage = v.get('mileage', '')
            price = v.get('value', '') or v.get('sale_value', '')
            
            if stock:
                key = (year, make, model, stock)
            elif mileage:
                key = (year, make, model, mileage)
            elif price:
                key = (year, make, model, price)
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
, val_str):
                        vehicle['year'] = val_str
                elif 'make' in attr_lower and not vehicle['makeName']:
                    vehicle['makeName'] = val_str.title()
                elif 'model' in attr_lower and not vehicle['model']:
                    vehicle['model'] = val_str
                elif 'trim' in attr_lower and not vehicle['trim']:
                    if vehicle['model'] and val_str.lower() not in vehicle['model'].lower():
                        vehicle['trim'] = val_str
                        vehicle['sub-model'] = val_str
                elif 'stock' in attr_lower and not vehicle['stock_number']:
                    if len(val_str) >= 3:
                        vehicle['stock_number'] = val_str
                elif 'mileage' in attr_lower and not vehicle['mileage']:
                    clean = re.sub(r'[^\d]', '', val_str)
                    if clean and clean.isdigit():
                        vehicle['mileage'] = clean
                elif 'sale' in attr_lower or 'special' in attr_lower:
                    clean = re.sub(r'[^\d]', '', val_str)
                    if clean and clean.isdigit() and 3000 <= int(clean) <= 300000:
                        if not vehicle['sale_value']:
                            vehicle['sale_value'] = clean
                elif 'price' in attr_lower and 'sale' not in attr_lower:
                    clean = re.sub(r'[^\d]', '', val_str)
                    if clean and clean.isdigit() and 3000 <= int(clean) <= 300000:
                        if not vehicle['value']:
                            vehicle['value'] = clean
            
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
                        logger.info("Extracted: {} {} {} {}".format(
                            vehicle['year'], vehicle['makeName'], 
                            vehicle['model'], vehicle.get('trim', '')))
                
                if vehicles:
                    return vehicles
        
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
        
        unique = []
        seen = set()
        
        for v in all_vehicles:
            year = v.get('year', '')
            make = v.get('makeName', '')
            model = v.get('model', '')
            stock = v.get('stock_number', '')
            mileage = v.get('mileage', '')
            price = v.get('value', '') or v.get('sale_value', '')
            
            if stock:
                key = (year, make, model, stock)
            elif mileage:
                key = (year, make, model, mileage)
            elif price:
                key = (year, make, model, price)
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
        for v in self.vehicles:
            brand = v.get('makeName', 'Unknown')
            brands[brand] = brands.get(brand, 0) + 1
        
        print("\nBrand Distribution:")
        for brand, count in sorted(brands.items()):
            print("  {}: {}".format(brand, count))
        
        print("\n{:<10} {:<6} {:<15} {:<10} {:<10} {:<10} {:<10}".format(
            'Make', 'Year', 'Model', 'Trim', 'Mileage', 'Value', 'Stock#'))
        print("-" * 80)
        
        for v in self.vehicles:
            print("{:<10} {:<6} {:<15} {:<10} {:<10} {:<10} {:<10}".format(
                v.get('makeName', '')[:9],
                v.get('year', ''),
                v.get('model', '')[:14],
                v.get('trim', '')[:9],
                v.get('mileage', '')[:9],
                v.get('value', '')[:9],
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
, val_str):
                        vehicle['year'] = val_str
                elif 'make' in attr_lower and not vehicle['makeName']:
                    vehicle['makeName'] = val_str.title()
                elif 'model' in attr_lower and not vehicle['model']:
                    vehicle['model'] = val_str
                elif 'trim' in attr_lower and not vehicle['trim']:
                    if vehicle['model'] and val_str.lower() not in vehicle['model'].lower():
                        vehicle['trim'] = val_str
                        vehicle['sub-model'] = val_str
                elif 'stock' in attr_lower and not vehicle['stock_number']:
                    if len(val_str) >= 3:
                        vehicle['stock_number'] = val_str
                elif 'mileage' in attr_lower and not vehicle['mileage']:
                    clean = re.sub(r'[^\d]', '', val_str)
                    if clean and clean.isdigit():
                        vehicle['mileage'] = clean
            
            return vehicle
            
        except Exception as e:
            logger.error("Error extracting vehicle: {}".format(str(e)))
            import traceback
            logger.error(traceback.format_exc())
            return vehicle
        vehicle = {
            'makeName': '', 'year': '', 'model': '', 'sub-model': '', 'trim': '',
            'mileage': '', 'value': '', 'sale_value': '', 'stock_number': '', 'engine': ''
        }
        
        try:
            text = element.get_text(separator=' ', strip=True)
            text = re.sub(r'\s+', ' ', text)
            
            year_match = re.search(r'\b(19[89]\d|20[0-2]\d)\b', text)
            if year_match:
                vehicle['year'] = year_match.group(1)
            
            make, model = self.extract_make_and_model(text)
            if make:
                vehicle['makeName'] = make
            if model:
                vehicle['model'] = model
            
            trim = self.extract_trim(text, model)
            if trim:
                vehicle['trim'] = trim
                vehicle['sub-model'] = trim
            
            # ENHANCED PRICE EXTRACTION - Better sale price detection
            original_price = None
            sale_price = None
            
            # Pattern 1: Explicit sale/now price patterns
            sale_patterns = [
                r'(?:Sale\s*Price|Now|Special|Internet\s*Price)[:\s]*\$\s*([0-9,]+)',
                r'Sale[:\s]*\$\s*([0-9,]+)',
                r'Now[:\s]*\$\s*([0-9,]+)',
            ]
            
            for pattern in sale_patterns:
                m = re.search(pattern, text, re.IGNORECASE)
                if m:
                    try:
                        price = int(m.group(1).replace(',', ''))
                        if 3000 <= price <= 300000:
                            sale_price = price
                            break
                    except:
                        pass
            
            # Pattern 2: Was/List price patterns (original price)
            original_patterns = [
                r'(?:Was|List\s*Price|MSRP|Retail)[:\s]*\$\s*([0-9,]+)',
            ]
            
            for pattern in original_patterns:
                m = re.search(pattern, text, re.IGNORECASE)
                if m:
                    try:
                        price = int(m.group(1).replace(',', ''))
                        if 3000 <= price <= 300000:
                            original_price = price
                            break
                    except:
                        pass
            
            # Pattern 3: If no explicit patterns, find all prices
            if not sale_price and not original_price:
                all_prices = re.findall(r'\$\s*([0-9,]+)', text)
                valid_prices = []
                for price_str in all_prices:
                    try:
                        price = int(price_str.replace(',', ''))
                        if 3000 <= price <= 300000:
                            valid_prices.append(price)
                    except:
                        pass
                
                if len(valid_prices) >= 2:
                    # Sort prices - higher is likely original, lower is sale
                    valid_prices.sort(reverse=True)
                    original_price = valid_prices[0]
                    sale_price = valid_prices[1]
                elif len(valid_prices) == 1:
                    original_price = valid_prices[0]
            
            # Assign prices to vehicle dict
            if original_price:
                vehicle['value'] = str(original_price)
            if sale_price:
                vehicle['sale_value'] = str(sale_price)
            
            # If we have sale price but it's higher than original, swap them
            if vehicle['value'] and vehicle['sale_value']:
                if int(vehicle['sale_value']) > int(vehicle['value']):
                    vehicle['value'], vehicle['sale_value'] = vehicle['sale_value'], vehicle['value']
            
            mileage_patterns = [
                r'(\d{1,3}(?:,\d{3})*)\s*(?:km|kilometers?)\b',
                r'(\d{1,3}(?:,\d{3})*)\s*(?:miles?|mi)\b',
                r'(\d{1,3}(?:,\d{3})*)\s+km\b',
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
            
            for attr, value in element.attrs.items():
                if 'data-' not in attr.lower():
                    continue
                attr_lower = attr.lower()
                val_str = str(value)
                
                if 'year' in attr_lower and not vehicle['year']:
                    if re.match(r'^(19[89]\d|20[0-2]\d)

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
                        logger.info("Extracted: {} {} {} {}".format(
                            vehicle['year'], vehicle['makeName'], 
                            vehicle['model'], vehicle.get('trim', '')))
                
                if vehicles:
                    return vehicles
        
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
        
        unique = []
        seen = set()
        
        for v in all_vehicles:
            year = v.get('year', '')
            make = v.get('makeName', '')
            model = v.get('model', '')
            stock = v.get('stock_number', '')
            mileage = v.get('mileage', '')
            price = v.get('value', '') or v.get('sale_value', '')
            
            if stock:
                key = (year, make, model, stock)
            elif mileage:
                key = (year, make, model, mileage)
            elif price:
                key = (year, make, model, price)
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
, val_str):
                        vehicle['year'] = val_str
                elif 'make' in attr_lower and not vehicle['makeName']:
                    vehicle['makeName'] = val_str.title()
                elif 'model' in attr_lower and not vehicle['model']:
                    vehicle['model'] = val_str
                elif 'trim' in attr_lower and not vehicle['trim']:
                    if vehicle['model'] and val_str.lower() not in vehicle['model'].lower():
                        vehicle['trim'] = val_str
                        vehicle['sub-model'] = val_str
                elif 'stock' in attr_lower and not vehicle['stock_number']:
                    if len(val_str) >= 3:
                        vehicle['stock_number'] = val_str
                elif 'mileage' in attr_lower and not vehicle['mileage']:
                    clean = re.sub(r'[^\d]', '', val_str)
                    if clean and clean.isdigit():
                        vehicle['mileage'] = clean
                elif 'sale' in attr_lower or 'special' in attr_lower:
                    clean = re.sub(r'[^\d]', '', val_str)
                    if clean and clean.isdigit() and 3000 <= int(clean) <= 300000:
                        if not vehicle['sale_value']:
                            vehicle['sale_value'] = clean
                elif 'price' in attr_lower and 'sale' not in attr_lower:
                    clean = re.sub(r'[^\d]', '', val_str)
                    if clean and clean.isdigit() and 3000 <= int(clean) <= 300000:
                        if not vehicle['value']:
                            vehicle['value'] = clean
            
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
                        logger.info("Extracted: {} {} {} {}".format(
                            vehicle['year'], vehicle['makeName'], 
                            vehicle['model'], vehicle.get('trim', '')))
                
                if vehicles:
                    return vehicles
        
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
        
        unique = []
        seen = set()
        
        for v in all_vehicles:
            year = v.get('year', '')
            make = v.get('makeName', '')
            model = v.get('model', '')
            stock = v.get('stock_number', '')
            mileage = v.get('mileage', '')
            price = v.get('value', '') or v.get('sale_value', '')
            
            if stock:
                key = (year, make, model, stock)
            elif mileage:
                key = (year, make, model, mileage)
            elif price:
                key = (year, make, model, price)
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
        for v in self.vehicles:
            brand = v.get('makeName', 'Unknown')
            brands[brand] = brands.get(brand, 0) + 1
        
        print("\nBrand Distribution:")
        for brand, count in sorted(brands.items()):
            print("  {}: {}".format(brand, count))
        
        print("\n{:<10} {:<6} {:<15} {:<10} {:<10} {:<10} {:<10}".format(
            'Make', 'Year', 'Model', 'Trim', 'Mileage', 'Value', 'Stock#'))
        print("-" * 80)
        
        for v in self.vehicles:
            print("{:<10} {:<6} {:<15} {:<10} {:<10} {:<10} {:<10}".format(
                v.get('makeName', '')[:9],
                v.get('year', ''),
                v.get('model', '')[:14],
                v.get('trim', '')[:9],
                v.get('mileage', '')[:9],
                v.get('value', '')[:9],
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
, val_str):
                        vehicle['year'] = val_str
                elif 'make' in attr_lower and not vehicle['makeName']:
                    vehicle['makeName'] = val_str.title()
                elif 'model' in attr_lower and not vehicle['model']:
                    vehicle['model'] = val_str
                elif 'trim' in attr_lower and not vehicle['trim']:
                    if vehicle['model'] and val_str.lower() not in vehicle['model'].lower():
                        vehicle['trim'] = val_str
                        vehicle['sub-model'] = val_str
                elif 'stock' in attr_lower and not vehicle['stock_number']:
                    if len(val_str) >= 3:
                        vehicle['stock_number'] = val_str
                elif 'mileage' in attr_lower and not vehicle['mileage']:
                    clean = re.sub(r'[^\d]', '', val_str)
                    if clean and clean.isdigit():
                        vehicle['mileage'] = clean
            
            return vehicle
            
        except Exception as e:
            logger.error("Error: {}".format(str(e)))
            import traceback
            logger.error(traceback.format_exc())
            return vehicle
        vehicle = {
            'makeName': '', 'year': '', 'model': '', 'sub-model': '', 'trim': '',
            'mileage': '', 'value': '', 'sale_value': '', 'stock_number': '', 'engine': ''
        }
        
        try:
            text = element.get_text(separator=' ', strip=True)
            text = re.sub(r'\s+', ' ', text)
            
            # Get raw HTML to check for classes/attributes
            element_html = str(element)
            
            year_match = re.search(r'\b(19[89]\d|20[0-2]\d)\b', text)
            if year_match:
                vehicle['year'] = year_match.group(1)
            
            make, model = self.extract_make_and_model(text)
            if make:
                vehicle['makeName'] = make
            if model:
                vehicle['model'] = model
            
            trim = self.extract_trim(text, model)
            if trim:
                vehicle['trim'] = trim
                vehicle['sub-model'] = trim
            
            # ULTRA AGGRESSIVE PRICE EXTRACTION
            prices_found = {
                'sale': [],
                'original': [],
                'all': []
            }
            
            # Extract ALL prices from text with context
            price_pattern = r'(?:^|[^\d])(\$?\s*[0-9]{1,3}(?:,\d{3})+|\$?\s*[0-9]{5,6})(?:[^\d]|$)'
            for match in re.finditer(price_pattern, text):
                try:
                    price_str = match.group(1).replace('
        vehicle = {
            'makeName': '', 'year': '', 'model': '', 'sub-model': '', 'trim': '',
            'mileage': '', 'value': '', 'sale_value': '', 'stock_number': '', 'engine': ''
        }
        
        try:
            text = element.get_text(separator=' ', strip=True)
            text = re.sub(r'\s+', ' ', text)
            
            year_match = re.search(r'\b(19[89]\d|20[0-2]\d)\b', text)
            if year_match:
                vehicle['year'] = year_match.group(1)
            
            make, model = self.extract_make_and_model(text)
            if make:
                vehicle['makeName'] = make
            if model:
                vehicle['model'] = model
            
            trim = self.extract_trim(text, model)
            if trim:
                vehicle['trim'] = trim
                vehicle['sub-model'] = trim
            
            # ENHANCED PRICE EXTRACTION - Better sale price detection
            original_price = None
            sale_price = None
            
            # Pattern 1: Explicit sale/now price patterns
            sale_patterns = [
                r'(?:Sale\s*Price|Now|Special|Internet\s*Price)[:\s]*\$\s*([0-9,]+)',
                r'Sale[:\s]*\$\s*([0-9,]+)',
                r'Now[:\s]*\$\s*([0-9,]+)',
            ]
            
            for pattern in sale_patterns:
                m = re.search(pattern, text, re.IGNORECASE)
                if m:
                    try:
                        price = int(m.group(1).replace(',', ''))
                        if 3000 <= price <= 300000:
                            sale_price = price
                            break
                    except:
                        pass
            
            # Pattern 2: Was/List price patterns (original price)
            original_patterns = [
                r'(?:Was|List\s*Price|MSRP|Retail)[:\s]*\$\s*([0-9,]+)',
            ]
            
            for pattern in original_patterns:
                m = re.search(pattern, text, re.IGNORECASE)
                if m:
                    try:
                        price = int(m.group(1).replace(',', ''))
                        if 3000 <= price <= 300000:
                            original_price = price
                            break
                    except:
                        pass
            
            # Pattern 3: If no explicit patterns, find all prices
            if not sale_price and not original_price:
                all_prices = re.findall(r'\$\s*([0-9,]+)', text)
                valid_prices = []
                for price_str in all_prices:
                    try:
                        price = int(price_str.replace(',', ''))
                        if 3000 <= price <= 300000:
                            valid_prices.append(price)
                    except:
                        pass
                
                if len(valid_prices) >= 2:
                    # Sort prices - higher is likely original, lower is sale
                    valid_prices.sort(reverse=True)
                    original_price = valid_prices[0]
                    sale_price = valid_prices[1]
                elif len(valid_prices) == 1:
                    original_price = valid_prices[0]
            
            # Assign prices to vehicle dict
            if original_price:
                vehicle['value'] = str(original_price)
            if sale_price:
                vehicle['sale_value'] = str(sale_price)
            
            # If we have sale price but it's higher than original, swap them
            if vehicle['value'] and vehicle['sale_value']:
                if int(vehicle['sale_value']) > int(vehicle['value']):
                    vehicle['value'], vehicle['sale_value'] = vehicle['sale_value'], vehicle['value']
            
            mileage_patterns = [
                r'(\d{1,3}(?:,\d{3})*)\s*(?:km|kilometers?)\b',
                r'(\d{1,3}(?:,\d{3})*)\s*(?:miles?|mi)\b',
                r'(\d{1,3}(?:,\d{3})*)\s+km\b',
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
            
            for attr, value in element.attrs.items():
                if 'data-' not in attr.lower():
                    continue
                attr_lower = attr.lower()
                val_str = str(value)
                
                if 'year' in attr_lower and not vehicle['year']:
                    if re.match(r'^(19[89]\d|20[0-2]\d)

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
                        logger.info("Extracted: {} {} {} {}".format(
                            vehicle['year'], vehicle['makeName'], 
                            vehicle['model'], vehicle.get('trim', '')))
                
                if vehicles:
                    return vehicles
        
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
        
        unique = []
        seen = set()
        
        for v in all_vehicles:
            year = v.get('year', '')
            make = v.get('makeName', '')
            model = v.get('model', '')
            stock = v.get('stock_number', '')
            mileage = v.get('mileage', '')
            price = v.get('value', '') or v.get('sale_value', '')
            
            if stock:
                key = (year, make, model, stock)
            elif mileage:
                key = (year, make, model, mileage)
            elif price:
                key = (year, make, model, price)
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
, val_str):
                        vehicle['year'] = val_str
                elif 'make' in attr_lower and not vehicle['makeName']:
                    vehicle['makeName'] = val_str.title()
                elif 'model' in attr_lower and not vehicle['model']:
                    vehicle['model'] = val_str
                elif 'trim' in attr_lower and not vehicle['trim']:
                    if vehicle['model'] and val_str.lower() not in vehicle['model'].lower():
                        vehicle['trim'] = val_str
                        vehicle['sub-model'] = val_str
                elif 'stock' in attr_lower and not vehicle['stock_number']:
                    if len(val_str) >= 3:
                        vehicle['stock_number'] = val_str
                elif 'mileage' in attr_lower and not vehicle['mileage']:
                    clean = re.sub(r'[^\d]', '', val_str)
                    if clean and clean.isdigit():
                        vehicle['mileage'] = clean
                elif 'sale' in attr_lower or 'special' in attr_lower:
                    clean = re.sub(r'[^\d]', '', val_str)
                    if clean and clean.isdigit() and 3000 <= int(clean) <= 300000:
                        if not vehicle['sale_value']:
                            vehicle['sale_value'] = clean
                elif 'price' in attr_lower and 'sale' not in attr_lower:
                    clean = re.sub(r'[^\d]', '', val_str)
                    if clean and clean.isdigit() and 3000 <= int(clean) <= 300000:
                        if not vehicle['value']:
                            vehicle['value'] = clean
            
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
                        logger.info("Extracted: {} {} {} {}".format(
                            vehicle['year'], vehicle['makeName'], 
                            vehicle['model'], vehicle.get('trim', '')))
                
                if vehicles:
                    return vehicles
        
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
        
        unique = []
        seen = set()
        
        for v in all_vehicles:
            year = v.get('year', '')
            make = v.get('makeName', '')
            model = v.get('model', '')
            stock = v.get('stock_number', '')
            mileage = v.get('mileage', '')
            price = v.get('value', '') or v.get('sale_value', '')
            
            if stock:
                key = (year, make, model, stock)
            elif mileage:
                key = (year, make, model, mileage)
            elif price:
                key = (year, make, model, price)
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
        for v in self.vehicles:
            brand = v.get('makeName', 'Unknown')
            brands[brand] = brands.get(brand, 0) + 1
        
        print("\nBrand Distribution:")
        for brand, count in sorted(brands.items()):
            print("  {}: {}".format(brand, count))
        
        print("\n{:<10} {:<6} {:<15} {:<10} {:<10} {:<10} {:<10}".format(
            'Make', 'Year', 'Model', 'Trim', 'Mileage', 'Value', 'Stock#'))
        print("-" * 80)
        
        for v in self.vehicles:
            print("{:<10} {:<6} {:<15} {:<10} {:<10} {:<10} {:<10}".format(
                v.get('makeName', '')[:9],
                v.get('year', ''),
                v.get('model', '')[:14],
                v.get('trim', '')[:9],
                v.get('mileage', '')[:9],
                v.get('value', '')[:9],
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
, '').replace(',', '').strip()
                    if price_str:
                        price = int(price_str)
                        if 3000 <= price <= 300000:
                            # Get context around price (50 chars before and after)
                            start = max(0, match.start() - 50)
                            end = min(len(text), match.end() + 50)
                            context = text[start:end].lower()
                            
                            prices_found['all'].append(price)
                            
                            # Categorize based on context
                            if any(word in context for word in ['sale', 'now', 'special', 'internet', 'discount', 'reduced', 'clearance']):
                                prices_found['sale'].append(price)
                                logger.debug("Found SALE price {} with context: ...{}...".format(price, context))
                            elif any(word in context for word in ['was', 'msrp', 'list', 'retail', 'original']):
                                prices_found['original'].append(price)
                                logger.debug("Found ORIGINAL price {} with context: ...{}...".format(price, context))
                except (ValueError, AttributeError):
                    pass
            
            # Check HTML for price-related classes and data attributes
            if hasattr(element, 'find_all'):
                # Look for elements with price-related classes
                for price_elem in element.find_all(class_=re.compile(r'price', re.I)):
                    elem_text = price_elem.get_text().strip()
                    elem_class = ' '.join(price_elem.get('class', [])).lower()
                    
                    price_match = re.search(r'[\$]?\s*([0-9,]+)', elem_text)
                    if price_match:
                        try:
                            price = int(price_match.group(1).replace(',', ''))
                            if 3000 <= price <= 300000:
                                if any(word in elem_class for word in ['sale', 'special', 'internet', 'now', 'discount']):
                                    prices_found['sale'].append(price)
                                    logger.debug("Found SALE price {} in class: {}".format(price, elem_class))
                                elif any(word in elem_class for word in ['msrp', 'list', 'retail', 'was', 'original']):
                                    prices_found['original'].append(price)
                                    logger.debug("Found ORIGINAL price {} in class: {}".format(price, elem_class))
                                else:
                                    prices_found['all'].append(price)
                        except:
                            pass
            
            # Check all data attributes
            for attr, value in element.attrs.items():
                attr_lower = attr.lower()
                val_str = str(value).lower()
                
                # Look for price in attribute value
                price_match = re.search(r'(\d+)', val_str)
                if price_match:
                    try:
                        price = int(price_match.group(1))
                        if 3000 <= price <= 300000:
                            if any(word in attr_lower for word in ['sale', 'special', 'internet', 'now', 'discount']):
                                prices_found['sale'].append(price)
                                logger.debug("Found SALE price {} in attr: {}".format(price, attr))
                            elif any(word in attr_lower for word in ['price', 'msrp', 'list', 'retail', 'was']):
                                if 'sale' not in attr_lower:
                                    prices_found['original'].append(price)
                                    logger.debug("Found ORIGINAL price {} in attr: {}".format(price, attr))
                    except:
                        pass
            
            # Deduplicate prices
            prices_found['sale'] = list(set(prices_found['sale']))
            prices_found['original'] = list(set(prices_found['original']))
            prices_found['all'] = list(set(prices_found['all']))
            
            logger.debug("All prices found - Sale: {}, Original: {}, All: {}".format(
                prices_found['sale'], prices_found['original'], prices_found['all']))
            
            # Decision logic for price assignment
            original_price = None
            sale_price = None
            
            # Case 1: We have both categorized sale and original prices
            if prices_found['sale'] and prices_found['original']:
                sale_price = min(prices_found['sale'])  # Lowest sale price
                original_price = max(prices_found['original'])  # Highest original price
                logger.debug("Case 1: Both found - Sale: {}, Original: {}".format(sale_price, original_price))
            
            # Case 2: Only sale prices found
            elif prices_found['sale']:
                sale_price = min(prices_found['sale'])
                # Try to find an original price from all prices that's higher
                higher_prices = [p for p in prices_found['all'] if p > sale_price]
                if higher_prices:
                    original_price = min(higher_prices)  # Use the smallest price that's higher than sale
                logger.debug("Case 2: Sale only - Sale: {}, Original: {}".format(sale_price, original_price))
            
            # Case 3: Only original prices found
            elif prices_found['original']:
                original_price = max(prices_found['original'])
                # Try to find a sale price from all prices that's lower
                lower_prices = [p for p in prices_found['all'] if p < original_price]
                if lower_prices:
                    sale_price = max(lower_prices)  # Use the highest price that's lower than original
                logger.debug("Case 3: Original only - Sale: {}, Original: {}".format(sale_price, original_price))
            
            # Case 4: No categorized prices, use all prices
            elif len(prices_found['all']) >= 2:
                sorted_prices = sorted(set(prices_found['all']), reverse=True)
                original_price = sorted_prices[0]
                sale_price = sorted_prices[1]
                logger.debug("Case 4: Multiple uncategorized - Sale: {}, Original: {}".format(sale_price, original_price))
            
            # Case 5: Only one price
            elif len(prices_found['all']) == 1:
                original_price = prices_found['all'][0]
                logger.debug("Case 5: Single price - Original: {}".format(original_price))
            
            # Validate: original should be higher than sale
            if original_price and sale_price:
                if sale_price >= original_price:
                    # If sale is same or higher, treat as single price
                    logger.debug("Sale >= Original, treating as single price")
                    sale_price = None
            
            # Assign to vehicle
            if original_price:
                vehicle['value'] = str(original_price)
            if sale_price:
                vehicle['sale_value'] = str(sale_price)
            
            logger.info("Final prices for {} {} {} - Value: ${}, Sale: ${}".format(
                vehicle.get('year', ''), vehicle.get('makeName', ''), vehicle.get('model', ''),
                vehicle.get('value', 'None'), vehicle.get('sale_value', 'None')))
            
            # Extract mileage
            mileage_patterns = [
                r'(\d{1,3}(?:,\d{3})*)\s*(?:km|kilometers?)\b',
                r'(\d{1,3}(?:,\d{3})*)\s*(?:miles?|mi)\b',
                r'(\d{1,3}(?:,\d{3})*)\s+km\b',
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
            
            # Extract from remaining data attributes
            for attr, value in element.attrs.items():
                if 'data-' not in attr.lower():
                    continue
                attr_lower = attr.lower()
                val_str = str(value)
                
                if 'year' in attr_lower and not vehicle['year']:
                    if re.match(r'^(19[89]\d|20[0-2]\d)
        vehicle = {
            'makeName': '', 'year': '', 'model': '', 'sub-model': '', 'trim': '',
            'mileage': '', 'value': '', 'sale_value': '', 'stock_number': '', 'engine': ''
        }
        
        try:
            text = element.get_text(separator=' ', strip=True)
            text = re.sub(r'\s+', ' ', text)
            
            year_match = re.search(r'\b(19[89]\d|20[0-2]\d)\b', text)
            if year_match:
                vehicle['year'] = year_match.group(1)
            
            make, model = self.extract_make_and_model(text)
            if make:
                vehicle['makeName'] = make
            if model:
                vehicle['model'] = model
            
            trim = self.extract_trim(text, model)
            if trim:
                vehicle['trim'] = trim
                vehicle['sub-model'] = trim
            
            # ENHANCED PRICE EXTRACTION - Better sale price detection
            original_price = None
            sale_price = None
            
            # Pattern 1: Explicit sale/now price patterns
            sale_patterns = [
                r'(?:Sale\s*Price|Now|Special|Internet\s*Price)[:\s]*\$\s*([0-9,]+)',
                r'Sale[:\s]*\$\s*([0-9,]+)',
                r'Now[:\s]*\$\s*([0-9,]+)',
            ]
            
            for pattern in sale_patterns:
                m = re.search(pattern, text, re.IGNORECASE)
                if m:
                    try:
                        price = int(m.group(1).replace(',', ''))
                        if 3000 <= price <= 300000:
                            sale_price = price
                            break
                    except:
                        pass
            
            # Pattern 2: Was/List price patterns (original price)
            original_patterns = [
                r'(?:Was|List\s*Price|MSRP|Retail)[:\s]*\$\s*([0-9,]+)',
            ]
            
            for pattern in original_patterns:
                m = re.search(pattern, text, re.IGNORECASE)
                if m:
                    try:
                        price = int(m.group(1).replace(',', ''))
                        if 3000 <= price <= 300000:
                            original_price = price
                            break
                    except:
                        pass
            
            # Pattern 3: If no explicit patterns, find all prices
            if not sale_price and not original_price:
                all_prices = re.findall(r'\$\s*([0-9,]+)', text)
                valid_prices = []
                for price_str in all_prices:
                    try:
                        price = int(price_str.replace(',', ''))
                        if 3000 <= price <= 300000:
                            valid_prices.append(price)
                    except:
                        pass
                
                if len(valid_prices) >= 2:
                    # Sort prices - higher is likely original, lower is sale
                    valid_prices.sort(reverse=True)
                    original_price = valid_prices[0]
                    sale_price = valid_prices[1]
                elif len(valid_prices) == 1:
                    original_price = valid_prices[0]
            
            # Assign prices to vehicle dict
            if original_price:
                vehicle['value'] = str(original_price)
            if sale_price:
                vehicle['sale_value'] = str(sale_price)
            
            # If we have sale price but it's higher than original, swap them
            if vehicle['value'] and vehicle['sale_value']:
                if int(vehicle['sale_value']) > int(vehicle['value']):
                    vehicle['value'], vehicle['sale_value'] = vehicle['sale_value'], vehicle['value']
            
            mileage_patterns = [
                r'(\d{1,3}(?:,\d{3})*)\s*(?:km|kilometers?)\b',
                r'(\d{1,3}(?:,\d{3})*)\s*(?:miles?|mi)\b',
                r'(\d{1,3}(?:,\d{3})*)\s+km\b',
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
            
            for attr, value in element.attrs.items():
                if 'data-' not in attr.lower():
                    continue
                attr_lower = attr.lower()
                val_str = str(value)
                
                if 'year' in attr_lower and not vehicle['year']:
                    if re.match(r'^(19[89]\d|20[0-2]\d)

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
                        logger.info("Extracted: {} {} {} {}".format(
                            vehicle['year'], vehicle['makeName'], 
                            vehicle['model'], vehicle.get('trim', '')))
                
                if vehicles:
                    return vehicles
        
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
        
        unique = []
        seen = set()
        
        for v in all_vehicles:
            year = v.get('year', '')
            make = v.get('makeName', '')
            model = v.get('model', '')
            stock = v.get('stock_number', '')
            mileage = v.get('mileage', '')
            price = v.get('value', '') or v.get('sale_value', '')
            
            if stock:
                key = (year, make, model, stock)
            elif mileage:
                key = (year, make, model, mileage)
            elif price:
                key = (year, make, model, price)
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
, val_str):
                        vehicle['year'] = val_str
                elif 'make' in attr_lower and not vehicle['makeName']:
                    vehicle['makeName'] = val_str.title()
                elif 'model' in attr_lower and not vehicle['model']:
                    vehicle['model'] = val_str
                elif 'trim' in attr_lower and not vehicle['trim']:
                    if vehicle['model'] and val_str.lower() not in vehicle['model'].lower():
                        vehicle['trim'] = val_str
                        vehicle['sub-model'] = val_str
                elif 'stock' in attr_lower and not vehicle['stock_number']:
                    if len(val_str) >= 3:
                        vehicle['stock_number'] = val_str
                elif 'mileage' in attr_lower and not vehicle['mileage']:
                    clean = re.sub(r'[^\d]', '', val_str)
                    if clean and clean.isdigit():
                        vehicle['mileage'] = clean
                elif 'sale' in attr_lower or 'special' in attr_lower:
                    clean = re.sub(r'[^\d]', '', val_str)
                    if clean and clean.isdigit() and 3000 <= int(clean) <= 300000:
                        if not vehicle['sale_value']:
                            vehicle['sale_value'] = clean
                elif 'price' in attr_lower and 'sale' not in attr_lower:
                    clean = re.sub(r'[^\d]', '', val_str)
                    if clean and clean.isdigit() and 3000 <= int(clean) <= 300000:
                        if not vehicle['value']:
                            vehicle['value'] = clean
            
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
                        logger.info("Extracted: {} {} {} {}".format(
                            vehicle['year'], vehicle['makeName'], 
                            vehicle['model'], vehicle.get('trim', '')))
                
                if vehicles:
                    return vehicles
        
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
        
        unique = []
        seen = set()
        
        for v in all_vehicles:
            year = v.get('year', '')
            make = v.get('makeName', '')
            model = v.get('model', '')
            stock = v.get('stock_number', '')
            mileage = v.get('mileage', '')
            price = v.get('value', '') or v.get('sale_value', '')
            
            if stock:
                key = (year, make, model, stock)
            elif mileage:
                key = (year, make, model, mileage)
            elif price:
                key = (year, make, model, price)
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
        for v in self.vehicles:
            brand = v.get('makeName', 'Unknown')
            brands[brand] = brands.get(brand, 0) + 1
        
        print("\nBrand Distribution:")
        for brand, count in sorted(brands.items()):
            print("  {}: {}".format(brand, count))
        
        print("\n{:<10} {:<6} {:<15} {:<10} {:<10} {:<10} {:<10}".format(
            'Make', 'Year', 'Model', 'Trim', 'Mileage', 'Value', 'Stock#'))
        print("-" * 80)
        
        for v in self.vehicles:
            print("{:<10} {:<6} {:<15} {:<10} {:<10} {:<10} {:<10}".format(
                v.get('makeName', '')[:9],
                v.get('year', ''),
                v.get('model', '')[:14],
                v.get('trim', '')[:9],
                v.get('mileage', '')[:9],
                v.get('value', '')[:9],
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
, val_str):
                        vehicle['year'] = val_str
                elif 'make' in attr_lower and not vehicle['makeName']:
                    vehicle['makeName'] = val_str.title()
                elif 'model' in attr_lower and not vehicle['model']:
                    vehicle['model'] = val_str
                elif 'trim' in attr_lower and not vehicle['trim']:
                    if vehicle['model'] and val_str.lower() not in vehicle['model'].lower():
                        vehicle['trim'] = val_str
                        vehicle['sub-model'] = val_str
                elif 'stock' in attr_lower and not vehicle['stock_number']:
                    if len(val_str) >= 3:
                        vehicle['stock_number'] = val_str
                elif 'mileage' in attr_lower and not vehicle['mileage']:
                    clean = re.sub(r'[^\d]', '', val_str)
                    if clean and clean.isdigit():
                        vehicle['mileage'] = clean
            
            return vehicle
            
        except Exception as e:
            logger.error("Error extracting vehicle: {}".format(str(e)))
            import traceback
            logger.error(traceback.format_exc())
            return vehicle
        vehicle = {
            'makeName': '', 'year': '', 'model': '', 'sub-model': '', 'trim': '',
            'mileage': '', 'value': '', 'sale_value': '', 'stock_number': '', 'engine': ''
        }
        
        try:
            text = element.get_text(separator=' ', strip=True)
            text = re.sub(r'\s+', ' ', text)
            
            year_match = re.search(r'\b(19[89]\d|20[0-2]\d)\b', text)
            if year_match:
                vehicle['year'] = year_match.group(1)
            
            make, model = self.extract_make_and_model(text)
            if make:
                vehicle['makeName'] = make
            if model:
                vehicle['model'] = model
            
            trim = self.extract_trim(text, model)
            if trim:
                vehicle['trim'] = trim
                vehicle['sub-model'] = trim
            
            # ENHANCED PRICE EXTRACTION - Better sale price detection
            original_price = None
            sale_price = None
            
            # Pattern 1: Explicit sale/now price patterns
            sale_patterns = [
                r'(?:Sale\s*Price|Now|Special|Internet\s*Price)[:\s]*\$\s*([0-9,]+)',
                r'Sale[:\s]*\$\s*([0-9,]+)',
                r'Now[:\s]*\$\s*([0-9,]+)',
            ]
            
            for pattern in sale_patterns:
                m = re.search(pattern, text, re.IGNORECASE)
                if m:
                    try:
                        price = int(m.group(1).replace(',', ''))
                        if 3000 <= price <= 300000:
                            sale_price = price
                            break
                    except:
                        pass
            
            # Pattern 2: Was/List price patterns (original price)
            original_patterns = [
                r'(?:Was|List\s*Price|MSRP|Retail)[:\s]*\$\s*([0-9,]+)',
            ]
            
            for pattern in original_patterns:
                m = re.search(pattern, text, re.IGNORECASE)
                if m:
                    try:
                        price = int(m.group(1).replace(',', ''))
                        if 3000 <= price <= 300000:
                            original_price = price
                            break
                    except:
                        pass
            
            # Pattern 3: If no explicit patterns, find all prices
            if not sale_price and not original_price:
                all_prices = re.findall(r'\$\s*([0-9,]+)', text)
                valid_prices = []
                for price_str in all_prices:
                    try:
                        price = int(price_str.replace(',', ''))
                        if 3000 <= price <= 300000:
                            valid_prices.append(price)
                    except:
                        pass
                
                if len(valid_prices) >= 2:
                    # Sort prices - higher is likely original, lower is sale
                    valid_prices.sort(reverse=True)
                    original_price = valid_prices[0]
                    sale_price = valid_prices[1]
                elif len(valid_prices) == 1:
                    original_price = valid_prices[0]
            
            # Assign prices to vehicle dict
            if original_price:
                vehicle['value'] = str(original_price)
            if sale_price:
                vehicle['sale_value'] = str(sale_price)
            
            # If we have sale price but it's higher than original, swap them
            if vehicle['value'] and vehicle['sale_value']:
                if int(vehicle['sale_value']) > int(vehicle['value']):
                    vehicle['value'], vehicle['sale_value'] = vehicle['sale_value'], vehicle['value']
            
            mileage_patterns = [
                r'(\d{1,3}(?:,\d{3})*)\s*(?:km|kilometers?)\b',
                r'(\d{1,3}(?:,\d{3})*)\s*(?:miles?|mi)\b',
                r'(\d{1,3}(?:,\d{3})*)\s+km\b',
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
            
            for attr, value in element.attrs.items():
                if 'data-' not in attr.lower():
                    continue
                attr_lower = attr.lower()
                val_str = str(value)
                
                if 'year' in attr_lower and not vehicle['year']:
                    if re.match(r'^(19[89]\d|20[0-2]\d)

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
                        logger.info("Extracted: {} {} {} {}".format(
                            vehicle['year'], vehicle['makeName'], 
                            vehicle['model'], vehicle.get('trim', '')))
                
                if vehicles:
                    return vehicles
        
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
        
        unique = []
        seen = set()
        
        for v in all_vehicles:
            year = v.get('year', '')
            make = v.get('makeName', '')
            model = v.get('model', '')
            stock = v.get('stock_number', '')
            mileage = v.get('mileage', '')
            price = v.get('value', '') or v.get('sale_value', '')
            
            if stock:
                key = (year, make, model, stock)
            elif mileage:
                key = (year, make, model, mileage)
            elif price:
                key = (year, make, model, price)
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
, val_str):
                        vehicle['year'] = val_str
                elif 'make' in attr_lower and not vehicle['makeName']:
                    vehicle['makeName'] = val_str.title()
                elif 'model' in attr_lower and not vehicle['model']:
                    vehicle['model'] = val_str
                elif 'trim' in attr_lower and not vehicle['trim']:
                    if vehicle['model'] and val_str.lower() not in vehicle['model'].lower():
                        vehicle['trim'] = val_str
                        vehicle['sub-model'] = val_str
                elif 'stock' in attr_lower and not vehicle['stock_number']:
                    if len(val_str) >= 3:
                        vehicle['stock_number'] = val_str
                elif 'mileage' in attr_lower and not vehicle['mileage']:
                    clean = re.sub(r'[^\d]', '', val_str)
                    if clean and clean.isdigit():
                        vehicle['mileage'] = clean
                elif 'sale' in attr_lower or 'special' in attr_lower:
                    clean = re.sub(r'[^\d]', '', val_str)
                    if clean and clean.isdigit() and 3000 <= int(clean) <= 300000:
                        if not vehicle['sale_value']:
                            vehicle['sale_value'] = clean
                elif 'price' in attr_lower and 'sale' not in attr_lower:
                    clean = re.sub(r'[^\d]', '', val_str)
                    if clean and clean.isdigit() and 3000 <= int(clean) <= 300000:
                        if not vehicle['value']:
                            vehicle['value'] = clean
            
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
                        logger.info("Extracted: {} {} {} {}".format(
                            vehicle['year'], vehicle['makeName'], 
                            vehicle['model'], vehicle.get('trim', '')))
                
                if vehicles:
                    return vehicles
        
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
        
        unique = []
        seen = set()
        
        for v in all_vehicles:
            year = v.get('year', '')
            make = v.get('makeName', '')
            model = v.get('model', '')
            stock = v.get('stock_number', '')
            mileage = v.get('mileage', '')
            price = v.get('value', '') or v.get('sale_value', '')
            
            if stock:
                key = (year, make, model, stock)
            elif mileage:
                key = (year, make, model, mileage)
            elif price:
                key = (year, make, model, price)
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
        for v in self.vehicles:
            brand = v.get('makeName', 'Unknown')
            brands[brand] = brands.get(brand, 0) + 1
        
        print("\nBrand Distribution:")
        for brand, count in sorted(brands.items()):
            print("  {}: {}".format(brand, count))
        
        print("\n{:<10} {:<6} {:<15} {:<10} {:<10} {:<10} {:<10}".format(
            'Make', 'Year', 'Model', 'Trim', 'Mileage', 'Value', 'Stock#'))
        print("-" * 80)
        
        for v in self.vehicles:
            print("{:<10} {:<6} {:<15} {:<10} {:<10} {:<10} {:<10}".format(
                v.get('makeName', '')[:9],
                v.get('year', ''),
                v.get('model', '')[:14],
                v.get('trim', '')[:9],
                v.get('mileage', '')[:9],
                v.get('value', '')[:9],
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
