import React, { useState } from 'react';
import { ConditionalRenderingDemo } from './examples/ConditionalRenderingDemo';
import { ListRenderingDemo } from './examples/ListRenderingDemo';
import { AdvancedRenderingDemo } from './examples/AdvancedRenderingDemo';
import { DataTableDemo } from './examples/DataTableDemo';

export const Chapter4Page = () => {
  const [activeExample, setActiveExample] = useState('conditional');

  return (
    <div className="chapter-page">
      <div className="chapter-header">
        <h1>第4章：条件渲染与列表渲染</h1>
        <p>学习动态构建React UI的核心技术</p>
      </div>

      <div className="example-navigation">
        <button 
          className={activeExample === 'conditional' ? 'active' : ''} 
          onClick={() => setActiveExample('conditional')}
        >
          条件渲染
        </button>
        <button 
          className={activeExample === 'list' ? 'active' : ''} 
          onClick={() => setActiveExample('list')}
        >
          列表渲染
        </button>
        <button 
          className={activeExample === 'advanced' ? 'active' : ''} 
          onClick={() => setActiveExample('advanced')}
        >
          高级渲染
        </button>
        <button 
          className={activeExample === 'datatable' ? 'active' : ''} 
          onClick={() => setActiveExample('datatable')}
        >
          数据表格
        </button>
      </div>

      <div className="example-content">
        {activeExample === 'conditional' && <ConditionalRenderingDemo />}
        {activeExample === 'list' && <ListRenderingDemo />}
        {activeExample === 'advanced' && <AdvancedRenderingDemo />}
        {activeExample === 'datatable' && <DataTableDemo />}
      </div>
    </div>
  );
};

export default Chapter4Page;