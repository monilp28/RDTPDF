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
        trim_count = 0
        for vehicle in self.vehicles:
            brand = vehicle.get('makeName', 'Unknown')
            brand_counts[brand] = brand_counts.get(brand, 0) + 1
            if vehicle.get('trim'):
                trim_count += 1
        
        print("\nBrand Distribution:")
        for brand, count in sorted(brand_counts.items()):
            print("  {}: {} vehicles".format(brand, count))
        
        print("\nData Completeness:")
        print("  Vehicles with trim data: {} ({:.1f}%)".format(trim_count, 100.0 * trim_count / len(self.vehicles)))
        
        # Count vehicles with different data points
        with_mileage = sum(1 for v in self.vehicles if v.get('mileage'))
        with_price = sum(1 for v in self.vehicles if v.get('value') or v.get('sale_value'))
        with_stock = sum(1 for v in self.vehicles if v.get('stock_number'))
        with_engine = sum(1 for v in self.vehicles if v.get('engine'))
        
        print("  Vehicles with mileage: {} ({:.1f}%)".format(with_mileage, 100.0 * with_mileage / len(self.vehicles)))
        print("  Vehicles with price: {} ({:.1f}%)".format(with_price, 100.0 * with_price / len(self.vehicles)))
        print("  Vehicles with stock#: {} ({:.1f}%)".format(with_stock, 100.0 * with_stock / len(self.vehicles)))
        print("  Vehicles with engine: {} ({:.1f}%)".format(with_engine, 100.0 * with_engine / len(self.vehicles)))
        
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
                make, year, model, submodel, trim, mileage, value, sale_value, stock, engine))#!/usr/bin/env python3
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
                'Camry', 'RAV4', 'Highlander', 'Prius', 'Corolla', 'Corolla Cross', 'Tacoma', 'Tundra', 
                'Sienna', '4Runner', 'Sequoia', 'Avalon', 'C-HR', 'Venza', 'Land Cruiser', 
                'GR86', 'Supra', 'Yaris', 'Yaris Cross', 'Matrix', 'FJ Cruiser', 'Celica', 'MR2', 'Crown',
                'bZ4X', 'GR Corolla', 'Solara', 'Echo', 'Tercel', 'Pickup'
            },
            'Honda': {
                'Civic', 'Accord', 'CR-V', 'HR-V', 'Pilot', 'Odyssey', 'Fit', 'Insight', 
                'Ridgeline', 'Passport', 'Element', 'S2000', 'NSX', 'Prelude', 'del Sol',
                'Clarity', 'CR-Z', 'Crosstour'
            },
            'Ford': {
                'F-150', 'F-250', 'F-350', 'F-450', 'Escape', 'Explorer', 'Expedition', 'Edge', 
                'Fusion', 'Focus', 'Fiesta', 'Mustang', 'Bronco', 'Bronco Sport', 'Ranger', 
                'Transit', 'Transit Connect', 'Taurus', 'Crown Victoria', 'Thunderbird', 
                'Maverick', 'EcoSport', 'Flex', 'Excursion'
            },
            'Chevrolet': {
                'Silverado', 'Silverado 1500', 'Silverado 2500', 'Silverado 3500', 
                'Silverado 2500HD', 'Silverado 3500HD', 'Tahoe', 'Suburban', 'Equinox', 
                'Traverse', 'Malibu', 'Cruze', 'Impala', 'Camaro', 'Corvette', 'Colorado', 
                'Blazer', 'Trax', 'Trailblazer', 'Spark', 'Volt', 'Bolt', 'Sonic', 'Avalanche'
            },
            'GMC': {
                'Sierra', 'Sierra 1500', 'Sierra 2500', 'Sierra 3500', 'Sierra 2500HD', 
                'Sierra 3500HD', 'Yukon', 'Yukon XL', 'Acadia', 'Terrain', 'Canyon', 
                'Savana', 'Envoy', 'Jimmy'
            },
            'Dodge': {
                'Charger', 'Challenger', 'Journey', 'Durango', 'Grand Caravan', 'Caravan',
                'Dart', 'Avenger', 'Nitro', 'Magnum', 'Caliber', 'Dakota'
            },
            'Ram': {
                '1500', '2500', '3500', '1500 Classic', '2500HD', '3500HD', 'ProMaster', 
                'ProMaster City'
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

    def fetch_all_pages(self):
        """Fetch all inventory pages (page 1, 2, 3, etc.)"""
        all_soups = []
        page_num = 1
        max_pages = 10  # Safety limit
        
        while page_num <= max_pages:
            url = "{}?page={}".format(self.target_url.rstrip('/'), page_num)
            
            try:
                logger.info("Fetching page {}: {}".format(page_num, url))
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                
                logger.info("Page {} Response: {}, Size: {} bytes".format(
                    page_num, response.status_code, len(response.content)))
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Check if page has content
                page_text = soup.get_text()
                
                # Check if this page has vehicles (look for year patterns)
                has_vehicles = bool(re.search(r'\b(19[89]\d|20[0-2]\d)\b', page_text))
                
                # Check for "no results" or empty page indicators
                no_results = any([
                    'no vehicles found' in page_text.lower(),
                    'no results' in page_text.lower(),
                    '0 vehicles' in page_text.lower()
                ])
                
                if not has_vehicles or no_results:
                    logger.info("Page {} appears empty or has no vehicles, stopping pagination".format(page_num))
                    break
                
                all_soups.append((page_num, soup))
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
        
        # First pass: Check for multi-word models (e.g., "Corolla Cross", "Range Rover Sport")
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
                            r'\b{}\b'.format(re.escape(model.replace("-", " "))),  # Handle hyphens as spaces
                            r'\b{}\b'.format(re.escape(model.replace(" ", ""))),   # Handle spaces removed
                            r'\b{}\b'.format(re.escape(model.replace("-", "")))    # Handle hyphens removed
                        ]
                        
                        for model_pattern in model_patterns:
                            if re.search(model_pattern, text, re.IGNORECASE):
                                return make, model
        
        # Fallback: generic patterns
        generic_pattern = r'\b(20[0-2][0-9])\s+([A-Z][a-zA-Z-]+)\s+([A-Z][a-zA-Z0-9-\s]+?)(?:\s+[A-Z]{2,}|\s+\d|\s*$)'
        match = re.search(generic_pattern, text)
        if match:
            year, potential_make, potential_model = match.groups()
            potential_model = potential_model.strip()
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
            
            logger.debug("Processing element text: {}...".format(element_text[:150]))
            
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
            
            # Extract trim using enhanced method - make sure it's not part of the model
            trim = self.extract_trim_from_text(element_text)
            if trim:
                # Double check trim is not already in the model name
                if model and trim.lower() not in model.lower():
                    vehicle['trim'] = trim
                    vehicle['sub-model'] = trim
                elif not model:
                    vehicle['trim'] = trim
                    vehicle['sub-model'] = trim
            
            orig_price = None
            sale_price = None

            # Enhanced price patterns
            paired_patterns = [
                r"Was[:\s]*\$\s*([0-9,]+)\s*(?:Now|Sale\s*Price)[:\s]*\$\s*([0-9,]+)",
                r"List\s*Price[:\s]*\$\s*([0-9,]+)\s*(?:Now|Sale\s*Price)[:\s]*\$\s*([0-9,]+)",
                r"Retail\s*Price[:\s]*\$\s*([0-9,]+)\s*(?:Now|Sale\s*Price)[:\s]*\$\s*([0-9,]+)",
                r"\$\s*([0-9,]+)\s+Was\s+\$\s*([0-9,]+)",  # Reversed format
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
                # Find all prices in the text
                all_prices = re.findall(r'\$\s*([0-9,]+)', element_text)
                valid_prices = []
                for price_str in all_prices:
                    try:
                        price = int(price_str.replace(',', ''))
                        if 3000 <= price <= 300000:
                            valid_prices.append(price)
                    except:
                        pass
                
                # If we have prices, use them
                if len(valid_prices) >= 2:
                    # Likely the higher is original, lower is sale
                    valid_prices.sort(reverse=True)
                    orig_price = valid_prices[0]
                    sale_price = valid_prices[1] if valid_prices[1] < orig_price else None
                elif len(valid_prices) == 1:
                    orig_price = valid_prices[0]

            # Assign into vehicle dict
            if sale_price is not None and (orig_price is None or sale_price < orig_price):
                if orig_price is not None:
                    vehicle['value'] = str(orig_price)
                vehicle['sale_value'] = str(sale_price)
            elif orig_price is not None:
                vehicle['value'] = str(orig_price)
            
            # Extract mileage - more patterns
            mileage_patterns = [
                r'(\d{1,3}(?:,\d{3})*)\s*(?:km|kilometers?)\b',
                r'(\d{1,3}(?:,\d{3})*)\s*(?:miles?|mi)\b',
                r'Odometer[:\s]*(\d{1,3}(?:,\d{3})*)',
                r'Mileage[:\s]*(\d{1,3}(?:,\d{3})*)',
                r'(\d{1,3}(?:,\d{3})*)\s*(?:k|K)\s*(?:km|mi|miles?)\b',
                r'(\d{1,3}(?:,\d{3})*)\s+km\b',  # Space before km
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
            
            # Extract stock number - more patterns
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
            
            # Check HTML attributes for additional data
            for attr, value in element.attrs.items():
                attr_lower = attr.lower()
                if 'data-' in attr_lower:
                    if 'year' in attr_lower and not vehicle['year']:
                        if re.match(r'^(19[8-9][0-9]|20[0-2][0-9])

    def is_complete_vehicle(self, vehicle):
        """Check if vehicle has enough accurate data - RELAXED criteria"""
        if not isinstance(vehicle, dict):
            return False
        
        # Must have year and make
        has_year = bool(vehicle.get('year', '').strip())
        has_make = bool(vehicle.get('makeName', '').strip())
        
        if not (has_year and has_make):
            return False
        
        # Must have model OR at least 2 of: price, mileage, stock number
        has_model = bool(vehicle.get('model', '').strip())
        has_price = bool(vehicle.get('value', '').strip() or vehicle.get('sale_value', '').strip())
        has_mileage = bool(vehicle.get('mileage', '').strip())
        has_stock = bool(vehicle.get('stock_number', '').strip())
        
        identifying_count = sum([has_price, has_mileage, has_stock])
        
        # Accept if we have model, or if we have at least 2 identifying fields
        return has_model or identifying_count >= 2

    def find_vehicle_containers(self, soup):
        """Find vehicle container elements with accurate data"""
        vehicles = []
        
        # Strategy 1: Try more specific selectors first
        priority_selectors = [
            '[data-vehicle-id]',
            '[data-stock-number]',
            '[data-vin]',
            '.vehicle-card',
            '.inventory-item',
            '.vehicle-listing',
            '.srp-list-item',
            'article[class*="vehicle"]',
            'div[class*="vehicle-tile"]',
            'li[class*="vehicle"]'
        ]
        
        for selector in priority_selectors:
            elements = soup.select(selector)
            if elements:
                logger.info("Found {} elements with selector: {}".format(len(elements), selector))
                
                for element in elements:
                    vehicle = self.extract_clean_vehicle_data(element)
                    
                    if self.is_complete_vehicle(vehicle):
                        vehicles.append(vehicle)
                        logger.info("Extracted: {} {} {} {} - Stock: {} - Mileage: {}".format(
                            vehicle['year'], vehicle['makeName'], vehicle['model'], 
                            vehicle.get('trim', '(no trim)'), 
                            vehicle.get('stock_number', '(no stock)'),
                            vehicle.get('mileage', '(no mileage)')))
                    else:
                        logger.debug("Incomplete vehicle skipped: {} {} {}".format(
                            vehicle.get('year', '?'), 
                            vehicle.get('makeName', '?'), 
                            vehicle.get('model', '?')))
                
                if vehicles:
                    logger.info("Successfully extracted {} vehicles using {}".format(len(vehicles), selector))
                    return vehicles
        
        # Strategy 2: Try broader selectors
        fallback_selectors = [
            '.vehicle',
            '.car-item',
            '.listing-item',
            '.inventory-card',
            'article',
            'li[class*="item"]',
            'div[class*="card"]',
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
        
        # Strategy 3: Look for any div/section that contains year + make pattern
        logger.info("Strategy 3: Searching all divs for vehicle patterns...")
        all_divs = soup.find_all(['div', 'section', 'article', 'li'])
        
        for div in all_divs:
            div_text = div.get_text(separator=' ', strip=True)
            # Look for year pattern
            if re.search(r'\b(19[89]\d|20[0-2]\d)\b', div_text):
                # Check if it contains a known make
                for make in self.car_makes.keys():
                    if re.search(r'\b' + re.escape(make) + r'\b', div_text, re.IGNORECASE):
                        vehicle = self.extract_clean_vehicle_data(div)
                        if self.is_complete_vehicle(vehicle):
                            vehicles.append(vehicle)
                            break
        
        if vehicles:
            logger.info("Extracted {} vehicles using pattern search in all divs".format(len(vehicles)))
            return vehicles
        
        return vehicles

    def scrape_inventory(self):
        """Main scraping method - only returns accurate data for any brand"""
        logger.info("=" * 80)
        logger.info("UNIVERSAL RED DEER TOYOTA USED INVENTORY SCRAPER")
        logger.info("Extracting accurate data for ANY brand/model - no fallback samples")
        logger.info("=" * 80)
        
        # Fetch all pages
        all_pages = self.fetch_all_pages()
        if not all_pages:
            logger.error("Cannot proceed without any pages")
            return []
        
        all_vehicles = []
        
        # Process each page
        for page_num, soup in all_pages:
            logger.info("=" * 60)
            logger.info("Processing page {}".format(page_num))
            logger.info("=" * 60)
            
            logger.info("Searching for vehicle containers on page {}...".format(page_num))
            page_vehicles = self.find_vehicle_containers(soup)
            
            if not page_vehicles or len(page_vehicles) < 5:
                logger.warning("Found only {} vehicles with selectors on page {}, trying text extraction...".format(
                    len(page_vehicles), page_num))
                
                page_text = soup.get_text()
                
                # Enhanced pattern to catch multi-word models
                make_list = '|'.join(self.car_makes.keys())
                
                # Try to find year + make + model (including multi-word models)
                patterns = [
                    r'(19[8-9]\d|20[0-2]\d)\s+({0})\s+(Corolla Cross|Range Rover Sport|Grand Cherokee|[A-Za-z0-9][A-Za-z0-9\s-]*?)(?=\s+[A-Z]{{2,}}|\s+\$|\s*\n)'.format(make_list),
                    r'(19[8-9]\d|20[0-2]\d)\s+({0})\s+([A-Za-z0-9-]+)'.format(make_list)
                ]
                
                text_vehicles = []
                for pattern in patterns:
                    matches = re.findall(pattern, page_text, re.IGNORECASE | re.MULTILINE)
                    
                    for match in matches:
                        year = match[0]
                        make = match[1]
                        model = match[2].strip()
                        
                        # Find the make in our database (case-insensitive)
                        actual_make = None
                        for m in self.car_makes.keys():
                            if m.lower() == make.lower():
                                actual_make = m
                                break
                        
                        if not actual_make:
                            continue
                        
                        # Check if model exists in our database
                        found_model = None
                        sorted_models = sorted(self.car_makes[actual_make], key=len, reverse=True)
                        for known_model in sorted_models:
                            if known_model.lower() == model.lower() or \
                               known_model.lower().replace(' ', '') == model.lower().replace(' ', ''):
                                found_model = known_model
                                break
                        
                        if not found_model:
                            found_model = model
                        
                        vehicle = {
                            'makeName': actual_make,
                            'year': year,
                            'model': found_model,
                            'sub-model': '',
                            'trim': '',
                            'mileage': '',
                            'value': '',
                            'sale_value': '',
                            'stock_number': '',
                            'engine': ''
                        }
                        
                        # Extract trim from surrounding context
                        match_pos = page_text.find('{} {} {}'.format(year, actual_make, model))
                        if match_pos >= 0:
                            context_start = max(0, match_pos - 150)
                            context_end = min(len(page_text), match_pos + 300)
                            context = page_text[context_start:context_end]
                            
                            trim = self.extract_trim_from_text(context)
                            if trim and trim.lower() not in found_model.lower():
                                vehicle['trim'] = trim
                                vehicle['sub-model'] = trim
                            
                            # Try to extract price from context
                            price_match = re.search(r'\$\s*([0-9,]+)', context)
                            if price_match:
                                try:
                                    price_val = int(price_match.group(1).replace(',', ''))
                                    if 3000 <= price_val <= 300000:
                                        vehicle['value'] = str(price_val)
                                except:
                                    pass
                            
                            # Try to extract mileage from context
                            mileage_match = re.search(r'(\d{1,3}(?:,\d{3})*)\s*(?:km|kilometers?|miles?)', context, re.IGNORECASE)
                            if mileage_match:
                                vehicle['mileage'] = mileage_match.group(1).replace(',', '')
                            
                            # Try to extract stock number from context
                            stock_match = re.search(r'(?:Stock|#)\s*([A-Z0-9]{3,10})', context, re.IGNORECASE)
                            if stock_match:
                                vehicle['stock_number'] = stock_match.group(1)
                        
                        if self.is_complete_vehicle(vehicle):
                            text_vehicles.append(vehicle)
                
                # Merge text-extracted vehicles with selector-extracted ones
                page_vehicles.extend(text_vehicles)
                logger.info("After text extraction on page {}: {} vehicles found".format(page_num, len(page_vehicles)))
            else:
                logger.info("Page {} found {} vehicles using selectors".format(page_num, len(page_vehicles)))
            
            all_vehicles.extend(page_vehicles)
        
        # Remove duplicates based on multiple criteria - IMPROVED
        unique_vehicles = []
        seen_combinations = set()
        seen_details = []  # Store full details for better duplicate detection
        
        for vehicle in all_vehicles:
            # Create a fingerprint of the vehicle
            year = vehicle.get('year', '')
            make = vehicle.get('makeName', '')
            model = vehicle.get('model', '')
            trim = vehicle.get('trim', '')
            stock = vehicle.get('stock_number', '')
            mileage = vehicle.get('mileage', '')
            price = vehicle.get('value', '') or vehicle.get('sale_value', '')
            
            # Primary identifier - stock number is most unique
            if stock:
                identifier = (year, make, model, stock)
                if identifier in seen_combinations:
                    logger.debug("Duplicate found by stock: {} {} {} - Stock: {}".format(year, make, model, stock))
                    continue
                seen_combinations.add(identifier)
                unique_vehicles.append(vehicle)
                seen_details.append({'year': year, 'make': make, 'model': model, 'trim': trim, 
                                    'stock': stock, 'mileage': mileage, 'price': price})
                continue
            
            # Secondary identifier - year + make + model + mileage
            if mileage:
                identifier = (year, make, model, mileage)
                if identifier in seen_combinations:
                    logger.debug("Duplicate found by mileage: {} {} {} - Mileage: {}".format(year, make, model, mileage))
                    continue
                seen_combinations.add(identifier)
                unique_vehicles.append(vehicle)
                seen_details.append({'year': year, 'make': make, 'model': model, 'trim': trim,
                                    'stock': stock, 'mileage': mileage, 'price': price})
                continue
            
            # Tertiary identifier - year + make + model + price
            if price:
                identifier = (year, make, model, price)
                # Check if we already have this combo
                if identifier in seen_combinations:
                    logger.debug("Duplicate found by price: {} {} {} - Price: {}".format(year, make, model, price))
                    continue
                seen_combinations.add(identifier)
                unique_vehicles.append(vehicle)
                seen_details.append({'year': year, 'make': make, 'model': model, 'trim': trim,
                                    'stock': stock, 'mileage': mileage, 'price': price})
                continue
            
            # If no unique identifiers, just use year + make + model + trim
            identifier = (year, make, model, trim)
            if identifier not in seen_combinations and year and make and model:
                seen_combinations.add(identifier)
                unique_vehicles.append(vehicle)
                seen_details.append({'year': year, 'make': make, 'model': model, 'trim': trim,
                                    'stock': stock, 'mileage': mileage, 'price': price})
        
        self.vehicles = unique_vehicles
        logger.info("=" * 80)
        logger.info("FINAL RESULT: {} unique vehicles with accurate data".format(len(self.vehicles)))
        logger.info("Removed {} duplicates".format(len(all_vehicles) - len(self.vehicles)))
        logger.info("=" * 80)
        
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
    exit(exit_code), str(value)):
                            vehicle['year'] = str(value)
                    elif 'make' in attr_lower and not vehicle['makeName']:
                        vehicle['makeName'] = str(value).title()
                    elif 'model' in attr_lower and not vehicle['model']:
                        vehicle['model'] = str(value)
                    elif 'trim' in attr_lower and not vehicle['trim']:
                        trim_val = str(value)
                        # Make sure trim is not part of model
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
        
        # Strategy 1: Try more specific selectors first
        priority_selectors = [
            '[data-vehicle-id]',
            '[data-stock-number]',
            '[data-vin]',
            '.vehicle-card',
            '.inventory-item',
            '.vehicle-listing',
            '.srp-list-item',
            'article[class*="vehicle"]',
            'div[class*="vehicle-tile"]',
            'li[class*="vehicle"]'
        ]
        
        for selector in priority_selectors:
            elements = soup.select(selector)
            if elements:
                logger.info("Found {} elements with selector: {}".format(len(elements), selector))
                
                for element in elements:
                    vehicle = self.extract_clean_vehicle_data(element)
                    
                    if self.is_complete_vehicle(vehicle):
                        vehicles.append(vehicle)
                        logger.info("Extracted complete vehicle: {} {} {} {} - Stock: {}".format(
                            vehicle['year'], vehicle['makeName'], vehicle['model'], 
                            vehicle.get('trim', ''), vehicle['stock_number']))
                
                if vehicles:
                    logger.info("Successfully extracted {} vehicles using {}".format(len(vehicles), selector))
                    return vehicles
        
        # Strategy 2: Try broader selectors
        fallback_selectors = [
            '.vehicle',
            '.car-item',
            '.listing-item',
            '.inventory-card',
            'article',
            'li[class*="item"]',
            'div[class*="card"]',
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
        
        # Strategy 3: Look for any div/section that contains year + make pattern
        logger.info("Strategy 3: Searching all divs for vehicle patterns...")
        all_divs = soup.find_all(['div', 'section', 'article', 'li'])
        
        for div in all_divs:
            div_text = div.get_text(separator=' ', strip=True)
            # Look for year pattern
            if re.search(r'\b(19[89]\d|20[0-2]\d)\b', div_text):
                # Check if it contains a known make
                for make in self.car_makes.keys():
                    if re.search(r'\b' + re.escape(make) + r'\b', div_text, re.IGNORECASE):
                        vehicle = self.extract_clean_vehicle_data(div)
                        if self.is_complete_vehicle(vehicle):
                            vehicles.append(vehicle)
                            break
        
        if vehicles:
            logger.info("Extracted {} vehicles using pattern search in all divs".format(len(vehicles)))
            return vehicles
        
        return vehicles

    def scrape_inventory(self):
        """Main scraping method - only returns accurate data for any brand"""
        logger.info("=" * 80)
        logger.info("UNIVERSAL RED DEER TOYOTA USED INVENTORY SCRAPER")
        logger.info("Extracting accurate data for ANY brand/model - no fallback samples")
        logger.info("=" * 80)
        
        # Fetch all pages
        all_pages = self.fetch_all_pages()
        if not all_pages:
            logger.error("Cannot proceed without any pages")
            return []
        
        all_vehicles = []
        
        # Process each page
        for page_num, soup in all_pages:
            logger.info("=" * 60)
            logger.info("Processing page {}".format(page_num))
            logger.info("=" * 60)
            
            logger.info("Searching for vehicle containers on page {}...".format(page_num))
            page_vehicles = self.find_vehicle_containers(soup)
            
            if not page_vehicles or len(page_vehicles) < 5:
                logger.warning("Found only {} vehicles with selectors on page {}, trying text extraction...".format(
                    len(page_vehicles), page_num))
                
                page_text = soup.get_text()
                
                # Enhanced pattern to catch multi-word models
                make_list = '|'.join(self.car_makes.keys())
                
                # Try to find year + make + model (including multi-word models)
                patterns = [
                    r'(19[8-9]\d|20[0-2]\d)\s+({0})\s+(Corolla Cross|Range Rover Sport|Grand Cherokee|[A-Za-z0-9][A-Za-z0-9\s-]*?)(?=\s+[A-Z]{{2,}}|\s+\$|\s*\n)'.format(make_list),
                    r'(19[8-9]\d|20[0-2]\d)\s+({0})\s+([A-Za-z0-9-]+)'.format(make_list)
                ]
                
                text_vehicles = []
                for pattern in patterns:
                    matches = re.findall(pattern, page_text, re.IGNORECASE | re.MULTILINE)
                    
                    for match in matches:
                        year = match[0]
                        make = match[1]
                        model = match[2].strip()
                        
                        # Find the make in our database (case-insensitive)
                        actual_make = None
                        for m in self.car_makes.keys():
                            if m.lower() == make.lower():
                                actual_make = m
                                break
                        
                        if not actual_make:
                            continue
                        
                        # Check if model exists in our database
                        found_model = None
                        sorted_models = sorted(self.car_makes[actual_make], key=len, reverse=True)
                        for known_model in sorted_models:
                            if known_model.lower() == model.lower() or \
                               known_model.lower().replace(' ', '') == model.lower().replace(' ', ''):
                                found_model = known_model
                                break
                        
                        if not found_model:
                            found_model = model
                        
                        vehicle = {
                            'makeName': actual_make,
                            'year': year,
                            'model': found_model,
                            'sub-model': '',
                            'trim': '',
                            'mileage': '',
                            'value': '',
                            'sale_value': '',
                            'stock_number': '',
                            'engine': ''
                        }
                        
                        # Extract trim from surrounding context
                        match_pos = page_text.find('{} {} {}'.format(year, actual_make, model))
                        if match_pos >= 0:
                            context_start = max(0, match_pos - 150)
                            context_end = min(len(page_text), match_pos + 300)
                            context = page_text[context_start:context_end]
                            
                            trim = self.extract_trim_from_text(context)
                            if trim and trim.lower() not in found_model.lower():
                                vehicle['trim'] = trim
                                vehicle['sub-model'] = trim
                            
                            # Try to extract price from context
                            price_match = re.search(r'\$\s*([0-9,]+)', context)
                            if price_match:
                                try:
                                    price_val = int(price_match.group(1).replace(',', ''))
                                    if 3000 <= price_val <= 300000:
                                        vehicle['value'] = str(price_val)
                                except:
                                    pass
                            
                            # Try to extract mileage from context
                            mileage_match = re.search(r'(\d{1,3}(?:,\d{3})*)\s*(?:km|kilometers?|miles?)', context, re.IGNORECASE)
                            if mileage_match:
                                vehicle['mileage'] = mileage_match.group(1).replace(',', '')
                            
                            # Try to extract stock number from context
                            stock_match = re.search(r'(?:Stock|#)\s*([A-Z0-9]{3,10})', context, re.IGNORECASE)
                            if stock_match:
                                vehicle['stock_number'] = stock_match.group(1)
                        
                        if self.is_complete_vehicle(vehicle):
                            text_vehicles.append(vehicle)
                
                # Merge text-extracted vehicles with selector-extracted ones
                page_vehicles.extend(text_vehicles)
                logger.info("After text extraction on page {}: {} vehicles found".format(page_num, len(page_vehicles)))
            else:
                logger.info("Page {} found {} vehicles using selectors".format(page_num, len(page_vehicles)))
            
            all_vehicles.extend(page_vehicles)
        
        logger.info("=" * 80)
        logger.info("Total vehicles before deduplication: {}".format(len(all_vehicles)))
        
        # Remove duplicates based on multiple criteria
        unique_vehicles = []
        seen_combinations = set()
        
        for vehicle in all_vehicles:
            # Create multiple possible identifiers to catch duplicates
            # Use VIN-like identifier first (most unique)
            identifier1 = (
                vehicle.get('year', ''),
                vehicle.get('makeName', ''),
                vehicle.get('model', ''),
                vehicle.get('stock_number', '')
            )
            
            # Backup identifier using mileage
            identifier2 = (
                vehicle.get('year', ''),
                vehicle.get('makeName', ''),
                vehicle.get('model', ''),
                vehicle.get('mileage', '')
            )
            
            # Backup identifier using price
            identifier3 = (
                vehicle.get('year', ''),
                vehicle.get('makeName', ''),
                vehicle.get('model', ''),
                vehicle.get('value', '') or vehicle.get('sale_value', '')
            )
            
            # Check all identifiers
            is_duplicate = False
            for identifier in [identifier1, identifier2, identifier3]:
                if identifier in seen_combinations and all(identifier):
                    is_duplicate = True
                    break
            
            if not is_duplicate and any(identifier1):
                # Add all valid identifiers to seen set
                if all(identifier1):
                    seen_combinations.add(identifier1)
                if all(identifier2):
                    seen_combinations.add(identifier2)
                if all(identifier3):
                    seen_combinations.add(identifier3)
                    
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
