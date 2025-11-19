// Vue与TypeScript集成示例

import { User } from './src/types/user.types';

/**
 * Vue示例类
 */
export class VueExample {
    /**
     * 运行所有Vue示例
     */
    runExamples(): void {
        this.demonstrateComponentScript();
        this.demonstrateCompositionApi();
        this.demonstratePiniaStore();
        this.demonstrateComposables();
    }
    
    /**
     * 演示组件脚本类型定义
     */
    private demonstrateComponentScript(): void {
        console.log("\n1. Vue组件类型定义:");
        console.log(`
// 选项式API
<script lang="ts">
import { defineComponent, PropType } from 'vue';

interface User {
  id: string;
  name: string;
  email: string;
  role: 'admin' | 'user' | 'guest';
}

export default defineComponent({
  name: 'UserCard',
  props: {
    user: {
      type: Object as PropType<User>,
      required: true
    },
    showActions: {
      type: Boolean,
      default: true
    }
  },
  emits: {
    edit: (userId: string) => true,
    delete: (userId: string) => true
  },
  methods: {
    onEdit() {
      this.$emit('edit', this.user.id);
    },
    onDelete() {
      this.$emit('delete', this.user.id);
    }
  }
});
</script>
        `);
    }
    
    /**
     * 演示组合式API类型定义
     */
    private demonstrateCompositionApi(): void {
        console.log("\n2. 组合式API类型定义:");
        console.log(`
// 组合式API
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';

interface User {
  id: string;
  name: string;
  email: string;
  role: 'admin' | 'user' | 'guest';
}

// 组件属性
interface Props {
  user: User;
  showActions?: boolean;
}

// 定义组件属性和事件
const props = withDefaults(defineProps<Props>(), {
  showActions: true
});

// 定义事件
interface Emits {
  edit: [userId: string];
  delete: [userId: string];
}

const emit = defineEmits<Emits>();

// 响应式状态
const isLoading = ref(false);
const isAdmin = computed(() => props.user.role === 'admin');

// 方法
const handleEdit = (): void => {
  emit('edit', props.user.id);
};

const handleDelete = (): void => {
  emit('delete', props.user.id);
};
</script>
        `);
    }
    
    /**
     * 演示Pinia状态管理
     */
    private demonstratePiniaStore(): void {
        console.log("\n3. Pinia状态管理:");
        console.log(`
// 用户store
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

interface User {
  id: string;
  name: string;
  email: string;
  role: 'admin' | 'user' | 'guest';
}

export const useUserStore = defineStore('user', () => {
  // 状态
  const users = ref<User[]>([]);
  const currentUser = ref<User | null>(null);
  const loading = ref(false);
  
  // 计算属性
  const isAuthenticated = computed(() => !!currentUser.value);
  const isAdmin = computed(() => currentUser.value?.role === 'admin');
  
  // 操作
  const fetchUsers = async () => {
    loading.value = true;
    try {
      const response = await fetch('/api/users');
      const data = await response.json() as User[];
      users.value = data;
    } finally {
      loading.value = false;
    }
  };
  
  const setCurrentUser = (user: User | null) => {
    currentUser.value = user;
  };
  
  return {
    // 状态
    users,
    currentUser,
    loading,
    
    // 计算属性
    isAuthenticated,
    isAdmin,
    
    // 操作
    fetchUsers,
    setCurrentUser
  };
});
        `);
    }
    
    /**
     * 演示组合函数
     */
    private demonstrateComposables(): void {
        console.log("\n4. 组合函数:");
        console.log(`
// API组合函数
import { ref, computed } from 'vue';

interface ApiResponse<T> {
  data: T;
  success: boolean;
  message?: string;
}

export function useApi<T>(url: string) {
  const data = ref<T | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);
  
  const isLoading = computed(() => loading.value);
  const isError = computed(() => !!error.value);
  const isSuccess = computed(() => !loading.value && !error.value && !!data.value);
  
  const fetchData = async () => {
    loading.value = true;
    error.value = null;
    
    try {
      const response = await fetch(url);
      
      if (!response.ok) {
        throw new Error(\`Error: \${response.status}\`);
      }
      
      const result = await response.json() as ApiResponse<T>;
      data.value = result.data;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error';
    } finally {
      loading.value = false;
    }
  };
  
  return {
    data,
    isLoading,
    isError,
    isSuccess,
    fetchData
  };
}

// 分页组合函数
export function usePagination<T>(
  items: T[], 
  pageSize = 10
) {
  const currentPage = ref(1);
  
  const totalPages = computed(() => Math.ceil(items.length / pageSize));
  
  const paginatedItems = computed(() => {
    const start = (currentPage.value - 1) * pageSize;
    const end = start + pageSize;
    return items.slice(start, end);
  });
  
  const hasNextPage = computed(() => currentPage.value < totalPages.value);
  const hasPrevPage = computed(() => currentPage.value > 1);
  
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
  
  return {
    currentPage,
    totalPages,
    paginatedItems,
    hasNextPage,
    hasPrevPage,
    nextPage,
    prevPage
  };
}
        `);
    }
}