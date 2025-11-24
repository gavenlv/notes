import { registerMicroApps, start } from 'qiankun';

// 注册子应用
registerMicroApps([
  {
    name: 'react-app',
    entry: '//localhost:3002',
    container: '#react-app',
    activeRule: '/react',
  },
  {
    name: 'vue-app',
    entry: '//localhost:3003',
    container: '#vue-app',
    activeRule: '/vue',
  },
]);

// 启动 qiankun
start();