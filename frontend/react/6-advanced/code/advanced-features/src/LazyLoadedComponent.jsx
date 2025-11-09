import { useEffect } from 'react';

const LazyLoadedComponent = () => {
  useEffect(() => {
    console.log('懒加载组件已加载');
  }, []);

  return (
    <div className="lazy-loaded-component">
      <h3>懒加载组件已成功加载！</h3>
      <p>这个组件是通过 React.lazy 和 Suspense 动态加载的。</p>
      <p>代码分割可以帮助减少初始加载时间，提高应用性能。</p>
      <div className="lazy-features">
        <ul>
          <li>按需加载，减少初始 bundle 大小</li>
          <li>提升首屏加载速度</li>
          <li>改善用户体验</li>
          <li>优化网络资源利用</li>
        </ul>
      </div>
    </div>
  );
};

export default LazyLoadedComponent;
