# Luxury trims - COMPLETE LIST
            'AMG': [r'\bAMG\b'],
            'M Sport': [r'\bM\s+Sport\b'],
            'M Performance': [r'\bM\s+Performance\b'],
            'xDrive': [r'\bxDrive\b'],
            'S-Line': [r'\bS-Line\b', r'\bSline\b'],
            'S tronic': [r'\bS\s+tronic\b'],
            'F Sport': [r'\bF\s+Sport\b'],
            'F Sport Handling': [r'\bF\s+Sport\s+Handling\b'],
            'Executive': [r'\bExecutive\b'],
            'Prestige': [r'\bPrestige\b'],
            'Premium Plus': [r'\bPremium\s+Plus\b'],
            'Technik': [r'\bTechnik\b'],
            'Progressiv': [r'\bProgressiv\b'],
            'Komfort': [r'\bKomfort\b'],
            'Luxury Line': [r'\bLuxury\s+Line\b'],
            'Sport Line': [r'\bSport\s+Line\b'],
            'M Package': [r'\bM\s+Package\b'],
            
            # Jeep trims - COMPLETE LIST
            'Sport': [r'\bSport\b(?!\s+Utility)'],
            'Sahara': [r'\bSahara\b'],
            'Rubicon': [r'\bRubicon\b'],
            'Rubicon 392': [r'\bRubicon\s+392\b'],
            'High Altitude': [r'\bHigh\s+Altitude\b'],
            'Overland': [r'\bOverland\b'],
            'Summit': [r'\bSummit\b'],
            'Summit Reserve': [r'\bSummit\s+Reserve\b'],
            'Trailhawk': [r'\bTrailhawk\b'],
            'Limited': [r'\bLimited\b'],
            'Latitude': [r'\bLatitude\b'],
            'Altitude': [r'\bAltitude\b'],
            'Willys': [r'\bWillys\b'],
            'Mojave': [r'\bMojave\b'],
            'Xtreme Recon': [r'\bXtreme\s+Recon\b'],
            '4xe': [r'\b4xe\b'],
            
            # Cadillac trims - COMPLETE LIST
            'Luxury': [r'\bLuxury\b'],
            'Premium Luxury': [r'\bPremium\s+Luxury\b'],
            'Sport': [r'\bSport\b'],
            'V-Series': [r'\bV-Series\b'],
            'Platinum': [r'\bPlatinum\b'],
            'ESV': [r'\bESV\b'],
            
            # Lincoln trims - COMPLETE LIST
            'Premiere': [r'\bPremiere\b'],
            'Reserve': [r'\bReserve\b'],
            'Black Label': [r'\bBlack\s+Label\b'],
            'Grand Touring': [r'\bGrand\s+Touring\b'],
            
            # Volkswagen trims - COMPLETE LIST
            'Trendline': [r'\bTrendline\b'],
            'Comfortline': [r'\bComfortline\b'],
            'Highline': [r'\bHighline\b'],
            'Execline': [r'\bExecline\b'],
            'R-Line': [r'\bR-Line\b'],
            'SEL': [r'\bSEL\b(?!\w)'],
            'SE': [r'\bSE\b(?!\w)'],
            'Autobahn': [r'\bAutobahn\b'],
            'GLI': [r'\bGLI\b'],
            'GTI': [r'\bGTI\b'],
            'Golf R': [r'\bGolf\s+R\b'],
            
            # Lexus trims - COMPLETE LIST
            'Base': [r'\bBase\b'],
            'Premium': [r'\bPremium\b'],
            'Luxury': [r'\bLuxury\b'],
            'F Sport': [r'\bF\s+Sport\b'],
            'F Sport Series 1': [r'\bF\s+Sport\s+Series\s+1\b'],
            'F Sport Series 2': [r'\bF\s+Sport\s+Series\s+2\b'],
            'F Sport Series 3': [r'\bF\s+Sport\s+Series\s+3\b'],
            'Executive': [r'\bExecutive\b'],
            'Ultra Luxury': [r'\bUltra\s+Luxury\b'],
            'Crafted Line': [r'\bCrafted\s+Line\b'],
            
            # Acura trims - COMPLETE LIST
            'Base': [r'\bBase\b'],
            'Premium': [r'\bPremium\b'],
            'Technology': [r'\bTechnology\b'],
            'A-Spec': [r'\bA-Spec\b'],
            'Advance': [r'\bAdvance\b'],
            'Type S': [r'\bType\s+S\b'],
            
            # Infiniti trims - COMPLETE LIST
            'Pure': [r'\bPure\b'],
            'Luxe': [r'\bLuxe\b'],
            'Sensory': [r'\bSensory\b'],
            'ProActive': [r'\bProActive\b'],
            'ProAssist': [r'\bProAssist\b'],
            'Essential': [r'\bEssential\b'],
            'Premium': [r'\bPremium\b'],
            'Red Sport 400': [r'\bRed\s+Sport\s+400\b'],
            
            # Buick trims - COMPLETE LIST
            'Preferred': [r'\bPreferred\b'],
            'Essence': [r'\bEssence\b'],
            'Avenir': [r'\bAvenir\b'],
            'Sport Touring': [r'\bSport\s+Touring\b'],#!/usr/bin/env python3
"""
Red Deer Toyota Used Inventory Scraper - Enhanced Version
Improved vehicle detection and trim extraction for all brands
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

class EnhancedRedDeerToyotaScraper:
    def __init__(self):
        self.base_url = "https://www.reddeertoyota.com"
        self.target_url = "https://www.reddeertoyota.com/inventory/used/"
        self.session = requests.Session()
        
        # Enhanced headers to mimic real browser
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
            'DNT': '1'
        })
        
        self.vehicles = []
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Expanded trim patterns with more variations
        self.trim_patterns = self._build_comprehensive_trim_patterns()
        
        # Car makes database
        self.car_makes = self._build_car_makes_database()

    def _build_comprehensive_trim_patterns(self):
        """Build comprehensive trim pattern dictionary"""
        return {
            # Toyota trims - COMPLETE LIST
            'LE': [r'\bLE\b(?!\w)', r'\bL\.E\.\b'],
            'SE': [r'\bSE\b(?!\w)', r'\bS\.E\.\b'],
            'XLE': [r'\bXLE\b(?!\w)', r'\bX\.L\.E\.\b'],
            'XSE': [r'\bXSE\b(?!\w)', r'\bX\.S\.E\.\b'],
            'Limited': [r'\bLimited\b', r'\bLtd\b'],
            'Platinum': [r'\bPlatinum\b', r'\bPlat\b'],
            'Capstone': [r'\bCapstone\b'],  # ADDED
            'Hybrid': [r'\bHybrid\b', r'\bHV\b'],
            'Prime': [r'\bPrime\b'],
            'TRD': [r'\bTRD\b'],
            'SR': [r'\bSR\b(?!\d)', r'\bS\.R\.\b'],
            'SR5': [r'\bSR5\b', r'\bSR-5\b'],
            'TRD Pro': [r'\bTRD\s+Pro\b', r'\bTRD-Pro\b'],
            'TRD Off-Road': [r'\bTRD\s+Off-?Road\b'],
            'TRD Sport': [r'\bTRD\s+Sport\b'],
            'Nightshade': [r'\bNightshade\b'],
            'Trail': [r'\bTrail\b(?!\w)'],
            'Adventure': [r'\bAdventure\b'],
            'Bronze Edition': [r'\bBronze\s+Edition\b'],
            'Woodland Edition': [r'\bWoodland\s+Edition\b'],
            'TRD Lift': [r'\bTRD\s+Lift\b'],
            'Trail Special Edition': [r'\bTrail\s+Special\s+Edition\b'],
            'XP Predator': [r'\bXP\s+Predator\b'],
            'CrewMax': [r'\bCrewMax\b'],
            'Double Cab': [r'\bDouble\s+Cab\b'],
            'Access Cab': [r'\bAccess\s+Cab\b'],
            
            # Honda trims - COMPLETE LIST
            'LX': [r'\bLX\b(?!\w)', r'\bL\.X\.\b'],
            'DX': [r'\bDX\b(?!\w)', r'\bD\.X\.\b'],
            'EX': [r'\bEX\b(?!\w)', r'\bE\.X\.\b'],
            'EX-L': [r'\bEX-L\b', r'\bEXL\b'],
            'Touring': [r'\bTouring\b'],
            'Sport': [r'\bSport\b(?!\s+Utility)'],
            'Sport Touring': [r'\bSport\s+Touring\b'],
            'Type R': [r'\bType\s+R\b', r'\bType-R\b'],
            'Si': [r'\bSi\b(?!\w)'],
            'Elite': [r'\bElite\b'],
            'Black Edition': [r'\bBlack\s+Edition\b'],
            'TrailSport': [r'\bTrailSport\b', r'\bTrail\s+Sport\b'],
            'Hybrid': [r'\bHybrid\b'],
            'e:HEV': [r'\be:HEV\b', r'\beHEV\b'],
            
            # Ford trims - COMPLETE LIST
            'XL': [r'\bXL\b(?!\w)'],
            'XLT': [r'\bXLT\b'],
            'Lariat': [r'\bLariat\b'],
            'King Ranch': [r'\bKing\s+Ranch\b'],
            'Platinum': [r'\bPlatinum\b'],
            'Limited': [r'\bLimited\b'],
            'Raptor': [r'\bRaptor\b'],
            'Raptor R': [r'\bRaptor\s+R\b'],
            'ST': [r'\bST\b(?!\w)'],
            'RS': [r'\bRS\b(?!\w)'],
            'GT': [r'\bGT\b(?!\w)'],
            'GT500': [r'\bGT500\b'],
            'Mach 1': [r'\bMach\s+1\b', r'\bMach\s*1\b'],
            'Shelby': [r'\bShelby\b'],
            'Tremor': [r'\bTremor\b'],
            'FX4': [r'\bFX4\b'],
            'STX': [r'\bSTX\b'],
            'Titanium': [r'\bTitanium\b'],
            'SEL': [r'\bSEL\b(?!\w)'],
            'SE': [r'\bSE\b(?!\w)'],
            'SES': [r'\bSES\b'],
            'ST-Line': [r'\bST-Line\b'],
            'Wildtrak': [r'\bWildtrak\b'],
            'Badlands': [r'\bBadlands\b'],
            'Outer Banks': [r'\bOuter\s+Banks\b'],
            'Heritage Edition': [r'\bHeritage\s+Edition\b'],
            'Big Bend': [r'\bBig\s+Bend\b'],
            'Black Diamond': [r'\bBlack\s+Diamond\b'],
            'Everglades': [r'\bEverglades\b'],
            'Sport': [r'\bSport\b'],
            'Timberline': [r'\bTimberline\b'],
            
            # Dodge/Ram trims - COMPLETE LIST
            'SXT': [r'\bSXT\b'],
            'GT': [r'\bGT\b(?!\w)'],
            'R/T': [r'\bR/T\b', r'\bRT\b(?!\w)'],
            'SRT': [r'\bSRT\b'],
            'SRT 392': [r'\bSRT\s+392\b'],
            'Hellcat': [r'\bHellcat\b'],
            'Hellcat Redeye': [r'\bHellcat\s+Redeye\b'],
            'Redeye': [r'\bRedeye\b'],
            'Demon': [r'\bDemon\b'],
            'Demon 170': [r'\bDemon\s+170\b'],
            'Scat Pack': [r'\bScat\s+Pack\b', r'\bScatPack\b'],
            'Scat Pack Widebody': [r'\bScat\s+Pack\s+Widebody\b'],
            'Daytona': [r'\bDaytona\b'],
            'Shaker': [r'\bShaker\b'],
            'Jailbreak': [r'\bJailbreak\b'],
            'Super Bee': [r'\bSuper\s+Bee\b'],
            'Big Horn': [r'\bBig\s+Horn\b'],
            'Lone Star': [r'\bLone\s+Star\b'],
            'Laramie': [r'\bLaramie\b'],
            'Laramie Longhorn': [r'\bLaramie\s+Longhorn\b'],
            'Longhorn': [r'\bLonghorn\b'],
            'Rebel': [r'\bRebel\b'],
            'TRX': [r'\bTRX\b'],
            'Limited': [r'\bLimited\b'],
            'Limited Longhorn': [r'\bLimited\s+Longhorn\b'],
            'Warlock': [r'\bWarlock\b'],
            'Night Edition': [r'\bNight\s+Edition\b'],
            'Blacktop': [r'\bBlacktop\b'],
            'Rallye': [r'\bRallye\b'],
            'Express': [r'\bExpress\b'],
            'Tradesman': [r'\bTradesman\b'],
            'SLT': [r'\bSLT\b'],
            'Sport': [r'\bSport\b'],
            
            # Chevrolet trims - COMPLETE LIST
            'LS': [r'\bLS\b(?!\w)'],
            'LT': [r'\bLT\b(?!\w)'],
            'LT1': [r'\bLT1\b'],
            'LTZ': [r'\bLTZ\b'],
            'Premier': [r'\bPremier\b'],
            'High Country': [r'\bHigh\s+Country\b'],
            'Z71': [r'\bZ71\b', r'\bZ-71\b'],
            'SS': [r'\bSS\b(?!\w)'],
            'RST': [r'\bRST\b'],
            'Midnight': [r'\bMidnight\b'],
            'RS': [r'\bRS\b(?!\w)'],
            'ZL1': [r'\bZL1\b'],
            'Z28': [r'\bZ28\b', r'\bZ/28\b'],
            '1LT': [r'\b1LT\b'],
            '2LT': [r'\b2LT\b'],
            '3LT': [r'\b3LT\b'],
            '1SS': [r'\b1SS\b'],
            '2SS': [r'\b2SS\b'],
            'WT': [r'\bWT\b(?!\w)'],
            'Custom': [r'\bCustom\b'],
            'Trail Boss': [r'\bTrail\s+Boss\b'],
            'LT Trail Boss': [r'\bLT\s+Trail\s+Boss\b'],
            'Redline': [r'\bRedline\b'],
            'Activ': [r'\bActiv\b'],
            'Midnight Edition': [r'\bMidnight\s+Edition\b'],
            
            # GMC trims - COMPLETE LIST
            'SLE': [r'\bSLE\b'],
            'SLT': [r'\bSLT\b'],
            'Denali': [r'\bDenali\b'],
            'Denali Ultimate': [r'\bDenali\s+Ultimate\b'],
            'AT4': [r'\bAT4\b', r'\bAT-4\b'],
            'AT4X': [r'\bAT4X\b'],
            'Elevation': [r'\bElevation\b'],
            'Pro': [r'\bPro\b(?!\w)'],
            'Canyon': [r'\bCanyon\b'],
            
            # Nissan trims - COMPLETE LIST
            'S': [r'\b(?<!\w)S(?!\w)'],
            'SV': [r'\bSV\b'],
            'SL': [r'\bSL\b(?!\w)'],
            'SR': [r'\bSR\b(?!\d)'],
            'Platinum': [r'\bPlatinum\b'],
            'Nismo': [r'\bNismo\b'],
            'Pro-4X': [r'\bPro-4X\b', r'\bPro4X\b'],
            'Midnight Edition': [r'\bMidnight\s+Edition\b'],
            'Rock Creek': [r'\bRock\s+Creek\b'],
            'Premium': [r'\bPremium\b'],
            
            # Hyundai trims - COMPLETE LIST
            'Preferred': [r'\bPreferred\b'],
            'Essential': [r'\bEssential\b'],
            'Luxury': [r'\bLuxury\b'],
            'Ultimate': [r'\bUltimate\b'],
            'Calligraphy': [r'\bCalligraphy\b'],
            'N Line': [r'\bN\s+Line\b', r'\bN-Line\b'],
            'N': [r'\bN\b(?!\s+Line)'],
            'SEL': [r'\bSEL\b(?!\w)'],
            'SE': [r'\bSE\b(?!\w)'],
            'Limited': [r'\bLimited\b'],
            'Sport': [r'\bSport\b'],
            'Value Edition': [r'\bValue\s+Edition\b'],
            'Tech': [r'\bTech\b(?!\w)'],
            'Convenience': [r'\bConvenience\b'],
            'Premium': [r'\bPremium\b'],
            'Active': [r'\bActive\b'],
            'Trend': [r'\bTrend\b'],
            'XRT': [r'\bXRT\b'],
            
            # Kia trims - COMPLETE LIST
            'LX': [r'\bLX\b(?!\w)'],
            'EX': [r'\bEX\b(?!\w)'],
            'SX': [r'\bSX\b(?!\w)'],
            'GT-Line': [r'\bGT-Line\b', r'\bGT\s+Line\b'],
            'S': [r'\b(?<!\w)S(?!\w)'],
            'X-Line': [r'\bX-Line\b'],
            'SX Prestige': [r'\bSX\s+Prestige\b'],
            'EX Premium': [r'\bEX\s+Premium\b'],
            'Luxury': [r'\bLuxury\b'],
            'Limited': [r'\bLimited\b'],
            'Nightfall': [r'\bNightfall\b'],
            
            # Subaru trims - COMPLETE LIST
            'Base': [r'\bBase\b'],
            'Premium': [r'\bPremium\b'],
            'Sport': [r'\bSport\b'],
            'Limited': [r'\bLimited\b'],
            'Touring': [r'\bTouring\b'],
            'Touring XT': [r'\bTouring\s+XT\b'],
            'Onyx Edition': [r'\bOnyx\s+Edition\b'],
            'Onyx Edition XT': [r'\bOnyx\s+Edition\s+XT\b'],
            'Wilderness': [r'\bWilderness\b'],
            'STI': [r'\bSTI\b', r'\bS\.T\.I\.\b'],
            'WRX': [r'\bWRX\b'],
            'tS': [r'\btS\b'],
            'XT': [r'\bXT\b(?!\w)'],
            
            # Mazda trims
            'GX': [r'\bGX\b(?!\w)'],
            'GS': [r'\bGS\b(?!\w)'],
            'Grand Touring': [r'\bGrand\s+Touring\b'],
            'Signature': [r'\bSignature\b'],
            
            # Luxury trims
            'AMG': [r'\bAMG\b'],
            'M Sport': [r'\bM\s+Sport\b'],
            'S-Line': [r'\bS-Line\b', r'\bSline\b'],
            'F Sport': [r'\bF\s+Sport\b'],
            'Executive': [r'\bExecutive\b'],
            
            # Generic/Common trims across brands
            'AWD': [r'\bAWD\b', r'\bAll\s+Wheel\s+Drive\b'],
            '4WD': [r'\b4WD\b', r'\b4x4\b', r'\b4X4\b'],
            'FWD': [r'\bFWD\b'],
            '2WD': [r'\b2WD\b'],
            'Extended Cab': [r'\bExtended\s+Cab\b'],
            'Crew Cab': [r'\bCrew\s+Cab\b'],
            'Quad Cab': [r'\bQuad\s+Cab\b'],
            'Regular Cab': [r'\bRegular\s+Cab\b'],
            'SuperCrew': [r'\bSuperCrew\b'],
            'SuperCab': [r'\bSuperCab\b'],
            'Long Bed': [r'\bLong\s+Bed\b'],
            'Short Bed': [r'\bShort\s+Bed\b'],
        }

    def _build_car_makes_database(self):
        """Build comprehensive car makes database"""
        return {
            'Toyota': {'Camry', 'RAV4', 'Highlander', 'Prius', 'Corolla', 'Tacoma', 'Tundra', 
                      'Sienna', '4Runner', 'Sequoia', 'Avalon', 'C-HR', 'Venza', 'GR86', 'Supra',
                      'Yaris', 'Matrix', 'FJ Cruiser', 'Celica', 'Land Cruiser', 'Crown', 'bZ4X',
                      'GR Corolla', 'Solara', 'Echo', 'Tercel', 'Pickup'},
            'Honda': {'Civic', 'Accord', 'CR-V', 'HR-V', 'Pilot', 'Odyssey', 'Fit', 'Ridgeline', 'Passport',
                     'Element', 'Insight', 'Clarity', 'CR-Z', 'S2000', 'Prelude', 'del Sol', 'Crosstour'},
            'Ford': {'F-150', 'F-250', 'F-350', 'F-450', 'Escape', 'Explorer', 'Expedition', 'Edge', 
                    'Fusion', 'Mustang', 'Bronco', 'Bronco Sport', 'Ranger', 'Maverick', 'Focus',
                    'Fiesta', 'Taurus', 'Flex', 'EcoSport', 'Transit', 'Transit Connect', 'E-Series',
                    'Excursion', 'Freestar', 'Windstar', 'Crown Victoria', 'Five Hundred', 'Freestyle'},
            'Chevrolet': {'Silverado', 'Silverado 1500', 'Silverado 2500', 'Silverado 3500', 'Tahoe', 
                         'Suburban', 'Equinox', 'Traverse', 'Malibu', 'Camaro', 'Corvette', 'Colorado', 
                         'Blazer', 'Trax', 'Trailblazer', 'Cruze', 'Impala', 'Sonic', 'Spark', 'Volt',
                         'Bolt', 'Express', 'Avalanche', 'SSR', 'HHR', 'Cobalt', 'Uplander'},
            'GMC': {'Sierra', 'Sierra 1500', 'Sierra 2500', 'Sierra 3500', 'Yukon', 'Yukon XL', 
                   'Acadia', 'Terrain', 'Canyon', 'Savana', 'Envoy', 'Jimmy'},
            'Dodge': {'Charger', 'Challenger', 'Journey', 'Durango', 'Grand Caravan', 'Dart', 'Avenger',
                     'Caravan', 'Magnum', 'Caliber', 'Neon', 'Stratus', 'Intrepid', 'Dakota', 'Nitro'},
            'Ram': {'1500', '2500', '3500', '4500', '5500', 'ProMaster', 'ProMaster City'},
            'Nissan': {'Altima', 'Sentra', 'Rogue', 'Murano', 'Pathfinder', 'Armada', 'Titan', 
                      'Frontier', '370Z', 'GT-R', 'Leaf', 'Kicks', 'Versa', 'Maxima', 'Juke',
                      'Xterra', 'Quest', 'Cube', 'NV', 'NV200', 'Ariya', '350Z', '240SX'},
            'Hyundai': {'Elantra', 'Sonata', 'Tucson', 'Santa Fe', 'Palisade', 'Kona', 'Venue',
                       'Accent', 'Veloster', 'Genesis', 'Azera', 'Santa Cruz', 'Ioniq', 'Ioniq 5',
                       'Ioniq 6', 'Nexo', 'Santa Fe Sport'},
            'Kia': {'Forte', 'Optima', 'K5', 'Sportage', 'Sorento', 'Telluride', 'Soul', 'Seltos',
                   'Stinger', 'Rio', 'Sedona', 'Carnival', 'Niro', 'EV6', 'Borrego', 'Rondo',
                   'Spectra', 'Amanti'},
            'Mazda': {'Mazda3', 'Mazda6', 'CX-3', 'CX-5', 'CX-9', 'CX-30', 'CX-50', 'MX-5', 'MX-5 Miata',
                     'CX-7', 'RX-7', 'RX-8', 'Tribute', 'MPV', 'Protege', 'Millenia', 'MX-30'},
            'Subaru': {'Outback', 'Forester', 'Impreza', 'Legacy', 'Crosstrek', 'Ascent', 'WRX', 'BRZ',
                      'Solterra', 'Baja', 'Tribeca', 'XV Crosstrek'},
            'Volkswagen': {'Jetta', 'Passat', 'Golf', 'Tiguan', 'Atlas', 'Taos', 'ID.4', 'Beetle',
                          'GTI', 'Golf R', 'Touareg', 'CC', 'Eos', 'Rabbit', 'Routan'},
            'BMW': {'3 Series', '5 Series', '7 Series', 'X1', 'X3', 'X5', 'X7', 'Z4', 'i3', 'i4', 'iX',
                   '2 Series', '4 Series', '6 Series', '8 Series', 'X2', 'X4', 'X6', 'M3', 'M4', 'M5'},
            'Mercedes-Benz': {'C-Class', 'E-Class', 'S-Class', 'GLA', 'GLB', 'GLC', 'GLE', 'GLS', 'CLA', 
                             'SL', 'A-Class', 'B-Class', 'CLS', 'G-Class', 'GL-Class', 'ML-Class',
                             'GLK', 'SLC', 'SLK', 'EQB', 'EQE', 'EQS'},
            'Audi': {'A3', 'A4', 'A5', 'A6', 'A7', 'A8', 'Q3', 'Q4 e-tron', 'Q5', 'Q7', 'Q8', 'TT', 'R8',
                    'e-tron', 'Allroad', 'RS3', 'RS4', 'RS5', 'RS6', 'RS7', 'S3', 'S4', 'S5', 'S6'},
            'Lexus': {'ES', 'IS', 'GS', 'LS', 'NX', 'RX', 'GX', 'LX', 'UX', 'LC', 'RC', 'CT', 'HS',
                     'LFA', 'SC'},
            'Infiniti': {'Q50', 'Q60', 'QX50', 'QX55', 'QX60', 'QX80', 'G35', 'G37', 'M35', 'M37',
                        'FX35', 'FX37', 'FX50', 'EX35', 'JX35', 'QX70'},
            'Acura': {'ILX', 'TLX', 'RLX', 'RDX', 'MDX', 'NSX', 'TSX', 'TL', 'RSX', 'RL', 'ZDX',
                     'Integra', 'Legend', 'Vigor', 'CL', 'EL'},
            'Jeep': {'Wrangler', 'Grand Cherokee', 'Cherokee', 'Compass', 'Renegade', 'Gladiator',
                    'Wagoneer', 'Grand Wagoneer', 'Liberty', 'Patriot', 'Commander'},
            'Cadillac': {'Escalade', 'Escalade ESV', 'XT4', 'XT5', 'XT6', 'CT4', 'CT5', 'CTS', 'ATS',
                        'XTS', 'SRX', 'DTS', 'STS', 'CTS-V', 'ATS-V', 'Lyriq'},
            'Lincoln': {'Navigator', 'Aviator', 'Corsair', 'Nautilus', 'Continental', 'MKZ', 'MKX',
                       'MKC', 'MKS', 'MKT', 'Town Car', 'LS'},
            'Buick': {'Enclave', 'Encore', 'Encore GX', 'Envision', 'LaCrosse', 'Regal', 'Verano',
                     'Lucerne', 'Rendezvous', 'Terraza'},
            'Chrysler': {'Pacifica', '300', 'Voyager', 'Aspen', 'Sebring', 'PT Cruiser', 'Town & Country',
                        'Concorde', 'Crossfire', '200'},
            'Tesla': {'Model 3', 'Model S', 'Model X', 'Model Y', 'Cybertruck', 'Roadster'},
            'Mitsubishi': {'Outlander', 'Eclipse Cross', 'Mirage', 'RVR', 'Lancer', 'Montero', 'Galant',
                          'Endeavor', 'Outlander Sport', '3000GT'},
            'Volvo': {'XC90', 'XC60', 'XC40', 'S60', 'S90', 'V60', 'V90', 'C40', 'S40', 'V50', 'V70',
                     'XC70', 'C30', 'C70'},
            'Land Rover': {'Range Rover', 'Range Rover Sport', 'Range Rover Evoque', 'Range Rover Velar',
                          'Discovery', 'Discovery Sport', 'Defender', 'LR2', 'LR3', 'LR4', 'Freelander'},
            'Porsche': {'911', 'Cayenne', 'Macan', 'Panamera', 'Taycan', 'Boxster', 'Cayman', '718'},
            'Jaguar': {'F-Pace', 'E-Pace', 'I-Pace', 'XE', 'XF', 'XJ', 'F-Type', 'X-Type', 'S-Type'},
            'Genesis': {'G70', 'G80', 'G90', 'GV70', 'GV80'},
            'Alfa Romeo': {'Giulia', 'Stelvio', '4C'},
            'Fiat': {'500', '500X', '500L', 'Spider', '124 Spider'},
            'Mini': {'Cooper', 'Cooper Clubman', 'Cooper Countryman', 'Paceman'},
            'Suzuki': {'Grand Vitara', 'SX4', 'Kizashi', 'XL7'},
            'Scion': {'tC', 'xB', 'xD', 'FR-S', 'iM', 'iQ'},
            'Pontiac': {'Grand Prix', 'G6', 'G5', 'Vibe', 'Solstice', 'Torrent', 'Montana'},
            'Saturn': {'Vue', 'Outlook', 'Aura', 'Sky', 'Ion'},
            'Hummer': {'H2', 'H3', 'H3T'},
            'Mercury': {'Grand Marquis', 'Milan', 'Mariner', 'Mountaineer', 'Sable'},
            'Saab': {'9-3', '9-5', '9-7X'},
        }

    def fetch_page_content(self):
        """Fetch page with retry logic"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                logger.info(f"Fetching {self.target_url} (attempt {attempt + 1}/{max_retries})")
                response = self.session.get(self.target_url, timeout=30)
                response.raise_for_status()
                
                logger.info(f"Response: {response.status_code}, Size: {len(response.content)} bytes")
                
                # Check for JavaScript content
                if 'application/json' in response.headers.get('Content-Type', ''):
                    return response.json(), 'json'
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Check for API endpoints in page
                scripts = soup.find_all('script')
                for script in scripts:
                    if script.string and 'inventory' in script.string.lower():
                        # Try to extract JSON data from script tags
                        json_match = re.search(r'({.*"vehicles".*})', script.string, re.DOTALL)
                        if json_match:
                            try:
                                data = json.loads(json_match.group(1))
                                logger.info("Found JSON data in script tag")
                                return data, 'json'
                            except:
                                pass
                
                return soup, 'html'
                
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                else:
                    logger.error("All fetch attempts failed")
                    return None, None

    def extract_trim_from_text(self, text):
        """Extract trim using comprehensive pattern matching"""
        if not text:
            return ''
        
        # Try each trim pattern
        for trim_name, patterns in self.trim_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return trim_name
        
        # Look for common trim indicators
        trim_indicators = [
            r'\b([A-Z]{2,4})\b(?=\s|$)',  # 2-4 uppercase letters
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+(?:Edition|Package|Trim)\b'
        ]
        
        for pattern in trim_indicators:
            match = re.search(pattern, text)
            if match:
                potential_trim = match.group(1).strip()
                if len(potential_trim) >= 2 and potential_trim.upper() not in ['SUV', 'CAR', 'VAN']:
                    return potential_trim
        
        return ''

    def extract_vehicle_from_element(self, element):
        """Enhanced vehicle extraction"""
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
            # Get all text content
            element_text = element.get_text(separator=' ', strip=True)
            element_text = re.sub(r'\s+', ' ', element_text)
            
            # Try to get structured data from attributes first
            for attr in ['data-year', 'data-model-year']:
                if element.get(attr):
                    vehicle['year'] = str(element[attr])
                    break
            
            for attr in ['data-make', 'data-manufacturer']:
                if element.get(attr):
                    vehicle['makeName'] = str(element[attr]).title()
                    break
            
            for attr in ['data-model', 'data-model-name']:
                if element.get(attr):
                    vehicle['model'] = str(element[attr])
                    break
            
            for attr in ['data-trim', 'data-trim-name']:
                if element.get(attr):
                    vehicle['trim'] = str(element[attr])
                    vehicle['sub-model'] = str(element[attr])
                    break
            
            # Extract from text if not found in attributes
            if not vehicle['year']:
                year_match = re.search(r'\b(19[89]\d|20[0-2]\d)\b', element_text)
                if year_match:
                    vehicle['year'] = year_match.group(1)
            
            # Extract make and model
            if not vehicle['makeName'] or not vehicle['model']:
                for make, models in self.car_makes.items():
                    if re.search(r'\b' + re.escape(make) + r'\b', element_text, re.IGNORECASE):
                        if not vehicle['makeName']:
                            vehicle['makeName'] = make
                        
                        for model in models:
                            if re.search(r'\b' + re.escape(model) + r'\b', element_text, re.IGNORECASE):
                                if not vehicle['model']:
                                    vehicle['model'] = model
                                break
                    
                    if vehicle['makeName'] and vehicle['model']:
                        break
            
            # Extract trim if not found
            if not vehicle['trim']:
                trim = self.extract_trim_from_text(element_text)
                if trim:
                    vehicle['trim'] = trim
                    vehicle['sub-model'] = trim
            
            # Enhanced price extraction
            price_patterns = [
                (r'(?:Sale|Now|Special|Internet)\s*Price[:\s]*\$\s*([0-9,]+)', 'sale'),
                (r'(?:Was|List|MSRP|Retail)\s*Price[:\s]*\$\s*([0-9,]+)', 'original'),
                (r'\$\s*([0-9]{2}[0-9,]*)', 'general')
            ]
            
            for pattern, price_type in price_patterns:
                matches = re.findall(pattern, element_text, re.IGNORECASE)
                for match in matches:
                    price_val = int(match.replace(',', ''))
                    if 1000 <= price_val <= 500000:
                        if price_type == 'sale' and not vehicle['sale_value']:
                            vehicle['sale_value'] = str(price_val)
                        elif price_type == 'original' and not vehicle['value']:
                            vehicle['value'] = str(price_val)
                        elif price_type == 'general' and not vehicle['value'] and not vehicle['sale_value']:
                            vehicle['value'] = str(price_val)
            
            # Extract mileage
            mileage_patterns = [
                r'(\d{1,3}(?:,\d{3})*)\s*(?:km|kilometers?|miles?|mi)\b',
                r'(?:Mileage|Odometer)[:\s]*(\d{1,3}(?:,\d{3})*)'
            ]
            
            for pattern in mileage_patterns:
                match = re.search(pattern, element_text, re.IGNORECASE)
                if match:
                    mileage_val = match.group(1).replace(',', '')
                    if mileage_val.isdigit() and 0 <= int(mileage_val) <= 500000:
                        vehicle['mileage'] = mileage_val
                        break
            
            # Extract stock number
            stock_patterns = [
                r'Stock[#\s:]*([A-Z0-9]{3,15})\b',
                r'#\s*([A-Z0-9]{3,15})\b',
                r'VIN[:\s]*([A-Z0-9]{17})\b'
            ]
            
            for pattern in stock_patterns:
                match = re.search(pattern, element_text, re.IGNORECASE)
                if match:
                    stock_val = match.group(1)
                    if len(stock_val) >= 3:
                        vehicle['stock_number'] = stock_val
                        break
            
            # Extract engine
            engine_patterns = [
                r'(\d\.\d+L\s*(?:V?\d+|I\d+|Hybrid|Turbo|Diesel))',
                r'Engine[:\s]*(\d\.\d+L[^,\n]*)',
                r'(\d\.\d+\s*L(?:iter)?[^,\n]*)',
            ]
            
            for pattern in engine_patterns:
                match = re.search(pattern, element_text, re.IGNORECASE)
                if match:
                    engine = match.group(1).strip()
                    engine = re.sub(r'\s+', ' ', engine)
                    vehicle['engine'] = engine
                    break
            
            return vehicle
            
        except Exception as e:
            logger.debug(f"Error extracting vehicle: {e}")
            return vehicle

    def is_valid_vehicle(self, vehicle):
        """Validate vehicle has minimum required data"""
        return (
            vehicle.get('year') and
            vehicle.get('makeName') and
            vehicle.get('model') and
            (vehicle.get('value') or vehicle.get('sale_value') or vehicle.get('stock_number'))
        )

    def find_vehicles_in_html(self, soup):
        """Enhanced vehicle finding with multiple strategies"""
        vehicles = []
        
        # Strategy 1: Look for common vehicle container selectors
        selectors = [
            '[data-vehicle]',
            '[data-vin]',
            '[data-stock]',
            '.vehicle-card',
            '.inventory-item',
            '.srp-list-item',
            '.vehicle-listing',
            '[class*="vehicle"]',
            '[class*="inventory"]',
            'article',
            '.car-item',
            '.listing'
        ]
        
        for selector in selectors:
            elements = soup.select(selector)
            if elements:
                logger.info(f"Found {len(elements)} elements with selector: {selector}")
                
                for element in elements:
                    vehicle = self.extract_vehicle_from_element(element)
                    if self.is_valid_vehicle(vehicle):
                        vehicles.append(vehicle)
                
                if vehicles:
                    logger.info(f"Successfully extracted {len(vehicles)} vehicles using {selector}")
                    return vehicles
        
        # Strategy 2: Look for vehicle data in JSON-LD structured data
        json_ld_scripts = soup.find_all('script', type='application/ld+json')
        for script in json_ld_scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, dict) and data.get('@type') == 'Car':
                    vehicle = self._extract_from_json_ld(data)
                    if self.is_valid_vehicle(vehicle):
                        vehicles.append(vehicle)
                elif isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict) and item.get('@type') == 'Car':
                            vehicle = self._extract_from_json_ld(item)
                            if self.is_valid_vehicle(vehicle):
                                vehicles.append(vehicle)
            except:
                pass
        
        if vehicles:
            return vehicles
        
        # Strategy 3: Parse entire page text for vehicle patterns
        page_text = soup.get_text()
        vehicles = self._extract_from_text(page_text)
        
        return vehicles

    def _extract_from_json_ld(self, data):
        """Extract vehicle from JSON-LD structured data"""
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
        
        vehicle['year'] = str(data.get('modelDate', data.get('productionDate', ''))[:4])
        vehicle['makeName'] = data.get('brand', {}).get('name', '') if isinstance(data.get('brand'), dict) else data.get('brand', '')
        vehicle['model'] = data.get('model', '')
        vehicle['trim'] = data.get('vehicleModelDate', '')
        
        if 'mileageFromOdometer' in data:
            vehicle['mileage'] = str(data['mileageFromOdometer'].get('value', ''))
        
        if 'offers' in data and isinstance(data['offers'], dict):
            price = data['offers'].get('price', '')
            if price:
                vehicle['value'] = str(price)
        
        return vehicle

    def _extract_from_text(self, text):
        """Last resort: extract vehicles from plain text"""
        vehicles = []
        
        # Look for year + make + model patterns
        pattern = r'(20[0-2]\d|19[89]\d)\s+([A-Z][a-z]+)\s+([A-Z][a-z0-9\-]+)'
        matches = re.findall(pattern, text)
        
        for match in matches[:50]:  # Limit to avoid duplicates
            year, make, model = match
            
            # Validate against known makes
            if make in self.car_makes or make.lower() in [m.lower() for m in self.car_makes]:
                vehicle = {
                    'year': year,
                    'makeName': make,
                    'model': model,
                    'sub-model': '',
                    'trim': '',
                    'mileage': '',
                    'value': '',
                    'sale_value': '',
                    'stock_number': '',
                    'engine': ''
                }
                
                # Try to extract more info from surrounding text
                context_start = max(0, text.find(match[0]) - 200)
                context_end = min(len(text), text.find(match[0]) + 200)
                context = text[context_start:context_end]
                
                # Extract trim from context
                trim = self.extract_trim_from_text(context)
                if trim:
                    vehicle['trim'] = trim
                    vehicle['sub-model'] = trim
                
                vehicles.append(vehicle)
        
        return vehicles

    def remove_duplicates(self, vehicles):
        """Remove duplicate vehicles"""
        seen = set()
        unique = []
        
        for vehicle in vehicles:
            key = (
                vehicle.get('year', ''),
                vehicle.get('makeName', ''),
                vehicle.get('model', ''),
                vehicle.get('stock_number', ''),
                vehicle.get('value', '') or vehicle.get('sale_value', '')
            )
            
            if key not in seen and any(key):
                seen.add(key)
                unique.append(vehicle)
        
        return unique

    def scrape_inventory(self):
        """Main scraping method"""
        logger.info("=" * 80)
        logger.info("ENHANCED RED DEER TOYOTA SCRAPER")
        logger.info("=" * 80)
        
        content, content_type = self.fetch_page_content()
        
        if not content:
            logger.error("Failed to fetch page content")
            return []
        
        if content_type == 'json':
            # Handle JSON response
            logger.info("Processing JSON data")
            # Add JSON parsing logic here if needed
            vehicles = []
        else:
            # Handle HTML response
            logger.info("Processing HTML data")
            vehicles = self.find_vehicles_in_html(content)
        
        # Remove duplicates
        vehicles = self.remove_duplicates(vehicles)
        
        self.vehicles = vehicles
        logger.info(f"
