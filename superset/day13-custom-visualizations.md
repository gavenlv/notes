# Day 13: Custom Visualizations

## User Story 1: Create Custom Chart Plugin

**Title**: Develop Custom Visualization Plugin

**Description**: Create a custom chart plugin for Superset including frontend components, backend registration, and configuration options.

**Acceptance Criteria**:
- Custom chart plugin is created
- Frontend component is implemented
- Backend registration is working
- Configuration options are available
- Plugin is properly packaged

**Step-by-Step Guide**:

1. **Plugin Structure Setup**:
```bash
# Create plugin directory structure
mkdir -p superset_custom_chart/src/superset_custom_chart
mkdir -p superset_custom_chart/superset_custom_chart/static/js
mkdir -p superset_custom_chart/superset_custom_chart/templates

# Plugin structure
superset_custom_chart/
├── setup.py
├── MANIFEST.in
├── README.md
├── src/
│   └── superset_custom_chart/
│       ├── __init__.py
│       ├── static/
│       │   └── js/
│       │       └── CustomChart.js
│       └── templates/
│           └── custom_chart.html
```

2. **Frontend Component Implementation**:
```javascript
// src/superset_custom_chart/static/js/CustomChart.js
import { t } from '@superset-ui/core';
import { ChartMetadata, ChartPlugin } from '@superset-ui/chart';

const metadata = new ChartMetadata({
  name: 'custom-chart',
  description: 'A custom chart plugin for Superset',
  thumbnail: './custom-chart-thumbnail.png',
});

export default class CustomChartPlugin extends ChartPlugin {
  constructor() {
    super({
      metadata,
      loadChart: () => import('./CustomChart'),
    });
  }
}

// Custom chart component
import React from 'react';
import { styled } from '@superset-ui/core';

const Styles = styled.div`
  padding: ${({ theme }) => theme.gridUnit * 4}px;
  height: ${({ height }) => height}px;
  width: ${({ width }) => width}px;
`;

export default function CustomChart(props) {
  const { data, height, width, formData } = props;
  
  // Process data for visualization
  const processedData = processChartData(data, formData);
  
  return (
    <Styles height={height} width={width}>
      <div className="custom-chart">
        <h3>Custom Chart</h3>
        <div className="chart-container">
          {/* Custom visualization implementation */}
          {renderCustomVisualization(processedData, formData)}
        </div>
      </div>
    </Styles>
  );
}

// Data processing function
function processChartData(data, formData) {
  const { metrics, columns } = formData;
  
  return data.map(row => ({
    x: row[columns[0]],
    y: row[metrics[0]],
    label: row[columns[0]],
    value: row[metrics[0]]
  }));
}

// Custom visualization rendering
function renderCustomVisualization(data, formData) {
  // Implement custom visualization logic
  return (
    <div className="custom-visualization">
      {data.map((item, index) => (
        <div key={index} className="data-point">
          <span className="label">{item.label}</span>
          <span className="value">{item.value}</span>
        </div>
      ))}
    </div>
  );
}
```

3. **Backend Registration**:
```python
# src/superset_custom_chart/__init__.py
from superset_custom_chart.static.js.CustomChart import CustomChartPlugin

# Register the plugin
def register_custom_chart():
    """Register the custom chart plugin with Superset"""
    from superset.charts.registry import ChartRegistry
    
    registry = ChartRegistry()
    registry.register(CustomChartPlugin())
    
    return registry

# Plugin configuration
CUSTOM_CHART_CONFIG = {
    'name': 'custom-chart',
    'label': 'Custom Chart',
    'description': 'A custom chart plugin for Superset',
    'thumbnail': 'custom-chart-thumbnail.png',
    'form_data_schema': {
        'type': 'object',
        'properties': {
            'custom_option': {
                'type': 'string',
                'title': 'Custom Option',
                'description': 'A custom configuration option'
            }
        }
    }
}
```

**Reference Documents**:
- [Custom Chart Development](https://superset.apache.org/docs/developing-charts-plugins)
- [Plugin Architecture](https://superset.apache.org/docs/developing-charts-plugins#architecture)

---

## User Story 2: Advanced Chart Configuration

**Title**: Implement Advanced Chart Configuration Options

**Description**: Add comprehensive configuration options for custom charts including data transformation, styling, and interactive features.

**Acceptance Criteria**:
- Configuration options are implemented
- Data transformation is available
- Styling options are configurable
- Interactive features work
- Configuration validation is in place

**Step-by-Step Guide**:

1. **Chart Configuration Schema**:
```javascript
// Chart configuration schema
const configSchema = {
  type: 'object',
  properties: {
    // Data configuration
    dataSource: {
      type: 'string',
      title: 'Data Source',
      description: 'Select the data source for the chart'
    },
    
    // Visualization options
    chartType: {
      type: 'string',
      title: 'Chart Type',
      enum: ['bar', 'line', 'scatter', 'custom'],
      default: 'bar'
    },
    
    // Styling options
    colors: {
      type: 'array',
      title: 'Color Palette',
      items: {
        type: 'string',
        format: 'color'
      },
      default: ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
    },
    
    // Interactive features
    enableTooltip: {
      type: 'boolean',
      title: 'Enable Tooltips',
      default: true
    },
    
    enableZoom: {
      type: 'boolean',
      title: 'Enable Zoom',
      default: false
    },
    
    // Custom options
    customOptions: {
      type: 'object',
      title: 'Custom Options',
      properties: {
        animationDuration: {
          type: 'number',
          title: 'Animation Duration (ms)',
          default: 1000
        },
        showLegend: {
          type: 'boolean',
          title: 'Show Legend',
          default: true
        }
      }
    }
  }
};

// Configuration validation
function validateChartConfig(config) {
  const errors = [];
  
  // Validate required fields
  if (!config.dataSource) {
    errors.push('Data source is required');
  }
  
  // Validate color palette
  if (config.colors && config.colors.length < 2) {
    errors.push('At least 2 colors are required');
  }
  
  // Validate custom options
  if (config.customOptions) {
    if (config.customOptions.animationDuration < 0) {
      errors.push('Animation duration must be positive');
    }
  }
  
  return errors;
}
```

2. **Data Transformation Functions**:
```javascript
// Data transformation utilities
export class DataTransformer {
  constructor(config) {
    this.config = config;
  }
  
  // Transform raw data for visualization
  transformData(rawData, formData) {
    const { metrics, columns, filters } = formData;
    
    let transformedData = rawData;
    
    // Apply filters
    if (filters && filters.length > 0) {
      transformedData = this.applyFilters(transformedData, filters);
    }
    
    // Apply aggregations
    if (metrics && metrics.length > 0) {
      transformedData = this.applyAggregations(transformedData, metrics);
    }
    
    // Apply sorting
    if (formData.sortBy) {
      transformedData = this.applySorting(transformedData, formData.sortBy);
    }
    
    // Apply grouping
    if (columns && columns.length > 0) {
      transformedData = this.applyGrouping(transformedData, columns);
    }
    
    return transformedData;
  }
  
  // Apply data filters
  applyFilters(data, filters) {
    return data.filter(row => {
      return filters.every(filter => {
        const value = row[filter.column];
        switch (filter.operator) {
          case '==':
            return value === filter.value;
          case '>':
            return value > filter.value;
          case '<':
            return value < filter.value;
          case 'in':
            return filter.values.includes(value);
          default:
            return true;
        }
      });
    });
  }
  
  // Apply data aggregations
  applyAggregations(data, metrics) {
    const aggregated = {};
    
    data.forEach(row => {
      const key = this.getGroupKey(row);
      if (!aggregated[key]) {
        aggregated[key] = {};
      }
      
      metrics.forEach(metric => {
        const value = row[metric];
        if (!aggregated[key][metric]) {
          aggregated[key][metric] = 0;
        }
        aggregated[key][metric] += value;
      });
    });
    
    return Object.entries(aggregated).map(([key, values]) => ({
      group: key,
      ...values
    }));
  }
  
  // Get grouping key
  getGroupKey(row) {
    return Object.keys(row)
      .filter(key => !this.isMetric(key))
      .map(key => row[key])
      .join('|');
  }
  
  // Check if field is a metric
  isMetric(field) {
    return this.config.metrics && this.config.metrics.includes(field);
  }
}
```

3. **Interactive Features Implementation**:
```javascript
// Interactive features
export class ChartInteractions {
  constructor(chartElement, config) {
    this.chartElement = chartElement;
    this.config = config;
    this.setupInteractions();
  }
  
  // Setup interactive features
  setupInteractions() {
    if (this.config.enableTooltip) {
      this.setupTooltips();
    }
    
    if (this.config.enableZoom) {
      this.setupZoom();
    }
    
    if (this.config.enableSelection) {
      this.setupSelection();
    }
  }
  
  // Setup tooltips
  setupTooltips() {
    const tooltip = d3.select('body')
      .append('div')
      .attr('class', 'custom-chart-tooltip')
      .style('position', 'absolute')
      .style('visibility', 'hidden')
      .style('background', 'rgba(0, 0, 0, 0.8)')
      .style('color', 'white')
      .style('padding', '8px')
      .style('border-radius', '4px');
    
    this.chartElement.selectAll('.data-point')
      .on('mouseover', (event, d) => {
        tooltip.style('visibility', 'visible')
          .html(this.formatTooltip(d))
          .style('left', (event.pageX + 10) + 'px')
          .style('top', (event.pageY - 10) + 'px');
      })
      .on('mouseout', () => {
        tooltip.style('visibility', 'hidden');
      });
  }
  
  // Setup zoom functionality
  setupZoom() {
    const zoom = d3.zoom()
      .scaleExtent([0.5, 5])
      .on('zoom', (event) => {
        this.chartElement.select('.chart-content')
          .attr('transform', event.transform);
      });
    
    this.chartElement.call(zoom);
  }
  
  // Setup selection functionality
  setupSelection() {
    this.chartElement.selectAll('.data-point')
      .on('click', (event, d) => {
        this.handleSelection(d);
      });
  }
  
  // Handle data selection
  handleSelection(data) {
    // Emit selection event
    this.chartElement.dispatch('selection', {
      detail: { data, timestamp: Date.now() }
    });
  }
  
  // Format tooltip content
  formatTooltip(data) {
    return `
      <div>
        <strong>${data.label}</strong><br/>
        Value: ${data.value}<br/>
        ${data.additionalInfo || ''}
      </div>
    `;
  }
}
```

**Reference Documents**:
- [Chart Configuration](https://superset.apache.org/docs/developing-charts-plugins#configuration)
- [Interactive Features](https://superset.apache.org/docs/developing-charts-plugins#interactions)

---

## User Story 3: Chart Styling and Theming

**Title**: Implement Advanced Chart Styling

**Description**: Create comprehensive styling and theming options for custom charts including CSS customization, theme integration, and responsive design.

**Acceptance Criteria**:
- CSS styling is implemented
- Theme integration works
- Responsive design is applied
- Custom themes are supported
- Styling is configurable

**Step-by-Step Guide**:

1. **CSS Styling Implementation**:
```css
/* Custom chart styles */
.custom-chart {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: var(--chart-background, #ffffff);
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.custom-chart-header {
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-color, #e1e5e9);
  background: var(--header-background, #f8f9fa);
}

.custom-chart-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-color, #2c3e50);
  margin: 0;
}

.custom-chart-content {
  padding: 20px;
  min-height: 300px;
}

.custom-chart-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-top: 16px;
  padding: 16px 20px;
  border-top: 1px solid var(--border-color, #e1e5e9);
  background: var(--legend-background, #f8f9fa);
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: var(--text-color, #2c3e50);
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 2px;
}

/* Data point styles */
.data-point {
  cursor: pointer;
  transition: all 0.2s ease;
}

.data-point:hover {
  transform: scale(1.05);
  opacity: 0.8;
}

.data-point.selected {
  stroke: var(--selection-color, #007bff);
  stroke-width: 2px;
}

/* Responsive design */
@media (max-width: 768px) {
  .custom-chart {
    border-radius: 4px;
  }
  
  .custom-chart-header {
    padding: 12px 16px;
  }
  
  .custom-chart-content {
    padding: 16px;
  }
  
  .custom-chart-legend {
    padding: 12px 16px;
    gap: 12px;
  }
}

/* Dark theme support */
[data-theme="dark"] .custom-chart {
  background: var(--dark-chart-background, #2c3e50);
  color: var(--dark-text-color, #ecf0f1);
}

[data-theme="dark"] .custom-chart-header {
  background: var(--dark-header-background, #34495e);
  border-bottom-color: var(--dark-border-color, #4a5568);
}

[data-theme="dark"] .custom-chart-legend {
  background: var(--dark-legend-background, #34495e);
  border-top-color: var(--dark-border-color, #4a5568);
}
```

2. **Theme Integration**:
```javascript
// Theme integration
export class ChartTheme {
  constructor(theme = 'light') {
    this.theme = theme;
    this.colors = this.getThemeColors();
    this.styles = this.getThemeStyles();
  }
  
  // Get theme colors
  getThemeColors() {
    const lightColors = {
      primary: '#007bff',
      secondary: '#6c757d',
      success: '#28a745',
      danger: '#dc3545',
      warning: '#ffc107',
      info: '#17a2b8',
      light: '#f8f9fa',
      dark: '#343a40',
      text: '#2c3e50',
      background: '#ffffff',
      border: '#e1e5e9'
    };
    
    const darkColors = {
      primary: '#007bff',
      secondary: '#6c757d',
      success: '#28a745',
      danger: '#dc3545',
      warning: '#ffc107',
      info: '#17a2b8',
      light: '#34495e',
      dark: '#2c3e50',
      text: '#ecf0f1',
      background: '#2c3e50',
      border: '#4a5568'
    };
    
    return this.theme === 'dark' ? darkColors : lightColors;
  }
  
  // Get theme styles
  getThemeStyles() {
    return {
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
      fontSize: '14px',
      lineHeight: '1.5',
      borderRadius: '8px',
      boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
      transition: 'all 0.2s ease'
    };
  }
  
  // Apply theme to chart
  applyTheme(chartElement) {
    const colors = this.colors;
    const styles = this.styles;
    
    // Apply CSS custom properties
    chartElement.style.setProperty('--chart-background', colors.background);
    chartElement.style.setProperty('--text-color', colors.text);
    chartElement.style.setProperty('--border-color', colors.border);
    chartElement.style.setProperty('--primary-color', colors.primary);
    
    // Apply base styles
    Object.assign(chartElement.style, {
      fontFamily: styles.fontFamily,
      fontSize: styles.fontSize,
      lineHeight: styles.lineHeight,
      borderRadius: styles.borderRadius,
      boxShadow: styles.boxShadow,
      transition: styles.transition
    });
  }
  
  // Update theme
  updateTheme(newTheme) {
    this.theme = newTheme;
    this.colors = this.getThemeColors();
    this.styles = this.getThemeStyles();
  }
}
```

3. **Responsive Design Implementation**:
```javascript
// Responsive design utilities
export class ResponsiveChart {
  constructor(chartElement, config) {
    this.chartElement = chartElement;
    this.config = config;
    this.resizeObserver = null;
    this.setupResponsive();
  }
  
  // Setup responsive behavior
  setupResponsive() {
    // Create resize observer
    this.resizeObserver = new ResizeObserver(entries => {
      for (const entry of entries) {
        this.handleResize(entry);
      }
    });
    
    // Start observing
    this.resizeObserver.observe(this.chartElement);
    
    // Handle window resize
    window.addEventListener('resize', this.handleWindowResize.bind(this));
  }
  
  // Handle resize events
  handleResize(entry) {
    const { width, height } = entry.contentRect;
    this.updateChartSize(width, height);
  }
  
  // Handle window resize
  handleWindowResize() {
    const rect = this.chartElement.getBoundingClientRect();
    this.updateChartSize(rect.width, rect.height);
  }
  
  // Update chart size
  updateChartSize(width, height) {
    // Update chart dimensions
    this.chartElement.style.width = `${width}px`;
    this.chartElement.style.height = `${height}px`;
    
    // Trigger chart redraw
    this.redrawChart();
  }
  
  // Redraw chart with new dimensions
  redrawChart() {
    // Clear existing content
    this.chartElement.select('.chart-content').selectAll('*').remove();
    
    // Redraw with new dimensions
    this.renderChart();
  }
  
  // Render chart
  renderChart() {
    const width = this.chartElement.node().getBoundingClientRect().width;
    const height = this.chartElement.node().getBoundingClientRect().height;
    
    // Create SVG
    const svg = this.chartElement.select('.chart-content')
      .append('svg')
      .attr('width', width)
      .attr('height', height);
    
    // Render chart content
    this.renderChartContent(svg, width, height);
  }
  
  // Render chart content
  renderChartContent(svg, width, height) {
    // Implement chart rendering logic
    // This will depend on the specific chart type
  }
  
  // Cleanup
  destroy() {
    if (this.resizeObserver) {
      this.resizeObserver.disconnect();
    }
    window.removeEventListener('resize', this.handleWindowResize);
  }
}
```

**Reference Documents**:
- [Chart Styling](https://superset.apache.org/docs/developing-charts-plugins#styling)
- [Theme Integration](https://superset.apache.org/docs/developing-charts-plugins#theming)

---

## User Story 4: Chart Testing and Validation

**Title**: Implement Comprehensive Chart Testing

**Description**: Create testing framework for custom charts including unit tests, integration tests, and visual regression tests.

**Acceptance Criteria**:
- Unit tests are implemented
- Integration tests are created
- Visual regression tests work
- Test coverage is comprehensive
- Testing automation is set up

**Step-by-Step Guide**:

1. **Unit Testing Setup**:
```javascript
// Unit tests for custom chart
import { render, screen } from '@testing-library/react';
import CustomChart from './CustomChart';

describe('CustomChart', () => {
  const mockData = [
    { label: 'Category A', value: 100 },
    { label: 'Category B', value: 200 },
    { label: 'Category C', value: 150 }
  ];
  
  const mockFormData = {
    metrics: ['value'],
    columns: ['label'],
    chartType: 'bar',
    colors: ['#1f77b4', '#ff7f0e', '#2ca02c']
  };
  
  test('renders chart with data', () => {
    render(
      <CustomChart
        data={mockData}
        height={400}
        width={600}
        formData={mockFormData}
      />
    );
    
    expect(screen.getByText('Custom Chart')).toBeInTheDocument();
    expect(screen.getByText('Category A')).toBeInTheDocument();
    expect(screen.getByText('Category B')).toBeInTheDocument();
    expect(screen.getByText('Category C')).toBeInTheDocument();
  });
  
  test('handles empty data', () => {
    render(
      <CustomChart
        data={[]}
        height={400}
        width={600}
        formData={mockFormData}
      />
    );
    
    expect(screen.getByText('No data available')).toBeInTheDocument();
  });
  
  test('applies custom styling', () => {
    const customFormData = {
      ...mockFormData,
      customOptions: {
        backgroundColor: '#f0f0f0',
        textColor: '#333333'
      }
    };
    
    render(
      <CustomChart
        data={mockData}
        height={400}
        width={600}
        formData={customFormData}
      />
    );
    
    const chartElement = screen.getByTestId('custom-chart');
    expect(chartElement).toHaveStyle({
      backgroundColor: '#f0f0f0',
      color: '#333333'
    });
  });
});

// Data transformation tests
describe('DataTransformer', () => {
  const transformer = new DataTransformer({
    metrics: ['value'],
    columns: ['category']
  });
  
  test('transforms data correctly', () => {
    const rawData = [
      { category: 'A', value: 100 },
      { category: 'B', value: 200 },
      { category: 'A', value: 150 }
    ];
    
    const formData = {
      metrics: ['value'],
      columns: ['category']
    };
    
    const result = transformer.transformData(rawData, formData);
    
    expect(result).toEqual([
      { group: 'A', value: 250 },
      { group: 'B', value: 200 }
    ]);
  });
  
  test('applies filters correctly', () => {
    const data = [
      { category: 'A', value: 100 },
      { category: 'B', value: 200 },
      { category: 'C', value: 300 }
    ];
    
    const filters = [
      { column: 'value', operator: '>', value: 150 }
    ];
    
    const result = transformer.applyFilters(data, filters);
    
    expect(result).toEqual([
      { category: 'B', value: 200 },
      { category: 'C', value: 300 }
    ]);
  });
});
```

2. **Integration Testing**:
```javascript
// Integration tests
describe('CustomChart Integration', () => {
  test('integrates with Superset correctly', () => {
    // Test plugin registration
    const plugin = new CustomChartPlugin();
    expect(plugin.metadata.name).toBe('custom-chart');
    expect(plugin.metadata.description).toBe('A custom chart plugin for Superset');
  });
  
  test('handles Superset data format', () => {
    const supersetData = {
      columns: ['category', 'value'],
      data: [
        ['A', 100],
        ['B', 200],
        ['C', 150]
      ]
    };
    
    const formData = {
      metrics: ['value'],
      columns: ['category']
    };
    
    render(
      <CustomChart
        data={supersetData}
        height={400}
        width={600}
        formData={formData}
      />
    );
    
    // Verify data is processed correctly
    expect(screen.getByText('A')).toBeInTheDocument();
    expect(screen.getByText('B')).toBeInTheDocument();
    expect(screen.getByText('C')).toBeInTheDocument();
  });
  
  test('responds to configuration changes', () => {
    const { rerender } = render(
      <CustomChart
        data={mockData}
        height={400}
        width={600}
        formData={mockFormData}
      />
    );
    
    // Change configuration
    const newFormData = {
      ...mockFormData,
      chartType: 'line',
      colors: ['#ff0000', '#00ff00', '#0000ff']
    };
    
    rerender(
      <CustomChart
        data={mockData}
        height={400}
        width={600}
        formData={newFormData}
      />
    );
    
    // Verify chart updates
    const chartElement = screen.getByTestId('custom-chart');
    expect(chartElement).toHaveAttribute('data-chart-type', 'line');
  });
});
```

3. **Visual Regression Testing**:
```javascript
// Visual regression tests using Playwright
import { test, expect } from '@playwright/test';

test.describe('CustomChart Visual Tests', () => {
  test('renders chart correctly', async ({ page }) => {
    await page.goto('/chart/custom-chart');
    
    // Wait for chart to load
    await page.waitForSelector('[data-testid="custom-chart"]');
    
    // Take screenshot
    const chartElement = await page.locator('[data-testid="custom-chart"]');
    await expect(chartElement).toHaveScreenshot('custom-chart-default.png');
  });
  
  test('renders different chart types', async ({ page }) => {
    const chartTypes = ['bar', 'line', 'scatter'];
    
    for (const chartType of chartTypes) {
      await page.goto(`/chart/custom-chart?type=${chartType}`);
      await page.waitForSelector('[data-testid="custom-chart"]');
      
      const chartElement = await page.locator('[data-testid="custom-chart"]');
      await expect(chartElement).toHaveScreenshot(`custom-chart-${chartType}.png`);
    }
  });
  
  test('handles responsive design', async ({ page }) => {
    await page.goto('/chart/custom-chart');
    await page.waitForSelector('[data-testid="custom-chart"]');
    
    // Test different viewport sizes
    const viewports = [
      { width: 1920, height: 1080 },
      { width: 1366, height: 768 },
      { width: 768, height: 1024 },
      { width: 375, height: 667 }
    ];
    
    for (const viewport of viewports) {
      await page.setViewportSize(viewport);
      await page.waitForTimeout(1000); // Wait for resize
      
      const chartElement = await page.locator('[data-testid="custom-chart"]');
      await expect(chartElement).toHaveScreenshot(
        `custom-chart-responsive-${viewport.width}x${viewport.height}.png`
      );
    }
  });
  
  test('handles dark theme', async ({ page }) => {
    await page.goto('/chart/custom-chart?theme=dark');
    await page.waitForSelector('[data-testid="custom-chart"]');
    
    const chartElement = await page.locator('[data-testid="custom-chart"]');
    await expect(chartElement).toHaveScreenshot('custom-chart-dark-theme.png');
  });
});
```

**Reference Documents**:
- [Chart Testing](https://superset.apache.org/docs/developing-charts-plugins#testing)
- [Testing Framework](https://superset.apache.org/docs/developing-charts-plugins#testing-framework)

---

## User Story 5: Chart Documentation and Deployment

**Title**: Create Documentation and Deploy Custom Chart

**Description**: Develop comprehensive documentation and deployment process for custom charts including user guides, API documentation, and deployment automation.

**Acceptance Criteria**:
- Documentation is comprehensive
- API documentation is complete
- Deployment process is automated
- User guide is available
- Maintenance procedures are documented

**Step-by-Step Guide**:

1. **Documentation Structure**:
```markdown
# Custom Chart Plugin Documentation

## Overview
The Custom Chart Plugin extends Apache Superset with a new visualization type that provides [description of functionality].

## Installation
```bash
pip install superset-custom-chart
```

## Configuration
Add the following to your `superset_config.py`:
```python
CUSTOM_CHART_CONFIG = {
    'enabled': True,
    'default_options': {
        'chartType': 'bar',
        'colors': ['#1f77b4', '#ff7f0e', '#2ca02c']
    }
}
```

## Usage
1. Navigate to the Chart creation page
2. Select "Custom Chart" from the visualization type dropdown
3. Configure your data source and metrics
4. Customize chart options
5. Save and view your chart

## Configuration Options

### Basic Options
- **Chart Type**: Choose between bar, line, scatter, or custom
- **Color Palette**: Define custom colors for data series
- **Animation Duration**: Set animation speed in milliseconds

### Advanced Options
- **Enable Tooltips**: Show detailed information on hover
- **Enable Zoom**: Allow users to zoom into chart areas
- **Show Legend**: Display chart legend

## API Reference

### Chart Component
```javascript
<CustomChart
  data={chartData}
  height={400}
  width={600}
  formData={configuration}
/>
```

### Data Format
```javascript
{
  columns: ['category', 'value'],
  data: [
    ['Category A', 100],
    ['Category B', 200],
    ['Category C', 150]
  ]
}
```

### Configuration Schema
```javascript
{
  type: 'object',
  properties: {
    chartType: {
      type: 'string',
      enum: ['bar', 'line', 'scatter', 'custom']
    },
    colors: {
      type: 'array',
      items: { type: 'string', format: 'color' }
    }
  }
}
```

## Examples

### Basic Bar Chart
```javascript
const config = {
  chartType: 'bar',
  colors: ['#1f77b4', '#ff7f0e', '#2ca02c'],
  enableTooltip: true
};
```

### Interactive Line Chart
```javascript
const config = {
  chartType: 'line',
  enableZoom: true,
  enableTooltip: true,
  customOptions: {
    animationDuration: 1000,
    showLegend: true
  }
};
```

## Troubleshooting

### Common Issues
1. **Chart not rendering**: Check data format and configuration
2. **Styling issues**: Verify CSS custom properties are set
3. **Performance problems**: Optimize data size and rendering

### Debug Mode
Enable debug mode for detailed logging:
```python
CUSTOM_CHART_DEBUG = True
```

## Contributing
See [CONTRIBUTING.md](./CONTRIBUTING.md) for development guidelines.
```

2. **Deployment Automation**:
```yaml
# .github/workflows/deploy.yml
name: Deploy Custom Chart Plugin

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '16'
          
      - name: Setup Python
        uses: actions/setup-python@v3
        with:
          python-version: '3.9'
          
      - name: Install dependencies
        run: |
          npm install
          pip install -r requirements.txt
          
      - name: Run tests
        run: |
          npm test
          python -m pytest tests/
          
      - name: Run visual tests
        run: |
          npm run test:visual
          
  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v3
        with:
          python-version: '3.9'
          
      - name: Build package
        run: |
          python setup.py sdist bdist_wheel
          
      - name: Upload to PyPI
        uses: pypa/gh-action-pypi-publish@v1.4.2
        with:
          password: ${{ secrets.PYPI_API_TOKEN }}
          
  deploy-docs:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '16'
          
      - name: Install dependencies
        run: npm install
        
      - name: Build documentation
        run: npm run docs:build
        
      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./docs/build
```

3. **Maintenance Procedures**:
```markdown
# Maintenance Guide

## Version Management
- Follow semantic versioning (MAJOR.MINOR.PATCH)
- Update CHANGELOG.md for each release
- Tag releases in Git repository

## Dependency Updates
- Monitor security vulnerabilities
- Update dependencies regularly
- Test thoroughly after updates

## Performance Monitoring
- Monitor chart rendering performance
- Track memory usage
- Optimize data processing

## User Support
- Maintain issue tracker
- Provide documentation updates
- Respond to user feedback

## Release Process
1. Update version in setup.py
2. Update CHANGELOG.md
3. Create release tag
4. Deploy to PyPI
5. Update documentation
6. Announce release
```

**Reference Documents**:
- [Plugin Deployment](https://superset.apache.org/docs/developing-charts-plugins#deployment)
- [Documentation Standards](https://superset.apache.org/docs/developing-charts-plugins#documentation)

---

## Summary

Key custom visualization concepts covered:
- **Plugin Development**: Structure, frontend, backend registration
- **Advanced Configuration**: Options, data transformation, interactions
- **Styling and Theming**: CSS, theme integration, responsive design
- **Testing**: Unit tests, integration tests, visual regression
- **Documentation and Deployment**: Documentation, automation, maintenance

**Next Steps**:
- Create custom chart plugin
- Implement advanced configuration
- Add styling and theming
- Set up comprehensive testing
- Deploy and document plugin