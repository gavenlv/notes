import React from 'react';
import { ComponentDemo } from './examples/ComponentDemo';
import { PropsDemo } from './examples/PropsDemo';
import { CompositionDemo } from './examples/CompositionDemo';
import { UserManagementSystem } from './examples/UserManagementSystem';

export const Chapter2Page = () => {
  const [activeExample, setActiveExample] = React.useState('component');

  return (
    <div className="chapter-page">
      <div className="chapter-header">
        <h1>第2章：组件与Props</h1>
        <p>深入学习React组件系统和Props使用</p>
      </div>

      <div className="example-navigation">
        <button 
          className={activeExample === 'component' ? 'active' : ''} 
          onClick={() => setActiveExample('component')}
        >
          组件类型
        </button>
        <button 
          className={activeExample === 'props' ? 'active' : ''} 
          onClick={() => setActiveExample('props')}
        >
          Props使用
        </button>
        <button 
          className={activeExample === 'composition' ? 'active' : ''} 
          onClick={() => setActiveExample('composition')}
        >
          组件组合
        </button>
        <button 
          className={activeExample === 'user-system' ? 'active' : ''} 
          onClick={() => setActiveExample('user-system')}
        >
          用户管理系统
        </button>
      </div>

      <div className="example-content">
        {activeExample === 'component' && <ComponentDemo />}
        {activeExample === 'props' && <PropsDemo />}
        {activeExample === 'composition' && <CompositionDemo />}
        {activeExample === 'user-system' && <UserManagementSystem />}
      </div>
    </div>
  );
};

export default Chapter2Page;