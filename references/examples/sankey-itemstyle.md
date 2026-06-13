# 桑基图节点自定义样式 / Specify ItemStyle for Each Node in Sankey

**Category:** `sankey`
**Example dir:** `sankey-itemstyle`

## Template
- **sankey/basic.html** — Sankey
Data format: `{ nodes: [{name: string, itemStyle?: {}}, ...], links: [{source: string, target: string, value: number}, ...] }`

## Option Code
```javascript
option = {
  backgroundColor: '#fff',
  title: {
    subtext: 'Data From lisachristina1234 on GitHub',
    left: 'center'
  },
  series: [
    {
      type: 'sankey',
      left: 50.0,
      top: 20.0,
      right: 150.0,
      bottom: 25.0,
      data: [
        {
          name: 'Werne',
          itemStyle: {
            color: '#f18bbf',
            borderColor: '#f18bbf'
          }
        },
        {
          name: 'Duesseldorf',
          itemStyle: {
            color: '#0078D7',
            borderColor: '#0078D7'
          }
        },
        {
          name: 'Cambridge',
          itemStyle: {
            color: '#3891A7',
            borderColor: '#3891A7'
          }
        },
        {
          name: 'Colma',
          itemStyle: {
            color: '#0037DA',
            borderColor: '#0037DA'
          }
        },
        {
          name: 'W. York',
          itemStyle: {
            color: '#C0BEAF',
            borderColor: '#C0BEAF'
          }
        },
        {
          name: 'Frankfurt am Main',
          itemStyle: {
            color: '#EA005E',
            borderColor: '#EA005E'
          }
        },
        {
          name: 'Metz',
          itemStyle: {
            color: '#D13438',
            borderColor: '#D13438'
          }
        },
        {
          name: 'Orleans',
          itemStyle: {
            color: '#567C73',
            borderColor: '#567C73'
          }
        },
        {
          name: 'Saint-Denis',
          itemStyle: {
            color: '#9ed566',
            borderColor: '#9ed566'
          }
        },
        {
          name: 'Hof',
          itemStyle: {
            color: '#2BCC7F',
            borderColor: '#2BCC7F'
          }
        },
        {
          name: 'Cliffside',
          itemStyle: {
            color: '#809B48',
            borderColor: '#809B48'
          }
        },
        {
          name: 'Leeds',
          itemStyle: {
            color: '#9B2D1F',
            borde
```

## Key Points
- Generate via: `scripts/build_template.py sankey/basic.html -d data.json`
- Validate: `scripts/validate_chart.py <output.html>`
