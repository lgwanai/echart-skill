# 元素周期表 / Periodic Table

**Category:** `matrix`
**Example dir:** `matrix-periodic-table`
**Difficulty:** 10

## Template Match
- **geo/lines.html** — 

## Option Code
```javascript
const colors = {
  red: '#f88',
  green: '#8f8',
  blue: '#8bf',
  yellow: '#ff8'
};
option = {
  matrix: {
    x: {
      data: Array.from({ length: 19 }, (_, i) => i + 1 + ''),
      label: {
        show: false
      },
      itemStyle: {
        borderWidth: 0
      },
      dividerLineStyle: {
        width: 0
      }
    },
    y: {
      data: Array.from({ length: 10 }, (_, i) => i + 1 + ''),
      label: {
        show: false
      },
      itemStyle: {
        borderWidth: 0
      },
      dividerLineStyle: {
        width: 0
      }
    },
    left: 'center',
    width: 900,
    backgroundStyle: {
      borderWidth: 0
    },
    body: {
      itemStyle: {
        borderWidth: 0
      }
    }
  },
  series: {
    type: 'custom',
    coordinateSystem: 'matrix',
    data: [
      ['1', '1', '1', 'H', colors.red],
      ['19', '1', '2', 'He', colors.red],
      ['1', '2', '3', 'Li', colors.red],
      ['2', '2', '4', 'Be', colors.red],
      ['14', '2', '5', 'B', colors.yellow],
      ['15', '2', '6', 'C', colors.yellow],
      ['16', '2', '7', 'N', colors.yellow],
      ['17', '2', '8', 'O', colors.yellow],
      ['18', '2', '9', 'F', colors.yellow],
      ['19', '2', '10', 'Ne', colors.yellow],
      ['1', '3', '11', 'Na', colors.red],
      ['2', '3', '12', 'Mg', colors.red],
      ['14', '3', '13', 'Al', colors.yellow],
      ['15', '3', '14', 'Si', colors.yellow],
      ['16', '3', '15', 'P', colors.yellow],
      ['17', '3', '16', 'S', colors.yellow],
      ['18', '3', '17', 'Cl', colors.yellow],
      ['19', '3', '18', 'Ar', colors.yellow],
      ['1', '4', '19', 'K', colors.red],
      ['2', '4', '20', 'Ca', colors.red],
      ['4', '4', '21', 'Sc', colors.blue],
      ['5', '4', '22', 'Ti', colors.blue],
      ['6', '4', '23', 'V', colors.blue],
      ['7', '4', '24', 'Cr', colors.blue],
      ['8', '4', '25', 'Mn', colors.blue],
      ['9', '4', '26', 'Fe', colors.blue],
      ['10', '4', '27', 'Co', colors.blue],
      ['11', '4', '28', 'Ni', colors.blue],
      ['12', '4', '29', 'Cu', colors.blue],
      ['13', '4', '30', 'Zn', colors.blue],
      ['14', '4', '31', 'Ga', colors.yellow],
      ['15', '4', '32', 'Ge', colors.yellow],
      ['16', '4', '33', 'As', colors.yellow],
      ['17', '4', '34', 'Se', colors.yellow],
      ['18', '4', '35', 'Br', colors.yellow],
      ['19', '4', '36', 'Kr', colors.yellow],
      ['1', '5', '37', 'Rb', colors.red],
      ['2', '5', '38', 'Sr', colors.red],
      ['4', '5', '39', 'Y', colors.blue],
      ['5', '5', '40', 'Zr', colors.blue],
      ['6', '5', '41', 'Nb', colors.blue],
      ['7', '5', '42', 'Mo', colors.blue],
      ['8', '5', '43', 'Tc', colors.blue],
      ['9', '5', '44', 'Ru', colors.blue],
      ['10', '5', '45', 'Rh', colors.blue],
      ['11', '5', '46', 'Pd', colors.blue],
      ['12', '5', '47', 'Ag', colors.blue],
      ['13', '5', '48', 'Cd', colors.blue],
      ['14', '5', '49', 'In', colors.yellow],
      ['15', '5', '50', 'Sn', colors.yellow],
      ['16', '5', '
```



## Key Points
- This is an official ECharts example from `matrix-periodic-table/main.js`
- Template data format: `GEO_COORD_MAP + FLIGHTS [[from, to, val], ...]`
- Use `scripts/build_template.py` with the matching template + data
- Always validate with `scripts/validate_chart.py` after generation
