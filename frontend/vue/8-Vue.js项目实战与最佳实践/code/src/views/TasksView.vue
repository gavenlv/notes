<template>
  <div class="tasks-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>任务管理</span>
          <el-button 
            type="primary" 
            @click="showCreateDialog = true"
            style="float: right;"
          >
            新建任务
          </el-button>
        </div>
      </template>
      
      <el-table :data="tasks" style="width: 100%" v-loading="loading">
        <el-table-column prop="title" label="任务标题" width="200" />
        <el-table-column prop="description" label="任务描述" />
        <el-table-column label="状态" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.completed ? 'success' : 'warning'">
              {{ scope.row.completed ? '已完成' : '进行中' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button 
              size="small" 
              @click="editTask(scope.row)"
            >
              编辑
            </el-button>
            <el-button 
              size="small" 
              type="danger" 
              @click="deleteTask(scope.row.id)"
            >
              删除
            </el-button>
            <el-button 
              size="small" 
              :type="scope.row.completed ? 'warning' : 'success'"
              @click="toggleTaskStatus(scope.row)"
            >
              {{ scope.row.completed ? '设为进行中' : '设为完成' }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <!-- 创建/编辑任务对话框 -->
    <el-dialog 
      :title="editingTask ? '编辑任务' : '创建任务'" 
      v-model="showCreateDialog"
      width="500px"
    >
      <el-form 
        :model="taskForm" 
        :rules="taskRules" 
        ref="taskFormRef"
        label-width="80px"
      >
        <el-form-item label="任务标题" prop="title">
          <el-input v-model="taskForm.title" />
        </el-form-item>
        
        <el-form-item label="任务描述" prop="description">
          <el-input 
            v-model="taskForm.description" 
            type="textarea"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showCreateDialog = false">取消</el-button>
          <el-button 
            type="primary" 
            @click="saveTask"
          >
            确定
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { useTaskStore } from '../stores/tasks'

export default {
  name: 'TasksView',
  setup() {
    const taskStore = useTaskStore()
    const showCreateDialog = ref(false)
    const editingTask = ref(null)
    const taskFormRef = ref(null)
    
    const taskForm = reactive({
      title: '',
      description: ''
    })
    
    const taskRules = {
      title: [
        { required: true, message: '请输入任务标题', trigger: 'blur' }
      ]
    }
    
    const loadTasks = async () => {
      await taskStore.fetchTasks()
    }
    
    const saveTask = async () => {
      taskFormRef.value.validate(async (valid) => {
        if (valid) {
          try {
            if (editingTask.value) {
              await taskStore.updateTask(editingTask.value.id, {
                ...taskForm,
                completed: editingTask.value.completed
              })
            } else {
              await taskStore.addTask(taskForm)
            }
            showCreateDialog.value = false
            resetForm()
          } catch (error) {
            console.error('保存任务失败:', error)
          }
        }
      })
    }
    
    const editTask = (task) => {
      editingTask.value = task
      taskForm.title = task.title
      taskForm.description = task.description
      showCreateDialog.value = true
    }
    
    const deleteTask = async (id) => {
      try {
        await ElMessageBox.confirm('确定要删除这个任务吗？', '提示', {
          type: 'warning'
        })
        await taskStore.deleteTask(id)
      } catch (error) {
        console.error('删除任务失败:', error)
      }
    }
    
    const toggleTaskStatus = async (task) => {
      try {
        await taskStore.updateTask(task.id, {
          ...task,
          completed: !task.completed
        })
      } catch (error) {
        console.error('更新任务状态失败:', error)
      }
    }
    
    const resetForm = () => {
      taskFormRef.value.resetFields()
      editingTask.value = null
    }
    
    onMounted(() => {
      loadTasks()
    })
    
    return {
      tasks: taskStore.tasks,
      loading: taskStore.loading,
      showCreateDialog,
      editingTask,
      taskForm,
      taskRules,
      taskFormRef,
      saveTask,
      editTask,
      deleteTask,
      toggleTaskStatus,
      resetForm
    }
  }
}
</script>

<style scoped>
.tasks-container {
  padding: 20px;
}

.card-header {
  font-weight: bold;
}

.dialog-footer {
  text-align: right;
}
</style>