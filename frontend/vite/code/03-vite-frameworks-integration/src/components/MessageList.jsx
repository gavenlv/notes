import React from 'react'
import { formatTime } from '../utils/formatTime.js'

/**
 * 消息列表组件
 * 演示React的列表渲染和数据处理
 */
export const MessageList = ({ messages }) => {
  // 按时间戳降序排序消息
  const sortedMessages = [...messages].sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))

  // 空消息列表状态
  if (!sortedMessages || sortedMessages.length === 0) {
    return (
      <div className="message-list empty">
        <p className="empty-message">暂无消息，添加一条新消息吧！</p>
      </div>
    )
  }

  return (
    <div className="message-list">
      <div className="message-list-header">
        <h3>消息列表 ({sortedMessages.length})</h3>
      </div>
      
      <div className="messages-container">
        {sortedMessages.map((message) => (
          <div 
            key={message.id} 
            className="message-item"
            // 添加动画效果的类名
            data-testid={`message-${message.id}`}
          >
            <div className="message-header">
              <span className="message-time">
                {formatTime(message.time)}
              </span>
              <span className="message-id">#${message.id.toString().slice(-4)}</span>
            </div>
            <div className="message-content">
              {message.text}
            </div>
          </div>
        ))}
      </div>
      <div className="message-list-footer">
        <p className="message-stats">
          总消息数: {sortedMessages.length}
        </p>
        {sortedMessages.length > 1 && (
          <p className="message-tip">
            消息按时间倒序排列
          </p>
        )}
      </div>
    </div>
  )
}

// 为MessageList组件添加CSS样式
const style = document.createElement('style')
style.textContent = `
.message-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  max-height: 400px;
  background-color: var(--background-primary);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-color);
  overflow: hidden;
}

.message-list.empty {
  justify-content: center;
  align-items: center;
  min-height: 200px;
  background-color: var(--background-secondary);
}

.empty-message {
  color: var(--text-secondary);
  font-style: italic;
}

.message-list-header {
  padding: 1rem;
  background-color: var(--background-secondary);
  border-bottom: 1px solid var(--border-color);
}

.message-list-header h3 {
  margin: 0;
  font-size: 1.1rem;
  color: var(--text-primary);
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 0.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  max-height: 300px;
}

.message-item {
  background-color: var(--background-secondary);
  border-radius: var(--radius-sm);
  padding: 0.75rem;
  border-left: 3px solid var(--primary-color);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  animation: fadeIn 0.3s ease-in;
}

.message-item:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.message-time {
  font-size: 0.8rem;
  color: var(--text-secondary);
  font-family: monospace;
}

.message-id {
  font-size: 0.75rem;
  color: var(--text-secondary);
  background-color: var(--background-primary);
  padding: 0.125rem 0.375rem;
  border-radius: 999px;
}

.message-content {
  color: var(--text-primary);
  line-height: 1.5;
  word-wrap: break-word;
  white-space: pre-wrap;
}

.message-list-footer {
  padding: 0.75rem 1rem;
  background-color: var(--background-secondary);
  border-top: 1px solid var(--border-color);
  font-size: 0.85rem;
}

.message-stats {
  margin: 0;
  color: var(--text-secondary);
}

.message-tip {
  margin: 0.25rem 0 0;
  color: var(--text-secondary);
  font-style: italic;
  font-size: 0.8rem;
}

/* 滚动条样式 */
.messages-container::-webkit-scrollbar {
  width: 6px;
}

.messages-container::-webkit-scrollbar-track {
  background: var(--background-primary);
  border-radius: 3px;
}

.messages-container::-webkit-scrollbar-thumb {
  background: var(--border-color);
  border-radius: 3px;
}

.messages-container::-webkit-scrollbar-thumb:hover {
  background: var(--text-secondary);
}

/* 消息淡入动画 */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 响应式调整 */
@media (max-width: 480px) {
  .message-list {
    max-height: 300px;
  }
  
  .messages-container {
    max-height: 200px;
  }
  
  .message-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
  }
}
`
document.head.appendChild(style)
