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
                'Camry', 'RAV4', 'Highlander', 'Prius', 'Corolla', 'Tacoma', 'Tundra', 
                'Sienna', '4Runner', 'Sequoia', 'Avalon', 'C-HR', 'Venza', 'Land Cruiser', 
                'GR86', 'Supra', 'Yaris', 'Matrix', 'FJ Cruiser', 'Celica', 'MR2', 'Crown',
                'bZ4X', 'GR Corolla', 'Solara', 'Echo'
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

    def fetch_main_page(self):
        """Fetch the main inventory page"""
        try:
            logger.info("Fetching: {}".format(self.target_url))
            response = self.session.get(self.target_url, timeout=30)
            response.raise_for_status()
            
            logger.info("Response: {}, Size: {} bytes".format(response.status_code, len(response.content)))
            soup = BeautifulSoup(response.content, 'html.parser')
            
            title = soup.find('title')
            if title:
                logger.info("Page title: {}".format(title.get_text().strip()))
            
            return soup
            
        except Exception as e:
            logger.error("Failed to fetch main page: {}".format(str(e)))
            return None

    def extract_make_and_model(self, text):
        """Extract make and model from text using comprehensive patterns"""
        text = re.sub(r'\s+', ' ', text.strip())
        
        for make, models in self.car_makes.items():
            make_patterns = [
                r'\b{}\b'.format(re.escape(make)),
                r'\b{}\b'.format(re.escape(make.upper())),
                r'\b{}\b'.format(re.escape(make.lower()))
            ]
            
            for make_pattern in make_patterns:
                if re.search(make_pattern, text, re.IGNORECASE):
                    for model in models:
                        model_patterns = [
                            r'\b{}\b'.format(re.escape(model)),
                            r'\b{}\b'.format(re.escape(model.replace("-", ""))),
                            r'\b{}\b'.format(re.escape(model.replace(" ", "")))
                        ]
                        
                        for model_pattern in model_patterns:
                            if re.search(model_pattern, text, re.IGNORECASE):
                                return make, model
        
        generic_pattern = r'\b(20[0-2][0-9])\s+([A-Z][a-zA-Z-]+)\s+([A-Z][a-zA-Z0-9-]+)\b'
        match = re.search(generic_pattern, text)
        if match:
            year, potential_make, potential_model = match.groups()
            for make in self.car_makes.keys():
                if make.lower() == potential_make.lower():
                    return make, potential_model
        
        return None, None

    def extract_trim_from_text(self, text):
        """Extract trim using comprehensive pattern matching - COMPLETE"""
        if not text:
            return ''
        
        trim_patterns = {
            # Toyota trims - COMPLETE with Capstone
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
            
            # Ford trims - COMPLETE
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
            
            # Dodge/Ram trims - COMPLETE
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
            
            logger.debug("Processing element text: {}...".format(element_text[:100]))
            
            year_match = re.search(r'\b(19[8-9][0-9]|20[0-2][0-9])\b', element_text)
            if year_match:
                vehicle['year'] = year_match.group(1)
            
            make, model = self.extract_make_and_model(element_text)
            if make:
                vehicle['makeName'] = make
            if model:
                vehicle['model'] = model
            
            trim = self.extract_trim_from_text(element_text)
            if trim:
                vehicle['trim'] = trim
                vehicle['sub-model'] = trim
            
            orig_price = None
            sale_price = None

            paired_patterns = [
                r"Was[:\s]*\$([0-9,]+)\s*(?:Now|Sale Price)[:\s]*\$([0-9,]+)",
                r"List Price[:\s]*\$([0-9,]+)\s*(?:Now|Sale Price)[:\s]*\$([0-9,]+)",
                r"Retail Price[:\s]*\$([0-9,]+)\s*(?:Now|Sale Price)[:\s]*\$([0-9,]+)",
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
                sale_patterns = [
                    r"(?:Sale\s*Price|Now|Internet\s*Price|Special|Clearance)[:\s]*\$([0-9,]+)",
                ]
                orig_patterns = [
                    r"(?:Price|MSRP|List\s*Price|Retail\s*Price|Was)[:\s]*\$([0-9,]+)",
                    r"\$([0-9]{2}[0-9,]*)",
                ]
                for pattern in sale_patterns:
                    m = re.search(pattern, element_text, re.IGNORECASE)
                    if m:
                        try:
                            sp = int(m.group(1).replace(',', ''))
                            if 3000 <= sp <= 300000:
                                sale_price = sp
                                break
                        except Exception:
                            pass
                for pattern in orig_patterns:
                    m = re.search(pattern, element_text, re.IGNORECASE)
                    if m:
                        try:
                            op = int(m.group(1).replace(',', ''))
                            if 3000 <= op <= 300000:
                                if sale_price is None or op != sale_price:
                                    orig_price = op
                                    break
                        except Exception:
                            pass

            if sale_price is not None and (orig_price is None or sale_price < orig_price):
                if orig_price is not None:
                    vehicle['value'] = str(orig_price)
                vehicle['sale_value'] = str(sale_price)
            elif orig_price is not None:
                vehicle['value'] = str(orig_price)
            
            mileage_patterns = [
                r'(\d{1,3}(?:,\d{3})*)\s*(?:km|kilometers?)\b',
                r'(\d{1,3}(?:,\d{3})*)\s*(?:miles?|mi)\b',
                r'Odometer[:\s]*(\d{1,3}(?:,\d{3})*)',
                r'Mileage[:\s]*(\d{1,3}(?:,\d{3})*)',
                r'(\d{1,3}(?:,\d{3})*)\s*(?:k|K)\s*(?:km|mi|miles?)\b'
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
            
            stock_patterns = [
                r'Stock[#\s]*([A-Z0-9]{3,10})\b',
                r'#([A-Z0-9]{3,10})\b',
                r'ID[:\s]*([A-Z0-9]{3,10})\b',
                r'VIN[:\s]*([A-Z0-9]{17})\b'
            ]
            
            for pattern in stock_patterns:
                stock_match = re.search(pattern, element_text, re.IGNORECASE)
                if stock_match:
                    stock_value = stock_match.group(1)
                    if len(stock_value) >= 3 and stock_value.isalnum():
                        vehicle['stock_number'] = stock_value
                        break
            
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
            
            for attr, value in element.attrs.items():
                attr_lower = attr.lower()
                if 'data-' in attr_lower:
                    if 'year' in attr_lower and not vehicle['year']:
                        if re.match(r'^(19[8-9][0-9]|20[0-2][0-9])$', str(value)):
                            vehicle['year'] = str(value)
                    elif 'make' in attr_lower and not vehicle['makeName']:
                        vehicle['makeName'] = str(value).title()
                    elif 'model' in attr_lower and not vehicle['model']:
                        vehicle['model'] = str(value)
                    elif 'trim' in attr_lower and not vehicle['trim']:
                        vehicle['trim'] = str(value)
                        vehicle['sub-model'] = str(value)
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
            
            return vehicle
            
        except Exception as e:
            logger.debug("Error extracting vehicle data: {}".format(str(e)))
            return vehicle

    def is_complete_vehicle(self, vehicle):
        """Check if vehicle has enough accurate data"""
        if not isinstance(vehicle, dict):
            return False
        
        required_fields = ['year', 'makeName']
        has_required = all(vehicle.get(field, '').strip() for field in required_fields)
        
        identifying_fields = ['model', 'value', 'stock_number', 'mileage']
        has_identifying = sum(1 for field in identifying_fields if vehicle.get(field, '').strip()) >= 1
        
        return has_required and has_identifying

    def find_vehicle_containers(self, soup):
        """Find vehicle container elements with accurate data"""
        vehicles = []
        
        priority_selectors = [
            '[data-vehicle-id]',
            '[data-stock-number]',
            '[data-vin]',
            '.vehicle-card',
            '.inventory-item',
            '.vehicle-listing',
            '.srp-list-item'
        ]
        
        for selector in priority_selectors:
            elements = soup.select(selector)
            if elements:
                logger.info("Found {} elements with selector: {}".format(len(elements), selector))
                
                for element in elements:
                    vehicle = self.extract_clean_vehicle_data(element)
                    
                    if self.is_complete_vehicle(vehicle):
                        vehicles.append(vehicle)
                        logger.info("Extracted complete vehicle: {} {} {} - Stock: {}".format(
                            vehicle['year'], vehicle['makeName'], vehicle['model'], vehicle['stock_number']))
                
                if vehicles:
                    logger.info("Successfully extracted {} vehicles using {}".format(len(vehicles), selector))
                    return vehicles
        
        fallback_selectors = [
            '.vehicle',
            '.car-item',
            '.listing-item',
            '.inventory-card',
            '[class*="vehicle"]',
            '[class*="inventory"]'
        ]
        
        for selector in fallback_selectors:
            elements = soup.select(selector)
            if elements:
                logger.info("Trying fallback selector: {} ({} elements)".format(selector, len(elements)))
                
                for element in elements:
                    vehicle = self.extract_clean_vehicle_data(element)
                    
                    if self.is_complete_vehicle(vehicle):
                        vehicles.append(vehicle)
                
                if vehicles:
                    logger.info("Extracted {} vehicles using fallback {}".format(len(vehicles), selector))
                    return vehicles
        
        return vehicles

    def scrape_inventory(self):
        """Main scraping method - only returns accurate data for any brand"""
        logger.info("=" * 80)
        logger.info("UNIVERSAL RED DEER TOYOTA USED INVENTORY SCRAPER")
        logger.info("Extracting accurate data for ANY brand/model - no fallback samples")
        logger.info("=" * 80)
        
        soup = self.fetch_main_page()
        if not soup:
            logger.error("Cannot proceed without main page")
            return []
        
        logger.info("Searching for vehicle containers...")
        vehicles = self.find_vehicle_containers(soup)
        
        if not vehicles:
            logger.warning("No complete vehicles found with current selectors")
            
            logger.info("Attempting text-based extraction as final attempt...")
            page_text = soup.get_text()
            
            make_list = '|'.join(self.car_makes.keys())
            vehicle_pattern = r'(19[8-9][0-9]|20[0-2][0-9])\s+({0})\s+([A-Za-z0-9-]+).*?\$([0-9,]+)'.format(make_list)
            
            matches = re.findall(vehicle_pattern, page_text, re.IGNORECASE)
            
            for match in matches[:20]:
                vehicle = {
                    'makeName': match[1],
                    'year': match[0],
                    'model': match[2],
                    'sub-model': '',
                    'trim': '',
                    'mileage': '',
                    'value': "${:,}".format(int(match[3].replace(',', ''))),
                    'sale_value': '',
                    'stock_number': '',
                    'engine': ''
                }
                
                context_start = max(0, page_text.find(match[0]) - 100)
                context_end = min(len(page_text), page_text.find(match[0]) + 200)
                context = page_text[context_start:context_end]
                trim = self.extract_trim_from_text(context)
                if trim:
                    vehicle['trim'] = trim
                    vehicle['sub-model'] = trim
                
                if self.is_complete_vehicle(vehicle):
                    vehicles.append(vehicle)
        
        unique_vehicles = []
        seen_combinations = set()
        
        for vehicle in vehicles:
            identifier = (
                vehicle.get('year', ''),
                vehicle.get('makeName', ''),
                vehicle.get('model', ''),
                vehicle.get('stock_number', ''),
                vehicle.get('value', '')
            )
            
            if identifier not in seen_combinations and any(identifier):
                seen_combinations.add(identifier)
                unique_vehicles.append(vehicle)
        
        self.vehicles = unique_vehicles
        logger.info("FINAL RESULT: {} unique vehicles with accurate data".format(len(self.vehicles)))
        
        return self.vehicles

    def save_to_csv(self, filename):
        """Save only if we have real vehicle data - accepts full path"""
        fieldnames = ['makeName', 'year', 'model', 'sub-model', 'trim', 'mileage', 'value', 'sale_value', 'stock_number', 'engine']
        
        if not self.vehicles:
            logger.info("No vehicles found - NOT creating CSV file")
            return False
        
        try:
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for vehicle in self.vehicles:
                    row = {field: vehicle.get(field, '') for field in fieldnames}
                    writer.writerow(row)
            
            logger.info("CSV saved with {} accurate vehicle records to {}".format(len(self.vehicles), filename))
            return True
            
        except Exception as e:
            logger.error("Error saving CSV: {}".format(str(e)))
            return False

    def print_results(self):
        """Print results with accuracy validation"""
        print("\n" + "=" * 100)
        print("RED DEER TOYOTA USED INVENTORY - UNIVERSAL SCRAPER (ALL BRANDS)")
        print("=" * 100)
        
        if not self.vehicles:
            print("No vehicles with complete, accurate data were found.")
            print("\nThis indicates:")
            print("- Website structure may have changed")
            print("- JavaScript-heavy content requires browser automation")
            print("- Anti-scraping protection is active")
            print("- No used vehicles currently available with accessible data")
            print("\nNO CSV file will be created without accurate data.")
            return
        
        print("Found {} vehicles with accurate, complete data".format(len(self.vehicles)))
        print("Generated: {}".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        
        brand_counts = {}
        for vehicle in self.vehicles:
            brand = vehicle.get('makeName', 'Unknown')
            brand_counts[brand] = brand_counts.get(brand, 0) + 1
        
        print("\nBrand Distribution:")
        for brand, count in sorted(brand_counts.items()):
            print("  {}: {} vehicles".format(brand, count))
        
        print("\n{:<12} {:<6} {:<15} {:<12} {:<10} {:<10} {:<10} {:<10} {:<10} {:<20}".format(
            'Make', 'Year', 'Model', 'Sub-Model', 'Trim', 'Mileage', 'Value', 'Sale', 'Stock#', 'Engine'))
        print("-" * 125)
        
        for vehicle in self.vehicles:
            make = vehicle.get('makeName', '')[:11]
            year = vehicle.get('year', '')
            model = vehicle.get('model', '')[:14]
            submodel = vehicle.get('sub-model', '')[:11]
            trim = vehicle.get('trim', '')[:9]
            mileage = vehicle.get('mileage', '')[:9]
            value = vehicle.get('value', '')[:9]
            sale_value = vehicle.get('sale_value', '')[:9]
            stock = vehicle.get('stock_number', '')[:9]
            engine = vehicle.get('engine', '')[:19]
            
            print("{:<12} {:<6} {:<15} {:<12} {:<10} {:<10} {:<10} {:<10} {:<10} {:<20}".format(
                make, year, model, submodel, trim, mileage, value, sale_value, stock, engine))

def main():
    """Main execution - no fallback data"""
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
            csv_saved = scraper.save_to_csv(csv_path)
            print("\nCSV Status: {}".format('Successfully created with accurate data' if csv_saved else 'Failed to create'))
            
            if csv_saved and os.path.exists(csv_path):
                with open(csv_path, 'r') as f:
                    lines = f.readlines()
                    print("{} contains {} lines (including header)".format(csv_path, len(lines)))
        else:
            print("\nCSV Status: No file created - no accurate vehicle data found")
            if os.path.exists(csv_path):
                os.remove(csv_path)
                print("Removed any existing CSV file to prevent stale data")
        
        return 0 if vehicles else 1
        
    except Exception as e:
        logger.error("Scraper failed: {}".format(str(e)))
        print("Error: {}".format(str(e)))
        
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.abspath(os.path.join(script_dir, '..', '..'))
            csv_path = os.path.join(project_root, 'public', 'data', 'inventory.csv')
            if os.path.exists(csv_path):
                os.remove(csv_path)
                print("Removed existing CSV file due to scraper error")
        except Exception:
            pass
        
        return 1

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
