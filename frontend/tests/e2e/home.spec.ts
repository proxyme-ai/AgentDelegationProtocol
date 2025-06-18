import { test, expect } from '@playwright/test';

test('landing page has Start Demo text', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByText('Start Demo')).toBeVisible();
});
