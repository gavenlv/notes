<template>
  <div class="todo-item" :class="{ completed: todo.completed }">
    <input 
      type="checkbox" 
      :checked="todo.completed" 
      @change="$emit('toggle-complete', todo.id)"
    >
    <span class="todo-text">{{ todo.text }}</span>
    <button @click="$emit('delete-todo', todo.id)" class="delete-btn">删除</button>
  </div>
</template>

<script>
export default {
  name: 'TodoItem',
  props: {
    todo: {
      type: Object,
      required: true
    }
  },
  emits: ['toggle-complete', 'delete-todo']
}
</script>

<style scoped>
.todo-item {
  display: flex;
  align-items: center;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  margin-bottom: 10px;
  background-color: #fff;
}

.todo-item.completed {
  background-color: #f8f9fa;
}

.todo-item.completed .todo-text {
  text-decoration: line-through;
  color: #6c757d;
}

.todo-text {
  flex: 1;
  margin: 0 10px;
  text-align: left;
}

.delete-btn {
  background-color: #dc3545;
  border: none;
  color: white;
  padding: 4px 8px;
  text-align: center;
  text-decoration: none;
  display: inline-block;
  font-size: 12px;
  cursor: pointer;
  border-radius: 4px;
}

.delete-btn:hover {
  background-color: #c82333;
}
</style>