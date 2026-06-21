## 图表类型：折柱混合 (Mixed Line and Bar)

**生成指令**：你现在的任务是生成一个 ECharts 的 `option` 配置。请根据以下骨架代码和数据结构要求，结合用户的实际数据进行填充和修改，生成一份完整的图表配置参数。

### 双坐标生成规则

- 折线 + 柱状混合图必须先判断单位和量级。只要单位不同，或最大值相差约 5 倍以上，就必须使用双 y 轴。
- 柱状系列使用左轴 `yAxisIndex: 0`，折线系列使用右轴 `yAxisIndex: 1`。不要把不同量级的柱线系列放到同一个 y 轴里。
- 两个 y 轴都需要填写真实指标名和单位；没有给出单位时使用真实字段名，不要创造目标达成率、KPI 等数据中不存在的概念。
- 如果两组指标同单位且量级接近，可以使用单 y 轴，但必须确认折线和柱状都清晰可读。

### ECharts Option 骨架参考
请基于此结构（已剥离冗长写死的数据）生成配置。不要直接输出此骨架，而是要输出**包含真实数据和完整逻辑**的完整 `option` 对象：

```javascript
option = {
  tooltip: {
    trigger: 'axis',
    axisPointer: {
      type: 'cross',
      crossStyle: {
        color: '#999'
      }
    }
  },
  toolbox: {
    feature: {
      dataView: { show: true, readOnly: false },
      magicType: { show: true, type: ['line', 'bar'] },
      restore: { show: true },
      saveAsImage: { show: true }
    }
  },
  legend: {
    data: ['Evaporation', 'Precipitation', 'Temperature']
  },
  xAxis: [
    {
      type: 'category',
      data: [ /* 请使用用户的真实数据数组替换此处 */ ],
      axisPointer: {
        type: 'shadow'
      }
    }
  ],
  yAxis: [
    {
      type: 'value',
      name: 'Precipitation',
      min: 0,
      max: 250,
      interval: 50,
      axisLabel: {
        formatter: '{value} ml'
      }
    },
    {
      type: 'value',
      name: 'Temperature',
      min: 0,
      max: 25,
      interval: 5,
      axisLabel: {
        formatter: '{value} °C'
      }
    }
  ],
  series: [
    {
      name: 'Evaporation',
      type: 'bar',
      yAxisIndex: 0,
      tooltip: {
        valueFormatter: function (value) {
          return value + ' ml';
        }
      },
      data: [ /* 请使用用户的真实数据数组替换此处 */ ]
    },
    {
      name: 'Precipitation',
      type: 'bar',
      yAxisIndex: 0,
      tooltip: {
        valueFormatter: function (value) {
          return value + ' ml';
        }
      },
      data: [ /* 请使用用户的真实数据数组替换此处 */ ]
    },
    {
      name: 'Temperature',
      type: 'line',
      yAxisIndex: 1,
      tooltip: {
        valueFormatter: function (value) {
          return value + ' °C';
        }
      },
      data: [ /* 请使用用户的真实数据数组替换此处 */ ]
    }
  ]
};
```
