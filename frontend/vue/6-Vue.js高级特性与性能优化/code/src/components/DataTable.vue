<template>
  <div class="data-table">
    <div class="table-header">
      <slot name="header">
        <h3>Data Table</h3>
      </slot>
    </div>
    
    <div class="table-body">
      <div v-for="item in items" :key="item.id" class="table-row">
        <slot name="item" :item="item">
          <div class="default-item">
            {{ item }}
          </div>
        </slot>
      </div>
    </div>
    
    <div class="table-footer">
      <slot name="footer">
        <p>Total items: {{ items.length }}</p>
      </slot>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DataTable',
  props: {
    items: {
      type: Array,
      required: true
    }
  }
}
</script>

<style scoped>
.data-table {
  border: 1px solid #ddd;
  border-radius: 4px;
  overflow: hidden;
  margin: 20px 0;
}

.table-header {
  background-color: #f5f5f5;
  padding: 10px 20px;
  border-bottom: 1px solid #ddd;
}

.table-body {
  padding: 0;
}

.table-row {
  border-bottom: 1px solid #eee;
}

.table-row:last-child {
  border-bottom: none;
}

.default-item {
  padding: 10px 20px;
}

.table-footer {
  background-color: #f5f5f5;
  padding: 10px 20px;
  border-top: 1px solid #ddd;
  text-align: right;
}
</style>