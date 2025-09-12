import json
import os
import sys
import traceback
from typing import Any

# Resolve project root robustly (works in Vercel packaged FS)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CANDIDATES = [
    os.path.normpath(os.path.join(BASE_DIR, '..', 'src', 'script')),
    os.path.normpath(os.path.join(BASE_DIR, '..', '..', 'src', 'script')),
    os.path.normpath(os.path.join(os.getcwd(), 'src', 'script')),
]
for p in CANDIDATES:
    if os.path.isdir(p) and p not in sys.path:
        sys.path.append(p)

IMPORT_ERROR = None
UniversalRedDeerToyotaScraper = None
try:
    from toyota_scrapper import UniversalRedDeerToyotaScraper  # type: ignore
except Exception as e:
    IMPORT_ERROR = e


def _json_response(status: int, body: Any):
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json",
            "Cache-Control": "no-store",
        },
        "body": json.dumps(body),
    }


def handler(request, response=None):
    """
    Vercel Python Serverless Function entrypoint.
    Runs the scraper and returns latest vehicles as JSON without committing to GitHub.
    """
    # Basic method guard (allow GET/POST)
    method = getattr(request, 'method', 'GET').upper()
    if method not in ("GET", "POST"):
        return _json_response(405, {"error": "Method Not Allowed"})

    if IMPORT_ERROR or UniversalRedDeerToyotaScraper is None:
        return _json_response(500, {
            "error": "Scraper import failed",
            "details": str(IMPORT_ERROR) if IMPORT_ERROR else "Unknown import error",
            "search_paths": [p for p in CANDIDATES],
            "cwd": os.getcwd(),
            "base": BASE_DIR,
        })

    try:
        scraper = UniversalRedDeerToyotaScraper()
        vehicles = scraper.scrape_inventory()
        # Return normalized data; UI already expects sale_value support
        return _json_response(200, {
            "ok": True,
            "count": len(vehicles or []),
            "vehicles": vehicles or [],
        })
    except Exception as e:
        return _json_response(500, {"error": str(e), "trace": traceback.format_exc()})
