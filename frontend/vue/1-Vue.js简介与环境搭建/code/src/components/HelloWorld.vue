<template>
  <div class="hello">
    <h2>{{ msg }}</h2>
    <p>This is a reusable component example.</p>
    
    <h3>Key Vue.js Features Demonstrated:</h3>
    <ul>
      <li v-for="feature in features" :key="feature.id">
        {{ feature.name }}: {{ feature.description }}
      </li>
    </ul>
    
    <div class="user-info">
      <h3>User Information Component</h3>
      <p>Name: {{ user.name }}</p>
      <p>Age: {{ user.age }}</p>
      <p>Email: {{ user.email }}</p>
      <button @click="updateUser">Update User Info</button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'HelloWorld',
  props: {
    msg: {
      type: String,
      default: 'Hello World Component'
    }
  },
  data() {
    return {
      features: [
        { id: 1, name: 'Declarative Rendering', description: 'Vue extends standard HTML with special syntax' },
        { id: 2, 'Reactivity System', description: 'Automatically tracks JavaScript state changes' },
        { id: 3, 'Component-Based Architecture', description: 'Build encapsulated components' },
        { id: 4, 'Virtual DOM', description: 'Efficiently update the DOM' }
      ],
      user: {
        name: 'John Doe',
        age: 30,
        email: 'john.doe@example.com'
      }
    }
  },
  methods: {
    updateUser() {
      this.user.name = 'Jane Smith'
      this.user.age = 25
      this.user.email = 'jane.smith@example.com'
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
.hello {
  margin: 20px 0;
  padding: 20px;
  background-color: #fff;
  border-radius: 5px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

h3 {
  margin: 20px 0 10px;
  color: #42b983;
}

ul {
  list-style-type: none;
  padding: 0;
}

li {
  margin: 10px 0;
  padding: 10px;
  background-color: #f8f8f8;
  border-left: 4px solid #42b983;
}

.user-info {
  margin-top: 20px;
  padding: 15px;
  background-color: #e8f5e9;
  border-radius: 5px;
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
  margin: 10px 2px;
  cursor: pointer;
  border-radius: 4px;
}

button:hover {
  background-color: #359c6d;
}
</style>