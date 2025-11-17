<template>
  <div class="user-profile">
    <h2>User Profile</h2>
    <div v-if="loading">Loading...</div>
    <div v-else-if="user">
      <p>Name: {{ user.name }}</p>
      <p>Email: {{ user.email }}</p>
      <button @click="updateUser">Update User</button>
    </div>
    <div v-else>No user data</div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { User } from '@/types';
import apiClient from '@/utils/apiClient';
import { useDebug } from '@/composables/useDebug';

const { logDebug } = useDebug();

// 响应式数据
const user = ref<User | null>(null);
const loading = ref(true);

// 获取用户信息
const fetchUser = async () => {
  try {
    loading.value = true;
    const response = await apiClient.get<User>('/user/profile');
    user.value = response.data;
    logDebug('User fetched:', user.value);
  } catch (error) {
    console.error('Failed to fetch user:', error);
  } finally {
    loading.value = false;
  }
};

// 更新用户信息
const updateUser = async () => {
  if (!user.value) return;
  
  try {
    const updatedUser = { ...user.value, name: `${user.value.name} (updated)` };
    const response = await apiClient.put<User>('/user/profile', updatedUser);
    user.value = response.data;
    logDebug('User updated:', user.value);
  } catch (error) {
    console.error('Failed to update user:', error);
  }
};

// 组件挂载时获取用户信息
onMounted(() => {
  fetchUser();
});
</script>

<style scoped>
.user-profile {
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 4px;
  margin: 10px 0;
}
</style>