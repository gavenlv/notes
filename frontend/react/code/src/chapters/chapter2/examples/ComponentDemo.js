import React, { useState, useEffect } from 'react';

// 函数组件示例
function FunctionComponent({ name, onIncrement }) {
  return (
    <div className="component-example function-component">
      <h3>函数组件</h3>
      <p>你好，{name}！这是一个函数组件。</p>
      <p>函数组件是最简单的React组件定义方式。</p>
      <button onClick={onIncrement}>点击我</button>
    </div>
  );
}

// 类组件示例
class ClassComponent extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      count: 0
    };
  }

  componentDidMount() {
    console.log('类组件已挂载');
  }

  componentDidUpdate() {
    console.log('类组件已更新');
  }

  componentWillUnmount() {
    console.log('类组件将卸载');
  }

  handleIncrement = () => {
    this.setState({
      count: this.state.count + 1
    });
  }

  render() {
    return (
      <div className="component-example class-component">
        <h3>类组件</h3>
        <p>你好，{this.props.name}！这是一个类组件。</p>
        <p>计数器: {this.state.count}</p>
        <p>类组件可以拥有内部状态和生命周期方法。</p>
        <button onClick={this.handleIncrement}>增加计数</button>
      </div>
    );
  }
}

// 使用Hooks的函数组件
function HooksComponent({ name }) {
  const [count, setCount] = useState(0);
  const [isVisible, setIsVisible] = useState(true);

  useEffect(() => {
    console.log('Hooks组件已挂载或更新');
    
    return () => {
      console.log('Hooks组件将卸载或更新前清理');
    };
  }, [count]); // 只在count变化时执行

  return (
    <div className="component-example hooks-component">
      <h3>Hooks函数组件</h3>
      <p>你好，{name}！这是一个使用Hooks的函数组件。</p>
      <p>计数器: {count}</p>
      <p>组件可见性: {isVisible ? '可见' : '隐藏'}</p>
      
      <div className="button-group">
        <button onClick={() => setCount(count + 1)}>增加计数</button>
        <button onClick={() => setIsVisible(!isVisible)}>
          {isVisible ? '隐藏' : '显示'}
        </button>
      </div>
      
      {!isVisible && (
        <div className="hidden-content">
          这是隐藏的内容，切换可见性可以看到它。
        </div>
      )}
    </div>
  );
}

export const ComponentDemo = () => {
  const [clickCount, setClickCount] = useState(0);
  const [showClassComponent, setShowClassComponent] = useState(true);

  const handleFunctionButtonClick = () => {
    setClickCount(clickCount + 1);
  };

  return (
    <div className="demo-container">
      <div className="demo-description">
        <h2>React组件类型示例</h2>
        <p>React支持多种组件类型，包括函数组件、类组件和使用Hooks的函数组件。</p>
        <p>函数组件是最简单和推荐的方式，而类组件更适合需要复杂状态管理的场景。</p>
      </div>

      <div className="examples-grid">
        <FunctionComponent 
          name="React学习者" 
          onIncrement={handleFunctionButtonClick} 
        />
        
        {showClassComponent && (
          <div>
            <ClassComponent name="类组件用户" />
            <button 
              onClick={() => setShowClassComponent(false)}
              className="toggle-button"
            >
              卸载类组件
            </button>
          </div>
        )}
        
        {!showClassComponent && (
          <button 
            onClick={() => setShowClassComponent(true)}
            className="toggle-button"
          >
            挂载类组件
          </button>
        )}
        
        <HooksComponent name="Hooks用户" />
      </div>

      <div className="demo-info">
        <h3>交互信息</h3>
        <p>函数组件按钮被点击了 {clickCount} 次</p>
        <p>打开浏览器控制台，可以看到组件的生命周期日志。</p>
      </div>
    </div>
  );
};