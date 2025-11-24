import React from 'react';

const Header = () => {
  return (
    <header style={{ 
      backgroundColor: '#343a40', 
      color: 'white', 
      padding: '20px', 
      borderRadius: '4px',
      marginBottom: '20px'
    }}>
      <h2>Remote Header Component</h2>
      <p>This header component is exposed via Module Federation and can be consumed by other applications.</p>
    </header>
  );
};

export default Header;