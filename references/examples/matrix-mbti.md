# MBTI 伴侣相容性 / MBTI Partner Compatibility

**Category:** `matrix`
**Example dir:** `matrix-mbti`
**Difficulty:** 11

## Template Match
- **geo/lines.html** — 

## Option Code
```javascript
// Click on the data to toggle grouping
const mbti = [
  'ENFJ',
  'ENFP',
  'ENTJ',
  'ENTP',
  'ESFJ',
  'ESFP',
  'ESTJ',
  'ESTP',
  'INFJ',
  'INFP',
  'INTJ',
  'INTP',
  'ISFJ',
  'ISFP',
  'ISTJ',
  'ISTP'
];
const color = {
  green: '#2D9A69',
  purple: '#7D568F',
  blue: '#3A8DAB',
  yellow: '#E0A433',
  greenLighter: '#10CA77',
  purpleLighter: '#9253AF',
  blueLighter: '#26A9D9',
  yellowLighter: '#F4AC24',
  greenDarker: '#0FB369',
  purpleDarker: '#854AA0',
  blueDarker: '#2298C3',
  yellowDarker: '#F2A30D'
};
const fontSize = {
  group: window.innerHeight > 700 ? 24 : 16,
  item: window.innerHeight > 700 ? 13 : 11,
  value: window.innerHeight > 700 ? 15 : 12
};
const getColor = (mbti, lightness = 0) => {
  if (mbti.indexOf('NF') >= 0) {
    return lightness < 0
      ? color.greenLighter
      : lightness > 0
      ? color.greenDarker
      : color.green;
  }
  if (mbti.indexOf('NT') >= 0) {
    return lightness < 0
      ? color.purpleLighter
      : lightness > 0
      ? color.purpleDarker
      : color.purple;
  }
  if (mbti.indexOf('S') >= 0 && mbti.indexOf('J') >= 0) {
    return lightness < 0
      ? color.blueLighter
      : lightness > 0
      ? color.blueDarker
      : color.blue;
  }
  if (mbti.indexOf('S') >= 0 && mbti.indexOf('P') >= 0) {
    return lightness < 0
      ? color.yellowLighter
      : lightness > 0
      ? color.yellowDarker
      : color.yellow;
  }
};
const generateGroup = (groupName) => {
  const colorMap = {
    NF: color.green,
    NT: color.purple,
    SJ: color.blue,
    SP: color.yellow
  };
  const groupMembers = {
    NF: ['INFJ', 'INFP', 'ENFJ', 'ENFP'],
    NT: ['INTJ', 'INTP', 'ENTJ', 'ENTP'],
    SJ: ['ISFJ', 'ISTJ', 'ESFJ', 'ESTJ'],
    SP: ['ISFP', 'ISTP', 'ESFP', 'ESTP']
  };
  return {
    value: groupName,
    label: {
      color: colorMap[groupName],
      fontSize: fontSize.group,
      fontWeight: 'bolder',
      padding: 0
    },
    children: groupMembers[groupName].map((mbti) => ({
      value: mbti,
      label: {
        color: colorMap[groupName],
        fontSize: fontSize.item,
        fontWeight: 'bold'
      }
    }))
  };
};
const xData = [
  generateGroup('NF'),
  generateGroup('NT'),
  generateGroup('SJ'),
  generateGroup('SP')
];
const yData = [
  generateGroup('NF'),
  generateGroup('NT'),
  generateGroup('SJ'),
  generateGroup('SP')
];
const originalData = [
  ['ENFJ', 'ENFJ', 0.86],
  ['ENFJ', 'ENFP', 0.91],
  ['ENFJ', 'ENTJ', 0.42],
  ['ENFJ', 'ENTP', 0.73],
  ['ENFJ', 'ESFJ', 0.64],
  ['ENFJ', 'ESFP', 0.8],
  ['ENFJ', 'ESTJ', 0.22],
  ['ENFJ', 'ESTP', 0.41],
  ['ENFJ', 'INFJ', 0.74],
  ['ENFJ', 'INFP', 0.73],
  ['ENFJ', 'INTJ', 0.16],
  ['ENFJ', 'INTP', 0.35],
  ['ENFJ', 'ISFJ', 0.3],
  ['ENFJ', 'ISFP', 0.4],
  ['ENFJ', 'ISTJ', 0.18],
  ['ENFJ', 'ISTP', 0.09],
  ['ENFP', 'ENFJ', 0.91],
  ['ENFP', 'ENFP', 0.97],
  ['ENFP', 'ENTJ', 0.37],
  ['ENFP', 'ENTP', 0.85],
  ['ENFP', 'ESFJ', 0.42],
  ['ENFP', 'ESFP', 0.93],
  ['ENFP', 'ESTJ', 0.27],
  ['ENFP', 'ESTP', 0.76],

```



## Key Points
- This is an official ECharts example from `matrix-mbti/main.js`
- Template data format: `GEO_COORD_MAP + FLIGHTS [[from, to, val], ...]`
- Use `scripts/build_template.py` with the matching template + data
- Always validate with `scripts/validate_chart.py` after generation
