<?php
// index.php - Portal Endpoint
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Terminal Access | Data Extraction</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    colors: {
                        'term-bg': '#000000',
                        'term-text': '#cccccc',
                        'term-accent': '#33ff00',
                        'term-error': '#ff3333',
                    },
                    fontFamily: {
                        mono: ['"Courier New"', 'Courier', 'monospace'],
                    }
                }
            }
        }
    </script>
    <style type="text/tailwindcss">
        @layer utilities {
            .json-key { @apply text-cyan-400; }
            .json-string { @apply text-green-400; }
            .json-number { @apply text-purple-400; }
            .json-boolean { @apply text-blue-400; }
            
            .cursor-blink {
                animation: blink 1s infinite;
            }
            
            @keyframes blink {
                0%, 100% { opacity: 1; }
                50% { opacity: 0; }
            }
        }
    </style>
</head>
<body class="bg-gray-900 text-term-text font-mono h-screen flex flex-col p-3 sm:p-5 overflow-hidden">

    <header class="mb-3 sm:mb-5 border-b border-gray-800 pb-2.5">
        <div class="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-3 mb-3">
            <div class="text-lg sm:text-xl uppercase tracking-widest text-term-accent">> SYSTEM_ACCESS</div>
            <div class="grid grid-cols-2 sm:flex gap-2 sm:gap-3">
                <button id="fetchCodesBtn" class="cursor-pointer uppercase font-bold transition-all p-1.5 sm:p-2 text-xs sm:text-sm border border-gray-800 text-yellow-400 hover:bg-yellow-400 hover:text-gray-900 disabled:opacity-50 disabled:cursor-not-allowed">
                    🔄 FETCH_CODES
                </button>
                <button id="scrapeEngBtn" class="cursor-pointer uppercase font-bold transition-all p-1.5 sm:p-2 text-xs sm:text-sm border border-gray-800 text-cyan-400 hover:bg-cyan-400 hover:text-gray-900 disabled:opacity-50 disabled:cursor-not-allowed">
                    📊 SCRAPE_ENG
                </button>
                <a href="/officernd" class="cursor-pointer uppercase font-bold transition-all p-1.5 sm:p-2 text-xs sm:text-sm border border-gray-800 text-orange-400 hover:bg-orange-400 hover:text-gray-900 no-underline text-center">
                    OfficeRnD
                </a>
            </div>
        </div>
        <form id="commandForm" class="flex flex-col sm:flex-row gap-2 sm:gap-4 sm:items-center">
            <div class="flex gap-2 sm:gap-4 items-center flex-1">
                <span class="text-sm sm:text-base">CODE:</span>
                <input type="text" id="codeInput" placeholder="013001" autocomplete="off" required pattern="[0-9]+" class="bg-gray-900 border border-gray-800 text-term-accent p-2 text-sm sm:text-base outline-none focus:border-term-accent flex-1 min-w-0">
                <button type="submit" id="execBtn" class="cursor-pointer uppercase font-bold transition-all p-2 text-sm sm:text-base border border-gray-800 text-term-accent hover:bg-term-accent hover:text-gray-900 disabled:opacity-50 disabled:cursor-not-allowed whitespace-nowrap">EXECUTE</button>
            </div>
        </form>
    </header>

    <div class="flex-grow bg-term-bg border border-gray-800 p-2 sm:p-4 overflow-y-auto text-xs sm:text-sm whitespace-pre-wrap relative shadow-[inset_0_0_20px_rgba(0,0,0,0.8)]" id="terminal">
        <div class="mb-1.5 leading-snug"><span class="text-gray-500 mr-2.5">[SYSTEM]</span> Ready for input...</div>
    </div>

    <script>
        const terminal = document.getElementById('terminal');
        const form = document.getElementById('commandForm');
        const codeInput = document.getElementById('codeInput');
        const execBtn = document.getElementById('execBtn');
        const fetchCodesBtn = document.getElementById('fetchCodesBtn');
        const scrapeEngBtn = document.getElementById('scrapeEngBtn');

        function log(message, type = 'info') {
            const line = document.createElement('div');
            line.className = 'mb-1.5 leading-snug';
            
            const time = new Date().toLocaleTimeString('en-US', { hour12: false });
            let prompt = '';
            
            if (type === 'error') {
                prompt = '<span class="text-term-error">[ERROR]</span>';
            } else if (type === 'success') {
                prompt = '<span class="text-term-accent">[SUCCESS]</span>';
            } else {
                prompt = '<span class="text-gray-500 mr-2.5">[' + time + ']</span>';
            }
            
            line.innerHTML = `${prompt} ${message}`;
            terminal.appendChild(line);
            terminal.scrollTop = terminal.scrollHeight;
            
            // Add a subtle flash effect for new logs
            line.style.opacity = '0';
            line.style.transform = 'translateX(-10px)';
            setTimeout(() => {
                line.style.transition = 'all 0.3s ease';
                line.style.opacity = '1';
                line.style.transform = 'translateX(0)';
            }, 10);
        }

        function syntaxHighlight(json) {
            if (typeof json !== 'string') {
                json = JSON.stringify(json, undefined, 2);
            }
            json = json.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
            return json.replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g, function (match) {
                let cls = 'json-number';
                if (/^"/.test(match)) {
                    if (/:$/.test(match)) {
                        cls = 'json-key';
                    } else {
                        cls = 'json-string';
                    }
                } else if (/true|false/.test(match)) {
                    cls = 'json-boolean';
                } else if (/null/.test(match)) {
                    cls = 'json-boolean'; // Using same color for null
                }
                return '<span class="' + cls + '">' + match + '</span>';
            });
        }
        
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const code = codeInput.value.trim();
            
            if (!code) {
                log('Activity code is required.', 'error');
                return;
            }

            // Disable UI
            codeInput.disabled = true;
            execBtn.disabled = true;

            // Use relative URL through nginx reverse proxy
            const endpoint = `/api-scraper/scrape?code=${code}`;

            log(`Initiating sequence for Code: ${code}...`);
            log(`Connecting to endpoint: ${window.location.origin}${endpoint}`);

            try {
                const startTime = performance.now();
                const response = await fetch(endpoint);
                
                if (!response.ok) {
                    throw new Error(`HTTP Error: ${response.status}`);
                }

                const data = await response.text(); // Get text first to handle non-JSON responses
                
                const duration = ((performance.now() - startTime) / 1000).toFixed(2);
                log(`Process completed in ${duration}s. Parsing output...`);

                try {
                    const jsonData = JSON.parse(data);
                    log('Data received successfully:', 'success');
                    
                    const pre = document.createElement('pre');
                    pre.style.color = '#ddd';
                    pre.innerHTML = syntaxHighlight(jsonData);
                    terminal.appendChild(pre);

                } catch (e) {
                    log('Output received (Non-JSON format):', 'info');
                    const pre = document.createElement('pre');
                    pre.textContent = data;
                    terminal.appendChild(pre);
                }

            } catch (error) {
                log(`Execution failed: ${error.message}`, 'error');
            } finally {
                // Re-enable UI
                codeInput.disabled = false;
                execBtn.disabled = false;
                codeInput.focus();
                terminal.scrollTop = terminal.scrollHeight;
                
                // Add a separator
                const sep = document.createElement('div');
                sep.className = 'border-b border-dashed border-gray-800 my-5';
                terminal.appendChild(sep);
            }
        });

        // Fetch Codes Button Handler
        fetchCodesBtn.addEventListener('click', async () => {
            // Disable button
            fetchCodesBtn.disabled = true;
            fetchCodesBtn.textContent = '⏳ CHECKING...';

            log('Initiating SW_CODES fetch sequence...');
            log('Step 1: Checking MOCI API for total codes...');

            try {
                // Step 1: Check for updates
                const checkResponse = await fetch('/sw-codes/check-update.php');
                
                if (!checkResponse.ok) {
                    throw new Error(`HTTP Error: ${checkResponse.status}`);
                }

                const checkData = await checkResponse.json();
                
                if (!checkData.success) {
                    throw new Error(checkData.message || 'Failed to check for updates');
                }

                // Display comparison
                log(`MOCI API Total: ${checkData.api_total} codes`);
                log(`Database Total: ${checkData.db_total} codes`);
                log(`Difference: ${checkData.difference} codes`);
                log(`Last Update: ${checkData.last_update || 'Never'}`);
                
                if (!checkData.needs_update) {
                    log('✓ Database is already up to date!', 'success');
                    log('No fetch required. All codes are current.');
                    fetchCodesBtn.disabled = false;
                    fetchCodesBtn.textContent = '🔄 FETCH_CODES';
                    
                    const sep = document.createElement('div');
                    sep.className = 'border-b border-dashed border-gray-800 my-5';
                    terminal.appendChild(sep);
                    terminal.scrollTop = terminal.scrollHeight;
                    return;
                }

                // Step 2: Update needed - start fetch
                const diff = Math.abs(checkData.difference);
                const action = checkData.difference > 0 ? 'new codes to fetch' : 'codes to update';
                log(`⚠ Update required: ${diff} ${action}`, 'info');
                log('Step 2: Starting fetch process...');
                
                fetchCodesBtn.textContent = '⏳ FETCHING...';

                // Trigger fetch (retry with force=1 if already running)
                let fetchResponse = await fetch('/sw-codes/trigger-fetch-codes.php');
                let fetchResult = await fetchResponse.json();

                if (!fetchResult.success && fetchResult.message && fetchResult.message.includes('already running')) {
                    log('Fetch already in progress. Force restarting...', 'info');
                    fetchResponse = await fetch('/sw-codes/trigger-fetch-codes.php?force=1');
                    fetchResult = await fetchResponse.json();
                }

                if (!fetchResponse.ok) {
                    throw new Error(fetchResult.message || `HTTP Error: ${fetchResponse.status}`);
                }
                
                if (!fetchResult.success) {
                    throw new Error(fetchResult.message || 'Failed to start fetch');
                }

                log('✓ Fetch process started successfully!', 'success');

                // Show container diagnostics if available
                if (fetchResult.container_state) {
                    log(`Container state: ${fetchResult.container_state}`);
                }
                if (fetchResult.container_state === 'exited' && fetchResult.log_tail) {
                    log('⚠ Container exited immediately. Last logs:', 'error');
                    fetchResult.log_tail.split('\n').forEach(line => {
                        if (line.trim()) log(`  ${line}`, 'error');
                    });
                    throw new Error('Container crashed on startup — see logs above');
                }

                log('Step 3: Monitoring progress...');
                
                // Step 3: Monitor progress in real-time
                await monitorFetchProgress();

            } catch (error) {
                log(`SW_CODES fetch failed: ${error.message}`, 'error');
            } finally {
                // Re-enable button
                fetchCodesBtn.disabled = false;
                fetchCodesBtn.textContent = '🔄 FETCH_CODES';
                
                // Add separator
                const sep = document.createElement('div');
                sep.className = 'border-b border-dashed border-gray-800 my-5';
                terminal.appendChild(sep);
                terminal.scrollTop = terminal.scrollHeight;
            }
        });

        // Monitor fetch progress in real-time
        async function monitorFetchProgress() {
            let checkCount = 0;
            const maxChecks = 600; // 600 checks * 3 seconds = 30 minutes max (enough for large fetches)
            let lastPageShown = 0; // Track last page we displayed
            let seenRunning = false; // Guard: don't accept "completed" until we've seen the fetch actually start
            let pendingChecks = 0; // Count consecutive "pending" polls to detect a stuck container

            return new Promise((resolve) => {
                const progressInterval = setInterval(async () => {
                    checkCount++;

                    try {
                        // Use new progress endpoint for real-time updates
                        const progressResponse = await fetch('/sw-codes/progress.php');

                        if (!progressResponse.ok) {
                            throw new Error(`Progress check failed: ${progressResponse.status}`);
                        }

                        const progressData = await progressResponse.json();

                        if (progressData.success) {
                            const status = progressData.status;
                            const currentPage = progressData.current_page || 0;
                            const totalPages = progressData.total_pages || 0;
                            const newInserted = progressData.new_inserted || 0;
                            const updated = progressData.updated || 0;

                            // Track when the fetch has actually started running
                            if (status === 'running' || status === 'starting') {
                                seenRunning = true;
                                pendingChecks = 0;
                            }

                            // Detect stuck process: if still "pending" after ~2 min, abort
                            if (status === 'pending') {
                                pendingChecks++;
                                if (pendingChecks >= 40) { // 40 × 3s = 120s (PHP startup on loaded host)
                                    clearInterval(progressInterval);
                                    log('Fetch process did not start within 60s — may have failed.', 'error');
                                    log('Try again or check /tmp/discover_codes_php.log (PHP fetch) or /tmp/discover_codes.log on the server.', 'error');
                                    resolve();
                                    return;
                                }
                            }

                            // Show page progress (only new pages)
                            if (currentPage > lastPageShown && currentPage > 0) {
                                const changes = [];
                                if (newInserted > 0) changes.push(`+${newInserted} new`);
                                if (updated > 0) changes.push(`~${updated} updated`);

                                const changeText = changes.length > 0 ? `, ${changes.join(', ')}` : '';
                                log(`Page ${currentPage}/${totalPages}${changeText}`);
                                lastPageShown = currentPage;
                            }

                            // Only accept "completed" after we've seen the fetch actually running.
                            // This prevents reading a stale "completed" from the previous run.
                            if (status === 'completed' && seenRunning) {
                                clearInterval(progressInterval);
                                
                                // Show completion summary
                                const sep1 = document.createElement('div');
                                sep1.className = 'border-t-2 border-term-accent my-3';
                                terminal.appendChild(sep1);
                                
                                log('FETCH COMPLETED SUCCESSFULLY!', 'success');
                                log('═══════════════════════════════════════', 'success');
                                log(`📊 Total Records:  ${progressData.total_records || 0}`, 'success');
                                log(`➕ New Inserted:   +${newInserted}`, 'success');
                                log(`🔄 Updated:        ~${updated}`, 'success');
                                log('═══════════════════════════════════════', 'success');
                                
                                const sep2 = document.createElement('div');
                                sep2.className = 'border-t-2 border-term-accent my-3';
                                terminal.appendChild(sep2);
                                
                                resolve();
                            } else if (status === 'error') {
                                clearInterval(progressInterval);
                                log('Fetch process encountered an error', 'error');
                                log(progressData.message || 'Unknown error', 'error');
                                resolve();
                            }
                        }

                        // Safety timeout
                        if (checkCount >= maxChecks) {
                            clearInterval(progressInterval);
                            log('Monitoring timeout reached (30 minutes)', 'error');
                            log('Fetch may still be running. Check status manually.', 'error');
                            resolve();
                        }

                    } catch (error) {
                        console.error('Progress monitoring error:', error);
                        // Don't stop on individual check errors, keep trying
                    }
                }, 3000); // Check every 3 seconds
            });
        }

        // Scrape ENG Button Handler
        scrapeEngBtn.addEventListener('click', async () => {
            await handleScrapeClick('en', scrapeEngBtn);
        });

        // Generic scrape handler for GSheet scrapers
        async function handleScrapeClick(language, button) {
            // Disable button
            button.disabled = true;
            const originalText = button.textContent;
            button.textContent = '⏳ STARTING...';

            const langLabel = language.toUpperCase();
            log(`Initiating ${langLabel} scraper sequence...`);
            log(`Step 1: Triggering ${langLabel} scraper...`);

            try {
                // Call trigger endpoint
                const triggerEndpoint = `/gsheet-scraper/trigger-scrape-${language}.php`;
                const triggerResponse = await fetch(triggerEndpoint);
                
                if (!triggerResponse.ok) {
                    throw new Error(`HTTP Error: ${triggerResponse.status}`);
                }

                const triggerData = await triggerResponse.json();
                
                if (!triggerData.success) {
                    throw new Error(triggerData.message || 'Failed to start scraper');
                }

                log(`✓ ${langLabel} scraper started successfully!`, 'success');
                log('Step 2: Monitoring progress...');
                
                button.textContent = '⏳ SCRAPING...';

                // Monitor progress
                await monitorScrapeProgress(language);

            } catch (error) {
                log(`${langLabel} scraper failed: ${error.message}`, 'error');
            } finally {
                // Re-enable button
                button.disabled = false;
                button.textContent = originalText;
                
                // Add separator
                const sep = document.createElement('div');
                sep.className = 'border-b border-dashed border-gray-800 my-5';
                terminal.appendChild(sep);
                terminal.scrollTop = terminal.scrollHeight;
            }
        }

        // Monitor scrape progress in real-time
        async function monitorScrapeProgress(language) {
            let checkCount = 0;
            const maxChecks = 600; // 600 checks * 3 seconds = 30 minutes max
            let lastRowShown = 0; // Track last row we displayed

            return new Promise((resolve) => {
                const progressInterval = setInterval(async () => {
                    checkCount++;

                    try {
                        // Poll progress endpoint
                        const progressEndpoint = `/gsheet-scraper/progress-${language}.php`;
                        const progressResponse = await fetch(progressEndpoint);
                        
                        if (!progressResponse.ok) {
                            throw new Error(`Progress check failed: ${progressResponse.status}`);
                        }

                        const progressData = await progressResponse.json();

                        if (progressData.success) {
                            const status = progressData.status;
                            const currentRow = progressData.current_row || 0;
                            const totalRows = progressData.total_rows || 0;

                            // Show row progress (only new rows)
                            if (currentRow > lastRowShown && currentRow > 0 && totalRows > 0) {
                                log(`Processing row ${currentRow}/${totalRows}`);
                                lastRowShown = currentRow;
                            }

                            // Check if completed
                            if (status === 'completed') {
                                clearInterval(progressInterval);
                                
                                // Calculate elapsed time
                                const elapsedTime = progressData.elapsed_time || 0;
                                const minutes = Math.floor(elapsedTime / 60);
                                const seconds = Math.floor(elapsedTime % 60);
                                const timeStr = minutes > 0 
                                    ? `${minutes}m ${seconds}s` 
                                    : `${seconds}s`;
                                
                                // Show completion summary
                                const sep1 = document.createElement('div');
                                sep1.className = 'border-t-2 border-term-accent my-3';
                                terminal.appendChild(sep1);
                                
                                log('SCRAPING COMPLETED SUCCESSFULLY!', 'success');
                                log('═══════════════════════════════════════', 'success');
                                log(`📊 Total Rows Processed: ${progressData.rows_processed || totalRows}`, 'success');
                                log(`⏱️  Elapsed Time: ${timeStr}`, 'success');
                                log(`✓ ${progressData.message || 'Scraping completed'}`, 'success');
                                log('═══════════════════════════════════════', 'success');
                                
                                const sep2 = document.createElement('div');
                                sep2.className = 'border-t-2 border-term-accent my-3';
                                terminal.appendChild(sep2);
                                
                                resolve();
                            } else if (status === 'error') {
                                clearInterval(progressInterval);
                                log('Scraper encountered an error', 'error');
                                log(progressData.message || 'Unknown error', 'error');
                                resolve();
                            } else if (status === 'idle') {
                                // No active scrape process yet, keep waiting
                                if (checkCount > 10) {
                                    // After 30 seconds of idle, something might be wrong
                                    log('Warning: No active scrape process detected', 'error');
                                }
                            }
                        }

                        // Safety timeout
                        if (checkCount >= maxChecks) {
                            clearInterval(progressInterval);
                            log('Monitoring timeout reached (30 minutes)', 'error');
                            log('Scraper may still be running. Check status manually.', 'error');
                            resolve();
                        }

                    } catch (error) {
                        console.error('Progress monitoring error:', error);
                        // Don't stop on individual check errors, keep trying
                    }
                }, 3000); // Check every 3 seconds
            });
        }

        // Initial focus
        codeInput.focus();
    </script>
</body>
</html>
