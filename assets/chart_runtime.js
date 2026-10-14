/* One maintained bootstrap for compiler output. Options contain data, never code. */
(() => {
  const configs = JSON.parse(document.getElementById('chart-build-spec').textContent);
  window.__chartBuild = {expected: configs.map(c => c.id), ready: [], errors: []};
  window.dashboardCharts = window.dashboardCharts || [];
  for (const config of configs) {
    try {
      const root = document.getElementById(config.id);
      if (!root || !root.clientWidth || !root.clientHeight) throw new Error('Missing/zero-size container');
      const chart = echarts.init(root, null, {renderer: 'svg'});
      chart.setOption(config.option, {notMerge: true, lazyUpdate: false});
      window.dashboardCharts.push(chart);
      const observer = new ResizeObserver(() => {
        if (root.clientWidth && root.clientHeight) chart.resize();
      });
      observer.observe(root);
      window.__chartBuild.ready.push(config.id);
    } catch (error) {
      window.__chartBuild.errors.push({id: config.id, error: String(error)});
      console.error(config.id + ': ' + error);
    }
  }
})();
