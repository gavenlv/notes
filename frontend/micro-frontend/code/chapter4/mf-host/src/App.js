import React, { useState } from 'react';

// 懒加载远程组件
const RemoteButton = React.lazy(() => import('remote/Button'));
const RemoteHeader = React.lazy(() => import('remote/Header'));

const App = () => {
  const [showRemote, setShowRemote] = useState(false);

  return (
    <div className="container">
      <h1>Host Application</h1>
      <p>This is the host application consuming remote components via Module Federation.</p>
      
      <div>
        <button 
          onClick={() => setShowRemote(!showRemote)}
          style={{ 
            padding: '10px 20px', 
            backgroundColor: '#28a745', 
            color: 'white', 
            border: 'none', 
            borderRadius: '4px', 
            cursor: 'pointer',
            marginRight: '10px'
          }}
        >
          {showRemote ? 'Hide' : 'Show'} Remote Components
        </button>
      </div>

      {showRemote && (
        <div className="remote-component">
          <h2>Remote Components:</h2>
          <React.Suspense fallback="Loading Remote Button...">
            <RemoteButton />
          </React.Suspense>
          
          <React.Suspense fallback="Loading Remote Header...">
            <RemoteHeader />
          </React.Suspense>
        </div>
      )}

      <div style={{ marginTop: '20px' }}>
        <h3>Host Application Features:</h3>
        <ul>
          <li>Consumes remote components via Module Federation</li>
          <li>Uses React.lazy for dynamic loading</li>
          <li>Shares React and ReactDOM dependencies</li>
        </ul>
      </div>
    </div>
  );
};

export default App;