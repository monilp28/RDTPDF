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
        
        # Universal car makes and models
        self.car_makes = {
            # Toyota models
            'Toyota': {
                'Camry', 'RAV4', 'Highlander', 'Prius', 'Corolla', 'Tacoma', 'Tundra', 
                'Sienna', '4Runner', 'Sequoia', 'Avalon', 'C-HR', 'Venza', 'Land Cruiser', 
                'GR86', 'Supra', 'Yaris', 'Matrix', 'FJ Cruiser', 'Celica', 'MR2'
            },
            # Honda models
            'Honda': {
                'Civic', 'Accord', 'CR-V', 'HR-V', 'Pilot', 'Odyssey', 'Fit', 'Insight', 
                'Ridgeline', 'Passport', 'Element', 'S2000', 'NSX', 'Prelude', 'del Sol'
            },
            # Ford models
            'Ford': {
                'F-150', 'F-250', 'F-350', 'Escape', 'Explorer', 'Expedition', 'Edge', 
                'Fusion', 'Focus', 'Fiesta', 'Mustang', 'Bronco', 'Ranger', 'Transit', 
                'Taurus', 'Crown Victoria', 'Thunderbird'
            },
            # Chevrolet models
            'Chevrolet': {
                'Silverado', 'Tahoe', 'Suburban', 'Equinox', 'Traverse', 'Malibu', 
                'Cruze', 'Impala', 'Camaro', 'Corvette', 'Colorado', 'Blazer', 'Trax'
            },
            # GMC models
            'GMC': {
                'Sierra', 'Yukon', 'Acadia', 'Terrain', 'Canyon', 'Savana', 'Envoy'
            },
            # Dodge/Ram models
            'Dodge': {
                'Charger', 'Challenger', 'Journey', 'Durango', 'Grand Caravan', 'Dart', 'Avenger'
            },
            'Ram': {
                '1500', '2500', '3500', 'ProMaster'
            },
            # Nissan models
            'Nissan': {
                'Altima', 'Sentra', 'Rogue', 'Murano', 'Pathfinder', 'Armada', 'Titan', 
                'Frontier', '370Z', 'GT-R', 'Leaf', 'Kicks', 'Versa'
            },
            # Hyundai models
            'Hyundai': {
                'Elantra', 'Sonata', 'Tucson', 'Santa Fe', 'Palisade', 'Accent', 'Veloster', 
                'Genesis', 'Azera', 'Venue'
            },
            # Kia models
            'Kia': {
                'Forte', 'Optima', 'Sportage', 'Sorento', 'Telluride', 'Soul', 'Stinger', 
                'Rio', 'Sedona', 'Niro'
            },
            # Mazda models
            'Mazda': {
                'Mazda3', 'Mazda6', 'CX-3', 'CX-5', 'CX-9', 'MX-5', 'CX-30', 'RX-7', 'RX-8'
            },
            # Subaru models
            'Subaru': {
                'Outback', 'Forester', 'Impreza', 'Legacy', 'Crosstrek', 'Ascent', 'WRX', 'BRZ'
            },
            # Volkswagen models
            'Volkswagen': {
                'Jetta', 'Passat', 'Golf', 'Tiguan', 'Atlas', 'Beetle', 'GTI', 'Touareg'
            },
            # Luxury brands
            'BMW': {
                '3 Series', '5 Series', '7 Series', 'X1', 'X3', 'X5', 'X7', 'Z4', 'i3', 'i8'
            },
            'Mercedes-Benz': {
                'C-Class', 'E-Class', 'S-Class', 'GLA', 'GLC', 'GLE', 'GLS', 'CLA', 'SL'
            },
            'Audi': {
                'A3', 'A4', 'A6', 'A8', 'Q3', 'Q5', 'Q7', 'Q8', 'TT', 'R8'
            },
            'Lexus': {
                'ES', 'IS', 'GS', 'LS', 'NX', 'RX', 'GX', 'LX', 'UX', 'LC'
            },
            'Infiniti': {
                'Q50', 'Q60', 'QX50', 'QX60', 'QX80', 'G35', 'G37', 'FX35', 'FX37'
            },
            'Acura': {
                'ILX', 'TLX', 'RLX', 'RDX', 'MDX', 'NSX', 'TSX', 'TL', 'RSX'
            },
            # Jeep models
            'Jeep': {
                'Wrangler', 'Grand Cherokee', 'Cherokee', 'Compass', 'Renegade', 'Gladiator', 'Liberty'
            },
            # Cadillac models
            'Cadillac': {
                'Escalade', 'XT4', 'XT5', 'XT6', 'CT4', 'CT5', 'CTS', 'ATS', 'SRX'
            },
            # Lincoln models
            'Lincoln': {
                'Navigator', 'Aviator', 'Corsair', 'Nautilus', 'Continental', 'MKZ', 'MKX'
            },
            # Buick models
            'Buick': {
                'Enclave', 'Encore', 'Envision', 'LaCrosse', 'Regal', 'Verano'
            }
        }

    def fetch_main_page(self):
        """Fetch the main inventory page"""
        try:
            logger.info("Fetching: {}".format(self.target_url))
            response = self.session.get(self.target_url, timeout=30)
            response.raise_for_status()
            
            logger.info("Response: {}, Size: {} bytes".format(response.status_code, len(response.content)))
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Log page info
            title = soup.find('title')
            if title:
                logger.info("Page title: {}".format(title.get_text().strip()))
            
            return soup
            
        except Exception as e:
            logger.error("Failed to fetch main page: {}".format(str(e)))
            return None

    def extract_make_and_model(self, text):
        """Extract make and model from text using comprehensive patterns"""
        # Clean up text
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Try to find make and model combinations
        for make, models in self.car_makes.items():
            # Create patterns for this make
            make_patterns = [
                r'\b{}\b'.format(re.escape(make)),
                r'\b{}\b'.format(re.escape(make.upper())),
                r'\b{}\b'.format(re.escape(make.lower()))
            ]
            
            for make_pattern in make_patterns:
                if re.search(make_pattern, text, re.IGNORECASE):
                    # Found the make, now look for models
                    for model in models:
                        model_patterns = [
                            r'\b{}\b'.format(re.escape(model)),
                            r'\b{}\b'.format(re.escape(model.replace("-", ""))),  # Handle hyphens
                            r'\b{}\b'.format(re.escape(model.replace(" ", "")))   # Handle spaces
                        ]
                        
                        for model_pattern in model_patterns:
                            if re.search(model_pattern, text, re.IGNORECASE):
                                return make, model
        
        # If no exact match found, try generic patterns
        # Look for Year Make Model patterns
        generic_pattern = r'\b(20[0-2][0-9])\s+([A-Z][a-zA-Z-]+)\s+([A-Z][a-zA-Z0-9-]+)\b'
        match = re.search(generic_pattern, text)
        if match:
            year, potential_make, potential_model = match.groups()
            # Validate the potential make against known makes
            for make in self.car_makes.keys():
                if make.lower() == potential_make.lower():
                    return make, potential_model
        
        return None, None

    def extract_clean_vehicle_data(self, element):
        """Extract clean, accurate vehicle data from element - universal version"""
        vehicle = {
            'makeName': '',
            'year': '',
            'model': '',
            'sub-model': '',
            'trim': '',
            'mileage': '',
            'value': '',
            'stock_number': '',
            'engine': ''
        }
        
        try:
            # Get clean text without extra whitespace
            element_text = element.get_text(separator=' ', strip=True)
            element_text = re.sub(r'\s+', ' ', element_text)
            
            logger.debug("Processing element text: {}...".format(element_text[:100]))
            
            # Extract year - must be 4 digits starting with 19 or 20
            year_match = re.search(r'\b(19[8-9][0-9]|20[0-2][0-9])\b', element_text)
            if year_match:
                vehicle['year'] = year_match.group(1)
            
            # Extract make and model using universal method
            make, model = self.extract_make_and_model(element_text)
            if make:
                vehicle['makeName'] = make
            if model:
                vehicle['model'] = model
            
            # Extract trim levels - comprehensive patterns for all brands
            trim_patterns = {
                # Toyota trims
                'LE': r'\bLE\b(?!\w)',
                'SE': r'\bSE\b(?!\w)',
                'XLE': r'\bXLE\b(?!\w)',
                'XSE': r'\bXSE\b(?!\w)',
                'Limited': r'\bLimited\b(?!\w)',
                'Platinum': r'\bPlatinum\b(?!\w)',
                'Hybrid': r'\bHybrid\b(?!\w)',
                'Prime': r'\bPrime\b(?!\w)',
                'TRD': r'\bTRD\b(?!\w)',
                'SR': r'\bSR\b(?!\w)',
                'SR5': r'\bSR5\b(?!\w)',
                'TRD Pro': r'\bTRD\s+Pro\b',
                'TRD Off-Road': r'\bTRD\s+Off-?Road\b',
                'TRD Sport': r'\bTRD\s+Sport\b',
                # Honda trims
                'LX': r'\bLX\b(?!\w)',
                'EX': r'\bEX\b(?!\w)',
                'EX-L': r'\bEX-L\b(?!\w)',
                'Touring': r'\bTouring\b(?!\w)',
                'Sport': r'\bSport\b(?!\w)',
                'Type R': r'\bType\s+R\b',
                'Si': r'\bSi\b(?!\w)',
                # Ford trims - Enhanced
                'XL': r'\bXL\b(?!\w)',
                'XLT': r'\bXLT\b(?!\w)',
                'Lariat': r'\bLariat\b(?!\w)',
                'King Ranch': r'\bKing\s+Ranch\b',
                'Raptor': r'\bRaptor\b(?!\w)',
                'ST': r'\bST\b(?!\w)',
                'RS': r'\bRS\b(?!\w)',
                'GT': r'\bGT\b(?!\w)',
                'Shelby': r'\bShelby\b(?!\w)',
                'Tremor': r'\bTremor\b(?!\w)',
                'FX4': r'\bFX4\b(?!\w)',
                'STX': r'\bSTX\b(?!\w)',
                'SuperCrew': r'\bSuperCrew\b(?!\w)',
                'SuperCab': r'\bSuperCab\b(?!\w)',
                'Titanium': r'\bTitanium\b(?!\w)',
                'SEL': r'\bSEL\b(?!\w)',
                'SES': r'\bSES\b(?!\w)',
                'ST-Line': r'\bST-Line\b(?!\w)',
                'Vignale': r'\bVignale\b(?!\w)',
                'Wildtrak': r'\bWildtrak\b(?!\w)',
                # Dodge trims - Enhanced
                'SXT': r'\bSXT\b(?!\w)',
                'R/T': r'\bR/T\b(?!\w)',
                'RT': r'\bRT\b(?!\w)',
                'SRT': r'\bSRT\b(?!\w)',
                'Hellcat': r'\bHellcat\b(?!\w)',
                'Redeye': r'\bRedeye\b(?!\w)',
                'Demon': r'\bDemon\b(?!\w)',
                'Scat Pack': r'\bScat\s+Pack\b',
                'ScatPack': r'\bScatPack\b(?!\w)',
                'Pursuit': r'\bPursuit\b(?!\w)',
                'Police': r'\bPolice\b(?!\w)',
                'Express': r'\bExpress\b(?!\w)',
                'Tradesman': r'\bTradesman\b(?!\w)',
                'Big Horn': r'\bBig\s+Horn\b',
                'Laramie': r'\bLaramie\b(?!\w)',
                'Rebel': r'\bRebel\b(?!\w)',
                'TRX': r'\bTRX\b(?!\w)',
                'Warlock': r'\bWarlock\b(?!\w)',
                'Night Edition': r'\bNight\s+Edition\b',
                'Blacktop': r'\bBlacktop\b(?!\w)',
                'Rallye': r'\bRallye\b(?!\w)',
                'AWD': r'\bAWD\b(?!\w)',
                'Plus': r'\bPlus\b(?!\w)',
                'Crew': r'\bCrew\b(?!\w)',
                'Quad Cab': r'\bQuad\s+Cab\b',
                'Regular Cab': r'\bRegular\s+Cab\b',
                # Hyundai trims - Enhanced
                'Blue': r'\bBlue\b(?!\w)',
                'SE': r'\bSE\b(?!\w)', # Already defined but important for Hyundai
                'SEL': r'\bSEL\b(?!\w)', # Already defined but important for Hyundai
                'Ultimate': r'\bUltimate\b(?!\w)',
                'Calligraphy': r'\bCalligraphy\b(?!\w)',
                'N Line': r'\bN\s+Line\b',
                'N-Line': r'\bN-Line\b(?!\w)',
                'Preferred': r'\bPreferred\b(?!\w)',
                'Essential': r'\bEssential\b(?!\w)',
                'Luxury': r'\bLuxury\b(?!\w)',
                'Trend': r'\bTrend\b(?!\w)',
                'GL': r'\bGL\b(?!\w)',
                'GLS': r'\bGLS\b(?!\w)',
                'Limited': r'\bLimited\b(?!\w)', # Already defined but important
                'Sport': r'\bSport\b(?!\w)', # Already defined but important
                'Value Edition': r'\bValue\s+Edition\b',
                'Tech': r'\bTech\b(?!\w)',
                'Convenience': r'\bConvenience\b(?!\w)',
                'Premium': r'\bPremium\b(?!\w)', # Already defined but important
                'Active': r'\bActive\b(?!\w)',
                'Preferred AWD': r'\bPreferred\s+AWD\b',
                'Ultimate AWD': r'\bUltimate\s+AWD\b',
                # Chevrolet trims
                'LS': r'\bLS\b(?!\w)',
                'LT': r'\bLT\b(?!\w)',
                'LTZ': r'\bLTZ\b(?!\w)',
                'SS': r'\bSS\b(?!\w)',
                'Z71': r'\bZ71\b(?!\w)',
                'High Country': r'\bHigh\s+Country\b',
                'Premier': r'\bPremier\b(?!\w)',
                'RS': r'\bRS\b(?!\w)', # Already defined but important for Chevy
                'Redline': r'\bRedline\b(?!\w)',
                'Midnight': r'\bMidnight\b(?!\w)',
                # GMC trims
                'Denali': r'\bDenali\b(?!\w)',
                'SLE': r'\bSLE\b(?!\w)',
                'SLT': r'\bSLT\b(?!\w)',
                'AT4': r'\bAT4\b(?!\w)',
                'Elevation': r'\bElevation\b(?!\w)',
                # Nissan trims
                'S': r'\bS\b(?!\w)',
                'SV': r'\bSV\b(?!\w)',
                'SL': r'\bSL\b(?!\w)',
                'SR': r'\bSR\b(?!\w)', # Already defined
                'Nismo': r'\bNismo\b(?!\w)',
                'Midnight Edition': r'\bMidnight\s+Edition\b',
                'Pro-4X': r'\bPro-4X\b(?!\w)',
                # Kia trims  
                'LX': r'\bLX\b(?!\w)', # Already defined
                'S': r'\bS\b(?!\w)', # Already defined
                'EX': r'\bEX\b(?!\w)', # Already defined
                'SX': r'\bSX\b(?!\w)',
                'GT': r'\bGT\b(?!\w)', # Already defined
                'GT-Line': r'\bGT-Line\b(?!\w)',
                'Turbo': r'\bTurbo\b(?!\w)',
                # Mazda trims
                'Sport': r'\bSport\b(?!\w)', # Already defined
                'Touring': r'\bTouring\b(?!\w)', # Already defined
                'Grand Touring': r'\bGrand\s+Touring\b',
                'Signature': r'\bSignature\b(?!\w)',
                'Carbon Edition': r'\bCarbon\s+Edition\b',
                # Subaru trims
                'Base': r'\bBase\b(?!\w)', # Already defined
                'Premium': r'\bPremium\b(?!\w)', # Already defined
                'Limited': r'\bLimited\b(?!\w)', # Already defined
                'Touring': r'\bTouring\b(?!\w)', # Already defined
                'Onyx Edition': r'\bOnyx\s+Edition\b',
                'Wilderness': r'\bWilderness\b(?!\w)',
                'STI': r'\bSTI\b(?!\w)',
                # Luxury trims
                'Base': r'\bBase\b(?!\w)', # Already defined
                'Premium': r'\bPremium\b(?!\w)', # Already defined
                'Luxury': r'\bLuxury\b(?!\w)', # Already defined
                'Executive': r'\bExecutive\b(?!\w)', # Already defined
                'M Sport': r'\bM\s+Sport\b', # Already defined
                'AMG': r'\bAMG\b(?!\w)', # Already defined
                'S-Line': r'\bS-Line\b(?!\w)', # Already defined
                'F Sport': r'\bF\s+Sport\b' # Already defined
            }
            
            for trim_name, pattern in trim_patterns.items():
                if re.search(pattern, element_text, re.IGNORECASE):
                    vehicle['trim'] = trim_name
                    vehicle['sub-model'] = trim_name  # Use same value for both
                    break
            
            # Extract price - be more specific about format
            price_patterns = [
                r'\$([0-9]{2}[0-9,]*)',  # $XX,XXX format
                r'Price[:\s]*\$([0-9,]+)',
                r'MSRP[:\s]*\$([0-9,]+)',
                r'Starting at[:\s]*\$([0-9,]+)'
            ]
            
            for pattern in price_patterns:
                price_match = re.search(pattern, element_text)
                if price_match:
                    price_value = price_match.group(1).replace(',', '')
                    # Validate price is reasonable (between $3,000 and $300,000 for used cars)
                    try:
                        price_int = int(price_value)
                        if 3000 <= price_int <= 300000:
                            vehicle['value'] = price_value
                            break
                    except ValueError:
                        continue
            
            # Extract mileage - more accurate patterns including miles and km
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
                    # Validate mileage is reasonable (0 to 500,000)
                    try:
                        mileage_int = int(mileage_value)
                        if 0 <= mileage_int <= 500000:
                            vehicle['mileage'] = mileage_value
                            break
                    except ValueError:
                        continue
            
            # Extract stock number - more specific
            stock_patterns = [
                r'Stock[#\s]*([A-Z0-9]{3,10})\b',
                r'#([A-Z0-9]{3,10})\b',
                r'ID[:\s]*([A-Z0-9]{3,10})\b',
                r'VIN[:\s]*([A-Z0-9]{17})\b'  # VIN numbers
            ]
            
            for pattern in stock_patterns:
                stock_match = re.search(pattern, element_text, re.IGNORECASE)
                if stock_match:
                    stock_value = stock_match.group(1)
                    # Validate stock number format
                    if len(stock_value) >= 3 and stock_value.isalnum():
                        vehicle['stock_number'] = stock_value
                        break
            
            # Extract engine - much more comprehensive patterns for all brands
            engine_patterns = [
                r'(\d\.\d+L\s*(?:V?\d+|I\d+|[0-9]-?Cyl|Cylinder))',  # 2.5L V6, 1.8L 4Cyl
                r'(\d\.\d+\s*L\s*(?:V?\d+|I\d+|[0-9]-?Cyl))',        # 3.5 L V6
                r'(\d\.\d+L)\s*(?:Engine|Motor)',                     # 2.4L Engine
                r'Engine[:\s]*(\d\.\d+L[^,\n]*)',                     # Engine: 2.0L description
                r'(\d\.\d+L\s*Hybrid)',                               # 1.8L Hybrid
                r'(\d\.\d+L\s*Turbo)',                                # 2.0L Turbo
                r'(\d\.\d+L\s*Supercharged)',                         # 6.2L Supercharged
                r'(\d\.\d+L\s*Diesel)',                               # 3.0L Diesel
                r'(V\d+\s*\d\.\d+L)',                                 # V8 5.0L
                r'(\d+\.\d+\s*Liter)',                                # 3.6 Liter
                r'Electric\s*Motor',                                   # Electric vehicles
                r'(\d+kWh\s*Battery)'                                 # Battery capacity
            ]
            
            for pattern in engine_patterns:
                engine_match = re.search(pattern, element_text, re.IGNORECASE)
                if engine_match:
                    engine_text = engine_match.group(1).strip()
                    # Clean up engine text
                    engine_text = re.sub(r'\s+', ' ', engine_text)
                    
                    # For electric vehicles
                    if 'Electric' in engine_text or 'kWh' in engine_text:
                        vehicle['engine'] = engine_text
                        break
                    
                    # Validate engine size is reasonable (0.8L to 8.0L for most cars)
                    engine_size_match = re.search(r'(\d+\.\d+)L', engine_text)
                    if engine_size_match:
                        engine_size = float(engine_size_match.group(1))
                        if 0.8 <= engine_size <= 8.0:
                            vehicle['engine'] = engine_text
                            break
            
            # Check HTML attributes for additional data
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
                    elif 'price' in attr_lower and not vehicle['value']:
                        price_clean = re.sub(r'[^\d]', '', str(value))
                        if price_clean and 3000 <= int(price_clean) <= 300000:
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
        
        # Must have at least these essential fields
        required_fields = ['year', 'makeName']  # Changed from just model to include make
        has_required = all(vehicle.get(field, '').strip() for field in required_fields)
        
        # Must have at least 1 of these identifying fields
        identifying_fields = ['model', 'value', 'stock_number', 'mileage']
        has_identifying = sum(1 for field in identifying_fields if vehicle.get(field, '').strip()) >= 1
        
        return has_required and has_identifying

    def find_vehicle_containers(self, soup):
        """Find vehicle container elements with accurate data"""
        vehicles = []
        
        # Try more specific selectors first
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
        
        # Try broader selectors if specific ones fail
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
        
        # Fetch main page
        soup = self.fetch_main_page()
        if not soup:
            logger.error("Cannot proceed without main page")
            return []
        
        # Find and extract vehicle data
        logger.info("Searching for vehicle containers...")
        vehicles = self.find_vehicle_containers(soup)
        
        if not vehicles:
            logger.warning("No complete vehicles found with current selectors")
            
            # Try one more approach - look for any text that contains vehicle info
            logger.info("Attempting text-based extraction as final attempt...")
            page_text = soup.get_text()
            
            # Look for structured vehicle information patterns (any brand)
            make_list = '|'.join(self.car_makes.keys())
            vehicle_pattern = r'(19[8-9][0-9]|20[0-2][0-9])\s+({0})\s+([A-Za-z0-9-]+).*?\$([0-9,]+)'.format(make_list)
            
            matches = re.findall(vehicle_pattern, page_text, re.IGNORECASE)
            
            for match in matches[:20]:  # Limit results
                vehicle = {
                    'makeName': match[1],
                    'year': match[0],
                    'model': match[2],
                    'sub-model': '',
                    'trim': '',
                    'mileage': '',
                    'value': "${:,}".format(int(match[3].replace(',', ''))),
                    'stock_number': '',
                    'engine': ''
                }
                
                if self.is_complete_vehicle(vehicle):
                    vehicles.append(vehicle)
        
        # Remove duplicates based on multiple criteria
        unique_vehicles = []
        seen_combinations = set()
        
        for vehicle in vehicles:
            # Create unique identifier
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
        fieldnames = ['makeName', 'year', 'model', 'sub-model', 'trim', 'mileage', 'value', 'stock_number', 'engine']
        
        if not self.vehicles:
            logger.info("No vehicles found - NOT creating CSV file")
            return False
        
        try:
            # Ensure directory exists
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
        
        # Show brand distribution
        brand_counts = {}
        for vehicle in self.vehicles:
            brand = vehicle.get('makeName', 'Unknown')
            brand_counts[brand] = brand_counts.get(brand, 0) + 1
        
        print("\nBrand Distribution:")
        for brand, count in sorted(brand_counts.items()):
            print("  {}: {} vehicles".format(brand, count))
        
        # Print header using .format() to avoid any string issues
        print("\n{:<12} {:<6} {:<15} {:<12} {:<10} {:<10} {:<10} {:<10} {:<20}".format(
            'Make', 'Year', 'Model', 'Sub-Model', 'Trim', 'Mileage', 'Value', 'Stock#', 'Engine'))
        print("-" * 110)
        
        # Print each vehicle
        for vehicle in self.vehicles:
            make = vehicle.get('makeName', '')[:11]
            year = vehicle.get('year', '')
            model = vehicle.get('model', '')[:14]
            submodel = vehicle.get('sub-model', '')[:11]
            trim = vehicle.get('trim', '')[:9]
            mileage = vehicle.get('mileage', '')[:9]
            value = vehicle.get('value', '')[:9]
            stock = vehicle.get('stock_number', '')[:9]
            engine = vehicle.get('engine', '')[:19]
            
            print("{:<12} {:<6} {:<15} {:<12} {:<10} {:<10} {:<10} {:<10} {:<20}".format(
                make, year, model, submodel, trim, mileage, value, stock, engine))

def main():
    """Main execution - no fallback data"""
    scraper = UniversalRedDeerToyotaScraper()
    
    try:
        # Run the precise scraper
        vehicles = scraper.scrape_inventory()
        
        # Display results
        scraper.print_results()
        
        # Determine project root and public/data path so the React app can fetch the CSV
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(script_dir, '..', '..'))
        public_data_dir = os.path.join(project_root, 'public', 'data')
        os.makedirs(public_data_dir, exist_ok=True)
        csv_path = os.path.join(public_data_dir, 'inventory.csv')
        
        # Only save CSV if we have real data
        if vehicles:
            csv_saved = scraper.save_to_csv(csv_path)
            print("\nCSV Status: {}".format('Successfully created with accurate data' if csv_saved else 'Failed to create'))
            
            if csv_saved and os.path.exists(csv_path):
                with open(csv_path, 'r') as f:
                    lines = f.readlines()
                    print("{} contains {} lines (including header)".format(csv_path, len(lines)))
        else:
            print("\nCSV Status: No file created - no accurate vehicle data found")
            # Remove any existing CSV file to avoid stale data
            if os.path.exists(csv_path):
                os.remove(csv_path)
                print("Removed any existing CSV file to prevent stale data")
        
        return 0 if vehicles else 1
        
    except Exception as e:
        logger.error("Scraper failed: {}".format(str(e)))
        print("Error: {}".format(str(e)))
        
        # Remove any existing CSV file on error (inside public/data)
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
