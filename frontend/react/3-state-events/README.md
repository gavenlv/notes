# 第3章：状态与事件处理 - 构建交互式React应用

## 章节介绍

状态(state)和事件处理是React应用的核心概念，它们使得组件能够响应用户操作并动态更新UI。理解状态管理和事件处理机制是构建交互式React应用的基础。

本章将深入探讨：
- 状态的概念与重要性
- useState Hook的全面使用
- 事件处理机制与最佳实践
- 表单处理与受控组件
- 状态管理模式与常见问题
- 自定义Hook入门

通过本章学习，你将掌握如何构建响应用户操作的交互式React组件。

## 状态(State)的概念

### 什么是状态？

在React中，状态是组件的私有数据，它描述了组件在特定时间点的UI表现。当状态发生变化时，React会重新渲染组件以反映新的状态。

状态具有以下特点：
1. **私有性** - 状态是组件私有的，其他组件无法直接访问
2. **可变性** - 状态可以被组件自身修改
3. **驱动渲染** - 状态变化会触发组件重新渲染
4. **不可变性原则** - 状态应该被视为不可变的，总是通过替换而非修改来更新

### 为什么需要状态？

想象一个简单的计数器应用：
- 当前计数值需要存储在某个地方
- 当用户点击按钮时，计数值需要增加
- UI需要显示最新的计数值

这些需求都需要通过状态来实现：
- 计数值存储在状态中
- 点击按钮触发状态更新
- 状态变化导致UI重新渲染

### 状态 vs Props

状态和Props都是组件的数据，但它们有本质区别：

| 特性 | State (状态) | Props (属性) |
|------|-------------|--------------|
| 来源 | 组件内部 | 父组件传递 |
| 可变性 | 可变的 | 只读的 |
| 作用 | 描述组件自身状态 | 描述组件配置 |
| 修改 | 组件内部通过setter修改 | 父组件重新渲染时修改 |

```jsx
function Counter({ initialValue }) { // initialValue 是Props
  const [count, setCount] = useState(initialValue); // count 是State
  
  return (
    <div>
      <p>Props初始值: {initialValue}</p>
      <p>当前计数: {count}</p>
      <button onClick={() => setCount(count + 1)}>增加</button>
    </div>
  );
}
```

## useState Hook深入理解

### 基本用法

useState是React提供的最基础的状态Hook，它返回一个数组，包含当前状态值和更新函数：

```jsx
import { useState } from 'react';

// 基本语法
const [stateVariable, setStateFunction] = useState(initialValue);

// 示例：计数器
function Counter() {
  const [count, setCount] = useState(0); // 初始值为0
  
  return (
    <div>
      <p>当前计数: {count}</p>
      <button onClick={() => setCount(count + 1)}>增加</button>
    </div>
  );
}
```

### 状态更新方式

#### 1. 直接替换值

```jsx
const [name, setName] = useState('初始名称');

// 直接替换
setName('新名称'); 
```

#### 2. 函数式更新

当新状态值依赖于前一个状态时，推荐使用函数式更新，避免竞态条件：

```jsx
const [count, setCount] = useState(0);

// 函数式更新
setCount(prevCount => prevCount + 1);

// 如果连续多次更新，函数式更新更安全
const handleIncrement = () => {
  setCount(prevCount => prevCount + 1);
  setCount(prevCount => prevCount + 1);
  setCount(prevCount => prevCount + 1);
  // 最终结果是当前值+3，而不是+1
};
```

### 不同类型的状态

#### 原始类型

```jsx
const [number, setNumber] = useState(0);
const [string, setString] = useState('');
const [boolean, setBoolean] = useState(false);
const [isNull, setIsNull] = useState(null);
```

#### 对象类型

```jsx
const [user, setUser] = useState({
  name: '',
  age: 0,
  email: ''
});

// 更新对象 - 必须合并旧状态
const updateUser = () => {
  setUser(prevUser => ({
    ...prevUser,
    name: '新名称'
  }));
  // 错误方式：直接修改属性
  // user.name = '新名称'; // 这不会触发重新渲染
  // setUser(user);
};
```

#### 数组类型

```jsx
const [items, setItems] = useState([]);

// 添加元素
const addItem = (newItem) => {
  setItems(prevItems => [...prevItems, newItem]);
};

// 删除元素
const removeItem = (index) => {
  setItems(prevItems => prevItems.filter((_, i) => i !== index));
};

// 更新元素
const updateItem = (index, newValue) => {
  setItems(prevItems => 
    prevItems.map((item, i) => i === index ? newValue : item)
  );
};
```

### 惰性初始状态

如果初始状态需要通过复杂计算得出，可以传递一个函数给useState，这个函数只在组件首次渲染时执行一次：

```jsx
// 每次渲染都会执行expensiveComputation
const [data, setData] = useState(expensiveComputation());

// 只在首次渲染时执行expensiveComputation
const [data, setData] = useState(() => expensiveComputation());

// 示例：从本地存储加载初始状态
const [settings, setSettings] = useState(() => {
  const savedSettings = localStorage.getItem('userSettings');
  return savedSettings ? JSON.parse(savedSettings) : {
    theme: 'light',
    fontSize: 'medium'
  };
});
```

## 事件处理机制

### 事件系统概述

React实现了自己的事件系统，它封装了原生DOM事件，提供了跨浏览器的一致性接口。React事件系统具有以下特点：

1. **跨浏览器兼容性** - 处理不同浏览器的差异
2. **事件委托** - 所有事件委托到根节点
3. **合成事件** - 提供统一的API接口
4. **性能优化** - 减少事件监听器数量

### 事件绑定方式

#### 1. 箭头函数绑定

```jsx
function ButtonExample() {
  const [count, setCount] = useState(0);
  
  // 箭头函数方式
  const handleClick = () => {
    setCount(count + 1);
  };
  
  return <button onClick={handleClick}>点击次数: {count}</button>;
}
```

#### 2. 内联箭头函数

```jsx
function ButtonExample() {
  const [count, setCount] = useState(0);
  
  return (
    <button onClick={() => setCount(count + 1)}>
      点击次数: {count}
    </button>
  );
}
```

#### 3. 类组件中的绑定方式

```jsx
class ButtonExample extends React.Component {
  constructor(props) {
    super(props);
    this.state = { count: 0 };
    
    // 方式1：在构造函数中绑定
    this.handleClick = this.handleClick.bind(this);
  }
  
  // 方式2：使用箭头函数（推荐）
  handleClick = () => {
    this.setState({ count: this.state.count + 1 });
  }
  
  // 方式3：内联绑定（性能较差）
  // handleClick() {
  //   this.setState({ count: this.state.count + 1 });
  // }
  
  render() {
    return (
      <div>
        <button onClick={this.handleClick}>
          方式1/2: 点击次数: {this.state.count}
        </button>
        
        {/* <button onClick={() => this.handleClick()}>
          方式3: 点击次数: {this.state.count}
        </button> */}
      </div>
    );
  }
}
```

### 常见事件类型

#### 鼠标事件

```jsx
function MouseEvents() {
  const [position, setPosition] = useState({ x: 0, y: 0 });
  
  const handleMouseMove = (e) => {
    setPosition({
      x: e.clientX,
      y: e.clientY
    });
  };
  
  return (
    <div 
      onMouseMove={handleMouseMove}
      style={{ height: '200px', backgroundColor: '#f0f0f0' }}
    >
      <p>鼠标位置: ({position.x}, {position.y})</p>
      <button onClick={() => alert('点击了按钮')}>
        点击按钮
      </button>
      <button onMouseEnter={() => console.log('鼠标进入')}
              onMouseLeave={() => console.log('鼠标离开')}>
        悬停效果
      </button>
    </div>
  );
}
```

#### 键盘事件

```jsx
function KeyboardEvents() {
  const [text, setText] = useState('');
  const [keyInfo, setKeyInfo] = useState('');
  
  const handleKeyDown = (e) => {
    setKeyInfo(`按下了: ${e.key}, 键码: ${e.keyCode}`);
    
    // 特殊按键处理
    if (e.key === 'Enter') {
      alert('提交内容: ' + text);
    }
  };
  
  return (
    <div>
      <input 
        type="text"
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="输入内容并按回车"
      />
      <p>{keyInfo}</p>
    </div>
  );
}
```

#### 表单事件

```jsx
function FormEvents() {
  const [formData, setFormData] = useState({
    username: '',
    password: ''
  });
  
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };
  
  const handleSubmit = (e) => {
    e.preventDefault(); // 阻止默认提交行为
    console.log('表单数据:', formData);
  };
  
  return (
    <form onSubmit={handleSubmit}>
      <input 
        name="username"
        value={formData.username}
        onChange={handleChange}
        placeholder="用户名"
      />
      <input 
        name="password"
        type="password"
        value={formData.password}
        onChange={handleChange}
        placeholder="密码"
      />
      <button type="submit">提交</button>
    </form>
  );
}
```

### 事件对象

React的事件对象(SyntheticEvent)包装了原生事件对象，提供了跨浏览器的兼容性：

```jsx
function EventObject() {
  const handleClick = (e) => {
    console.log('事件对象:', e);
    console.log('事件类型:', e.type);
    console.log('目标元素:', e.target);
    console.log('当前元素:', e.currentTarget);
    
    // 获取原生事件对象
    console.log('原生事件:', e.nativeEvent);
    
    // 阻止事件冒泡
    // e.stopPropagation();
    
    // 阻止默认行为
    // e.preventDefault();
  };
  
  return <button onClick={handleClick}>点击查看事件对象</button>;
}
```

## 表单处理与受控组件

### 受控组件概念

受控组件是指表单元素的值由React状态控制，并且通过事件处理函数来更新状态：

```jsx
function ControlledInput() {
  const [value, setValue] = useState('');
  
  const handleChange = (e) => {
    setValue(e.target.value);
  };
  
  return (
    <div>
      <p>输入的值: {value}</p>
      <input 
        type="text"
        value={value}
        onChange={handleChange}
      />
    </div>
  );
}
```

受控组件的特点：
1. 表单元素的值由React状态控制
2. 用户输入通过事件处理函数更新状态
3. React完全控制表单的数据流

### 常见表单元素处理

#### 文本输入框

```jsx
function TextInput() {
  const [value, setValue] = useState('');
  
  return (
    <input 
      type="text"
      value={value}
      onChange={(e) => setValue(e.target.value)}
      placeholder="请输入文本"
    />
  );
}
```

#### 多行文本框

```jsx
function TextArea() {
  const [value, setValue] = useState('');
  
  return (
    <textarea
      value={value}
      onChange={(e) => setValue(e.target.value)}
      placeholder="请输入多行文本"
      rows={4}
    />
  );
}
```

#### 选择框(单选)

```jsx
function SelectBox() {
  const [value, setValue] = useState('option1');
  
  return (
    <select value={value} onChange={(e) => setValue(e.target.value)}>
      <option value="option1">选项1</option>
      <option value="option2">选项2</option>
      <option value="option3">选项3</option>
    </select>
  );
}
```

#### 复选框

```jsx
function Checkbox() {
  const [isChecked, setIsChecked] = useState(false);
  
  return (
    <label>
      <input
        type="checkbox"
        checked={isChecked}
        onChange={(e) => setIsChecked(e.target.checked)}
      />
      同意条款
    </label>
  );
}
```

#### 单选按钮组

```jsx
function RadioGroup() {
  const [gender, setGender] = useState('male');
  
  return (
    <div>
      <label>
        <input
          type="radio"
          value="male"
          checked={gender === 'male'}
          onChange={(e) => setGender(e.target.value)}
        />
        男
      </label>
      <label>
        <input
          type="radio"
          value="female"
          checked={gender === 'female'}
          onChange={(e) => setGender(e.target.value)}
        />
        女
      </label>
      <p>选择的性别: {gender}</p>
    </div>
  );
}
```

### 完整表单示例

```jsx
function CompleteForm() {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    gender: 'male',
    hobbies: [],
    country: 'china',
    description: ''
  });
  
  const [errors, setErrors] = useState({});
  
  // 处理文本/选择框变化
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };
  
  // 处理复选框变化
  const handleCheckboxChange = (e) => {
    const { name, value, checked } = e.target;
    if (checked) {
      setFormData(prev => ({
        ...prev,
        [name]: [...prev[name], value]
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        [name]: prev[name].filter(item => item !== value)
      }));
    }
  };
  
  // 表单验证
  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.username.trim()) {
      newErrors.username = '用户名不能为空';
    }
    
    if (!formData.email.trim()) {
      newErrors.email = '邮箱不能为空';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = '邮箱格式不正确';
    }
    
    if (!formData.password.trim()) {
      newErrors.password = '密码不能为空';
    } else if (formData.password.length < 6) {
      newErrors.password = '密码长度至少6位';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };
  
  // 表单提交
  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (validateForm()) {
      console.log('表单数据:', formData);
      alert('表单提交成功!');
    }
  };
  
  return (
    <form onSubmit={handleSubmit} style={{ maxWidth: '400px', margin: '0 auto' }}>
      <div style={{ marginBottom: '15px' }}>
        <label style={{ display: 'block', marginBottom: '5px' }}>用户名:</label>
        <input 
          type="text"
          name="username"
          value={formData.username}
          onChange={handleChange}
          style={{ width: '100%', padding: '8px' }}
        />
        {errors.username && <p style={{ color: 'red', fontSize: '12px' }}>{errors.username}</p>}
      </div>
      
      <div style={{ marginBottom: '15px' }}>
        <label style={{ display: 'block', marginBottom: '5px' }}>邮箱:</label>
        <input 
          type="email"
          name="email"
          value={formData.email}
          onChange={handleChange}
          style={{ width: '100%', padding: '8px' }}
        />
        {errors.email && <p style={{ color: 'red', fontSize: '12px' }}>{errors.email}</p>}
      </div>
      
      <div style={{ marginBottom: '15px' }}>
        <label style={{ display: 'block', marginBottom: '5px' }}>密码:</label>
        <input 
          type="password"
          name="password"
          value={formData.password}
          onChange={handleChange}
          style={{ width: '100%', padding: '8px' }}
        />
        {errors.password && <p style={{ color: 'red', fontSize: '12px' }}>{errors.password}</p>}
      </div>
      
      <div style={{ marginBottom: '15px' }}>
        <p>性别:</p>
        <label>
          <input
            type="radio"
            name="gender"
            value="male"
            checked={formData.gender === 'male'}
            onChange={handleChange}
          />
          男
        </label>
        <label style={{ marginLeft: '10px' }}>
          <input
            type="radio"
            name="gender"
            value="female"
            checked={formData.gender === 'female'}
            onChange={handleChange}
          />
          女
        </label>
      </div>
      
      <div style={{ marginBottom: '15px' }}>
        <p>爱好:</p>
        <label>
          <input
            type="checkbox"
            name="hobbies"
            value="reading"
            checked={formData.hobbies.includes('reading')}
            onChange={handleCheckboxChange}
          />
          阅读
        </label>
        <label style={{ marginLeft: '10px' }}>
          <input
            type="checkbox"
            name="hobbies"
            value="sports"
            checked={formData.hobbies.includes('sports')}
            onChange={handleCheckboxChange}
          />
          运动
        </label>
        <label style={{ marginLeft: '10px' }}>
          <input
            type="checkbox"
            name="hobbies"
            value="music"
            checked={formData.hobbies.includes('music')}
            onChange={handleCheckboxChange}
          />
          音乐
        </label>
      </div>
      
      <div style={{ marginBottom: '15px' }}>
        <label style={{ display: 'block', marginBottom: '5px' }}>国家:</label>
        <select 
          name="country"
          value={formData.country}
          onChange={handleChange}
          style={{ width: '100%', padding: '8px' }}
        >
          <option value="china">中国</option>
          <option value="usa">美国</option>
          <option value="japan">日本</option>
        </select>
      </div>
      
      <div style={{ marginBottom: '15px' }}>
        <label style={{ display: 'block', marginBottom: '5px' }}>自我介绍:</label>
        <textarea
          name="description"
          value={formData.description}
          onChange={handleChange}
          rows={4}
          style={{ width: '100%', padding: '8px' }}
        />
      </div>
      
      <button 
        type="submit"
        style={{ 
          padding: '10px 20px', 
          backgroundColor: '#007bff', 
          color: 'white', 
          border: 'none',
          cursor: 'pointer'
        }}
      >
        提交
      </button>
    </form>
  );
}
```

## 状态管理模式

### 单一状态 vs 多个状态

对于复杂组件，需要决定使用一个状态对象还是多个独立的状态：

```jsx
// 方式1：多个独立状态
function MultiStateComponent() {
  const [name, setName] = useState('');
  const [age, setAge] = useState(0);
  const [email, setEmail] = useState('');
  
  return (
    <div>
      <input value={name} onChange={(e) => setName(e.target.value)} />
      <input value={age} onChange={(e) => setAge(e.target.value)} />
      <input value={email} onChange={(e) => setEmail(e.target.value)} />
    </div>
  );
}

// 方式2：单一状态对象
function SingleStateComponent() {
  const [formData, setFormData] = useState({
    name: '',
    age: 0,
    email: ''
  });
  
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };
  
  return (
    <div>
      <input name="name" value={formData.name} onChange={handleChange} />
      <input name="age" value={formData.age} onChange={handleChange} />
      <input name="email" value={formData.email} onChange={handleChange} />
    </div>
  );
}
```

选择建议：
- **使用多个独立状态**：当状态之间没有关联，或者你希望简化单个状态的更新逻辑
- **使用状态对象**：当状态之间有紧密关联，或者需要一起更新多个状态

### 状态逻辑复用：自定义Hook入门

当多个组件需要相同的状态逻辑时，可以将其提取为自定义Hook：

```jsx
// 自定义Hook：计数器
function useCounter(initialValue = 0) {
  const [count, setCount] = useState(initialValue);
  
  const increment = () => setCount(prev => prev + 1);
  const decrement = () => setCount(prev => prev - 1);
  const reset = () => setCount(initialValue);
  
  return { count, increment, decrement, reset };
}

// 使用自定义Hook
function Counter() {
  const { count, increment, decrement, reset } = useCounter(10);
  
  return (
    <div>
      <p>当前计数: {count}</p>
      <button onClick={increment}>增加</button>
      <button onClick={decrement}>减少</button>
      <button onClick={reset}>重置</button>
    </div>
  );
}
```

## 常见状态问题与解决方案

### 状态更新不生效

#### 问题：直接修改状态

```jsx
// 错误示例
function ProblemComponent() {
  const [user, setUser] = useState({ name: '张三', age: 30 });
  
  const updateAge = () => {
    // 直接修改状态 - 不会触发重新渲染
    user.age = user.age + 1;
    setUser(user);
  };
  
  return (
    <div>
      <p>姓名: {user.name}, 年龄: {user.age}</p>
      <button onClick={updateAge}>增加年龄</button>
    </div>
  );
}

// 正确解决方案
function SolutionComponent() {
  const [user, setUser] = useState({ name: '张三', age: 30 });
  
  const updateAge = () => {
    // 创建新对象 - 触发重新渲染
    setUser(prevUser => ({
      ...prevUser,
      age: prevUser.age + 1
    }));
  };
  
  return (
    <div>
      <p>姓名: {user.name}, 年龄: {user.age}</p>
      <button onClick={updateAge}>增加年龄</button>
    </div>
  );
}
```

#### 问题：异步更新导致的状态丢失

```jsx
// 问题示例：多次更新状态
function AsyncUpdateProblem() {
  const [count, setCount] = useState(0);
  
  const handleClick = () => {
    // 这些更新可能不会按预期工作，因为setState是异步的
    setCount(count + 1); // 基于count=0
    setCount(count + 1); // 基于count=0
    setCount(count + 1); // 基于count=0
    // 结果可能是1，而不是3
  };
  
  return (
    <div>
      <p>计数: {count}</p>
      <button onClick={handleClick}>增加3次</button>
    </div>
  );
}

// 解决方案：使用函数式更新
function AsyncUpdateSolution() {
  const [count, setCount] = useState(0);
  
  const handleClick = () => {
    // 使用函数式更新确保基于最新状态
    setCount(prev => prev + 1);
    setCount(prev => prev + 1);
    setCount(prev => prev + 1);
    // 结果是3，符合预期
  };
  
  return (
    <div>
      <p>计数: {count}</p>
      <button onClick={handleClick}>增加3次</button>
    </div>
  );
}
```

### 闭包陷阱

当事件处理函数中使用了状态，而状态没有及时更新时，会出现闭包陷阱：

```jsx
// 问题示例
function ClosureProblem() {
  const [count, setCount] = useState(0);
  
  // 使用useEffect创建一个定时器
  useEffect(() => {
    const timer = setInterval(() => {
      // 闭包陷阱：count总是初始值0
      console.log('当前计数:', count);
    }, 1000);
    
    return () => clearInterval(timer);
  }, []); // 依赖数组为空，只在组件挂载时执行一次
  
  return (
    <div>
      <p>计数: {count}</p>
      <button onClick={() => setCount(count + 1)}>增加</button>
    </div>
  );
}

// 解决方案1：使用函数式更新
function ClosureSolution1() {
  const [count, setCount] = useState(0);
  
  useEffect(() => {
    const timer = setInterval(() => {
      // 使用函数式更新获取最新状态
      setCount(prevCount => {
        console.log('当前计数:', prevCount);
        return prevCount;
      });
    }, 1000);
    
    return () => clearInterval(timer);
  }, []);
  
  return (
    <div>
      <p>计数: {count}</p>
      <button onClick={() => setCount(count + 1)}>增加</button>
    </div>
  );
}

// 解决方案2：使用useRef
function ClosureSolution2() {
  const [count, setCount] = useState(0);
  const countRef = useRef(count);
  
  // 更新ref以保持与state同步
  useEffect(() => {
    countRef.current = count;
  }, [count]);
  
  useEffect(() => {
    const timer = setInterval(() => {
      // 使用ref获取最新状态
      console.log('当前计数:', countRef.current);
    }, 1000);
    
    return () => clearInterval(timer);
  }, []);
  
  return (
    <div>
      <p>计数: {count}</p>
      <button onClick={() => setCount(count + 1)}>增加</button>
    </div>
  );
}
```

## 实践案例：构建交互式任务列表

让我们构建一个完整的任务管理应用，综合运用状态管理和事件处理：

```jsx
import { useState } from 'react';

function TaskManager() {
  const [tasks, setTasks] = useState([
    { id: 1, text: '学习React', completed: false },
    { id: 2, text: '完成任务列表', completed: false }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [filter, setFilter] = useState('all'); // all, active, completed
  
  // 添加任务
  const addTask = () => {
    if (inputValue.trim()) {
      const newTask = {
        id: Date.now(),
        text: inputValue,
        completed: false
      };
      
      setTasks(prevTasks => [...prevTasks, newTask]);
      setInputValue('');
    }
  };
  
  // 切换任务完成状态
  const toggleTask = (id) => {
    setTasks(prevTasks =>
      prevTasks.map(task =>
        task.id === id ? { ...task, completed: !task.completed } : task
      )
    );
  };
  
  // 删除任务
  const deleteTask = (id) => {
    setTasks(prevTasks => prevTasks.filter(task => task.id !== id));
  };
  
  // 获取过滤后的任务
  const getFilteredTasks = () => {
    switch (filter) {
      case 'active':
        return tasks.filter(task => !task.completed);
      case 'completed':
        return tasks.filter(task => task.completed);
      default:
        return tasks;
    }
  };
  
  // 获取任务统计
  const getTaskStats = () => {
    const total = tasks.length;
    const completed = tasks.filter(task => task.completed).length;
    const active = total - completed;
    
    return { total, completed, active };
  };
  
  const stats = getTaskStats();
  const filteredTasks = getFilteredTasks();
  
  return (
    <div style={{ maxWidth: '500px', margin: '0 auto', padding: '20px' }}>
      <h1>任务管理</h1>
      
      {/* 输入区域 */}
      <div style={{ marginBottom: '20px', display: 'flex' }}>
        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && addTask()}
          placeholder="添加新任务..."
          style={{ flex: '1', padding: '10px', border: '1px solid #ddd', borderRadius: '4px 0 0 4px' }}
        />
        <button
          onClick={addTask}
          style={{ 
            padding: '10px 15px', 
            border: 'none', 
            backgroundColor: '#28a745', 
            color: 'white',
            borderRadius: '0 4px 4px 0',
            cursor: 'pointer'
          }}
        >
          添加
        </button>
      </div>
      
      {/* 统计信息 */}
      <div style={{ marginBottom: '20px', display: 'flex', justifyContent: 'space-between' }}>
        <span>总计: {stats.total}</span>
        <span>已完成: {stats.completed}</span>
        <span>未完成: {stats.active}</span>
      </div>
      
      {/* 过滤器 */}
      <div style={{ marginBottom: '20px', display: 'flex' }}>
        <button
          onClick={() => setFilter('all')}
          style={{ 
            marginRight: '10px', 
            padding: '5px 10px',
            border: '1px solid #ddd',
            backgroundColor: filter === 'all' ? '#007bff' : 'white',
            color: filter === 'all' ? 'white' : 'black'
          }}
        >
          全部
        </button>
        <button
          onClick={() => setFilter('active')}
          style={{ 
            marginRight: '10px', 
            padding: '5px 10px',
            border: '1px solid #ddd',
            backgroundColor: filter === 'active' ? '#007bff' : 'white',
            color: filter === 'active' ? 'white' : 'black'
          }}
        >
          未完成
        </button>
        <button
          onClick={() => setFilter('completed')}
          style={{ 
            padding: '5px 10px',
            border: '1px solid #ddd',
            backgroundColor: filter === 'completed' ? '#007bff' : 'white',
            color: filter === 'completed' ? 'white' : 'black'
          }}
        >
          已完成
        </button>
      </div>
      
      {/* 任务列表 */}
      <ul style={{ listStyle: 'none', padding: '0' }}>
        {filteredTasks.length === 0 ? (
          <li style={{ textAlign: 'center', color: '#666', padding: '20px' }}>
            {filter === 'all' ? '暂无任务' : 
             filter === 'active' ? '暂无未完成任务' : 
             '暂无已完成任务'}
          </li>
        ) : (
          filteredTasks.map(task => (
            <li 
              key={task.id} 
              style={{ 
                display: 'flex', 
                alignItems: 'center', 
                padding: '10px',
                borderBottom: '1px solid #eee'
              }}
            >
              <input
                type="checkbox"
                checked={task.completed}
                onChange={() => toggleTask(task.id)}
                style={{ marginRight: '10px' }}
              />
              <span 
                style={{ 
                  flex: '1', 
                  textDecoration: task.completed ? 'line-through' : 'none',
                  color: task.completed ? '#666' : 'black'
                }}
              >
                {task.text}
              </span>
              <button
                onClick={() => deleteTask(task.id)}
                style={{ 
                  padding: '5px 10px', 
                  border: 'none', 
                  backgroundColor: '#dc3545', 
                  color: 'white',
                  borderRadius: '4px',
                  cursor: 'pointer'
                }}
              >
                删除
              </button>
            </li>
          ))
        )}
      </ul>
    </div>
  );
}
```

## 最佳实践总结

1. **使用函数式更新**：当新状态依赖于旧状态时，使用函数式更新避免竞态条件。

2. **保持状态扁平化**：避免嵌套过深的状态结构，保持状态扁平化便于更新和维护。

3. **将相关状态分组**：将相关的状态值组织在一个对象中，便于管理。

4. **提取自定义Hook**：将可复用的状态逻辑提取为自定义Hook，提高代码复用性。

5. **使用受控组件**：对于表单元素，使用受控组件模式，让React控制数据流。

6. **避免直接修改状态**：始终使用提供的setter函数更新状态，不要直接修改状态对象。

7. **合理使用useEffect**：注意useEffect的依赖数组，避免不必要的重复执行。

8. **处理事件对象**：理解事件对象的属性和方法，如`stopPropagation()`和`preventDefault()`。

9. **表单验证**：为表单添加适当的验证，提供良好的用户体验。

10. **考虑性能**：对于频繁更新的状态，考虑使用`useCallback`和`useMemo`优化性能。

## 练习项目

1. **待办事项应用**：创建一个功能完整的待办事项应用，包括添加、删除、编辑、标记完成等功能。

2. **购物车系统**：实现一个购物车，包括商品添加、数量调整、价格计算、删除商品等功能。

3. **用户设置面板**：创建一个设置面板，包含主题切换、表单验证、实时预览等功能。

4. **实时搜索组件**：实现一个搜索框，支持防抖、搜索建议、高亮匹配等高级功能。

5. **多步骤表单**：创建一个多步骤向导式表单，包括步骤导航、数据验证、进度保存等功能。

## 总结

本章我们深入学习了React中的状态管理和事件处理机制，包括：

- 状态的概念与重要性
- useState Hook的全面使用
- 事件处理机制与常见事件类型
- 表单处理与受控组件模式
- 状态管理模式与最佳实践
- 常见问题与解决方案
- 自定义Hook入门

状态管理和事件处理是构建交互式React应用的基础。掌握这些概念将使你能够创建响应用户操作、动态更新UI的复杂应用。下一章我们将学习条件渲染与列表渲染，进一步丰富我们的React开发技能。