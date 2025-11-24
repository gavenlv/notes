<template>
  <div style="padding: 20px; border: 2px solid #42b883; border-radius: 8px;">
    <h1>Vue 微应用</h1>
    <p>{{ message }}</p>
    <div>
      <button @click="increment">计数器: {{ count }}</button>
      <button @click="sendMessageToReact" style="margin-left: 10px;">
        发送消息给 React 应用
      </button>
    </div>
    <div style="margin-top: 20px;">
      <h3>Vue 应用特点：</h3>
      <ul>
        <li>使用 Composition API 管理状态</li>
        <li>通过 Custom Events 实现应用间通信</li>
        <li>独立开发和部署</li>
      </ul>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue';

export default {
  name: 'App',
  setup() {
    const count = ref(0);
    const message = ref('Hello from Vue App!');

    const increment = () => {
      count.value++;
    };

    const handleAppMessage = (event) => {
      if (event.detail && event.detail.type === 'from-react') {
        message.value = `Received from React: ${event.detail.data}`;
      }
    };

    const sendMessageToReact = () => {
      const event = new CustomEvent('app-message', {
        detail: {
          type: 'from-vue',
          data: `Hello from Vue! Count is ${count.value}`
        }
      });
      window.dispatchEvent(event);
    };

    onMounted(() => {
      console.log('Vue App mounted');
      window.addEventListener('app-message', handleAppMessage);
    });

    onUnmounted(() => {
      window.removeEventListener('app-message', handleAppMessage);
    });

    return {
      count,
      message,
      increment,
      sendMessageToReact
    };
  }
};
</script>