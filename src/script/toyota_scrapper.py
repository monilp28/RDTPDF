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

# -----------------------------------------------------------------------
# SET THIS after finding the API URL with Chrome DevTools (see above).
# Leave as empty string to run auto-discovery first.
# Can also be set via environment variable: TOYOTA_API_URL
# -----------------------------------------------------------------------
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
    # ── Japanese Mainstream ──────────────────────────────────────────────
    'Toyota': {
        # Cars
        'Camry','Corolla','Corolla Cross','Yaris','Avalon','Echo','Prius','Prius C',
        'Prius V','Prius Prime','Crown','GR86','86','Supra','Matrix','Venza',
        # SUVs / Crossovers
        'RAV4','RAV4 Prime','Highlander','Highlander Hybrid','4Runner','Sequoia',
        'C-HR','Land Cruiser','FJ Cruiser','bZ4X',
        # Trucks & Vans
        'Tacoma','Tundra','Sienna',
    },
    'Honda': {
        # Cars
        'Civic','Accord','Insight','Jazz','Fit','HR-V','City',
        # SUVs / Crossovers
        'CR-V','Pilot','Passport','Ridgeline',
        # Vans
        'Odyssey',
        # Performance
        'CR-Z','S2000','Element',
    },
    'Mazda': {
        # Cars
        'Mazda2','Mazda3','Mazda5','Mazda6','MX-5','MX-5 Miata',
        # SUVs / Crossovers
        'CX-3','CX-30','CX-5','CX-50','CX-7','CX-8','CX-9','CX-90','MX-30',
        # Trucks
        'B-Series',
    },
    'Nissan': {
        # Cars
        'Altima','Sentra','Maxima','Versa','Versa Note','Micra','Leaf',
        # SUVs / Crossovers
        'Rogue','Rogue Sport','Murano','Pathfinder','Armada','Kicks','Juke','Xterra','Qashqai',
        # Trucks & Vans
        'Frontier','Titan','Titan XD','Quest','NV200','NV Cargo',
        # Performance
        '370Z','350Z','GT-R',
    },
    'Subaru': {
        # Cars
        'Impreza','Legacy','WRX','WRX STI','BRZ',
        # SUVs / Crossovers
        'Outback','Forester','Crosstrek','Ascent','Solterra','Tribeca','XV',
    },
    'Mitsubishi': {
        # Cars
        'Lancer','Lancer Evolution','Galant','Eclipse','Eclipse Cross','i-MiEV',
        # SUVs
        'Outlander','Outlander PHEV','Outlander Sport','RVR','ASX','Eclipse Cross',
        # Trucks
        'Raider',
    },
    'Suzuki': {
        'Swift','SX4','Aerio','Forenza','Reno','Grand Vitara','Vitara','XL-7','Kizashi',
    },
    'Isuzu': {
        'Rodeo','Trooper','Ascender','i-Series',
    },

    # ── Korean ───────────────────────────────────────────────────────────
    'Hyundai': {
        # Cars
        'Accent','Elantra','Elantra N','Sonata','Azera','Ioniq','Ioniq 5','Ioniq 6',
        'Veloster','Veloster N','Genesis Coupe',
        # SUVs / Crossovers
        'Tucson','Santa Fe','Santa Cruz','Palisade','Venue','Kona','Kona Electric',
        'Santa Fe XL','ix35',
    },
    'Kia': {
        # Cars
        'Rio','Forte','Forte5','Optima','K5','Stinger','EV6',
        # SUVs / Crossovers
        'Soul','Soul EV','Sportage','Sorento','Telluride','Seltos','Niro','Niro EV',
        'Niro PHEV','Carnival','Sedona','Rondo',
    },
    'Genesis': {
        'G70','G80','G90','GV70','GV80','GV60',
    },

    # ── North American Domestic ──────────────────────────────────────────
    'Ford': {
        # Cars & Crossovers
        'Fusion','Focus','Fiesta','Taurus','Mustang','Mustang Mach-E','C-MAX',
        # SUVs
        'Escape','Edge','Explorer','Expedition','Bronco','Bronco Sport','EcoSport','Flex',
        # Trucks & Vans
        'F-150','F-150 Lightning','F-250','F-350','F-450','Ranger','Maverick',
        'Transit','Transit Connect','E-Series','E-Transit',
    },
    'Chevrolet': {
        # Cars
        'Malibu','Impala','Cruze','Sonic','Spark','Cobalt','Aveo','Trax',
        'Camaro','Corvette','Volt','Bolt EV','Bolt EUV',
        # SUVs
        'Equinox','Traverse','Tahoe','Suburban','Blazer','Trailblazer','HHR',
        # Trucks & Vans
        'Silverado','Silverado 1500','Silverado 2500','Silverado 2500HD',
        'Silverado 3500HD','Colorado','Avalanche','Express',
    },
    'GMC': {
        # Cars
        'Sierra','Sierra 1500','Sierra 2500','Sierra 2500HD','Sierra 3500HD',
        'Canyon','Sonoma',
        # SUVs
        'Acadia','Terrain','Yukon','Yukon XL','Envoy','Envision','Envoy XL',
        # EV
        'Hummer EV',
    },
    'Dodge': {
        # Cars
        'Charger','Challenger','Dart','Avenger','Neon','Stratus','Viper',
        # SUVs / Vans
        'Durango','Journey','Grand Caravan','Caravan','Hornet',
    },
    'Ram': {
        '1500','1500 Classic','2500','3500','4500','5500',
        'ProMaster','ProMaster City',
    },
    'Jeep': {
        'Wrangler','Wrangler Unlimited','Grand Cherokee','Grand Cherokee L',
        'Cherokee','Compass','Renegade','Gladiator','Patriot','Commander',
        'Liberty','Grand Wagoneer','Wagoneer','Avenger',
    },
    'Chrysler': {
        '200','300','300C','Pacifica','Pacifica Hybrid','Voyager','PT Cruiser',
        'Sebring','Town & Country','Aspen',
    },
    'Lincoln': {
        'Navigator','Navigator L','Aviator','Corsair','Nautilus','MKZ','MKC',
        'MKS','MKT','MKX','Blackwood','Town Car',
    },
    'Cadillac': {
        # Cars
        'CT4','CT5','CT6','ATS','CTS','XTS','STS','DTS','DeVille','Eldorado',
        # SUVs
        'XT4','XT5','XT6','Escalade','Escalade ESV','SRX','Lyriq',
    },
    'Buick': {
        'Encore','Encore GX','Envision','Envista','Enclave','LaCrosse','Regal',
        'Verano','Cascada','Lucerne','Rendezvous','Rainier','Terraza',
    },
    'Pontiac': {
        'G3','G5','G6','G8','Solstice','Torrent','Vibe','Montana','Aztek',
        'Grand Prix','Grand Am','Bonneville','Firebird',
    },
    'Saturn': {
        'Aura','Ion','Vue','Outlook','Sky',
    },
    'Hummer': {
        'H1','H2','H3','H3T',
    },
    'Tesla': {
        'Model S','Model 3','Model X','Model Y','Cybertruck','Roadster',
    },

    # ── German ───────────────────────────────────────────────────────────
    'Volkswagen': {
        # Cars
        'Jetta','Jetta GLI','Passat','Golf','Golf GTI','Golf R','Golf Sportwagen',
        'Golf Alltrack','Beetle','New Beetle','Eos','CC','Arteon','ID.4','ID.3',
        # SUVs
        'Tiguan','Atlas','Atlas Cross Sport','Touareg','Taos',
    },
    'Audi': {
        # Cars
        'A3','A3 Sportback','A3 Sedan','A4','A4 Allroad','A5','A6','A7','A8',
        'TT','TTS','TT RS','RS3','RS5','RS6','RS7','S3','S4','S5','S6','S7','S8',
        'e-tron','e-tron GT','Q4 e-tron',
        # SUVs
        'Q3','Q4','Q5','Q5 Sportback','Q7','Q8','SQ5','SQ7','SQ8','RS Q8',
        'Allroad',
    },
    'BMW': {
        # Cars
        '1 Series','2 Series','3 Series','4 Series','5 Series','6 Series',
        '7 Series','8 Series','M2','M3','M4','M5','M6','M8','Z3','Z4','Z8',
        'i3','i4','i7','i8','iX',
        # SUVs
        'X1','X2','X3','X4','X5','X6','X7','iX3','XM',
    },
    'Mercedes-Benz': {
        # Cars
        'A-Class','B-Class','C-Class','CLA','CLS','E-Class','S-Class','SL','SLC','SLK',
        'AMG GT','C 300','C 43','C 63','E 300','E 350','E 400','E 450','E 550',
        'S 450','S 500','S 550','S 580','S 650','S 63','S 65',
        # SUVs
        'GLA','GLB','GLC','GLC Coupe','GLE','GLE Coupe','GLS','G-Class','G 550',
        'AMG GLE 63','EQC','EQE','EQS',
        # Vans
        'Metris','Sprinter',
    },
    'Porsche': {
        '911','Boxster','Cayman','718 Boxster','718 Cayman',
        'Cayenne','Macan','Panamera','Taycan',
    },
    'Smart': {
        'Fortwo','Forfour',
    },

    # ── British ──────────────────────────────────────────────────────────
    'Land Rover': {
        'Range Rover','Range Rover Sport','Range Rover Evoque','Range Rover Velar',
        'Discovery','Discovery Sport','LR2','LR4','Defender','Freelander',
    },
    'Jaguar': {
        'XE','XF','XJ','F-Type','E-Pace','F-Pace','I-Pace','XK','S-Type','X-Type',
    },
    'MINI': {
        'Cooper','Cooper S','Clubman','Convertible','Countryman','Paceman',
        'Coupe','Roadster','John Cooper Works',
    },

    # ── Italian ──────────────────────────────────────────────────────────
    'Fiat': {
        '500','500X','500L','500e','124 Spider','Bravo','Punto',
    },
    'Alfa Romeo': {
        'Giulia','Stelvio','4C','Spider','GTV','Giulietta','Tonale',
    },
    'Ferrari': {
        '430','458','488','F8','SF90','812','Roma','Portofino','California',
    },
    'Lamborghini': {
        'Gallardo','Huracan','Aventador','Urus',
    },
    'Maserati': {
        'Ghibli','Quattroporte','GranTurismo','Levante','Grecale',
    },

    # ── Swedish ──────────────────────────────────────────────────────────
    'Volvo': {
        # Cars
        'S40','S60','S80','S90','V40','V60','V70','V90','C30','C70',
        # SUVs
        'XC40','XC60','XC70','XC90',
        # Electric
        'C40',
    },

    # ── French ───────────────────────────────────────────────────────────
    'Peugeot': {
        '206','207','208','3008','5008','RCZ',
    },
    'Renault': {
        'Megane','Clio','Scenic','Kadjar','Captur','Koleos',
    },

    # ── Luxury / Niche ───────────────────────────────────────────────────
    'Acura': {
        # Cars
        'ILX','TLX','TL','TSX','RL','RLX','CSX','RSX','NSX','Integra',
        # SUVs
        'RDX','MDX','CDX','ZDX',
    },
    'Lexus': {
        # Cars
        'IS','IS F','RC','RC F','ES','GS','GS F','LS','LC','LFA','UX',
        # SUVs
        'NX','NX 300h','RX','RX 350','RX 450h','GX','LX','UX','RZ',
    },
    'Infiniti': {
        # Cars
        'Q30','Q40','Q45','Q50','Q60','Q70','QX30',
        # SUVs
        'QX50','QX55','QX60','QX70','QX80','EX','FX','JX','M',
    },
    'Lincoln': {
        'Navigator','Navigator L','Aviator','Corsair','Nautilus','MKZ','MKC',
        'MKS','MKT','MKX','Blackwood','Town Car',
    },

    # ── Other / Specialty ───────────────────────────────────────────────
    'Scion': {
        'tC','xB','xD','xA','iA','iM','iQ','FR-S',
    },
    'Pontiac': {
        'G3','G5','G6','G8','Solstice','Torrent','Vibe','Montana','Aztek',
        'Grand Prix','Grand Am','Bonneville',
    },
    'Mercury': {
        'Grand Marquis','Mariner','Milan','Montego','Monterey','Mountaineer','Sable',
    },
    'Oldsmobile': {
        'Alero','Aurora','Bravada','Intrigue','Silhouette',
    },
    'Saab': {
        '9-2X','9-3','9-5','9-7X',
    },
    'Daewoo': {
        'Leganza','Lanos','Nubira',
    },
    'Geo': {
        'Metro','Prizm','Tracker',
    },
    'Rivian': {
        'R1T','R1S',
    },
    'Lucid': {
        'Air',
    },
    'Polestar': {
        '1','2','3','4',
    },
    'Genesis': {
        'G70','G80','G90','GV70','GV80','GV60',
    },
    'Fisker': {
        'Ocean',
    },
}

TRIM_PATTERNS = {
    # ── Toyota / Lexus ───────────────────────────────────────────────────
    'Capstone':         r'\bCapstone\b',
    'TRD Pro':          r'\bTRD\s+Pro\b',
    'TRD Off-Road':     r'\bTRD\s+Off-?Road\b',
    'TRD Sport':        r'\bTRD\s+Sport\b',
    'TRD':              r'\bTRD\b',
    'SR5':              r'\bSR5\b',
    'SR':               r'\bSR\b(?!\d)',
    'XLE':              r'\bXLE\b',
    'XSE':              r'\bXSE\b',
    'XLE Premium':      r'\bXLE\s+Premium\b',
    'Nightshade':       r'\bNightshade\b',
    'Adventure':        r'\bAdventure\b',
    'Trail':            r'\bTrail\b(?!\w)',
    'CrewMax':          r'\bCrewMax\b',
    'Double Cab':       r'\bDouble\s+Cab\b',
    'Access Cab':       r'\bAccess\s+Cab\b',
    'Prime':            r'\bPrime\b',
    'Hybrid':           r'\bHybrid\b',
    'PHEV':             r'\bPHEV\b',
    # Lexus
    'F Sport':          r'\bF\s+Sport\b',
    'F':                r'\bF\b(?!\s+Sport)',
    'Ultra Luxury':     r'\bUltra\s+Luxury\b',
    'Prado':            r'\bPrado\b',

    # ── Ford / Lincoln ───────────────────────────────────────────────────
    'Raptor':           r'\bRaptor\b',
    'Raptor R':         r'\bRaptor\s+R\b',
    'King Ranch':       r'\bKing\s+Ranch\b',
    'Platinum':         r'\bPlatinum\b',
    'Lariat':           r'\bLariat\b',
    'XLT':              r'\bXLT\b',
    'XL':               r'\bXL\b(?!\w)',
    'STX':              r'\bSTX\b',
    'FX2':              r'\bFX2\b',
    'FX4':              r'\bFX4\b',
    'Tremor':           r'\bTremor\b',
    'Wildtrak':         r'\bWildtrak\b',
    'Badlands':         r'\bBadlands\b',
    'Black Diamond':    r'\bBlack\s+Diamond\b',
    'Big Bend':         r'\bBig\s+Bend\b',
    'Outer Banks':      r'\bOuter\s+Banks\b',
    'First Edition':    r'\bFirst\s+Edition\b',
    'ST-Line':          r'\bST-?Line\b',
    'ST':               r'\bST\b(?!\w)',
    'Titanium':         r'\bTitanium\b',
    'Titanium Hybrid':  r'\bTitanium\s+Hybrid\b',
    'Ambiente':         r'\bAmbiente\b',
    'Trend':            r'\bTrend\b',
    # Lincoln
    'Reserve':          r'\bReserve\b',
    'Black Label':      r'\bBlack\s+Label\b',

    # ── GM (Chevy / GMC / Buick / Cadillac) ─────────────────────────────
    'High Country':     r'\bHigh\s+Country\b',
    'LTZ':              r'\bLTZ\b',
    'LT':               r'\bLT\b(?!\w)',
    'LS':               r'\bLS\b(?!\w)',
    'LT Trail Boss':    r'\bLT\s+Trail\s+Boss\b',
    'Trail Boss':       r'\bTrail\s+Boss\b',
    'Z71':              r'\bZ71\b',
    'ZR2':              r'\bZR2\b',
    'ZL1':              r'\bZL1\b',
    'RS':               r'\bRS\b(?!\d)',
    'SS':               r'\bSS\b(?!\w)',
    'AT4X':             r'\bAT4X\b',
    'AT4':              r'\bAT4\b',
    'Denali Ultimate':  r'\bDenali\s+Ultimate\b',
    'Denali':           r'\bDenali\b',
    'SLT':              r'\bSLT\b',
    'SLE':              r'\bSLE\b',
    'SL':               r'\bSL\b(?!\w)',
    'SV':               r'\bSV\b',
    'Pro':              r'\bPro\b(?!\s*-)',
    # Cadillac
    'Luxury':           r'\bLuxury\b',
    'Premium Luxury':   r'\bPremium\s+Luxury\b',
    'Premium':          r'\bPremium\b',
    'Sport':            r'\bSport\b(?!\s+Utility)',
    'V-Series':         r'\bV-Series\b',
    'Blackwing':        r'\bBlackwing\b',
    # Buick
    'Avenir':           r'\bAvenir\b',
    'Essence':          r'\bEssence\b',

    # ── Dodge / Ram / Jeep / Chrysler ────────────────────────────────────
    'Hellcat':          r'\bHellcat\b',
    'Hellcat Redeye':   r'\bHellcat\s+Redeye\b',
    'Jailbreak':        r'\bJailbreak\b',
    'Widebody':         r'\bWidebody\b',
    'Scat Pack':        r'\bScat\s+Pack\b',
    'SRT 392':          r'\bSRT\s+392\b',
    'SRT':              r'\bSRT\b',
    'R/T':              r'\bR/T\b',
    'GT':               r'\bGT\b(?!\w)',
    'SXT':              r'\bSXT\b',
    'SXT Plus':         r'\bSXT\s+Plus\b',
    'SE':               r'\bSE\b(?!\w)',
    'TRX':              r'\bTRX\b',
    'Rebel':            r'\bRebel\b',
    'Laramie Longhorn': r'\bLaramie\s+Longhorn\b',
    'Laramie':          r'\bLaramie\b',
    'Longhorn':         r'\bLonghorn\b',
    'Big Horn':         r'\bBig\s+Horn\b',
    'Night Edition':    r'\bNight\s+Edition\b',
    'Power Wagon':      r'\bPower\s+Wagon\b',
    'Limited Longhorn': r'\bLimited\s+Longhorn\b',
    # Jeep
    'Rubicon 392':      r'\bRubicon\s+392\b',
    'Rubicon':          r'\bRubicon\b',
    'Sahara':           r'\bSahara\b',
    'Willys':           r'\bWillys\b',
    'Trailhawk':        r'\bTrailhawk\b',
    'Overland':         r'\bOverland\b',
    'Summit Reserve':   r'\bSummit\s+Reserve\b',
    'Summit':           r'\bSummit\b',
    'Altitude':         r'\bAltitude\b',
    'Mojave':           r'\bMojave\b',
    'Freedom':          r'\bFreedom\b',
    # Chrysler
    '300S':             r'\b300S\b',
    'Touring L':        r'\bTouring\s+L\b',
    'Touring':          r'\bTouring\b',

    # ── Nissan / Infiniti ────────────────────────────────────────────────
    'Nismo':            r'\bNismo\b',
    'Pro-4X':           r'\bPro-4X\b',
    'Pro-2X':           r'\bPro-2X\b',
    'Midnight Edition': r'\bMidnight\s+Edition\b',
    'Rock Creek':       r'\bRock\s+Creek\b',

    # ── Hyundai / Kia / Genesis ──────────────────────────────────────────
    'Calligraphy':      r'\bCalligraphy\b',
    'N Line':           r'\bN\s+Line\b',
    'N':                r'\bN\b(?!\s+Line)',
    'Ultimate':         r'\bUltimate\b',
    'Preferred':        r'\bPreferred\b',
    'Essential':        r'\bEssential\b',
    'Luxury':           r'\bLuxury\b',
    'Prestige':         r'\bPrestige\b',

    # ── Subaru ───────────────────────────────────────────────────────────
    'XT':               r'\bXT\b',
    'Wilderness':       r'\bWilderness\b',
    'Onyx Edition':     r'\bOnyx\s+Edition\b',
    'Onyx':             r'\bOnyx\b',
    'Limited XT':       r'\bLimited\s+XT\b',

    # ── Volkswagen / Audi ────────────────────────────────────────────────
    'Execline':         r'\bExecline\b',
    'Highline':         r'\bHighline\b',
    'Comfortline':      r'\bComfortline\b',
    'Trendline':        r'\bTrendline\b',
    'Sportline':        r'\bSportline\b',
    'R-Line':           r'\bR-?Line\b',
    'GTI':              r'\bGTI\b',
    'Autobahn':         r'\bAutobahn\b',
    'Progressiv':       r'\bProgressiv\b',
    'Comf':             r'\bComf\b',
    # Audi
    'Technik':          r'\bTechnik\b',
    'Progressiv':       r'\bProgressiv\b',
    'Komfort':          r'\bKomfort\b',
    'Quattro':          r'\bQuattro\b',

    # ── BMW / Mercedes ───────────────────────────────────────────────────
    'M Sport':          r'\bM\s+Sport\b',
    'xDrive':           r'\bxDrive\b',
    'sDrive':           r'\bsDrive\b',
    'AMG':              r'\bAMG\b',
    '4MATIC':           r'\b4MATIC\b',
    'AMG Line':         r'\bAMG\s+Line\b',

    # ── Honda / Acura ────────────────────────────────────────────────────
    'Type R':           r'\bType\s+R\b',
    'Si':               r'\bSi\b(?!\w)',
    'EX-L':             r'\bEX-L\b',
    'EX':               r'\bEX\b(?!\w)',
    'LX':               r'\bLX\b(?!\w)',
    'Sport Touring':    r'\bSport\s+Touring\b',
    'Elite':            r'\bElite\b',
    'A-Spec':           r'\bA-?Spec\b',
    'Advance':          r'\bAdvance\b',
    'TrailSport':       r'\bTrailSport\b',

    # ── Mazda ────────────────────────────────────────────────────────────
    'Signature':        r'\bSignature\b',
    'Carbon Edition':   r'\bCarbon\s+Edition\b',
    'Turbo':            r'\bTurbo\b',

    # ── Volvo ────────────────────────────────────────────────────────────
    'Inscription':      r'\bInscription\b',
    'Momentum':         r'\bMomentum\b',
    'R-Design':         r'\bR-?Design\b',
    'Polestar':         r'\bPolestar\b',

    # ── Generic / Universal ──────────────────────────────────────────────
    'Capstone':         r'\bCapstone\b',
    'Limited':          r'\bLimited\b',
    'LE':               r'\bLE\b(?!\w)',
    'XLE':              r'\bXLE\b',
    'AWD':              r'\bAWD\b',
    '4WD':              r'\b4WD\b',
    '4x4':              r'\b4x4\b',
    '4x2':              r'\b4x2\b',
    'IVT':              r'\bIVT\b',
    '2 Door':           r'\b2\s*Door\b',
    '4 Door':           r'\b4\s*Door\b',
    'Crew Cab':         r'\bCrew\s+Cab\b',
    'Extended Cab':     r'\bExtended\s+Cab\b',
    'Regular Cab':      r'\bRegular\s+Cab\b',
    'Long Box':         r'\bLong\s+Box\b',
    'Short Box':        r'\bShort\s+Box\b',
}

# Common dealer platform API URL patterns to auto-discover
API_CANDIDATES = [
    # Dealer.com / Cox Automotive
    "/apis/widget/INVENTORY_LISTING_DEFAULT_AUTO_USED:inventory-data-bus1/getInventory",
    "/apis/widget/INVENTORY_LISTING_DEFAULT_AUTO_USED:inventory-data-bus1/getInventory?pageSize=100",
    "/apis/widget/INVENTORY_LISTING_DEFAULT_AUTO_ALL:inventory-data-bus1/getInventory?condition=used",
    # Generic REST patterns
    "/api/inventory/listings?condition=used&pageSize=100",
    "/api/inventory/search?condition=used",
    "/api/vehicles/used",
    "/inventory/api/used",
    "/inventory/used.json",
    "/_api/inventory?type=used",
    "/ajax/inventory?condition=used",
    # DealerSocket
    "/inventory/listing?type=used&format=json",
    "/inventory/search?format=json&type=used",
    # CDK / FortellaMedia
    "/vehicle/search?condition=used&format=json",
    "/api/search/vehicle?condition=used",
    # Autotrader/vAuto integrations
    "/api/srp/vehicles?condition=used",
    "/api/srp/listings?condition=used",
    # Toyota-specific platforms
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
    """Map a JSON object from the dealer API to our standard vehicle dict."""
    v = {'makeName':'','year':'','model':'','sub-model':'','trim':'',
         'mileage':'','value':'','sale_value':'','stock_number':'','engine':''}

    # Try common field names used across dealer platforms
    field_map = {
        'makeName':   ['make','makeName','Make','manufacturer'],
        'year':       ['year','modelYear','Year','yr'],
        'model':      ['model','modelName','Model'],
        'trim':       ['trim','trimName','Trim','trimLevel','subModel'],
        'mileage':    ['mileage','odometer','miles','km','Mileage','Odometer'],
        'value':      ['price','listPrice','retailPrice','msrp','Price','salePrice',
                       'internetPrice','sellingPrice','askingPrice'],
        'sale_value': ['salePrice','internetPrice','specialPrice','discountPrice',
                       'webPrice','ourPrice'],
        'stock_number':['stockNumber','stock','stockNum','StockNumber','vin'],
        'engine':     ['engine','engineDescription','engineSize'],
    }

    for our_key, candidates in field_map.items():
        for c in candidates:
            val = item.get(c) or item.get(c.lower()) or item.get(c.upper())
            if val:
                v[our_key] = str(val).strip()
                break

    # Ensure sale < regular
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
    """Score a vehicle record by how complete it is (higher = better)."""
    fields = ['stock_number', 'mileage', 'engine', 'trim', 'value', 'sale_value']
    return sum(1 for f in fields if v.get(f, '').strip())


def dedup(vehicles):
    """
    Two-pass deduplication:
    Pass 1 — keep one entry per stock number (the most complete).
    Pass 2 — for entries without a stock number, drop them if a stocked entry
              already covers the same year+make+model+price combination.
    """
    # Pass 1: group by stock number, keep most complete per stock
    by_stock = {}   # stock -> best vehicle
    no_stock = []

    for v in vehicles:
        stock = v.get('stock_number', '').strip()
        if stock:
            if stock not in by_stock or completeness(v) > completeness(by_stock[stock]):
                by_stock[stock] = v
        else:
            no_stock.append(v)

    stocked = list(by_stock.values())

    # Build a lookup: (year, make, model, price) -> True for every stocked vehicle
    stocked_ymmp = set()
    for v in stocked:
        stocked_ymmp.add((
            v.get('year',''), v.get('makeName',''),
            v.get('model',''), v.get('value',''),
        ))

    # Pass 2: only keep no-stock entries that don't duplicate a stocked vehicle
    extra = []
    seen_extra = set()
    for v in no_stock:
        ymmp = (v.get('year',''), v.get('makeName',''), v.get('model',''), v.get('value',''))
        if ymmp in stocked_ymmp:
            continue          # a stocked entry already covers this
        if ymmp in seen_extra:
            continue          # duplicate within the no-stock group
        seen_extra.add(ymmp)
        extra.append(v)

    return stocked + extra


# -----------------------------------------------------------------------
# Strategy 1: JSON API
# -----------------------------------------------------------------------

def try_json_api(url):
    """Try fetching a JSON API endpoint. Returns list of vehicles or []."""
    try:
        resp = SESSION.get(url, timeout=15)
        if resp.status_code != 200:
            return []
        ct = resp.headers.get('Content-Type','')
        if 'json' not in ct and not resp.text.strip().startswith(('{','[')):
            return []
        data = resp.json()

        # Drill into common wrapper keys
        if isinstance(data, dict):
            for key in ['vehicles','inventory','listings','results','data',
                        'items','records','vehicles_list','vehicleList']:
                if key in data and isinstance(data[key], list):
                    data = data[key]
                    break
            if isinstance(data, dict):
                # Try one level deeper
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
    """Try the configured URL first, then auto-discover."""
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
# Strategy 2: HTML scraping (works from residential IPs / self-hosted runner)
# -----------------------------------------------------------------------

def scrape_html():
    all_vehicles = []
    page_num = 1

    logger.info("Falling back to HTML scraping (requires non-blocked IP)...")

    for page_num in range(1, 11):
        url = "{}?page={}".format(TARGET.rstrip('/'), page_num)
        try:
            resp = SESSION.get(url, timeout=30)
            if resp.status_code == 403:
                logger.error("403 Forbidden — this IP is blocked by Cloudflare.")
                logger.error("Run this scraper on your own machine or a self-hosted GitHub Actions runner.")
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

    # Strategy 1: JSON API (bypasses Cloudflare — works from any IP)
    vehicles = discover_and_scrape_json()

    # Strategy 2: HTML fallback (requires residential/self-hosted IP)
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
        print("\nNEXT STEPS — pick one:")
        print("  A) Find the JSON API: Open Chrome DevTools → Network → XHR/Fetch")
        print("     while loading https://www.reddeertoyota.com/inventory/used/")
        print("     Set the API URL as TOYOTA_API_URL env var in GitHub secrets.")
        print("")
        print("  B) Self-hosted runner: Run the GitHub Action on your own PC.")
        print("     See .github/workflows/daily-scrape.yml for instructions.")
        if os.path.exists(csv_path):
            os.remove(csv_path)

    return 0 if vehicles else 1


if __name__ == "__main__":
    exit(main())
