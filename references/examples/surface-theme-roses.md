# Theme Roses / Theme Roses

**Category:** `surface`
**Example dir:** `surface-theme-roses`

## Template
- **3d/surface.html** — Surface
Data format: `equation.z as JS function`

## Option Code
```javascript
var sin = Math.sin;
var cos = Math.cos;
var pow = Math.pow;
var sqrt = Math.sqrt;
var cosh = Math.cosh;
var sinh = Math.sinh;
var exp = Math.exp;
var PI = Math.PI;
var square = function (x) {
  return x * x;
};
var mod2 = function (a, b) {
  var c = a % b;
  return c > 0 ? c : c + b;
};
var theta1 = -(20 / 9) * PI;
var theta2 = 15 * PI;
function getParametricEquation(dx, dy) {
  return {
    u: {
      min: 0,
      max: 1,
      step: 1 / 24
    },
    v: {
      min: theta1,
      max: theta2,
      step: (theta2 - theta1) / 575
    },
    x: function (x1, theta) {
      var phi = (PI / 2) * exp(-theta / (8 * PI));
      var y1 =
        1.9565284531299512 *
        square(x1) *
        square(1.2768869870150188 * x1 - 1) *
        sin(phi);
      var X =
        1 -
        square(1.25 * square(1 - mod2(3.6 * theta, 2 * PI) / PI) - 0.25) / 2;
      var r = X * (x1 * sin(phi) + y1 * cos(phi));
      return r * sin(theta) + dx;
    },
    y: function (x1, theta) {
      var phi = (PI / 2) * exp(-theta / (8 * PI));
      var y1 =
        1.9565284531299512 *
        square(x1) *
        square(1.2768869870150188 * x1 - 1) *
        sin(phi);
      var X =
        1 -
        square(1.25 * square(1 - mod2(3.6 * theta, 2 * PI) / PI) - 0.25) / 2;
      var r = X * (x1 * sin(phi) + y1 * cos(phi));
      return r * cos(theta) + dy;
    },
    z: function (x1, theta) {
      var phi = (PI / 2) * exp(-theta / (8 * PI));
      var y1 =
        1.9565284531299512 *
        square(x1) *
        square(1.2768869870150188 * x1 - 1) *
        sin(phi);
      var X =
        1 -
        square(1.25 * square(1 - mod2(3.6 * theta, 2 * PI) / PI) - 0.25) / 2;
      var r = X * (x1 * sin(phi) + y1 * cos(phi));
      return X * (x1 * cos(phi) - y1 * sin(phi));
    }
  };
}
function createSeries(dx, dy, color) {
  return {
    type: 'surface',
    parametric: true,
    shading: 'realistic',
    silent: true,
    wireframe: {
      show: false
    },
    realisticMaterial: {
      roughn
```

## Key Points
- Generate via: `scripts/build_template.py 3d/surface.html -d data.json`
- Validate: `scripts/validate_chart.py <output.html>`
