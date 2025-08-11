# 高级前端面试问题及答案

## 1. JavaScript 深入理解

### 问题1: 解释 JavaScript 中的闭包及其应用场景
**答案:**
闭包是指函数能够访问其词法作用域之外的变量，即使该函数在其定义作用域之外执行。闭包由函数及其词法环境组成。

应用场景:
- 模块化开发 (创建私有变量和方法)
- 函数柯里化
- 定时器和事件处理程序
- 回调函数

示例:
```javascript
function createCounter() {
  let count = 0;
  return function() {
    return ++count;
  };
}
const counter = createCounter();
console.log(counter()); // 1
console.log(counter()); // 2
```

### 问题2: 解释 JavaScript 的原型链和继承机制
**答案:**
JavaScript 是基于原型的语言，每个对象都有一个原型对象，它继承属性和方法。原型链是对象通过 `__proto__` 属性连接起来的链式结构，用于查找属性和方法。

继承机制:
- 通过原型链继承
- 构造函数继承
- 组合继承
- ES6 Class 继承 (语法糖)

示例:
```javascript
// 原型链继承
function Animal(name) {
  this.name = name;
}
Animal.prototype.speak = function() {
  console.log(`${this.name} makes a noise.`);
};

function Dog(name) {
  Animal.call(this, name);
}
Dog.prototype = Object.create(Animal.prototype);
Dog.prototype.constructor = Dog;
Dog.prototype.speak = function() {
  console.log(`${this.name} barks.`);
};

const dog = new Dog('Rex');
dog.speak(); // Rex barks.
```

### 问题3: 解释 JavaScript 的事件循环机制
**答案:**
JavaScript 是单线程的，事件循环是处理异步操作的机制。事件循环的核心是：执行栈、宏任务队列和微任务队列。

执行流程:
1. 执行同步代码，将异步任务放入相应队列
2. 执行栈为空时，执行所有微任务
3. 执行一个宏任务
4. 重复 2-3 步骤

宏任务: setTimeout, setInterval, I/O 操作
微任务: Promise.then, MutationObserver, process.nextTick

## 2. 前端框架与库

### 问题4: React 和 Vue 的核心区别是什么？各自的优势在哪里？
**答案:**
React 和 Vue 都是流行的前端框架，但有以下核心区别:

1. **数据流向**: React 是单向数据流，Vue 支持双向数据绑定
2. **组件化**: React 使用 JSX，Vue 使用模板语法
3. **状态管理**: React 使用 Redux 等外部库，Vue 内置 Vuex/Pinia
4. **虚拟 DOM**: React 使用 diff 算法，Vue 有更精细的依赖追踪

React 优势:
- 生态系统更丰富
- 更适合大型应用
- 函数式编程风格
- 跨平台能力强 (React Native)

Vue 优势:
- 上手更容易
- 文档更友好
- 性能优秀
- 更贴近传统 Web 开发模式

### 问题5: 解释 React Hooks 的工作原理及使用注意事项
**答案:**
Hooks 是 React 16.8 引入的特性，允许在函数组件中使用状态和生命周期等特性。

工作原理:
- Hooks 依赖调用顺序，必须在组件顶层调用
- React 内部维护一个链表来存储 Hooks 的状态
- 每次组件渲染时，按顺序遍历 Hooks 链表

使用注意事项:
- 不要在循环、条件或嵌套函数中调用 Hooks
- 使用 ESLint 插件确保 Hooks 规则被遵循
- 理解闭包在 Hooks 中的影响
- 注意 useEffect 的依赖数组

示例:
```javascript
function Counter() {
  const [count, setCount] = useState(0);
  const [name, setName] = useState('');

  useEffect(() => {
    document.title = `Count: ${count}`;
  }, [count]); // 仅在 count 变化时执行

  return (
    <div>
      <input value={name} onChange={e => setName(e.target.value)} />
      <button onClick={() => setCount(count + 1)}>Increment</button>
      <p>Count: {count}</p>
    </div>
  );
}
```

## 3. 性能优化

### 问题6: 如何优化大型 React 应用的性能？
**答案:**
1. **组件优化**: 使用 React.memo, useMemo, useCallback 减少不必要的重渲染
2. **虚拟列表**: 对于长列表，使用 react-window 或 react-virtualized 只渲染可见项
3. **代码分割**: 使用 React.lazy 和 Suspense 实现按需加载
4. **状态管理优化**: 合理设计状态结构，避免不必要的状态更新
5. **渲染优化**: 避免在渲染过程中创建函数和对象
6. **图片优化**: 使用适当的图片格式和大小，实现懒加载
7. **服务端渲染**: 使用 Next.js 等框架实现服务端渲染
8. **性能监控**: 使用 React DevTools Profiler 分析性能瓶颈

### 问题7: 解释网页加载过程中的关键渲染路径及优化方法
**答案:**
关键渲染路径是浏览器将 HTML、CSS 和 JavaScript 转换为可见网页的过程。

主要步骤:
1. 解析 HTML 生成 DOM 树
2. 解析 CSS 生成 CSSOM 树
3. 合并 DOM 和 CSSOM 生成渲染树
4. 布局 (计算元素位置和大小)
5. 绘制 (将像素绘制到屏幕上)
6. 合成 (将图层组合并显示)

优化方法:
- 最小化关键资源大小
- 减少关键资源数量
- 优化关键路径长度
- 预加载关键资源
- 延迟加载非关键资源
- 优化 CSS 选择器
- 避免阻塞渲染的 JavaScript

## 4. 前端工程化

### 问题8: 解释 Webpack 的工作原理及优化策略
**答案:**
Webpack 是一个模块打包器，将多个模块打包成一个或多个 bundle。

工作原理:
1. 入口: 从指定的入口文件开始
2. 依赖解析: 递归解析所有依赖
3. 转换: 使用 loader 转换非 JavaScript 文件
4. 优化: 应用插件进行代码优化
5. 输出: 将打包后的文件输出到指定目录

优化策略:
- 代码分割: 分割 vendor 和 app 代码
- 懒加载: 实现按需加载
- 资源压缩: 使用 TersPlugin 压缩 JavaScript，MiniCssExtractPlugin 压缩 CSS
- 缓存优化: 配置 contenthash 实现浏览器缓存
- 并行构建: 使用 thread-loader 或 happyPack 加速构建
- 减小打包体积: 移除无用代码，使用 tree-shaking

### 问题9: 什么是微前端？有哪些实现方式？
**答案:**
微前端是一种架构模式，将大型前端应用拆分为多个独立的小型应用，每个应用可以独立开发、测试和部署。

实现方式:
1. **iframe**: 简单但性能较差，隔离性最好
2. **Web Components**: 基于标准，但浏览器支持不完全
3. **模块联邦**: Webpack 5 提供的功能，实现应用间模块共享
4. **路由分发**: 根据路由将请求分发到不同的子应用
5. **组合式应用**: 使用 JavaScript 框架将多个应用组合到一起

优势:
- 技术栈无关
- 独立部署
- 代码隔离
- 团队自治

## 5. 浏览器原理与安全

### 问题10: 解释浏览器的同源策略及跨域解决方案
**答案:**
同源策略是浏览器的安全机制，限制不同源的文档或脚本如何相互访问。同源指协议、域名和端口都相同。

跨域解决方案:
1. **CORS**: 服务器设置 Access-Control-Allow-Origin 等响应头
2. **JSONP**: 利用 script 标签没有跨域限制的特性
3. **代理服务器**: 开发环境使用 Webpack Dev Server 代理，生产环境使用 Nginx 代理
4. **postMessage**: 不同窗口间通信
5. **WebSocket**: 不受同源策略限制
6. **document.domain**: 适用于主域相同、子域不同的情况

### 问题11: 如何防止 XSS 攻击？
**答案:**
XSS (跨站脚本攻击) 是攻击者将恶意脚本注入到网页中，当用户访问时执行的攻击方式。

防护措施:
1. **输入验证**: 对用户输入进行严格验证和过滤
2. **输出编码**: 对输出到页面的内容进行 HTML 编码
3. **CSP (内容安全策略)**: 限制资源加载和脚本执行
4. **使用 React/Vue 等框架**: 这些框架会自动转义用户输入
5. **避免使用 eval 和 innerHTML**: 这些方法容易导致 XSS 攻击
6. **设置 HttpOnly 标志**: 防止 cookie 被窃取

## 6. 设计模式与架构

### 问题12: 解释观察者模式和发布-订阅模式的区别及应用场景
**答案:**
观察者模式和发布-订阅模式都是用于实现对象间通信的设计模式。

观察者模式:
- 观察者直接订阅被观察者
- 被观察者维护观察者列表
- 被观察者状态变化时直接通知所有观察者
- 耦合度较高

发布-订阅模式:
- 引入了消息中间件 (发布者和订阅者之间的中介)
- 发布者不直接知道订阅者
- 订阅者不直接知道发布者
- 耦合度较低

应用场景:
- 观察者模式: 组件间通信 (如 React 中的父子组件通信)
- 发布-订阅模式: 跨组件、跨模块通信 (如 Vue 中的事件总线)

### 问题13: 什么是 MVVM 架构？它解决了什么问题？
**答案:**
MVVM (Model-View-ViewModel) 是一种软件架构模式，将应用分为三个部分:
- Model: 数据模型和业务逻辑
- View: 用户界面
- ViewModel: 连接 Model 和 View 的桥梁，负责数据绑定和命令转发

MVVM 解决的问题:
1. **关注点分离**: 将 UI 和业务逻辑分离
2. **减少模板代码**: 通过数据绑定减少手动 DOM 操作
3. **提高可测试性**: 可以单独测试 ViewModel
4. **双向数据绑定**: 实现 UI 和数据的自动同步

Vue 和 Angular 是基于 MVVM 架构的前端框架。