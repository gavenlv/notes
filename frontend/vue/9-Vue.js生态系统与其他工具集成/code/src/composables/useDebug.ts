import { ref, Ref } from 'vue';

// 调试相关的组合式函数
export function useDebug() {
  const isDebugEnabled = ref(false);

  // 切换调试模式
  const toggleDebug = () => {
    isDebugEnabled.value = !isDebugEnabled.value;
    localStorage.setItem('debug', isDebugEnabled.value.toString());
  };

  // 初始化调试模式
  const initDebug = () => {
    const debugFlag = localStorage.getItem('debug');
    isDebugEnabled.value = debugFlag === 'true';
  };

  // 记录调试信息
  const logDebug = (...args: any[]) => {
    if (isDebugEnabled.value) {
      console.log('[DEBUG]', ...args);
    }
  };

  return {
    isDebugEnabled: isDebugEnabled as Readonly<Ref<boolean>>,
    toggleDebug,
    initDebug,
    logDebug
  };
}