import mitt from 'mitt'

// 创建事件总线实例
const bus = mitt()

// 导出事件总线
export default bus

// 可以在这里定义常用的事件名称常量
export const EVENTS = {
  USER_LOGIN: 'user:login',
  USER_LOGOUT: 'user:logout',
  NOTIFICATION: 'notification:show',
  DATA_UPDATE: 'data:update'
}