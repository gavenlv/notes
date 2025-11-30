// 简化版任务管理应用演示
// 由于这是演示版本，我们实现了核心功能的简化版本

// 状态管理
class Store {
  constructor(initialState, reducers) {
    this.state = initialState;
    this.reducers = reducers;
    this.listeners = [];
  }
  
  getState() {
    return this.state;
  }
  
  dispatch(action) {
    const prevState = { ...this.state };
    const newState = this.reducers(this.state, action);
    
    const stateChanged = JSON.stringify(prevState) !== JSON.stringify(newState);
    
    if (stateChanged) {
      this.state = newState;
      this.notifyListeners(prevState, action);
    }
    
    return this.state;
  }
  
  subscribe(listener) {
    this.listeners.push(listener);
    
    return () => {
      this.listeners = this.listeners.filter(l => l !== listener);
    };
  }
  
  notifyListeners(prevState, action) {
    this.listeners.forEach(listener => {
      listener(this.state, prevState, action);
    });
  }
}

// 路由器
class Router {
  constructor(routes) {
    this.routes = routes;
    this.currentRoute = null;
    this.init();
  }
  
  init() {
    window.addEventListener('popstate', () => {
      this.handleRouteChange();
    });
    
    window.addEventListener('load', () => {
      this.handleRouteChange();
    });
    
    document.addEventListener('click', (event) => {
      const link = event.target.closest('[data-route]');
      if (link) {
        event.preventDefault();
        const href = link.getAttribute('href');
        this.navigate(href);
      }
    });
    
    this.handleRouteChange();
  }
  
  navigate(path) {
    window.history.pushState({}, '', path);
    this.handleRouteChange();
  }
  
  handleRouteChange() {
    const path = window.location.pathname || '/';
    const route = this.routes.find(r => r.path === path) || { component: 'NotFound' };
    
    this.currentRoute = route;
    this.render();
  }
  
  render() {
    const appContent = document.getElementById('app-content');
    
    appContent.innerHTML = '<div class="text-center p-4">加载中...</div>';
    
    if (window.DemoComponents && window.DemoComponents[this.currentRoute.component]) {
      const component = window.DemoComponents[this.currentRoute.component];
      
      if (typeof component.render === 'function') {
        appContent.innerHTML = component.render();
        component.onMount && component.onMount();
      } else {
        appContent.innerHTML = component;
      }
    } else {
      appContent.innerHTML = '<div class="text-center p-4"><h2>页面未找到</h2></div>';
    }
    
    this.updateActiveNavLinks();
  }
  
  updateActiveNavLinks() {
    document.querySelectorAll('[data-route]').forEach(link => {
      const href = link.getAttribute('href');
      if (href === window.location.pathname) {
        link.classList.add('active');
      } else {
        link.classList.remove('active');
      }
    });
  }
}

// Reducer
function appReducer(state = { tasks: [], user: null, loading: false }, action) {
  switch (action.type) {
    case 'SET_USER':
      return { ...state, user: action.payload };
      
    case 'LOGOUT':
      return { ...state, user: null };
      
    case 'ADD_TASK':
      return { ...state, tasks: [...state.tasks, action.payload] };
      
    case 'UPDATE_TASK':
      return {
        ...state,
        tasks: state.tasks.map(task => 
          task.id === action.payload.id ? action.payload : task
        )
      };
      
    case 'DELETE_TASK':
      return {
        ...state,
        tasks: state.tasks.filter(task => task.id !== action.payload)
      };
      
    case 'SET_LOADING':
      return { ...state, loading: action.payload };
      
    default:
      return state;
  }
}

// 通知服务
class NotificationService {
  static show(message, type = 'info') {
    const container = document.getElementById('notification-container');
    
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    container.appendChild(notification);
    
    // 3秒后自动移除
    setTimeout(() => {
      notification.remove();
    }, 3000);
  }
}

// 模拟任务服务
class TaskService {
  static getAll() {
    // 模拟从API获取任务
    return new Promise(resolve => {
      setTimeout(() => {
        const tasks = [
          { id: '1', title: '学习JavaScript', status: 'completed', category: 'study', dueDate: '2023-06-01', priority: 'high' },
          { id: '2', title: '完成项目报告', status: 'in_progress', category: 'work', dueDate: '2023-06-15', priority: 'medium' },
          { id: '3', title: '健身计划', status: 'pending', category: 'health', dueDate: '2023-06-20', priority: 'low' }
        ];
        resolve(tasks);
      }, 500);
    });
  }
  
  static create(taskData) {
    return new Promise(resolve => {
      setTimeout(() => {
        const newTask = { ...taskData, id: Date.now().toString() };
        resolve(newTask);
      }, 300);
    });
  }
  
  static update(id, taskData) {
    return new Promise(resolve => {
      setTimeout(() => {
        resolve({ ...taskData, id });
      }, 300);
    });
  }
  
  static delete(id) {
    return new Promise(resolve => {
      setTimeout(() => {
        resolve(true);
      }, 200);
    });
  }
}

// 演示组件
const DemoComponents = {
  Demo: {
    render() {
      return `
        <div class="demo-section">
          <h2>JavaScript任务管理应用演示</h2>
          <p>这是一个简化的任务管理应用演示，展示了第11章实战项目中的核心功能。</p>
          
          <div class="demo-tabs">
            <div class="demo-tab active" onclick="switchTab('features')">功能演示</div>
            <div class="demo-tab" onclick="switchTab('architecture')">架构设计</div>
            <div class="demo-tab" onclick="switchTab('code')">核心代码</div>
          </div>
          
          <div id="features-tab" class="demo-content active">
            <h3>功能演示</h3>
            <div class="demo-actions">
              <button onclick="loadTasks()" class="btn btn-primary">加载任务</button>
              <button onclick="addNewTask()" class="btn btn-outline">添加任务</button>
              <button onclick="toggleTaskStatus()" class="btn btn-outline">切换任务状态</button>
            </div>
            <div id="tasks-container">
              <p>点击"加载任务"按钮查看任务列表</p>
            </div>
          </div>
          
          <div id="architecture-tab" class="demo-content">
            <h3>架构设计</h3>
            <div class="code-block">
项目结构:
task-manager/
├── src/
│   ├── components/    # UI组件
│   ├── state/         # 状态管理
│   ├── router/        # 路由系统
│   ├── services/      # 服务层
│   ├── utils/         # 工具函数
│   └── pages/         # 页面组件
├── public/            # 静态资源
└── dist/             # 构建输出
            </div>
            <p>这个项目采用了模块化架构，将功能分离到不同的模块中，提高了代码的可维护性和可扩展性。</p>
          </div>
          
          <div id="code-tab" class="demo-content">
            <h3>核心代码示例</h3>
            <div class="code-block">
// 状态管理 - Redux-like实现
class Store {
  constructor(initialState, reducers) {
    this.state = initialState;
    this.reducers = reducers;
    this.listeners = [];
  }
  
  getState() {
    return this.state;
  }
  
  dispatch(action) {
    const prevState = { ...this.state };
    const newState = this.reducers(this.state, action);
    
    if (JSON.stringify(prevState) !== JSON.stringify(newState)) {
      this.state = newState;
      this.notifyListeners(prevState, action);
    }
    
    return this.state;
  }
}
            </div>
          </div>
        </div>
      `;
    },
    onMount() {
      // 初始化演示
    }
  },
  
  Features: {
    render() {
      return `
        <div class="demo-section">
          <h2>功能特性</h2>
          <ul>
            <li><strong>模块化设计</strong> - 使用ES模块组织代码</li>
            <li><strong>状态管理</strong> - 简化版Redux实现</li>
            <li><strong>路由系统</strong> - 自定义前端路由器</li>
            <li><strong>组件化</strong> - 可复用的UI组件</li>
            <li><strong>异步处理</strong> - Promise和async/await</li>
            <li><strong>事件系统</strong> - 事件委托和处理</li>
            <li><strong>数据持久化</strong> - localStorage集成</li>
            <li><strong>响应式设计</strong> - 适配不同屏幕尺寸</li>
          </ul>
        </div>
      `;
    }
  },
  
  Architecture: {
    render() {
      return `
        <div class="demo-section">
          <h2>架构设计</h2>
          <h3>技术选择</h3>
          <ul>
            <li><strong>核心语言</strong>: ES2021+ JavaScript</li>
            <li><strong>构建工具</strong>: Vite</li>
            <li><strong>状态管理</strong>: 自定义实现</li>
            <li><strong>路由</strong>: 自定义路由器</li>
            <li><strong>样式</strong>: 原生CSS</li>
          </ul>
          
          <h3>设计原则</h3>
          <ul>
            <li><strong>关注点分离</strong> - 将UI、状态、逻辑分离</li>
            <li><strong>单一职责</strong> - 每个模块只负责一个功能</li>
            <li><strong>可测试性</strong> - 代码易于测试</li>
            <li><strong>可扩展性</strong> - 易于添加新功能</li>
          </ul>
        </div>
      `;
    }
  },
  
  Technologies: {
    render() {
      return `
        <div class="demo-section">
          <h2>技术栈</h2>
          
          <h3>核心JavaScript特性</h3>
          <div class="code-block">
// ES6+ 特性
- 类和继承
- 箭头函数
- 解构赋值
- Promise/async-await
- 模块系统
- 扩展运算符
          </div>
          
          <h3>高级特性应用</h3>
          <ul>
            <li><strong>Proxy</strong> - 用于数据验证和观察</li>
            <li><strong>Generator</strong> - 用于异步流程控制</li>
            <li><strong>迭代器</strong> - 用于自定义数据结构遍历</li>
            <li><strong>Reflect</strong> - 用于元编程操作</li>
          </ul>
          
          <h3>设计模式应用</h3>
          <ul>
            <li><strong>观察者模式</strong> - 状态管理和事件系统</li>
            <li><strong>策略模式</strong> - 不同的数据处理策略</li>
            <li><strong>单例模式</strong> - 全局服务实例</li>
            <li><strong>工厂模式</strong> - 组件创建</li>
          </ul>
        </div>
      `;
    }
  },
  
  NotFound: {
    render() {
      return '<div class="demo-section"><h2>页面未找到</h2><p>您访问的页面不存在</p></div>';
    }
  }
};

// 路由配置
const routes = [
  { path: '/demo', component: 'Demo' },
  { path: '/features', component: 'Features' },
  { path: '/architecture', component: 'Architecture' },
  { path: '/technologies', component: 'Technologies' }
];

// 初始化应用
function initializeApp() {
  // 初始化状态管理
  const store = new Store(
    { tasks: [], user: null, loading: false },
    appReducer
  );
  
  // 将store暴露到全局
  window.store = store;
  window.DemoComponents = DemoComponents;
  
  // 初始化路由
  const router = new Router(routes);
  
  // 设置全局事件监听器
  document.getElementById('login-btn').addEventListener('click', () => {
    // 模拟登录
    store.dispatch({
      type: 'SET_USER',
      payload: { id: '1', name: '演示用户', email: 'demo@example.com' }
    });
    
    document.getElementById('auth-buttons').style.display = 'none';
    document.getElementById('user-info').style.display = 'flex';
    document.getElementById('username').textContent = '演示用户';
    
    NotificationService.show('登录成功', 'success');
  });
  
  document.getElementById('logout-btn').addEventListener('click', () => {
    // 模拟退出
    store.dispatch({ type: 'LOGOUT' });
    
    document.getElementById('auth-buttons').style.display = 'flex';
    document.getElementById('user-info').style.display = 'none';
    
    NotificationService.show('已退出登录', 'info');
  });
}

// 演示功能函数
function switchTab(tabName) {
  // 隐藏所有标签内容
  document.querySelectorAll('.demo-content').forEach(tab => {
    tab.classList.remove('active');
  });
  
  // 移除所有按钮的active类
  document.querySelectorAll('.demo-tab').forEach(btn => {
    btn.classList.remove('active');
  });
  
  // 显示选中的标签内容
  document.getElementById(`${tabName}-tab`).classList.add('active');
  
  // 设置选中按钮的active类
  event.target.classList.add('active');
}

async function loadTasks() {
  const container = document.getElementById('tasks-container');
  container.innerHTML = '<p>正在加载任务...</p>';
  
  try {
    const tasks = await TaskService.getAll();
    
    // 更新状态
    tasks.forEach(task => {
      window.store.dispatch({
        type: 'ADD_TASK',
        payload: task
      });
    });
    
    // 渲染任务列表
    renderTasks(tasks);
    NotificationService.show(`成功加载 ${tasks.length} 个任务`, 'success');
  } catch (error) {
    container.innerHTML = '<p>加载任务失败</p>';
    NotificationService.show('加载任务失败', 'error');
  }
}

function renderTasks(tasks) {
  const container = document.getElementById('tasks-container');
  
  if (tasks.length === 0) {
    container.innerHTML = '<p>暂无任务</p>';
    return;
  }
  
  const tasksHTML = tasks.map(task => {
    const statusClass = task.status === 'completed' ? 'completed' : '';
    const statusText = task.status === 'completed' ? '已完成' : 
                      task.status === 'in_progress' ? '进行中' : '待处理';
    
    return `
      <div class="task-item ${statusClass}" style="border: 1px solid #ddd; padding: 10px; margin-bottom: 10px; border-radius: 5px;">
        <h4>${task.title}</h4>
        <div class="task-meta">
          <span>状态: ${statusText}</span>
          <span style="margin-left: 10px;">分类: ${task.category}</span>
          <span style="margin-left: 10px;">截止日期: ${task.dueDate}</span>
        </div>
        <div style="margin-top: 10px;">
          <button onclick="editTask('${task.id}')" class="btn btn-outline btn-sm">编辑</button>
          <button onclick="deleteTask('${task.id}')" class="btn btn-outline btn-sm">删除</button>
        </div>
      </div>
    `;
  }).join('');
  
  container.innerHTML = tasksHTML;
}

async function addNewTask() {
  const newTask = {
    title: '新任务 ' + Date.now().toString().slice(-4),
    status: 'pending',
    category: 'work',
    dueDate: '2023-07-01',
    priority: 'medium'
  };
  
  try {
    const createdTask = await TaskService.create(newTask);
    
    // 更新状态
    window.store.dispatch({
      type: 'ADD_TASK',
      payload: createdTask
    });
    
    // 重新渲染任务列表
    const state = window.store.getState();
    renderTasks(state.tasks);
    
    NotificationService.show('任务创建成功', 'success');
  } catch (error) {
    NotificationService.show('创建任务失败', 'error');
  }
}

function toggleTaskStatus() {
  const state = window.store.getState();
  const tasks = state.tasks;
  
  if (tasks.length === 0) {
    NotificationService.show('没有可用的任务', 'warning');
    return;
  }
  
  // 随机选择一个未完成的任务
  const incompleteTasks = tasks.filter(task => task.status !== 'completed');
  
  if (incompleteTasks.length === 0) {
    NotificationService.show('所有任务都已完成', 'info');
    return;
  }
  
  const randomTask = incompleteTasks[Math.floor(Math.random() * incompleteTasks.length)];
  const updatedTask = {
    ...randomTask,
    status: randomTask.status === 'pending' ? 'in_progress' : 'completed'
  };
  
  try {
    await TaskService.update(randomTask.id, updatedTask);
    
    // 更新状态
    window.store.dispatch({
      type: 'UPDATE_TASK',
      payload: updatedTask
    });
    
    // 重新渲染任务列表
    renderTasks(window.store.getState().tasks);
    
    NotificationService.show(`任务 "${randomTask.title}" 状态已更新`, 'success');
  } catch (error) {
    NotificationService.show('更新任务状态失败', 'error');
  }
}

function editTask(taskId) {
  NotificationService.show(`编辑任务 ${taskId} 的功能将在完整版中实现`, 'info');
}

async function deleteTask(taskId) {
  if (!confirm('确定要删除这个任务吗？')) {
    return;
  }
  
  try {
    await TaskService.delete(taskId);
    
    // 更新状态
    window.store.dispatch({
      type: 'DELETE_TASK',
      payload: taskId
    });
    
    // 重新渲染任务列表
    renderTasks(window.store.getState().tasks);
    
    NotificationService.show('任务已删除', 'success');
  } catch (error) {
    NotificationService.show('删除任务失败', 'error');
  }
}

// 当DOM加载完成后初始化应用
document.addEventListener('DOMContentLoaded', initializeApp);