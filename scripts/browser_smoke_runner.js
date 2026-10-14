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
    await page.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));
  } catch (error) {
    navigationError = String(error);
  }

  const runtime = await page.evaluate(() => {
    const chartRoots = Array.from(document.querySelectorAll('[_echarts_instance_]'));
    const rendered = chartRoots.map(root => {
      const surface = root.querySelector('canvas,svg');
      const rect = root.getBoundingClientRect();
      const surfaceRect = surface ? surface.getBoundingClientRect() : null;
      const instance = window.echarts?.getInstanceByDom?.(root);
      const liveOption = instance?.getOption?.();
      return {
        id: root.id || root.getAttribute('_echarts_instance_') || '(unnamed)',
        hasSurface: Boolean(surface),
        hasLiveSeries: Boolean(instance?.getZr?.() && liveOption?.series?.length),
        width: Math.round(rect.width),
        height: Math.round(rect.height),
        surfaceWidth: surfaceRect ? Math.round(surfaceRect.width) : 0,
        surfaceHeight: surfaceRect ? Math.round(surfaceRect.height) : 0,
      };
    });
    const declared = Array.from(document.querySelectorAll('[data-echart-chart],.chart-surface'));
    const missingCharts = declared.filter(root => !root.hasAttribute('_echarts_instance_')).map(root => root.id || '(unnamed)');
    const reconciliationErrors = [];
    const compiled = document.getElementById('chart-build-spec');
    if (compiled) {
      const configs = JSON.parse(compiled.textContent);
      for (const config of configs) {
        const root = document.getElementById(config.id);
        const instance = root && window.echarts?.getInstanceByDom(root);
        if (!instance) { reconciliationErrors.push(`missing expected chart ${config.id}`); continue; }
        const actual = instance.getOption();
        if (actual.series.length !== config.option.series.length) reconciliationErrors.push(`${config.id}: series count differs`);
        config.option.series.forEach((series, index) => {
          const live = actual.series[index];
          if (!live || live.type !== series.type || live.name !== series.name || JSON.stringify(live.data) !== JSON.stringify(series.data))
            reconciliationErrors.push(`${config.id}: series ${index} type/data differs`);
          if (series.yAxisIndex !== undefined && live?.yAxisIndex !== series.yAxisIndex)
            reconciliationErrors.push(`${config.id}: series ${index} axis differs`);
          for (const key of ['stack', 'connectNulls', 'smooth']) {
            if (series[key] !== undefined && series[key] !== live?.[key])
              reconciliationErrors.push(`${config.id}: series ${index} ${key} differs`);
          }
        });
        for (const key of ['xAxis', 'yAxis']) {
          const expected = config.option[key];
          if (!expected) continue;
          (Array.isArray(expected) ? expected : [expected]).forEach((axis, i) => {
            if (axis.data && JSON.stringify(axis.data) !== JSON.stringify(actual[key]?.[i]?.data))
              reconciliationErrors.push(`${config.id}: ${key} categories differ`);
            if (axis.name && axis.name !== actual[key]?.[i]?.name)
              reconciliationErrors.push(`${config.id}: ${key} unit/name differs`);
          });
        }
        const table = document.querySelector(`[data-chart-table="${config.id}"] table`);
        const input = config.input;
        const series = config.option.series;
        const categoryAxis = ['bar','stacked_bar'].includes(input.view) ? config.option.yAxis : config.option.xAxis;
        const rows = series[0].data.map((_, i) => [
          input.view === 'scatter' ? series[0].data[i][0] : input.view === 'pie' ? series[0].data[i].name : categoryAxis.data[i],
          ...series.map(s => input.view === 'scatter' ? s.data[i][1] : input.view === 'pie' ? s.data[i].value : s.data[i])
        ]);
        const visibleRows = table ? Array.from(table.querySelectorAll('tbody tr'), tr => Array.from(tr.querySelectorAll('td'), (td, i) => {
          if (i === 0 && input.view !== 'scatter') return td.textContent;
          return td.textContent === '—' ? null : td.textContent.trim() === '' ? 'EMPTY' : Number(td.textContent);
        })) : [];
        if (JSON.stringify(rows) !== JSON.stringify(visibleRows)) reconciliationErrors.push(`${config.id}: source table differs`);
        const headings = table ? Array.from(table.querySelectorAll('thead th'), th => th.textContent) : [];
        if (JSON.stringify(headings) !== JSON.stringify([input.x, ...input.metrics.map(m => m.field)]))
          reconciliationErrors.push(`${config.id}: source table headings differ`);
        const svg = root.querySelector('svg');
        if (!svg || !svg.querySelector('path,rect,circle,text')) reconciliationErrors.push(`${config.id}: empty SVG`);
      }
    }
    return {
      missingCharts,
      reconciliationErrors,
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

  // Verify resize, not only the initial desktop snapshot.
  await page.setViewportSize({width: 390, height: 844});
  await page.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));
  runtime.mobileOverflow = await page.evaluate(() => document.body.scrollWidth > window.innerWidth + 20);
  await page.setViewportSize({width: 1440, height: 1000});
  await page.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));

  if (screenshotPath) await page.screenshot({ path: screenshotPath, fullPage: true });
  await browser.close();

  const errors = [];
  if (navigationError) errors.push(`navigation failed: ${navigationError}`);
  errors.push(...runtime.missingCharts.map(id => `uninitialized chart: ${id}`));
  errors.push(...runtime.reconciliationErrors);
  if (runtime.mobileOverflow) errors.push('page horizontally overflows mobile viewport');
  errors.push(...pageErrors.map(value => `pageerror: ${value}`));
  errors.push(...consoleErrors.map(value => `console error: ${value}`));
  errors.push(...failedRequests.map(value => `request failed: ${value}`));
  errors.push(...externalRequests.map(value => `external request: ${value}`));
  if (expectsECharts && runtime.chartCount === 0) errors.push('no live ECharts instance was created');
  for (const chart of runtime.rendered) {
    if (!chart.hasLiveSeries) errors.push(`chart ${chart.id} has no live ECharts series`);
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
