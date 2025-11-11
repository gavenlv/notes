import React, { useState } from 'react';

// 基本Props使用
function BasicPropsDemo({ name, age, isStudent }) {
  return (
    <div className="props-example">
      <h3>基本Props使用</h3>
      <p>姓名: {name}</p>
      <p>年龄: {age}</p>
      <p>是否是学生: {isStudent ? '是' : '否'}</p>
    </div>
  );
}

// Props解构与默认值
function DestructuredPropsDemo({ 
  title = "默认标题", 
  content = "默认内容", 
  author = "匿名作者",
  tags = [] 
}) {
  return (
    <div className="props-example">
      <h3>Props解构与默认值</h3>
      <h4>{title}</h4>
      <p>{content}</p>
      <p>作者: {author}</p>
      <div className="tags">
        标签: {tags.map((tag, index) => (
          <span key={index} className="tag">{tag}</span>
        ))}
      </div>
    </div>
  );
}

// Props类型检查（在实际项目中应该使用PropTypes或TypeScript）
function ValidatedPropsDemo({ email, phone, age }) {
  const [errors, setErrors] = useState({});
  
  const validateProps = () => {
    const newErrors = {};
    
    if (!email || !email.includes('@')) {
      newErrors.email = '请输入有效的邮箱地址';
    }
    
    if (!phone || !/^1[3-9]\d{9}$/.test(phone)) {
      newErrors.phone = '请输入有效的手机号码';
    }
    
    if (age && (isNaN(age) || age < 0 || age > 150)) {
      newErrors.age = '年龄必须在0-150之间';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };
  
  return (
    <div className="props-example">
      <h3>Props验证示例</h3>
      <div className="prop-info">
        <div className={errors.email ? 'error' : ''}>
          邮箱: {email || '未提供'} 
          {errors.email && <span className="error-message"> ({errors.email})</span>}
        </div>
        <div className={errors.phone ? 'error' : ''}>
          电话: {phone || '未提供'}
          {errors.phone && <span className="error-message"> ({errors.phone})</span>}
        </div>
        <div className={errors.age ? 'error' : ''}>
          年龄: {age || '未提供'}
          {errors.age && <span className="error-message"> ({errors.age})</span>}
        </div>
      </div>
      <button onClick={validateProps}>验证Props</button>
    </div>
  );
}

// Props的只读性演示
function ReadOnlyPropsDemo({ initialCount }) {
  const [count, setCount] = useState(initialCount || 0);
  const [attempts, setAttempts] = useState(0);
  
  const handleDirectMutationAttempt = () => {
    // 尝试直接修改props（错误做法）
    try {
      // 下面这行代码会报错，因为props是只读的
      // initialCount = 100; // 这行代码会报错
      setAttempts(attempts + 1);
    } catch (error) {
      console.error('不能直接修改Props:', error);
    }
  };
  
  return (
    <div className="props-example">
      <h3>Props只读性演示</h3>
      <p>初始计数 (来自Props): {initialCount}</p>
      <p>当前状态计数: {count}</p>
      <p>尝试直接修改Props的次数: {attempts}</p>
      
      <div className="button-group">
        <button onClick={handleDirectMutationAttempt}>
          尝试直接修改Props (错误做法)
        </button>
        <button onClick={() => setCount(count + 1)}>
          通过状态更新计数 (正确做法)
        </button>
      </div>
      
      <p className="note">
        Props是只读的，不能直接修改。应该通过状态管理或回调函数来实现数据更新。
      </p>
    </div>
  );
}

// 回调函数作为Props
function CallbackPropsDemo({ onButtonClick, onInputChange }) {
  const [inputValue, setInputValue] = useState('');
  
  const handleChange = (e) => {
    const value = e.target.value;
    setInputValue(value);
    if (onInputChange) {
      onInputChange(value);
    }
  };
  
  return (
    <div className="props-example">
      <h3>回调函数Props</h3>
      <p>当前输入: {inputValue}</p>
      <input 
        type="text" 
        value={inputValue} 
        onChange={handleChange}
        placeholder="输入文本"
      />
      <button onClick={() => onButtonClick && onButtonClick(inputValue)}>
        提交数据
      </button>
    </div>
  );
}

// 子组件作为Props (Children)
function ChildrenPropsDemo({ title, children }) {
  return (
    <div className="props-example children-demo">
      <h3>{title}</h3>
      <div className="children-content">
        {children}
      </div>
    </div>
  );
}

export const PropsDemo = () => {
  const [childInput, setChildInput] = useState('');
  
  const handleChildButtonClick = (data) => {
    alert(`来自子组件的数据: ${data}`);
  };
  
  const handleChildInputChange = (value) => {
    setChildInput(value);
  };
  
  return (
    <div className="demo-container">
      <div className="demo-description">
        <h2>Props使用示例</h2>
        <p>Props是React组件之间通信的主要方式。它们是父组件向子组件传递数据的只读对象。</p>
      </div>

      <div className="examples-grid">
        <BasicPropsDemo 
          name="张三" 
          age={28} 
          isStudent={false} 
        />
        
        <DestructuredPropsDemo 
          title="React学习指南" 
          author="前端开发者"
          tags={["React", "JavaScript", "Frontend"]}
        />
        
        <ValidatedPropsDemo 
          email="zhangsan@example.com" 
          phone="13800138000" 
          age="28" 
        />
        
        <ReadOnlyPropsDemo initialCount={10} />
        
        <div className="callback-demo-container">
          <h3>父组件接收的数据</h3>
          <p>来自子组件的输入: {childInput}</p>
          <CallbackPropsDemo 
            onButtonClick={handleChildButtonClick}
            onInputChange={handleChildInputChange}
          />
        </div>
        
        <ChildrenPropsDemo title="Children Props示例">
          <p>这是通过children props传递的内容</p>
          <ul>
            <li>可以是任意JSX元素</li>
            <li>可以是文本</li>
            <li>可以是其他组件</li>
            <li>非常灵活，常用于复合组件</li>
          </ul>
        </ChildrenPropsDemo>
      </div>
      
      <div className="demo-info">
        <h3>Props使用要点</h3>
        <ul>
          <li>Props是只读的，组件不能修改自己的Props</li>
          <li>可以使用解构语法简化Props的访问</li>
          <li>可以为Props设置默认值</li>
          <li>回调函数Props允许子组件与父组件通信</li>
          <li>children是一个特殊的Prop，用于传递组件内容</li>
        </ul>
      </div>
    </div>
  );
};