import React, { useState, useEffect } from 'react';

const App = () => {
  const [count, setCount] = useState(0);
  const [message, setMessage] = useState('Hello from React App!');

  useEffect(() => {
    console.log('React App mounted');
    
    // 监听来自其他应用的消息
    const handleMessage = (event) => {
      if (event.detail && event.detail.type === 'from-vue') {
        setMessage(`Received from Vue: ${event.detail.data}`);
      }
    };

    window.addEventListener('app-message', handleMessage);
    
    return () => {
      window.removeEventListener('app-message', handleMessage);
    };
  }, []);

  const sendMessageToVue = () => {
    const event = new CustomEvent('app-message', {
      detail: {
        type: 'from-react',
        data: `Hello from React! Count is ${count}`
      }
    });
    window.dispatchEvent(event);
  };

  return (
    <div style={{ padding: '20px', border: '2px solid #61dafb', borderRadius: '8px' }}>
      <h1>React 微应用</h1>
      <p>{message}</p>
      <div>
        <button onClick={() => setCount(count + 1)}>
          计数器: {count}
        </button>
        <button onClick={sendMessageToVue} style={{ marginLeft: '10px' }}>
          发送消息给 Vue 应用
        </button>
      </div>
      <div style={{ marginTop: '20px' }}>
        <h3>React 应用特点：</h3>
        <ul>
          <li>使用 React Hooks 管理状态</li>
          <li>通过 Custom Events 实现应用间通信</li>
          <li>独立开发和部署</li>
        </ul>
      </div>
    </div>
  );
};

export default App;