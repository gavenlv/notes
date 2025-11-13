import React, { useState } from 'react';

// 基本点击事件
function ClickEventExample() {
  const [clickCount, setClickCount] = useState(0);
  const [message, setMessage] = useState('');
  
  const handleClick = () => {
    const newCount = clickCount + 1;
    setClickCount(newCount);
    setMessage(`你点击了 ${newCount} 次`);
  };
  
  const handleDoubleClick = () => {
    alert('你双击了按钮！');
  };
  
  return (
    <div className="example-section">
      <h3>点击事件处理</h3>
      
      <div className="example-group">
        <p>点击次数: {clickCount}</p>
        <p>{message}</p>
        <button onClick={handleClick}>点击我</button>
        <button onDoubleClick={handleDoubleClick}>双击我</button>
      </div>
    </div>
  );
}

// 鼠标事件
function MouseEventExample() {
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const [isHovering, setIsHovering] = useState(false);
  
  const handleMouseMove = (e) => {
    setMousePosition({
      x: e.clientX,
      y: e.clientY
    });
  };
  
  const handleMouseEnter = () => {
    setIsHovering(true);
  };
  
  const handleMouseLeave = () => {
    setIsHovering(false);
  };
  
  return (
    <div className="example-section">
      <h3>鼠标事件处理</h3>
      
      <div className="example-group">
        <p>鼠标位置: ({mousePosition.x}, {mousePosition.y})</p>
        <p>悬停状态: {isHovering ? '悬停中' : '未悬停'}</p>
        <div 
          className="mouse-area"
          onMouseMove={handleMouseMove}
          onMouseEnter={handleMouseEnter}
          onMouseLeave={handleMouseLeave}
        >
          在这个区域移动鼠标
        </div>
      </div>
    </div>
  );
}

// 键盘事件
function KeyboardEventExample() {
  const [keyPressed, setKeyPressed] = useState('');
  const [keyInfo, setKeyInfo] = useState('');
  const [inputValue, setInputValue] = useState('');
  
  const handleKeyDown = (e) => {
    setKeyPressed(e.key);
    setKeyInfo(`键码: ${e.keyCode}, 是否Shift: ${e.shiftKey}, 是否Ctrl: ${e.ctrlKey}`);
    
    // 特殊键处理
    if (e.key === 'Enter') {
      alert('你按下了回车键！');
    } else if (e.key === 'Escape') {
      setInputValue('');
    }
  };
  
  const handleKeyPress = (e) => {
    console.log('KeyPress事件:', e.key);
  };
  
  const handleKeyUp = (e) => {
    console.log('KeyUp事件:', e.key);
  };
  
  return (
    <div className="example-section">
      <h3>键盘事件处理</h3>
      
      <div className="example-group">
        <p>按下的键: {keyPressed}</p>
        <p>键信息: {keyInfo}</p>
        <p>输入值: {inputValue}</p>
        
        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={handleKeyDown}
          onKeyPress={handleKeyPress}
          onKeyUp={handleKeyUp}
          placeholder="在这里输入并按键"
        />
      </div>
    </div>
  );
}

// 表单事件
function FormEventExample() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    selectValue: 'option1',
    isChecked: false
  });
  
  const [isSubmitted, setIsSubmitted] = useState(false);
  
  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };
  
  const handleSubmit = (e) => {
    e.preventDefault(); // 阻止默认提交行为
    setIsSubmitted(true);
    console.log('表单数据:', formData);
  };
  
  const handleReset = (e) => {
    // 重置表单
    setFormData({
      name: '',
      email: '',
      selectValue: 'option1',
      isChecked: false
    });
    setIsSubmitted(false);
  };
  
  return (
    <div className="example-section">
      <h3>表单事件处理</h3>
      
      {isSubmitted && (
        <div className="success-message">
          表单提交成功！数据: {JSON.stringify(formData)}
        </div>
      )}
      
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>姓名:</label>
          <input
            type="text"
            name="name"
            value={formData.name}
            onChange={handleChange}
          />
        </div>
        
        <div className="form-group">
          <label>邮箱:</label>
          <input
            type="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
          />
        </div>
        
        <div className="form-group">
          <label>选择:</label>
          <select
            name="selectValue"
            value={formData.selectValue}
            onChange={handleChange}
          >
            <option value="option1">选项1</option>
            <option value="option2">选项2</option>
            <option value="option3">选项3</option>
          </select>
        </div>
        
        <div className="form-group">
          <label>
            <input
              type="checkbox"
              name="isChecked"
              checked={formData.isChecked}
              onChange={handleChange}
            />
            同意条款
          </label>
        </div>
        
        <div className="form-group">
          <button type="submit">提交</button>
          <button type="button" onClick={handleReset}>重置</button>
        </div>
      </form>
    </div>
  );
}

// 事件对象
function EventObjectExample() {
  const [eventInfo, setEventInfo] = useState('');
  
  const handleClick = (e) => {
    const info = {
      type: e.type,
      target: e.target.tagName,
      currentTarget: e.currentTarget.tagName,
      timeStamp: e.timeStamp,
      clientX: e.clientX,
      clientY: e.clientY
    };
    
    setEventInfo(JSON.stringify(info, null, 2));
  };
  
  const handleChildClick = (e) => {
    e.stopPropagation(); // 阻止事件冒泡
    alert('子元素被点击，但事件不会冒泡到父元素');
  };
  
  const handleParentClick = () => {
    alert('父元素被点击');
  };
  
  const handleLinkClick = (e) => {
    e.preventDefault(); // 阻止默认行为
    alert('链接被点击，但不会跳转');
  };
  
  return (
    <div className="example-section">
      <h3>事件对象与事件控制</h3>
      
      <div className="example-group">
        <h4>事件对象信息</h4>
        <button onClick={handleClick}>点击查看事件对象</button>
        <pre>{eventInfo}</pre>
      </div>
      
      <div className="example-group">
        <h4>事件冒泡与阻止冒泡</h4>
        <div onClick={handleParentClick} className="parent-box">
          父元素 (点击会触发)
          <div onClick={handleChildClick} className="child-box">
            子元素 (点击不会冒泡)
          </div>
        </div>
      </div>
      
      <div className="example-group">
        <h4>阻止默认行为</h4>
        <a 
          href="https://example.com" 
          onClick={handleLinkClick}
        >
          点击此链接 (不会跳转)
        </a>
      </div>
    </div>
  );
}

// 事件绑定方式
function EventBindingExample() {
  const [message, setMessage] = useState('');
  
  // 方式1: 箭头函数
  const handleArrowClick = () => {
    setMessage('箭头函数方式绑定事件');
  };
  
  // 方式2: 类组件中的绑定 (此处演示函数组件中的等效方式)
  // 在类组件中，通常需要在构造函数中绑定或使用箭头函数方法
  
  // 方式3: 内联箭头函数
  const updateMessage = (msg) => {
    setMessage(msg);
  };
  
  // 方式4: 带参数的事件处理
  const handleClickWithParams = (e, param1, param2) => {
    setMessage(`参数1: ${param1}, 参数2: ${param2}, 事件类型: ${e.type}`);
  };
  
  return (
    <div className="example-section">
      <h3>事件绑定方式</h3>
      
      <div className="example-group">
        <h4>不同的事件绑定方式</h4>
        <button onClick={handleArrowClick}>方式1: 箭头函数</button>
        <button onClick={() => updateMessage('内联函数方式')}>方式2: 内联函数</button>
        <button onClick={(e) => handleClickWithParams(e, '参数1', '参数2')}>
          方式3: 带参数的事件处理
        </button>
      </div>
      
      <div className="message-display">
        <p>消息: {message}</p>
      </div>
    </div>
  );
}

// 自定义事件
function CustomEventExample() {
  const [customEventData, setCustomEventData] = useState('');
  
  // 创建自定义事件
  const fireCustomEvent = () => {
    const customEvent = new CustomEvent('myCustomEvent', {
      detail: { message: '这是自定义事件', timestamp: Date.now() }
    });
    
    document.dispatchEvent(customEvent);
    setCustomEventData('已触发自定义事件，检查控制台');
  };
  
  // 监听自定义事件
  React.useEffect(() => {
    const handleCustomEvent = (e) => {
      console.log('自定义事件触发:', e.detail);
      setCustomEventData(`自定义事件数据: ${e.detail.message}, 时间戳: ${e.detail.timestamp}`);
    };
    
    document.addEventListener('myCustomEvent', handleCustomEvent);
    
    return () => {
      document.removeEventListener('myCustomEvent', handleCustomEvent);
    };
  }, []);
  
  return (
    <div className="example-section">
      <h3>自定义事件</h3>
      
      <div className="example-group">
        <button onClick={fireCustomEvent}>触发自定义事件</button>
        <p>{customEventData}</p>
        <p>打开控制台查看自定义事件的详细信息</p>
      </div>
    </div>
  );
}

export const EventHandlingDemo = () => {
  return (
    <div className="demo-container">
      <div className="demo-description">
        <h2>事件处理示例</h2>
        <p>本示例演示了React中各种事件的处理方式，包括鼠标事件、键盘事件、表单事件、事件对象和自定义事件等。</p>
      </div>

      <div className="examples-grid">
        <ClickEventExample />
        <MouseEventExample />
        <KeyboardEventExample />
        <FormEventExample />
        <EventObjectExample />
        <EventBindingExample />
        <CustomEventExample />
      </div>
      
      <div className="demo-info">
        <h3>事件处理要点</h3>
        <ul>
          <li>React事件使用驼峰命名法，如onClick而非onclick</li>
          <li>事件处理函数接收合成事件对象，兼容性更好</li>
          <li>使用e.stopPropagation()阻止事件冒泡</li>
          <li>使用e.preventDefault()阻止默认行为</li>
          <li>箭头函数绑定事件是最推荐的方式，避免了this问题</li>
          <li>表单提交时记得调用e.preventDefault()阻止默认刷新</li>
        </ul>
      </div>
    </div>
  );
};