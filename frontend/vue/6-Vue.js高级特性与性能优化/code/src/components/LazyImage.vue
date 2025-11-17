<template>
  <div class="lazy-image" ref="imageContainer">
    <img 
      v-if="loaded" 
      :src="src" 
      :alt="alt"
      :class="imgClass"
    >
    <div v-else class="placeholder" :style="placeholderStyle">
      <div class="loading-spinner" v-if="loading">Loading...</div>
      <div v-else class="load-button" @click="loadImage">Load Image</div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'LazyImage',
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
    },
    lazy: {
      type: Boolean,
      default: true
    }
  },
  data() {
    return {
      loaded: !this.lazy,
      loading: false,
      observer: null
    }
  },
  computed: {
    placeholderStyle() {
      return {
        width: typeof this.width === 'number' ? `${this.width}px` : this.width,
        height: typeof this.height === 'number' ? `${this.height}px` : this.height
      }
    }
  },
  methods: {
    loadImage() {
      if (this.loaded) return
      
      this.loading = true
      
      // 创建新的图片对象来预加载
      const img = new Image()
      img.onload = () => {
        this.loaded = true
        this.loading = false
      }
      img.onerror = () => {
        this.loading = false
        console.error('Failed to load image:', this.src)
      }
      img.src = this.src
    },
    
    createObserver() {
      // 使用Intersection Observer API实现懒加载
      this.observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            this.loadImage()
            // 加载后取消观察
            if (this.observer) {
              this.observer.unobserve(this.$refs.imageContainer)
              this.observer = null
            }
          }
        })
      }, {
        rootMargin: '50px' // 提前50px开始加载
      })
      
      this.observer.observe(this.$refs.imageContainer)
    }
  },
  
  mounted() {
    if (this.lazy) {
      // 检查是否支持Intersection Observer
      if ('IntersectionObserver' in window) {
        this.createObserver()
      } else {
        // 不支持的话直接加载
        this.loadImage()
      }
    }
  },
  
  beforeUnmount() {
    // 清理observer
    if (this.observer) {
      this.observer.disconnect()
    }
  }
}
</script>

<style scoped>
.lazy-image {
  display: inline-block;
}

.placeholder {
  background-color: #f5f5f5;
  display: flex;
  justify-content: center;
  align-items: center;
  border-radius: 4px;
}

.loading-spinner {
  color: #999;
}

.load-button {
  padding: 8px 16px;
  background-color: #42b983;
  color: white;
  border-radius: 4px;
  cursor: pointer;
}

img {
  max-width: 100%;
  border-radius: 4px;
}
</style>