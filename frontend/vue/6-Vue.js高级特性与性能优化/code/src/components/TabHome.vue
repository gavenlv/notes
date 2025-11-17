<template>
  <div class="tab-home">
    <h3>Home Component</h3>
    <p>This is the home tab content.</p>
    <p>Current timestamp: {{ timestamp }}</p>
  </div>
</template>

<script>
export default {
  name: 'TabHome',
  data() {
    return {
      timestamp: new Date().toLocaleTimeString()
    }
  },
  // 当组件被keep-alive缓存时，activated和deactivated钩子会被触发
  activated() {
    console.log('Home component activated')
    // 更新时间戳以显示组件确实被重新激活
    this.timestamp = new Date().toLocaleTimeString()
  },
  deactivated() {
    console.log('Home component deactivated')
  }
}
</script>