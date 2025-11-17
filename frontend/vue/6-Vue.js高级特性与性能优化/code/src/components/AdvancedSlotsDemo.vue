<template>
  <div class="advanced-slots-demo">
    <h2>Advanced Slots Demo</h2>
    
    <!-- 默认插槽 -->
    <BaseLayout>
      <p>This content goes in the default slot.</p>
    </BaseLayout>
    
    <!-- 具名插槽 -->
    <BaseLayout>
      <template #header>
        <h3>Custom Header</h3>
      </template>
      
      <p>This content goes in the default slot.</p>
      
      <template #footer>
        <p>Custom Footer Content</p>
      </template>
    </BaseLayout>
    
    <!-- 作用域插槽 -->
    <DataTable :items="users">
      <template #item="{ item }">
        <div class="user-item">
          <strong>{{ item.name }}</strong> - {{ item.email }}
        </div>
      </template>
    </DataTable>
  </div>
</template>

<script>
import BaseLayout from './BaseLayout.vue'
import DataTable from './DataTable.vue'

export default {
  name: 'AdvancedSlotsDemo',
  components: {
    BaseLayout,
    DataTable
  },
  data() {
    return {
      users: [
        { id: 1, name: 'John Doe', email: 'john@example.com' },
        { id: 2, name: 'Jane Smith', email: 'jane@example.com' },
        { id: 3, name: 'Bob Johnson', email: 'bob@example.com' }
      ]
    }
  }
}
</script>

<style scoped>
.advanced-slots-demo {
  margin: 20px 0;
}

.user-item {
  padding: 10px;
  border-bottom: 1px solid #eee;
}

.user-item:last-child {
  border-bottom: none;
}
</style>