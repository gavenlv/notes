import React, { useState, useEffect } from 'react';

// 这是一个用于演示代码分割的大型组件
// 在实际项目中，这种组件会包含复杂的功能和大型依赖
const LazyLoadedComponent = () => {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    // 模拟组件的初始化工作
    // console.log('LazyLoadedComponent 已加载');
  }, []);

  return (
    <div className="lazy-loaded-component">
      <h3>懒加载组件示例</h3>
      <p>这个组件是通过 React.lazy 和 Suspense 懒加载的。</p>
      <p>组件状态: {mounted ? '已挂载' : '未挂载'}</p>
      <div className="component-info">
        <h4>代码分割的优势:</h4>
        <ul>
          <li>减小初始加载的 JavaScript 包体积</li>
          <li>按需加载，只在需要时下载代码</li>
          <li>提高首屏加载速度和用户体验</li>
          <li>更好的代码组织和维护性</li>
        </ul>
      </div>
    </div>
  );
};

export default LazyLoadedComponent;