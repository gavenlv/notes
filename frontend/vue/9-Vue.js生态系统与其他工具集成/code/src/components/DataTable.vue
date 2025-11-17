<template>
  <div class="data-table">
    <el-table 
      :data="tableData" 
      style="width: 100%" 
      :loading="loading"
      @selection-change="handleSelectionChange"
    >
      <el-table-column type="selection" width="55"></el-table-column>
      <el-table-column prop="id" label="ID" width="80"></el-table-column>
      <el-table-column prop="name" label="Name" width="180"></el-table-column>
      <el-table-column prop="email" label="Email"></el-table-column>
      <el-table-column prop="role" label="Role" width="120"></el-table-column>
      <el-table-column label="Actions" width="200">
        <template #default="scope">
          <el-button size="small" @click="handleEdit(scope.$index, scope.row)">Edit</el-button>
          <el-button size="small" type="danger" @click="handleDelete(scope.$index, scope.row)">Delete</el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <div class="table-actions">
      <el-button type="primary" @click="handleAdd">Add User</el-button>
      <el-button type="danger" :disabled="selectedRows.length === 0" @click="handleBatchDelete">Delete Selected</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { ElTable, ElTableColumn, ElButton, ElMessage, ElMessageBox } from 'element-plus';
import { User } from '@/types';
import apiClient from '@/utils/apiClient';

// 数据表相关数据
const tableData = ref<User[]>([]);
const loading = ref(false);
const selectedRows = ref<User[]>([]);

// 获取表格数据
const fetchData = async () => {
  try {
    loading.value = true;
    const response = await apiClient.get<User[]>('/users');
    tableData.value = response.data;
  } catch (error) {
    ElMessage.error('Failed to fetch data');
    console.error(error);
  } finally {
    loading.value = false;
  }
};

// 处理选择变化
const handleSelectionChange = (rows: User[]) => {
  selectedRows.value = rows;
};

// 处理编辑操作
const handleEdit = (index: number, row: User) => {
  ElMessage.info(`Editing user: ${row.name}`);
  // 这里可以打开编辑对话框
};

// 处理删除操作
const handleDelete = (index: number, row: User) => {
  ElMessageBox.confirm(
    `Are you sure you want to delete user ${row.name}?`,
    'Confirm Delete',
    {
      confirmButtonText: 'Delete',
      cancelButtonText: 'Cancel',
      type: 'warning',
    }
  )
  .then(async () => {
    try {
      await apiClient.delete(`/users/${row.id}`);
      ElMessage.success('User deleted successfully');
      fetchData(); // 重新加载数据
    } catch (error) {
      ElMessage.error('Failed to delete user');
      console.error(error);
    }
  })
  .catch(() => {
    ElMessage.info('Delete canceled');
  });
};

// 处理添加操作
const handleAdd = () => {
  ElMessage.info('Adding new user');
  // 这里可以打开添加对话框
};

// 处理批量删除
const handleBatchDelete = () => {
  ElMessageBox.confirm(
    `Are you sure you want to delete ${selectedRows.value.length} users?`,
    'Confirm Batch Delete',
    {
      confirmButtonText: 'Delete',
      cancelButtonText: 'Cancel',
      type: 'warning',
    }
  )
  .then(async () => {
    try {
      // 批量删除逻辑
      const deletePromises = selectedRows.value.map(user => 
        apiClient.delete(`/users/${user.id}`)
      );
      
      await Promise.all(deletePromises);
      ElMessage.success('Users deleted successfully');
      fetchData(); // 重新加载数据
    } catch (error) {
      ElMessage.error('Failed to delete users');
      console.error(error);
    }
  })
  .catch(() => {
    ElMessage.info('Batch delete canceled');
  });
};

// 组件挂载时获取数据
onMounted(() => {
  fetchData();
});
</script>

<style scoped>
.data-table {
  margin: 20px 0;
}

.table-actions {
  margin-top: 20px;
  display: flex;
  gap: 10px;
}
</style>