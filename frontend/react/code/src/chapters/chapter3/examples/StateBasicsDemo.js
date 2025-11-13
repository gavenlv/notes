import React, { useState, useEffect, useRef } from 'react';

// 基本状态使用
function BasicStateExample() {
  const [count, setCount] = useState(0);
  const [text, setText] = useState('');
  const [isVisible, setIsVisible] = useState(false);

  return (
    <div className="example-section">
      <h3>基本状态使用</h3>
      
      <div className="example-group">
        <h4>计数器</h4>
        <p>当前计数: {count}</p>
        <div className="button-group">
          <button onClick={() => setCount(count - 1)}>减少</button>
          <button onClick={() => setCount(count + 1)}>增加</button>
          <button onClick={() => setCount(0)}>重置</button>
        </div>
      </div>
      
      <div className="example-group">
        <h4>文本输入</h4>
        <input 
          type="text" 
          value={text} 
          onChange={(e) => setText(e.target.value)} 
          placeholder="输入一些文本"
        />
        <p>输入的文本: {text}</p>
      </div>
      
      <div className="example-group">
        <h4>可见性切换</h4>
        <button onClick={() => setIsVisible(!isVisible)}>
          {isVisible ? '隐藏' : '显示'}内容
        </button>
        {isVisible && <p>这是可见性切换的内容</p>}
      </div>
    </div>
  );
}

// 对象状态
function ObjectStateExample() {
  const [user, setUser] = useState({
    name: '张三',
    age: 28,
    email: 'zhangsan@example.com',
    address: {
      city: '北京',
      district: '朝阳区'
    }
  });

  const updateName = () => {
    // 错误方式 - 直接修改
    // user.name = '李四';
    // setUser(user);
    
    // 正确方式 - 创建新对象
    setUser(prevUser => ({
      ...prevUser,
      name: prevUser.name === '张三' ? '李四' : '张三'
    }));
  };

  const updateAge = () => {
    setUser(prevUser => ({
      ...prevUser,
      age: prevUser.age + 1
    }));
  };

  const updateCity = () => {
    setUser(prevUser => ({
      ...prevUser,
      address: {
        ...prevUser.address,
        city: prevUser.address.city === '北京' ? '上海' : '北京'
      }
    }));
  };

  return (
    <div className="example-section">
      <h3>对象状态管理</h3>
      
      <div className="user-info">
        <p>姓名: {user.name}</p>
        <p>年龄: {user.age}</p>
        <p>邮箱: {user.email}</p>
        <p>城市: {user.address.city}</p>
        <p>区域: {user.address.district}</p>
      </div>
      
      <div className="button-group">
        <button onClick={updateName}>切换姓名</button>
        <button onClick={updateAge}>增加年龄</button>
        <button onClick={updateCity}>切换城市</button>
      </div>
      
      <div className="code-note">
        <p><strong>注意：</strong>更新对象状态时，必须创建新对象，不能直接修改原对象</p>
        <p>使用展开运算符(...)可以方便地创建新对象</p>
      </div>
    </div>
  );
}

// 数组状态
function ArrayStateExample() {
  const [items, setItems] = useState([
    { id: 1, name: '苹果' },
    { id: 2, name: '香蕉' },
    { id: 3, name: '橙子' }
  ]);

  const [newItem, setNewItem] = useState('');

  const addItem = () => {
    if (newItem.trim()) {
      const id = Date.now();
      setItems(prevItems => [...prevItems, { id, name: newItem }]);
      setNewItem('');
    }
  };

  const deleteItem = (id) => {
    setItems(prevItems => prevItems.filter(item => item.id !== id));
  };

  const updateItem = (id) => {
    const newName = prompt('输入新名称:');
    if (newName && newName.trim()) {
      setItems(prevItems =>
        prevItems.map(item =>
          item.id === id ? { ...item, name: newName } : item
        )
      );
    }
  };

  return (
    <div className="example-section">
      <h3>数组状态管理</h3>
      
      <div className="add-item">
        <input
          type="text"
          value={newItem}
          onChange={(e) => setNewItem(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && addItem()}
          placeholder="输入新项目"
        />
        <button onClick={addItem}>添加</button>
      </div>
      
      <ul className="item-list">
        {items.map(item => (
          <li key={item.id} className="item">
            <span>{item.name}</span>
            <div className="item-actions">
              <button onClick={() => updateItem(item.id)}>编辑</button>
              <button onClick={() => deleteItem(item.id)}>删除</button>
            </div>
          </li>
        ))}
      </ul>
      
      <div className="code-note">
        <p><strong>数组操作：</strong></p>
        <p>添加: [...prevItems, newItem]</p>
        <p>删除: prevItems.filter(item => item.id !== id)</p>
        <p>更新: prevItems.map(item => item.id === id ? newItem : item)</p>
      </div>
    </div>
  );
}

// 状态更新问题与解决方案
function StateUpdateProblems() {
  const [count1, setCount1] = useState(0);
  const [count2, setCount2] = useState(0);
  const [userInfo, setUserInfo] = useState({
    name: '张三',
    age: 30
  });

  // 问题1: 基于当前状态的多次更新
  const problem1 = () => {
    setCount1(count1 + 1); // 基于初始count1=0
    setCount1(count1 + 1); // 基于初始count1=0
    setCount1(count1 + 1); // 基于初始count1=0
    // 结果可能是1，而不是3
  };

  // 解决方案1: 使用函数式更新
  const solution1 = () => {
    setCount2(prevCount => prevCount + 1);
    setCount2(prevCount => prevCount + 1);
    setCount2(prevCount => prevCount + 1);
    // 结果是3，符合预期
  };

  // 问题2: 直接修改对象
  const problem2 = () => {
    userInfo.age = userInfo.age + 1; // 直接修改
    setUserInfo(userInfo); // 引用没变，React可能不会检测到变化
  };

  // 解决方案2: 创建新对象
  const solution2 = () => {
    setUserInfo(prevUser => ({
      ...prevUser,
      age: prevUser.age + 1
    }));
  };

  return (
    <div className="example-section">
      <h3>状态更新问题与解决方案</h3>
      
      <div className="problem-solution">
        <h4>问题1: 基于当前状态的多次更新</h4>
        <div className="example-group">
          <p>计数1(问题): {count1}</p>
          <button onClick={problem1}>增加3次(可能失败)</button>
        </div>
        <div className="example-group">
          <p>计数2(解决): {count2}</p>
          <button onClick={solution1}>增加3次(正确)</button>
        </div>
        <div className="code-note">
          <p>问题: setState是异步的，连续多次使用当前值可能不准确</p>
          <p>解决: 使用函数式更新确保基于最新状态</p>
        </div>
      </div>
      
      <div className="problem-solution">
        <h4>问题2: 直接修改对象</h4>
        <div className="example-group">
          <p>当前用户信息: {userInfo.name}, {userInfo.age}岁</p>
          <button onClick={problem2}>增加年龄(可能失败)</button>
          <button onClick={solution2}>增加年龄(正确)</button>
        </div>
        <div className="code-note">
          <p>问题: 直接修改对象不会触发重新渲染</p>
          <p>解决: 创建新对象，保持状态不可变性</p>
        </div>
      </div>
    </div>
  );
}

// 闭包陷阱演示
function ClosureTrapExample() {
  const [count, setCount] = useState(0);
  const countRef = useRef(count);

  // 更新ref以保持与state同步
  useEffect(() => {
    countRef.current = count;
  }, [count]);

  // 问题: 闭包陷阱
  useEffect(() => {
    const timer = setInterval(() => {
      // 闭包陷阱: count总是初始值0
      console.log('问题 - 当前计数:', count);
    }, 3000);
    
    return () => clearInterval(timer);
  }, []); // 依赖数组为空，只在组件挂载时执行一次

  // 解决方案1: 使用函数式更新
  useEffect(() => {
    const timer = setInterval(() => {
      setCount(prevCount => {
        console.log('方案1 - 当前计数:', prevCount);
        return prevCount;
      });
    }, 3000);
    
    return () => clearInterval(timer);
  }, []);

  // 解决方案2: 使用useRef
  useEffect(() => {
    const timer = setInterval(() => {
      console.log('方案2 - 当前计数:', countRef.current);
    }, 3000);
    
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="example-section">
      <h3>闭包陷阱演示</h3>
      
      <div className="example-group">
        <p>当前计数: {count}</p>
        <button onClick={() => setCount(count + 1)}>增加计数</button>
      </div>
      
      <div className="code-note">
        <p><strong>闭包陷阱:</strong> 在事件处理或effect中，状态值可能不是最新的</p>
        <p><strong>解决方案1:</strong> 使用函数式更新</p>
        <p><strong>解决方案2:</strong> 使用useRef保持最新状态</p>
        <p>打开控制台查看不同方案的结果</p>
      </div>
    </div>
  );
}

// 自定义Hook示例
function useCounter(initialValue = 0) {
  const [count, setCount] = useState(initialValue);
  
  const increment = () => setCount(prevCount => prevCount + 1);
  const decrement = () => setCount(prevCount => prevCount - 1);
  const reset = () => setCount(initialValue);
  
  return { count, increment, decrement, reset };
}

function CustomHookExample() {
  // 使用自定义Hook创建多个计数器
  const counter1 = useCounter(10);
  const counter2 = useCounter(0);
  const counter3 = useCounter(100);
  
  return (
    <div className="example-section">
      <h3>自定义Hook示例</h3>
      
      <div className="example-group">
        <h4>计数器1 (初始值: 10)</h4>
        <p>计数: {counter1.count}</p>
        <div className="button-group">
          <button onClick={counter1.increment}>增加</button>
          <button onClick={counter1.decrement}>减少</button>
          <button onClick={counter1.reset}>重置</button>
        </div>
      </div>
      
      <div className="example-group">
        <h4>计数器2 (初始值: 0)</h4>
        <p>计数: {counter2.count}</p>
        <div className="button-group">
          <button onClick={counter2.increment}>增加</button>
          <button onClick={counter2.decrement}>减少</button>
          <button onClick={counter2.reset}>重置</button>
        </div>
      </div>
      
      <div className="example-group">
        <h4>计数器3 (初始值: 100)</h4>
        <p>计数: {counter3.count}</p>
        <div className="button-group">
          <button onClick={counter3.increment}>增加</button>
          <button onClick={counter3.decrement}>减少</button>
          <button onClick={counter3.reset}>重置</button>
        </div>
      </div>
      
      <div className="code-note">
        <p><strong>自定义Hook:</strong> 将可复用的状态逻辑提取为Hook</p>
        <p>优点: 代码复用、逻辑分离、组件更简洁</p>
      </div>
    </div>
  );
}

export const StateBasicsDemo = () => {
  return (
    <div className="demo-container">
      <div className="demo-description">
        <h2>状态管理基础示例</h2>
        <p>本示例演示了React状态管理的核心概念，包括基本状态使用、对象/数组状态、常见问题及解决方案，以及自定义Hook的使用。</p>
      </div>

      <div className="examples-grid">
        <BasicStateExample />
        <ObjectStateExample />
        <ArrayStateExample />
        <StateUpdateProblems />
        <ClosureTrapExample />
        <CustomHookExample />
      </div>
      
      <div className="demo-info">
        <h3>状态管理要点</h3>
        <ul>
          <li>使用useState Hook管理组件状态</li>
          <li>更新对象或数组时，必须创建新对象/数组，不能直接修改</li>
          <li>当新状态依赖于旧状态时，使用函数式更新</li>
          <li>注意闭包陷阱，使用useRef或函数式更新解决</li>
          <li>将可复用的状态逻辑提取为自定义Hook</li>
        </ul>
      </div>
    </div>
  );
};