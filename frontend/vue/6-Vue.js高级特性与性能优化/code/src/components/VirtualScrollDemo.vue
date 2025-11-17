<template>
  <div class="virtual-scroll-demo">
    <h2>Virtual Scroll Demo</h2>
    <p>Rendering a list of {{ items.length }} items efficiently</p>
    
    <div class="scroll-container" ref="scrollContainer" @scroll="handleScroll">
      <div class="scroll-placeholder" :style="{ height: `${totalHeight}px` }"></div>
      <div class="scroll-content" :style="{ transform: `translateY(${offsetY}px)` }">
        <div
          v-for="item in visibleItems"
          :key="item.id"
          class="list-item"
          :style="{ height: `${itemHeight}px` }"
        >
          <div class="item-content">
            <strong>Item {{ item.id }}</strong>
            <p>{{ item.content }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'VirtualScrollDemo',
  data() {
    return {
      items: [],
      itemHeight: 80,
      containerHeight: 400,
      scrollTop: 0
    }
  },
  computed: {
    totalHeight() {
      return this.items.length * this.itemHeight
    },
    visibleCount() {
      return Math.ceil(this.containerHeight / this.itemHeight) + 2 // 添加缓冲项
    },
    startIndex() {
      return Math.floor(this.scrollTop / this.itemHeight)
    },
    endIndex() {
      return Math.min(this.startIndex + this.visibleCount, this.items.length)
    },
    visibleItems() {
      return this.items.slice(this.startIndex, this.endIndex)
    },
    offsetY() {
      return this.startIndex * this.itemHeight
    }
  },
  methods: {
    handleScroll(event) {
      this.scrollTop = event.target.scrollTop
    }
  },
  created() {
    // 生成大量数据项
    this.items = Array.from({ length: 10000 }, (_, i) => ({
      id: i + 1,
      content: `This is item ${i + 1} with some sample content to demonstrate virtual scrolling.`
    }))
  },
  mounted() {
    // 设置容器高度
    this.$refs.scrollContainer.style.height = `${this.containerHeight}px`
  }
}
</script>

<style scoped>
.virtual-scroll-demo {
  margin: 20px 0;
}

.scroll-container {
  border: 1px solid #ddd;
  border-radius: 4px;
  overflow-y: auto;
  position: relative;
}

.scroll-placeholder {
  position: absolute;
  width: 100%;
}

.scroll-content {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
}

.list-item {
  border-bottom: 1px solid #eee;
}

.item-content {
  padding: 10px 20px;
}
</style>