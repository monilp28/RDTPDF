import json
import os
import sys
import traceback

# Add path resolution for imports
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CANDIDATES = [
    os.path.normpath(os.path.join(BASE_DIR, '..', 'src', 'script')),
    os.path.normpath(os.path.join(BASE_DIR, '..', '..', 'src', 'script')),
    os.path.normpath(os.path.join(os.getcwd(), 'src', 'script')),
    os.path.normpath(os.path.join(BASE_DIR, '..')),  # Add parent directory
]

for p in CANDIDATES:
    if os.path.isdir(p) and p not in sys.path:
        sys.path.append(p)

# Try to import the scraper
IMPORT_ERROR = None
UniversalRedDeerToyotaScraper = None

try:
    from toyota_scrapper import UniversalRedDeerToyotaScraper
except ImportError as e:
    IMPORT_ERROR = f"Cannot import toyota_scrapper: {e}"
except Exception as e:
    IMPORT_ERROR = f"Import error: {e}"

def handler(request, context=None):
    """
    Vercel Python serverless function handler
    """
    # Set CORS headers for all responses
    headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
        "Cache-Control": "no-store, no-cache, must-revalidate"
    }
    
    # Handle preflight OPTIONS request
    method = getattr(request, 'method', 'GET')
    if method == 'OPTIONS':
        return {
            "statusCode": 200,
            "headers": headers,
            "body": ""
        }
    
    # Only allow GET and POST
    if method not in ('GET', 'POST'):
        return {
            "statusCode": 405,
            "headers": headers,
            "body": json.dumps({"error": "Method not allowed", "allowed": ["GET", "POST"]})
        }
    
    # Check if import was successful
    if IMPORT_ERROR or UniversalRedDeerToyotaScraper is None:
        return {
            "statusCode": 500,
            "headers": headers,
            "body": json.dumps({
                "error": "Scraper import failed",
                "details": str(IMPORT_ERROR) if IMPORT_ERROR else "Unknown import error",
                "debug": {
                    "search_paths": CANDIDATES,
                    "cwd": os.getcwd(),
                    "base_dir": BASE_DIR,
                    "path": sys.path[-3:]  # Show last 3 paths added
                }
            })
        }
    
    try:
        # Run the scraper
        scraper = UniversalRedDeerToyotaScraper()
        vehicles = scraper.scrape_inventory()
        
        # Ensure vehicles is a list
        if vehicles is None:
            vehicles = []
        
        return {
            "statusCode": 200,
            "headers": headers,
            "body": json.dumps({
                "ok": True,
                "success": True,
                "count": len(vehicles),
                "vehicles": vehicles,
                "timestamp": scraper.timestamp if hasattr(scraper, 'timestamp') else None
            })
        }
        
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": headers,
            "body": json.dumps({
                "error": f"Scraper execution failed: {str(e)}",
                "type": type(e).__name__,
                "traceback": traceback.format_exc()
            })
        }

# For local testing
if __name__ == "__main__":
    class MockRequest:
        method = 'GET'
    
    result = handler(MockRequest())
    print(json.dumps(json.loads(result['body']), indent=2))
