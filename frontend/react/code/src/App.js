import React, { useState } from 'react';
import './index.css';

// 导入各章节的示例组件
import Chapter1 from './chapters/chapter1';
import Chapter2 from './chapters/chapter2';
import Chapter3 from './chapters/chapter3';
import Chapter4 from './chapters/chapter4';

function App() {
  const [activeChapter, setActiveChapter] = useState(1);

  const chapters = [
    { id: 1, title: '第一章：React基础入门', component: Chapter1 },
    { id: 2, title: '第二章：组件与Props', component: Chapter2 },
    { id: 3, title: '第三章：状态与事件处理', component: Chapter3 },
    { id: 4, title: '第四章：条件渲染与列表渲染', component: Chapter4 }
  ];

  const ActiveChapterComponent = chapters.find(chapter => chapter.id === activeChapter)?.component;

  return (
    <div className="app">
      <div className="nav-container">
        <h1>React从零到专家 - 实践代码示例</h1>
        <div className="nav-tabs">
          {chapters.map(chapter => (
            <button
              key={chapter.id}
              className={`nav-tab ${activeChapter === chapter.id ? 'active' : ''}`}
              onClick={() => setActiveChapter(chapter.id)}
            >
              {chapter.title}
            </button>
          ))}
        </div>
      </div>
      
      <div className="content-area">
        {ActiveChapterComponent && <ActiveChapterComponent />}
      </div>
    </div>
  );
}

export default App;