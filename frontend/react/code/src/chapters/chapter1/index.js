import React, { useState } from 'react';
import './styles.css';
import JSXDemo from './examples/JSXDemo';
import ComponentDemo from './examples/ComponentDemo';
import PropsDemo from './examples/PropsDemo';
import FirstApp from './examples/FirstApp';

function Chapter1() {
  const [activeExample, setActiveExample] = useState('jsx');

  const examples = [
    { id: 'jsx', title: '1. JSX语法示例', component: JSXDemo },
    { id: 'component', title: '2. 组件使用示例', component: ComponentDemo },
    { id: 'props', title: '3. Props传递示例', component: PropsDemo },
    { id: 'firstApp', title: '4. 第一个React应用', component: FirstApp }
  ];

  const ActiveExampleComponent = examples.find(example => example.id === activeExample)?.component;

  return (
    <div className="chapter-container">
      <div className="example-tabs">
        {examples.map(example => (
          <button
            key={example.id}
            className={`example-tab ${activeExample === example.id ? 'active' : ''}`}
            onClick={() => setActiveExample(example.id)}
          >
            {example.title}
          </button>
        ))}
      </div>
      
      <div className="example-content">
        {ActiveExampleComponent && <ActiveExampleComponent />}
      </div>
    </div>
  );
}

export default Chapter1;