import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { chromium } from "playwright";

const baseUrl = (process.env.PREVIEW_URL || "http://127.0.0.1:8080").replace(/\/$/, "");
const screenshotDir = process.env.SCREENSHOT_DIR;
const routes = ["/", "/publications/", "/research/", "/grants/", "/team/", "/activity/", "/news/", "/waste-monitoring/", "/contact/"];
const viewports = [
  { name: "desktop-1440", width: 1440, height: 1000 },
  { name: "desktop-1024", width: 1024, height: 900 },
  { name: "tablet-768", width: 768, height: 1024 },
  { name: "mobile-390", width: 390, height: 844 },
  { name: "mobile-375", width: 375, height: 812 },
];
const results = [];
const browser = await chromium.launch({ headless: true });

try {
  if (screenshotDir) fs.mkdirSync(screenshotDir, { recursive: true });
  for (const viewport of viewports) {
    const context = await browser.newContext({ viewport: { width: viewport.width, height: viewport.height }, reducedMotion: "reduce" });
    for (const route of routes) {
      const page = await context.newPage();
      const consoleErrors = [];
      const requestFailures = [];
      page.on("console", (message) => { if (message.type() === "error") consoleErrors.push(message.text()); });
      page.on("requestfailed", (request) => { if (request.url().startsWith(baseUrl)) requestFailures.push(`${request.url()}: ${request.failure()?.errorText}`); });
      const response = await page.goto(`${baseUrl}${route}`, { waitUntil: "networkidle", timeout: 90_000 });
      assert.ok(response?.ok(), `${viewport.name} ${route}: HTTP ${response?.status()}`);
      await page.evaluate(() => document.fonts.ready);
      const layout = await page.evaluate(() => ({
        viewport: window.innerWidth,
        scrollWidth: document.documentElement.scrollWidth,
        title: document.title,
        h1: document.querySelector("h1")?.textContent?.trim() || "",
      }));
      assert.ok(layout.scrollWidth <= layout.viewport + 1, `${viewport.name} ${route}: horizontal overflow ${layout.scrollWidth} > ${layout.viewport}`);
      assert.deepEqual(consoleErrors, [], `${viewport.name} ${route}: console errors`);
      assert.deepEqual(requestFailures, [], `${viewport.name} ${route}: failed internal requests`);
      if (screenshotDir) {
        const slug = route === "/" ? "home" : route.replaceAll("/", "");
        await page.screenshot({ path: path.join(screenshotDir, `${slug}-${viewport.name}.png`), fullPage: viewport.width === 1440 || viewport.width === 390, animations: "disabled" });
      }
      results.push({ viewport: viewport.name, route, ...layout });
      await page.close();
    }
    await context.close();
  }

  const interactionContext = await browser.newContext({ viewport: { width: 390, height: 844 }, reducedMotion: "reduce" });
  const interactionPage = await interactionContext.newPage();
  await interactionPage.goto(`${baseUrl}/`, { waitUntil: "networkidle" });
  await interactionPage.click(".wml-hamburger-btn");
  assert.equal(await interactionPage.getAttribute(".wml-hamburger-btn", "aria-expanded"), "true");
  assert.equal(await interactionPage.getAttribute("#wml-mobile-drawer", "aria-hidden"), "false");

  await interactionPage.goto(`${baseUrl}/publications/`, { waitUntil: "networkidle" });
  assert.equal(await interactionPage.locator("[data-publication]:visible").count(), 9);
  await interactionPage.fill("#publication-search", "Clostridium");
  await interactionPage.waitForTimeout(300);
  assert.ok(await interactionPage.locator("[data-publication]:visible").count() >= 1);
  assert.match(await interactionPage.locator("#publication-search-status").textContent(), /publication/);
  await interactionPage.click("[data-clear-publications]");
  await interactionPage.selectOption("#publication-year", "2026");
  assert.ok(await interactionPage.locator("[data-publication]:visible").count() >= 1);

  await interactionPage.goto(`${baseUrl}/news/`, { waitUntil: "networkidle" });
  await interactionPage.click(".news-filter-disclosure > summary");
  await interactionPage.selectOption("#news-category", "research");
  assert.equal(await interactionPage.locator("[data-news-card]:visible").count(), 1);

  const bibResponse = await interactionPage.request.get(`${baseUrl}/downloads/bibtex/publication-1.bib`);
  assert.ok(bibResponse.ok());
  assert.match(await bibResponse.text(), /^@article\{/);
  await interactionContext.close();
} finally {
  await browser.close();
}

console.log(`Browser QA passed for ${results.length} route/viewport combinations plus mobile navigation, filters, and BibTeX interactions.`);
