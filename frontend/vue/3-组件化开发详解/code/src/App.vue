<template>
  <div id="app">
    <h1>Vue.js 组件化开发详解</h1>
    
    <section>
      <h2>1. 用户卡片组件示例</h2>
      <user-card 
        :user="currentUser"
        @user-updated="handleUserUpdated"
      />
    </section>

    <section>
      <h2>2. 可折叠面板组件示例</h2>
      <collapsible-panel title="点击展开/收起">
        <p>这是可折叠面板的内容。</p>
        <p>可以放置任何内容在这里。</p>
      </collapsible-panel>
    </section>

    <section>
      <h2>3. 带验证的表单组件示例</h2>
      <form-with-validation @form-submitted="handleFormSubmit" />
    </section>

    <section>
      <h2>4. 通知组件示例</h2>
      <button @click="showNotification">显示通知</button>
      <notification 
        :show="isNotificationVisible"
        :message="notificationMessage"
        @close="hideNotification"
      />
    </section>

    <section>
      <h2>5. 图片懒加载组件示例</h2>
      <div class="image-container">
        <image-lazy-load 
          src="https://picsum.photos/400/300?random=1"
          alt="示例图片1"
        />
        <image-lazy-load 
          src="https://picsum.photos/400/300?random=2"
          alt="示例图片2"
        />
        <image-lazy-load 
          src="https://picsum.photos/400/300?random=3"
          alt="示例图片3"
        />
      </div>
    </section>
  </div>
</template>

<script>
import UserCard from './components/UserCard.vue'
import CollapsiblePanel from './components/CollapsiblePanel.vue'
import FormWithValidation from './components/FormWithValidation.vue'
import Notification from './components/Notification.vue'
import ImageLazyLoad from './components/ImageLazyLoad.vue'

export default {
  name: 'App',
  components: {
    UserCard,
    CollapsiblePanel,
    FormWithValidation,
    Notification,
    ImageLazyLoad
  },
  data() {
    return {
      currentUser: {
        name: '张三',
        email: 'zhangsan@example.com',
        avatar: 'https://picsum.photos/100/100'
      },
      isNotificationVisible: false,
      notificationMessage: '这是一条通知消息！'
    }
  },
  methods: {
    handleUserUpdated(updatedUser) {
      this.currentUser = updatedUser
      console.log('用户信息已更新:', updatedUser)
    },
    handleFormSubmit(formData) {
      console.log('表单提交数据:', formData)
      alert('表单提交成功！')
    },
    showNotification() {
      this.isNotificationVisible = true
    },
    hideNotification() {
      this.isNotificationVisible = false
    }
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}

section {
  margin-bottom: 40px;
  padding: 20px;
  border: 1px solid #eee;
  border-radius: 4px;
}

.image-container {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  justify-content: center;
}
</style>