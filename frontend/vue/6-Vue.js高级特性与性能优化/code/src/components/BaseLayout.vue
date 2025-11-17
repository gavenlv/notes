<template>
  <div class="base-layout">
    <header class="layout-header">
      <slot name="header">
        <h2>Default Header</h2>
      </slot>
    </header>
    
    <main class="layout-main">
      <slot></slot>
    </main>
    
    <footer class="layout-footer">
      <slot name="footer">
        <p>Default Footer</p>
      </slot>
    </footer>
  </div>
</template>

<script>
export default {
  name: 'BaseLayout'
}
</script>

<style scoped>
.base-layout {
  border: 1px solid #ddd;
  border-radius: 4px;
  overflow: hidden;
}

.layout-header {
  background-color: #f5f5f5;
  padding: 20px;
  border-bottom: 1px solid #ddd;
}

.layout-main {
  padding: 20px;
  min-height: 100px;
}

.layout-footer {
  background-color: #f5f5f5;
  padding: 10px 20px;
  border-top: 1px solid #ddd;
  text-align: center;
}
</style>