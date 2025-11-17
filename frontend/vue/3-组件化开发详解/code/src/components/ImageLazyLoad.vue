<template>
  <div class="image-lazy-load">
    <img
      v-if="isLoaded"
      :src="src"
      :alt="alt"
      :class="imgClass"
      @load="onLoad"
      @error="onError"
    />
    <div
      v-else
      class="placeholder"
      :style="placeholderStyle"
    >
      <div v-if="!hasError" class="loading">加载中...</div>
      <div v-else class="error">加载失败</div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ImageLazyLoadComponent',
  props: {
    src: {
      type: String,
      required: true
    },
    alt: {
      type: String,
      default: ''
    },
    width: {
      type: [String, Number],
      default: '100%'
    },
    height: {
      type: [String, Number],
      default: '200px'
    },
    imgClass: {
      type: String,
      default: ''
    }
  },
  emits: ['load', 'error'],
  data() {
    return {
      isLoaded: false,
      hasError: false,
      observer: null
    }
  },
  computed: {
    placeholderStyle() {
      return {
        width: typeof this.width === 'number' ? this.width + 'px' : this.width,
        height: typeof this.height === 'number' ? this.height + 'px' : this.height
      }
    }
  },
  mounted() {
    // 检查浏览器是否支持 IntersectionObserver
    if ('IntersectionObserver' in window) {
      this.observer = new IntersectionObserver(
        this.handleIntersection,
        {
          root: null,
          rootMargin: '0px',
          threshold: 0.1
        }
      )
      
      this.observer.observe(this.$el)
    } else {
      // 如果不支持，则直接加载图片
      this.loadImage()
    }
  },
  beforeUnmount() {
    if (this.observer) {
      this.observer.disconnect()
    }
  },
  methods: {
    handleIntersection(entries) {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          this.loadImage()
          // 加载后停止观察
          if (this.observer) {
            this.observer.unobserve(entry.target)
          }
        }
      })
    },
    
    loadImage() {
      // 创建一个新的 Image 对象来预加载图片
      const img = new Image()
      img.onload = () => {
        this.isLoaded = true
        this.$emit('load', this.src)
      }
      img.onerror = () => {
        this.hasError = true
        this.$emit('error', this.src)
      }
      img.src = this.src
    },
    
    onLoad() {
      // 图片加载完成事件
    },
    
    onError() {
      // 图片加载失败事件
      this.hasError = true
    }
  }
}
</script>

<style scoped>
.image-lazy-load {
  display: inline-block;
  overflow: hidden;
}

.placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f5f5f5;
  border-radius: 4px;
}

.loading {
  color: #999;
  font-size: 14px;
}

.error {
  color: #f56c6c;
  font-size: 14px;
}

img {
  display: block;
  max-width: 100%;
  height: auto;
  transition: opacity 0.3s;
}
</style>