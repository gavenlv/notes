import { ref, Ref } from 'vue';
import apiClient from '@/utils/apiClient';
import { ApiResponse } from '@/types';

// 泛型API组合式函数
export function useApi<T>() {
  const data = ref<T | null>(null) as Ref<T | null>;
  const loading = ref(false);
  const error = ref<string | null>(null);

  // GET请求
  const get = async (url: string) => {
    try {
      loading.value = true;
      error.value = null;
      const response: ApiResponse<T> = await apiClient.get<T>(url);
      data.value = response.data;
      return response;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error';
      throw err;
    } finally {
      loading.value = false;
    }
  };

  // POST请求
  const post = async (url: string, payload: any) => {
    try {
      loading.value = true;
      error.value = null;
      const response: ApiResponse<T> = await apiClient.post<T>(url, payload);
      data.value = response.data;
      return response;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error';
      throw err;
    } finally {
      loading.value = false;
    }
  };

  // PUT请求
  const put = async (url: string, payload: any) => {
    try {
      loading.value = true;
      error.value = null;
      const response: ApiResponse<T> = await apiClient.put<T>(url, payload);
      data.value = response.data;
      return response;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error';
      throw err;
    } finally {
      loading.value = false;
    }
  };

  // DELETE请求
  const remove = async (url: string) => {
    try {
      loading.value = true;
      error.value = null;
      const response: ApiResponse<T> = await apiClient.delete<T>(url);
      return response;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error';
      throw err;
    } finally {
      loading.value = false;
    }
  };

  return {
    data: data as Readonly<Ref<T | null>>,
    loading: loading as Readonly<Ref<boolean>>,
    error: error as Readonly<Ref<string | null>>,
    get,
    post,
    put,
    remove
  };
}