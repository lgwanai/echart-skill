# åºäº marpi ç¤ºä¾ä¿®æ¹çåªå£°ææ / Noise modified from marpi's demo

**Category:** `bar3D`
**Example dir:** `bar3d-noise-modified-from-marpi-demo`

## Template
- **3d/bar3d.html** — Bar3D
Data format: `[[x, y, z], ...]`

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
  
```

## Key Points
- Generate via: `scripts/build_template.py 3d/bar3d.html -d data.json`
- Validate: `scripts/validate_chart.py <output.html>`
