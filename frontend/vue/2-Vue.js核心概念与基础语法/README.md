# 第二章：Vue.js核心概念与基础语法

## 本章概述
本章将深入学习Vue.js的核心概念和基础语法，包括Vue实例、模板语法、数据绑定、计算属性、侦听器、事件处理等重要内容。通过本章的学习，你将掌握Vue.js的基础开发技能，能够创建具有交互功能的Web应用。

## 内容目录
1. [Vue实例和生命周期](#vue实例和生命周期)
2. [模板语法与数据绑定](#模板语法与数据绑定)
3. [计算属性和侦听器](#计算属性和侦听器)
4. [Class与Style绑定](#class与style绑定)
5. [条件渲染与列表渲染](#条件渲染与列表渲染)
6. [事件处理](#事件处理)
7. [表单输入绑定](#表单输入绑定)
8. [组件化开发基础](#组件化开发基础)
9. [本章小结](#本章小结)

## Vue实例和生命周期

### Vue应用实例
在Vue 3中，我们使用`createApp`函数创建应用实例：

```javascript
import { createApp } from 'vue'
import App from './App.vue'

const app = createApp(App)
```

### Vue实例选项
创建Vue实例时可以传递多种选项：

```javascript
const app = createApp({
  // 数据
  data() {
    return {
      message: 'Hello Vue!'
    }
  },
  
  // 方法
  methods: {
    greet() {
      console.log('Hello!')
    }
  },
  
  // 计算属性
  computed: {
    reversedMessage() {
      return this.message.split('').reverse().join('')
    }
  },
  
  // 侦听器
  watch: {
    message(newVal, oldVal) {
      console.log(`Message changed from ${oldVal} to ${newVal}`)
    }
  }
})
```

### 生命周期钩子
Vue实例在创建和销毁过程中会经历一系列阶段，我们可以在特定阶段执行自定义逻辑：

```javascript
const app = createApp({
  data() {
    return {
      message: 'Hello Vue!'
    }
  },
  
  // 创建前
  beforeCreate() {
    console.log('beforeCreate')
  },
  
  // 创建后
  created() {
    console.log('created')
  },
  
  // 挂载前
  beforeMount() {
    console.log('beforeMount')
  },
  
  // 挂载后
  mounted() {
    console.log('mounted')
  },
  
  // 更新前
  beforeUpdate() {
    console.log('beforeUpdate')
  },
  
  // 更新后
  updated() {
    console.log('updated')
  },
  
  // 卸载前
  beforeUnmount() {
    console.log('beforeUnmount')
  },
  
  // 卸载后
  unmounted() {
    console.log('unmounted')
  }
})
```

## 模板语法与数据绑定

### 文本插值
使用双大括号语法进行文本插值：

```vue
<template>
  <p>{{ message }}</p>
  <p>Using JavaScript expression: {{ message.split('').reverse().join('') }}</p>
</template>
```

### 原始HTML
使用`v-html`指令输出原始HTML：

```vue
<template>
  <p>Using text interpolation: {{ rawHtml }}</p>
  <p>Using v-html directive: <span v-html="rawHtml"></span></p>
</template>

<script>
export default {
  data() {
    return {
      rawHtml: '<span style="color: red">This should be red.</span>'
    }
  }
}
</script>
```

### 属性绑定
使用`v-bind`指令或简写`:`绑定属性：

```vue
<template>
  <div v-bind:id="dynamicId"></div>
  <div :id="dynamicId"></div>
  
  <button :disabled="isButtonDisabled">Button</button>
  
  <!-- 动态绑定多个属性 -->
  <div v-bind="objectOfAttributes"></div>
</template>

<script>
export default {
  data() {
    return {
      dynamicId: 'my-id',
      isButtonDisabled: true,
      objectOfAttributes: {
        id: 'container',
        class: 'wrapper'
      }
    }
  }
}
</script>
```

## 计算属性和侦听器

### 计算属性
计算属性是基于响应式依赖进行缓存的，只有依赖发生改变时才会重新计算：

```vue
<template>
  <div>
    <p>Original message: "{{ message }}"</p>
    <p>Computed reversed message: "{{ reversedMessage }}"</p>
    <p>Method reversed message: "{{ reverseMessage() }}"</p>
  </div>
</template>

<script>
export default {
  data() {
    return {
      message: 'Hello'
    }
  },
  
  computed: {
    // 计算属性的getter
    reversedMessage() {
      return this.message.split('').reverse().join('')
    }
  },
  
  methods: {
    reverseMessage() {
      return this.message.split('').reverse().join('')
    }
  }
}
</script>
```

### 计算属性的setter
计算属性默认只有getter，也可以提供setter：

```vue
<template>
  <div>
    <p>{{ fullName }}</p>
    <input v-model="fullName">
  </div>
</template>

<script>
export default {
  data() {
    return {
      firstName: 'Foo',
      lastName: 'Bar'
    }
  },
  
  computed: {
    fullName: {
      // getter
      get() {
        return this.firstName + ' ' + this.lastName
      },
      // setter
      set(newValue) {
        const names = newValue.split(' ')
        this.firstName = names[0]
        this.lastName = names[names.length - 1]
      }
    }
  }
}
</script>
```

### 侦听器
当需要在数据变化时执行异步操作或开销较大的操作时，使用侦听器：

```vue
<template>
  <div>
    <p>
      Ask a yes/no question:
      <input v-model="question" />
    </p>
    <p>{{ answer }}</p>
  </div>
</template>

<script>
export default {
  data() {
    return {
      question: '',
      answer: 'Questions usually contain a question mark. ;-)'
    }
  },
  
  watch: {
    // 侦听question变化
    question(newQuestion, oldQuestion) {
      if (newQuestion.indexOf('?') > -1) {
        this.getAnswer()
      }
    }
  },
  
  methods: {
    async getAnswer() {
      this.answer = 'Thinking...'
      try {
        const res = await fetch('https://yesno.wtf/api')
        this.answer = (await res.json()).answer
      } catch (error) {
        this.answer = 'Error! Could not reach the API. ' + error
      }
    }
  }
}
</script>
```

## Class与Style绑定

### 绑定HTML Class

#### 对象语法
```vue
<template>
  <div :class="{ active: isActive, 'text-danger': hasError }">
    Class binding with object syntax
  </div>
  
  <div :class="classObject">
    Class binding with object variable
  </div>
</template>

<script>
export default {
  data() {
    return {
      isActive: true,
      hasError: false,
      classObject: {
        active: true,
        'text-danger': false
      }
    }
  }
}
</script>
```

#### 数组语法
```vue
<template>
  <div :class="[activeClass, errorClass]">
    Class binding with array syntax
  </div>
  
  <div :class="[isActive ? activeClass : '', errorClass]">
    Conditional class binding
  </div>
  
  <div :class="[{ active: isActive }, errorClass]">
    Mixed syntax
  </div>
</template>

<script>
export default {
  data() {
    return {
      activeClass: 'active',
      errorClass: 'text-danger',
      isActive: true
    }
  }
}
</script>
```

### 绑定内联样式

#### 对象语法
```vue
<template>
  <div :style="{ color: activeColor, fontSize: fontSize + 'px' }">
    Style binding with object syntax
  </div>
  
  <div :style="styleObject">
    Style binding with object variable
  </div>
</template>

<script>
export default {
  data() {
    return {
      activeColor: 'red',
      fontSize: 30,
      styleObject: {
        color: 'blue',
        fontSize: '20px'
      }
    }
  }
}
</script>
```

#### 数组语法
```vue
<template>
  <div :style="[baseStyles, overridingStyles]">
    Style binding with array syntax
  </div>
</template>

<script>
export default {
  data() {
    return {
      baseStyles: {
        color: 'green',
        fontSize: '16px'
      },
      overridingStyles: {
        color: 'red'  // 会覆盖baseStyles中的color
      }
    }
  }
}
</script>
```

## 条件渲染与列表渲染

### 条件渲染

#### v-if
```vue
<template>
  <div>
    <h1 v-if="awesome">Vue is awesome!</h1>
    <h1 v-else>Oh no 😢</h1>
    
    <!-- v-else-if -->
    <div v-if="type === 'A'">
      A
    </div>
    <div v-else-if="type === 'B'">
      B
    </div>
    <div v-else-if="type === 'C'">
      C
    </div>
    <div v-else>
      Not A/B/C
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      awesome: true,
      type: 'A'
    }
  }
}
</script>
```

#### v-show
```vue
<template>
  <div>
    <h1 v-show="ok">Hello!</h1>
  </div>
</template>

<script>
export default {
  data() {
    return {
      ok: true
    }
  }
}
</script>
```

#### `<template>`上的条件渲染
```vue
<template>
  <template v-if="loginType === 'admin'">
    <label>Admin</label>
    <input placeholder="Enter your username" key="username-input">
  </template>
  <template v-else>
    <label>Guest</label>
    <input placeholder="Enter your email" key="email-input">
  </template>
</template>

<script>
export default {
  data() {
    return {
      loginType: 'admin'
    }
  }
}
</script>
```

### 列表渲染

#### v-for with Array
```vue
<template>
  <ul>
    <li v-for="item in items" :key="item.id">
      {{ item.message }}
    </li>
  </ul>
  
  <!-- 获取索引 -->
  <ul>
    <li v-for="(item, index) in items" :key="item.id">
      {{ index }} - {{ item.message }}
    </li>
  </ul>
</template>

<script>
export default {
  data() {
    return {
      items: [
        { id: 1, message: 'Foo' },
        { id: 2, message: 'Bar' }
      ]
    }
  }
}
</script>
```

#### v-for with Object
```vue
<template>
  <ul>
    <li v-for="(value, key) in myObject" :key="key">
      {{ key }}: {{ value }}
    </li>
    
    <!-- 获取索引 -->
    <li v-for="(value, key, index) in myObject" :key="key">
      {{ index }}. {{ key }}: {{ value }}
    </li>
  </ul>
</template>

<script>
export default {
  data() {
    return {
      myObject: {
        title: 'How to do lists in Vue',
        author: 'Jane Doe',
        publishedAt: '2016-04-10'
      }
    }
  }
}
</script>
```

#### v-for with Range
```vue
<template>
  <div>
    <span v-for="n in 10" :key="n">{{ n }} </span>
  </div>
</template>
```

#### 在组件上使用v-for
```vue
<template>
  <div>
    <todo-item
      v-for="todo in todos"
      :key="todo.id"
      :title="todo.title"
      :is-complete="todo.isComplete"
    ></todo-item>
  </div>
</template>

<script>
import TodoItem from './TodoItem.vue'

export default {
  components: {
    TodoItem
  },
  data() {
    return {
      todos: [
        { id: 1, title: 'Do the dishes', isComplete: false },
        { id: 2, title: 'Take out the trash', isComplete: true },
        { id: 3, title: 'Mow the lawn', isComplete: false }
      ]
    }
  }
}
</script>
```

## 事件处理

### 监听事件
使用`v-on`指令或简写`@`监听DOM事件：

```vue
<template>
  <div>
    <button v-on:click="counter += 1">Add 1</button>
    <p>The button above has been clicked {{ counter }} times.</p>
    
    <button @click="greet">Greet</button>
    <button @click="say('hello')">Say hello</button>
    <button @click="say('bye')">Say bye</button>
  </div>
</template>

<script>
export default {
  data() {
    return {
      counter: 0
    }
  },
  
  methods: {
    greet(event) {
      // event是原生DOM事件
      alert('Hello ' + event.target.tagName)
    },
    
    say(message) {
      alert(message)
    }
  }
}
</script>
```

### 事件修饰符
```vue
<template>
  <div>
    <!-- 阻止单击事件继续传播 -->
    <a @click.stop="doThis"></a>
    
    <!-- 提交事件不再重载页面 -->
    <form @submit.prevent="onSubmit"></form>
    
    <!-- 修饰符可以串联 -->
    <a @click.stop.prevent="doThat"></a>
    
    <!-- 只有修饰符 -->
    <form @submit.prevent></form>
    
    <!-- 添加事件监听器时使用事件捕获模式 -->
    <div @click.capture="doThis">...</div>
    
    <!-- 只当在 event.target 是当前元素自身时触发处理函数 -->
    <div @click.self="doThat">...</div>
    
    <!-- 点击事件将只会触发一次 -->
    <a @click.once="doThis"></a>
    
    <!-- 滚动事件的默认行为 (即滚动行为) 将会立即触发 -->
    <div @scroll.passive="onScroll">...</div>
  </div>
</template>

<script>
export default {
  methods: {
    doThis() {
      console.log('doThis')
    },
    
    doThat() {
      console.log('doThat')
    },
    
    onSubmit() {
      console.log('onSubmit')
    },
    
    onScroll() {
      console.log('onScroll')
    }
  }
}
</script>
```

### 按键修饰符
```vue
<template>
  <div>
    <!-- 只有在 `key` 是 `Enter` 时调用 `vm.submit()` -->
    <input @keyup.enter="submit">
    
    <!-- 缩写语法 -->
    <input @keyup.enter="submit">
    
    <!-- 处理多个按键 -->
    <input @keyup.ctrl.enter="clear">
  </div>
</template>

<script>
export default {
  methods: {
    submit() {
      console.log('submit')
    },
    
    clear() {
      console.log('clear')
    }
  }
}
</script>
```

## 表单输入绑定

### 基础用法

#### 文本
```vue
<template>
  <div>
    <input v-model="message" placeholder="edit me">
    <p>Message is: {{ message }}</p>
  </div>
</template>

<script>
export default {
  data() {
    return {
      message: ''
    }
  }
}
</script>
```

#### 多行文本
```vue
<template>
  <div>
    <span>Multiline message is:</span>
    <p style="white-space: pre-line;">{{ message }}</p>
    <br>
    <textarea v-model="message" placeholder="add multiple lines"></textarea>
  </div>
</template>

<script>
export default {
  data() {
    return {
      message: ''
    }
  }
}
</script>
```

#### 复选框
```vue
<template>
  <div>
    <!-- 单个复选框 -->
    <input type="checkbox" id="checkbox" v-model="checked">
    <label for="checkbox">{{ checked }}</label>
    
    <!-- 多个复选框 -->
    <div>
      <input type="checkbox" id="jack" value="Jack" v-model="checkedNames">
      <label for="jack">Jack</label>
      <input type="checkbox" id="john" value="John" v-model="checkedNames">
      <label for="john">John</label>
      <input type="checkbox" id="mike" value="Mike" v-model="checkedNames">
      <label for="mike">Mike</label>
      <br>
      <span>Checked names: {{ checkedNames }}</span>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      checked: false,
      checkedNames: []
    }
  }
}
</script>
```

#### 单选按钮
```vue
<template>
  <div>
    <input type="radio" id="one" value="One" v-model="picked">
    <label for="one">One</label>
    <br>
    <input type="radio" id="two" value="Two" v-model="picked">
    <label for="two">Two</label>
    <br>
    <span>Picked: {{ picked }}</span>
  </div>
</template>

<script>
export default {
  data() {
    return {
      picked: ''
    }
  }
}
</script>
```

#### 选择框
```vue
<template>
  <div>
    <!-- 单选 -->
    <select v-model="selected">
      <option disabled value="">请选择</option>
      <option>A</option>
      <option>B</option>
      <option>C</option>
    </select>
    <span>Selected: {{ selected }}</span>
    
    <!-- 多选 -->
    <select v-model="selectedMultiple" multiple style="width: 50px;">
      <option>A</option>
      <option>B</option>
      <option>C</option>
    </select>
    <br>
    <span>Selected: {{ selectedMultiple }}</span>
  </div>
</template>

<script>
export default {
  data() {
    return {
      selected: '',
      selectedMultiple: []
    }
  }
}
</script>
```

### 值绑定
```vue
<template>
  <div>
    <!-- 复选框 -->
    <input
      type="checkbox"
      v-model="toggle"
      true-value="yes"
      false-value="no"
    >
    
    <!-- 单选按钮 -->
    <input type="radio" v-model="pick" :value="a">
    
    <!-- 选择框 -->
    <select v-model="selected">
      <option :value="{ number: 123 }">123</option>
    </select>
  </div>
</template>

<script>
export default {
  data() {
    return {
      toggle: 'no',
      pick: '',
      a: 'a',
      selected: null
    }
  }
}
</script>
```

### 修饰符
```vue
<template>
  <div>
    <!-- 在"change"时而非"input"时更新 -->
    <input v-model.lazy="msg" >
    <span>{{ msg }}</span>
    
    <!-- 自动将用户的输入值转为数值类型 -->
    <input v-model.number="age" type="number">
    
    <!-- 自动过滤用户输入的首尾空白字符 -->
    <input v-model.trim="msg2">
  </div>
</template>

<script>
export default {
  data() {
    return {
      msg: '',
      age: 0,
      msg2: ''
    }
  }
}
</script>
```

## 组件化开发基础

组件系统是Vue.js的核心特性之一，它允许我们将UI拆分为独立的、可复用的代码片段。

### 组件基础

#### 定义组件
```vue
<!-- 定义一个按钮组件 -->
<template>
  <button class="my-button" @click="handleClick">
    <slot></slot>
  </button>
</template>

<script>
export default {
  name: 'MyButton',
  methods: {
    handleClick() {
      this.$emit('click')
    }
  }
}
</script>

<style scoped>
.my-button {
  background-color: #42b983;
  border: none;
  color: white;
  padding: 10px 20px;
  text-align: center;
  text-decoration: none;
  display: inline-block;
  font-size: 16px;
  margin: 4px 2px;
  cursor: pointer;
  border-radius: 4px;
}
</style>
```

#### 使用组件
```vue
<template>
  <div>
    <my-button @click="handleClick">点击我</my-button>
  </div>
</template>

<script>
import MyButton from './components/MyButton.vue'

export default {
  components: {
    MyButton
  },
  methods: {
    handleClick() {
      console.log('按钮被点击了')
    }
  }
}
</script>
```

### Props传递数据

Props是父组件向子组件传递数据的方式：

```vue
<!-- 父组件 -->
<template>
  <child-component 
    :title="parentTitle" 
    :likes="10" 
    :is-published="true" 
    :comment-ids="[1, 2, 3]" 
    :author="{ name: 'John', company: 'Example' }"
  />
</template>

<script>
import ChildComponent from './ChildComponent.vue'

export default {
  components: {
    ChildComponent
  },
  data() {
    return {
      parentTitle: '父组件传递的标题'
    }
  }
}
</script>
```

```vue
<!-- 子组件 -->
<template>
  <div>
    <h3>{{ title }}</h3>
    <p>点赞数: {{ likes }}</p>
    <p>已发布: {{ isPublished ? '是' : '否' }}</p>
  </div>
</template>

<script>
export default {
  name: 'ChildComponent',
  props: {
    title: String,
    likes: Number,
    isPublished: Boolean,
    commentIds: Array,
    author: Object
  }
}
</script>
```

### 自定义事件

子组件通过`$emit`向父组件传递事件：

```vue
<!-- 子组件 -->
<template>
  <div>
    <button @click="handleClick">删除</button>
  </div>
</template>

<script>
export default {
  name: 'TodoItem',
  methods: {
    handleClick() {
      // 向父组件发送delete事件
      this.$emit('delete', this.todo.id)
    }
  }
}
</script>
```

```vue
<!-- 父组件 -->
<template>
  <div>
    <todo-item 
      v-for="todo in todos" 
      :key="todo.id"
      :todo="todo"
      @delete="handleDelete"
    />
  </div>
</template>

<script>
import TodoItem from './TodoItem.vue'

export default {
  components: {
    TodoItem
  },
  data() {
    return {
      todos: [
        { id: 1, text: '学习Vue' },
        { id: 2, text: '完成项目' }
      ]
    }
  },
  methods: {
    handleDelete(id) {
      this.todos = this.todos.filter(todo => todo.id !== id)
    }
  }
}
</script>
```

### 插槽(Slots)

插槽允许父组件向子组件传递内容：

```vue
<!-- 子组件 -->
<template>
  <div class="alert">
    <strong>{{ title }}</strong>
    <slot></slot>
    <slot name="footer">
      <button @click="$emit('close')">关闭</button>
    </slot>
  </div>
</template>

<script>
export default {
  name: 'AlertBox',
  props: ['title']
}
</script>
```

```vue
<!-- 父组件 -->
<template>
  <alert-box title="重要提示">
    <p>这是警告内容</p>
    <template #footer>
      <button @click="handleConfirm">确认</button>
      <button @click="handleCancel">取消</button>
    </template>
  </alert-box>
</template>

<script>
import AlertBox from './AlertBox.vue'

export default {
  components: {
    AlertBox
  },
  methods: {
    handleConfirm() {
      console.log('用户确认')
    },
    handleCancel() {
      console.log('用户取消')
    }
  }
}
</script>
```

## 本章小结

通过本章的学习，我们掌握了Vue.js的核心概念和基础语法：

1. **Vue实例和生命周期**：了解了Vue实例的创建方式和各个生命周期钩子的作用
2. **模板语法与数据绑定**：学会了如何使用文本插值、属性绑定等进行数据展示
3. **计算属性和侦听器**：掌握了计算属性的缓存特性和侦听器的使用场景
4. **Class与Style绑定**：学会了动态绑定CSS类和内联样式
5. **条件渲染与列表渲染**：掌握了v-if/v-show和v-for的使用方法
6. **事件处理**：学会了如何处理用户交互事件及使用事件修饰符
7. **表单输入绑定**：掌握了v-model在各种表单元素中的使用
8. **组件化开发基础**：学会了如何创建和使用组件，通过props传递数据，通过事件进行通信

这些基础知识是Vue.js开发的核心，熟练掌握后就能创建具有丰富交互功能的Web应用。

## 实践练习

1. 创建一个简单的待办事项应用，包含添加、删除、标记完成等功能
2. 实现一个计算器组件，支持基本的数学运算
3. 创建一个表单验证示例，包含用户名、邮箱、密码等字段的验证
4. 实现一个图片轮播组件，支持自动播放和手动切换
5. 创建一个可复用的模态框组件，支持自定义内容和操作按钮