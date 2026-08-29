const fs = require('fs');
const { pathToFileURL } = require('url');
const { chromium } = require('playwright');

async function main() {
  const [htmlPath, timeoutText, screenshotPath] = process.argv.slice(2);
  const timeoutMs = Number(timeoutText || 15000);
  const source = fs.readFileSync(htmlPath, 'utf8');
  const expectsECharts = /\becharts\.init\s*\(/.test(source);
  const consoleErrors = [];
  const pageErrors = [];
  const failedRequests = [];
  const externalRequests = [];
  const launchOptions = { headless: true };
  if (process.env.ECHART_SMOKE_BROWSER) {
    launchOptions.executablePath = process.env.ECHART_SMOKE_BROWSER;
  }
  const browser = await chromium.launch(launchOptions);
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
  page.setDefaultTimeout(timeoutMs);
  page.on('console', message => {
    if (message.type() === 'error') consoleErrors.push(message.text());
  });
  page.on('pageerror', error => pageErrors.push(String(error)));
  page.on('requestfailed', request => failedRequests.push(`${request.method()} ${request.url()}`));
  page.on('request', request => {
    if (/^https?:\/\//i.test(request.url())) externalRequests.push(request.url());
  });

  let navigationError = null;
  try {
    await page.goto(pathToFileURL(htmlPath).href, { waitUntil: 'load', timeout: timeoutMs });
    if (expectsECharts) {
      await page.waitForFunction(() => document.querySelectorAll('[_echarts_instance_]').length > 0);
    }
  } catch (error) {
    navigationError = String(error);
  }

  const runtime = await page.evaluate(() => {
    const chartRoots = Array.from(document.querySelectorAll('[_echarts_instance_]'));
    const rendered = chartRoots.map(root => {
      const surface = root.querySelector('canvas,svg');
      const rect = root.getBoundingClientRect();
      const surfaceRect = surface ? surface.getBoundingClientRect() : null;
      return {
        id: root.id || root.getAttribute('_echarts_instance_') || '(unnamed)',
        hasSurface: Boolean(surface),
        width: Math.round(rect.width),
        height: Math.round(rect.height),
        surfaceWidth: surfaceRect ? Math.round(surfaceRect.width) : 0,
        surfaceHeight: surfaceRect ? Math.round(surfaceRect.height) : 0,
      };
    });
    return {
      readyState: document.readyState,
      chartCount: chartRoots.length,
      rendered,
      canvasCount: document.querySelectorAll('canvas').length,
      svgCount: document.querySelectorAll('svg').length,
      bodyWidth: document.body ? document.body.scrollWidth : 0,
      bodyHeight: document.body ? document.body.scrollHeight : 0,
      viewportWidth: window.innerWidth,
      loadMs: Math.round(performance.getEntriesByType('navigation')[0]?.duration || 0),
    };
  });

  if (screenshotPath) await page.screenshot({ path: screenshotPath, fullPage: true });
  await browser.close();

  const errors = [];
  if (navigationError) errors.push(`navigation failed: ${navigationError}`);
  errors.push(...pageErrors.map(value => `pageerror: ${value}`));
  errors.push(...consoleErrors.map(value => `console error: ${value}`));
  errors.push(...failedRequests.map(value => `request failed: ${value}`));
  errors.push(...externalRequests.map(value => `external request: ${value}`));
  if (expectsECharts && runtime.chartCount === 0) errors.push('no live ECharts instance was created');
  for (const chart of runtime.rendered) {
    if (!chart.hasSurface) errors.push(`chart ${chart.id} has no canvas/svg surface`);
    if (chart.width <= 0 || chart.height <= 0) errors.push(`chart ${chart.id} has zero-sized container`);
    if (chart.surfaceWidth <= 0 || chart.surfaceHeight <= 0) errors.push(`chart ${chart.id} has zero-sized render surface`);
  }
  if (runtime.bodyWidth > runtime.viewportWidth + 20) {
    errors.push(`page horizontally overflows viewport (${runtime.bodyWidth}px > ${runtime.viewportWidth}px)`);
  }
  if (runtime.loadMs > 8000) errors.push(`page load took ${runtime.loadMs}ms (> 8000ms)`);

  process.stdout.write(JSON.stringify({ ok: errors.length === 0, errors, runtime }, null, 2));
  process.exitCode = errors.length === 0 ? 0 : 1;
}

main().catch(error => {
  process.stdout.write(JSON.stringify({ ok: false, errors: [String(error)], runtime: null }, null, 2));
  process.exitCode = 1;
});
