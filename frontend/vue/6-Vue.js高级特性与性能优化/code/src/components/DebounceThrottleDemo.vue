<template>
  <div class="debounce-throttle-demo">
    <h2>Debounce & Throttle Demo</h2>
    
    <div class="demo-section">
      <h3>Search with Debounce</h3>
      <input 
        v-model="searchQuery" 
        @input="debouncedSearch" 
        placeholder="Type to search (debounced)"
        class="search-input"
      >
      <p>Search results for: "{{ debouncedQuery }}"</p>
      <ul>
        <li v-for="item in filteredItems" :key="item">{{ item }}</li>
      </ul>
    </div>
    
    <div class="demo-section">
      <h3>Button with Throttle</h3>
      <button @click="throttledClick" class="throttle-button">
        Click Me (throttled)
      </button>
      <p>Button clicked {{ clickCount }} times</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DebounceThrottleDemo',
  data() {
    return {
      searchQuery: '',
      debouncedQuery: '',
      clickCount: 0,
      items: [
        'Apple', 'Banana', 'Cherry', 'Date', 'Elderberry',
        'Fig', 'Grape', 'Honeydew', 'Iceberg', 'Jackfruit',
        'Kiwi', 'Lemon', 'Mango', 'Nectarine', 'Orange'
      ]
    }
  },
  computed: {
    filteredItems() {
      return this.items.filter(item => 
        item.toLowerCase().includes(this.debouncedQuery.toLowerCase())
      )
    }
  },
  methods: {
    // 防抖搜索
    debouncedSearch: debounce(function() {
      this.debouncedQuery = this.searchQuery
    }, 300),
    
    // 节流点击
    throttledClick: throttle(function() {
      this.clickCount++
    }, 1000)
  }
}

// 防抖函数
function debounce(func, delay) {
  let timeoutId
  return function(...args) {
    clearTimeout(timeoutId)
    timeoutId = setTimeout(() => func.apply(this, args), delay)
  }
}

// 节流函数
function throttle(func, delay) {
  let lastCall = 0
  return function(...args) {
    const now = Date.now()
    if (now - lastCall >= delay) {
      lastCall = now
      func.apply(this, args)
    }
  }
}
</script>

<style scoped>
.debounce-throttle-demo {
  margin: 20px 0;
}

.demo-section {
  margin-bottom: 30px;
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.search-input {
  width: 100%;
  padding: 10px;
  margin-bottom: 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.throttle-button {
  padding: 10px 20px;
  background-color: #42b983;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

ul {
  text-align: left;
  margin-top: 10px;
}
</style>