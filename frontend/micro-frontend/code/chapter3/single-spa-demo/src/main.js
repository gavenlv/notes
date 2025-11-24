import { registerApplication, start } from 'single-spa';

// 简单的导航高亮功能
function setActiveNavLink() {
  const links = document.querySelectorAll('.nav-link');
  links.forEach(link => {
    link.classList.remove('active');
    if (link.getAttribute('href') === location.hash) {
      link.classList.add('active');
    }
  });
}

// 监听 hash 变化来更新导航高亮
window.addEventListener('hashchange', setActiveNavLink);
setActiveNavLink(); // 初始设置

// 注册 React 应用
registerApplication({
  name: 'react-app',
  app: () => import('./apps/react-app/react.app.js'),
  activeWhen: ['/react']
});

// 注册 Vue 应用
registerApplication({
  name: 'vue-app',
  app: () => import('./apps/vue-app/vue.app.js'),
  activeWhen: ['/vue']
});

// 启动 single-spa
start();