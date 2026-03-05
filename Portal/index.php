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
                <button id="fetchCodes2Btn" class="cursor-pointer uppercase font-bold transition-all p-1.5 sm:p-2 text-xs sm:text-sm border border-yellow-600 text-yellow-500 hover:bg-yellow-500 hover:text-gray-900 disabled:opacity-50 disabled:cursor-not-allowed" title="curl-based fetch">
                    🔄 FETCH_CODES_2
                </button>
                <button id="fetchCodes3Btn" class="cursor-pointer uppercase font-bold transition-all p-1.5 sm:p-2 text-xs sm:text-sm border border-green-600 text-green-500 hover:bg-green-500 hover:text-gray-900 disabled:opacity-50 disabled:cursor-not-allowed" title="Pure PHP fetch (best on VPS)">
                    🔄 FETCH_CODES_3
                </button>
                <button id="scrapeEngBtn" class="cursor-pointer uppercase font-bold transition-all p-1.5 sm:p-2 text-xs sm:text-sm border border-gray-800 text-cyan-400 hover:bg-cyan-400 hover:text-gray-900 disabled:opacity-50 disabled:cursor-not-allowed">
                    📊 SCRAPE_ENG
                </button>
                <button id="scrapeCrBtn" class="cursor-pointer uppercase font-bold transition-all p-1.5 sm:p-2 text-xs sm:text-sm border border-gray-800 text-purple-400 hover:bg-purple-400 hover:text-gray-900 disabled:opacity-50 disabled:cursor-not-allowed">
                    📄 SCRAPE_CR
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

    <!-- CR Scraper Modal -->
    <div id="crModal" class="hidden fixed inset-0 bg-black bg-opacity-80 flex items-center justify-center z-50">
        <div class="bg-gray-900 border-2 border-purple-400 p-6 max-w-lg w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div class="flex justify-between items-center mb-4">
                <h2 class="text-purple-400 text-lg uppercase tracking-wider">📄 SCRAPE_CR - Certificate Download</h2>
                <button id="closeCrModal" class="text-gray-500 hover:text-white text-2xl">&times;</button>
            </div>

            <div class="space-y-4">
                <!-- Search Type Tabs -->
                <div class="flex border border-gray-700">
                    <button data-search-type="cr" class="cr-tab flex-1 p-2 text-sm uppercase font-bold bg-purple-400 text-gray-900 transition-all">CR Number</button>
                    <button data-search-type="en" class="cr-tab flex-1 p-2 text-sm uppercase font-bold text-gray-400 hover:text-white transition-all border-l border-gray-700">EN Name</button>
                    <button data-search-type="ar" class="cr-tab flex-1 p-2 text-sm uppercase font-bold text-gray-400 hover:text-white transition-all border-l border-gray-700">AR Name</button>
                </div>

                <div>
                    <input type="text" id="crSearchInput" placeholder="Enter CR number..." autocomplete="off" dir="ltr"
                           class="w-full bg-gray-900 border border-gray-700 text-purple-400 p-3 text-lg outline-none focus:border-purple-400">
                </div>

                <div class="flex gap-3">
                    <button id="searchCrBtn" class="flex-1 uppercase font-bold transition-all p-3 border border-cyan-400 text-cyan-400 hover:bg-cyan-400 hover:text-gray-900 disabled:opacity-50 disabled:cursor-not-allowed">
                        🔍 SEARCH
                    </button>
                </div>

                <!-- Search Results List (shown when multiple companies found) -->
                <div id="crResultsList" class="hidden">
                    <label class="block text-gray-400 mb-2 text-sm">Select a company:</label>
                    <div id="crResultsContainer" class="max-h-48 overflow-y-auto border border-gray-700 bg-black"></div>
                </div>

                <!-- Selected Company Info -->
                <div id="selectedCompanyInfo" class="hidden border border-green-800 bg-gray-950 p-3">
                    <div class="text-green-400 text-xs uppercase mb-2 font-bold">Selected Company</div>
                    <div id="selectedCompanyDetails" class="text-sm space-y-1"></div>
                </div>

                <div>
                    <label class="block text-gray-400 mb-2">Certificate Type:</label>
                    <select id="certTypeSelect" class="w-full bg-gray-900 border border-gray-700 text-purple-400 p-3 text-base outline-none focus:border-purple-400">
                        <option value="BOTH">CR + CP (Both Certificates)</option>
                        <option value="CR">CR Only (Commercial Registration)</option>
                    </select>
                </div>

                <div class="flex gap-3">
                    <button id="downloadCrBtn" class="flex-1 uppercase font-bold transition-all p-3 border border-purple-400 text-purple-400 hover:bg-purple-400 hover:text-gray-900 disabled:opacity-50 disabled:cursor-not-allowed" disabled>
                        📥 DOWNLOAD PDF
                    </button>
                </div>
            </div>

            <div id="crStatus" class="mt-4 text-sm text-gray-500 hidden">
                <div class="border-t border-gray-700 pt-3">
                    <span id="crStatusText">Ready...</span>
                </div>
            </div>
        </div>
    </div>

    <div class="flex-grow bg-term-bg border border-gray-800 p-2 sm:p-4 overflow-y-auto text-xs sm:text-sm whitespace-pre-wrap relative shadow-[inset_0_0_20px_rgba(0,0,0,0.8)]" id="terminal">
        <div class="mb-1.5 leading-snug"><span class="text-gray-500 mr-2.5">[SYSTEM]</span> Ready for input...</div>
    </div>

    <script>
        const terminal = document.getElementById('terminal');
        const form = document.getElementById('commandForm');
        const codeInput = document.getElementById('codeInput');
        const execBtn = document.getElementById('execBtn');
        const fetchCodesBtn = document.getElementById('fetchCodesBtn');
        const fetchCodes2Btn = document.getElementById('fetchCodes2Btn');
        const fetchCodes3Btn = document.getElementById('fetchCodes3Btn');
        const scrapeEngBtn = document.getElementById('scrapeEngBtn');
        const scrapeCrBtn = document.getElementById('scrapeCrBtn');
        
        // CR Modal elements
        const crModal = document.getElementById('crModal');
        const closeCrModal = document.getElementById('closeCrModal');
        const crSearchInput = document.getElementById('crSearchInput');
        const certTypeSelect = document.getElementById('certTypeSelect');
        const searchCrBtn = document.getElementById('searchCrBtn');
        const downloadCrBtn = document.getElementById('downloadCrBtn');
        const crStatus = document.getElementById('crStatus');
        const crStatusText = document.getElementById('crStatusText');
        const crResultsList = document.getElementById('crResultsList');
        const crResultsContainer = document.getElementById('crResultsContainer');
        const selectedCompanyInfo = document.getElementById('selectedCompanyInfo');
        const selectedCompanyDetails = document.getElementById('selectedCompanyDetails');

        let crSearchType = 'cr'; // 'cr', 'en', 'ar'
        let selectedCompanyCr = null; // CR number of selected company

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
        
        function updateCrStatus(message, isError = false) {
            crStatus.classList.remove('hidden');
            crStatusText.textContent = message;
            crStatusText.className = isError ? 'text-red-400' : 'text-purple-400';
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

        // Fetch Codes 2 - simple: just trigger and monitor (curl-based)
        fetchCodes2Btn.addEventListener('click', async () => {
            fetchCodes2Btn.disabled = true;
            fetchCodes2Btn.textContent = '⏳ FETCHING...';
            log('Initiating FETCH_CODES_2 (curl) — go to URL, fetch all pages...');
            try {
                let r = await fetch('/sw-codes/trigger-fetch-codes2.php');
                let res = await r.json();
                if (!res.success && res.message && res.message.includes('already running')) {
                    log('Fetch Codes 2 already running. Force restarting...', 'info');
                    r = await fetch('/sw-codes/trigger-fetch-codes2.php?force=1');
                    res = await r.json();
                }
                if (!res.success) throw new Error(res.message || 'Failed to start');
                log('✓ Fetch Codes 2 started.', 'success');
                if (res.container_state) log(`State: ${res.container_state}`);
                if (res.container_state === 'exited' && res.log_tail) {
                    res.log_tail.split('\n').forEach(l => { if (l.trim()) log(`  ${l}`, 'error'); });
                }
                await monitorFetchProgress();
            } catch (e) {
                log(`Fetch Codes 2 failed: ${e.message}`, 'error');
            } finally {
                fetchCodes2Btn.disabled = false;
                fetchCodes2Btn.textContent = '🔄 FETCH_CODES_2';
                const sep = document.createElement('div');
                sep.className = 'border-b border-dashed border-gray-800 my-5';
                terminal.appendChild(sep);
                terminal.scrollTop = terminal.scrollHeight;
            }
        });

        fetchCodes3Btn.addEventListener('click', async () => {
            fetchCodes3Btn.disabled = true;
            fetchCodes3Btn.textContent = '⏳ FETCHING...';
            log('Initiating FETCH_CODES_3 (PHP) — pure PHP curl...');
            try {
                let r = await fetch('/sw-codes/trigger-fetch-codes-php.php');
                let res = await r.json();
                if (!res.success && res.message && res.message.includes('already running')) {
                    log('PHP fetch already running. Force restarting...', 'info');
                    r = await fetch('/sw-codes/trigger-fetch-codes-php.php?force=1');
                    res = await r.json();
                }
                if (!res.success) throw new Error(res.message || 'Failed to start');
                log('✓ Fetch Codes 3 (PHP) started.', 'success');
                await monitorFetchProgress();
            } catch (e) {
                log(`Fetch Codes 3 failed: ${e.message}`, 'error');
            } finally {
                fetchCodes3Btn.disabled = false;
                fetchCodes3Btn.textContent = '🔄 FETCH_CODES_3';
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

                            // Detect stuck process: if still "pending" after ~60s, abort
                            if (status === 'pending') {
                                pendingChecks++;
                                if (pendingChecks >= 20) { // 20 × 3s = 60s (slow import on host)
                                    clearInterval(progressInterval);
                                    log('Fetch process did not start within 60s — may have failed.', 'error');
                                    log('Try again or check /tmp/discover_codes.log on the server.', 'error');
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

        // ==========================================
        // SCRAPE_CR - Certificate Download Functions
        // ==========================================

        // Search type tab handling
        document.querySelectorAll('.cr-tab').forEach(tab => {
            tab.addEventListener('click', () => {
                crSearchType = tab.dataset.searchType;
                // Update tab styles
                document.querySelectorAll('.cr-tab').forEach(t => {
                    t.classList.remove('bg-purple-400', 'text-gray-900');
                    t.classList.add('text-gray-400');
                });
                tab.classList.add('bg-purple-400', 'text-gray-900');
                tab.classList.remove('text-gray-400');

                // Update input placeholder and direction
                if (crSearchType === 'cr') {
                    crSearchInput.placeholder = 'Enter CR number...';
                    crSearchInput.dir = 'ltr';
                } else if (crSearchType === 'en') {
                    crSearchInput.placeholder = 'Enter English company name...';
                    crSearchInput.dir = 'ltr';
                } else {
                    crSearchInput.placeholder = 'ادخل اسم الشركة بالعربي...';
                    crSearchInput.dir = 'rtl';
                }
                crSearchInput.focus();
            });
        });

        function selectCompany(company) {
            selectedCompanyCr = company.cr_number;
            selectedCompanyInfo.classList.remove('hidden');
            selectedCompanyDetails.innerHTML = `
                <div class="text-gray-300"><span class="text-gray-500">CR:</span> <span class="text-purple-400">${company.cr_number}</span></div>
                ${company.english_name ? `<div class="text-gray-300"><span class="text-gray-500">EN:</span> ${company.english_name}</div>` : ''}
                ${company.arabic_name ? `<div class="text-gray-300" dir="rtl"><span class="text-gray-500">AR:</span> ${company.arabic_name}</div>` : ''}
                ${company.cp_number ? `<div class="text-gray-300"><span class="text-gray-500">CP:</span> ${company.cp_number}</div>` : ''}
                ${company.status ? `<div class="text-gray-300"><span class="text-gray-500">Status:</span> <span class="${company.status === 'Active' ? 'text-green-400' : 'text-yellow-400'}">${company.status}</span></div>` : ''}
            `;
            downloadCrBtn.disabled = false;
            updateCrStatus(`Selected: ${company.english_name || company.arabic_name || company.cr_number}`);

            // Log to terminal
            log(`[CR] Selected: CR ${company.cr_number} - ${company.english_name || company.arabic_name || 'N/A'}`, 'success');

            // Highlight selected row
            document.querySelectorAll('.cr-result-row').forEach(r => r.classList.remove('bg-purple-900', 'bg-opacity-30'));
            const row = document.querySelector(`.cr-result-row[data-cr="${company.cr_number}"]`);
            if (row) row.classList.add('bg-purple-900', 'bg-opacity-30');
        }

        function renderResults(companies) {
            crResultsContainer.innerHTML = '';

            if (!companies || companies.length === 0) {
                crResultsList.classList.add('hidden');
                updateCrStatus('No companies found', true);
                return;
            }

            // If single result, auto-select it
            if (companies.length === 1) {
                crResultsList.classList.add('hidden');
                selectCompany(companies[0]);
                return;
            }

            // Multiple results - show selection list
            crResultsList.classList.remove('hidden');
            updateCrStatus(`${companies.length} companies found - select one`);

            companies.forEach(company => {
                const row = document.createElement('div');
                row.className = 'cr-result-row p-3 border-b border-gray-800 cursor-pointer hover:bg-purple-900 hover:bg-opacity-20 transition-all';
                row.dataset.cr = company.cr_number;
                row.innerHTML = `
                    <div class="flex justify-between items-start gap-2">
                        <div class="flex-1 min-w-0">
                            <div class="text-purple-400 font-bold text-sm">CR ${company.cr_number}</div>
                            ${company.english_name ? `<div class="text-gray-300 text-xs truncate">${company.english_name}</div>` : ''}
                            ${company.arabic_name ? `<div class="text-gray-400 text-xs truncate" dir="rtl">${company.arabic_name}</div>` : ''}
                        </div>
                        <div class="text-right flex-shrink-0">
                            ${company.status ? `<span class="text-xs ${company.status === 'Active' ? 'text-green-400' : 'text-yellow-400'}">${company.status}</span>` : ''}
                            ${company.cp_number ? `<div class="text-gray-600 text-xs">CP ${company.cp_number}</div>` : ''}
                        </div>
                    </div>
                `;
                row.addEventListener('click', () => selectCompany(company));
                crResultsContainer.appendChild(row);
            });
        }

        // Open CR Modal
        scrapeCrBtn.addEventListener('click', () => {
            crModal.classList.remove('hidden');
            crSearchInput.focus();
            crStatus.classList.add('hidden');
            // Reset selection
            selectedCompanyCr = null;
            selectedCompanyInfo.classList.add('hidden');
            crResultsList.classList.add('hidden');
            downloadCrBtn.disabled = true;
        });

        // Close CR Modal
        closeCrModal.addEventListener('click', () => {
            crModal.classList.add('hidden');
        });

        // Close modal on outside click
        crModal.addEventListener('click', (e) => {
            if (e.target === crModal) {
                crModal.classList.add('hidden');
            }
        });

        // Close modal on Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && !crModal.classList.contains('hidden')) {
                crModal.classList.add('hidden');
            }
        });

        // Search on Enter key
        crSearchInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                searchCrBtn.click();
            }
        });

        // Search CR Button Handler
        searchCrBtn.addEventListener('click', async () => {
            const query = crSearchInput.value.trim();

            if (!query) {
                updateCrStatus('Please enter a search term', true);
                return;
            }

            // Reset previous selection
            selectedCompanyCr = null;
            selectedCompanyInfo.classList.add('hidden');
            crResultsList.classList.add('hidden');
            downloadCrBtn.disabled = true;

            searchCrBtn.disabled = true;
            searchCrBtn.textContent = '⏳ SEARCHING...';
            updateCrStatus('Searching companies...');

            const typeLabel = crSearchType === 'cr' ? 'CR Number' : crSearchType === 'en' ? 'English Name' : 'Arabic Name';
            log(`[CR] Searching by ${typeLabel}: "${query}"...`);

            try {
                // Use ?q= for name searches, ?cr= for exact CR number search
                const isExactCr = crSearchType === 'cr' && /^\d+$/.test(query);
                let companies = [];

                if (isExactCr) {
                    // Try exact CR search first (faster, works for non-user companies)
                    const response = await fetch(`/api-cr/search?cr=${encodeURIComponent(query)}`);
                    if (!response.ok) throw new Error(`HTTP Error: ${response.status}`);
                    const data = await response.json();

                    if (data.status === 'success' && data.data) {
                        companies = [data.data];
                        log('[CR] Company found via CR lookup!', 'success');
                    }
                }

                // Also do a query search (finds multiple matches, searches by name)
                const qResponse = await fetch(`/api-cr/search?q=${encodeURIComponent(query)}`);
                if (qResponse.ok) {
                    const qData = await qResponse.json();
                    if (qData.status === 'success' && qData.companies) {
                        // Merge results, dedup by CR
                        const seenCrs = new Set(companies.map(c => c.cr_number));
                        for (const c of qData.companies) {
                            if (!seenCrs.has(c.cr_number)) {
                                seenCrs.add(c.cr_number);
                                companies.push(c);
                            }
                        }
                        if (qData.count > 0) {
                            log(`[CR] Found ${qData.count} result(s) from establishments`, 'success');
                        }
                    }
                }

                if (companies.length === 0) {
                    log('[CR] No companies found', 'error');
                    updateCrStatus('No companies found', true);
                } else {
                    log(`[CR] Total: ${companies.length} company(ies) found`);
                    // Log each result to terminal
                    companies.forEach(c => {
                        log(`[CR]   CR ${c.cr_number} | ${c.english_name || 'N/A'} | ${c.arabic_name || 'N/A'} | ${c.status || 'N/A'}`);
                    });
                    renderResults(companies);
                }

            } catch (error) {
                log(`[CR] Search failed: ${error.message}`, 'error');
                updateCrStatus(`Error: ${error.message}`, true);
            } finally {
                searchCrBtn.disabled = false;
                searchCrBtn.textContent = '🔍 SEARCH';

                const sep = document.createElement('div');
                sep.className = 'border-b border-dashed border-gray-800 my-5';
                terminal.appendChild(sep);
            }
        });

        // Download CR Button Handler
        downloadCrBtn.addEventListener('click', async () => {
            const crNumber = selectedCompanyCr;
            const certType = certTypeSelect.value;

            if (!crNumber) {
                updateCrStatus('Please search and select a company first', true);
                return;
            }

            downloadCrBtn.disabled = true;
            downloadCrBtn.textContent = '⏳ DOWNLOADING...';
            updateCrStatus(`Downloading ${certType} certificate(s)...`);

            const certLabel = certType === 'BOTH' ? 'CR + CP' : certType;
            log(`[CR] Downloading ${certLabel} certificate for CR: ${crNumber}...`);

            try {
                const response = await fetch(`/api-cr/download?cr=${crNumber}&type=${certType}&format=base64`);

                if (!response.ok) {
                    throw new Error(`HTTP Error: ${response.status}`);
                }

                const data = await response.json();

                if (data.status === 'success' && data.files) {
                    log(`[CR] Downloaded ${data.count} file(s)!`, 'success');

                    for (const [filename, base64Data] of Object.entries(data.files)) {
                        const byteCharacters = atob(base64Data);
                        const byteNumbers = new Array(byteCharacters.length);
                        for (let i = 0; i < byteCharacters.length; i++) {
                            byteNumbers[i] = byteCharacters.charCodeAt(i);
                        }
                        const byteArray = new Uint8Array(byteNumbers);
                        const blob = new Blob([byteArray], { type: 'application/pdf' });

                        const url = window.URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = filename;
                        document.body.appendChild(a);
                        a.click();
                        window.URL.revokeObjectURL(url);
                        document.body.removeChild(a);

                        log(`[CR] Downloaded: ${filename}`, 'success');
                    }

                    updateCrStatus(`Downloaded ${data.count} file(s) successfully!`);

                } else {
                    throw new Error(data.message || 'Download failed');
                }

            } catch (error) {
                log(`[CR] Download failed: ${error.message}`, 'error');
                updateCrStatus(`Error: ${error.message}`, true);
            } finally {
                downloadCrBtn.disabled = false;
                downloadCrBtn.textContent = '📥 DOWNLOAD PDF';

                const sep = document.createElement('div');
                sep.className = 'border-b border-dashed border-gray-800 my-5';
                terminal.appendChild(sep);
            }
        });

        // Initial focus
        codeInput.focus();
    </script>
</body>
</html>
