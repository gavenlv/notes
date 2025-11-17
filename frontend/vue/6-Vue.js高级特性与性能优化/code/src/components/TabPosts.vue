<template>
  <div class="tab-posts">
    <h3>Posts Component</h3>
    <p>This tab demonstrates async data loading.</p>
    <div v-if="loading">Loading posts...</div>
    <ul v-else>
      <li v-for="post in posts" :key="post.id">
        {{ post.title }}
      </li>
    </ul>
  </div>
</template>

<script>
export default {
  name: 'TabPosts',
  data() {
    return {
      loading: true,
      posts: []
    }
  },
  mounted() {
    // 模拟异步数据加载
    setTimeout(() => {
      this.posts = [
        { id: 1, title: 'Post 1' },
        { id: 2, title: 'Post 2' },
        { id: 3, title: 'Post 3' }
      ]
      this.loading = false
    }, 1000)
  },
  activated() {
    console.log('Posts component activated')
  },
  deactivated() {
    console.log('Posts component deactivated')
  }
}
</script>