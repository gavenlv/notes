<template>
  <div id="app">
    <h1>Vue.js 核心概念与基础语法示例</h1>
    
    <!-- Vue实例和生命周期示例 -->
    <div class="section">
      <h2>1. Vue实例和生命周期</h2>
      <p>计数器: {{ counter }}</p>
      <button @click="incrementCounter">增加计数</button>
      <p>生命周期状态: {{ lifecycleStatus }}</p>
    </div>

    <!-- 模板语法与数据绑定示例 -->
    <div class="section">
      <h2>2. 模板语法与数据绑定</h2>
      <p>消息: {{ message }}</p>
      <p>反转消息: {{ reversedMessage }}</p>
      <p>原始HTML: <span v-html="rawHtml"></span></p>
      <p :id="dynamicId">动态ID元素</p>
    </div>

    <!-- 计算属性和侦听器示例 -->
    <div class="section">
      <h2>3. 计算属性和侦听器</h2>
      <p>姓名: 
        <input v-model="firstName" placeholder="名"> +
        <input v-model="lastName" placeholder="姓"> =
        <strong>{{ fullName }}</strong>
      </p>
      <p>侦听器消息: {{ watcherMessage }}</p>
    </div>

    <!-- Class与Style绑定示例 -->
    <div class="section">
      <h2>4. Class与Style绑定</h2>
      <div :class="{ active: isActive, 'text-danger': hasError }">
        Class绑定示例
      </div>
      <div :style="{ color: activeColor, fontSize: fontSize + 'px' }">
        Style绑定示例
      </div>
      <button @click="toggleClass">切换Class</button>
      <button @click="toggleStyle">切换Style</button>
    </div>

    <!-- 条件渲染示例 -->
    <div class="section">
      <h2>5. 条件渲染</h2>
      <button @click="showConditional = !showConditional">切换显示</button>
      <p v-if="showConditional">这是一个条件渲染的元素</p>
      <p v-else>这是else部分</p>
    </div>

    <!-- 列表渲染示例 -->
    <div class="section">
      <h2>6. 列表渲染</h2>
      <ul>
        <li v-for="(item, index) in items" :key="item.id">
          {{ index + 1 }}. {{ item.name }} - {{ item.description }}
        </li>
      </ul>
      <button @click="addItem">添加项目</button>
      <button @click="removeItem">移除项目</button>
    </div>

    <!-- 事件处理示例 -->
    <div class="section">
      <h2>7. 事件处理</h2>
      <button @click="handleClick">点击我</button>
      <button @click.stop="handleStopClick">阻止冒泡点击</button>
      <p>按钮被点击了 {{ clickCount }} 次</p>
    </div>

    <!-- 表单输入绑定示例 -->
    <div class="section">
      <h2>8. 表单输入绑定</h2>
      <form @submit.prevent="handleSubmit">
        <div>
          <label>文本输入:</label>
          <input v-model="textInput" placeholder="请输入文本">
        </div>
        
        <div>
          <label>多行文本:</label>
          <textarea v-model="textareaInput" placeholder="请输入多行文本"></textarea>
        </div>
        
        <div>
          <label>复选框:</label>
          <input type="checkbox" v-model="checkboxValue">
          <span>选中状态: {{ checkboxValue }}</span>
        </div>
        
        <div>
          <label>单选按钮:</label>
          <input type="radio" id="option1" value="选项1" v-model="radioValue">
          <label for="option1">选项1</label>
          <input type="radio" id="option2" value="选项2" v-model="radioValue">
          <label for="option2">选项2</label>
          <span>选中值: {{ radioValue }}</span>
        </div>
        
        <div>
          <label>选择框:</label>
          <select v-model="selectValue">
            <option disabled value="">请选择</option>
            <option>选项A</option>
            <option>选项B</option>
            <option>选项C</option>
          </select>
          <span>选中值: {{ selectValue }}</span>
        </div>
        
        <button type="submit">提交</button>
      </form>
      
      <div v-if="formData" class="form-result">
        <h3>表单数据:</h3>
        <pre>{{ formData }}</pre>
      </div>
    </div>

    <!-- 组件示例 -->
    <div class="section">
      <h2>9. 组件使用示例</h2>
      <todo-item 
        v-for="todo in todos" 
        :key="todo.id"
        :todo="todo"
        @toggle-complete="toggleTodoComplete"
        @delete-todo="deleteTodo"
      />
      
      <div class="add-todo">
        <input v-model="newTodoText" placeholder="添加新的待办事项" @keyup.enter="addTodo">
        <button @click="addTodo">添加</button>
      </div>
    </div>

    <!-- 计算器组件示例 -->
    <div class="section">
      <h2>10. 计算器组件示例</h2>
      <calculator />
    </div>
  </div>
</template>

<script>
import TodoItem from './components/TodoItem.vue'
import Calculator from './components/Calculator.vue'

export default {
  name: 'App',
  components: {
    TodoItem,
    Calculator
  },
  data() {
    return {
      // Vue实例和生命周期
      counter: 0,
      lifecycleStatus: 'created',
      
      // 模板语法与数据绑定
      message: 'Hello Vue!',
      rawHtml: '<span style="color: red">这是原始HTML</span>',
      dynamicId: 'dynamic-element',
      
      // 计算属性和侦听器
      firstName: '张',
      lastName: '三',
      watcherMessage: '等待变化...',
      
      // Class与Style绑定
      isActive: true,
      hasError: false,
      activeColor: 'blue',
      fontSize: 16,
      
      // 条件渲染
      showConditional: true,
      
      // 列表渲染
      items: [
        { id: 1, name: '项目1', description: '这是第一个项目' },
        { id: 2, name: '项目2', description: '这是第二个项目' }
      ],
      
      // 事件处理
      clickCount: 0,
      
      // 表单输入绑定
      textInput: '',
      textareaInput: '',
      checkboxValue: false,
      radioValue: '选项1',
      selectValue: '',
      formData: null,
      
      // 组件示例
      todos: [
        { id: 1, text: '学习Vue基础', completed: false },
        { id: 2, text: '完成第二章练习', completed: false }
      ],
      newTodoText: ''
    }
  },
  
  computed: {
    // 计算属性
    reversedMessage() {
      return this.message.split('').reverse().join('')
    },
    
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
  },
  
  watch: {
    // 侦听器
    message(newVal, oldVal) {
      this.watcherMessage = `消息从 "${oldVal}" 改变为 "${newVal}"`
    }
  },
  
  // 生命周期钩子
  beforeCreate() {
    console.log('beforeCreate')
  },
  
  created() {
    console.log('created')
    this.lifecycleStatus = 'created'
  },
  
  beforeMount() {
    console.log('beforeMount')
    this.lifecycleStatus = 'beforeMount'
  },
  
  mounted() {
    console.log('mounted')
    this.lifecycleStatus = 'mounted'
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
  },
  
  methods: {
    // Vue实例和生命周期
    incrementCounter() {
      this.counter++
    },
    
    // Class与Style绑定
    toggleClass() {
      this.isActive = !this.isActive
      this.hasError = !this.hasError
    },
    
    toggleStyle() {
      this.activeColor = this.activeColor === 'blue' ? 'red' : 'blue'
      this.fontSize = this.fontSize === 16 ? 20 : 16
    },
    
    // 列表渲染
    addItem() {
      const newId = this.items.length > 0 ? Math.max(...this.items.map(item => item.id)) + 1 : 1
      this.items.push({
        id: newId,
        name: `项目${newId}`,
        description: `这是第${newId}个项目`
      })
    },
    
    removeItem() {
      if (this.items.length > 0) {
        this.items.pop()
      }
    },
    
    // 事件处理
    handleClick() {
      this.clickCount++
    },
    
    handleStopClick() {
      alert('阻止冒泡的点击事件')
    },
    
    // 表单输入绑定
    handleSubmit() {
      this.formData = {
        textInput: this.textInput,
        textareaInput: this.textareaInput,
        checkboxValue: this.checkboxValue,
        radioValue: this.radioValue,
        selectValue: this.selectValue
      }
      alert('表单已提交，请查看结果')
    },
    
    // 组件示例
    toggleTodoComplete(id) {
      const todo = this.todos.find(todo => todo.id === id)
      if (todo) {
        todo.completed = !todo.completed
      }
    },
    
    deleteTodo(id) {
      this.todos = this.todos.filter(todo => todo.id !== id)
    },
    
    addTodo() {
      if (this.newTodoText.trim()) {
        const newId = this.todos.length > 0 ? Math.max(...this.todos.map(todo => todo.id)) + 1 : 1
        this.todos.push({
          id: newId,
          text: this.newTodoText,
          completed: false
        })
        this.newTodoText = ''
      }
    }
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}

.section {
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 20px;
  margin: 20px 0;
  text-align: left;
}

.section h2 {
  color: #42b983;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
}

.active {
  background-color: #42b983;
  color: white;
  padding: 10px;
  border-radius: 4px;
}

.text-danger {
  color: red;
  font-weight: bold;
}

.form-result {
  background-color: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  padding: 15px;
  margin-top: 15px;
}

.add-todo {
  margin-top: 20px;
  display: flex;
  gap: 10px;
}

button {
  background-color: #42b983;
  border: none;
  color: white;
  padding: 8px 16px;
  text-align: center;
  text-decoration: none;
  display: inline-block;
  font-size: 14px;
  margin: 4px 2px;
  cursor: pointer;
  border-radius: 4px;
}

button:hover {
  background-color: #359c6d;
}

input, textarea, select {
  padding: 8px;
  margin: 5px;
  border: 1px solid #ccc;
  border-radius: 4px;
}

label {
  font-weight: bold;
}
</style>