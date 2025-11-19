// Vue 3 组合函数 - 分页逻辑

import { ref, computed, reactive } from 'vue';

// 分页配置接口
export interface PaginationConfig {
  initialPage?: number;
  initialPageSize?: number;
  totalItems?: number;
}

// 分页信息接口
export interface PaginationInfo {
  currentPage: number;
  pageSize: number;
  totalPages: number;
  totalItems: number;
  hasNextPage: boolean;
  hasPrevPage: boolean;
  startItem: number;
  endItem: number;
}

/**
 * 分页组合函数
 * @param config 分页配置
 * @returns 分页状态和方法
 */
export function usePagination(config: PaginationConfig = {}) {
  // 默认配置
  const {
    initialPage = 1,
    initialPageSize = 10,
    totalItems = 0
  } = config;
  
  // 状态
  const currentPage = ref(initialPage);
  const pageSize = ref(initialPageSize);
  const total = ref(totalItems);
  
  // 计算属性
  const totalPages = computed(() => Math.ceil(total.value / pageSize.value));
  
  const hasNextPage = computed(() => currentPage.value < totalPages.value);
  const hasPrevPage = computed(() => currentPage.value > 1);
  
  const startItem = computed(() => {
    if (total.value === 0) return 0;
    return (currentPage.value - 1) * pageSize.value + 1;
  });
  
  const endItem = computed(() => {
    return Math.min(currentPage.value * pageSize.value, total.value);
  });
  
  // 分页信息
  const paginationInfo = computed<PaginationInfo>(() => ({
    currentPage: currentPage.value,
    pageSize: pageSize.value,
    totalPages: totalPages.value,
    totalItems: total.value,
    hasNextPage: hasNextPage.value,
    hasPrevPage: hasPrevPage.value,
    startItem: startItem.value,
    endItem: endItem.value
  }));
  
  // 方法
  const goToPage = (page: number) => {
    if (page >= 1 && page <= totalPages.value) {
      currentPage.value = page;
    }
  };
  
  const nextPage = () => {
    if (hasNextPage.value) {
      currentPage.value++;
    }
  };
  
  const prevPage = () => {
    if (hasPrevPage.value) {
      currentPage.value--;
    }
  };
  
  const firstPage = () => {
    currentPage.value = 1;
  };
  
  const lastPage = () => {
    currentPage.value = totalPages.value;
  };
  
  const setPageSize = (size: number) => {
    pageSize.value = size;
    // 重置到第一页
    currentPage.value = 1;
  };
  
  const updateTotal = (newTotal: number) => {
    total.value = newTotal;
    // 如果当前页超出范围，调整到有效页面
    if (currentPage.value > totalPages.value) {
      currentPage.value = Math.max(1, totalPages.value);
    }
  };
  
  // 重置分页
  const resetPagination = () => {
    currentPage.value = initialPage;
    pageSize.value = initialPageSize;
    total.value = totalItems;
  };
  
  return {
    // 状态
    currentPage,
    pageSize,
    total,
    
    // 计算属性
    totalPages,
    hasNextPage,
    hasPrevPage,
    startItem,
    endItem,
    paginationInfo,
    
    // 方法
    goToPage,
    nextPage,
    prevPage,
    firstPage,
    lastPage,
    setPageSize,
    updateTotal,
    resetPagination
  };
}

/**
 * 带数据的分页组合函数
 * @param fetchData 获取数据的函数
 * @param config 分页配置
 * @returns 分页状态、数据和方法
 */
export function usePaginatedData<T>(
  fetchData: (page: number, pageSize: number) => Promise<{
    items: T[];
    total: number;
  }>,
  config: PaginationConfig = {}
) {
  const pagination = usePagination(config);
  const items = ref<T[]>([]);
  const isLoading = ref(false);
  const error = ref<string | null>(null);
  
  // 获取数据
  const loadData = async () => {
    isLoading.value = true;
    error.value = null;
    
    try {
      const result = await fetchData(pagination.currentPage.value, pagination.pageSize.value);
      items.value = result.items;
      pagination.updateTotal(result.total);
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to load data';
      items.value = [];
    } finally {
      isLoading.value = false;
    }
  };
  
  // 重新加载数据
  const refresh = () => {
    return loadData();
  };
  
  // 跳转到指定页并加载数据
  const goToPage = async (page: number) => {
    pagination.goToPage(page);
    return loadData();
  };
  
  // 下一页并加载数据
  const nextPage = async () => {
    if (pagination.hasNextPage.value) {
      pagination.nextPage();
      return loadData();
    }
  };
  
  // 上一页并加载数据
  const prevPage = async () => {
    if (pagination.hasPrevPage.value) {
      pagination.prevPage();
      return loadData();
    }
  };
  
  // 更新页面大小并重新加载数据
  const setPageSize = async (size: number) => {
    pagination.setPageSize(size);
    return loadData();
  };
  
  // 初始加载数据
  if (config.totalItems === undefined) {
    loadData();
  }
  
  return {
    // 数据
    items,
    isLoading,
    error,
    
    // 分页状态和方法
    ...pagination,
    
    // 数据方法
    loadData,
    refresh,
    goToPage,
    nextPage,
    prevPage,
    setPageSize
  };
}