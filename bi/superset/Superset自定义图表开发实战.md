# Superset自定义图表开发实战

## 1. 自定义图表开发概述

### 1.1 自定义图表类型

在Superset中，我们可以开发以下几种类型的自定义图表：

- **基于D3.js的原生图表**：完全自定义的可视化实现
- **基于ECharts的图表**：利用ECharts强大的可视化能力
- **基于Highcharts的图表**：使用Highcharts的丰富图表类型
- **基于Vega/Vega-Lite的图表**：声明式图表定义
- **基于React封装的第三方图表库**：如AntV, Recharts等

### 1.2 开发流程

开发自定义图表的基本流程：

1. 创建前端可视化组件
2. 定义图表元数据和配置选项
3. 实现数据转换逻辑
4. 注册图表到Superset
5. 测试和优化

## 2. 环境准备

### 2.1 目录结构设置

在`superset-frontend/plugins`目录下创建自定义图表目录：

```bash
# 创建自定义图表目录
mkdir -p superset-frontend/plugins/charts/my-custom-chart
cd superset-frontend/plugins/charts/my-custom-chart
```

### 2.2 初始化项目文件

创建基本文件结构：

```
my-custom-chart/
├── package.json
├── src/
│   ├── MyCustomChartPlugin.js
│   ├── MyCustomChart.jsx
│   ├── controlPanel.js
│   ├── transformProps.js
│   └── images/
│       └── thumbnail.png
└── stories/
    └── MyCustomChart.stories.jsx
```

## 3. 实现自定义图表前端组件

### 3.1 创建package.json

```json
{
  "name": "@superset-ui/plugin-chart-my-custom-chart",
  "version": "0.1.0",
  "description": "Superset My Custom Chart",
  "main": "lib/index.js",
  "files": ["lib"],
  "scripts": {
    "build": "npm run clean && npm run babel && npm run copy",
    "babel": "babel src --out-dir lib",
    "clean": "rimraf lib",
    "copy": "copyfiles -u 1 src/images/** lib/"
  },
  "peerDependencies": {
    "@superset-ui/chart": "^0.15.0",
    "@superset-ui/core": "^0.15.0",
    "react": "^16.13.1",
    "react-dom": "^16.13.1"
  },
  "devDependencies": {
    "@babel/cli": "^7.7.5",
    "@babel/core": "^7.7.5",
    "@babel/preset-env": "^7.7.5",
    "@babel/preset-react": "^7.7.4",
    "copyfiles": "^2.1.1",
    "rimraf": "^3.0.0"
  }
}
```

### 3.2 实现图表组件 (MyCustomChart.jsx)

```jsx
import React from 'react';
import { styled } from '@superset-ui/core';
import { MyCustomChart as D3CustomChart } from './d3CustomChart';

// 样式组件
const ChartContainer = styled.div`
  width: 100%;
  height: 100%;
`;

/**
 * 自定义图表React组件
 */
export default function MyCustomChart(props) {
  const { 
    width, 
    height, 
    data, 
    xAxis, 
    yAxis, 
    colorScheme, 
    title 
  } = props;

  return (
    <ChartContainer>
      <D3CustomChart
        width={width}
        height={height}
        data={data}
        xAxis={xAxis}
        yAxis={yAxis}
        colorScheme={colorScheme}
        title={title}
      />
    </ChartContainer>
  );
}
```

### 3.3 实现数据转换函数 (transformProps.js)

```javascript
/**
 * 将Superset数据转换为图表所需格式
 */
export default function transformProps(chartProps) {
  const {
    width,
    height,
    formData,
    queriesData,
  } = chartProps;

  // 获取查询数据
  const data = queriesData[0]?.data || [];
  
  // 获取表单配置项
  const {
    xAxis, // 在控制面板中定义的配置项
    yAxis,
    colorScheme,
    title,
  } = formData;

  // 转换数据格式（根据图表需要进行调整）
  const transformedData = data.map(row => ({
    x: row[xAxis],
    y: row[yAxis],
  }));

  return {
    width,
    height,
    data: transformedData,
    xAxis,
    yAxis,
    colorScheme,
    title,
  };
}
```

### 3.4 创建控制面板配置 (controlPanel.js)

```javascript
import { t, validateNonEmpty } from '@superset-ui/core';

/**
 * 控制面板配置 - 定义图表的配置选项
 */
const config = {
  // 控制面板类型
  controlPanelSections: [
    {
      // 通用配置区域
      label: t('Query'),
      expanded: true,
      controlSetRows: [
        ['metrics'],
        ['adhoc_filters'],
        ['groupby'],
      ],
    },
    {
      // 图表特定配置区域
      label: t('Chart Options'),
      expanded: true,
      controlSetRows: [
        ['title'],
        ['color_scheme'],
        [{
          name: 'xAxis',
          config: {
            type: 'SelectControl',
            label: t('X Axis'),
            choices: [], // 将在运行时填充
            default: null,
            isDynamic: true,
            description: t('Select column for X axis'),
          },
        }],
        [{
          name: 'yAxis',
          config: {
            type: 'SelectControl',
            label: t('Y Axis'),
            choices: [], // 将在运行时填充
            default: null,
            isDynamic: true,
            description: t('Select column for Y axis'),
          },
        }],
      ],
    },
  ],

  // 表单验证规则
  validationConfig: {
    metrics: [validateNonEmpty],
    groupby: [validateNonEmpty],
  },
};

export default config;
```

### 3.5 创建插件注册文件 (MyCustomChartPlugin.js)

```javascript
import { ChartPlugin } from '@superset-ui/chart';
import { MyCustomChart } from './MyCustomChart';
import transformProps from './transformProps';
import controlPanel from './controlPanel';

/**
 * 自定义图表插件类
 */
export default class MyCustomChartPlugin extends ChartPlugin {
  constructor() {
    super({
      chartType: 'my_custom_chart',
      // 图表名称，将显示在图表类型选择器中
      name: 'My Custom Chart',
      // 图表描述
      description: 'A custom visualization chart',
      // 图表缩略图（将在images目录下创建）
      thumbnail: '/static/assets/images/my_custom_chart.png',
      // 图表组件
      loadChart: () => Promise.resolve(MyCustomChart),
      // 数据转换函数
      transformProps,
      // 控制面板配置
      controlPanel,
    });
  }
}
```

### 3.6 实现D3.js可视化核心 (d3CustomChart.js)

```javascript
import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';

/**
 * D3.js可视化核心实现
 */
export function MyCustomChart(props) {
  const { width, height, data, colorScheme } = props;
  const svgRef = useRef();

  useEffect(() => {
    if (!data || data.length === 0) return;

    // 清除现有图表
    d3.select(svgRef.current).selectAll('*').remove();

    // 创建SVG元素
    const svg = d3.select(svgRef.current)
      .attr('width', width)
      .attr('height', height);

    // 设置边距和内部尺寸
    const margin = { top: 20, right: 30, bottom: 40, left: 40 };
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    // 创建主绘图区域
    const g = svg.append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    // 创建X比例尺
    const xScale = d3.scaleBand()
      .domain(data.map(d => d.x))
      .range([0, innerWidth])
      .padding(0.1);

    // 创建Y比例尺
    const yScale = d3.scaleLinear()
      .domain([0, d3.max(data, d => d.y)])
      .range([innerHeight, 0]);

    // 创建颜色比例尺
    const colorScale = d3.scaleOrdinal(colorScheme)
      .domain(data.map(d => d.x));

    // 绘制X轴
    g.append('g')
      .attr('transform', `translate(0,${innerHeight})`)
      .call(d3.axisBottom(xScale));

    // 绘制Y轴
    g.append('g')
      .call(d3.axisLeft(yScale));

    // 绘制柱状图
    g.selectAll('.bar')
      .data(data)
      .enter()
      .append('rect')
      .attr('class', 'bar')
      .attr('x', d => xScale(d.x))
      .attr('y', d => yScale(d.y))
      .attr('width', xScale.bandwidth())
      .attr('height', d => innerHeight - yScale(d.y))
      .attr('fill', d => colorScale(d.x));

  }, [data, width, height, colorScheme]);

  return <svg ref={svgRef} />;
}
```

## 4. 注册和集成图表

### 4.1 注册到前端

创建或修改`superset-frontend/src/visualizations/presets/MainPreset.js`：

```javascript
import { Preset } from '@superset-ui/core';
import MyCustomChartPlugin from '@superset-ui/plugin-chart-my-custom-chart';

// 注册自定义图表插件
export default class MainPreset extends Preset {
  constructor() {
    super({
      name: 'Main Preset',
      presets: [],
      plugins: [
        new MyCustomChartPlugin(),
        // 其他已注册的图表插件
      ],
    });
  }
}
```

### 4.2 在webpack中添加插件

修改`superset-frontend/webpack.config.js`，添加新插件的路径别名：

```javascript
// 添加到resolve.alias部分
resolve: {
  alias: {
    // 现有别名...
    '@superset-ui/plugin-chart-my-custom-chart': 
      path.resolve(__dirname, 'plugins/charts/my-custom-chart/src'),
  },
},
```

### 4.3 后端配置

在`superset/config.py`中添加图表类型：

```python
# 添加自定义图表
def CUSTOM_CHART_TYPES():
    return [
        {
            'name': 'my_custom_chart',
            'verbose_name': 'My Custom Chart',
            'is_timeseries': False,
        },
        # 其他自定义图表...
    ]
```

## 5. 创建示例故事 (Storybook)

为了更好地开发和测试自定义图表，创建Storybook示例：

```jsx
// stories/MyCustomChart.stories.jsx
import React from 'react';
import { withKnobs } from '@storybook/addon-knobs';
import MyCustomChartPlugin from '../src/MyCustomChartPlugin';

// 模拟数据
const mockData = [
  { x: 'A', y: 10 },
  { x: 'B', y: 20 },
  { x: 'C', y: 15 },
  { x: 'D', y: 25 },
];

// 创建模拟图表属性
const createProps = () => ({
  width: 600,
  height: 400,
  data: mockData,
  xAxis: 'category',
  yAxis: 'value',
  colorScheme: ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'],
  title: 'Custom Chart Example',
});

export default {
  title: 'Charts/MyCustomChart',
  decorators: [withKnobs],
};

export const Default = () => {
  const plugin = new MyCustomChartPlugin();
  const Chart = plugin.loadChart();
  return <Chart {...createProps()} />;
};
```

## 6. 测试与调试

### 6.1 运行前端开发服务器

```bash
cd superset-frontend
npm run dev
```

### 6.2 运行Storybook

```bash
cd superset-frontend
npm run storybook
```

### 6.3 常见问题与调试技巧

#### 6.3.1 图表不显示

- 检查数据转换函数是否正确返回数据
- 验证图表组件的尺寸设置
- 使用浏览器开发工具检查控制台错误

#### 6.3.2 控制面板选项不显示

- 确保controlPanel.js配置正确
- 检查字段名是否与transformProps中使用的一致
- 确认插件已正确注册

## 7. 高级功能实现

### 7.1 交互式图表功能

添加悬停和点击交互：

```javascript
// 在d3CustomChart.js中添加交互功能
// 添加悬停效果
g.selectAll('.bar')
  .data(data)
  .enter()
  .append('rect')
  // 基本属性设置...
  .on('mouseover', function(event, d) {
    d3.select(this).style('opacity', 0.8);
    // 显示工具提示
    const tooltip = g.append('text')
      .attr('x', xScale(d.x) + xScale.bandwidth() / 2)
      .attr('y', yScale(d.y) - 10)
      .attr('text-anchor', 'middle')
      .text(`Value: ${d.y}`);
  })
  .on('mouseout', function() {
    d3.select(this).style('opacity', 1);
    // 移除工具提示
    g.selectAll('text').remove();
  })
  .on('click', function(event, d) {
    // 点击事件处理
    console.log('Clicked on', d);
    // 可以触发过滤或其他操作
  });
```

### 7.2 响应式设计

实现响应式图表：

```jsx
// 在MyCustomChart.jsx中添加响应式支持
import { useResizeDetector } from 'react-resize-detector';

export default function MyCustomChart(props) {
  const { 
    data, 
    xAxis, 
    yAxis, 
    colorScheme, 
    title 
  } = props;
  
  const { width, height, ref } = useResizeDetector();

  return (
    <ChartContainer ref={ref}>
      <D3CustomChart
        width={width}
        height={height || 400}
        data={data}
        xAxis={xAxis}
        yAxis={yAxis}
        colorScheme={colorScheme}
        title={title}
      />
    </ChartContainer>
  );
}
```

### 7.3 动画效果

添加过渡动画：

```javascript
// 在d3CustomChart.js中添加动画
g.selectAll('.bar')
  .data(data)
  .enter()
  .append('rect')
  // 基本属性设置...
  .attr('height', 0)
  .attr('y', innerHeight)
  .transition()
  .duration(750)
  .attr('y', d => yScale(d.y))
  .attr('height', d => innerHeight - yScale(d.y));
```

## 8. 发布和部署

### 8.1 构建自定义图表

```bash
cd superset-frontend/plugins/charts/my-custom-chart
npm run build
```

### 8.2 集成到Superset构建

修改`superset-frontend/package.json`，添加自定义插件作为依赖：

```json
{
  "dependencies": {
    "@superset-ui/plugin-chart-my-custom-chart": "file:plugins/charts/my-custom-chart"
  }
}
```

### 8.3 重新构建Superset前端

```bash
cd superset-frontend
npm run build
```

### 8.4 注册为独立npm包（可选）

如果需要在多个项目中复用，可以将图表发布为npm包：

```bash
# 登录npm
npm login

# 发布包
npm publish --access public
```

## 9. 性能优化

### 9.1 大数据集处理

```javascript
// 大数据集优化策略
const optimizeData = (data, limit = 1000) => {
  // 抽样或聚合大数据集
  if (data.length > limit) {
    const sampleRate = Math.ceil(data.length / limit);
    return data.filter((_, i) => i % sampleRate === 0);
  }
  return data;
};

// 在transformProps中使用
export default function transformProps(chartProps) {
  // 现有代码...
  const optimizedData = optimizeData(transformedData);
  
  return {
    // 其他属性...
    data: optimizedData,
  };
}
```

### 9.2 使用Web Worker处理大量计算

```javascript
// 创建worker.js
self.onmessage = function(e) {
  const { data } = e.data;
  // 执行耗时计算
  const result = performComplexCalculation(data);
  // 返回结果
  self.postMessage(result);
};

// 在图表组件中使用
const [processedData, setProcessedData] = useState([]);

useEffect(() => {
  const worker = new Worker('/path/to/worker.js');
  worker.postMessage({ data });
  worker.onmessage = (e) => {
    setProcessedData(e.data);
  };
  return () => worker.terminate();
}, [data]);
```

### 9.3 避免不必要的重渲染

使用React.memo和useMemo优化性能：

```jsx
const MemoizedCustomChart = React.memo(function MemoizedCustomChart(props) {
  // 图表渲染逻辑
  return <D3CustomChart {...props} />;
});

export default function MyCustomChart(props) {
  // 使用useMemo缓存计算结果
  const processedProps = useMemo(() => {
    // 数据处理逻辑
    return {
      ...props,
      // 处理后的数据
    };
  }, [props]);

  return <MemoizedCustomChart {...processedProps} />;
}
```

## 10. 最佳实践

### 10.1 代码组织

- 分离数据转换、业务逻辑和渲染逻辑
- 使用组件化设计提高可维护性
- 添加适当的注释和文档

### 10.2 数据处理

- 尽可能在transformProps中完成数据转换
- 处理缺失数据和异常情况
- 确保数据格式一致性

### 10.3 可访问性

```jsx
// 添加可访问性支持
<rect
  aria-label={`Value: ${d.y}`}
  role="img"
  // 其他属性
/>
```

### 10.4 文档和测试

- 编写详细的README.md文件
- 创建单元测试和集成测试
- 使用Storybook展示各种使用场景

通过本实战指南，您应该能够成功开发和集成自定义图表到Superset中。自定义图表开发是扩展Superset功能的重要方式，掌握这些技术可以极大地增强Superset的数据可视化能力。