<template>
  <div id="app">
    <el-container>
      <el-header>
        <navbar />
      </el-header>
      <el-container>
        <el-aside width="200px">
          <sidebar />
        </el-aside>
        <el-main>
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script>
import Navbar from './components/business/Navbar.vue'
import Sidebar from './components/business/Sidebar.vue'

export default {
  name: 'App',
  components: {
    Navbar,
    Sidebar
  }
}
</script>

<style>
#app {
  height: 100vh;
}

.el-header {
  background-color: #409eff;
  color: #fff;
  line-height: 60px;
}

.el-aside {
  background-color: #f5f5f5;
}

.el-main {
  background-color: #fff;
}
</style>