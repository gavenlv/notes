// React + TypeScript API Hook

import { useState, useEffect, useCallback } from 'react';

// API状态接口
interface ApiState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

// API选项接口
interface ApiOptions<T> {
  immediate?: boolean;
  onSuccess?: (data: T) => void;
  onError?: (error: string) => void;
  refetchInterval?: number;
}

// 通用API Hook
export function useApi<T>(
  url: string,
  options: ApiOptions<T> = {}
) {
  const [state, setState] = useState<ApiState<T>>({
    data: null,
    loading: false,
    error: null
  });
  
  const { immediate = true, onSuccess, onError, refetchInterval } = options;
  
  // 定义获取数据的函数
  const fetchData = useCallback(async () => {
    setState(prev => ({ ...prev, loading: true, error: null }));
    
    try {
      const response = await fetch(url);
      
      if (!response.ok) {
        throw new Error(`Error: ${response.status} ${response.statusText}`);
      }
      
      const data = await response.json() as T;
      setState({ data, loading: false, error: null });
      
      if (onSuccess) {
        onSuccess(data);
      }
      
      return data;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      setState(prev => ({
        ...prev,
        loading: false,
        error: errorMessage
      }));
      
      if (onError) {
        onError(errorMessage);
      }
      
      throw error;
    }
  }, [url, onSuccess, onError]);
  
  // 立即获取数据
  useEffect(() => {
    if (immediate) {
      fetchData();
    }
  }, [immediate, fetchData]);
  
  // 设置定时刷新
  useEffect(() => {
    if (refetchInterval && refetchInterval > 0) {
      const interval = setInterval(fetchData, refetchInterval);
      return () => clearInterval(interval);
    }
  }, [fetchData, refetchInterval]);
  
  return {
    ...state,
    fetchData,
    refetch: fetchData,
    reset: () => setState({ data: null, loading: false, error: null })
  };
}

// CRUD操作Hook
export function useCrudApi<T>(
  baseUrl: string,
  options: ApiOptions<T> = {}
) {
  const apiState = useApi<T[]>(baseUrl, options);
  
  // 创建项目
  const createItem = useCallback(async (item: Omit<T, 'id'>): Promise<T> => {
    const response = await fetch(baseUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(item)
    });
    
    if (!response.ok) {
      throw new Error(`Create error: ${response.status} ${response.statusText}`);
    }
    
    const newItem = await response.json() as T;
    
    // 更新本地状态
    if (apiState.data) {
      apiState.fetchData();
    }
    
    return newItem;
  }, [baseUrl, apiState]);
  
  // 更新项目
  const updateItem = useCallback(async (id: string | number, updates: Partial<T>): Promise<T> => {
    const response = await fetch(`${baseUrl}/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(updates)
    });
    
    if (!response.ok) {
      throw new Error(`Update error: ${response.status} ${response.statusText}`);
    }
    
    const updatedItem = await response.json() as T;
    
    // 更新本地状态
    if (apiState.data) {
      apiState.fetchData();
    }
    
    return updatedItem;
  }, [baseUrl, apiState]);
  
  // 删除项目
  const deleteItem = useCallback(async (id: string | number): Promise<boolean> => {
    const response = await fetch(`${baseUrl}/${id}`, {
      method: 'DELETE'
    });
    
    if (!response.ok) {
      throw new Error(`Delete error: ${response.status} ${response.statusText}`);
    }
    
    // 更新本地状态
    if (apiState.data) {
      apiState.fetchData();
    }
    
    return true;
  }, [baseUrl, apiState]);
  
  return {
    ...apiState,
    createItem,
    updateItem,
    deleteItem
  };
}

// 分页API Hook
export function usePaginatedApi<T>(
  baseUrl: string,
  initialPage = 1,
  pageSize = 10
) {
  const [currentPage, setCurrentPage] = useState(initialPage);
  const [totalItems, setTotalItems] = useState(0);
  
  const url = `${baseUrl}?page=${currentPage}&limit=${pageSize}`;
  const { data, loading, error, fetchData } = useApi<{
    items: T[];
    total: number;
    page: number;
    totalPages: number;
  }>(url);
  
  // 更新总项目数
  useEffect(() => {
    if (data) {
      setTotalItems(data.total);
    }
  }, [data]);
  
  // 计算总页数
  const totalPages = data ? data.totalPages : Math.ceil(totalItems / pageSize);
  
  // 页面导航函数
  const goToPage = useCallback((page: number) => {
    if (page >= 1 && page <= totalPages) {
      setCurrentPage(page);
    }
  }, [totalPages]);
  
  const nextPage = useCallback(() => {
    goToPage(currentPage + 1);
  }, [currentPage, goToPage]);
  
  const prevPage = useCallback(() => {
    goToPage(currentPage - 1);
  }, [currentPage, goToPage]);
  
  const firstPage = useCallback(() => {
    goToPage(1);
  }, [goToPage]);
  
  const lastPage = useCallback(() => {
    goToPage(totalPages);
  }, [goToPage, totalPages]);
  
  // 计算分页信息
  const paginationInfo = {
    currentPage,
    totalPages,
    pageSize,
    totalItems,
    hasNextPage: currentPage < totalPages,
    hasPrevPage: currentPage > 1,
    startItem: (currentPage - 1) * pageSize + 1,
    endItem: Math.min(currentPage * pageSize, totalItems)
  };
  
  return {
    items: data?.items || [],
    loading,
    error,
    paginationInfo,
    goToPage,
    nextPage,
    prevPage,
    firstPage,
    lastPage,
    refetch: fetchData
  };
}