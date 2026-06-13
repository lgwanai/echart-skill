# MBTI 伴侣相容性 / MBTI Partner Compatibility

**Category:** `matrix`
**Example dir:** `matrix-mbti`

## Template
⚠️ No template — use knowledge base
Data format: `N/A`

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
```

## Key Points
- Generate via: `scripts/build_template.py  -d data.json`
- Validate: `scripts/validate_chart.py <output.html>`
