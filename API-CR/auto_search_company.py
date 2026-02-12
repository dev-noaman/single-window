import argparse
import time
import json
import os
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

import sys

# Directory and File paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "data")

# Create data directory if it doesn't exist
os.makedirs(DATA_DIR, exist_ok=True)

# Load environment variables from data/.env file
ENV_PATH = os.path.join(DATA_DIR, ".env")
if os.path.exists(ENV_PATH):
    load_dotenv(ENV_PATH)
else:
    # Fallback to current directory for safety during transition
    load_dotenv()

# Windows console encoding fix
sys.stdout.reconfigure(encoding='utf-8')

# Cache file paths inside data/ folder
REQUEST_CACHE_FILE = os.path.join(DATA_DIR, "request_cache.json")
SESSION_CACHE_FILE = os.path.join(DATA_DIR, "session_cache.json")

# Request validity period (6 days in seconds)
REQUEST_VALIDITY_DAYS = 6
REQUEST_VALIDITY_SECONDS = REQUEST_VALIDITY_DAYS * 24 * 60 * 60

# Certificate type lookup IDs
CERT_TYPE_CR = "1360041"  # Commercial Registration certificate
CERT_TYPE_CP = "1360040"  # Commercial Permit certificate


# Helper for clearer output
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def load_request_cache():
    """Load request cache from JSON file."""
    if os.path.exists(REQUEST_CACHE_FILE):
        try:
            with open(REQUEST_CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"[WARNING] Could not load request cache: {e}")
    return {}


def save_request_cache(cache):
    """Save request cache to JSON file."""
    try:
        with open(REQUEST_CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache, f, indent=2, ensure_ascii=False)
    except IOError as e:
        print(f"[WARNING] Could not save request cache: {e}")


def get_cached_request(cr_no, cert_type):
    """
    Get cached request if available and not marked as closed.
    Returns (request_id, cp_no, source_key_id) or (None, None, None) if closed/not found.
    """
    cache = load_request_cache()
    cache_key = f"{cr_no}_{cert_type}"
    
    if cache_key in cache:
        entry = cache[cache_key]
        
        # Check if request was marked as closed/invalid
        if entry.get("is_closed"):
            # Silently skip closed requests
            return None, None, None
        
        started_at = entry.get("started_at", entry.get("created_at", 0))  # fallback for old cache
        current_time = time.time()
        age_seconds = current_time - started_at
        started_human = entry.get("started_at_human", entry.get("created_at_human", "unknown"))
        
        return (
            entry.get("request_id"),
            entry.get("cp_no"),
            entry.get("source_key_id")
        )
    
    return None, None, None


def invalidate_cached_request(cr_no, cert_type, reason="closed"):
    """Mark a cached request as closed/invalid with timestamp."""
    cache = load_request_cache()
    cache_key = f"{cr_no}_{cert_type}"
    
    if cache_key in cache:
        cache[cache_key]["is_closed"] = True
        cache[cache_key]["closed_at"] = time.time()
        cache[cache_key]["closed_at_human"] = time.strftime("%Y-%m-%d %H:%M:%S")
        cache[cache_key]["close_reason"] = reason
        save_request_cache(cache)


def cache_request(cr_no, cert_type, request_id, cp_no, source_key_id):
    """Save request to cache with start timestamp."""
    cache = load_request_cache()
    cache_key = f"{cr_no}_{cert_type}"
    
    cache[cache_key] = {
        "request_id": request_id,
        "cr_no": cr_no,
        "cp_no": cp_no,
        "cert_type": cert_type,
        "source_key_id": source_key_id,
        "started_at": time.time(),
        "started_at_human": time.strftime("%Y-%m-%d %H:%M:%S"),
        "is_closed": False,
        "closed_at": None,
        "closed_at_human": None
    }
    
    save_request_cache(cache)


def load_session_cache():
    """Load session cache from JSON file."""
    if os.path.exists(SESSION_CACHE_FILE):
        try:
            with open(SESSION_CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"[WARNING] Could not load session cache: {e}")
    return {}


def save_session_cache(cookies, dp_token, access_id, ltpa_token, username, establishments=None):
    """Save session to cache."""
    session = {
        "cookies": cookies,
        "dp_token": dp_token,
        "access_id": access_id,
        "ltpa_token": ltpa_token,
        "username": username,
        "establishments": establishments or {},
        "saved_at": time.time(),
        "saved_at_human": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    try:
        with open(SESSION_CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(session, f, indent=2, ensure_ascii=False)
    except IOError as e:
        print(f"[WARNING] Could not save session cache: {e}")


def get_valid_session():
    """
    Get cached session if still valid (less than 1 hour old).
    Returns session dict or None if expired/not found.
    """
    session = load_session_cache()
    if session:
        saved_at = session.get("saved_at", 0)
        age_seconds = time.time() - saved_at
        # Session valid for 1 hour (tokens may expire)
        if age_seconds < 3600:
            return session
        else:
            print(f"[SESSION] Cached session expired, will re-login")
    return None


def refresh_session_context(context, page, dp_token, access_id, username, cr_no):
    """
    Refresh server-side session context for a specific CR number.
    The government API uses session state for CR certificates.
    Simulates the portal flow: return to search page → search → enter company.
    """
    api_url = "https://api.sw.gov.qa/API/Private"

    # Step 1: Navigate page back to dashboard (return to previous page)
    try:
        page.goto("https://investor.sw.gov.qa/wps/myportal/investors/dashboard",
                   wait_until="networkidle", timeout=15000)
        time.sleep(1)
    except Exception as e:
        print(f"[WARNING] Dashboard navigation failed: {e}")

    # Step 2: Re-search for the company (search) - sets server context
    try:
        search_headers = {
            "Authorization": f"Bearer {dp_token}",
            "uri": "api/sw-certificates/search-companies",
            "crNo": str(cr_no),
            "profileId": username,
            "page": "0",
            "size": "1",
            "lang": "en",
            "QID": username,
            "accessId": access_id,
            "requestSource": "Angular",
            "Accept": "application/json, text/plain, */*",
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Referer": "https://investor.sw.gov.qa/wps/myportal/investors/dashboard",
            "Origin": "https://investor.sw.gov.qa"
        }
        search_resp = context.request.get(api_url, headers=search_headers)

        # Step 3: Try to "enter" the company by fetching its details
        if search_resp.ok:
            search_data = search_resp.json()
            # Extract company ID to simulate entering it
            companies = []
            if isinstance(search_data, list):
                companies = search_data
            elif isinstance(search_data, dict):
                companies = search_data.get('data', search_data.get('items', search_data.get('content', [])))
                if not companies and 'crNumber' in search_data:
                    companies = [search_data]

            if companies and isinstance(companies[0], dict):
                company = companies[0]
                company_id = (company.get('sourceKeyId') or company.get('id') or
                             company.get('crId') or company.get('establishmentId') or
                             company.get('keyId'))
                if company_id:
                    # Call establishment details to "enter" the company
                    detail_headers = {
                        "Authorization": f"Bearer {dp_token}",
                        "uri": "api/sw-dashboard/establishments",
                        "crNo": str(cr_no),
                        "profileId": username,
                        "lang": "en",
                        "QID": username,
                        "accessId": access_id,
                        "requestSource": "Angular",
                        "Accept": "application/json, text/plain, */*",
                        "Referer": "https://investor.sw.gov.qa/wps/myportal/investors/dashboard",
                        "Origin": "https://investor.sw.gov.qa"
                    }
                    context.request.get(api_url, headers=detail_headers)

        print(f"[+] Session context refreshed for CR {cr_no}")
    except Exception as e:
        print(f"[WARNING] Context refresh search failed: {e}")


def save_cert_request(context, dp_token, access_id, username, cr_no, cp_no, cert_type, source_key_id=None):
    """
    Step 1: Save certificate request and get requestId
    cert_type: CERT_TYPE_CR for CR certificate, CERT_TYPE_CP for CP certificate
    source_key_id: Internal database ID from search results (format: "1@{id}" for CR, "2@{id}" for CP)
    """
    api_url = "https://api.sw.gov.qa/API/Private"

    # Build sourceKeyId - API accepts "1-ID" format (with dash)
    if source_key_id:
        source_key = str(source_key_id)
    else:
        source_key = f"1-{cr_no}"
        print(f"[WARNING] No sourceKeyId found, using CR number: {source_key}")

    payload = {
        "appRequests": {
            "sourceKeyId": source_key,
            "crNo": str(cr_no),
            "cpNo": str(cp_no),
            "estNameEn": "",
            "estNameAr": "",
            "counter": False,
            "userId": username,
            "requestType": {
                "lookupId": cert_type
            },
            "requestId": None
        },
        "applicantInfo": {
            "identityNo": username,
            "identityExpiryDate": "2027-07-24",
            "mobile": "",
            "email": "",
            "identityType": "1180001"
        },
        "isForOtherPerson": False,
        "loggedInUser": username
    }

    headers = {
        "Authorization": f"Bearer {dp_token}",
        "uri": "api/sw-certificates/save-cert-request",
        "crNo": str(cr_no),
        "cpNo": str(cp_no),
        "profileId": username,
        "lang": "en",
        "QID": username,
        "accessId": access_id,
        "requestSource": "Angular",
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
        "Referer": "https://investor.sw.gov.qa/wps/myportal/investors/dashboard",
        "Origin": "https://investor.sw.gov.qa"
    }
    
    response = context.request.post(api_url, headers=headers, data=payload)
    
    if response.ok:
        data = response.json()
        if data.get("data") and data["data"].get("requestId"):
            return data["data"]["requestId"]
        else:
            print(f"ERROR: No requestId in response: {data}")
            return None
    else:
        print(f"ERROR: save-cert-request failed: {response.status} {response.status_text}")
        try:
            error_text = response.text()
        except:
            pass
        return None


def download_cert_pdf(context, dp_token, access_id, username, request_id, output_filename, ltpa_token=None):
    """
    Step 2: Download PDF using requestId
    """
    api_url = "https://api.sw.gov.qa/API/Private"
    
    # Build cookie string from context
    cookies = context.cookies()
    cookie_str = "; ".join([f"{c['name']}={c['value']}" for c in cookies])
    
    headers = {
        "Authorization": f"Bearer {dp_token}",
        "uri": "api/sw-certificates/get-cert-contents",
        "requestId": str(request_id),
        "profileId": username,
        "lang": "en",
        "QID": username,
        "accessId": access_id,
        "requestSource": "Angular",
        "Accept": "application/pdf, application/octet-stream, */*",
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
        "Expires": "Sat, 01 Jan 2000 00:00:00 GMT",
        "Referer": "https://investor.sw.gov.qa/wps/myportal/investors/dashboard",
        "Origin": "https://investor.sw.gov.qa",
        "dpToken": dp_token,
        "Cookie": cookie_str
    }
    
    # Add LtpaToken2 if available
    if ltpa_token:
        headers["LtpaToken2"] = ltpa_token
    
    # Use GET with requestId in header (timeout 90s for slow CP certificates)
    response = context.request.get(api_url, headers=headers, timeout=90000)
    
    if response.ok:
        pdf_data = response.body()
        
        # Validate PDF size (should be at least 1KB for a valid certificate)
        if len(pdf_data) < 1000:
            print(f"WARNING: PDF size is suspiciously small ({len(pdf_data)} bytes)")
            print(f"The certificate might not be ready yet or there was an error")
            return False
        
        with open(output_filename, 'wb') as f:
            f.write(pdf_data)
        print(f"✓ PDF saved: {output_filename} ({len(pdf_data):,} bytes)")
        return True
    else:
        print(f"ERROR: get-cert-contents failed: {response.status} {response.status_text}")
        try:
            resp_text = response.text()
            print(f"Response: {resp_text[:500] if len(resp_text) > 500 else resp_text}")
        except:
            pass
        return False


def download_certificate(context, dp_token, access_id, username, cr_no, cp_no, cert_type, output_dir=".", ltpa_token=None, source_key_id=None, page=None):
    """
    Full workflow: check cache -> (save request if needed) -> download PDF
    cert_type: "CR" or "CP"
    source_key_id: Internal database ID from search results
    page: Playwright page object (needed for CR certs to refresh session context)

    Uses cached requestId if available and not closed.
    If download fails with cached request, marks it as closed and creates new one.
    For CR certificates, always creates a new request (no cache) due to server-side session state.
    """
    type_lookup = CERT_TYPE_CR if cert_type == "CR" else CERT_TYPE_CP
    type_name = "Commercial Registration" if cert_type == "CR" else "Commercial Permit"

    print(f"\n[*] Downloading {type_name} certificate for CR: {cr_no}...")

    # For CR certificates: refresh server session context and skip cache
    # The government API uses session state for CR certs, so we must
    # simulate: return to search → search for company → enter company
    if cert_type == "CR":
        if page:
            print(f"[*] Refreshing session context for CR {cr_no}...")
            refresh_session_context(context, page, dp_token, access_id, username, cr_no)

        # Invalidate any old cached CR request for this CR number
        invalidate_cached_request(cr_no, cert_type, reason="cr_always_fresh")
        cached_request_id = None
        used_cache = False
    else:
        # For CP certificates, cache works fine
        cached_request_id, cached_cp_no, cached_source_key_id = get_cached_request(cr_no, cert_type)
        used_cache = False

    if cached_request_id:
        # Try cached request first (CP only)
        request_id = cached_request_id
        used_cache = True
        print(f"[+] Trying cached requestId: {request_id}")
    else:
        # No valid cache - create new request
        print(f"[*] Creating new certificate request...")
        request_id = save_cert_request(context, dp_token, access_id, username, cr_no, cp_no, type_lookup, source_key_id)
        
        if not request_id:
            print(f"[-] Failed to get requestId for {cert_type} certificate")
            return False
        
        print(f"[+] Received new requestId: {request_id}")
        
        # Cache the new request for future use
        cache_request(cr_no, cert_type, request_id, cp_no, source_key_id)
        
        #  CP certificates take longer to process than CR
        wait_time = 8 if cert_type == "CP" else 5
        print(f"[*] Waiting for certificate generation... ({wait_time}s)")
        time.sleep(wait_time)
    
    # Try to download PDF
    print(f"[*] Downloading PDF...")
    filename = os.path.join(output_dir, f"{cert_type}_{cr_no}.pdf")
    success = download_cert_pdf(context, dp_token, access_id, username, request_id, filename, ltpa_token)
    
    # If download failed with cached request, the request might be closed
    if not success and used_cache:
        print(f"[!] Download failed with cached request - request may be closed")
        invalidate_cached_request(cr_no, cert_type, reason="download_failed")
        
        # Retry with new request
        print(f"[*] Creating new certificate request (retry)...")
        request_id = save_cert_request(context, dp_token, access_id, username, cr_no, cp_no, type_lookup, source_key_id)
        
        if not request_id:
            print(f"[-] Failed to get new requestId for {cert_type} certificate")
            return False
        
        print(f"[+] Received new requestId: {request_id}")
        cache_request(cr_no, cert_type, request_id, cp_no, source_key_id)
        
        print(f"[*] Waiting for certificate generation...")
        time.sleep(3)
        
        print(f"[*] Retrying download...")
        success = download_cert_pdf(context, dp_token, access_id, username, request_id, filename, ltpa_token)
    
    if success:
        print(f"[+] {type_name} certificate downloaded successfully!")
    else:
        print(f"[-] Failed to download {type_name} certificate")
    
    return success


def search_companies_by_query(query, username, password):
    """
    Search companies by CR number, English name, or Arabic name.
    Returns a list of company dicts with: cr_number, english_name, arabic_name, cp_number, status, internal_id.
    Uses Playwright to login and call the government API.
    """
    results = []
    seen_crs = set()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(ignore_https_errors=True)
        page = context.new_page()

        try:
            # --- Login flow (same as run_company_search) ---
            page.goto("https://investor.sw.gov.qa/wps/myportal/investors/login/", wait_until="networkidle")
            page.wait_for_selector("#userName", timeout=30000)
            page.fill("#userName", username)
            page.fill("#userPassword", password)

            try:
                submit_btn = page.locator("button[type='submit'], input[type='submit'], .login-btn, #loginBtn")
                if submit_btn.count() > 0:
                    submit_btn.first.click()
                else:
                    page.press("#userPassword", "Enter")
            except:
                page.press("#userPassword", "Enter")

            logged_in = False
            for attempt in range(30):
                time.sleep(1)
                current_url = page.url
                cookies = context.cookies()
                dp_token_found = any(c['name'] == 'dpToken' for c in cookies)
                if "dashboard" in current_url.lower() or dp_token_found:
                    logged_in = True
                    break

            if not logged_in:
                return {"error": "Login timed out. Please check credentials."}

            cookies = context.cookies()
            dp_token = next((c['value'] for c in cookies if c['name'] == 'dpToken'), None)
            access_id = next((c['value'] for c in cookies if c['name'] == 'accessId'), None)

            if not dp_token:
                return {"error": "Login succeeded but dpToken not found."}
            if not access_id:
                access_id = "10850851"

            api_url = "https://api.sw.gov.qa/API/Private"

            # --- Fetch establishments (user's companies) ---
            est_headers = {
                "Authorization": f"Bearer {dp_token}",
                "uri": "api/sw-dashboard/establishments",
                "profileId": username,
                "lang": "en",
                "QID": username,
                "accessId": access_id,
                "requestSource": "Angular",
                "Accept": "application/json, text/plain, */*",
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Referer": "https://investor.sw.gov.qa/wps/myportal/investors/dashboard",
                "Origin": "https://investor.sw.gov.qa"
            }

            est_response = context.request.get(api_url, headers=est_headers)

            if est_response.ok:
                est_data = est_response.json()
                establishments = []
                if isinstance(est_data, list):
                    establishments = est_data
                elif isinstance(est_data, dict):
                    establishments = est_data.get('data', est_data.get('content', est_data.get('items', [])))

                query_lower = query.lower().strip()

                for est in establishments:
                    if not isinstance(est, dict):
                        continue
                    cr = str(est.get('crNumber', est.get('crNo', '')))
                    en_name = str(est.get('establishmentNameEn', '') or '')
                    ar_name = str(est.get('establishmentNameAr', '') or '')
                    cp = str(est.get('cpNumber', '') or '')
                    status = est.get('statusEn', est.get('crStatusEn', ''))
                    internal_id = est.get('id', est.get('establishmentId', est.get('crId', '')))

                    # Match: CR number contains query, or name contains query
                    if (query_lower in cr.lower() or
                        query_lower in en_name.lower() or
                        query_lower in ar_name.lower() or
                        query in ar_name):  # Arabic exact substring match
                        if cr and cr not in seen_crs:
                            seen_crs.add(cr)
                            results.append({
                                'cr_number': cr,
                                'english_name': en_name or None,
                                'arabic_name': ar_name or None,
                                'cp_number': cp or None,
                                'status': status or None,
                                'internal_id': str(internal_id) if internal_id else None
                            })

            # --- Also try search-companies API (works for CR number lookups, may find non-user companies) ---
            if query.strip().isdigit():
                search_headers = {
                    "Authorization": f"Bearer {dp_token}",
                    "uri": "api/sw-certificates/search-companies",
                    "crNo": str(query.strip()),
                    "profileId": username,
                    "page": "0",
                    "size": "10",
                    "lang": "en",
                    "QID": username,
                    "accessId": access_id,
                    "requestSource": "Angular",
                    "Accept": "application/json, text/plain, */*",
                    "Cache-Control": "no-cache, no-store, must-revalidate",
                    "Pragma": "no-cache",
                    "Referer": "https://investor.sw.gov.qa/wps/myportal/investors/dashboard",
                    "Origin": "https://investor.sw.gov.qa"
                }

                search_resp = context.request.get(api_url, headers=search_headers)
                if search_resp.ok:
                    search_data = search_resp.json()
                    companies = []
                    if isinstance(search_data, list):
                        companies = search_data
                    elif isinstance(search_data, dict):
                        if "data" in search_data and isinstance(search_data["data"], list):
                            companies = search_data["data"]
                        elif "items" in search_data:
                            companies = search_data["items"]
                        elif "content" in search_data:
                            companies = search_data["content"]
                        elif "crNumber" in search_data:
                            companies = [search_data]

                    for company in companies:
                        if not isinstance(company, dict):
                            continue
                        cr = str(company.get('crNumber', ''))
                        if cr and cr not in seen_crs:
                            seen_crs.add(cr)
                            results.append({
                                'cr_number': cr,
                                'english_name': company.get('establishmentNameEn') or None,
                                'arabic_name': company.get('establishmentNameAr') or None,
                                'cp_number': str(company.get('cpNumber', '') or '') or None,
                                'status': company.get('statusEn', company.get('crStatusEn')) or None,
                                'internal_id': str(company.get('sourceKeyId', company.get('id', company.get('crId', ''))) or '') or None
                            })

            return results

        except Exception as e:
            return {"error": str(e)}
        finally:
            browser.close()


def run_company_search(cr_no, username, password, download_cr=False, download_cp=False, output_dir="."):
    """
    Search for company and optionally download CR/CP PDF certificates.
    
    Args:
        cr_no: Commercial Registration number to search
        username: Login username (QID)
        password: Login password
        download_cr: If True, download CR certificate PDF
        download_cp: If True, download CP certificate PDF
        output_dir: Directory to save PDF files
    """
    print(f"Launching browser to search for CR {cr_no}...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Create context with ignore_https_errors to mimic requests(verify=False)
        context = browser.new_context(ignore_https_errors=True)
        page = context.new_page()
        
        try:
            print("Navigating to login page...")
            page.goto("https://investor.sw.gov.qa/wps/myportal/investors/login/", wait_until="networkidle")
            
            print("Waiting for login form to load...")
            page.wait_for_selector("#userName", timeout=30000)
            
            print("Entering credentials...")
            page.fill("#userName", username)
            page.fill("#userPassword", password)
            
            print("Submitting login form...")
            # Try clicking submit button if it exists, otherwise press Enter
            try:
                submit_btn = page.locator("button[type='submit'], input[type='submit'], .login-btn, #loginBtn")
                if submit_btn.count() > 0:
                    submit_btn.first.click()
                else:
                    page.press("#userPassword", "Enter")
            except:
                page.press("#userPassword", "Enter")
            
            print("Waiting for login to complete...")
            
            # Wait for either dashboard URL or dpToken cookie
            logged_in = False
            for attempt in range(30):  # Try for 30 seconds
                time.sleep(1)
                current_url = page.url
                cookies = context.cookies()
                dp_token_found = any(c['name'] == 'dpToken' for c in cookies)
                
                if "dashboard" in current_url.lower() or dp_token_found:
                    logged_in = True
                    print(f"Login successful! (URL: {'dashboard' in current_url.lower()}, Cookie: {dp_token_found})")
                    break
                
                if attempt % 5 == 0:
                    print(f"  Still waiting... ({attempt}s) - URL: {current_url[:60]}...")
            
            if not logged_in:
                print("ERROR: Login timed out. Please check credentials or try again.")
                print(f"Final URL: {page.url}")
                return
            
            # Extract dpToken and accessId
            cookies = context.cookies()
            
            dp_token = next((c['value'] for c in cookies if c['name'] == 'dpToken'), None)
            access_id = next((c['value'] for c in cookies if c['name'] == 'accessId'), None)
            ltpa_token = next((c['value'] for c in cookies if c['name'] == 'LtpaToken2'), None)
            
            if not dp_token:
                print("ERROR: Login successful but dpToken cookie not found.")
                return
            
            if not access_id:
                 print("WARNING: accessId cookie not found. Using fallback or previous value might fail.")
                 # Fallback if needed, or let it be None and see if it fails clearly
                 access_id = "10850851" # Warning: This is likely stale

            if not ltpa_token:
                print("WARNING: LtpaToken2 cookie not found. PDF download may fail.")

            # Token retrieved. Proceeding to API call...

            # Define API details
            api_url = "https://api.sw.gov.qa/API/Private"
            
            # First, get establishments to find internal ID
            # First, get establishments to find internal ID
            est_headers = {
                "Authorization": f"Bearer {dp_token}",
                "uri": "api/sw-dashboard/establishments",
                "profileId": username,
                "lang": "en",
                "QID": username,
                "accessId": access_id,
                "requestSource": "Angular",
                "Accept": "application/json, text/plain, */*",
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Referer": "https://investor.sw.gov.qa/wps/myportal/investors/dashboard",
                "Origin": "https://investor.sw.gov.qa"
            }
            
            est_response = context.request.get(api_url, headers=est_headers)
            establishment_map = {}  # Map CR number to internal ID
            
            if est_response.ok:
                est_data = est_response.json()
                
                # Parse establishments to build CR -> ID mapping
                establishments = []
                if isinstance(est_data, list):
                    establishments = est_data
                elif isinstance(est_data, dict):
                    establishments = est_data.get('data', est_data.get('content', est_data.get('items', [])))
                
                for est in establishments:
                    if isinstance(est, dict):
                        est_cr = str(est.get('crNumber', est.get('crNo', '')))
                        est_id = est.get('id', est.get('establishmentId', est.get('crId', '')))
                        if est_cr and est_id:
                            establishment_map[est_cr] = est_id
            else:
                pass
            
            # Save session cache for future use
            cookies_list = [{"name": c["name"], "value": c["value"], "domain": c.get("domain", "")} for c in cookies]
            save_session_cache(cookies_list, dp_token, access_id, ltpa_token, username, establishment_map)
            
            # Now search for company details
            headers = {
                "Authorization": f"Bearer {dp_token}",
                "uri": "api/sw-certificates/search-companies",
                "crNo": str(cr_no),
                "profileId": username,
                "page": "0",
                "size": "4",
                "lang": "en",
                "QID": username,
                "accessId": access_id,
                "requestSource": "Angular",
                "Accept": "application/json, text/plain, */*",
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Referer": "https://investor.sw.gov.qa/wps/myportal/investors/dashboard",
                "Origin": "https://investor.sw.gov.qa"
            }
            
            # Perform API Fetch using Playwright's APIRequestContext
            # This shares the cookie jar with the browser context
            response = context.request.get(api_url, headers=headers)
            
            cp_number = None  # Will be extracted from company data
            source_key_id = None  # Internal ID from establishments
            
            if response.ok:
                data = response.json()
                
                # Normalize data to a list for iteration
                companies = []
                if isinstance(data, list):
                    companies = data
                elif isinstance(data, dict):
                    # Check keys
                    if "data" in data and isinstance(data["data"], list):
                        companies = data["data"]
                    elif "items" in data:
                         companies = data["items"]
                    elif "content" in data:
                         companies = data["content"]
                    elif "crNumber" in data:
                         companies = [data]
                    else:
                        print(f"WARNING: Could not identify company list. keys: {list(data.keys())}")
                
                if companies:
                    printed_crs = set()
                    for company in companies:
                        if isinstance(company, dict):
                            company_cr = str(company.get('crNumber', ''))
                            
                            # Avoid printing duplicate blocks for the same CR
                            if company_cr in printed_crs:
                                continue
                            printed_crs.add(company_cr)
                            
                            print("\n" + "="*40)
                            print(f"CR Number    : {company_cr}")
                            print(f"English Name : {company.get('establishmentNameEn')}")
                            # Add RTL marker for proper Arabic display
                            arabic_name = company.get('establishmentNameAr')
                            if arabic_name:
                                print(f"Arabic Name  : \u202B{arabic_name}\u202C")
                            else:
                                print(f"Arabic Name  : None")
                            cp_number = company.get('cpNumber')
                            print(f"CP Number    : {cp_number}")
                            status_en = company.get('statusEn') or company.get('crStatusEn')
                            print(f"Status       : {status_en}")
                            
                            # Get internal ID from establishments map
                            source_key_id = establishment_map.get(company_cr)
                            
                            # Also try to find ID in search result itself
                            if not source_key_id:
                                source_key_id = (company.get('id') or 
                                               company.get('crId') or 
                                               company.get('establishmentId') or
                                               company.get('sourceKeyId') or
                                               company.get('keyId'))
                            
                            if source_key_id:
                                print(f"Internal ID  : {source_key_id}")
                            else:
                                print(f"[WARNING] No internal ID found for CR {company_cr}")
                        print("="*40 + "\n")
                else:
                    print(f"No results found for CR {cr_no}")
                    return

            else:
                print(f"API Error: {response.status} {response.status_text}")
                try:
                    print(f"Server Response: {response.text()}")
                except UnicodeEncodeError:
                    print(f"Server Response: (Unicode Error printing response)")
                return
            
            # Download PDFs if requested
            if (download_cr or download_cp) and cp_number:
                # Create output directory if it doesn't exist
                if output_dir and output_dir != ".":
                    os.makedirs(output_dir, exist_ok=True)
                
                if download_cr:
                    download_certificate(context, dp_token, access_id, username,
                                        cr_no, cp_number, "CR", output_dir, ltpa_token, source_key_id, page=page)

                if download_cp:
                    download_certificate(context, dp_token, access_id, username,
                                        cr_no, cp_number, "CP", output_dir, ltpa_token, source_key_id)
            elif (download_cr or download_cp) and not cp_number:
                print("WARNING: Cannot download certificates - CP number not found in search results")
                
        except Exception as e:
            try:
                print(f"An unexpected error occurred: {e}")
            except UnicodeEncodeError:
                print(f"An unexpected error occurred: {repr(e)}")
        finally:
            browser.close()

if __name__ == "__main__":
    # Clear screen for clean start
    clear_screen()
    
    parser = argparse.ArgumentParser(
        description='Auto-login, fetch company details, and download CR/CP certificates.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python auto_search_company.py 76053                    # Search only
  python auto_search_company.py 76053 --cr               # Search + download CR PDF
  python auto_search_company.py 76053 --cp               # Search + download CP PDF  
  python auto_search_company.py 76053 --cr --cp          # Search + download both PDFs
  python auto_search_company.py 76053 --cr --cp -o pdfs  # Download to 'pdfs' folder
        """
    )
    parser.add_argument('cr_no', nargs='?', default="76053", help='The CR Number to search for')
    parser.add_argument('--cr', action='store_true', help='Download CR (Commercial Registration) certificate PDF')
    parser.add_argument('--cp', action='store_true', help='Download CP (Commercial Permit) certificate PDF')
    parser.add_argument('-o', '--output', default=".", help='Output directory for PDF files (default: current directory)')
    
    # Load credentials from environment variables
    USER_QID = os.getenv('USER_QID')
    USER_PASS = os.getenv('USER_PASSWORD')
    
    if not USER_QID or not USER_PASS:
        print("ERROR: Missing credentials. Please create a .env file with USER_QID and USER_PASSWORD")
        exit(1)
    
    args = parser.parse_args()
    # Handle the naive case where argparse might not catch the positional if purely modifying sys.argv isn't enough
    target_cr = args.cr_no
    
    run_company_search(target_cr, USER_QID, USER_PASS, 
                       download_cr=args.cr, 
                       download_cp=args.cp,
                       output_dir=args.output)
