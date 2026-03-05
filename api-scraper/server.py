"""
api-scraper HTTP server
Serves Qatar business activity scraping via a single Python HTTP endpoint.
Replaces API-php (scraper.php + Nginx + PHP-FPM) and API-node (server.js).
"""

import asyncio
import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

from scraper import scrape_activity_code

HOST = "0.0.0.0"
PORT = int(os.getenv("PORT", "8080"))


class ScraperHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print(f"[{self.log_date_time_string()}] {args[0]}")

    def send_json(self, data: dict, status: int = 200) -> None:
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)

        def param(name: str, default: str = "") -> str:
            vals = params.get(name, [])
            return vals[0] if vals else default

        path = parsed.path

        if path == "/health":
            self.send_json(
                {"status": "healthy", "service": "api-scraper", "version": "1.0.0"}
            )

        elif path == "/scrape":
            code = param("code") or param("activityCode") or "013001"
            print(f"[SCRAPE] code={code}")
            try:
                result = asyncio.run(scrape_activity_code(code))
            except Exception as exc:
                result = {"status": "error", "data": None, "error": str(exc)}
            self.send_json(result)

        elif path == "/":
            self.send_json(
                {
                    "service": "api-scraper",
                    "version": "1.0.0",
                    "endpoints": {
                        "GET /health": "Health check",
                        "GET /scrape?code=013001": "Scrape Qatar business activity data",
                    },
                }
            )

        else:
            self.send_json(
                {
                    "status": "error",
                    "message": f"Unknown endpoint: {path}",
                    "available": ["/", "/health", "/scrape"],
                },
                status=404,
            )


def main():
    print(f"\n{'='*50}")
    print("api-scraper HTTP Server")
    print(f"{'='*50}")
    print(f"[*] Listening on http://{HOST}:{PORT}")
    print(f"[*] Endpoints: /health  /scrape?code={{code}}")
    print(f"{'='*50}\n")
    server = HTTPServer((HOST, PORT), ScraperHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[*] Server stopped")
        server.shutdown()


if __name__ == "__main__":
    main()
