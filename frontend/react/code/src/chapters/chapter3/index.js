import React, { useState } from 'react';
import { StateBasicsDemo } from './examples/StateBasicsDemo';
import { EventHandlingDemo } from './examples/EventHandlingDemo';
import { FormsDemo } from './examples/FormsDemo';
import { TaskManagerDemo } from './examples/TaskManagerDemo';

export const Chapter3Page = () => {
  const [activeExample, setActiveExample] = useState('state-basics');

  return (
    <div className="chapter-page">
      <div className="chapter-header">
        <h1>第3章：状态与事件处理</h1>
        <p>深入学习React状态管理和事件处理机制</p>
      </div>

      <div className="example-navigation">
        <button 
          className={activeExample === 'state-basics' ? 'active' : ''} 
          onClick={() => setActiveExample('state-basics')}
        >
          状态基础
        </button>
        <button 
          className={activeExample === 'events' ? 'active' : ''} 
          onClick={() => setActiveExample('events')}
        >
          事件处理
        </button>
        <button 
          className={activeExample === 'forms' ? 'active' : ''} 
          onClick={() => setActiveExample('forms')}
        >
          表单处理
        </button>
        <button 
          className={activeExample === 'task-manager' ? 'active' : ''} 
          onClick={() => setActiveExample('task-manager')}
        >
          任务管理应用
        </button>
      </div>

      <div className="example-content">
        {activeExample === 'state-basics' && <StateBasicsDemo />}
        {activeExample === 'events' && <EventHandlingDemo />}
        {activeExample === 'forms' && <FormsDemo />}
        {activeExample === 'task-manager' && <TaskManagerDemo />}
      </div>
    </div>
  );
};

export default Chapter3Page;