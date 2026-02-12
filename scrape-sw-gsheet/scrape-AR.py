# pyright: reportMissingImports=false
import asyncio
import argparse
import os
import time
from typing import Optional, List, Tuple

import gspread
from oauth2client.service_account import ServiceAccountCredentials
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError, Page

# Import progress writer for real-time monitoring
from progress_writer import write_progress

# ----------------------------
# Configuration
# ----------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DRIVE_DIR = os.path.join(SCRIPT_DIR, "drive")
GOOGLE_CREDENTIALS_FILE = os.path.join(DRIVE_DIR, "google-credentials.json")
SPREADSHEET_NAME = "Filter"
WORKSHEET_NAME = "AR"
BASE_URL = "https://investor.sw.gov.qa/wps/portal/investors/home/!ut/p/z1/04_Sj9CPykssy0xPLMnMz0vMAfIjo8zivfxNXA393Q38LXy9DQzMAj0cg4NcLY0MDMz1w_Wj9KNQlISGGRkEOjuZBjm6Wxj7OxpCFRjgAI4G-sGpefoF2dlpjo6KigAeufkI/dz/d5/L0lHSkovd0RNQUZrQUVnQSEhLzROVkUvYXI!/"

# Details page XPaths (same as Selenium version)
X_ACTIVITY_CODE = "/html/body/div[4]/div/div/section/div[2]/main/section[3]/div/div/div/div/div[1]/div[2]"
X_ACTIVITY_NAME = "/html/body/div[4]/div/div/section/div[2]/main/section[3]/div/div/div/div/div[3]/div[2]"
X_TBODY = "/html/body/div[4]/div/div/section/div[2]/main/section[3]/div/div/div/div/div[8]/div[2]/table/tbody"
X_ELIGIBLE = "/html/body/div[4]/div/div/section/div[2]/main/section[3]/div/div/div/div/div[9]/div[2]/table/tbody/tr[2]/td"
X_NO_APPROVAL = "/html/body/div[4]/div/div/section/div[2]/main/section[3]/div/div/div/div/div[10]/div[2]"

# Search flow selectors
X_SEARCH_ICON = "//*[@id='searchIconId']"
X_BUSINESS_TAB = "//*[@id='nav-business-tab']"
CSS_SEARCH_INPUT = "input#searchInput"
X_FIRST_ACTIVITY = "//*[@id='businessList']/li/a/div"
X_LANG_TOGGLE = "//*[@id='swChangeLangLink']/div"

# Additional Step (Footer Business Activities Search) – user-provided XPaths
X_FOOTER_BUSINESS_ACTIVITIES = "/html/body/footer/section[1]/div/div/div[2]/ul/li[2]/a"
X_FOOTER_SEARCH_INPUT = "/html/body/div[4]/div/div/section/div[2]/main/section[3]/div/div/div[1]/div/div/input"
X_FOOTER_SEARCH_CONTAINER = "/html/body/div[4]/div/div/section/div[2]/main/section[3]/div/div/div[1]/div"
CSS_RESULTS_FIRST_ACTIVITY_LINK = "#pills-activities a.ba-link"


def format_column_b_as_text(worksheet):
    """Format Column B as TEXT to preserve leading zeros"""
    try:
        worksheet.format("B:B", {
            "numberFormat": {
                "type": "TEXT"
            }
        })
        return True
    except Exception as e:
        print(f"Warning: Could not format column B as TEXT: {e}")
        return False


def connect_to_sheets():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    credentials = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_CREDENTIALS_FILE, scope)
    client = gspread.authorize(credentials)
    return client.open(SPREADSHEET_NAME).worksheet(WORKSHEET_NAME)


async def _safe_screenshot(page: Page, filename: str) -> None:
    pass


async def _get_lang(page: Page) -> str:
    try:
        return (await page.evaluate("document.documentElement.lang")) or ""
    except Exception:
        return ""


async def set_language(page: Page, target_lang: str, timeout_s: int = 10) -> bool:
    """
    Toggle website language between Arabic and English.
    target_lang: 'ar' or 'en'
    """
    try:
        current_lang = await _get_lang(page)
        if current_lang == target_lang:
            return True

        btn = page.locator(f"xpath={X_LANG_TOGGLE}")
        await btn.wait_for(state="visible", timeout=10_000)
        try:
            await btn.scroll_into_view_if_needed()
        except Exception:
            # Element may have become detached, try without scroll
            pass
        await btn.click()

        # Wait until language changes
        deadline = time.time() + timeout_s
        while time.time() < deadline:
            if await _get_lang(page) == target_lang:
                try:
                    await page.wait_for_load_state("networkidle", timeout=10_000)
                except Exception:
                    pass
                return True
            await asyncio.sleep(0.25)
        return False
    except Exception:
        return False


async def click_xpath(page: Page, xpath: str, timeout_ms: int = 10_000) -> None:
    el = page.locator(f"xpath={xpath}")
    await el.wait_for(state="visible", timeout=timeout_ms)
    try:
        await el.scroll_into_view_if_needed()
    except Exception:
        # Element may have become detached, try without scroll
        pass
    await el.click()


async def fill_css(page: Page, selector: str, value: str, timeout_ms: int = 10_000) -> None:
    el = page.locator(selector)
    await el.wait_for(state="visible", timeout=timeout_ms)
    await el.fill(value)


async def direct_to_details(page: Page, code: str) -> Page:
    """
    FASTEST APPROACH: Go directly to the details page using the bacode URL parameter.
    Skips footer navigation, search, results scanning entirely.
    Returns the details Page.
    """
    # Construct direct URL to details page
    details_url = f"https://investor.sw.gov.qa/wps/portal/investors/information-center/ba/details?bacode={code}"
    
    await page.goto(details_url, wait_until="domcontentloaded")
    
    try:
        await page.wait_for_load_state("networkidle", timeout=30_000)
    except Exception:
        pass
    
    # Wait for the activity code element to be visible
    await page.locator(f"xpath={X_ACTIVITY_CODE}").wait_for(state="visible", timeout=30_000)
    
    return page


async def additional_step_footer_business_search(page: Page, code: str) -> Page:
    """
    Additional Step: use the footer Business Activities Search page to find and open the activity details.
    Returns the details Page (may be a popup/new tab).
    """
    await page.goto(BASE_URL, wait_until="domcontentloaded")
    try:
        await page.wait_for_load_state("networkidle", timeout=30_000)
    except Exception:
        pass

    # Scroll to footer and click Business activities
    try:
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    except Exception:
        pass
    footer = page.locator(f"xpath={X_FOOTER_BUSINESS_ACTIVITIES}")
    await footer.wait_for(state="visible", timeout=20_000)
    await footer.click()

    try:
        await page.wait_for_load_state("networkidle", timeout=30_000)
    except Exception:
        pass

    # Type code and trigger search
    inp = page.locator(f"xpath={X_FOOTER_SEARCH_INPUT}")
    await inp.wait_for(state="visible", timeout=20_000)
    await inp.fill(code)
    try:
        await inp.press("Enter")
    except Exception:
        pass

    # Prefer real SEARCH button if present; fall back to container click
    try:
        btn = page.locator("xpath=//button[contains(translate(normalize-space(.), 'search', 'SEARCH'), 'SEARCH')]")
        if await btn.count() > 0:
            await btn.first.click()
        else:
            await page.locator(f"xpath={X_FOOTER_SEARCH_CONTAINER}").click()
    except Exception:
        try:
            await page.locator(f"xpath={X_FOOTER_SEARCH_CONTAINER}").click()
        except Exception:
            pass

    try:
        await page.wait_for_load_state("networkidle", timeout=20_000)
    except Exception:
        pass

    # Results render under pills-activities
    results_root = page.locator("css=#pills-activities")
    await results_root.wait_for(state="attached", timeout=20_000)

    link = page.locator(f"css={CSS_RESULTS_FIRST_ACTIVITY_LINK}").first
    await link.wait_for(state="visible", timeout=20_000)

    # Details often open in a new tab (target=_blank)
    popup_page: Page | None = None
    try:
        async with page.expect_popup(timeout=20_000) as popup_info:
            await link.click()
        popup_page = await popup_info.value
    except Exception:
        await link.click()

    details_page = popup_page or page
    try:
        await details_page.wait_for_load_state("networkidle", timeout=30_000)
    except Exception:
        pass
    await details_page.locator(f"xpath={X_ACTIVITY_CODE}").wait_for(state="visible", timeout=30_000)
    return details_page


async def get_text_xpath(page: Page, xpath: str, timeout_ms: int = 10_000) -> str:
    el = page.locator(f"xpath={xpath}")
    await el.wait_for(state="visible", timeout=timeout_ms)
    try:
        await el.scroll_into_view_if_needed()
    except Exception:
        # Element may have become detached, try without scroll
        pass
    txt = await el.text_content()
    return (txt or "").strip()


async def get_table_data(page: Page) -> List[Tuple[str, str, str]]:
    try:
        tbody = page.locator(f"xpath={X_TBODY}")
        await tbody.wait_for(state="visible", timeout=10_000)
        try:
            await tbody.scroll_into_view_if_needed()
        except Exception:
            # Element may have become detached, try without scroll
            pass

        rows = tbody.locator("tr")
        n = await rows.count()
        out: List[Tuple[str, str, str]] = []
        for i in range(1, n + 1):
            td1 = await get_text_xpath(page, f"{X_TBODY}/tr[{i}]/td[1]")
            td2 = await get_text_xpath(page, f"{X_TBODY}/tr[{i}]/td[2]")
            td3 = await get_text_xpath(page, f"{X_TBODY}/tr[{i}]/td[3]")
            if td1 or td2 or td3:
                out.append((td1, td2, td3))
        return out
    except Exception:
        return []


async def get_eligible_status(page: Page) -> str:
    """
    Extract eligible status from the specific UL list (Arabic).
    XPath provided: .../table/tbody/tr[2]/td/ul
    Returns "لا يوجد تفاصيل" if not found.
    """
    try:
        # User-specific XPath for the UL containing eligibility items
        ul_xpath = "/html/body/div[4]/div/div/section/div[2]/main/section[3]/div/div/div/div/div[9]/div[2]/table/tbody/tr[2]/td/ul"
        
        ul_locator = page.locator(f"xpath={ul_xpath}")
        
        try:
            # Wait briefly to see if it exists
            await ul_locator.wait_for(state="visible", timeout=3000)
        except Exception:
            # If explicit UL not found, return default
            return "لا يوجد تفاصيل"

        # Extract all list items
        items = await ul_locator.locator("li").all_inner_texts()
        
        # Clean and filter empty items
        cleaned_items = [item.strip() for item in items if item.strip()]
        
        if cleaned_items:
            return "\n".join(cleaned_items)
            
        return "لا يوجد تفاصيل"

    except Exception:
        return "لا يوجد تفاصيل"


async def get_approvals_data(page: Page) -> str:
    """
    Extract approvals data using the same accordion IDs as Selenium version.
    Returns formatted Arabic string or default message.
    """
    try:
        # Scroll to middle to help lazy content
        try:
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight/2)")
        except Exception:
            pass

        # If no approvals heading, check no-approval message
        heading = page.locator("xpath=//h4[contains(text(), 'الموافقات المطلوبة')]")
        if await heading.count() == 0:
            try:
                no_el = page.locator(f"xpath={X_NO_APPROVAL}")
                if await no_el.count() > 0:
                    txt = ((await no_el.text_content()) or "").strip()
                    if txt and not any(str(i) in txt[:10] for i in range(1, 7)):
                        return "هذا النشاط لا يتطلب موافقة"
            except Exception:
                pass

        approval_data = []
        # Check approval buttons heading0..heading11
        for i in range(12):
            btn = page.locator(f"xpath=//*[@id='heading{i}']/button")
            if await btn.count() == 0:
                break
            try:
                try:
                    await btn.scroll_into_view_if_needed()
                except Exception:
                    # Element may have become detached, try without scroll
                    pass
                title_text = ((await btn.text_content()) or "").strip()
                if title_text and title_text[0].isdigit() and "." in title_text[:5]:
                    title_text = title_text.split(".", 1)[1].strip()
                approval_title = title_text or f"الموافقة {i+1}"
            except Exception:
                approval_title = f"الموافقة {i+1}"

            # Click to expand
            try:
                await btn.click()
            except Exception:
                try:
                    await page.evaluate("(el) => el.click()", await btn.element_handle())
                except Exception:
                    pass

            # Read agency
            agency = "غير محدد"
            try:
                agency_el = page.locator(f"xpath=//*[@id='collapse{i}']/div/div/div[1]/div[2]")
                if await agency_el.count() > 0:
                    try:
                        await agency_el.scroll_into_view_if_needed()
                    except Exception:
                        # Element may have become detached, try without scroll
                        pass
                    agency_txt = ((await agency_el.text_content()) or "").strip()
                    agency = agency_txt or agency
            except Exception:
                pass

            approval_data.append((i + 1, approval_title, agency))

        if not approval_data:
            return "هذا النشاط لا يتطلب موافقة"

        parts = []
        for num, title, agency in approval_data:
            parts.append(f"الموافقة {num}: {title}\nالجهة {num}: {agency}")
        return "\n\n".join(parts)
    except Exception:
        return "Error extracting approvals"


def save_activity_code_to_sheet(worksheet, row_number: int, activity_code: str) -> bool:
    try:
        # Write code as string (Column B is already formatted as TEXT to preserve leading zeros)
        worksheet.update_cell(row_number, 2, str(activity_code))
        return True
    except Exception:
        return False


def save_to_sheet(worksheet, row_number: int, col: int, value: str) -> bool:
    try:
        worksheet.update_cell(row_number, col, value)
        return True
    except Exception:
        return False


async def process_activity_code(page: Page, code: str, row_number: int, worksheet) -> bool:
    """
    Process a single activity code and write results to the sheet.
    """
    popup_details_page: Page | None = None
    try:
        print(f"Processing row {row_number} with code {code} ...")

        # FASTEST APPROACH: Try direct URL first
        try:
            # Direct URL attempt (silent)
            page = await direct_to_details(page, code)
            print("  ✓ Success")
        except Exception as e:
            print(f"\n  Direct URL failed: {e}")
            print(f"  Falling back to search methods...")
            
            # Fallback to original search flow
            try:
                await click_xpath(page, X_SEARCH_ICON)
                await click_xpath(page, X_BUSINESS_TAB)
                await fill_css(page, CSS_SEARCH_INPUT, code)

                try:
                    await page.wait_for_load_state("networkidle", timeout=10_000)
                except Exception:
                    pass

                # Primary flow: click first result
                try:
                    await click_xpath(page, X_FIRST_ACTIVITY)
                    await page.wait_for_load_state("networkidle", timeout=20_000)
                    await page.locator(f"xpath={X_ACTIVITY_CODE}").wait_for(state="visible", timeout=20_000)
                except PlaywrightTimeoutError:
                    print("Additional Step: Footer Business Activities Search")
                    details_page = await additional_step_footer_business_search(page, code)
                    if details_page is not page:
                        popup_details_page = details_page
                        page = details_page
            except Exception as fallback_error:
                print(f"All methods failed: {fallback_error}")
                return False

        # Ensure Arabic mode first
        await set_language(page, "ar")

        # Extract activity code
        activity_code = await get_text_xpath(page, X_ACTIVITY_CODE, timeout_ms=10_000)
        if not activity_code:
            return False
        save_activity_code_to_sheet(worksheet, row_number, activity_code)

        # Arabic activity name (Column C)
        await set_language(page, "ar")
        ar_name = await get_text_xpath(page, X_ACTIVITY_NAME, timeout_ms=10_000)
        save_to_sheet(worksheet, row_number, 3, ar_name)

        # English activity name (Column D)
        if await set_language(page, "en"):
            en_name = await get_text_xpath(page, X_ACTIVITY_NAME, timeout_ms=10_000)
            save_to_sheet(worksheet, row_number, 4, en_name)

        # Back to Arabic for the rest
        await set_language(page, "ar")

        # Location data (Column E) – format in Arabic labels like Selenium AR script
        rows = await get_table_data(page)
        if rows:
            formatted = []
            for i, (main_location, sub_location, fee) in enumerate(rows, start=1):
                formatted.append(f"تصنيف الموقع {i}: {main_location}\nنوع الموقع {i}: {sub_location}\nالرسوم {i}: {fee}")
            save_to_sheet(worksheet, row_number, 5, "\n\n".join(formatted))

        # Eligible status (Column F)
        eligible = await get_eligible_status(page)
        save_to_sheet(worksheet, row_number, 6, eligible)

        # Approvals (Column G)
        approvals = await get_approvals_data(page)
        save_to_sheet(worksheet, row_number, 7, approvals)

        return True
    except Exception as e:
        print(f"Error processing activity code {code}: {e}")
        await _safe_screenshot(page, os.path.join(SCRIPT_DIR, f"error_row_{row_number}.png"))
        return False
    finally:
        if popup_details_page is not None:
            try:
                await popup_details_page.close()
            except Exception:
                pass


async def run(headless: bool) -> None:
    worksheet = connect_to_sheets()

    # Set headers (same as Selenium AR script)
    worksheet.update_cell(1, 2, "Activity_Code")
    worksheet.update_cell(1, 3, "AR-Activity")
    worksheet.update_cell(1, 4, "EN-Activity")
    worksheet.update_cell(1, 5, "Location")
    worksheet.update_cell(1, 6, "Eligible")
    worksheet.update_cell(1, 7, "Approvals")
    
    # Format Column B as TEXT to preserve leading zeros
    format_column_b_as_text(worksheet)

    codes = worksheet.col_values(1)[1:]  # from row 2
    if not codes:
        print("No activity codes found in sheet")
        write_progress('ar', 'error', 0, 0, 'No activity codes found in sheet')
        return
    
    total_rows = len(codes)
    start_time = time.time()
    total_success = 0
    total_failed = 0
    
    # Write initial progress - scraper starting
    write_progress('ar', 'running', 0, total_rows, 'Starting AR scraper...', start_time=start_time)

    base_url = BASE_URL

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless)
        page = await browser.new_page()
        page.set_default_timeout(120_000)

        try:
            for idx, code in enumerate(codes, start=2):
                ok = False
                
                # Update progress - processing current row
                current_row_num = idx - 1  # Convert to 0-based for display
                write_progress('ar', 'running', current_row_num, total_rows, 
                             f'Processing row {current_row_num}/{total_rows}', total_success, start_time=start_time)
                
                try:
                    await page.goto(base_url, wait_until="domcontentloaded")
                    await page.wait_for_load_state("networkidle", timeout=30_000)
                    ok = await process_activity_code(page, code, idx, worksheet)
                except Exception as e:
                    print(f"Error: {e}")
                    await _safe_screenshot(page, os.path.join(SCRIPT_DIR, f"error_row_{idx}.png"))

                if not ok:
                    print(f"Failed to process {code}")
                    total_failed += 1
                else:
                    total_success += 1
            
            # Write completion progress
            write_progress('ar', 'completed', total_rows, total_rows, 
                         'Scraping completed successfully', total_success, start_time=start_time)
            
        except Exception as e:
            # Write error progress on exception
            error_message = f'Scraper error: {str(e)}'
            write_progress('ar', 'error', 0, total_rows, error_message, total_success, start_time=start_time)
            print(f"Fatal error: {e}")
            raise
        finally:
            try:
                await browser.close()
            except Exception:
                # Browser may have already closed or crashed
                pass
                
    # Calculate elapsed time
    elapsed_time = time.time() - start_time
    minutes = int(elapsed_time // 60)
    seconds = int(elapsed_time % 60)
    
    # Print terminal summary
    print("\n" + "="*70)
    print("SCRAPE SUMMARY (AR)")
    print("="*70)
    print(f"Elapsed Time:       {minutes}m {seconds}s")
    print(f"Total Success Rows: {total_success}")
    if total_failed > 0:
        print(f"Total Failed Rows:  {total_failed}")
    print("="*70)


def main() -> None:
    parser = argparse.ArgumentParser(description="Scrape AR/EN details using Playwright (default headless)")
    parser.add_argument("--visible", action="store_true", help="Run browser visible (default is headless)")
    args = parser.parse_args()

    asyncio.run(run(headless=not args.visible))


if __name__ == "__main__":
    main()


