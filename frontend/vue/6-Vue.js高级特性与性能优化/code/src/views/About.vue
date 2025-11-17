<template>
  <div class="about">
    <h1>About Vue.js Advanced Features</h1>
    <p>This demo showcases various advanced features and performance optimization techniques in Vue.js.</p>
    
    <h2>Topics Covered</h2>
    <ul>
      <li>Dynamic Components & Keep-Alive</li>
      <li>Async Components</li>
      <li>Advanced Slots Usage</li>
      <li>Performance Optimization Strategies</li>
      <li>Code Splitting & Lazy Loading</li>
      <li>Webpack Optimization</li>
    </ul>
  </div>
</template>

<script>
export default {
  name: 'AboutPage'
}
</script>

<style scoped>
.about {
  text-align: left;
  max-width: 800px;
  margin: 0 auto;
}

ul {
  text-align: left;
  columns: 2;
  column-gap: 40px;
}
</style>