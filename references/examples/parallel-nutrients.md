# 营养结构（平行坐标） / Parallel Nutrients

**Category:** `parallel`
**Example dir:** `parallel-nutrients`

## Template
- **parallel/basic.html** — Parallel Coordinates
Data format: `[[dim1, dim2, dim3, ...], ...]  (parallelAxis defines each dimension)`

## Option Code
```javascript
const indices = {
  name: 0,
  group: 1,
  id: 16
};
const schema = [
  { name: 'name', index: 0 },
  { name: 'group', index: 1 },
  { name: 'protein', index: 2 },
  { name: 'calcium', index: 3 },
  { name: 'sodium', index: 4 },
  { name: 'fiber', index: 5 },
  { name: 'vitaminc', index: 6 },
  { name: 'potassium', index: 7 },
  { name: 'carbohydrate', index: 8 },
  { name: 'sugars', index: 9 },
  { name: 'fat', index: 10 },
  { name: 'water', index: 11 },
  { name: 'calories', index: 12 },
  { name: 'saturated', index: 13 },
  { name: 'monounsat', index: 14 },
  { name: 'polyunsat', index: 15 },
  { name: 'id', index: 16 }
];
const groupCategories = [];
const groupColors = [];
$.get(ROOT_PATH + '/data/asset/data/nutrients.json', function (data) {
  normalizeData(data);
  myChart.setOption((option = getOption(data)));
});
function normalizeData(originData) {
  const groupMap = {};
  originData.forEach(function (row) {
    const groupName = row[indices.group];
    if (!groupMap.hasOwnProperty(groupName)) {
      groupMap[groupName] = 1;
    }
  });
  originData.forEach(function (row) {
    row.forEach(function (item, index) {
      if (
        index !== indices.name &&
        index !== indices.group &&
        index !== indices.id
      ) {
        // Convert null to zero, as all of them under unit "g".
        row[index] = parseFloat(item) || 0;
      }
    });
  });
  for (const groupName in groupMap) {
    if (groupMap.hasOwnProperty(groupName)) {
      groupCategories.push(groupName);
    }
  }
  const hStep = Math.round(300 / (groupCategories.length - 1));
  for (var i = 0; i < groupCategories.length; i++) {
    groupColors.push(echarts.color.modifyHSL('#5A94DF', hStep * i));
  }
}
function getOption(data) {
  const lineStyle = {
    width: 0.5,
    opacity: 0.05
  };
  return {
    backgroundColor: '#333',
    tooltip: {
      padding: 10,
      backgroundColor: '#222',
      borderColor: '#777',
      borderWidth: 1
    },
    title: [
      {
        text: 
```

## Key Points
- Generate via: `scripts/build_template.py parallel/basic.html -d data.json`
- Validate: `scripts/validate_chart.py <output.html>`
