<template>
  <div class="tab-archive">
    <h3>Archive Component</h3>
    <p>This is the archive tab content.</p>
    <p>Count: {{ count }}</p>
    <button @click="increment">Increment</button>
  </div>
</template>

<script>
export default {
  name: 'TabArchive',
  data() {
    return {
      count: 0
    }
  },
  methods: {
    increment() {
      this.count++
    }
  },
  activated() {
    console.log('Archive component activated')
  },
  deactivated() {
    console.log('Archive component deactivated')
  }
}
</script>