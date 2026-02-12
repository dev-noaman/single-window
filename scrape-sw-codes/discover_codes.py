import asyncio
import json
import os
import time
import aiohttp
import asyncpg
from urllib.parse import urlparse

# API endpoint for ALL activities (no industry filter)
ALL_ACTIVITIES_URL = "https://investor.sw.gov.qa/wps/portal/investors/information-center/ba/search-results/!ut/p/z1/04_Sj9CPykssy0xPLMnMz0vMAfIjo8zivfxNXA393Q38Dbz9LA3MAt38_UyNDQ0MAk30w_EqcDTVjyJJv0VomJFBoLOTaZCju4Wxv6MhcfoNcABHA8L6o_AqAfkAVYG_r4uTgZmjqWeoo0uQobuvOboCLH4AK8DjyODEIv2C3NDQCINMT11HRUUAe2qoOw!!/dz/d5/L2dBISEvZ0FBIS9nQSEh/p0/IZ7_JO4E1OG0O0KN906QFON5310013=CZ6_JO4E1OG0O0KN906QFON53100Q4=NJbaSearchResource=/?"

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


def update_progress(status, message, current_page=0, total_pages=0, total_records=0, new_inserted=0, updated=0):
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


async def fetch_all_activities(session: aiohttp.ClientSession, pool):
    """Fetch all activities with pagination and save to database."""
    page = 1
    total_inserted = 0
    total_updated = 0
    total_pages = 1
    consecutive_no_changes = 0  # Track pages with no changes
    
    while True:
        url = f"{ALL_ACTIVITIES_URL}page={page}&size={PAGE_SIZE}"
        
        try:
            update_progress("running", f"Fetching page {page}...", page, total_pages, 0, total_inserted, total_updated)
            
            async with session.get(url, headers=HEADERS, timeout=aiohttp.ClientTimeout(total=TIMEOUT_SECONDS), ssl=False) as resp:
                if resp.status == 200:
                    text = await resp.text()
                    data = json.loads(text)
                    
                    # Navigate: data.activities.content
                    content = []
                    total_elements = 0
                    if isinstance(data, dict) and 'data' in data:
                        inner = data['data']
                        if isinstance(inner, dict) and 'activities' in inner:
                            act_data = inner['activities']
                            content = act_data.get('content', [])
                            total_pages = act_data.get('totalPages', 1)
                            total_elements = act_data.get('totalElements', 0)
                    
                    if page == 1:
                        print(f"Page 1... [Total: {total_elements} activities, {total_pages} pages]")
                        update_progress("running", f"Processing {total_elements} activities across {total_pages} pages", 1, total_pages, total_elements, 0, 0)
                    
                    if not content:
                        print("No more data")
                        break
                    
                    # Save to database - OPTIMIZED BATCH INSERT
                    page_inserted = 0
                    page_updated = 0
                    
                    async with pool.acquire() as conn:
                        # Get existing codes in this batch for comparison
                        codes_in_page = [item.get('activityCode') for item in content if isinstance(item, dict) and item.get('activityCode')]
                        
                        if codes_in_page:
                            # Check which codes already exist
                            existing_rows = await conn.fetch(
                                "SELECT activity_code FROM business_activity_codes WHERE activity_code = ANY($1)",
                                codes_in_page
                            )
                            existing_codes = set(row['activity_code'] for row in existing_rows)
                            
                            # Prepare batch data
                            for item in content:
                                if isinstance(item, dict) and item.get('activityCode'):
                                    code = item.get('activityCode', '')
                                    industry_id = str(item.get('isicIndustryId', ''))
                                    name_en = item.get('nameEn', '')
                                    name_ar = item.get('nameAr', '')
                                    description_en = item.get('descriptionEn', '')
                                    
                                    if code in existing_codes:
                                        # Update existing record
                                        await conn.execute("""
                                            UPDATE business_activity_codes 
                                            SET industry_id = $2, name_en = $3, name_ar = $4, 
                                                description_en = $5, updated_at = NOW()
                                            WHERE activity_code = $1
                                        """, code, industry_id, name_en, name_ar, description_en)
                                        page_updated += 1
                                    else:
                                        # Insert new record
                                        await conn.execute("""
                                            INSERT INTO business_activity_codes 
                                            (activity_code, industry_id, name_en, name_ar, description_en, updated_at)
                                            VALUES ($1, $2, $3, $4, $5, NOW())
                                        """, code, industry_id, name_en, name_ar, description_en)
                                        page_inserted += 1
                    
                    total_inserted += page_inserted
                    total_updated += page_updated
                    
                    # Status
                    parts = []
                    if page_inserted > 0:
                        parts.append(f"+{page_inserted} new")
                    if page_updated > 0:
                        parts.append(f"~{page_updated} updated")
                    
                    status = f", {', '.join(parts)}" if parts else " (no changes)"
                    print(f"  Page {page}: {len(content)} items{status}")
                    
                    # Update progress in real-time
                    update_progress("running", f"Page {page} completed", page, total_pages, total_elements, total_inserted, total_updated)
                    
                    # Smart skip: If no changes on this page, increment counter
                    if page_inserted == 0 and page_updated == 0:
                        consecutive_no_changes += 1
                        
                        # If 3 consecutive pages with no changes, assume rest is unchanged
                        if consecutive_no_changes >= 3:
                            remaining_pages = total_pages - page
                            if remaining_pages > 0:
                                print(f"\n⚡ Smart Skip: {consecutive_no_changes} consecutive pages with no changes")
                                print(f"   Skipping remaining {remaining_pages} pages (assumed unchanged)")
                                update_progress("running", f"Smart skip: {remaining_pages} pages assumed unchanged", page, total_pages, total_elements, total_inserted, total_updated)
                            break
                    else:
                        # Reset counter if we found changes
                        consecutive_no_changes = 0
                    
                    # Next page?
                    if page >= total_pages:
                        break
                    page += 1
                else:
                    print(f"HTTP {resp.status}")
                    update_progress("error", f"HTTP {resp.status}")
                    break
        except Exception as e:
            print(f"Error: {type(e).__name__}: {e}")
            update_progress("error", f"Error: {type(e).__name__}: {e}")
            break
    
    return total_inserted, total_updated


async def main():
    """Fetch all business activity codes and save to PostgreSQL database."""
    
    print("\n" + "=" * 50)
    print("Qatar Single Window - Business Activity Codes")
    print("=" * 50)
    print()
    
    update_progress("starting", "Initializing...")
    
    # Parse database configuration
    db_config = parse_postgres_url(DATABASE_URL)
    
    # Wait for database
    if not await wait_for_db(db_config):
        print("\n✗ Failed to connect to database")
        update_progress("error", "Failed to connect to database")
        return
    
    # Create connection pool
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
        # Get existing count
        existing_count = await get_existing_count(pool)
        if existing_count > 0:
            print(f"Database has {existing_count} existing records")
        print()
        
        start_time = time.time()
        
        # Fetch and save data
        connector = aiohttp.TCPConnector(limit=3)
        async with aiohttp.ClientSession(connector=connector) as session:
            total_inserted, total_updated = await fetch_all_activities(session, pool)
        
        # Get final count
        final_count = await get_existing_count(pool)
        elapsed = time.time() - start_time
        
        print(f"\n{'='*50}")
        print(f"COMPLETE!")
        print(f"{'='*50}")
        print(f"\n📊 SUMMARY")
        print(f"   Total records:  {final_count}")
        print(f"   New inserted:   +{total_inserted}")
        print(f"   Updated:        ~{total_updated}")
        print(f"\n⏱️  ELAPSED TIME: {elapsed:.1f} seconds")
        print(f"{'='*50}")
        
        update_progress("completed", "Fetch completed successfully", 0, 0, final_count, total_inserted, total_updated)
        
    finally:
        await pool.close()


if __name__ == "__main__":
    asyncio.run(main())
