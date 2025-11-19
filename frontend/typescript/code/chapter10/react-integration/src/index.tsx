// React + TypeScript 应用入口文件

import React from 'react';
import { createRoot } from 'react-dom/client';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import userReducer from './store/userSlice';
import App from './App';
import './index.css';

// 创建Redux store
const store = configureStore({
  reducer: {
    users: userReducer
  },
  devTools: process.env.NODE_ENV !== 'production'
});

// 类型导出
export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

// 渲染应用
const container = document.getElementById('root');
if (!container) throw new Error('Failed to find the root element');

const root = createRoot(container);
root.render(
  <React.StrictMode>
    <Provider store={store}>
      <App />
    </Provider>
  </React.StrictMode>
);