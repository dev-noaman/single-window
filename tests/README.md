# E2E Tests (Playwright)

Tests the Portal fetch codes flows against the live site (noaman.cloud).

## Run

```bash
cd tests
npm install
npx playwright install chromium
npx playwright test
```

## Known Issue

Both FETCH_CODES and FETCH_CODES_3 require the VPS to reach `investor.sw.gov.qa` (MOCI API). If tests fail with "Could not reach MOCI API", check:

- VPS outbound HTTPS (443) is allowed
- No IP/geo blocking of the VPS by the target
- DNS resolution from VPS: `curl -v https://investor.sw.gov.qa`
