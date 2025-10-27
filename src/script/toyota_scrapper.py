#!/usr/bin/env python3
"""
Red Deer Toyota Used Inventory Scraper - Universal Version (FIXED)
Extracts ALL accurate data for ANY brand/model with improved detection
FIXES:
- Better pagination handling
- Multiple extraction strategies (JSON, HTML selectors, text parsing)
- Improved duplicate detection
- Better model/trim recognition
- Debug mode for troubleshooting
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
    def __init__(self, debug_mode=False):
        self.base_url = "https://www.reddeertoyota.com"
        self.target_url = "https://www.reddeertoyota.com/inventory/used/"
        self.session = requests.Session()
        self.debug_mode = debug_mode
        
        # Enhanced headers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'DNT': '1'
        })
        
        self.vehicles = []
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Universal car makes and models - EXPANDED
        self.car_makes = {
            'Toyota': {
                'Camry', 'RAV4', 'Highlander', 'Prius', 'Corolla', 'Corolla Cross', 'Tacoma', 'Tundra', 
                'Sienna', '4Runner', 'Sequoia', 'Avalon', 'C-HR', 'Venza', 'Land Cruiser', 
                'GR86', 'Supra', 'Yaris', 'Yaris Cross', 'Matrix', 'FJ Cruiser', 'Celica', 'MR2', 'Crown',
                'bZ4X', 'GR Corolla', 'Solara', 'Echo', 'Tercel', 'Pickup'
            },
            'Honda': {
                'Civic', 'Accord', 'CR-V', 'HR-V', 'Pilot', 'Odyssey', 'Fit', 'Insight', 
                'Ridgeline', 'Passport', 'Element', 'S2000', 'NSX', 'Prelude', 'del Sol',
                'Clarity', 'CR-Z'
            },
            'Ford': {
                'F-150', 'F-250', 'F-350', 'Escape', 'Explorer', 'Expedition', 'Edge', 
                'Fusion', 'Focus', 'Fiesta', 'Mustang', 'Bronco', 'Bronco Sport', 'Ranger', 
                'Transit', 'Taurus', 'Crown Victoria', 'Thunderbird', 'Maverick', 'EcoSport',
                'Flex'
            },
            'Chevrolet': {
                'Silverado', 'Silverado 1500', 'Silverado 2500', 'Silverado 3500', 'Tahoe', 
                'Suburban', 'Equinox', 'Traverse', 'Malibu', 'Cruze', 'Impala', 'Camaro', 
                'Corvette', 'Colorado', 'Blazer', 'Trax', 'Trailblazer', 'Spark', 'Volt',
                'Bolt', 'Sonic'
            },
            'GMC': {
                'Sierra', 'Sierra 1500', 'Sierra 2500', 'Sierra 3500', 'Yukon', 'Yukon XL',
                'Acadia', 'Terrain', 'Canyon', 'Savana', 'Envoy'
            },
            'Dodge': {
                'Charger', 'Challenger', 'Journey', 'Durango', 'Grand Caravan', 'Dart', 
                'Avenger', 'Nitro', 'Magnum'
            },
            'Ram': {
                '1500', '2500', '3500', 'ProMaster'
            },
            'Nissan': {
                'Altima', 'Sentra', 'Rogue', 'Murano', 'Pathfinder', 'Armada', 'Titan', 
                'Frontier', '370Z', 'GT-R', 'Leaf', 'Kicks', 'Versa', 'Maxima', 'Juke',
                'Xterra'
            },
            'Hyundai': {
                'Elantra', 'Sonata', 'Tucson', 'Santa Fe', 'Palisade', 'Accent', 'Veloster', 
                'Genesis', 'Azera', 'Venue', 'Kona', 'Santa Cruz', 'Ioniq', 'Ioniq 5'
            },
            'Kia': {
                'Forte', 'Optima', 'K5', 'Sportage', 'Sorento', 'Telluride', 'Soul', 'Stinger', 
                'Rio', 'Sedona', 'Carnival', 'Niro', 'Seltos', 'EV6'
            },
            'Mazda': {
                'Mazda3', 'Mazda6', 'CX-3', 'CX-5', 'CX-9', 'MX-5', 'CX-30', 'CX-50', 'RX-7', 'RX-8'
            },
            'Subaru': {
                'Outback', 'Forester', 'Impreza', 'Legacy', 'Crosstrek', 'Ascent', 'WRX', 'BRZ',
                'Solterra'
            },
            'Volkswagen': {
                'Jetta', 'Passat', 'Golf', 'Tiguan', 'Atlas', 'Beetle', 'GTI', 'Touareg',
                'Taos', 'ID.4'
            },
            'BMW': {
                '3 Series', '5 Series', '7 Series', 'X1', 'X3', 'X5', 'X7', 'Z4', 'i3', 'i8',
                '2 Series', '4 Series', 'X2', 'iX'
            },
            'Mercedes-Benz': {
                'C-Class', 'E-Class', 'S-Class', 'GLA', 'GLC', 'GLE', 'GLS', 'CLA', 'SL',
                'GLB', 'G-Class', 'EQB', 'EQS'
            },
            'Audi': {
                'A3', 'A4', 'A6', 'A8', 'Q3', 'Q5', 'Q7', 'Q8', 'TT', 'R8', 'e-tron'
            },
            'Lexus': {
                'ES', 'IS', 'GS', 'LS', 'NX', 'RX', 'GX', 'LX', 'UX', 'LC', 'RC'
            },
            'Infiniti': {
                'Q50', 'Q60', 'QX50', 'QX60', 'QX80', 'G35', 'G37', 'FX35', 'FX37', 'QX55'
            },
            'Acura': {
                'ILX', 'TLX', 'RLX', 'RDX', 'MDX', 'NSX', 'TSX', 'TL', 'RSX', 'Integra'
            },
            'Jeep': {
                'Wrangler', 'Grand Cherokee', 'Cherokee', 'Compass', 'Renegade', 'Gladiator', 
                'Liberty', 'Wagoneer', 'Grand Wagoneer'
            },
            'Cadillac': {
                'Escalade', 'XT4', 'XT5', 'XT6', 'CT4', 'CT5', 'CTS', 'ATS', 'SRX', 'Lyriq'
            },
            'Lincoln': {
                'Navigator', 'Aviator', 'Corsair', 'Nautilus', 'Continental', 'MKZ', 'MKX'
            },
            'Buick': {
                'Enclave', 'Encore', 'Envision', 'LaCrosse', 'Regal', 'Verano'
            },
            'Chrysler': {'Pacifica', '300', 'Voyager'},
            'Tesla': {'Model 3', 'Model S', 'Model X', 'Model Y'},
            'Mitsubishi': {'Outlander', 'Eclipse Cross', 'Mirage', 'RVR'},
            'Volvo': {'XC90', 'XC60', 'XC40', 'S60', 'S90', 'V60'},
            'Land Rover': {'Range Rover', 'Range Rover Sport', 'Discovery', 'Defender'},
            'Porsche': {'911', 'Cayenne', 'Macan', 'Panamera', 'Taycan'},
            'Genesis': {'G70', 'G80', 'G90', 'GV70', 'GV80'}
        }

    def fetch_all_pages(self):
        """Fetch all inventory pages (page 1, 2, 3, etc.) - IMPROVED"""
        all_soups = []
        page_num = 1
        max_pages = 20  # Increased safety limit
        consecutive_empty = 0
        
        while page_num <= max_pages:
            # Try both URL formats
            if page_num == 1:
                url = self.target_url
            else:
                url = "{}?page={}".format(self.target_url.rstrip('/'), page_num)
            
            try:
                logger.info("Fetching page {}: {}".format(page_num, url))
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                
                logger.info("Page {} Response: {}, Size: {} bytes".format(
                    page_num, response.status_code, len(response.content)))
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Save HTML for debugging if enabled
                if self.debug_mode:
                    debug_dir = 'debug_html'
                    os.makedirs(debug_dir, exist_ok=True)
                    debug_file = os.path.join(debug_dir, 'page_{}.html'.format(page_num))
                    with open(debug_file, 'w', encoding='utf-8') as f:
                        f.write(response.text)
                    logger.info("Debug: Saved HTML to {}".format(debug_file))
                
                # Check if page has content - more comprehensive check
                page_text = soup.get_text()
                
                # Look for vehicle indicators
                has_year = bool(re.search(r'\b(19[89]\d|20[0-2]\d)\b', page_text))
                has_price = bool(re.search(r'\$\s*\d{4,}', page_text))
                has_stock = bool(re.search(r'(?:Stock|VIN|#)\s*[A-Z0-9]{5,}', page_text, re.IGNORECASE))
                
                has_vehicles = has_year and (has_price or has_stock)
                
                # Check for "no results" indicators
                no_results = any([
                    'no vehicles found' in page_text.lower(),
                    'no results' in page_text.lower(),
                    '0 vehicles' in page_text.lower(),
                    'no matches found' in page_text.lower()
                ])
                
                if has_vehicles and not no_results:
                    all_soups.append((page_num, soup))
                    consecutive_empty = 0
                    logger.info("Page {} has vehicles - added to processing queue".format(page_num))
                else:
                    consecutive_empty += 1
                    logger.info("Page {} appears empty (consecutive: {})".format(page_num, consecutive_empty))
                    # Only stop if we've seen 2 consecutive empty pages
                    if consecutive_empty >= 2:
                        logger.info("Stopping pagination after {} consecutive empty pages".format(consecutive_empty))
                        break
                
                page_num += 1
                
                # Small delay to be respectful
                time.sleep(0.5)
                
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 404:
                    logger.info("Page {} returned 404, stopping pagination".format(page_num))
                    break
                else:
                    logger.error("HTTP error on page {}: {}".format(page_num, str(e)))
                    break
            except Exception as e:
                logger.error("Failed to fetch page {}: {}".format(page_num, str(e)))
                break
        
        logger.info("Successfully fetched {} pages".format(len(all_soups)))
        return all_soups

    def extract_make_and_model(self, text):
        """Extract make and model from text using comprehensive patterns"""
        text = re.sub(r'\s+', ' ', text.strip())
        
        # First pass: Check for multi-word models
        for make, models in self.car_makes.items():
            make_patterns = [
                r'\b{}\b'.format(re.escape(make)),
                r'\b{}\b'.format(re.escape(make.upper())),
                r'\b{}\b'.format(re.escape(make.lower()))
            ]
            
            for make_pattern in make_patterns:
                if re.search(make_pattern, text, re.IGNORECASE):
                    # Sort models by length (longest first) to match multi-word models first
                    sorted_models = sorted(models, key=len, reverse=True)
                    
                    for model in sorted_models:
                        model_patterns = [
                            r'\b{}\b'.format(re.escape(model)),
                            r'\b{}\b'.format(re.escape(model.replace("-", " "))),
                            r'\b{}\b'.format(re.escape(model.replace(" ", ""))),
                            r'\b{}\b'.format(re.escape(model.replace("-", "")))
                        ]
                        
                        for model_pattern in model_patterns:
                            if re.search(model_pattern, text, re.IGNORECASE):
                                return make, model
        
        return None, None

    def extract_trim_from_text(self, text):
        """Extract trim using comprehensive pattern matching"""
        if not text:
            return ''
        
        trim_patterns = {
            # Toyota trims - COMPLETE
            'Capstone': r'\bCapstone\b',
            'Platinum': r'\bPlatinum\b',
            'Limited': r'\bLimited\b',
            'XLE': r'\bXLE\b',
            'XSE': r'\bXSE\b',
            'LE': r'\bLE\b(?!\w)',
            'SE': r'\bSE\b(?!\w)',
            'TRD Pro': r'\bTRD\s+Pro\b',
            'TRD Off-Road': r'\bTRD\s+Off-?Road\b',
            'TRD Sport': r'\bTRD\s+Sport\b',
            'TRD': r'\bTRD\b',
            'SR5': r'\bSR5\b',
            'SR': r'\bSR\b(?!\d)',
            'Hybrid': r'\bHybrid\b',
            'Prime': r'\bPrime\b',
            'Nightshade': r'\bNightshade\b',
            'Trail': r'\bTrail\b(?!\w)',
            'Adventure': r'\bAdventure\b',
            'Bronze Edition': r'\bBronze\s+Edition\b',
            'Woodland Edition': r'\bWoodland\s+Edition\b',
            'CrewMax': r'\bCrewMax\b',
            'Double Cab': r'\bDouble\s+Cab\b',
            
            # Honda trims
            'Touring': r'\bTouring\b',
            'Sport Touring': r'\bSport\s+Touring\b',
            'EX-L': r'\bEX-L\b',
            'EX': r'\bEX\b(?!\w)',
            'LX': r'\bLX\b(?!\w)',
            'Type R': r'\bType\s+R\b',
            'Si': r'\bSi\b',
            'TrailSport': r'\bTrailSport\b',
            'Elite': r'\bElite\b',
            
            # Ford trims
            'Raptor R': r'\bRaptor\s+R\b',
            'Raptor': r'\bRaptor\b',
            'King Ranch': r'\bKing\s+Ranch\b',
            'Lariat': r'\bLariat\b',
            'XLT': r'\bXLT\b',
            'XL': r'\bXL\b(?!\w)',
            'Tremor': r'\bTremor\b',
            'Wildtrak': r'\bWildtrak\b',
            'Badlands': r'\bBadlands\b',
            'Outer Banks': r'\bOuter\s+Banks\b',
            'Big Bend': r'\bBig\s+Bend\b',
            'Timberline': r'\bTimberline\b',
            'ST': r'\bST\b(?!\w)',
            'RS': r'\bRS\b(?!\w)',
            'GT': r'\bGT\b(?!\w)',
            'GT500': r'\bGT500\b',
            'Mach 1': r'\bMach\s+1\b',
            'Shelby': r'\bShelby\b',
            'Titanium': r'\bTitanium\b',
            'SEL': r'\bSEL\b(?!\w)',
            
            # Dodge/Ram trims
            'Hellcat Redeye': r'\bHellcat\s+Redeye\b',
            'Hellcat': r'\bHellcat\b',
            'SRT 392': r'\bSRT\s+392\b',
            'SRT': r'\bSRT\b',
            'Scat Pack': r'\bScat\s+Pack\b',
            'R/T': r'\bR/T\b',
            'SXT': r'\bSXT\b',
            'Demon': r'\bDemon\b',
            'TRX': r'\bTRX\b',
            'Rebel': r'\bRebel\b',
            'Laramie': r'\bLaramie\b',
            'Longhorn': r'\bLonghorn\b',
            'Big Horn': r'\bBig\s+Horn\b',
            'Lone Star': r'\bLone\s+Star\b',
            'Night Edition': r'\bNight\s+Edition\b',
            'Sport': r'\bSport\b(?!\s+Utility)',
            
            # Chevrolet trims
            'High Country': r'\bHigh\s+Country\b',
            'LTZ': r'\bLTZ\b',
            'LT': r'\bLT\b(?!\w)',
            'LS': r'\bLS\b(?!\w)',
            'Premier': r'\bPremier\b',
            'Z71': r'\bZ71\b',
            'ZL1': r'\bZL1\b',
            'SS': r'\bSS\b(?!\w)',
            'RST': r'\bRST\b',
            'Trail Boss': r'\bTrail\s+Boss\b',
            'Midnight': r'\bMidnight\b',
            
            # GMC trims
            'Denali': r'\bDenali\b',
            'AT4': r'\bAT4\b',
            'SLT': r'\bSLT\b',
            'SLE': r'\bSLE\b',
            'Elevation': r'\bElevation\b',
            
            # Nissan trims
            'SL': r'\bSL\b(?!\w)',
            'SV': r'\bSV\b',
            'S': r'\b(?<!\w)S(?!\w)',
            'Pro-4X': r'\bPro-4X\b',
            'Nismo': r'\bNismo\b',
            'Rock Creek': r'\bRock\s+Creek\b',
            
            # Hyundai trims
            'Calligraphy': r'\bCalligraphy\b',
            'Ultimate': r'\bUltimate\b',
            'Luxury': r'\bLuxury\b',
            'Preferred': r'\bPreferred\b',
            'Essential': r'\bEssential\b',
            'N Line': r'\bN\s+Line\b',
            'N': r'\bN\b(?!\s+Line)',
            
            # Kia trims
            'SX': r'\bSX\b(?!\w)',
            'GT-Line': r'\bGT-Line\b',
            'X-Line': r'\bX-Line\b',
            
            # Mazda trims
            'Signature': r'\bSignature\b',
            'Grand Touring': r'\bGrand\s+Touring\b',
            'Turbo': r'\bTurbo\b',
            
            # Subaru trims
            'Wilderness': r'\bWilderness\b',
            'Touring XT': r'\bTouring\s+XT\b',
            'Onyx Edition': r'\bOnyx\s+Edition\b',
            'STI': r'\bSTI\b',
            'Premium': r'\bPremium\b',
            
            # Jeep trims
            'Rubicon 392': r'\bRubicon\s+392\b',
            'Rubicon': r'\bRubicon\b',
            'Sahara': r'\bSahara\b',
            'High Altitude': r'\bHigh\s+Altitude\b',
            'Trailhawk': r'\bTrailhawk\b',
            'Overland': r'\bOverland\b',
            'Summit': r'\bSummit\b',
            'Mojave': r'\bMojave\b',
            'Willys': r'\bWillys\b',
            '4xe': r'\b4xe\b',
            
            # Luxury trims
            'AMG': r'\bAMG\b',
            'M Sport': r'\bM\s+Sport\b',
            'S-Line': r'\bS-Line\b',
            'F Sport': r'\bF\s+Sport\b',
            'Executive': r'\bExecutive\b',
            'Prestige': r'\bPrestige\b',
            
            # Generic
            'AWD': r'\bAWD\b',
            '4WD': r'\b4WD\b',
            'Crew Cab': r'\bCrew\s+Cab\b',
            'Quad Cab': r'\bQuad\s+Cab\b',
        }
        
        for trim_name, pattern in trim_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                return trim_name
        
        return ''

    def extract_clean_vehicle_data(self, element):
        """Extract clean, accurate vehicle data from element"""
        vehicle = {
            'makeName': '',
            'year': '',
            'model': '',
            'sub-model': '',
            'trim': '',
            'mileage': '',
            'value': '',
            'sale_value': '',
            'stock_number': '',
            'engine': ''
        }
        
        try:
            element_text = element.get_text(separator=' ', strip=True)
            element_text = re.sub(r'\s+', ' ', element_text)
            
            logger.debug("Processing element text: {}...".format(element_text[:150]))
            
            # Extract year
            year_match = re.search(r'\b(19[8-9][0-9]|20[0-2][0-9])\b', element_text)
            if year_match:
                vehicle['year'] = year_match.group(1)
            
            # Extract make and model
            make, model = self.extract_make_and_model(element_text)
            if make:
                vehicle['makeName'] = make
            if model:
                vehicle['model'] = model
            
            # Extract trim
            trim = self.extract_trim_from_text(element_text)
            if trim:
                if model and trim.lower() not in model.lower():
                    vehicle['trim'] = trim
                    vehicle['sub-model'] = trim
                elif not model:
                    vehicle['trim'] = trim
                    vehicle['sub-model'] = trim
            
            # Extract prices
            orig_price = None
            sale_price = None

            # Look for paired prices
            paired_patterns = [
                r"Was[:\s]*\$\s*([0-9,]+)\s*(?:Now|Sale\s*Price)[:\s]*\$\s*([0-9,]+)",
                r"List\s*Price[:\s]*\$\s*([0-9,]+)\s*(?:Now|Sale\s*Price)[:\s]*\$\s*([0-9,]+)",
                r"Retail\s*Price[:\s]*\$\s*([0-9,]+)\s*(?:Now|Sale\s*Price)[:\s]*\$\s*([0-9,]+)",
                r"\$\s*([0-9,]+)\s+Was\s+\$\s*([0-9,]+)",
            ]
            
            for pattern in paired_patterns:
                m = re.search(pattern, element_text, re.IGNORECASE)
                if m:
                    p1 = int(m.group(1).replace(',', ''))
                    p2 = int(m.group(2).replace(',', ''))
                    hi, lo = (p1, p2) if p1 >= p2 else (p2, p1)
                    orig_price, sale_price = hi, lo
                    break

            if orig_price is None and sale_price is None:
                all_prices = re.findall(r'\$\s*([0-9,]+)', element_text)
                valid_prices = []
                for price_str in all_prices:
                    try:
                        price = int(price_str.replace(',', ''))
                        if 3000 <= price <= 300000:
                            valid_prices.append(price)
                    except:
                        pass
                
                if len(valid_prices) >= 2:
                    valid_prices.sort(reverse=True)
                    orig_price = valid_prices[0]
                    sale_price = valid_prices[1] if valid_prices[1] < orig_price else None
                elif len(valid_prices) == 1:
                    orig_price = valid_prices[0]

            if sale_price is not None and (orig_price is None or sale_price < orig_price):
                if orig_price is not None:
                    vehicle['value'] = str(orig_price)
                vehicle['sale_value'] = str(sale_price)
            elif orig_price is not None:
                vehicle['value'] = str(orig_price)
            
            # Extract mileage
            mileage_patterns = [
                r'(\d{1,3}(?:,\d{3})*)\s*(?:km|kilometers?)\b',
                r'(\d{1,3}(?:,\d{3})*)\s*(?:miles?|mi)\b',
                r'Odometer[:\s]*(\d{1,3}(?:,\d{3})*)',
                r'Mileage[:\s]*(\d{1,3}(?:,\d{3})*)',
                r'(\d{1,3}(?:,\d{3})*)\s*(?:k|K)\s*(?:km|mi|miles?)\b',
                r'(\d{1,3}(?:,\d{3})*)\s+km\b',
            ]
            
            for pattern in mileage_patterns:
                mileage_match = re.search(pattern, element_text, re.IGNORECASE)
                if mileage_match:
                    mileage_value = mileage_match.group(1).replace(',', '')
                    try:
                        mileage_int = int(mileage_value)
                        if 0 <= mileage_int <= 500000:
                            vehicle['mileage'] = mileage_value
                            break
                    except ValueError:
                        continue
            
            # Extract stock number
            stock_patterns = [
                r'Stock[#:\s]*([A-Z0-9]{3,15})\b',
                r'Stock\s*#?\s*([A-Z0-9]{3,15})\b',
                r'#\s*([A-Z0-9]{3,15})\b',
                r'ID[:\s]*([A-Z0-9]{3,15})\b',
                r'VIN[:\s]*([A-Z0-9]{17})\b',
                r'Inventory[#:\s]*([A-Z0-9]{3,15})\b',
            ]
            
            for pattern in stock_patterns:
                stock_match = re.search(pattern, element_text, re.IGNORECASE)
                if stock_match:
                    stock_value = stock_match.group(1)
                    if len(stock_value) >= 3 and stock_value.isalnum():
                        vehicle['stock_number'] = stock_value
                        break
            
            # Extract engine
            engine_patterns = [
                r'(\d\.\d+L\s*(?:V?\d+|I\d+|[0-9]-?Cyl|Cylinder))',
                r'(\d\.\d+\s*L\s*(?:V?\d+|I\d+|[0-9]-?Cyl))',
                r'(\d\.\d+L)\s*(?:Engine|Motor)',
                r'Engine[:\s]*(\d\.\d+L[^,\n]*)',
                r'(\d\.\d+L\s*Hybrid)',
                r'(\d\.\d+L\s*Turbo)',
                r'(\d\.\d+L\s*Supercharged)',
                r'(\d\.\d+L\s*Diesel)',
                r'(V\d+\s*\d\.\d+L)',
                r'(\d+\.\d+\s*Liter)',
                r'Electric\s*Motor',
                r'(\d+kWh\s*Battery)'
            ]
            
            for pattern in engine_patterns:
                engine_match = re.search(pattern, element_text, re.IGNORECASE)
                if engine_match:
                    engine_text = engine_match.group(1).strip() if engine_match.lastindex else engine_match.group(0)
                    engine_text = re.sub(r'\s+', ' ', engine_text)
                    
                    if 'Electric' in engine_text or 'kWh' in engine_text:
                        vehicle['engine'] = engine_text
                        break
                    
                    engine_size_match = re.search(r'(\d+\.\d+)L', engine_text)
                    if engine_size_match:
                        engine_size = float(engine_size_match.group(1))
                        if 0.8 <= engine_size <= 8.0:
                            vehicle['engine'] = engine_text
                            break
            
            # Check HTML attributes
            for attr, value in element.attrs.items():
                attr_lower = attr.lower()
                if 'data-' in attr_lower:
                    if 'year' in attr_lower and not vehicle['year']:
                        if re.match(r'^(19[8-9][0-9]|20[0-2][0-9]), str(value)):
                            vehicle['year'] = str(value)
                    elif 'make' in attr_lower and not vehicle['makeName']:
                        vehicle['makeName'] = str(value).title()
                    elif 'model' in attr_lower and not vehicle['model']:
                        vehicle['model'] = str(value)
                    elif 'trim' in attr_lower and not vehicle['trim']:
                        trim_val = str(value)
                        if vehicle['model'] and trim_val.lower() not in vehicle['model'].lower():
                            vehicle['trim'] = trim_val
                            vehicle['sub-model'] = trim_val
                        elif not vehicle['model']:
                            vehicle['trim'] = trim_val
                            vehicle['sub-model'] = trim_val
                    elif 'sale' in attr_lower and not vehicle['sale_value']:
                        sale_clean = re.sub(r'[^\d]', '', str(value))
                        if sale_clean and sale_clean.isdigit() and 3000 <= int(sale_clean) <= 300000:
                            vehicle['sale_value'] = sale_clean
                    elif 'price' in attr_lower:
                        price_clean = re.sub(r'[^\d]', '', str(value))
                        if price_clean and price_clean.isdigit() and 3000 <= int(price_clean) <= 300000:
                            if vehicle['sale_value'] and int(price_clean) < int(vehicle['sale_value']):
                                vehicle['value'], vehicle['sale_value'] = vehicle['sale_value'], price_clean
                            elif not vehicle['value']:
                                vehicle['value'] = price_clean
                    elif 'stock' in attr_lower and not vehicle['stock_number']:
                        if len(str(value)) >= 3:
                            vehicle['stock_number'] = str(value)
                    elif 'mileage' in attr_lower and not vehicle['mileage']:
                        mile_clean = re.sub(r'[^\d]', '', str(value))
                        if mile_clean and mile_clean.isdigit():
                            vehicle['mileage'] = mile_clean
            
            return vehicle
            
        except Exception as e:
            logger.debug("Error extracting vehicle data: {}".format(str(e)))
            return vehicle

    def is_complete_vehicle(self, vehicle):
        """Check if vehicle has enough accurate data - IMPROVED"""
        if not isinstance(vehicle, dict):
            return False
        
        # Must have year and make
        required_fields = ['year', 'makeName']
        has_required = all(vehicle.get(field, '').strip() for field in required_fields)
        
        if not has_required:
            return False
        
        # Must have model OR at least 2 of: stock, mileage, price
        has_model = bool(vehicle.get('model', '').strip())
        
        identifying_fields = ['stock_number', 'mileage', 'value', 'sale_value']
        identifying_count = sum(1 for field in identifying_fields if vehicle.get(field, '').strip())
        
        # Either has model, or has at least 2 identifying fields
        return has_model or identifying_count >= 2

    def extract_from_json_or_scripts(self, soup):
        """Extract vehicle data from JSON-LD, script tags, or data attributes"""
        vehicles = []
        
        # Look for JSON-LD structured data
        json_ld_scripts = soup.find_all('script', type='application/ld+json')
        for script in json_ld_scripts:
            try:
                data = json.loads(script.string)
                items = data if isinstance(data, list) else [data]
                
                for item in items:
                    if isinstance(item, dict):
                        if item.get('@type') in ['Car', 'Vehicle', 'Product']:
                            vehicle = {
                                'makeName': item.get('brand', {}).get('name', '') if isinstance(item.get('brand'), dict) else item.get('brand', ''),
                                'year': str(item.get('modelDate', item.get('productionDate', ''))).split('-')[0],
                                'model': item.get('model', ''),
                                'sub-model': '',
                                'trim': item.get('vehicleConfiguration', ''),
                                'mileage': str(item.get('mileageFromOdometer', {}).get('value', '')) if isinstance(item.get('mileageFromOdometer'), dict) else '',
                                'value': str(item.get('offers', {}).get('price', '')) if isinstance(item.get('offers'), dict) else '',
                                'sale_value': '',
                                'stock_number': item.get('sku', item.get('productID', '')),
                                'engine': item.get('vehicleEngine', {}).get('name', '') if isinstance(item.get('vehicleEngine'), dict) else ''
                            }
                            
                            if self.is_complete_vehicle(vehicle):
                                vehicles.append(vehicle)
                                logger.info("Extracted from JSON-LD: {} {} {}".format(
                                    vehicle['year'], vehicle['makeName'], vehicle['model']))
            except Exception as e:
                logger.debug("Error parsing JSON-LD: {}".format(str(e)))
        
        # Look for JavaScript variables
        all_scripts = soup.find_all('script', type=['text/javascript', None])
        for script in all_scripts:
            if not script.string:
                continue
            
            script_text = script.string
            
            var_patterns = [
                r'vehicles\s*=\s*(\[.*?\]);',
                r'inventory\s*=\s*(\[.*?\]);',
                r'vehicleData\s*=\s*(\[.*?\]);',
                r'cars\s*=\s*(\[.*?\]);'
            ]
            
            for pattern in var_patterns:
                matches = re.findall(pattern, script_text, re.DOTALL)
                for match in matches:
                    try:
                        data = json.loads(match)
                        if isinstance(data, list):
                            for item in data:
                                if isinstance(item, dict):
                                    vehicle = {
                                        'makeName': item.get('make', item.get('makeName', '')),
                                        'year': str(item.get('year', '')),
                                        'model': item.get('model', ''),
                                        'sub-model': item.get('subModel', item.get('sub-model', '')),
                                        'trim': item.get('trim', ''),
                                        'mileage': str(item.get('mileage', item.get('odometer', ''))),
                                        'value': str(item.get('price', item.get('value', ''))),
                                        'sale_value': str(item.get('salePrice', item.get('sale_value', ''))),
                                        'stock_number': item.get('stockNumber', item.get('stock_number', item.get('vin', ''))),
                                        'engine': item.get('engine', '')
                                    }
                                    
                                    # Clean up values
                                    for key in vehicle:
                                        if vehicle[key] and vehicle[key] != 'None':
                                            vehicle[key] = str(vehicle[key]).replace(', '').replace(',', '').strip()
                                        else:
                                            vehicle[key] = ''
                                    
                                    if self.is_complete_vehicle(vehicle):
                                        vehicles.append(vehicle)
                                        logger.info("Extracted from JS variable: {} {} {}".format(
                                            vehicle['year'], vehicle['makeName'], vehicle['model']))
                    except Exception as e:
                        logger.debug("Error parsing JS variable: {}".format(str(e)))
        
        return vehicles

    def find_vehicle_containers(self, soup):
        """Find vehicle container elements with accurate data - IMPROVED"""
        vehicles = []
        
        # Strategy 1: Data attributes (most reliable)
        priority_selectors = [
            '[data-vehicle]',
            '[data-vehicle-id]',
            '[data-stock-number]',
            '[data-stock]',
            '[data-vin]',
            'article[data-vehicle-id]',
            'div[data-vehicle-id]',
            'li[data-vehicle-id]'
        ]
        
        for selector in priority_selectors:
            elements = soup.select(selector)
            if elements:
                logger.info("Found {} elements with selector: {}".format(len(elements), selector))
                
                for element in elements:
                    vehicle = self.extract_clean_vehicle_data(element)
                    
                    if self.is_complete_vehicle(vehicle):
                        vehicles.append(vehicle)
                        logger.debug("Extracted: {} {} {} - Stock: {}".format(
                            vehicle['year'], vehicle['makeName'], vehicle['model'], 
                            vehicle.get('stock_number', 'N/A')))
                
                if vehicles:
                    logger.info("Successfully extracted {} vehicles using {}".format(len(vehicles), selector))
                    return vehicles
        
        # Strategy 2: Class-based selectors
        class_selectors = [
            '.vehicle-card',
            '.inventory-item',
            '.vehicle-listing',
            '.srp-list-item',
            '.inventory-card',
            'article[class*="vehicle"]',
            'article[class*="inventory"]',
            'div[class*="vehicle-tile"]',
            'div[class*="vehicle-card"]',
            'div[class*="inventory-item"]',
            'li[class*="vehicle"]',
            'li[class*
