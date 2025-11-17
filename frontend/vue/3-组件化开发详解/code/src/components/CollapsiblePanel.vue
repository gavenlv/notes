<template>
  <div class="collapsible-panel">
    <div class="panel-header" @click="toggle">
      <h3>{{ title }}</h3>
      <span class="arrow" :class="{ rotated: isOpen }">▼</span>
    </div>
    <transition
      name="slide"
      @enter="enter"
      @after-enter="afterEnter"
      @leave="leave"
      @after-leave="afterLeave"
    >
      <div v-show="isOpen" class="panel-content">
        <div class="content-wrapper">
          <slot></slot>
        </div>
      </div>
    </transition>
  </div>
</template>

<script>
export default {
  name: 'CollapsiblePanel',
  props: {
    title: {
      type: String,
      required: true
    },
    initiallyOpen: {
      type: Boolean,
      default: false
    }
  },
  emits: ['toggle'],
  data() {
    return {
      isOpen: this.initiallyOpen
    }
  },
  methods: {
    toggle() {
      this.isOpen = !this.isOpen
      this.$emit('toggle', this.isOpen)
    },
    enter(element) {
      element.style.height = '0'
      element.style.opacity = '0'
      setTimeout(() => {
        element.style.height = element.scrollHeight + 'px'
        element.style.opacity = '1'
      }, 0)
    },
    afterEnter(element) {
      element.style.height = 'auto'
    },
    leave(element) {
      element.style.height = element.scrollHeight + 'px'
      element.style.opacity = '1'
      setTimeout(() => {
        element.style.height = '0'
        element.style.opacity = '0'
      }, 0)
    },
    afterLeave(element) {
      element.style.height = '0'
    }
  }
}
</script>

<style scoped>
.collapsible-panel {
  border: 1px solid #ddd;
  border-radius: 4px;
  overflow: hidden;
}

.panel-header {
  padding: 15px 20px;
  background-color: #f5f5f5;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.panel-header h3 {
  margin: 0;
  font-size: 18px;
}

.arrow {
  transition: transform 0.3s ease;
}

.arrow.rotated {
  transform: rotate(180deg);
}

.panel-content {
  overflow: hidden;
  transition: height 0.3s ease, opacity 0.3s ease;
}

.content-wrapper {
  padding: 20px;
}

.slide-enter-active,
.slide-leave-active {
  transition: all 0.3s ease;
}

.slide-enter-from,
.slide-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>