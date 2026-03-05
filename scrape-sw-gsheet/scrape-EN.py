# pyright: reportMissingImports=false
import asyncio
import argparse
import os
import re
import time
from typing import Optional, List, Tuple

import gspread
from oauth2client.service_account import ServiceAccountCredentials
from scrapling.fetchers import StealthyFetcher
from playwright.async_api import Page, TimeoutError as PlaywrightTimeoutError

# Import progress writer for real-time monitoring
from progress_writer import write_progress

# ----------------------------
# Configuration
# ----------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DRIVE_DIR = os.path.join(SCRIPT_DIR, "drive")
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "output")
GOOGLE_CREDENTIALS_FILE = os.path.join(DRIVE_DIR, "google-credentials.json")
SPREADSHEET_NAME = "Filter"
WORKSHEET_NAME = "EN"
BASE_URL = (
    "https://investor.sw.gov.qa/wps/portal/investors/home/"
    "!ut/p/z1/04_Sj9CPykssy0xPLMnMz0vMAfIjo8zivfxNXA393Q38LXy9DQzMAj0cg4NcLY0MDMz1"
    "w_Wj9KNQlISGGRkEOjuZBjm6Wxj7OxpCFRjgAI4G-sGJRfoF2dlpjo6KigD6q7KF/dz/d5/"
    "L0lHSkovd0RNQUZrQUVnQSEhLzROVkUvZW4!/"
)

# Details page XPaths
X_ACTIVITY_CODE = "/html/body/div[4]/div/div/section/div[2]/main/section[3]/div/div/div/div/div[1]/div[2]"
X_ACTIVITY_NAME = "/html/body/div[4]/div/div/section/div[2]/main/section[3]/div/div/div/div/div[3]/div[2]"
X_TBODY = "/html/body/div[4]/div/div/section/div[2]/main/section[3]/div/div/div/div/div[8]/div[2]/table/tbody"
X_NO_APPROVAL = "/html/body/div[4]/div/div/section/div[2]/main/section[3]/div/div/div/div/div[10]/div[2]"

# Search flow selectors
X_SEARCH_ICON = "//*[@id='searchIconId']"
X_BUSINESS_TAB = "//*[@id='nav-business-tab']"
CSS_SEARCH_INPUT = "input#searchInput"
X_FIRST_ACTIVITY = "//*[@id='businessList']/li/a/div"
X_LANG_TOGGLE = "//*[@id='swChangeLangLink']/div"

# Footer Business Activities Search
X_FOOTER_BUSINESS_ACTIVITIES = "/html/body/footer/section[1]/div/div/div[2]/ul/li[2]/a"
X_FOOTER_SEARCH_INPUT = (
    "/html/body/div[4]/div/div/section/div[2]/main/section[3]"
    "/div/div/div[1]/div/div/input"
)
X_FOOTER_SEARCH_CONTAINER = (
    "/html/body/div[4]/div/div/section/div[2]/main/section[3]/div/div/div[1]/div"
)
CSS_RESULTS_FIRST_ACTIVITY_LINK = "#pills-activities a.ba-link"


def format_column_b_as_text(worksheet):
    try:
        worksheet.format("B:B", {"numberFormat": {"type": "TEXT"}})
        return True
    except Exception as e:
        print(f"Warning: Could not format column B as TEXT: {e}")
        return False


def connect_to_sheets():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    credentials = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_CREDENTIALS_FILE, scope)
    client = gspread.authorize(credentials)
    return client.open(SPREADSHEET_NAME).worksheet(WORKSHEET_NAME)


# ------------------------------------------------------------------ helpers --

async def _get_lang(page: Page) -> str:
    try:
        return (await page.evaluate("document.documentElement.lang")) or ""
    except Exception:
        return ""


async def set_language(page: Page, target_lang: str, timeout_s: int = 10) -> bool:
    try:
        if await _get_lang(page) == target_lang:
            return True
        btn = page.locator(f"xpath={X_LANG_TOGGLE}")
        await btn.wait_for(state="visible", timeout=10_000)
        try:
            await btn.scroll_into_view_if_needed()
        except Exception:
            pass
        await btn.click()
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


async def get_text_xpath(page: Page, xpath: str, timeout_ms: int = 10_000) -> str:
    el = page.locator(f"xpath={xpath}")
    await el.wait_for(state="visible", timeout=timeout_ms)
    try:
        await el.scroll_into_view_if_needed()
    except Exception:
        pass
    return ((await el.text_content()) or "").strip()


async def get_table_data(page: Page) -> List[Tuple[str, str, str]]:
    try:
        tbody = page.locator(f"xpath={X_TBODY}")
        await tbody.wait_for(state="visible", timeout=10_000)
        try:
            await tbody.scroll_into_view_if_needed()
        except Exception:
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
    try:
        ul_xpath = (
            "/html/body/div[4]/div/div/section/div[2]/main/section[3]"
            "/div/div/div/div/div[9]/div[2]/table/tbody/tr[2]/td/ul"
        )
        ul_locator = page.locator(f"xpath={ul_xpath}")
        try:
            await ul_locator.wait_for(state="visible", timeout=3000)
        except Exception:
            return "No Business Requirements"
        items = await ul_locator.locator("li").all_inner_texts()
        cleaned = [i.strip() for i in items if i.strip()]
        return "\n".join(cleaned) if cleaned else "No Business Requirements"
    except Exception:
        return "No Business Requirements"


async def get_approvals_data(page: Page) -> str:
    try:
        try:
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight/2)")
        except Exception:
            pass
        heading = page.locator("xpath=//h4[contains(text(), 'الموافقات المطلوبة')]")
        if await heading.count() == 0:
            try:
                no_el = page.locator(f"xpath={X_NO_APPROVAL}")
                if await no_el.count() > 0:
                    txt = ((await no_el.text_content()) or "").strip()
                    if txt and not any(str(i) in txt[:10] for i in range(1, 7)):
                        return "No Approvals Needed"
            except Exception:
                pass
        approval_data = []
        for i in range(12):
            btn = page.locator(f"xpath=//*[@id='heading{i}']/button")
            if await btn.count() == 0:
                break
            try:
                try:
                    await btn.scroll_into_view_if_needed()
                except Exception:
                    pass
                title_text = ((await btn.text_content()) or "").strip()
                if title_text and title_text[0].isdigit() and "." in title_text[:5]:
                    title_text = title_text.split(".", 1)[1].strip()
                approval_title = title_text or f"Approval {i+1}"
            except Exception:
                approval_title = f"Approval {i+1}"
            try:
                await btn.click()
            except Exception:
                try:
                    await page.evaluate("(el) => el.click()", await btn.element_handle())
                except Exception:
                    pass
            agency = "Not specified"
            try:
                agency_el = page.locator(f"xpath=//*[@id='collapse{i}']/div/div/div[1]/div[2]")
                if await agency_el.count() > 0:
                    try:
                        await agency_el.scroll_into_view_if_needed()
                    except Exception:
                        pass
                    agency_txt = ((await agency_el.text_content()) or "").strip()
                    agency = agency_txt or agency
            except Exception:
                pass
            approval_data.append((i + 1, approval_title, agency))
        if not approval_data:
            return "No Approvals Needed"
        parts = [f"Approval {num}: {title}\nAgency {num}: {agency}" for num, title, agency in approval_data]
        return "\n\n".join(parts)
    except Exception:
        return "Error extracting approvals"


async def _footer_business_search(page: Page, code: str) -> Page:
    await page.goto(BASE_URL, wait_until="domcontentloaded")
    try:
        await page.wait_for_load_state("networkidle", timeout=30_000)
    except Exception:
        pass
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
    inp = page.locator(f"xpath={X_FOOTER_SEARCH_INPUT}")
    await inp.wait_for(state="visible", timeout=20_000)
    await inp.fill(code)
    try:
        await inp.press("Enter")
    except Exception:
        pass
    try:
        btn = page.locator(
            "xpath=//button[contains(translate(normalize-space(.), 'search', 'SEARCH'), 'SEARCH')]"
        )
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
    results_root = page.locator("css=#pills-activities")
    await results_root.wait_for(state="attached", timeout=20_000)
    all_links = page.locator(f"css={CSS_RESULTS_FIRST_ACTIVITY_LINK}")
    await all_links.first.wait_for(state="visible", timeout=20_000)
    count = await all_links.count()
    link = None
    for i in range(count):
        cur = all_links.nth(i)
        href = await cur.get_attribute("href")
        m = re.search(r"(?:\?|&)bacode=(\d+)", href or "")
        if m and m.group(1) == code:
            link = cur
            break
    if link is None:
        raise Exception(f"No exact match found for code {code}. Found {count} results but none matched exactly.")
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


def save_activity_code_to_sheet(worksheet, row_number: int, activity_code: str) -> bool:
    try:
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


async def process_activity_code(page: Page, code: str, row_number: int, worksheet) -> tuple:
    """
    Process a single activity code using direct URL (Scrapling already navigated there).
    Returns: (success, used_additional_step, error_msg)
    """
    popup_details_page: Page | None = None
    used_additional = False
    error_msg = None

    try:
        print(f"Processing row {row_number} with code {code} ...")

        # Strategy 1: direct URL (page already at details URL via StealthyFetcher)
        try:
            await page.locator(f"xpath={X_ACTIVITY_CODE}").wait_for(state="visible", timeout=30_000)
            print("  ✓ Direct URL success")
        except Exception as e:
            print(f"\n  Direct URL failed: {e}")
            print(f"  Falling back to search methods...")
            try:
                search_icon = page.locator(f"xpath={X_SEARCH_ICON}")
                await search_icon.wait_for(state="visible", timeout=10_000)
                await search_icon.click()
                business_tab = page.locator(f"xpath={X_BUSINESS_TAB}")
                await business_tab.wait_for(state="visible", timeout=10_000)
                await business_tab.click()
                inp = page.locator(CSS_SEARCH_INPUT)
                await inp.wait_for(state="visible", timeout=10_000)
                await inp.fill(code)
                try:
                    await page.wait_for_load_state("networkidle", timeout=10_000)
                except Exception:
                    pass
                await asyncio.sleep(1)
                use_additional_step = False
                try:
                    business_list = page.locator("//*[@id='businessList']/li")
                    result_count = await business_list.count()
                    if result_count > 1:
                        print(f"Multiple results detected ({result_count}), using footer search")
                        use_additional_step = True
                except Exception:
                    pass
                if use_additional_step:
                    used_additional = True
                    details_page = await _footer_business_search(page, code)
                    if details_page is not page:
                        popup_details_page = details_page
                        page = details_page
                else:
                    try:
                        first = page.locator(f"xpath={X_FIRST_ACTIVITY}")
                        await first.wait_for(state="visible", timeout=10_000)
                        await first.click()
                        await page.wait_for_load_state("networkidle", timeout=20_000)
                        await page.locator(f"xpath={X_ACTIVITY_CODE}").wait_for(state="visible", timeout=20_000)
                    except PlaywrightTimeoutError:
                        used_additional = True
                        details_page = await _footer_business_search(page, code)
                        if details_page is not page:
                            popup_details_page = details_page
                            page = details_page
            except Exception as fallback_error:
                error_msg = f"All methods failed: {fallback_error}"
                return False, used_additional, error_msg

        await set_language(page, "en")

        activity_code = await get_text_xpath(page, X_ACTIVITY_CODE, timeout_ms=10_000)
        if not activity_code:
            return False, used_additional, "Activity code not found on details page"
        save_activity_code_to_sheet(worksheet, row_number, activity_code)

        await set_language(page, "en")
        en_name = await get_text_xpath(page, X_ACTIVITY_NAME, timeout_ms=10_000)
        save_to_sheet(worksheet, row_number, 4, en_name)

        if await set_language(page, "ar"):
            ar_name = await get_text_xpath(page, X_ACTIVITY_NAME, timeout_ms=10_000)
            save_to_sheet(worksheet, row_number, 3, ar_name)

        await set_language(page, "en")

        rows = await get_table_data(page)
        if rows:
            formatted = [
                f"Main Location {i}: {m}\nSub Location {i}: {s}\nFee {i}: {f}"
                for i, (m, s, f) in enumerate(rows, start=1)
            ]
            save_to_sheet(worksheet, row_number, 5, "\n\n".join(formatted))

        eligible = await get_eligible_status(page)
        save_to_sheet(worksheet, row_number, 6, eligible)

        approvals = await get_approvals_data(page)
        save_to_sheet(worksheet, row_number, 7, approvals)

        return True, used_additional, None

    except Exception as e:
        error_msg = str(e)
        print(f"Error processing activity code {code}: {e}")
        return False, used_additional, error_msg
    finally:
        if popup_details_page is not None:
            try:
                await popup_details_page.close()
            except Exception:
                pass


async def run(headless: bool) -> None:
    import time as time_module

    start_time = time_module.time()

    worksheet = connect_to_sheets()

    worksheet.update_cell(1, 2, "Activity_Code")
    worksheet.update_cell(1, 3, "AR-Activity")
    worksheet.update_cell(1, 4, "EN-Activity")
    worksheet.update_cell(1, 5, "Location")
    worksheet.update_cell(1, 6, "Eligible")
    worksheet.update_cell(1, 7, "Approvals")
    format_column_b_as_text(worksheet)

    codes = worksheet.col_values(1)[1:]
    if not codes:
        print("No activity codes found in sheet")
        write_progress('en', 'error', 0, 0, 'No activity codes found in sheet')
        return

    total_rows = len(codes)
    start_time = time.time()
    write_progress('en', 'running', 0, total_rows, 'Starting EN scraper...', start_time=start_time)

    total_success = 0
    total_failed = 0
    failed_codes = []

    for idx, code in enumerate(codes, start=2):
        current_row_num = idx - 1
        write_progress('en', 'running', current_row_num, total_rows,
                       f'Processing row {current_row_num}/{total_rows}', total_success, start_time=start_time)

        ok = False
        error_msg = None

        details_url = (
            f"https://investor.sw.gov.qa/wps/portal/investors/information-center"
            f"/ba/details?bacode={code}"
        )

        # Use closure to pass data between async page_action and outer scope
        result_holder = {}

        async def page_action(page: Page, _code=code, _idx=idx, _worksheet=worksheet, _holder=result_holder):
            ok2, used_add, err = await process_activity_code(page, _code, _idx, _worksheet)
            _holder['ok'] = ok2
            _holder['error'] = err

        try:
            await StealthyFetcher.async_fetch(
                details_url,
                headless=headless,
                disable_resources=True,
                network_idle=True,
                page_action=page_action,
                timeout=120_000,
            )
            ok = result_holder.get('ok', False)
            error_msg = result_holder.get('error')
        except Exception as e:
            error_msg = str(e)
            print(f"Error: {e}")

        if not ok:
            print(f"Failed to process {code}")
            total_failed += 1
            failed_codes.append(code)
        else:
            total_success += 1

    write_progress('en', 'completed', total_rows, total_rows,
                   'Scraping completed successfully', total_success, start_time=start_time)

    elapsed_time = time_module.time() - start_time
    minutes = int(elapsed_time // 60)
    seconds = int(elapsed_time % 60)

    print("\n" + "="*70)
    print("SCRAPE SUMMARY (EN)")
    print("="*70)
    print(f"Elapsed Time:       {minutes}m {seconds}s")
    print(f"Total Success Rows: {total_success}")
    if total_failed > 0:
        print(f"Total Failed Rows:  {total_failed}")
    print("="*70)


def main() -> None:
    parser = argparse.ArgumentParser(description="Scrape EN/AR details using Scrapling (default headless)")
    parser.add_argument("--visible", action="store_true", help="Run browser visible (default is headless)")
    args = parser.parse_args()
    asyncio.run(run(headless=not args.visible))


if __name__ == "__main__":
    main()
