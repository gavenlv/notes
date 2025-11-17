<template>
  <div class="mobile-card" :class="{ 'mobile-card--compact': isCompact }">
    <div class="mobile-card__header">
      <h3 class="mobile-card__title">{{ title }}</h3>
      <div class="mobile-card__actions">
        <slot name="actions"></slot>
      </div>
    </div>
    <div class="mobile-card__content">
      <slot></slot>
    </div>
    <div class="mobile-card__footer" v-if="$slots.footer">
      <slot name="footer"></slot>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

// 定义Props
interface Props {
  title?: string;
  compact?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  title: '',
  compact: false
});

// 计算属性
const isCompact = computed(() => props.compact);
</script>

<style scoped>
.mobile-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  margin-bottom: 16px;
}

.mobile-card--compact {
  border-radius: 8px;
}

.mobile-card__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #f0f0f0;
}

.mobile-card__title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.mobile-card__actions {
  display: flex;
  gap: 8px;
}

.mobile-card__content {
  padding: 16px;
}

.mobile-card__footer {
  padding: 12px 16px;
  background-color: #f9f9f9;
  border-top: 1px solid #f0f0f0;
}
</style>