import React from 'react';
import Button from './Button';
import Header from './Header';

const App = () => {
  return (
    <div className="container">
      <h1>Remote Application</h1>
      <p>This is the remote application exposing components via Module Federation.</p>
      
      <div className="component">
        <h2>Exposed Button Component:</h2>
        <Button />
      </div>
      
      <div className="component">
        <h2>Exposed Header Component:</h2>
        <Header />
      </div>

      <div style={{ marginTop: '20px' }}>
        <h3>Remote Application Features:</h3>
        <ul>
          <li>Exposes components via Module Federation</li>
          <li>Can be run independently</li>
          <li>Shares React and ReactDOM dependencies</li>
        </ul>
      </div>
    </div>
  );
};

export default App;