#!/usr/bin/env python3
"""
Red Deer Toyota Used Inventory Scraper
Strategy 1: Hit the dealer's hidden JSON API (no Cloudflare on API endpoints)
Strategy 2: Playwright headless browser fallback (works on residential IPs)

HOW TO FIND THE JSON API (one-time setup):
  1. Open Chrome and go to https://www.reddeertoyota.com/inventory/used/
  2. Press F12 → Network tab → click "Fetch/XHR" filter
  3. Reload the page and watch for requests that return JSON vehicle data
  4. Copy that URL and set it as JSON_API_URL below (or set env var TOYOTA_API_URL)
"""

import csv, time, re, logging, os, json
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

JSON_API_URL = os.environ.get("TOYOTA_API_URL", "")

import requests
from bs4 import BeautifulSoup

SESSION = requests.Session()
SESSION.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/html, */*',
    'Accept-Language': 'en-US,en;q=0.9',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'https://www.reddeertoyota.com/inventory/used/',
})

BASE = "https://www.reddeertoyota.com"
TARGET = "https://www.reddeertoyota.com/inventory/used/"

CAR_MAKES = {
    # ── Toyota ───────────────────────────────────────────────────────────
    'Toyota': {
        'Camry','Camry Hybrid','Corolla','Corolla Cross','Corolla Cross Hybrid',
        'Corolla Hatchback','Yaris','Yaris Sedan','Avalon','Avalon Hybrid',
        'Echo','Prius','Prius C','Prius V','Prius Prime','Crown','Crown Signia',
        'GR86','86','GR Corolla','GR Supra','Supra','Matrix','Venza',
        'RAV4','RAV4 Prime','RAV4 Hybrid','RAV4 Adventure',
        'Highlander','Highlander Hybrid','4Runner','Sequoia',
        'C-HR','Land Cruiser','FJ Cruiser','bZ4X','Tacoma','Tundra','Sienna',
    },
    # ── Honda ─────────────────────────────────────────────────────────────
    'Honda': {
        'Civic','Civic Hatchback','Civic Si','Civic Type R',
        'Accord','Accord Hybrid','Accord Sedan','Accord Coupe',
        'Insight','Jazz','Fit','HR-V','City','CR-V','CR-V Hybrid',
        'Pilot','Passport','Ridgeline','Odyssey','CR-Z','S2000','Element',
    },
    # ── Mazda ─────────────────────────────────────────────────────────────
    'Mazda': {
        'Mazda2','Mazda3','Mazda3 Sport','Mazda5','Mazda6',
        'MX-5','MX-5 Miata','MX-5 RF',
        'CX-3','CX-30','CX-5','CX-50','CX-60','CX-7','CX-8','CX-9','CX-90','MX-30',
        'Tribute','B-Series','B2300','B3000','B4000',
    },
    # ── Nissan ────────────────────────────────────────────────────────────
    'Nissan': {
        'Altima','Sentra','Maxima','Versa','Versa Note','Micra','Leaf','Ariya',
        'Rogue','Rogue Sport','Rogue Select','Murano','Pathfinder',
        'Armada','Kicks','Juke','Xterra','Qashqai','X-Trail','Cube',
        'Frontier','Titan','Titan XD','Quest','NV200','NV Cargo','NV Passenger',
        '370Z','350Z','GT-R',
    },
    # ── Subaru ────────────────────────────────────────────────────────────
    'Subaru': {
        'Impreza','Impreza Sport','Legacy','WRX','WRX STI','BRZ',
        'Outback','Outback Wilderness','Forester','Crosstrek','Crosstrek Hybrid',
        'Ascent','Solterra','Tribeca','XV','Baja',
    },
    # ── Mitsubishi ────────────────────────────────────────────────────────
    'Mitsubishi': {
        'Lancer','Lancer Evolution','Lancer Sportback',
        'Galant','Eclipse','Eclipse Cross','Eclipse Cross PHEV','i-MiEV',
        'Outlander','Outlander PHEV','Outlander Sport','RVR','ASX',
        'Mirage','Mirage G4','Raider',
    },
    # ── Suzuki ────────────────────────────────────────────────────────────
    'Suzuki': {
        'Swift','SX4','SX4 S-Cross','Aerio','Forenza','Reno',
        'Grand Vitara','Vitara','XL-7','Kizashi','Equator',
    },
    # ── Isuzu ─────────────────────────────────────────────────────────────
    'Isuzu': {
        'Rodeo','Trooper','Ascender','i-280','i-290','i-350','i-370',
    },
    # ── Hyundai ───────────────────────────────────────────────────────────
    'Hyundai': {
        'Accent','Accent Hatchback','Elantra','Elantra N','Elantra GT',
        'Elantra Touring','Sonata','Sonata Hybrid','Azera',
        'Ioniq','Ioniq Electric','Ioniq Hybrid','Ioniq Plug-in',
        'Ioniq 5','Ioniq 6','Ioniq 9',
        'Veloster','Veloster N','Genesis Coupe',
        'Tucson','Tucson Hybrid','Santa Fe','Santa Fe XL','Santa Fe Hybrid',
        'Santa Cruz','Palisade','Venue','Kona','Kona Electric','Kona N',
        'ix35','Entourage',
    },
    # ── Kia ───────────────────────────────────────────────────────────────
    'Kia': {
        'Rio','Rio5','Forte','Forte5','Forte Koup',
        'Optima','Optima Hybrid','K5','Stinger','EV6','EV9',
        'Soul','Soul EV','Sportage','Sportage Hybrid',
        'Sorento','Sorento Hybrid','Telluride','Seltos',
        'Niro','Niro EV','Niro PHEV','Niro HEV',
        'Carnival','Sedona','Rondo','Spectra','Magentis','Amanti',
    },
    # ── Genesis ───────────────────────────────────────────────────────────
    'Genesis': {
        'G70','G80','G90','GV70','GV80','GV60','G80 Electrified',
    },
    # ── Ford ──────────────────────────────────────────────────────────────
    'Ford': {
        'Fusion','Fusion Hybrid','Fusion Energi',
        'Focus','Focus ST','Focus RS','Focus Electric',
        'Fiesta','Taurus','Taurus X','Mustang','Mustang Mach-E','Mustang GT',
        'Mustang EcoBoost','C-MAX','C-MAX Hybrid','C-MAX Energi',
        'Escape','Escape Hybrid','Escape PHEV',
        'Edge','Explorer','Explorer Sport','Expedition','Expedition MAX',
        'Bronco','Bronco Sport','EcoSport','Flex','Freestyle',
        'F-150','F-150 Lightning','F-150 Raptor',
        'F-250','F-250 Super Duty','F-350','F-350 Super Duty',
        'F-450','F-450 Super Duty',
        'Ranger','Maverick','Transit','Transit Connect','Transit-150',
        'Transit-250','Transit-350','E-Series','E-150','E-250','E-350','E-Transit',
        'Five Hundred','Freestar',
    },
    # ── Chevrolet ─────────────────────────────────────────────────────────
    'Chevrolet': {
        'Malibu','Malibu Hybrid','Impala','Cruze','Cruze Hatchback',
        'Sonic','Spark','Cobalt','Aveo','Aveo5','Trax','Trax EV',
        'Camaro','Camaro SS','Camaro ZL1','Corvette','Corvette Stingray',
        'Corvette Z06','Volt','Bolt EV','Bolt EUV',
        'Equinox','Equinox EV','Traverse','Tahoe','Suburban',
        'Blazer','Blazer EV','Trailblazer','HHR','Uplander',
        'Silverado','Silverado 1500','Silverado 2500','Silverado 2500HD',
        'Silverado 3500','Silverado 3500HD','Silverado EV',
        'Colorado','Avalanche','Express','Express 1500','Express 2500','Express 3500',
        'Captiva',
    },
    # ── GMC ───────────────────────────────────────────────────────────────
    'GMC': {
        'Sierra','Sierra 1500','Sierra 2500','Sierra 2500HD',
        'Sierra 3500','Sierra 3500HD','Sierra EV',
        'Canyon','Sonoma',
        'Acadia','Terrain','Yukon','Yukon XL','Envoy','Envoy XL',
        'Envision','Safari','Jimmy','Hummer EV',
    },
    # ── Dodge ─────────────────────────────────────────────────────────────
    'Dodge': {
        'Charger','Challenger','Dart','Avenger','Neon','Stratus',
        'Stratus Coupe','Viper','Caliber','Magnum',
        'Durango','Journey','Grand Caravan','Caravan','Hornet',
        'Dakota','Nitro',
    },
    # ── Ram ───────────────────────────────────────────────────────────────
    'Ram': {
        '1500','1500 Classic','1500 TRX',
        '2500','3500','4500','5500',
        'ProMaster','ProMaster City','ProMaster 1500','ProMaster 2500','ProMaster 3500',
        'Dakota',
    },
    # ── Jeep ──────────────────────────────────────────────────────────────
    'Jeep': {
        'Wrangler','Wrangler Unlimited','Wrangler 4xe',
        'Grand Cherokee','Grand Cherokee L','Grand Cherokee 4xe',
        'Cherokee','Compass','Compass Trailhawk',
        'Renegade','Gladiator','Patriot','Commander',
        'Liberty','Grand Wagoneer','Wagoneer','Avenger',
    },
    # ── Chrysler ──────────────────────────────────────────────────────────
    'Chrysler': {
        '200','300','300C','300S','Pacifica','Pacifica Hybrid',
        'Voyager','PT Cruiser','PT Cruiser Convertible',
        'Sebring','Sebring Convertible','Town & Country','Aspen','Crossfire',
    },
    # ── Lincoln ───────────────────────────────────────────────────────────
    'Lincoln': {
        'Navigator','Navigator L','Aviator','Aviator Grand Touring',
        'Corsair','Corsair Grand Touring','Nautilus',
        'MKZ','MKC','MKS','MKT','MKX','Blackwood','Town Car','LS',
    },
    # ── Cadillac ──────────────────────────────────────────────────────────
    'Cadillac': {
        'CT4','CT4-V','CT4-V Blackwing','CT5','CT5-V','CT5-V Blackwing','CT6',
        'ATS','ATS-V','CTS','CTS-V','XTS','STS','STS-V','DTS','DeVille','Eldorado',
        'XT4','XT5','XT5 Platinum','XT6','Escalade','Escalade ESV','Escalade IQ',
        'SRX','Lyriq','Celestiq',
    },
    # ── Buick ─────────────────────────────────────────────────────────────
    'Buick': {
        'Encore','Encore GX','Envision','Envista','Enclave','Enclave Avenir',
        'LaCrosse','Regal','Regal TourX','Regal Sportback',
        'Verano','Cascada','Lucerne','Rendezvous','Rainier','Terraza','Allure',
    },
    # ── Pontiac (discontinued 2010) ───────────────────────────────────────
    'Pontiac': {
        'G3','G5','G6','G6 GTP','G8','Solstice','Torrent',
        'Vibe','Montana','Montana SV6','Aztek',
        'Grand Prix','Grand Am','Bonneville','Pursuit',
    },
    # ── Saturn (discontinued 2010) ────────────────────────────────────────
    'Saturn': {
        'Aura','Ion','Ion Quad Coupe','Vue','Vue Hybrid','Outlook','Sky','Relay',
    },
    # ── Hummer ────────────────────────────────────────────────────────────
    'Hummer': {
        'H1','H1 Alpha','H2','H2 SUT','H3','H3T',
    },
    # ── Tesla ─────────────────────────────────────────────────────────────
    'Tesla': {
        'Model S','Model S Plaid','Model 3','Model 3 Long Range',
        'Model X','Model X Plaid','Model Y','Model Y Long Range',
        'Cybertruck','Roadster',
    },
    # ── Volkswagen ────────────────────────────────────────────────────────
    'Volkswagen': {
        'Jetta','Jetta GLI','Jetta Sportwagen',
        'Passat','Passat CC','Golf','Golf GTI','Golf R',
        'Golf Sportwagen','Golf Alltrack','Golf Wagon',
        'Beetle','New Beetle','Beetle Convertible',
        'Eos','CC','Arteon','ID.4','ID.3','ID.Buzz',
        'Tiguan','Atlas','Atlas Cross Sport','Touareg','Taos','Routan',
    },
    # ── Audi ──────────────────────────────────────────────────────────────
    'Audi': {
        'A3','A3 Sportback','A3 Sedan','A4','A4 Allroad','A4 Avant',
        'A5','A5 Sportback','A5 Cabriolet','A6','A6 Allroad',
        'A7','A8','A8 L','TT','TTS','TT RS',
        'RS3','RS4','RS5','RS6','RS7','RS e-tron GT',
        'S3','S4','S5','S6','S7','S8',
        'e-tron','e-tron GT','e-tron Sportback','Q4 e-tron','Q4 Sportback e-tron',
        'Q3','Q3 Sportback','Q4','Q5','Q5 Sportback','Q7','Q8',
        'SQ3','SQ5','SQ5 Sportback','SQ7','SQ8','RS Q8',
        'Allroad','Cabriolet',
    },
    # ── BMW ───────────────────────────────────────────────────────────────
    'BMW': {
        '1 Series','2 Series','2 Series Gran Coupe','3 Series','3 Series Gran Turismo',
        '4 Series','4 Series Gran Coupe','5 Series','5 Series Gran Turismo',
        '6 Series','6 Series Gran Coupe','6 Series Gran Turismo',
        '7 Series','8 Series','8 Series Gran Coupe',
        'M2','M2 Competition','M3','M3 Competition','M4','M4 Competition',
        'M5','M5 Competition','M6','M8','M8 Competition',
        'Z3','Z4','Z8','i3','i4','i5','i7','i8','iX','iX1','iX3',
        'X1','X2','X3','X3 M','X4','X4 M','X5','X5 M','X6','X6 M','X7','XM',
        '128i','130i','228i','235i','328i','335i','428i','435i',
        '528i','535i','550i','640i','650i','740i','750i','760i',
        'ActiveHybrid','Gran Coupe',
    },
    # ── Mercedes-Benz ─────────────────────────────────────────────────────
    'Mercedes-Benz': {
        'A-Class','A 220','A 250','B-Class','B 250',
        'C-Class','C 300','C 350','C 350e','C 400','C 43','C 63','C 63 S',
        'CLA','CLA 250','CLA 35','CLA 45',
        'CLS','CLS 450','CLS 500','CLS 53','CLS 550',
        'E-Class','E 300','E 350','E 400','E 450','E 550','E 53','E 63',
        'S-Class','S 450','S 500','S 550','S 580','S 650','S 63','S 65',
        'SL','SL 450','SL 550','SLC','SLC 300','SLK','SLK 250','SLK 300','SLK 350',
        'AMG GT','AMG GT S','AMG GT R','AMG GT C','AMG GT 43','AMG GT 53','AMG GT 63',
        'GLA','GLA 250','GLA 35','GLA 45',
        'GLB','GLB 250','GLB 35',
        'GLC','GLC 300','GLC 350e','GLC 43','GLC 63',
        'GLC Coupe','GLE','GLE 350','GLE 400','GLE 450','GLE 53','GLE 63',
        'GLE Coupe','GLS','GLS 450','GLS 580','GLS 600','G-Class','G 550','G 63',
        'AMG GLE 63','EQC','EQE','EQS','EQS SUV','EQE SUV',
        'Metris','Sprinter','Sprinter 1500','Sprinter 2500','Sprinter 3500',
    },
    # ── Porsche ───────────────────────────────────────────────────────────
    'Porsche': {
        '911','911 Carrera','911 Targa','911 Turbo','911 GT3','911 GT2',
        'Boxster','Cayman','718 Boxster','718 Cayman','718 Spyder',
        'Cayenne','Cayenne Coupe','Cayenne E-Hybrid','Cayenne Turbo',
        'Macan','Macan EV','Panamera','Panamera Sport Turismo','Taycan','Taycan Cross Turismo',
    },
    # ── Smart ─────────────────────────────────────────────────────────────
    'Smart': {
        'Fortwo','Fortwo Cabrio','Forfour',
    },
    # ── Land Rover ────────────────────────────────────────────────────────
    'Land Rover': {
        'Range Rover','Range Rover Sport','Range Rover Evoque','Range Rover Velar',
        'Discovery','Discovery Sport','Defender','Defender 90','Defender 110',
        'LR2','LR4','Freelander',
    },
    # ── Jaguar ────────────────────────────────────────────────────────────
    'Jaguar': {
        'XE','XF','XF Sportbrake','XJ','F-Type','F-Type R',
        'E-Pace','F-Pace','F-Pace SVR','I-Pace','XK','XKR','S-Type','X-Type',
    },
    # ── MINI ──────────────────────────────────────────────────────────────
    'MINI': {
        'Cooper','Cooper S','Cooper SE','Cooper Hardtop','Cooper Hatchback',
        'Clubman','Clubman S','Convertible','Countryman','Countryman S',
        'Countryman SE','Paceman','Coupe','Roadster','John Cooper Works',
        'Aceman',
    },
    # ── Fiat ──────────────────────────────────────────────────────────────
    'Fiat': {
        '500','500 Abarth','500 Cabrio','500X','500L','500e',
        '124 Spider','Bravo','Punto','Freemont',
    },
    # ── Alfa Romeo ────────────────────────────────────────────────────────
    'Alfa Romeo': {
        'Giulia','Giulia Quadrifoglio','Stelvio','Stelvio Quadrifoglio',
        '4C','4C Spider','Spider','GTV','Giulietta','Tonale',
    },
    # ── Ferrari ───────────────────────────────────────────────────────────
    'Ferrari': {
        '360','430','430 Scuderia','458','458 Italia','458 Speciale',
        '488','488 GTB','488 Spider','F8','F8 Tributo','SF90','SF90 Stradale',
        '812','812 Superfast','Roma','Portofino','California','California T',
        'GTC4Lusso','FF','Purosangue',
    },
    # ── Lamborghini ───────────────────────────────────────────────────────
    'Lamborghini': {
        'Gallardo','Gallardo Spyder','Huracan','Huracan Evo','Huracan Spyder',
        'Aventador','Aventador S','Aventador SVJ','Urus','Revuelto',
    },
    # ── Maserati ──────────────────────────────────────────────────────────
    'Maserati': {
        'Ghibli','Ghibli S','Quattroporte','Quattroporte S',
        'GranTurismo','GranCabrio','Levante','Levante S','Grecale',
    },
    # ── Volvo ─────────────────────────────────────────────────────────────
    'Volvo': {
        'S40','S60','S60 Cross Country','S80','S90',
        'V40','V60','V60 Cross Country','V70','V90','V90 Cross Country',
        'C30','C70','XC40','XC40 Recharge','XC60','XC70','XC90','C40 Recharge',
    },
    # ── Acura ─────────────────────────────────────────────────────────────
    'Acura': {
        'ILX','TLX','TLX Type S','TL','TSX','TSX Sport Wagon',
        'RL','RLX','RLX Sport Hybrid','CSX','RSX','RSX Type-S',
        'NSX','Integra','Integra Type S',
        'RDX','MDX','MDX Sport Hybrid','CDX','ZDX',
    },
    # ── Lexus ─────────────────────────────────────────────────────────────
    'Lexus': {
        'IS','IS 200t','IS 250','IS 300','IS 350','IS 500','IS F',
        'RC','RC 200t','RC 300','RC 350','RC F',
        'ES','ES 250','ES 300','ES 300h','ES 330','ES 350',
        'GS','GS 200t','GS 250','GS 300','GS 350','GS 450h','GS 460','GS F',
        'LS','LS 430','LS 460','LS 500','LS 500h','LS 600h',
        'LC','LC 500','LC 500h','LFA',
        'NX','NX 200t','NX 300','NX 300h','NX 350','NX 350h','NX 450h+',
        'RX','RX 300','RX 330','RX 350','RX 350h','RX 400h','RX 450h','RX 450h+','RX 500h',
        'GX','GX 460','GX 550','LX','LX 570','LX 600','UX','UX 200','UX 250h','RZ',
    },
    # ── Infiniti ──────────────────────────────────────────────────────────
    'Infiniti': {
        'Q30','Q40','Q45','Q50','Q50S','Q50 Red Sport',
        'Q60','Q60S','Q60 Red Sport','Q70','Q70L','QX30',
        'QX50','QX55','QX60','QX70','QX80',
        'EX','EX35','EX37','FX','FX35','FX37','FX45','FX50',
        'JX','JX35','M','M35','M37','M45','G','G25','G35','G37',
        'I','I30','I35',
    },
    # ── Scion (discontinued 2016) ────────────────────────────────────────
    'Scion': {
        'tC','xB','xD','xA','iA','iM','iQ','FR-S',
    },
    # ── Mercury (discontinued 2011) ───────────────────────────────────────
    'Mercury': {
        'Grand Marquis','Mariner','Mariner Hybrid','Milan','Milan Hybrid',
        'Montego','Monterey','Mountaineer','Sable',
    },
    # ── Oldsmobile (discontinued 2004) ───────────────────────────────────
    'Oldsmobile': {
        'Alero','Aurora','Bravada','Intrigue','Silhouette',
    },
    # ── Saab (discontinued 2011) ──────────────────────────────────────────
    'Saab': {
        '9-2X','9-3','9-3X','9-5','9-7X',
    },
    # ── Daewoo ────────────────────────────────────────────────────────────
    'Daewoo': {
        'Leganza','Lanos','Nubira',
    },
    # ── EVs / New Brands ─────────────────────────────────────────────────
    'Rivian': {
        'R1T','R1S',
    },
    'Lucid': {
        'Air','Air Pure','Air Touring','Air Grand Touring','Air Sapphire',
    },
    'Polestar': {
        '1','2','3','4',
    },
    'Fisker': {
        'Ocean',
    },
    # ── Peugeot ───────────────────────────────────────────────────────────
    'Peugeot': {
        '206','207','208','3008','5008','RCZ','2008','308',
    },
    # ── Renault ───────────────────────────────────────────────────────────
    'Renault': {
        'Megane','Clio','Scenic','Kadjar','Captur','Koleos','Zoe',
    },
}

TRIM_PATTERNS = {
    # Order matters — more specific patterns first to prevent partial matches

    # ── Toyota / Lexus ───────────────────────────────────────────────────
    'TRD Pro':              r'\bTRD\s+Pro\b',
    'TRD Off-Road':         r'\bTRD\s+Off-?Road\b',
    'TRD Sport':            r'\bTRD\s+Sport\b',
    'TRD':                  r'\bTRD\b',
    'SR5':                  r'\bSR5\b',
    'SR':                   r'\bSR\b(?!\d)',
    'XLE Premium':          r'\bXLE\s+Premium\b',
    'XLE':                  r'\bXLE\b',
    'XSE':                  r'\bXSE\b',
    'Capstone':             r'\bCapstone\b',
    'Nightshade':           r'\bNightshade\b',
    'Adventure':            r'\bAdventure\b',
    'CrewMax':              r'\bCrewMax\b',
    'Double Cab':           r'\bDouble\s+Cab\b',
    'Access Cab':           r'\bAccess\s+Cab\b',
    'RAV4 Hybrid':          r'\bRAV4\s+Hybrid\b',
    'Prius Prime':          r'\bPrius\s+Prime\b',
    # Lexus
    'F Sport':              r'\bF\s+Sport\b',
    'Ultra Luxury':         r'\bUltra\s+Luxury\b',

    # ── Ford / Lincoln ───────────────────────────────────────────────────
    'Raptor R':             r'\bRaptor\s+R\b',
    'Raptor':               r'\bRaptor\b',
    'King Ranch':           r'\bKing\s+Ranch\b',
    'Lariat':               r'\bLariat\b',
    'XLT':                  r'\bXLT\b',
    'STX':                  r'\bSTX\b',
    'FX4':                  r'\bFX4\b',
    'FX2':                  r'\bFX2\b',
    'Tremor':               r'\bTremor\b',
    'Wildtrak':             r'\bWildtrak\b',
    'Badlands':             r'\bBadlands\b',
    'Black Diamond':        r'\bBlack\s+Diamond\b',
    'Big Bend':             r'\bBig\s+Bend\b',
    'Outer Banks':          r'\bOuter\s+Banks\b',
    'Bronco First Edition': r'\bFirst\s+Edition\b',
    'ST-Line':              r'\bST-?Line\b',
    'Titanium Hybrid':      r'\bTitanium\s+Hybrid\b',
    'Titanium':             r'\bTitanium\b',
    'Trend':                r'\bTrend\b',
    'Ambiente':             r'\bAmbiente\b',
    # Lincoln
    'Black Label':          r'\bBlack\s+Label\b',
    'Reserve':              r'\bReserve\b',

    # ── GM (Chevy / GMC / Buick / Cadillac) ─────────────────────────────
    'High Country':         r'\bHigh\s+Country\b',
    'LT Trail Boss':        r'\bLT\s+Trail\s+Boss\b',
    'Trail Boss':           r'\bTrail\s+Boss\b',
    'LTZ':                  r'\bLTZ\b',
    'Z71':                  r'\bZ71\b',
    'ZR2':                  r'\bZR2\b',
    'ZL1':                  r'\bZL1\b',
    'AT4X':                 r'\bAT4X\b',
    'AT4':                  r'\bAT4\b',
    'Denali Ultimate':      r'\bDenali\s+Ultimate\b',
    'Denali':               r'\bDenali\b',
    'SLT':                  r'\bSLT\b',
    'SLE':                  r'\bSLE\b',
    # Cadillac
    'V-Series Blackwing':   r'\bV-Series\s+Blackwing\b',
    'V-Series':             r'\bV-Series\b',
    'Blackwing':            r'\bBlackwing\b',
    'Premium Luxury':       r'\bPremium\s+Luxury\b',
    # Buick
    'Avenir':               r'\bAvenir\b',
    'Essence':              r'\bEssence\b',
    'Preferred':            r'\bPreferred\b',

    # ── Dodge / Ram / Jeep / Chrysler ────────────────────────────────────
    'Hellcat Redeye':       r'\bHellcat\s+Redeye\b',
    'Hellcat':              r'\bHellcat\b',
    'Jailbreak':            r'\bJailbreak\b',
    'Widebody':             r'\bWidebody\b',
    'Scat Pack':            r'\bScat\s+Pack\b',
    'SRT 392':              r'\bSRT\s+392\b',
    'SRT':                  r'\bSRT\b',
    'R/T':                  r'\bR/T\b',
    'SXT Plus':             r'\bSXT\s+Plus\b',
    'SXT':                  r'\bSXT\b',
    'TRX':                  r'\bTRX\b',
    'Rebel':                r'\bRebel\b',
    'Laramie Longhorn':     r'\bLaramie\s+Longhorn\b',
    'Limited Longhorn':     r'\bLimited\s+Longhorn\b',
    'Laramie':              r'\bLaramie\b',
    'Longhorn':             r'\bLonghorn\b',
    'Big Horn':             r'\bBig\s+Horn\b',
    'Night Edition':        r'\bNight\s+Edition\b',
    'Power Wagon':          r'\bPower\s+Wagon\b',
    # Jeep
    'Rubicon 392':          r'\bRubicon\s+392\b',
    'Rubicon':              r'\bRubicon\b',
    'Sahara':               r'\bSahara\b',
    'Willys Sport':         r'\bWillys\s+Sport\b',
    'Willys':               r'\bWillys\b',
    'Trailhawk':            r'\bTrailhawk\b',
    'Summit Reserve':       r'\bSummit\s+Reserve\b',
    'Altitude':             r'\bAltitude\b',
    'Mojave':               r'\bMojave\b',
    'Freedom':              r'\bFreedom\b',
    'Wagoneer Series III':  r'\bWagoneer\s+Series\s+III\b',
    'Wagoneer Series II':   r'\bWagoneer\s+Series\s+II\b',
    'Wagoneer Series I':    r'\bWagoneer\s+Series\s+I\b',

    # ── Nissan / Infiniti ────────────────────────────────────────────────
    'Nismo':                r'\bNismo\b',
    'Pro-4X':               r'\bPro-4X\b',
    'Pro-2X':               r'\bPro-2X\b',
    'Midnight Edition':     r'\bMidnight\s+Edition\b',
    'Rock Creek':           r'\bRock\s+Creek\b',
    'Red Sport 400':        r'\bRed\s+Sport\s+400\b',
    'Red Sport':            r'\bRed\s+Sport\b',

    # ── Hyundai / Kia / Genesis ──────────────────────────────────────────
    'Calligraphy':          r'\bCalligraphy\b',
    'N Line':               r'\bN\s+Line\b',
    'Ultimate':             r'\bUltimate\b',
    'Essential':            r'\bEssential\b',
    'Prestige':             r'\bPrestige\b',
    'Luxury':               r'\bLuxury\b',

    # ── Subaru ───────────────────────────────────────────────────────────
    'Wilderness':           r'\bWilderness\b',
    'Onyx Edition XT':      r'\bOnyx\s+Edition\s+XT\b',
    'Onyx Edition':         r'\bOnyx\s+Edition\b',
    'Limited XT':           r'\bLimited\s+XT\b',
    'Sport XT':             r'\bSport\s+XT\b',
    'XT':                   r'\bXT\b(?!\w)',

    # ── Volkswagen ────────────────────────────────────────────────────────
    'Execline':             r'\bExecline\b',
    'Highline':             r'\bHighline\b',
    'Comfortline':          r'\bComfortline\b',
    'Trendline':            r'\bTrendline\b',
    'Sportline':            r'\bSportline\b',
    'R-Line':               r'\bR-?Line\b',
    'GTI':                  r'\bGTI\b',
    'Autobahn':             r'\bAutobahn\b',
    'Progressiv':           r'\bProgressiv\b',

    # ── Audi ─────────────────────────────────────────────────────────────
    'Technik':              r'\bTechnik\b',
    'Komfort':              r'\bKomfort\b',
    'Quattro':              r'\bQuattro\b',

    # ── BMW ──────────────────────────────────────────────────────────────
    'M Sport':              r'\bM\s+Sport\b',
    'xDrive':               r'\bxDrive\b',
    'sDrive':               r'\bsDrive\b',

    # ── Mercedes-Benz ─────────────────────────────────────────────────────
    'AMG Line':             r'\bAMG\s+Line\b',
    'AMG':                  r'\bAMG\b',
    '4MATIC+':              r'\b4MATIC\+\b',
    '4MATIC':               r'\b4MATIC\b',

    # ── Honda / Acura ────────────────────────────────────────────────────
    'Type R':               r'\bType\s+R\b',
    'Sport Touring':        r'\bSport\s+Touring\b',
    'EX-L Navi':            r'\bEX-L\s+Navi\b',
    'EX-L':                 r'\bEX-L\b',
    'A-Spec':               r'\bA-?Spec\b',
    'Advance':              r'\bAdvance\b',
    'TrailSport':           r'\bTrailSport\b',
    'Elite':                r'\bElite\b',

    # ── Mazda ────────────────────────────────────────────────────────────
    'Signature':            r'\bSignature\b',
    'Carbon Edition':       r'\bCarbon\s+Edition\b',
    'Turbo':                r'\bTurbo\b',

    # ── Volvo ────────────────────────────────────────────────────────────
    'Inscription Expression': r'\bInscription\s+Expression\b',
    'Inscription':          r'\bInscription\b',
    'Momentum Pro':         r'\bMomentum\s+Pro\b',
    'Momentum':             r'\bMomentum\b',
    'R-Design':             r'\bR-?Design\b',
    'Polestar Engineered':  r'\bPolestar\s+Engineered\b',

    # ── Generic / Universal ──────────────────────────────────────────────
    'Platinum':             r'\bPlatinum\b',
    'Limited':              r'\bLimited\b',
    'Touring L':            r'\bTouring\s+L\b',
    'Touring':              r'\bTouring\b',
    'Premium':              r'\bPremium\b',
    'Sport':                r'\bSport\b(?!\s+Utility)',
    'GT':                   r'\bGT\b(?!\w)',
    'ST':                   r'\bST\b(?!\w)',
    'RS':                   r'\bRS\b(?!\d)',
    'SS':                   r'\bSS\b(?!\w)',
    'LS':                   r'\bLS\b(?!\w)',
    'LT':                   r'\bLT\b(?!\w)',
    'SL':                   r'\bSL\b(?!\w)',
    'SV':                   r'\bSV\b',
    'SE':                   r'\bSE\b(?!\w)',
    'LE':                   r'\bLE\b(?!\w)',
    'EX':                   r'\bEX\b(?!\w)',
    'LX':                   r'\bLX\b(?!\w)',
    'Si':                   r'\bSi\b(?!\w)',
    'Hybrid':               r'\bHybrid\b',
    'Prime':                r'\bPrime\b',
    'PHEV':                 r'\bPHEV\b',
    'Electric':             r'\bElectric\b',
    'AWD':                  r'\bAWD\b',
    '4WD':                  r'\b4WD\b',
    '4x4':                  r'\b4x4\b',
    '4x2':                  r'\b4x2\b',
    'Crew Cab':             r'\bCrew\s+Cab\b',
    'Extended Cab':         r'\bExtended\s+Cab\b',
    'Double Cab':           r'\bDouble\s+Cab\b',
    'Regular Cab':          r'\bRegular\s+Cab\b',
    'Long Box':             r'\bLong\s+Box\b',
    'Short Box':            r'\bShort\s+Box\b',
    'Long Bed':             r'\bLong\s+Bed\b',
    'Short Bed':            r'\bShort\s+Bed\b',
    'IVT':                  r'\bIVT\b',
    'Summit':               r'\bSummit\b',
    'Overland':             r'\bOverland\b',
    'Pro':                  r'\bPro\b(?!\s*-)',
    'XL':                   r'\bXL\b(?!\w)',
}

# Common dealer platform API URL patterns to auto-discover
API_CANDIDATES = [
    "/apis/widget/INVENTORY_LISTING_DEFAULT_AUTO_USED:inventory-data-bus1/getInventory",
    "/apis/widget/INVENTORY_LISTING_DEFAULT_AUTO_USED:inventory-data-bus1/getInventory?pageSize=100",
    "/apis/widget/INVENTORY_LISTING_DEFAULT_AUTO_ALL:inventory-data-bus1/getInventory?condition=used",
    "/api/inventory/listings?condition=used&pageSize=100",
    "/api/inventory/search?condition=used",
    "/api/vehicles/used",
    "/inventory/api/used",
    "/inventory/used.json",
    "/_api/inventory?type=used",
    "/ajax/inventory?condition=used",
    "/inventory/listing?type=used&format=json",
    "/inventory/search?format=json&type=used",
    "/vehicle/search?condition=used&format=json",
    "/api/search/vehicle?condition=used",
    "/api/srp/vehicles?condition=used",
    "/api/srp/listings?condition=used",
    "/toyota/inventory/used",
    "/api/toyota/inventory?condition=used",
]


# -----------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------

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


def extract_prices_from_text(text):
    prices = []
    for m in re.finditer(r'\$\s*([0-9,]{4,})', text):
        try:
            p = int(m.group(1).replace(',',''))
            if 3000 <= p <= 300000:
                ctx = text[max(0,m.start()-80):m.end()+80].lower()
                prices.append({
                    'price': p,
                    'is_sale': any(k in ctx for k in ['sale','internet','special','now','reduced']),
                    'is_msrp': any(k in ctx for k in ['msrp','was','original','regular','list']),
                })
        except Exception:
            pass
    if not prices:
        return None, None
    deduped = {}
    for p in prices:
        if p['price'] not in deduped or p['is_sale'] or p['is_msrp']:
            deduped[p['price']] = p
    prices = list(deduped.values())
    msrp = [p['price'] for p in prices if p['is_msrp']]
    sale = [p['price'] for p in prices if p['is_sale']]
    if msrp and sale:
        reg, sal = max(msrp), min(sale)
    elif len(prices) >= 2:
        sp = sorted([p['price'] for p in prices], reverse=True)
        reg, sal = sp[0], (sp[1] if sp[1] < sp[0] else None)
    else:
        reg, sal = prices[0]['price'], None
    if reg and sal and sal >= reg:
        sal = None
    return reg, sal


def vehicle_from_json(item):
    v = {'makeName':'','year':'','model':'','sub-model':'','trim':'',
         'mileage':'','value':'','sale_value':'','stock_number':'','engine':''}
    field_map = {
        'makeName':    ['make','makeName','Make','manufacturer'],
        'year':        ['year','modelYear','Year','yr'],
        'model':       ['model','modelName','Model'],
        'trim':        ['trim','trimName','Trim','trimLevel','subModel'],
        'mileage':     ['mileage','odometer','miles','km','Mileage','Odometer'],
        'value':       ['price','listPrice','retailPrice','msrp','Price','salePrice',
                        'internetPrice','sellingPrice','askingPrice'],
        'sale_value':  ['salePrice','internetPrice','specialPrice','discountPrice',
                        'webPrice','ourPrice'],
        'stock_number':['stockNumber','stock','stockNum','StockNumber','vin'],
        'engine':      ['engine','engineDescription','engineSize'],
    }
    for our_key, candidates in field_map.items():
        for c in candidates:
            val = item.get(c) or item.get(c.lower()) or item.get(c.upper())
            if val:
                v[our_key] = str(val).strip()
                break
    if v['value'] and v['sale_value']:
        try:
            if int(re.sub(r'[^\d]','',v['sale_value'])) >= int(re.sub(r'[^\d]','',v['value'])):
                v['sale_value'] = ''
        except Exception:
            pass
    v['sub-model'] = v['trim']
    return v


def parse_html_element(element, idx=0):
    v = {'makeName':'','year':'','model':'','sub-model':'','trim':'',
         'mileage':'','value':'','sale_value':'','stock_number':'','engine':''}
    try:
        text = re.sub(r'\s+', ' ', element.get_text(separator=' ', strip=True))
        m = re.search(r'\b(19[89]\d|20[0-2]\d)\b', text)
        if m: v['year'] = m.group(1)
        make, model = extract_make_model(text)
        if make: v['makeName'] = make
        if model: v['model'] = model
        trim = extract_trim(text, model)
        if trim: v['trim'] = trim; v['sub-model'] = trim
        for pat in [r'Stock[#:\s]*([A-Z0-9]{3,15})\b', r'#\s*([A-Z0-9]{3,15})\b']:
            m2 = re.search(pat, text, re.IGNORECASE)
            if m2 and m2.group(1).isalnum() and len(m2.group(1)) >= 3:
                v['stock_number'] = m2.group(1); break
        reg, sal = extract_prices_from_text(text)
        if reg: v['value'] = str(reg)
        if sal: v['sale_value'] = str(sal)
        for pat in [r'(\d{1,3}(?:,\d{3})*)\s*(?:km|kilometers?)\b',
                    r'(\d{1,3}(?:,\d{3})*)\s*(?:miles?|mi)\b']:
            m3 = re.search(pat, text, re.IGNORECASE)
            if m3:
                val = m3.group(1).replace(',','')
                if 0 <= int(val) <= 500000: v['mileage'] = val; break
        for pat in [r'(\d\.\d+L\s*(?:V?\d+|I\d+))',r'(\d\.\d+L\s*Hybrid)',r'(\d\.\d+L\s*Turbo)']:
            m4 = re.search(pat, text, re.IGNORECASE)
            if m4: v['engine'] = m4.group(1).strip(); break
    except Exception as e:
        logger.debug("HTML parse error {}: {}".format(idx, e))
    return v


def is_valid(v):
    if not (v.get('year','').strip() and v.get('makeName','').strip()):
        return False
    extras = ['model','value','sale_value','stock_number','mileage']
    return bool(v.get('model','').strip()) or sum(1 for f in extras if v.get(f,'').strip()) >= 2


def completeness(v):
    fields = ['stock_number', 'mileage', 'engine', 'trim', 'value', 'sale_value']
    return sum(1 for f in fields if v.get(f, '').strip())


def dedup(vehicles):
    by_stock = {}
    no_stock = []
    for v in vehicles:
        stock = v.get('stock_number', '').strip()
        if stock:
            if stock not in by_stock or completeness(v) > completeness(by_stock[stock]):
                by_stock[stock] = v
        else:
            no_stock.append(v)
    stocked = list(by_stock.values())
    stocked_ymmp = set()
    for v in stocked:
        stocked_ymmp.add((v.get('year',''), v.get('makeName',''), v.get('model',''), v.get('value','')))
    extra = []
    seen_extra = set()
    for v in no_stock:
        ymmp = (v.get('year',''), v.get('makeName',''), v.get('model',''), v.get('value',''))
        if ymmp in stocked_ymmp or ymmp in seen_extra:
            continue
        seen_extra.add(ymmp)
        extra.append(v)
    return stocked + extra


# -----------------------------------------------------------------------
# Strategy 1: JSON API
# -----------------------------------------------------------------------

def try_json_api(url):
    try:
        resp = SESSION.get(url, timeout=15)
        if resp.status_code != 200:
            return []
        ct = resp.headers.get('Content-Type','')
        if 'json' not in ct and not resp.text.strip().startswith(('{','[')):
            return []
        data = resp.json()
        if isinstance(data, dict):
            for key in ['vehicles','inventory','listings','results','data',
                        'items','records','vehicles_list','vehicleList']:
                if key in data and isinstance(data[key], list):
                    data = data[key]
                    break
            if isinstance(data, dict):
                for v in data.values():
                    if isinstance(v, list) and len(v) > 0 and isinstance(v[0], dict):
                        data = v
                        break
        if not isinstance(data, list) or len(data) == 0:
            return []
        vehicles = []
        for item in data:
            if not isinstance(item, dict):
                continue
            v = vehicle_from_json(item)
            if is_valid(v):
                vehicles.append(v)
        logger.info("JSON API hit: {} — {} vehicles".format(url, len(vehicles)))
        return vehicles
    except Exception as e:
        logger.debug("JSON API failed {}: {}".format(url, e))
        return []


def discover_and_scrape_json():
    global JSON_API_URL
    if JSON_API_URL:
        vehicles = try_json_api(JSON_API_URL)
        if vehicles:
            return vehicles
        logger.warning("Configured JSON_API_URL returned no vehicles — trying auto-discovery")
    logger.info("Auto-discovering dealer JSON API ({} candidates)...".format(len(API_CANDIDATES)))
    for path in API_CANDIDATES:
        url = BASE + path
        vehicles = try_json_api(url)
        if vehicles:
            logger.info("SUCCESS: API found at {}".format(url))
            logger.info("TIP: Set TOYOTA_API_URL={} to skip discovery next time".format(url))
            return vehicles
    logger.info("No JSON API found via auto-discovery")
    return []


# -----------------------------------------------------------------------
# Strategy 2: HTML scraping
# -----------------------------------------------------------------------

def scrape_html():
    all_vehicles = []
    logger.info("Falling back to HTML scraping (requires non-blocked IP)...")
    for page_num in range(1, 11):
        url = "{}?page={}".format(TARGET.rstrip('/'), page_num)
        try:
            resp = SESSION.get(url, timeout=30)
            if resp.status_code == 403:
                logger.error("403 Forbidden — this IP is blocked by Cloudflare.")
                break
            resp.raise_for_status()
        except Exception as e:
            logger.error("HTML fetch failed page {}: {}".format(page_num, e))
            break
        soup = BeautifulSoup(resp.content, 'html.parser')
        if page_num == 1:
            with open('debug_page1.html', 'w', encoding='utf-8') as f:
                f.write(soup.prettify())
            logger.info("Saved debug_page1.html")
        page_text = soup.get_text()
        if not re.search(r'\b(19[89]\d|20[0-2]\d)\b', page_text):
            break
        selectors = [
            '[data-vehicle-id]','[data-stock-number]','[data-vin]',
            '.vehicle-card','.inventory-item','.vehicle-listing',
            'article[class*="vehicle"]','div[class*="vehicle"]',
            'li[class*="vehicle"]','.vehicle','article','li[class*="item"]',
        ]
        page_vehicles, seen = [], set()
        for selector in selectors:
            elements = soup.select(selector)
            if not elements: continue
            count = 0
            for idx, el in enumerate(elements):
                eid = id(el)
                if eid in seen: continue
                v = parse_html_element(el, idx)
                if is_valid(v):
                    page_vehicles.append(v)
                    seen.add(eid)
                    count += 1
            if count:
                logger.info("Page {} selector '{}' — {} vehicles".format(page_num, selector, count))
                break
        if not page_vehicles:
            logger.info("No vehicles on page {} — stopping".format(page_num))
            break
        all_vehicles.extend(page_vehicles)
        time.sleep(1.0)
    return all_vehicles


# -----------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------

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
    print("Found {} vehicles\n".format(len(vehicles)))
    brands = {}
    for v in vehicles:
        brands[v.get('makeName','Unknown')] = brands.get(v.get('makeName','Unknown'), 0) + 1
    for b, c in sorted(brands.items()):
        print("  {}: {}".format(b, c))
    sale_count = sum(1 for v in vehicles if v.get('sale_value'))
    print("\nWith sale prices: {}".format(sale_count))
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
    logger.info("RED DEER TOYOTA SCRAPER")
    logger.info("="*80)
    vehicles = discover_and_scrape_json()
    if not vehicles:
        vehicles = scrape_html()
    vehicles = dedup(vehicles)
    logger.info("FINAL: {} unique vehicles".format(len(vehicles)))
    print_results(vehicles)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, '..', '..'))
    csv_path = os.path.join(project_root, 'public', 'data', 'inventory.csv')
    if vehicles:
        save_csv(vehicles, csv_path)
        print("\nCSV created: {}".format(csv_path))
    else:
        print("\nNo vehicles found.")
        if os.path.exists(csv_path):
            os.remove(csv_path)
    return 0 if vehicles else 1


if __name__ == "__main__":
    exit(main())
