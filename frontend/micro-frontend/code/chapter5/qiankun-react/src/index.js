import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

// 为了让主应用能够正确识别子应用，需要添加一些生命周期函数
export async function bootstrap() {
  console.log('React app bootstraped');
}

export async function mount(props) {
  console.log('React app mounted');
  const root = ReactDOM.createRoot(document.getElementById('root'));
  root.render(<App />);
}

export async function unmount(props) {
  console.log('React app unmounted');
  const root = ReactDOM.createRoot(document.getElementById('root'));
  root.unmount();
}