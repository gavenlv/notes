import React, { useState } from 'react';
import './index.css';

// 导入各章节的示例组件
import Chapter1 from './chapters/chapter1';
import Chapter2 from './chapters/chapter2';

function App() {
  const [activeChapter, setActiveChapter] = useState(1);

  const chapters = [
    { id: 1, title: '第一章：React基础入门', component: Chapter1 },
    { id: 2, title: '第二章：组件与Props', component: Chapter2 }
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