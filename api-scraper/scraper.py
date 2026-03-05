import asyncio
import json
import os
import re
import time
from typing import Optional, List, Tuple, Dict, Any

from scrapling.fetchers import StealthyFetcher
from playwright.async_api import Page, TimeoutError as PlaywrightTimeoutError

# ----------------------------
# Configuration
# ----------------------------
BASE_URL = (
    "https://investor.sw.gov.qa/wps/portal/investors/home/"
    "!ut/p/z1/04_Sj9CPykssy0xPLMnMz0vMAfIjo8zivfxNXA393Q38LXy9DQzMAj0cg4NcLY0MDMz1"
    "w_Wj9KNQlISGGRkEOjuZBjm6Wxj7OxpCFRjgAI4G-sGJRfoF2dlpjo6KigD6q7KF/dz/d5/"
    "L0lHSkovd0RNQUZrQUVnQSEhLzROVkUvZW4!/"
)

# Details page XPaths
X_ACTIVITY_CODE = "/html/body/div[4]/div/div/section/div[2]/main/section[3]/div/div/div/div/div[1]/div[2]"
X_ACTIVITY_NAME = "/html/body/div[4]/div/div/section/div[2]/main/section[3]/div/div/div/div/div[3]/div[2]"
X_STATUS = "/html/body/div[4]/div/div/section/div[2]/main/section[3]/div/div/div/div/div[2]/div[2]/div"
X_TBODY = "/html/body/div[4]/div/div/section/div[2]/main/section[3]/div/div/div/div/div[8]/div[2]/table/tbody"
X_NO_APPROVAL = "/html/body/div[4]/div/div/section/div[2]/main/section[3]/div/div/div/div/div[10]/div[2]"

# Search flow selectors
X_SEARCH_ICON = "//*[@id='searchIconId']"
X_BUSINESS_TAB = "//*[@id='nav-business-tab']"
CSS_SEARCH_INPUT = "input#searchInput"
X_FIRST_ACTIVITY = "//*[@id='businessList']/li/a/div"
X_LANG_TOGGLE = "//*[@id='swChangeLangLink']/div"

# Footer business activities search
X_FOOTER_BUSINESS_ACTIVITIES = "/html/body/footer/section[1]/div/div/div[2]/ul/li[2]/a"
X_FOOTER_SEARCH_INPUT = (
    "/html/body/div[4]/div/div/section/div[2]/main/section[3]"
    "/div/div/div[1]/div/div/input"
)
X_FOOTER_SEARCH_CONTAINER = (
    "/html/body/div[4]/div/div/section/div[2]/main/section[3]/div/div/div[1]/div"
)
CSS_RESULTS_FIRST_ACTIVITY_LINK = "#pills-activities a.ba-link"


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


async def get_status(page: Page) -> str:
    try:
        return await get_text_xpath(page, X_STATUS, timeout_ms=10_000)
    except Exception:
        return "Unknown"


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
            await ul_locator.wait_for(state="visible", timeout=3_000)
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
    """Footer Business Activities Search fallback for ambiguous codes."""
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
        raise Exception(f"No exact match for code {code} in {count} results")
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


# --------------------------------------------------------- main scrape entry --

async def scrape_activity_code(code: str) -> Dict[str, Any]:
    """
    Scrape activity details for a given business activity code.
    Returns {"status": "success"|"error", "data": {...}|None, "error": str|None}.
    """
    extracted: Dict[str, Any] = {}

    details_url = (
        f"https://investor.sw.gov.qa/wps/portal/investors/information-center"
        f"/ba/details?bacode={code}"
    )

    async def page_action(page: Page) -> None:
        popup_details_page: Page | None = None
        try:
            # Strategy 1: direct URL (StealthyFetcher already navigated here)
            try:
                await page.locator(f"xpath={X_ACTIVITY_CODE}").wait_for(
                    state="visible", timeout=30_000
                )
                active_page = page
            except PlaywrightTimeoutError:
                # Strategy 2: search flow fallback
                active_page = await _run_search_fallback(page, code)
                if active_page is not page:
                    popup_details_page = active_page

            # Extract English data
            await set_language(active_page, "en")
            extracted["activity_code"] = await get_text_xpath(active_page, X_ACTIVITY_CODE)
            if not extracted["activity_code"]:
                extracted["_error"] = "Activity code element empty"
                return
            extracted["status"] = await get_status(active_page)

            await set_language(active_page, "en")
            extracted["name_en"] = await get_text_xpath(active_page, X_ACTIVITY_NAME)

            # Extract Arabic name
            if await set_language(active_page, "ar"):
                extracted["name_ar"] = await get_text_xpath(active_page, X_ACTIVITY_NAME)
            else:
                extracted["name_ar"] = "Error switching to Arabic"

            # Back to English for remaining fields
            await set_language(active_page, "en")

            rows = await get_table_data(active_page)
            if rows:
                parts = [
                    f"Main Location {i}: {m}\nSub Location {i}: {s}\nFee {i}: {f}"
                    for i, (m, s, f) in enumerate(rows, start=1)
                ]
                extracted["locations"] = "\n\n".join(parts)
            else:
                extracted["locations"] = ""

            extracted["eligible"] = await get_eligible_status(active_page)
            extracted["approvals"] = await get_approvals_data(active_page)

        except Exception as exc:
            extracted["_error"] = str(exc)
        finally:
            if popup_details_page is not None:
                try:
                    await popup_details_page.close()
                except Exception:
                    pass

    await StealthyFetcher.async_fetch(
        details_url,
        headless=True,
        disable_resources=True,
        network_idle=True,
        page_action=page_action,
        timeout=120_000,
    )

    if extracted.get("activity_code"):
        return {
            "status": "success",
            "data": {
                "activity_code": extracted.get("activity_code", ""),
                "status": extracted.get("status", ""),
                "name_en": extracted.get("name_en", ""),
                "name_ar": extracted.get("name_ar", ""),
                "locations": extracted.get("locations", ""),
                "eligible": extracted.get("eligible", ""),
                "approvals": extracted.get("approvals", ""),
            },
            "error": None,
        }
    return {
        "status": "error",
        "data": None,
        "error": extracted.get("_error", "No data extracted"),
    }


async def _run_search_fallback(page: Page, code: str) -> Page:
    """Search fallback: try header search first, then footer business search."""
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
        business_list = page.locator("//*[@id='businessList']/li")
        count = await business_list.count()
        if count > 1:
            return await _footer_business_search(page, code)
        # Single result - click it
        try:
            first = page.locator(f"xpath={X_FIRST_ACTIVITY}")
            await first.wait_for(state="visible", timeout=10_000)
            await first.click()
            await page.wait_for_load_state("networkidle", timeout=20_000)
            await page.locator(f"xpath={X_ACTIVITY_CODE}").wait_for(
                state="visible", timeout=20_000
            )
            return page
        except PlaywrightTimeoutError:
            return await _footer_business_search(page, code)
    except Exception:
        return await _footer_business_search(page, code)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--code", required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = asyncio.run(scrape_activity_code(args.code))
    if args.json:
        print(json.dumps(result, ensure_ascii=True, indent=2))
    else:
        if result["status"] == "success":
            for k, v in result["data"].items():
                print(f"{k}: {v}")
        else:
            print(f"Error: {result['error']}")
