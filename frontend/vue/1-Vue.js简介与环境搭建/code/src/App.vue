<template>
  <div id="app">
    <header>
      <h1>{{ title }}</h1>
      <p>Welcome to {{ frameworkName }} learning course!</p>
    </header>
    
    <main>
      <section class="intro">
        <h2>Chapter 1: Introduction and Environment Setup</h2>
        <p>This is a simple Vue.js application demonstrating the basic structure of a Vue project.</p>
        
        <div class="counter-section">
          <h3>Simple Counter Example</h3>
          <p>Count: {{ count }}</p>
          <button @click="increment">Increment</button>
          <button @click="decrement">Decrement</button>
          <button @click="reset">Reset</button>
        </div>
        
        <div class="message-section">
          <h3>Dynamic Message Example</h3>
          <input v-model="message" placeholder="Type something here">
          <p>Your message: {{ message }}</p>
        </div>
      </section>
      
      <HelloWorld msg="Welcome to Your Vue.js App"/>
    </main>
    
    <footer>
      <p>{{ footerText }}</p>
    </footer>
  </div>
</template>

<script>
import HelloWorld from './components/HelloWorld.vue'

export default {
  name: 'App',
  components: {
    HelloWorld
  },
  data() {
    return {
      title: 'Vue.js Learning Course',
      frameworkName: 'Vue.js',
      count: 0,
      message: 'Hello Vue!',
      footerText: 'Chapter 1 - Vue.js Introduction and Environment Setup'
    }
  },
  methods: {
    increment() {
      this.count++
    },
    decrement() {
      this.count--
    },
    reset() {
      this.count = 0
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

header {
  margin-bottom: 40px;
}

header h1 {
  color: #42b983;
}

.intro {
  background-color: #f5f5f5;
  padding: 20px;
  border-radius: 5px;
  margin-bottom: 30px;
}

.counter-section, .message-section {
  margin: 20px 0;
  padding: 15px;
  background-color: white;
  border-radius: 5px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
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

input {
  padding: 8px;
  margin: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

footer {
  margin-top: 40px;
  padding: 20px;
  border-top: 1px solid #eee;
  color: #666;
}
</style>