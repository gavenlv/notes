import React from 'react';
import { PanelEditorProps } from '@grafana/data';
import { SimpleOptions } from 'types';
import { Switch, InputNumber, ColorPicker, TextInput } from '@grafana/ui';

interface Props extends PanelEditorProps<SimpleOptions> {}

export const SimpleStatEditor: React.FC<Props> = ({ options, onOptionsChange }) => {
  return (
    <div>
      <div className="section gf-form-group">
        <h5 className="section-heading">显示选项</h5>
        
        <div className="gf-form">
          <span className="gf-form-label width-10">标题</span>
          <TextInput
            value={options.title || ''}
            onChange={(e) => onOptionsChange({ ...options, title: e.currentTarget.value })}
            placeholder="自定义标题"
            width={20}
          />
        </div>

        <div className="gf-form">
          <span className="gf-form-label width-10">前缀</span>
          <TextInput
            value={options.prefix || ''}
            onChange={(e) => onOptionsChange({ ...options, prefix: e.currentTarget.value })}
            placeholder="$"
            width={10}
          />
        </div>

        <div className="gf-form">
          <span className="gf-form-label width-10">后缀</span>
          <TextInput
            value={options.suffix || ''}
            onChange={(e) => onOptionsChange({ ...options, suffix: e.currentTarget.value })}
            placeholder="ms"
            width={10}
          />
        </div>

        <div className="gf-form">
          <span className="gf-form-label width-10">小数位数</span>
          <InputNumber
            value={options.decimals || 2}
            onChange={(value) => onOptionsChange({ ...options, decimals: value })}
            min={0}
            max={10}
            width={10}
          />
        </div>

        <div className="gf-form">
          <span className="gf-form-label width-10">显示趋势</span>
          <Switch
            value={options.showTrend || false}
            onChange={(value) => onOptionsChange({ ...options, showTrend: value })}
          />
        </div>
      </div>

      <div className="section gf-form-group">
        <h5 className="section-heading">阈值设置</h5>
        
        <div className="gf-form">
          <span className="gf-form-label width-10">警告阈值</span>
          <InputNumber
            value={options.warningThreshold || 70}
            onChange={(value) => onOptionsChange({ ...options, warningThreshold: value })}
            min={0}
            max={100}
            width={10}
          />
        </div>

        <div className="gf-form">
          <span className="gf-form-label width-10">危险阈值</span>
          <InputNumber
            value={options.threshold || 90}
            onChange={(value) => onOptionsChange({ ...options, threshold: value })}
            min={0}
            max={100}
            width={10}
          />
        </div>
      </div>
    </div>
  );
};