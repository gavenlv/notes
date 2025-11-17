<template>
  <div class="home">
    <h1>Vue.js Advanced Features Demo</h1>
    <p>Welcome to the Vue.js Advanced Features demonstration.</p>
    <div class="features">
      <div class="feature-card" v-for="feature in features" :key="feature.title">
        <h3>{{ feature.title }}</h3>
        <p>{{ feature.description }}</p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'HomePage',
  data() {
    return {
      features: [
        {
          title: 'Dynamic Components',
          description: 'Learn how to use dynamic components with keep-alive for better performance.'
        },
        {
          title: 'Async Components',
          description: 'Discover how to load components asynchronously to reduce initial bundle size.'
        },
        {
          title: 'Slots',
          description: 'Master advanced slot techniques for creating flexible components.'
        },
        {
          title: 'Performance Optimization',
          description: 'Implement various optimization techniques to improve your app performance.'
        }
      ]
    }
  }
}
</script>

<style scoped>
.features {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-top: 30px;
}

.feature-card {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 20px;
  text-align: left;
}

.feature-card h3 {
  color: #42b983;
  margin-top: 0;
}
</style>