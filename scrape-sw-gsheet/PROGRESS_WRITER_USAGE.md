# Progress Writer Module Usage Guide

## Overview

The `progress_writer` module provides a simple interface for writing progress updates to JSON files that can be monitored by the Portal interface in real-time.

## Requirements Satisfied

- **5.3**: Write progress updates to `/tmp/scrape_progress_en.json`
- **5.4**: Write progress updates to `/tmp/scrape_progress_ar.json`
- **6.1**: Progress data in JSON format
- **6.2**: Include "status" field with values: "running", "completed", or "error"
- **6.3**: Include "current_row" field
- **6.4**: Include "total_rows" field
- **6.5**: Include "message" field
- **6.6**: Include "rows_processed" field on completion

## Basic Usage

### Import the Module

```python
from progress_writer import write_progress
```

### Starting a Scraper

```python
# At the beginning of your scraper
write_progress(
    language='en',
    status='running',
    current_row=0,
    total_rows=100,
    message='Starting EN scraper...',
    rows_processed=0
)
```

### Processing Rows

```python
# After processing each row
for idx, code in enumerate(codes, start=1):
    # ... process the code ...
    
    write_progress(
        language='en',
        status='running',
        current_row=idx,
        total_rows=len(codes),
        message=f'Processing row {idx}/{len(codes)}',
        rows_processed=0
    )
```

### Successful Completion

```python
# When scraper completes successfully
write_progress(
    language='en',
    status='completed',
    current_row=total_rows,
    total_rows=total_rows,
    message='Scraping completed successfully',
    rows_processed=successful_count
)
```

### Error Handling

```python
# When an error occurs
try:
    # ... scraper logic ...
except Exception as e:
    write_progress(
        language='en',
        status='error',
        current_row=current_idx,
        total_rows=total_rows,
        message=str(e),
        rows_processed=0
    )
```

## Integration Example

Here's a complete example of integrating the progress writer into a scraper:

```python
from progress_writer import write_progress

async def run_scraper(language='en'):
    try:
        # Get codes to process
        codes = get_codes_from_sheet()
        total_rows = len(codes)
        successful_count = 0
        
        # Write initial progress
        write_progress(
            language=language,
            status='running',
            current_row=0,
            total_rows=total_rows,
            message=f'Starting {language.upper()} scraper...'
        )
        
        # Process each code
        for idx, code in enumerate(codes, start=1):
            # Update progress
            write_progress(
                language=language,
                status='running',
                current_row=idx,
                total_rows=total_rows,
                message=f'Processing row {idx}/{total_rows}'
            )
            
            # Process the code
            success = await process_code(code)
            if success:
                successful_count += 1
        
        # Write completion progress
        write_progress(
            language=language,
            status='completed',
            current_row=total_rows,
            total_rows=total_rows,
            message='Scraping completed successfully',
            rows_processed=successful_count
        )
        
    except Exception as e:
        # Write error progress
        write_progress(
            language=language,
            status='error',
            current_row=idx if 'idx' in locals() else 0,
            total_rows=total_rows if 'total_rows' in locals() else 0,
            message=str(e)
        )
        raise
```

## Progress File Format

The progress files are written in JSON format with the following structure:

```json
{
  "status": "running",
  "current_row": 5,
  "total_rows": 100,
  "message": "Processing row 5/100",
  "timestamp": 1769273680,
  "rows_processed": 0
}
```

### Field Descriptions

- **status**: Current status - one of: `"running"`, `"completed"`, or `"error"`
- **current_row**: The row currently being processed (1-based index)
- **total_rows**: Total number of rows to process
- **message**: Human-readable status message or error description
- **timestamp**: Unix timestamp (seconds since epoch) when progress was written
- **rows_processed**: Number of rows successfully processed (most relevant on completion)

## File Locations

- **English scraper**: `/tmp/scrape_progress_en.json`
- **Arabic scraper**: `/tmp/scrape_progress_ar.json`

These files are read by the Portal's progress monitoring endpoints:
- `/gsheet-scraper/progress-en.php`
- `/gsheet-scraper/progress-ar.php`

## Error Handling

The `write_progress()` function handles write errors gracefully. If it cannot write to the progress file (e.g., due to permissions), it will print a warning to the console but will not crash the scraper.

## Testing

Run the unit tests to verify the module works correctly:

```bash
python -m pytest test_progress_writer.py -v
```

All tests should pass, verifying that:
- Progress files are created correctly
- All required fields are present
- Status values are valid
- EN and AR files are independent
- Error handling works properly
