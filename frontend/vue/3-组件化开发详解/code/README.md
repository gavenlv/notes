# 第三章代码示例说明

## 目录结构
```
src/
├── components/
│   ├── UserCard.vue           # 用户卡片组件
│   ├── CollapsiblePanel.vue   # 可折叠面板组件
│   ├── FormWithValidation.vue # 带验证的表单组件
│   ├── Notification.vue       # 通知组件
│   ├── ImageLazyLoad.vue      # 图片懒加载组件
│   └── EventBus.js            # 事件总线
├── App.vue                    # 根组件
└── main.js                    # 入口文件
```

## 代码示例说明

### 1. UserCard.vue - 用户卡片组件
展示如何创建一个可复用的用户卡片组件，支持通过props传递用户信息。

### 2. CollapsiblePanel.vue - 可折叠面板组件
实现一个带动画效果的可折叠面板组件，展示组件状态管理和动画处理。

### 3. FormWithValidation.vue - 带验证的表单组件
演示如何创建带表单验证功能的组件，以及如何通过自定义事件向父组件传递验证结果。

### 4. Notification.vue - 通知组件
创建一个可复用的通知组件，展示如何使用作用域插槽和动态组件。

### 5. ImageLazyLoad.vue - 图片懒加载组件
结合Intersection Observer API实现图片懒加载功能，展示异步组件的概念。

### 6. EventBus.js - 事件总线
实现组件间通信的事件总线机制。

## 运行步骤
1. 确保已安装所有依赖：`npm install`
2. 启动开发服务器：`npm run serve`
3. 在浏览器中访问：http://localhost:8080

## 代码特点
- 展示了Vue 3 Composition API的使用
- 包含完整的组件通信示例
- 涵盖插槽、动态组件等高级特性
- 提供实际应用场景的解决方案

## 学习建议
1. 先理解每个组件的功能和实现方式
2. 尝试修改组件的props和事件处理逻辑
3. 练习创建自己的组件变体
4. 思考如何将这些组件应用到实际项目中