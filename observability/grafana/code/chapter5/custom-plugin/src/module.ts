import { PanelPlugin } from '@grafana/data';
import { SimpleOptions } from 'types';
import { SimpleStatPanel } from './SimpleStatPanel';
import { SimpleStatEditor } from './SimpleStatEditor';

export const plugin = new PanelPlugin<SimpleOptions>(SimpleStatPanel).setPanelOptions((builder) => {
  return builder
    .addTextInput({
      path: 'title',
      name: '标题',
      description: '自定义面板标题',
      defaultValue: '',
    })
    .addTextInput({
      path: 'prefix',
      name: '前缀',
      description: '数值前显示的前缀字符',
      defaultValue: '',
    })
    .addTextInput({
      path: 'suffix',
      name: '后缀',
      description: '数值后显示的后缀字符',
      defaultValue: '',
    })
    .addNumberInput({
      path: 'decimals',
      name: '小数位数',
      description: '数值显示的小数位数',
      defaultValue: 2,
    })
    .addSwitch({
      path: 'showTrend',
      name: '显示趋势',
      description: '是否显示数值趋势',
      defaultValue: false,
    })
    .addNumberInput({
      path: 'warningThreshold',
      name: '警告阈值',
      description: '警告级别阈值',
      defaultValue: 70,
    })
    .addNumberInput({
      path: 'threshold',
      name: '危险阈值',
      description: '危险级别阈值',
      defaultValue: 90,
    });
});

plugin.setEditor(SimpleStatEditor);