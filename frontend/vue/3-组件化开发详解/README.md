# 第三章：组件化开发详解

## 概述
本章将深入探讨Vue.js组件化开发的核心概念和实践技巧。我们将学习如何创建可复用、可维护的组件，掌握组件间通信的各种方式，以及如何组织大型项目的组件结构。

## 内容目录
1. [组件基础回顾](#组件基础回顾)
2. [组件通信详解](#组件通信详解)
   - Props向下传递数据
   - 自定义事件向上传递信息
   - 非父子组件通信
   - provide/inject跨层级通信
3. [插槽(Slots)深度解析](#插槽slots深度解析)
   - 默认插槽
   - 具名插槽
   - 作用域插槽
4. [动态组件与异步组件](#动态组件与异步组件)
   - component is 特性
   - keep-alive缓存组件
   - 异步组件加载
5. [组件生命周期详解](#组件生命周期详解)
6. [组件样式作用域](#组件样式作用域)
7. [高阶组件(HOC)模式](#高阶组件hoc模式)
8. [组件库设计原则](#组件库设计原则)
9. [本章小结](#本章小结)
10. [实践练习](#实践练习)

## 组件基础回顾
### 什么是组件？
组件是Vue.js中最强大的功能之一。它们帮助我们将UI拆分成独立的、可复用的部分，并且可以嵌套使用。

### 组件注册
#### 全局注册
```javascript
import { createApp } from 'vue'
import MyComponent from './MyComponent.vue'

const app = createApp({})
app.component('MyComponent', MyComponent)
```

#### 局部注册
```javascript
import ComponentA from './ComponentA.vue'
import ComponentB from './ComponentB.vue'

export default {
  components: {
    ComponentA,
    ComponentB
  }
}
```

## 组件通信详解
### Props向下传递数据
Props是父组件向子组件传递数据的主要方式。

#### 基本用法
```javascript
// 父组件
<template>
  <child-component :title="pageTitle" :likes="100" :is-published="true"></child-component>
</template>

// 子组件
export default {
  props: ['title', 'likes', 'isPublished'],
  template: `
    <div>
      <h1>{{ title }}</h1>
      <p>Likes: {{ likes }}</p>
      <p>Status: {{ isPublished ? 'Published' : 'Draft' }}</p>
    </div>
  `
}
```

#### Prop验证
```javascript
export default {
  props: {
    title: {
      type: String,
      required: true
    },
    likes: {
      type: Number,
      default: 0
    },
    isPublished: {
      type: Boolean,
      default: false
    },
    commentIds: {
      type: Array,
      default: () => []
    },
    author: {
      type: Object,
      default: () => ({})
    }
  }
}
```

### 自定义事件向上传递信息
子组件通过$emit触发事件向父组件传递信息。

```javascript
// 子组件
<template>
  <button @click="$emit('enlarge-text', 0.1)">
    Enlarge text
  </button>
</template>

// 父组件
<template>
  <blog-post 
    @enlarge-text="postFontSize += $event"
  ></blog-post>
</template>
```

### 非父子组件通信
对于非父子组件间的通信，我们可以使用事件总线或状态管理模式。

#### 使用mitt库实现事件总线
```javascript
// eventBus.js
import mitt from 'mitt'
export default mitt()

// 组件A
import bus from './eventBus.js'
export default {
  methods: {
    sendMessage() {
      bus.emit('message', 'Hello from Component A')
    }
  }
}

// 组件B
import bus from './eventBus.js'
export default {
  created() {
    bus.on('message', (data) => {
      console.log(data)
    })
  }
}
```

### provide/inject跨层级通信
provide和inject主要用于祖先组件向其所有子孙组件注入依赖。

```javascript
// 祖先组件
export default {
  provide() {
    return {
      theme: this.theme,
      userName: this.userName
    }
  },
  data() {
    return {
      theme: 'dark',
      userName: 'John Doe'
    }
  }
}

// 后代组件
export default {
  inject: ['theme', 'userName'],
  template: `
    <div :class="theme">
      Welcome, {{ userName }}!
    </div>
  `
}
```

## 插槽(Slots)深度解析
插槽是Vue实现内容分发的API，用来封装需要灵活定制的组件。

### 默认插槽
```javascript
// 定义组件
<template>
  <div class="container">
    <header>
      <!-- 我们希望把页头放这里 -->
    </header>
    <main>
      <slot></slot>
    </main>
    <footer>
      <!-- 我们希望把页脚放这里 -->
    </footer>
  </div>
</template>

// 使用组件
<base-layout>
  <p>A paragraph for the main content.</p>
  <p>And another one.</p>
</base-layout>
```

### 具名插槽
```javascript
// 定义组件
<template>
  <div class="container">
    <header>
      <slot name="header"></slot>
    </header>
    <main>
      <slot></slot>
    </main>
    <footer>
      <slot name="footer"></slot>
    </footer>
  </div>
</template>

// 使用组件
<base-layout>
  <template #header>
    <h1>Here might be a page title</h1>
  </template>

  <template #default>
    <p>A paragraph for the main content.</p>
    <p>And another one.</p>
  </template>

  <template #footer>
    <p>Here's some contact info</p>
  </template>
</base-layout>
```

### 作用域插槽
```javascript
// 定义组件
<template>
  <ul>
    <li v-for="(item, index) in items">
      <slot :item="item" :index="index"></slot>
    </li>
  </ul>
</template>

// 使用组件
<current-user>
  <template #default="slotProps">
    {{ slotProps.item.name }}
  </template>
</current-user>
```

## 动态组件与异步组件
### component is 特性
```javascript
<component :is="currentComponent"></component>

data() {
  return {
    currentComponent: 'HomePage'
  }
}
```

### keep-alive缓存组件
```javascript
<keep-alive>
  <component :is="currentComponent"></component>
</keep-alive>
```

### 异步组件加载
```javascript
// Vue 3
const AsyncComponent = defineAsyncComponent(() =>
  import('./components/AsyncComponent.vue')
)

// 带选项的异步组件
const AsyncComponentWithOptions = defineAsyncComponent({
  loader: () => import('./components/AsyncComponent.vue'),
  loadingComponent: LoadingComponent,
  errorComponent: ErrorComponent,
  delay: 200,
  timeout: 3000
})
```

## 组件生命周期详解
Vue组件有多个生命周期钩子函数，让我们可以在特定阶段执行代码：

1. setup()
2. beforeCreate()
3. created()
4. beforeMount()
5. mounted()
6. beforeUpdate()
7. updated()
8. beforeUnmount()
9. unmounted()

```javascript
export default {
  beforeCreate() {
    console.log('beforeCreate')
  },
  created() {
    console.log('created')
  },
  beforeMount() {
    console.log('beforeMount')
  },
  mounted() {
    console.log('mounted')
  },
  beforeUpdate() {
    console.log('beforeUpdate')
  },
  updated() {
    console.log('updated')
  },
  beforeUnmount() {
    console.log('beforeUnmount')
  },
  unmounted() {
    console.log('unmounted')
  }
}
```

## 组件样式作用域
### Scoped CSS
```vue
<style scoped>
.example {
  color: red;
}
</style>
```

### CSS Modules
```vue
<template>
  <p :class="$style.red">
    This should be red
  </p>
</template>

<style module>
.red {
  color: red;
}
</style>
```

## 高阶组件(HOC)模式
高阶组件是一个函数，接收一个组件并返回一个新的组件。

```javascript
// withAuth.js
import { h } from 'vue'

export default function withAuth(Component) {
  return {
    name: `withAuth${Component.name}`,
    setup(props, { slots }) {
      // 认证逻辑
      const isAuthenticated = checkAuth()
      
      if (!isAuthenticated) {
        return () => h('div', 'You need to login first!')
      }
      
      return () => h(Component, props, slots)
    }
  }
}
```

## 组件库设计原则
1. 单一职责原则：每个组件应该只负责一个功能
2. 可组合性：组件应该易于组合使用
3. 可配置性：提供合理的默认值和可配置选项
4. 可扩展性：支持插槽和事件以便于扩展
5. 文档完整性：提供完整的API文档和使用示例

## 本章小结
在本章中，我们深入学习了Vue.js组件化开发的各个方面：
1. 掌握了组件的基本概念和注册方式
2. 理解了组件间通信的各种机制
3. 学会了插槽的使用方法和场景
4. 了解了动态组件和异步组件的应用
5. 熟悉了组件生命周期和样式作用域
6. 掌握了高阶组件模式和组件库设计原则

## 实践练习
1. 创建一个用户卡片组件，支持传入用户信息并展示
2. 实现一个可折叠面板组件，支持展开/收起动画效果
3. 开发一个表单验证高阶组件，可以为任意表单组件添加验证功能
4. 设计一个通知组件，支持不同类型的通知消息显示
5. 构建一个图片懒加载组件，结合Intersection Observer API实现