"""
API-CR HTTP Server
Exposes company search and certificate download functionality via HTTP API.
"""

import json
import os
import time

# #region agent log
DEBUG_LOG = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "debug-650286.log")
def _log(loc, msg, data, hid):
    try:
        with open(DEBUG_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps({"sessionId":"650286","location":loc,"message":msg,"data":data,"timestamp":int(time.time()*1000),"hypothesisId":hid}) + "\n")
    except Exception:
        pass
# #endregion
import sys
import tempfile
import base64
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Allow concurrent requests (health checks while /search runs)."""
from urllib.parse import urlparse, parse_qs
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from auto_search_company import run_company_search, search_companies_by_query

# Server configuration
HOST = '0.0.0.0'
PORT = 8086

# Load credentials from environment or data/.env
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
ENV_PATH = os.path.join(DATA_DIR, ".env")

def load_credentials():
    """Load credentials from environment variables or .env file."""
    user_qid = os.getenv('USER_QID')
    user_pass = os.getenv('USER_PASSWORD')
    
    # Try loading from .env file if not in environment
    if (not user_qid or not user_pass) and os.path.exists(ENV_PATH):
        try:
            with open(ENV_PATH, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        if key == 'USER_QID' and not user_qid:
                            user_qid = value
                        elif key == 'USER_PASSWORD' and not user_pass:
                            user_pass = value
        except Exception as e:
            print(f"[WARNING] Could not load .env file: {e}")
    
    return user_qid, user_pass


class APIHandler(BaseHTTPRequestHandler):
    """HTTP request handler for API-CR endpoints."""
    
    def log_message(self, format, *args):
        """Override to provide better logging."""
        print(f"[{self.log_date_time_string()}] {args[0]}")
    
    def send_json_response(self, data, status_code=200):
        """Send a JSON response."""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        try:
            self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
        except BrokenPipeError:
            pass  # Client closed connection (e.g. healthcheck timeout)
    
    def send_pdf_response(self, pdf_data, filename):
        """Send a PDF file response."""
        self.send_response(200)
        self.send_header('Content-Type', 'application/pdf')
        self.send_header('Content-Disposition', f'attachment; filename="{filename}"')
        self.send_header('Content-Length', str(len(pdf_data)))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        try:
            self.wfile.write(pdf_data)
        except BrokenPipeError:
            pass
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests."""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        query_params = parse_qs(parsed_path.query)
        
        # Get single values from query params
        def get_param(name, default=None):
            values = query_params.get(name, [])
            return values[0] if values else default
        
        if path == '/health':
            self.handle_health()
        elif path == '/':
            self.handle_docs()
        elif path == '/search':
            # Support both ?cr= (exact CR) and ?q= (name/CR query with multiple results)
            q = get_param('q')
            if q:
                self.handle_search_query(q)
            else:
                self.handle_search(get_param('cr'))
        elif path == '/download':
            self.handle_download(
                get_param('cr'),
                get_param('type', 'CR'),  # CR, CP, or BOTH
                get_param('format', 'file')  # file or base64
            )
        else:
            self.send_json_response({
                'status': 'error',
                'message': f'Unknown endpoint: {path}',
                'available_endpoints': ['/', '/health', '/search', '/download']
            }, 404)
    
    def handle_health(self):
        """Health check endpoint."""
        user_qid, user_pass = load_credentials()
        has_credentials = bool(user_qid and user_pass)
        
        self.send_json_response({
            'status': 'healthy',
            'service': 'API-CR',
            'version': '1.0.0',
            'credentials_configured': has_credentials
        })
    
    def handle_docs(self):
        """API documentation endpoint."""
        self.send_json_response({
            'service': 'API-CR - Company Search & Certificate Download',
            'version': '1.0.0',
            'endpoints': {
                'GET /health': 'Health check',
                'GET /search?cr={CR_NUMBER}': 'Search company by CR number (single result)',
                'GET /search?q={QUERY}': 'Search by CR number, English name, or Arabic name (multiple results)',
                'GET /download?cr={CR_NUMBER}&type={CR|CP|BOTH}&format={file|base64}': 'Download certificate(s)'
            },
            'examples': {
                'search_cr': '/search?cr=76053',
                'search_name': '/search?q=arafat',
                'search_arabic': '/search?q=عرفات',
                'download_cr': '/download?cr=76053&type=CR',
                'download_cp': '/download?cr=76053&type=CP',
                'download_both': '/download?cr=76053&type=BOTH',
                'download_base64': '/download?cr=76053&type=CR&format=base64'
            }
        })
    
    def handle_search_query(self, query):
        """Handle company search by query (CR number, English name, or Arabic name)."""
        if not query or len(query.strip()) < 2:
            self.send_json_response({
                'status': 'error',
                'message': 'Query must be at least 2 characters'
            }, 400)
            return

        user_qid, user_pass = load_credentials()
        if not user_qid or not user_pass:
            self.send_json_response({
                'status': 'error',
                'message': 'Credentials not configured. Please set USER_QID and USER_PASSWORD in data/.env'
            }, 500)
            return

        try:
            result = search_companies_by_query(query.strip(), user_qid, user_pass)

            if isinstance(result, dict) and 'error' in result:
                self.send_json_response({
                    'status': 'error',
                    'message': result['error']
                }, 500)
                return

            self.send_json_response({
                'status': 'success',
                'companies': result,
                'count': len(result),
                'query': query.strip()
            })

        except Exception as e:
            self.send_json_response({
                'status': 'error',
                'message': str(e)
            }, 500)

    def handle_search(self, cr_no):
        """Handle company search request."""
        # #region agent log
        _log("api_server.py:handle_search:entry", "handle_search called", {"cr_no": cr_no}, "A")
        # #endregion
        if not cr_no:
            self.send_json_response({
                'status': 'error',
                'message': 'Missing required parameter: cr (CR number)'
            }, 400)
            return
        
        user_qid, user_pass = load_credentials()
        # #region agent log
        _log("api_server.py:handle_search:creds", "credentials check", {"has_qid": bool(user_qid), "has_pass": bool(user_pass)}, "A")
        # #endregion
        if not user_qid or not user_pass:
            self.send_json_response({
                'status': 'error',
                'message': 'Credentials not configured. Please set USER_QID and USER_PASSWORD in data/.env'
            }, 500)
            return
        
        try:
            # Capture output from search
            import io
            from contextlib import redirect_stdout
            
            output = io.StringIO()
            with redirect_stdout(output):
                run_company_search(cr_no, user_qid, user_pass, 
                                   download_cr=False, download_cp=False)
            
            captured_output = output.getvalue()
            
            # Parse output for company data
            company_data = self._parse_search_output(captured_output, cr_no)
            # #region agent log
            _log("api_server.py:handle_search:parsed", "after run_company_search", {"output_len": len(captured_output), "output_preview": captured_output[:500] if captured_output else "", "company_data": company_data, "has_english_name": bool(company_data.get("english_name"))}, "B")
            # #endregion
            
            self.send_json_response({
                'status': 'success',
                'data': company_data,
                'raw_output': captured_output
            })
            
        except Exception as e:
            # #region agent log
            _log("api_server.py:handle_search:exception", "exception in handle_search", {"error": str(e), "type": type(e).__name__}, "B")
            # #endregion
            self.send_json_response({
                'status': 'error',
                'message': str(e)
            }, 500)
    
    def handle_download(self, cr_no, cert_type, response_format):
        """Handle certificate download request."""
        if not cr_no:
            self.send_json_response({
                'status': 'error',
                'message': 'Missing required parameter: cr (CR number)'
            }, 400)
            return
        
        cert_type = cert_type.upper()
        if cert_type not in ['CR', 'CP', 'BOTH']:
            self.send_json_response({
                'status': 'error',
                'message': 'Invalid type parameter. Use: CR, CP, or BOTH'
            }, 400)
            return
        
        user_qid, user_pass = load_credentials()
        if not user_qid or not user_pass:
            self.send_json_response({
                'status': 'error',
                'message': 'Credentials not configured. Please set USER_QID and USER_PASSWORD in data/.env'
            }, 500)
            return
        
        try:
            # Create temporary directory for downloads
            with tempfile.TemporaryDirectory() as temp_dir:
                download_cr = cert_type in ['CR', 'BOTH']
                download_cp = cert_type in ['CP', 'BOTH']
                
                # Capture output
                import io
                from contextlib import redirect_stdout
                
                output = io.StringIO()
                with redirect_stdout(output):
                    run_company_search(cr_no, user_qid, user_pass,
                                       download_cr=download_cr,
                                       download_cp=download_cp,
                                       output_dir=temp_dir)
                
                captured_output = output.getvalue()
                
                # Check for downloaded files
                pdf_files = list(Path(temp_dir).glob("*.pdf"))
                
                if not pdf_files:
                    self.send_json_response({
                        'status': 'error',
                        'message': 'No PDF files were downloaded',
                        'details': captured_output
                    }, 500)
                    return
                
                # Handle response based on format
                if response_format == 'base64':
                    files_data = {}
                    for pdf_file in pdf_files:
                        with open(pdf_file, 'rb') as f:
                            pdf_data = f.read()
                            files_data[pdf_file.name] = base64.b64encode(pdf_data).decode('utf-8')
                    
                    self.send_json_response({
                        'status': 'success',
                        'files': files_data,
                        'count': len(files_data)
                    })
                else:
                    # Return single file or first file
                    pdf_file = pdf_files[0]
                    with open(pdf_file, 'rb') as f:
                        pdf_data = f.read()
                    
                    self.send_pdf_response(pdf_data, pdf_file.name)
                    
        except Exception as e:
            self.send_json_response({
                'status': 'error',
                'message': str(e)
            }, 500)
    
    def _parse_search_output(self, output, cr_no):
        """Parse search output to extract company data."""
        data = {
            'cr_number': cr_no,
            'english_name': None,
            'arabic_name': None,
            'cp_number': None,
            'status': None,
            'internal_id': None
        }
        
        lines = output.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('CR Number'):
                data['cr_number'] = line.split(':', 1)[1].strip() if ':' in line else cr_no
            elif line.startswith('English Name'):
                data['english_name'] = line.split(':', 1)[1].strip() if ':' in line else None
            elif line.startswith('Arabic Name'):
                value = line.split(':', 1)[1].strip() if ':' in line else None
                # Remove RTL markers
                if value:
                    value = value.replace('\u202b', '').replace('\u202c', '').strip()
                data['arabic_name'] = value
            elif line.startswith('CP Number'):
                data['cp_number'] = line.split(':', 1)[1].strip() if ':' in line else None
            elif line.startswith('Status'):
                data['status'] = line.split(':', 1)[1].strip() if ':' in line else None
            elif line.startswith('Internal ID'):
                data['internal_id'] = line.split(':', 1)[1].strip() if ':' in line else None
        
        return data


def main():
    """Start the HTTP server."""
    print(f"\n{'='*50}")
    print("API-CR HTTP Server")
    print(f"{'='*50}")
    
    # Check credentials
    user_qid, user_pass = load_credentials()
    if user_qid and user_pass:
        print(f"[OK] Credentials loaded (QID: {user_qid[:4]}...)")
    else:
        print("[WARNING] No credentials found!")
        print(f"  Please create {ENV_PATH} with:")
        print("    USER_QID=your_qid")
        print("    USER_PASSWORD=your_password")
    
    print(f"\n[*] Starting server on http://{HOST}:{PORT}")
    print(f"[*] Endpoints:")
    print(f"    GET /health              - Health check")
    print(f"    GET /search?cr=XXXXX     - Search company by CR number")
    print(f"    GET /search?q=QUERY      - Search by name or CR (multiple results)")
    print(f"    GET /download?cr=XXXXX&type=CR|CP|BOTH - Download certificates")
    print(f"\n{'='*50}\n")
    
    server = ThreadedHTTPServer((HOST, PORT), APIHandler)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[*] Server stopped")
        server.shutdown()


if __name__ == "__main__":
    main()
