<template>
  <div class="chart-container">
    <div ref="chartRef" class="chart-wrapper"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch } from 'vue';
import * as echarts from 'echarts';
import { useDebug } from '@/composables/useDebug';

const { logDebug } = useDebug();

// 定义Props
interface Props {
  options?: echarts.EChartsOption;
  theme?: string;
}

const props = withDefaults(defineProps<Props>(), {
  options: () => ({}),
  theme: ''
});

// 图表引用
const chartRef = ref<HTMLDivElement | null>(null);
let chartInstance: echarts.ECharts | null = null;

// 初始化图表
const initChart = () => {
  if (chartRef.value) {
    chartInstance = echarts.init(chartRef.value, props.theme);
    chartInstance.setOption(props.options);
    logDebug('Chart initialized');
  }
};

// 更新图表
const updateChart = () => {
  if (chartInstance) {
    chartInstance.setOption(props.options, true);
    logDebug('Chart updated');
  }
};

// 调整图表大小
const resizeChart = () => {
  if (chartInstance) {
    chartInstance.resize();
    logDebug('Chart resized');
  }
};

// 监听options变化
watch(() => props.options, () => {
  updateChart();
}, { deep: true });

// 监听窗口大小变化
const handleResize = () => {
  resizeChart();
};

// 组件挂载
onMounted(() => {
  initChart();
  window.addEventListener('resize', handleResize);
});

// 组件卸载前
onBeforeUnmount(() => {
  if (chartInstance) {
    chartInstance.dispose();
    chartInstance = null;
  }
  window.removeEventListener('resize', handleResize);
});
</script>

<style scoped>
.chart-container {
  width: 100%;
  height: 100%;
}

.chart-wrapper {
  width: 100%;
  height: 400px;
}
</style>