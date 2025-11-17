<template>
  <div class="lazy-load-demo">
    <h1>Lazy Load Images Demo</h1>
    <p>This page demonstrates lazy loading of images for performance optimization.</p>
    
    <div class="image-gallery">
      <div 
        v-for="(image, index) in images" 
        :key="image.id" 
        class="image-card"
      >
        <h3>{{ image.title }}</h3>
        <LazyImage 
          :src="image.url" 
          :alt="image.title"
          width="300"
          height="200"
          lazy
        />
        <p>Image {{ index + 1 }} of {{ images.length }}</p>
      </div>
    </div>
  </div>
</template>

<script>
import LazyImage from '@/components/LazyImage.vue'

export default {
  name: 'LazyLoadDemo',
  components: {
    LazyImage
  },
  data() {
    return {
      images: [
        {
          id: 1,
          title: 'Mountain Landscape',
          url: 'https://picsum.photos/300/200?random=1'
        },
        {
          id: 2,
          title: 'Ocean View',
          url: 'https://picsum.photos/300/200?random=2'
        },
        {
          id: 3,
          title: 'Forest Path',
          url: 'https://picsum.photos/300/200?random=3'
        },
        {
          id: 4,
          title: 'City Skyline',
          url: 'https://picsum.photos/300/200?random=4'
        },
        {
          id: 5,
          title: 'Desert Dunes',
          url: 'https://picsum.photos/300/200?random=5'
        },
        {
          id: 6,
          title: 'Snowy Mountains',
          url: 'https://picsum.photos/300/200?random=6'
        },
        {
          id: 7,
          title: 'Tropical Beach',
          url: 'https://picsum.photos/300/200?random=7'
        },
        {
          id: 8,
          title: 'Autumn Colors',
          url: 'https://picsum.photos/300/200?random=8'
        }
      ]
    }
  }
}
</script>

<style scoped>
.lazy-load-demo {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.image-gallery {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 30px;
  margin-top: 30px;
}

.image-card {
  text-align: center;
}

.image-card h3 {
  margin-bottom: 10px;
}
</style>