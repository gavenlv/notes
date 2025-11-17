<template>
  <div class="notification-wrapper">
    <transition name="fade">
      <div v-if="show" class="notification" :class="type">
        <div class="notification-content">
          <slot>
            <p>{{ message }}</p>
          </slot>
        </div>
        <button class="close-button" @click="$emit('close')">&times;</button>
      </div>
    </transition>
  </div>
</template>

<script>
export default {
  name: 'NotificationComponent',
  props: {
    show: {
      type: Boolean,
      default: false
    },
    message: {
      type: String,
      default: ''
    },
    type: {
      type: String,
      default: 'info', // info, success, warning, error
      validator(value) {
        return ['info', 'success', 'warning', 'error'].includes(value)
      }
    },
    duration: {
      type: Number,
      default: 3000
    }
  },
  emits: ['close'],
  watch: {
    show(newVal) {
      if (newVal && this.duration > 0) {
        this.setAutoClose()
      }
    }
  },
  methods: {
    setAutoClose() {
      clearTimeout(this.timer)
      this.timer = setTimeout(() => {
        this.$emit('close')
      }, this.duration)
    }
  },
  beforeUnmount() {
    clearTimeout(this.timer)
  }
}
</script>

<style scoped>
.notification-wrapper {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 1000;
}

.notification {
  display: flex;
  align-items: flex-start;
  min-width: 300px;
  padding: 15px;
  border-radius: 4px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  background-color: #fff;
  border-left: 4px solid #409eff;
}

.notification.success {
  border-left-color: #67c23a;
}

.notification.warning {
  border-left-color: #e6a23c;
}

.notification.error {
  border-left-color: #f56c6c;
}

.notification-content {
  flex: 1;
  padding-right: 10px;
}

.notification-content p {
  margin: 0;
  color: #606266;
}

.close-button {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: #909399;
  padding: 0;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-button:hover {
  color: #606266;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateX(100%);
}
</style>