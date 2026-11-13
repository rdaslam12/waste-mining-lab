import fs from "node:fs";
import path from "node:path";
import { chromium } from "playwright";

const output = process.env.VISUAL_DIR || "/tmp/wml-visual-comparison";
const origins = [
  { name: "live", url: (process.env.LIVE_URL || "https://waste-mining-lab.onrender.com").replace(/\/$/, "") },
  { name: "static", url: (process.env.PREVIEW_URL || "http://127.0.0.1:8080").replace(/\/$/, "") },
];
const defaultRoutes = ["/", "/publications/", "/research/", "/grants/", "/team/", "/activity/", "/news/", "/waste-monitoring/", "/contact/"];
const routes = process.env.VISUAL_ROUTES?.split(",").map((route) => route.trim()).filter(Boolean) || defaultRoutes;
const defaultViewports = [
  { name: "1440", width: 1440, height: 1000 },
  { name: "1024", width: 1024, height: 900 },
  { name: "768", width: 768, height: 1024 },
  { name: "390", width: 390, height: 844 },
  { name: "375", width: 375, height: 812 },
];
const selectedViewports = process.env.VISUAL_VIEWPORTS?.split(",").map((name) => name.trim()).filter(Boolean);
const viewports = selectedViewports?.length
  ? defaultViewports.filter((viewport) => selectedViewports.includes(viewport.name))
  : defaultViewports;
const report = [];
fs.mkdirSync(output, { recursive: true });
const browser = await chromium.launch({ headless: true });

async function gotoWithRetry(page, url) {
  let response;
  for (let attempt = 1; attempt <= 3; attempt += 1) {
    response = await page.goto(url, { waitUntil: "networkidle", timeout: 120_000 });
    if (response?.status() !== 503) return response;
    await page.waitForTimeout(attempt * 2500);
  }
  return response;
}

try {
  for (const origin of origins) {
    for (const viewport of viewports) {
      const context = await browser.newContext({ viewport: { width: viewport.width, height: viewport.height }, reducedMotion: "reduce" });
      for (const route of routes) {
        const page = await context.newPage();
        const errors = [];
        page.on("console", (message) => { if (message.type() === "error") errors.push(message.text()); });
        const response = await gotoWithRetry(page, `${origin.url}${route}`);
        await page.evaluate(() => document.fonts.ready);
        const metrics = await page.evaluate(() => {
          const header = document.querySelector(".wml-global-header")?.getBoundingClientRect();
          const main = document.querySelector("main")?.getBoundingClientRect();
          const h1 = document.querySelector("h1")?.getBoundingClientRect();
          const bodyStyle = getComputedStyle(document.body);
          return {
            viewportWidth: window.innerWidth,
            scrollWidth: document.documentElement.scrollWidth,
            pageHeight: document.documentElement.scrollHeight,
            headerHeight: header?.height || 0,
            mainWidth: main?.width || 0,
            h1Height: h1?.height || 0,
            fontFamily: bodyStyle.fontFamily,
            backgroundColor: bodyStyle.backgroundColor,
          };
        });
        const slug = route === "/" ? "home" : route.replaceAll("/", "");
        const file = path.join(output, `${origin.name}-${slug}-${viewport.name}.png`);
        await page.screenshot({ path: file, fullPage: viewport.width === 1440 || viewport.width === 390, animations: "disabled" });
        report.push({ origin: origin.name, route, viewport: viewport.name, status: response?.status(), errors, screenshot: file, ...metrics });
        await page.close();
        if (origin.name === "live") await new Promise((resolve) => setTimeout(resolve, 750));
      }
      await context.close();
    }
  }
} finally {
  await browser.close();
}

fs.writeFileSync(path.join(output, "report.json"), `${JSON.stringify(report, null, 2)}\n`);
const failures = report.filter((item) => item.status !== 200 || item.errors.length || item.scrollWidth > item.viewportWidth + 1);
if (failures.length) {
  console.error(JSON.stringify(failures, null, 2));
  process.exit(1);
}
console.log(`Captured and checked ${report.length} live/static route-viewport renders in ${output}.`);
