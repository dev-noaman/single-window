#!/usr/bin/env python3
"""
Fetch Codes 2 - Simple approach: use curl to fetch URL, then save to DB.
Bypasses Python SSL stack; curl handles HTTPS with -k (insecure).
"""
import asyncio
import json
import os
import subprocess
import time
import asyncpg
from urllib.parse import urlparse

# Same API endpoint as discover_codes.py
ALL_ACTIVITIES_URL = (
    "https://investor.sw.gov.qa/wps/portal/investors/information-center/ba/search-results/"
    "!ut/p/z1/04_Sj9CPykssy0xPLMnMz0vMAfIjo8zivfxNXA393Q38Dbz9LA3MAt38_UyNDQ0MAk30w_"
    "EqcDTVjyJJv0VomJFBoLOTaZCju4Wxv6MhcfoNcABHA8L6o_AqAfkAVYG_r4uTgZmjqWeoo0uQobuvOboCLH4A"
    "K8DjyODEIv2C3NDQCINMT11HRUUAe2qoOw!!/dz/d5/L2dBISEvZ0FBIS9nQSEh/p0/"
    "IZ7_JO4E1OG0O0KN906QFON5310013=CZ6_JO4E1OG0O0KN906QFON53100Q4=NJbaSearchResource=/?"
)

PAGE_SIZE = 100
PROGRESS_FILE = "/tmp/fetch_progress.json"
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://codesuser:StrongPasswordHere@db:5432/codesdb")


def update_progress(status, message, current_page=0, total_pages=0, total_records=0,
                    new_inserted=0, updated=0, skipped=0):
    try:
        with open(PROGRESS_FILE, 'w') as f:
            json.dump({
                "status": status, "message": message,
                "current_page": current_page, "total_pages": total_pages, "total_records": total_records,
                "new_inserted": new_inserted, "updated": updated, "skipped": skipped,
                "timestamp": time.time()
            }, f)
    except Exception as e:
        print(f"Failed to update progress: {e}")


def fetch_page_curl(page_num):
    """Fetch one page via curl -k (ignore SSL). Returns (content, total_pages, total_elements, success)."""
    url = f"{ALL_ACTIVITIES_URL}page={page_num}&size={PAGE_SIZE}"
    cmd = [
        "curl", "-k", "-s", "-L", "--max-time", "120",
        "-H", "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "-H", "Accept: application/json, text/plain, */*",
        url,
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=125)
        body = result.stdout
        if result.returncode != 0 or not body or not body.strip():
            print(f"curl failed on page {page_num} (code={result.returncode})")
            return [], 1, 0, False
        data = json.loads(body)
        content = []
        total_pages = 1
        total_elements = 0
        if isinstance(data, dict) and "data" in data:
            inner = data["data"]
            if isinstance(inner, dict) and "activities" in inner:
                act = inner["activities"]
                content = act.get("content", [])
                total_pages = act.get("totalPages", 1)
                total_elements = act.get("totalElements", 0)
        return content, total_pages, total_elements, True
    except subprocess.TimeoutExpired:
        print(f"curl timeout on page {page_num}")
        return [], 1, 0, False
    except (json.JSONDecodeError, Exception) as e:
        print(f"Error fetching page {page_num}: {e}")
        return [], 1, 0, False


async def save_page_to_db(pool, content, all_api_codes):
    page_inserted = page_updated = page_skipped = 0
    async with pool.acquire() as conn:
        codes_in_page = [i.get("activityCode") for i in content if isinstance(i, dict) and i.get("activityCode")]
        if not codes_in_page:
            return 0, 0, 0
        all_api_codes.update(codes_in_page)
        existing_rows = await conn.fetch(
            "SELECT activity_code, industry_id, name_en, name_ar, description_en "
            "FROM business_activity_codes WHERE activity_code = ANY($1)", codes_in_page
        )
        existing_map = {r["activity_code"]: (r["industry_id"], r["name_en"], r["name_ar"], r["description_en"]) for r in existing_rows}
        for item in content:
            if not (isinstance(item, dict) and item.get("activityCode")):
                continue
            code = item.get("activityCode", "")
            industry_id = str(item.get("isicIndustryId", ""))
            name_en = item.get("nameEn", "") or ""
            name_ar = item.get("nameAr", "") or ""
            description_en = item.get("descriptionEn", "") or ""
            key = (industry_id, name_en, name_ar, description_en)
            if code in existing_map:
                if key != existing_map[code]:
                    await conn.execute(
                        "UPDATE business_activity_codes SET industry_id=$2, name_en=$3, name_ar=$4, description_en=$5, updated_at=NOW() WHERE activity_code=$1",
                        code, industry_id, name_en, name_ar, description_en
                    )
                    page_updated += 1
                else:
                    page_skipped += 1
            else:
                await conn.execute(
                    "INSERT INTO business_activity_codes (activity_code, industry_id, name_en, name_ar, description_en, updated_at) VALUES ($1,$2,$3,$4,$5,NOW())",
                    code, industry_id, name_en, name_ar, description_en
                )
                page_inserted += 1
    return page_inserted, page_updated, page_skipped


async def main():
    print("\n" + "=" * 50)
    print("Qatar Single Window - Fetch Codes 2 (curl)")
    print("=" * 50)
    update_progress("starting", "Initializing...")

    parsed = urlparse(DATABASE_URL)
    db_config = {
        "host": parsed.hostname,
        "port": parsed.port or 5432,
        "user": parsed.username,
        "password": parsed.password,
        "database": parsed.path.lstrip("/"),
    }

    try:
        conn = await asyncpg.connect(**db_config)
        await conn.execute("SELECT 1")
        await conn.close()
    except Exception as e:
        print(f"✗ Database failed: {e}")
        update_progress("error", f"Database: {e}")
        return

    print("✓ Database connected")
    update_progress("running", "Database connected")

    pool = await asyncpg.create_pool(**db_config, min_size=1, max_size=10)
    total_inserted = total_updated = total_skipped = 0
    all_api_codes = set()
    start_time = time.time()

    try:
        # Fetch page 1 to get total
        content, total_pages, total_elements, ok = fetch_page_curl(1)
        if not ok:
            print("✗ Could not reach MOCI API")
            update_progress("error", "Could not reach MOCI API")
            return

        print(f"Page 1... [Total: {total_elements} activities, {total_pages} pages]")
        update_progress("running", f"Fetching 1/{total_pages}...", 1, total_pages, total_elements)

        for page in range(1, total_pages + 1):
            if page > 1:
                content, _, _, ok = fetch_page_curl(page)
                if not ok:
                    update_progress("error", f"Failed page {page}")
                    break
            update_progress("running", f"Page {page}/{total_pages}", page, total_pages, total_elements,
                            total_inserted, total_updated, total_skipped)
            if not content:
                break
            pi, pu, ps = await save_page_to_db(pool, content, all_api_codes)
            total_inserted += pi
            total_updated += pu
            total_skipped += ps
            print(f"  Page {page}: +{pi} new, ~{pu} updated, ={ps} unchanged")

        # Delete stale
        if all_api_codes:
            async with pool.acquire() as conn:
                db_codes = await conn.fetch("SELECT activity_code FROM business_activity_codes")
                stale = set(r["activity_code"] for r in db_codes) - all_api_codes
                if stale:
                    await conn.execute("DELETE FROM business_activity_codes WHERE activity_code = ANY($1)", list(stale))
                    print(f"🗑️ Deleted {len(stale)} stale codes")

        final = await pool.acquire()
        count = await final.fetchval("SELECT COUNT(*) FROM business_activity_codes")
        pool.release(final)
        elapsed = time.time() - start_time
        print(f"\nCOMPLETE! {count} records in {elapsed:.1f}s")
        update_progress("completed", "Fetch completed successfully", 0, 0, count,
                        total_inserted, total_updated, total_skipped)
    finally:
        await pool.close()


if __name__ == "__main__":
    update_progress("starting", "Starting Fetch Codes 2...")
    asyncio.run(main())
