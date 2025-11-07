import React from 'react';
import { PanelProps } from '@grafana/data';
import { SimpleOptions } from 'types';
import { useTheme } from '@grafana/ui';
import { stylesFactory } from '@grafana/ui';
import { css } from '@emotion/css';

interface Props extends PanelProps<SimpleOptions> {}

export const SimpleStatPanel: React.FC<Props> = ({ data, width, height, options }) => {
  const theme = useTheme();
  const styles = getStyles(theme);

  // 获取数据系列
  const series = data.series[0];
  const value = series?.fields[1]?.values.get(series.fields[1].values.length - 1) || 0;
  const title = series?.fields[0]?.values.get(series.fields[0].values.length - 1) || 'N/A';

  // 计算颜色
  let color = theme.colors.green;
  if (options.threshold && value > options.threshold) {
    color = theme.colors.red;
  } else if (options.warningThreshold && value > options.warningThreshold) {
    color = theme.colors.orange;
  }

  return (
    <div
      className={styles.wrapper}
      style={{
        width,
        height,
        backgroundColor: theme.colors.background.primary,
        border: `1px solid ${theme.colors.border.weak}`,
      }}
    >
      <div className={styles.title}>{options.title || title}</div>
      <div className={styles.value} style={{ color }}>
        {options.prefix}{value.toFixed(options.decimals || 2)}{options.suffix}
      </div>
      {options.showTrend && (
        <div className={styles.trend}>
          <span>趋势: ↑ 5%</span>
        </div>
      )}
    </div>
  );
};

const getStyles = stylesFactory((theme) => {
  return {
    wrapper: css`
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
      padding: 16px;
      border-radius: 4px;
    `,
    title: css`
      font-size: ${theme.typography.size.sm};
      color: ${theme.colors.text.secondary};
      margin-bottom: 8px;
    `,
    value: css`
      font-size: 36px;
      font-weight: ${theme.typography.weight.bold};
      line-height: 1;
    `,
    trend: css`
      font-size: ${theme.typography.size.xs};
      color: ${theme.colors.text.secondary};
      margin-top: 8px;
    `,
  };
});