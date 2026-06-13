# åºäº marpi ç¤ºä¾ä¿®æ¹çåªå£°ææ / Noise modified from marpi's demo

**Category:** `bar3D`
**Example dir:** `bar3d-noise-modified-from-marpi-demo`
**Difficulty:** 

## Template Match
- **3d/bar3d.html** — Bar3D

## Option Code
```javascript
$.getScript(CDN_PATH + 'simplex-noise@2.4.0/simplex-noise.js').done(
  function () {
    var simplex = new SimplexNoise();
    var UPDATE_DURATION = 1000;
    function initVisualizer() {
      var config = {
        numWaves: 2,
        randomize: randomize,
        color1: '#000',
        color2: '#300',
        color3: '#fff',
        size: 150,
        roughness: 0.5,
        metalness: 0
      };
      //gui.add(config, "numWaves", 1, 3).name("Waves number").onChange(update).listen();
      for (var i = 0; i < 2; i++) {
        config['wave' + i + 'axis' + 'x'] = Math.random();
        config['wave' + i + 'axis' + 'y'] = Math.random();
        config['wave' + i + 'rounding'] = Math.random();
        config['wave' + i + 'square'] = Math.random();
      }
      function randomize() {
        //config.numWaves = Math.floor(Math.random() * 3) + 1;
        for (var i = 0; i < 2; i++) {
          config['wave' + i + 'axis' + 'x'] = Math.random();
          config['wave' + i + 'axis' + 'y'] = Math.random();
          config['wave' + i + 'rounding'] = Math.random();
          config['wave' + i + 'square'] = Math.random();
        }
        // Iterate over all controllers
        for (var i in gui.__controllers) {
          gui.__controllers[i].updateDisplay();
        }
        update();
      }
      function update() {
        var item = [];
        var dataProvider = [];
        var mod = 0.1;
        //config.numWaves = Math.round(config.numWaves)
        //var occurenceR = Math.random() * .02
        //var r = 0//Math.random()
        for (var s = 0; s < config.size * config.size; s++) {
          var x = s % config.size;
          var y = Math.floor(s / config.size);
          //if (Math.random() < occurenceR)
          //    r = Math.random()
          var output = 0;
          for (var i = 0; i < config.numWaves; i++) {
            var n = simplex.noise2D(
              i * 213 +
                (-50 + x) * mod * (1 - config['wave' + i + 'axis' + 'x']) * 0.5,
              i * 3124 +
                (-50 + y) * mod * (1 - config['wave' + i + 'axis' + 'y']) * 0.5
            );
            n = Math.pow(n, 1.95 - 1.9 * config['wave' + i + 'rounding']);
            var square = Math.floor(
              (1.1 - config['wave' + i + 'square']) * 100
            );
            n = Math.round(n * square) / square;
            //output*=n
            if (output < n) output = n;
          }
          dataProvider.push([x, y, (output + 0.1) * 2]);
        }
        myChart.setOption({
          visualMap: {
            inRange: {
              barSize: 100 / config.size,
              color: [config.color1, config.color2, config.color3]
            }
          },
          series: [
            {
              data: dataProvider,
              realisticMaterial: {
                roughness: config.roughness,
                metalness: config.metalness
              }
            }
          ]
        });
        //setTimeout(update, UPDATE_DURATION);
  
```

## Relevant Debug Patterns
## #27
 — 3D Bar 空白：GL_INLINE + coordinateSystem + zAxis3D 配置错误
- **日期**：2026-06-13
- **现象**：33_3D_Bar 一片空白
- **根因**：(1) `GL_INLINE: ""` 破坏 echarts-gl 注入（同 #18）；(2) `coordinateSystem: 'cartesian3D'` + `zAxis3D: {type:'value'}` + `shading:'realistic'` 不是官方推荐的配置组合；(3) 官方示例用 `zAxis3D: {}`（空对象）、无 `coordinateSystem`、`shading: 'lambert'`
- **修复**：模板改为与 ECharts 官方 bar3D 示例完全一致的配置：`grid3D: {}`、`zAxis3D: {}`、`shading: 'lambert'`、无 `coordinateSystem`、无 `barSize`

---
...

## Key Points
- This is an official ECharts example from `bar3d-noise-modified-from-marpi-demo/main.js`
- Template data format: `[[x, y, z], ...]`
- Use `scripts/build_template.py` with the matching template + data
- Always validate with `scripts/validate_chart.py` after generation
