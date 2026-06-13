# å¾åä½ç´ å / Voxelize image

**Category:** `bar3D`
**Example dir:** `bar3d-voxelize-image`

## Template
- **3d/bar3d.html** — Bar3D
Data format: `[[x, y, z], ...]`

## Option Code
```javascript
var canvas = document.createElement('canvas');
var ctx = canvas.getContext('2d');
var imgData;
var currentImg;
// Configurations
var config = {
  scale: 0.3,
  roughness: 0,
  metalness: 1,
  projection: 'orthographic',
  depthOfField: 4,
  lockY: false,
  move: true,
  sameColor: false,
  color: '#777',
  colorContrast: 1.2,
  lightIntensity: 1,
  lightColor: '#fff',
  lightRotate: 30,
  lightPitch: 40,
  AO: 1.5,
  showEnvironment: false,
  barNumber: 80,
  barBevel: 0.18,
  barSize: 1.2
};
option = {
  tooltip: {},
  backgroundColor: '#000',
  xAxis3D: {
    type: 'value'
  },
  yAxis3D: {
    type: 'value'
  },
  zAxis3D: {
    type: 'value',
    min: 0,
    max: 100
  },
  grid3D: {
    show: false,
    viewControl: {
      projection: 'perspective',
      alpha: 45,
      beta: -45,
      panSensitivity: config.move ? 1 : 0,
      rotateSensitivity: config.lockY ? [1, 0] : 1,
      damping: 0.9,
      distance: 60
    },
    postEffect: {
      enable: true,
      bloom: {
        intensity: 0.2
      },
      screenSpaceAmbientOcclusion: {
        enable: true,
        intensity: 1.5,
        radius: 5,
        quality: 'high'
      },
      screenSpaceReflection: {
        enable: true
      },
      depthOfField: {
        enable: true,
        blurRadius: config.depthOfField,
        fstop: 10,
        focalDistance: 55
      }
    },
    boxDepth: 100,
    boxHeight: 20,
    environment: 'none',
    light: {
      main: {
        shadow: true,
        intensity: 2
      },
      ambientCubemap: {
        texture: ROOT_PATH + '/data-gl/asset/pisa.hdr',
        exposure: 2,
        diffuseIntensity: 0.2,
        specularIntensity: 1.5
      }
    }
  }
};
function updateData(pixelData, width, height) {
  console.time('update');
  var data = new Float32Array((pixelData.length / 4) * 3);
  var off = 0;
  for (var i = 0; i < pixelData.length / 4; i++) {
    var r = pixelData[i * 4];
    var g = pixelData[i * 4 + 1];
    var b = pixelData[i * 4 + 2];
    var lu
```

## Key Points
- Generate via: `scripts/build_template.py 3d/bar3d.html -d data.json`
- Validate: `scripts/validate_chart.py <output.html>`
