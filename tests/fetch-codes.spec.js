// @ts-check
const { test, expect } = require('@playwright/test');

// Full fetch of ~29 pages can take 5+ minutes
const FETCH_TIMEOUT_MS = 420000; // 7 min

test.describe('Fetch Codes', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('#terminal')).toBeVisible();
  });

  test('FETCH_CODES_2 completes without error', async ({ page }) => {
    const fetchBtn = page.locator('#fetchCodes2Btn');
    const terminal = page.locator('#terminal');

    await fetchBtn.click();
    await expect(fetchBtn).toBeDisabled({ timeout: 5000 });

    await expect(fetchBtn).toBeEnabled({ timeout: FETCH_TIMEOUT_MS });
    await expect(fetchBtn).toContainText('FETCH_CODES_2');

    const terminalText = await terminal.textContent();
    const hasFatal =
      /\[ERROR\].*may have failed/.test(terminalText) ||
      /\[ERROR\].*fetch failed/i.test(terminalText);
    expect(hasFatal, `Fatal error in terminal: ${terminalText.slice(-600)}`).toBe(false);

    const hasSuccess =
      terminalText.includes('FETCH COMPLETED') ||
      terminalText.includes('Already up to date') ||
      terminalText.includes('completed');
    expect(hasSuccess, `Expected success in terminal: ${terminalText.slice(-600)}`).toBeTruthy();
  });

  test('FETCH_CODES_3 (PHP) completes without error', async ({ page }) => {
    const fetchBtn = page.locator('#fetchCodes3Btn');
    const terminal = page.locator('#terminal');

    await fetchBtn.click();
    await expect(fetchBtn).toBeDisabled({ timeout: 5000 });
    await expect(fetchBtn).toBeEnabled({ timeout: FETCH_TIMEOUT_MS });
    await expect(fetchBtn).toContainText('FETCH_CODES_3');

    const terminalText = await terminal.textContent();
    const hasFatal = /\[ERROR\].*may have failed/.test(terminalText) || /\[ERROR\].*fetch failed/i.test(terminalText);
    expect(hasFatal, `Fatal error: ${terminalText.slice(-600)}`).toBe(false);
    const hasSuccess = terminalText.includes('FETCH COMPLETED') || terminalText.includes('Already up to date') || terminalText.includes('completed');
    expect(hasSuccess, `Expected success: ${terminalText.slice(-600)}`).toBeTruthy();
  });

  test('FETCH_CODES completes without error', async ({ page }) => {
    const fetchBtn = page.locator('#fetchCodesBtn');
    const terminal = page.locator('#terminal');

    await fetchBtn.click();
    await expect(fetchBtn).toBeDisabled({ timeout: 5000 });

    await expect(fetchBtn).toBeEnabled({ timeout: FETCH_TIMEOUT_MS });
    await expect(fetchBtn).toContainText('FETCH_CODES');

    const terminalText = await terminal.textContent();
    const hasFatal =
      /\[ERROR\].*may have failed/.test(terminalText) ||
      /\[ERROR\].*fetch failed/i.test(terminalText);
    expect(hasFatal, `Fatal error in terminal: ${terminalText.slice(-600)}`).toBe(false);

    const hasSuccess =
      terminalText.includes('FETCH COMPLETED') ||
      terminalText.includes('Already up to date') ||
      terminalText.includes('No fetch required') ||
      terminalText.includes('Database is already up to date');
    expect(hasSuccess, `Expected success in terminal: ${terminalText.slice(-600)}`).toBeTruthy();
  });
});
