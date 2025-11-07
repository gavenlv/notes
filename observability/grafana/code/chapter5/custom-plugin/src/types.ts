import { PanelOptions } from '@grafana/data';

export interface SimpleOptions extends PanelOptions {
  title?: string;
  prefix?: string;
  suffix?: string;
  decimals?: number;
  showTrend?: boolean;
  warningThreshold?: number;
  threshold?: number;
  backgroundColor?: string;
  textColor?: string;
}

export interface SimpleStatData {
  title: string;
  value: number;
  trend?: number;
}