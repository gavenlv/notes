<!-- Vue 3 + TypeScript 用户卡片组件 -->
<template>
  <div class="user-card">
    <div class="user-avatar">
      <img v-if="user.avatar" :src="user.avatar" :alt="user.name" />
      <div v-else class="avatar-placeholder">
        {{ user.name.charAt(0).toUpperCase() }}
      </div>
    </div>
    
    <div class="user-info">
      <h3 class="user-name">{{ user.name }}</h3>
      <p class="user-email">{{ user.email }}</p>
      <div 
        class="user-role"
        :style="{ backgroundColor: roleColors[user.role] }"
      >
        {{ formatRole(user.role) }}
      </div>
      
      <div class="user-dates">
        <span>创建于: {{ formatDate(user.createdAt) }}</span>
        <span v-if="user.updatedAt !== user.createdAt">
          更新于: {{ formatDate(user.updatedAt) }}
        </span>
      </div>
    </div>
    
    <div v-if="showActions" class="user-actions">
      <button 
        class="edit-button" 
        @click="handleEdit"
        :disabled="isLoading"
      >
        编辑
      </button>
      <button 
        class="delete-button" 
        @click="handleDelete"
        :disabled="isLoading"
      >
        {{ isLoading ? '删除中...' : '删除' }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

// 用户接口
interface User {
  id: string;
  name: string;
  email: string;
  role: 'admin' | 'user' | 'guest';
  avatar?: string;
  createdAt: string;
  updatedAt: string;
}

// 组件属性
interface Props {
  user: User;
  showActions?: boolean;
}

// 组件事件
interface Emits {
  edit: [userId: string];
  delete: [userId: string];
}

// 定义组件属性和事件
const props = withDefaults(defineProps<Props>(), {
  showActions: true
});

const emit = defineEmits<Emits>();

// 状态
const isLoading = ref(false);

// 角色颜色映射
const roleColors = {
  admin: '#e74c3c',
  user: '#3498db',
  guest: '#95a5a6'
};

// 方法
const formatDate = (dateString: string): string => {
  return new Date(dateString).toLocaleDateString();
};

const formatRole = (role: string): string => {
  return role.charAt(0).toUpperCase() + role.slice(1);
};

const handleEdit = (): void => {
  emit('edit', props.user.id);
};

const handleDelete = async (): Promise<void> => {
  if (window.confirm(`确定要删除用户 ${props.user.name} 吗？`)) {
    isLoading.value = true;
    try {
      emit('delete', props.user.id);
    } finally {
      isLoading.value = false;
    }
  }
};
</script>

<style scoped>
.user-card {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  transition: transform 0.2s;
}

.user-card:hover {
  transform: translateY(-4px);
}

.user-avatar {
  height: 120px;
  background-color: #ecf0f1;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.user-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-placeholder {
  width: 80px;
  height: 80px;
  background-color: #3498db;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  font-weight: 700;
}

.user-info {
  padding: 1.5rem;
}

.user-name {
  font-size: 1.2rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: #2c3e50;
}

.user-email {
  color: #7f8c8d;
  margin-bottom: 1rem;
}

.user-role {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  color: white;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
  margin-bottom: 1rem;
}

.user-dates {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  font-size: 0.8rem;
  color: #95a5a6;
}

.user-actions {
  display: flex;
  border-top: 1px solid #ecf0f1;
}

.edit-button,
.delete-button {
  flex: 1;
  padding: 0.75rem;
  border: none;
  background: none;
  cursor: pointer;
  transition: background-color 0.2s;
}

.edit-button {
  color: #3498db;
}

.edit-button:hover {
  background-color: rgba(52, 152, 219, 0.1);
}

.delete-button {
  color: #e74c3c;
}

.delete-button:hover {
  background-color: rgba(231, 76, 60, 0.1);
}

.edit-button:disabled,
.delete-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>