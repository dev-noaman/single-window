import asyncio
import json
import os
import time
import aiohttp
import asyncpg
from urllib.parse import urlparse

# API endpoint for ALL activities (no industry filter)
ALL_ACTIVITIES_URL = "https://investor.sw.gov.qa/wps/portal/investors/information-center/ba/search-results/!ut/p/z1/04_Sj9CPykssy0xPLMnMz0vMAfIjo8zivfxNXA393Q38Dbz9LA3MAt38_UyNDQ0MAk30w_EqcDTVjyJJv0VomJFBoLOTaZCju4Wxv6MhcfoNcABHA8L6o_AqAfkAVYG_r4uTgZmjqWeuo0uQobuvOboCLH4AK8DjyODEIv2C3NDQCINMT11HRUUAe2qoOw!!/dz/d5/L2dBISEvZ0FBIS9nQSEh/p0/IZ7_JO4E1OG0O0KN906QFON5310013=CZ6_JO4E1OG0O0KN906QFON53100Q4=NJbaSearchResource=/?"

# Settings
PAGE_SIZE = 100
TIMEOUT_SECONDS = 120
PROGRESS_FILE = "/tmp/fetch_progress.json"

# Headers to mimic browser
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
}

# Database configuration from environment
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://codesuser:StrongPasswordHere@db:5432/codesdb")


def update_progress(status, message, current_page=0, total_pages=0, total_records=0, new_inserted=0, updated=0, skipped=0):
    """Update progress file for real-time monitoring."""
    try:
        progress = {
            "status": status,
            "message": message,
            "current_page": current_page,
            "total_pages": total_pages,
            "total_records": total_records,
            "new_inserted": new_inserted,
            "updated": updated,
            "skipped": skipped,
            "timestamp": time.time()
        }
        with open(PROGRESS_FILE, 'w') as f:
            json.dump(progress, f)
    except Exception as e:
        print(f"Failed to update progress: {e}")


def parse_postgres_url(url):
    """Parse PostgreSQL connection URL into components."""
    parsed = urlparse(url)
    return {
        "host": parsed.hostname,
        "port": parsed.port or 5432,
        "user": parsed.username,
        "password": parsed.password,
        "database": parsed.path.lstrip("/")
    }


async def wait_for_db(db_config, max_retries=30):
    """Wait for database to be ready."""
    for retry in range(1, max_retries + 1):
        try:
            conn = await asyncpg.connect(**db_config)
            await conn.execute("SELECT 1")
            await conn.close()
            print(f"✓ Database connected")
            update_progress("running", "Database connected")
            return True
        except Exception as e:
            if retry < max_retries:
                print(f"  Waiting for database... ({retry}/{max_retries})")
                await asyncio.sleep(2)
            else:
                print(f"✗ Database connection failed: {e}")
                update_progress("error", f"Database connection failed: {e}")
                return False
    return False


async def get_existing_count(pool):
    """Get count of existing records in database."""
    async with pool.acquire() as conn:
        result = await conn.fetchval("SELECT COUNT(*) FROM business_activity_codes")
        return result or 0


async def fetch_single_page(session, page_num):
    """Fetch one page from the API.
    Returns (content, total_pages, total_elements, success).
    On any error: ([], 1, 0, False).
    """
    url = f"{ALL_ACTIVITIES_URL}page={page_num}&size={PAGE_SIZE}"
    try:
        async with session.get(url, headers=HEADERS, timeout=aiohttp.ClientTimeout(total=TIMEOUT_SECONDS), ssl=False) as resp:
            if resp.status != 200:
                print(f"HTTP {resp.status} on page {page_num}")
                return [], 1, 0, False
            text = await resp.text()
            if not text or not text.strip():
                print(f"Empty response on page {page_num} (Content-Type: {resp.content_type})")
                return [], 1, 0, False
            try:
                data = json.loads(text)
            except json.JSONDecodeError:
                preview = text[:300].replace('\n', ' ')
                print(f"Non-JSON response on page {page_num} (Content-Type: {resp.content_type}): {preview}")
                return [], 1, 0, False
            content = []
            total_pages = 1
            total_elements = 0
            if isinstance(data, dict) and 'data' in data:
                inner = data['data']
                if isinstance(inner, dict) and 'activities' in inner:
                    act_data = inner['activities']
                    content = act_data.get('content', [])
                    total_pages = act_data.get('totalPages', 1)
                    total_elements = act_data.get('totalElements', 0)
            return content, total_pages, total_elements, True
    except Exception as e:
        print(f"Error fetching page {page_num}: {type(e).__name__}: {e}")
        return [], 1, 0, False


async def save_page_to_db(pool, content, all_api_codes):
    """Save a page of content to DB with change detection.
    Updates all_api_codes in-place.
    Returns (inserted, updated, skipped).
    """
    page_inserted = 0
    page_updated = 0
    page_skipped = 0

    async with pool.acquire() as conn:
        codes_in_page = [
            item.get('activityCode') for item in content
            if isinstance(item, dict) and item.get('activityCode')
        ]

        if not codes_in_page:
            return 0, 0, 0

        all_api_codes.update(codes_in_page)

        existing_rows = await conn.fetch(
            "SELECT activity_code, industry_id, name_en, name_ar, description_en "
            "FROM business_activity_codes WHERE activity_code = ANY($1)",
            codes_in_page
        )
        existing_map = {
            row['activity_code']: (row['industry_id'], row['name_en'], row['name_ar'], row['description_en'])
            for row in existing_rows
        }

        for item in content:
            if isinstance(item, dict) and item.get('activityCode'):
                code = item.get('activityCode', '')
                industry_id = str(item.get('isicIndustryId', ''))
                name_en = item.get('nameEn', '')
                name_ar = item.get('nameAr', '')
                description_en = item.get('descriptionEn', '')

                if code in existing_map:
                    old = existing_map[code]
                    if (industry_id, name_en, name_ar, description_en) != old:
                        await conn.execute("""
                            UPDATE business_activity_codes
                            SET industry_id = $2, name_en = $3, name_ar = $4,
                                description_en = $5, updated_at = NOW()
                            WHERE activity_code = $1
                        """, code, industry_id, name_en, name_ar, description_en)
                        page_updated += 1
                    else:
                        page_skipped += 1
                else:
                    await conn.execute("""
                        INSERT INTO business_activity_codes
                        (activity_code, industry_id, name_en, name_ar, description_en, updated_at)
                        VALUES ($1, $2, $3, $4, $5, NOW())
                    """, code, industry_id, name_en, name_ar, description_en)
                    page_inserted += 1

    return page_inserted, page_updated, page_skipped


async def fetch_all_activities(session, pool, disable_smart_skip=False):
    """Fetch all activities with pagination and save to database.

    disable_smart_skip: Set True when we know new codes exist but they were not
    on the last page (they could be anywhere), so we must scan every page.

    Returns (total_inserted, total_updated, total_skipped, all_api_codes, fetch_complete).
    """
    page = 1
    total_inserted = 0
    total_updated = 0
    total_skipped = 0
    total_pages = 1
    total_elements = 0
    consecutive_no_changes = 0
    all_api_codes = set()
    fetch_complete = False

    while True:
        update_progress("running", f"Fetching page {page}...", page, total_pages, total_elements, total_inserted, total_updated)

        content, total_pages, total_elements, ok = await fetch_single_page(session, page)

        if not ok:
            update_progress("error", f"Failed to fetch page {page}")
            break

        if page == 1:
            print(f"Page 1... [Total: {total_elements} activities, {total_pages} pages]")
            update_progress("running", f"Processing {total_elements} activities across {total_pages} pages", 1, total_pages, total_elements, 0, 0)

        if not content:
            print("No more data")
            break

        page_inserted, page_updated, page_skipped = await save_page_to_db(pool, content, all_api_codes)

        total_inserted += page_inserted
        total_updated += page_updated
        total_skipped += page_skipped

        parts = []
        if page_inserted > 0:
            parts.append(f"+{page_inserted} new")
        if page_updated > 0:
            parts.append(f"~{page_updated} updated")
        if page_skipped > 0:
            parts.append(f"={page_skipped} unchanged")
        status_str = f", {', '.join(parts)}" if parts else " (no changes)"
        print(f"  Page {page}: {len(content)} items{status_str}")

        update_progress("running", f"Page {page} completed", page, total_pages, total_elements, total_inserted, total_updated, total_skipped)

        if not disable_smart_skip:
            if page_inserted == 0 and page_updated == 0:
                consecutive_no_changes += 1
                if consecutive_no_changes >= 3:
                    remaining_pages = total_pages - page
                    if remaining_pages > 0:
                        print(f"\n⚡ Smart Skip: {consecutive_no_changes} consecutive pages with no changes")
                        print(f"   Skipping remaining {remaining_pages} pages (assumed unchanged)")
                        update_progress("running", f"Smart skip: {remaining_pages} pages assumed unchanged", page, total_pages, total_elements, total_inserted, total_updated)
                    break
            else:
                consecutive_no_changes = 0

        if page >= total_pages:
            fetch_complete = True
            break
        page += 1

    return total_inserted, total_updated, total_skipped, all_api_codes, fetch_complete


async def main():
    """Fetch all business activity codes and save to PostgreSQL database."""

    print("\n" + "=" * 50)
    print("Qatar Single Window - Business Activity Codes")
    print("=" * 50)
    print()

    update_progress("starting", "Initializing...")

    db_config = parse_postgres_url(DATABASE_URL)

    if not await wait_for_db(db_config):
        print("\n✗ Failed to connect to database")
        update_progress("error", "Failed to connect to database")
        return

    pool = await asyncpg.create_pool(
        host=db_config["host"],
        port=db_config["port"],
        user=db_config["user"],
        password=db_config["password"],
        database=db_config["database"],
        min_size=1,
        max_size=10
    )

    try:
        existing_count = await get_existing_count(pool)
        if existing_count > 0:
            print(f"Database has {existing_count} existing records")
        print()

        start_time = time.time()
        total_inserted = 0
        total_updated = 0
        total_skipped = 0
        total_deleted = 0
        all_api_codes = set()
        fetch_complete = False

        connector = aiohttp.TCPConnector(limit=3)
        async with aiohttp.ClientSession(connector=connector) as session:

            # Peek at API metadata (page 1) to compare counts before committing to a full fetch
            _, total_pages, total_elements, ok = await fetch_single_page(session, 1)

            if ok and total_elements > existing_count and total_pages > 0:
                # API has more codes than DB — check the last page first.
                # New codes are typically appended to the end, so this is usually a 1-page fix.
                diff = total_elements - existing_count
                print(f"API has {total_elements} codes, DB has {existing_count} (+{diff} new) — checking last page first...")
                update_progress("running", f"API has more codes (+{diff}), checking last page (page {total_pages})...", 0, total_pages, total_elements)

                last_content, _, _, last_ok = await fetch_single_page(session, total_pages)

                if last_ok and last_content:
                    last_page_codes = [
                        item.get('activityCode') for item in last_content
                        if isinstance(item, dict) and item.get('activityCode')
                    ]
                    async with pool.acquire() as conn:
                        existing_rows = await conn.fetch(
                            "SELECT activity_code FROM business_activity_codes WHERE activity_code = ANY($1)",
                            last_page_codes
                        )
                        existing_set = set(row['activity_code'] for row in existing_rows)
                        new_on_last_page = sum(1 for c in last_page_codes if c not in existing_set)

                    if new_on_last_page > 0:
                        # Fast path: new codes are on the last page — save just that page
                        print(f"✓ Found {new_on_last_page} new code(s) on last page — fast sync!")
                        update_progress("running", f"Fast sync: saving {new_on_last_page} new codes from last page", total_pages, total_pages, total_elements)
                        total_inserted, total_updated, total_skipped = await save_page_to_db(pool, last_content, all_api_codes)
                        # fetch_complete stays False — partial fetch, skip stale deletion
                    else:
                        # New codes are NOT on the last page (inserted in the middle).
                        # Full fetch required; disable smart skip so we don't miss them.
                        print(f"  No new codes on last page — full fetch (codes inserted in the middle)...")
                        update_progress("running", "Falling back to full fetch (no smart skip)...", 0, total_pages, total_elements)
                        total_inserted, total_updated, total_skipped, all_api_codes, fetch_complete = await fetch_all_activities(
                            session, pool, disable_smart_skip=True
                        )
                else:
                    # Could not load last page — fall back to full fetch
                    print(f"  Could not load last page — falling back to full fetch...")
                    total_inserted, total_updated, total_skipped, all_api_codes, fetch_complete = await fetch_all_activities(session, pool)
            elif not ok:
                # API metadata fetch failed — cannot determine strategy.
                # Log the error and abort (don't blindly do a full fetch that will also fail).
                print("✗ Could not reach MOCI API — aborting fetch")
                update_progress("error", "Could not reach MOCI API (see container logs for details)")
            elif total_elements < existing_count:
                # API has FEWER codes than DB — some codes were removed from the API.
                # Must fetch every page (no smart skip) to build the complete API code set,
                # then delete whatever is in DB but no longer in the API.
                diff = existing_count - total_elements
                print(f"API has {total_elements} codes, DB has {existing_count} (-{diff} removed) — full fetch to find deleted codes...")
                update_progress("running", f"API has fewer codes (-{diff}), full fetch to detect deletions...", 0, total_pages, total_elements)
                total_inserted, total_updated, total_skipped, all_api_codes, fetch_complete = await fetch_all_activities(
                    session, pool, disable_smart_skip=True
                )
            else:
                # Counts are equal — check for data changes only. Smart skip is safe here.
                total_inserted, total_updated, total_skipped, all_api_codes, fetch_complete = await fetch_all_activities(session, pool)

        # Delete codes that no longer exist in the API (only when ALL pages were fetched)
        if all_api_codes and fetch_complete:
            async with pool.acquire() as conn:
                db_codes = await conn.fetch("SELECT activity_code FROM business_activity_codes")
                db_code_set = set(row['activity_code'] for row in db_codes)
                stale_codes = db_code_set - all_api_codes
                if stale_codes:
                    stale_list = list(stale_codes)
                    await conn.execute(
                        "DELETE FROM business_activity_codes WHERE activity_code = ANY($1)",
                        stale_list
                    )
                    total_deleted = len(stale_list)
                    print(f"\n🗑️  Deleted {total_deleted} stale codes: {', '.join(stale_list[:10])}{'...' if len(stale_list) > 10 else ''}")

        final_count = await get_existing_count(pool)
        elapsed = time.time() - start_time

        print(f"\n{'='*50}")
        print(f"COMPLETE!")
        print(f"{'='*50}")
        print(f"\n📊 SUMMARY")
        print(f"   Total records:  {final_count}")
        print(f"   New inserted:   +{total_inserted}")
        print(f"   Updated:        ~{total_updated}")
        print(f"   Unchanged:      ={total_skipped}")
        if total_deleted > 0:
            print(f"   Deleted:        -{total_deleted}")
        print(f"\n⏱️  ELAPSED TIME: {elapsed:.1f} seconds")
        print(f"{'='*50}")

        update_progress("completed", "Fetch completed successfully", 0, 0, final_count, total_inserted, total_updated, total_skipped)

    finally:
        await pool.close()


if __name__ == "__main__":
    asyncio.run(main())
