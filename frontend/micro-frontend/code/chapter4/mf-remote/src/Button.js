import React from 'react';

const Button = () => {
  const handleClick = () => {
    alert('Button clicked from remote application! This component is shared via Module Federation.');
  };

  return (
    <button 
      onClick={handleClick} 
      style={{ 
        padding: '10px 20px', 
        backgroundColor: '#007bff', 
        color: 'white', 
        border: 'none', 
        borderRadius: '4px', 
        cursor: 'pointer',
        fontSize: '16px'
      }}
    >
      Remote Button (Click Me!)
    </button>
  );
};

export default Button;