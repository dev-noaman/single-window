# pyright: reportMissingImports=false
import os
import argparse
import time
import re
import warnings
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from scrapling.fetchers import StealthyFetcher
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

# Suppress gspread deprecation warnings
warnings.filterwarnings('ignore', category=UserWarning, module='gspread')

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DRIVE_DIR = os.path.join(SCRIPT_DIR, "drive")
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "output")

# XPath / CSS Constants (same targets as the original Selenium version)
X_NEXT_BUTTON_LI = "//*[@id='pills-activities']//li[contains(@ng-click, 'nextPage()')]"
X_NEXT_BUTTON_LINK = "//*[@id='pills-activities']//li[contains(@ng-click, 'nextPage()')]//div[@class='page-link']"


def save_html_snapshot(page: Page, filename: str):
    try:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        file_path = os.path.join(OUTPUT_DIR, filename)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(page.content())
    except Exception:
        pass


def get_page_indicator_text(page: Page) -> str:
    try:
        element = page.locator("css=div.page-number")
        if element.count() > 0:
            return (element.first.inner_text() or "").strip()
        return ""
    except Exception:
        return ""


def get_page_numbers(page: Page):
    text = get_page_indicator_text(page)
    if not text:
        return None, None
    try:
        parts = text.replace("Page", "").strip().split("/")
        cur = int(parts[0].strip())
        last = int(parts[1].strip())
        return cur, last
    except Exception:
        return None, None


def get_activity_codes(page: Page) -> list:
    try:
        elements = page.locator("css=div.orange-text.ng-binding").all()
        codes = []
        for el in elements:
            text = (el.inner_text() or "").strip()
            if text and text.isdigit():
                codes.append(text)
        return codes
    except Exception:
        return []


def codes_fingerprint(codes: list) -> str:
    return "|".join(codes[:10]) if codes else ""


def wait_for_codes_change(page: Page, previous_codes: list, timeout: int = 20) -> list:
    prev_fp = codes_fingerprint(previous_codes)
    start = time.time()
    while (time.time() - start) < timeout:
        codes = get_activity_codes(page)
        if codes and codes_fingerprint(codes) != prev_fp:
            return codes
        time.sleep(0.5)
    return get_activity_codes(page)


def is_next_button_disabled(page: Page) -> bool:
    try:
        next_button = page.locator(f"xpath={X_NEXT_BUTTON_LI}")
        if next_button.count() == 0:
            return True
        class_attr = next_button.first.get_attribute("class") or ""
        return "disabled" in class_attr
    except Exception:
        return True


def get_total_results_count(page: Page, timeout: int = 5) -> int:
    try:
        element = page.locator("css=div.result-search-info span")
        element.wait_for(state="visible", timeout=timeout * 1000)
        text = (element.first.inner_text() or "").strip()
        if text:
            match = re.search(r'(\d[\d,]*)', text)
            if match:
                return int(match.group(1).replace(',', ''))
    except Exception:
        pass
    return None


def get_expected_pages(page: Page, timeout: int = 5) -> int:
    try:
        element = page.locator("css=div.page-number")
        element.wait_for(state="visible", timeout=timeout * 1000)
        text = (element.first.inner_text() or "").strip()
        if text:
            match = re.search(r'Page\s+\d+\s*/\s*(\d+)', text, re.IGNORECASE)
            if match:
                return int(match.group(1))
            numbers = re.findall(r'\d+', text)
            if len(numbers) >= 2:
                return int(numbers[-1])
    except Exception:
        pass
    return None


def set_page_size_30(page: Page) -> bool:
    try:
        dropdown = page.locator("#page_num_select")
        dropdown.wait_for(state="visible", timeout=10_000)
        dropdown.select_option("30")
        time.sleep(3)
        page.locator("css=div.orange-text.ng-binding").first.wait_for(state="visible", timeout=15_000)
        return True
    except Exception as e:
        print(f"Warning: Could not set page size to 30: {e}")
        return False


def wait_for_results(page: Page, expected_count: int = 30, timeout: int = 15) -> int:
    start = time.time()
    while (time.time() - start) < timeout:
        actual_count = len(get_activity_codes(page))
        if actual_count == expected_count:
            return actual_count
        if is_next_button_disabled(page) and actual_count > 0:
            return actual_count
        time.sleep(0.5)
    return len(get_activity_codes(page))


def save_codes_bulk(worksheet, start_row: int, codes: list) -> bool:
    if not worksheet or not codes:
        return True
    values = [[str(c)] for c in codes]
    end_row = start_row + len(codes) - 1
    range_notation = f"A{start_row}:A{end_row}"
    for _ in range(3):
        try:
            worksheet.update(range_notation, values)
            return True
        except Exception:
            time.sleep(1)
    try:
        for i, c in enumerate(codes):
            worksheet.update_cell(start_row + i, 1, str(c))
        return True
    except Exception:
        return False


def format_column_as_text(worksheet):
    try:
        worksheet.format("A:A", {"numberFormat": {"type": "TEXT"}})
        return True
    except Exception as e:
        print(f"Warning: Could not format column as TEXT: {e}")
        return False


def connect_to_sheets():
    try:
        credentials_file = os.path.join(DRIVE_DIR, "google-credentials.json")
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        credentials = ServiceAccountCredentials.from_json_keyfile_name(credentials_file, scope)
        client = gspread.authorize(credentials)
        spreadsheet = client.open("Filter")
        worksheet = spreadsheet.worksheet("CODE")
        return worksheet
    except Exception as e:
        print(f"Error connecting to Google Sheets: {e}")
        return None


def print_page_table(page_number: int, codes: list):
    try:
        print(f"\nPage {page_number}")
        print(f"Found {len(codes)} activities")
        print("┌─────────────┐")
        for code in codes:
            print(f"│ {code:<11} │")
        print("└─────────────┘")
    except UnicodeEncodeError:
        print(f"\nPage {page_number}")
        print(f"Found {len(codes)} activities")
        print("+-------------+")
        for code in codes:
            print(f"| {code:<11} |")
        print("+-------------+")


def main():
    parser = argparse.ArgumentParser(description='Scrape activity codes from investor portal (Scrapling)')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--visible', action='store_true', help='Run browser in visible mode')
    group.add_argument('--headless', action='store_true', help='Run browser in headless mode')
    args = parser.parse_args()

    is_headless = not args.visible
    start_time = time.time()

    print("Browser started (Scrapling StealthyFetcher)")

    # All scraping logic inside a sync page_action so StealthyFetcher manages
    # the browser lifecycle and anti-bot stealth features.
    collected = {
        'current_row': 2,
        'pages_processed': 0,
        'last_saved_fp': None,
        'expected_total_results': None,
        'expected_total_pages': None,
    }
    worksheet = connect_to_sheets()
    if worksheet:
        worksheet.update_cell(1, 1, "Search")
        format_column_as_text(worksheet)
    else:
        print("Could not connect to Google Sheets, skipping save")

    base_url = (
        "https://investor.sw.gov.qa/wps/portal/investors/home/"
        "!ut/p/z1/04_Sj9CPykssy0xPLMnMz0vMAfIjo8zivfxNXA393Q38LXy9DQzMAj0cg4NcLY0MDMz1"
        "w_Wj9KNQlISGGRkEOjuZBjm6Wxj7OxpCFRjgAI4G-sGpefoF2dlpjo6KigAeufkI/dz/d5/"
        "L2dBISEvZ0FBIS9nQSEh/"
    )

    def scrape_all_pages(page: Page):
        # Scroll to footer and click Business Activities link
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(1)

        footer_link = page.locator("xpath=/html/body/footer/section[1]/div/div/div[2]/ul/li[2]/a")
        footer_link.wait_for(state="visible", timeout=10_000)
        footer_link.click()

        page.wait_for_load_state("networkidle", timeout=30_000)
        time.sleep(5)

        # Type "10" in search box then press Enter (original behavior)
        input_xpath = (
            "/html/body/div[4]/div/div/section/div[2]/main/section[3]"
            "/div/div/div[1]/div/div/input"
        )
        input_field = page.locator(f"xpath={input_xpath}")
        input_field.wait_for(state="visible", timeout=10_000)
        input_field.fill("10")
        input_field.press("Enter")
        time.sleep(3)

        # Click Remove button to clear the filter
        remove_button_xpath = (
            "/html/body/div[4]/div/div/section/div[2]/main/section[3]"
            "/div/div/div[1]/div/div/div/div/span"
        )
        remove_button = page.locator(f"xpath={remove_button_xpath}")
        remove_button.wait_for(state="clickable", timeout=10_000)
        remove_button.click()

        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(1)

        # Scroll to activity codes container
        try:
            container = page.locator("xpath=/html/body/div[4]/div/div/section/div[2]/main/section[3]/div/div/div[3]")
            if container.count() > 0:
                container.first.scroll_into_view_if_needed()
                time.sleep(1)
        except Exception:
            pass

        set_page_size_30(page)
        wait_for_results(page, expected_count=30, timeout=15)

        activity_codes = get_activity_codes(page)

        collected['expected_total_results'] = get_total_results_count(page, timeout=5)
        collected['expected_total_pages'] = get_expected_pages(page, timeout=5)

        print(f"\n{'='*40}")
        if collected['expected_total_results']:
            print(f"Expected Total Results: {collected['expected_total_results']}")
        else:
            print("Expected Total Results: Unknown")
        if collected['expected_total_pages']:
            print(f"Expected Total Pages:   {collected['expected_total_pages']}")
        else:
            print("Expected Total Pages:   Unknown")
        print(f"{'='*40}\n")

        page_number = 1

        while True:
            ui_cur, ui_last = get_page_numbers(page)
            if ui_cur:
                page_number = ui_cur

            if activity_codes:
                print_page_table(page_number, activity_codes)

            if activity_codes and worksheet:
                try:
                    current_fp = codes_fingerprint(activity_codes)
                    if collected['last_saved_fp'] == current_fp:
                        print("Skipped saving (duplicate page content)")
                    else:
                        saved_ok = save_codes_bulk(worksheet, collected['current_row'], activity_codes)
                        if saved_ok:
                            collected['current_row'] += len(activity_codes)
                            print("Saved to sheet")
                            collected['last_saved_fp'] = current_fp
                        else:
                            print("Error saving to sheet")
                except Exception as e:
                    print(f"Error saving to sheet: {e}")

            save_html_snapshot(page, f"output_page_{page_number}.html")
            collected['pages_processed'] += 1

            if is_next_button_disabled(page):
                print("\nReached last page (Next button disabled)")
                break

            try:
                before_text = get_page_indicator_text(page)
                before_codes = activity_codes

                next_button_link = page.locator(f"xpath={X_NEXT_BUTTON_LINK}")
                next_button_link.wait_for(state="visible", timeout=10_000)
                try:
                    next_button_link.click()
                except Exception:
                    page.evaluate("(el) => el.click()", next_button_link.element_handle())

                # Wait for page indicator to change
                wait_start = time.time()
                while time.time() - wait_start < 15:
                    new_text = get_page_indicator_text(page)
                    if new_text != before_text:
                        break
                    time.sleep(0.5)

                ui_cur2, _ = get_page_numbers(page)
                if ui_cur2:
                    page_number = ui_cur2

                time.sleep(2)
                wait_for_results(page, expected_count=30, timeout=15)

                try:
                    container = page.locator(
                        "xpath=/html/body/div[4]/div/div/section/div[2]/main/section[3]/div/div/div[3]"
                    )
                    if container.count() > 0:
                        container.first.scroll_into_view_if_needed()
                        time.sleep(1)
                except Exception:
                    pass

                activity_codes = wait_for_codes_change(page, before_codes, timeout=25)

            except Exception as e:
                save_html_snapshot(page, f"output_stopped_page_{page_number}.html")
                print(f"Stopped pagination at page {page_number}: {e}")
                break

    try:
        StealthyFetcher.fetch(
            base_url,
            headless=is_headless,
            network_idle=True,
            page_action=scrape_all_pages,
            timeout=600_000,  # 10 min total (many pages)
        )
    except Exception as e:
        print(f"Error: {str(e)}")
        try:
            pass  # screenshot not available outside page_action
        except Exception:
            pass

    # Summary
    total_activities_saved = collected['current_row'] - 2
    elapsed_time = time.time() - start_time
    minutes = int(elapsed_time // 60)
    seconds = int(elapsed_time % 60)

    print(f"\n{'='*40}")
    print(f"{'SUMMARY':^40}")
    print(f"{'='*40}")
    print(f"\nElapsed Time:    {minutes}m {seconds}s")

    actual_pages = collected['expected_total_pages'] or collected['pages_processed']
    expected_total_pages = collected['expected_total_pages']
    expected_total_results = collected['expected_total_results']

    print(f"\nPages:")
    if expected_total_pages is not None:
        print(f"  Expected:      {expected_total_pages}")
        print(f"  Actual:        {actual_pages}")
        status = "✓ OK" if actual_pages == expected_total_pages else f"✗ MISMATCH (diff: {actual_pages - expected_total_pages:+d})"
        print(f"  Status:        {status}")
    else:
        print(f"  Actual:        {actual_pages}")
        print(f"  Status:        Unknown")

    print(f"\nResults:")
    if expected_total_results is not None:
        print(f"  Expected:      {expected_total_results}")
        print(f"  Scraped/Saved: {total_activities_saved}")
        status = "✓ OK" if total_activities_saved == expected_total_results else f"✗ MISMATCH (diff: {total_activities_saved - expected_total_results:+d})"
        print(f"  Status:        {status}")
    else:
        print(f"  Scraped/Saved: {total_activities_saved}")
        print(f"  Status:        Unknown")

    print(f"\n{'='*40}")

    os.makedirs(OUTPUT_DIR, exist_ok=True)


if __name__ == "__main__":
    main()
