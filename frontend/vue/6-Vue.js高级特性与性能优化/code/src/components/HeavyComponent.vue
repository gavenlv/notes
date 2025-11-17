<template>
  <div class="heavy-component">
    <h3>Heavy Component</h3>
    <p>This component was loaded asynchronously!</p>
    <div class="chart-container">
      <div class="chart-bar" v-for="(value, index) in chartData" :key="index" :style="{ height: value + '%' }">
        {{ value }}%
      </div>
    </div>
    <p>Random Data Visualization</p>
  </div>
</template>

<script>
export default {
  name: 'HeavyComponent',
  data() {
    return {
      chartData: Array.from({ length: 10 }, () => Math.floor(Math.random() * 100))
    }
  },
  created() {
    console.log('Heavy component created')
  }
}
</script>

<style scoped>
.heavy-component {
  margin-top: 20px;
  padding: 20px;
  background-color: #f9f9f9;
  border-radius: 4px;
}

.chart-container {
  display: flex;
  justify-content: space-around;
  align-items: flex-end;
  height: 100px;
  margin: 20px 0;
  border-bottom: 1px solid #ddd;
}

.chart-bar {
  width: 30px;
  background-color: #42b983;
  color: white;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  padding: 5px;
  border-radius: 4px 4px 0 0;
}
</style>