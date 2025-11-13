import React from 'react'

/**
 * 主题切换组件
 * 演示React的状态管理和CSS变量切换
 */
export const ThemeToggle = ({ theme, onToggleTheme }) => {
  // 切换主题
  const handleToggle = () => {
    const newTheme = theme === 'light' ? 'dark' : 'light'
    onToggleTheme(newTheme)
    
    // 可选：添加主题切换的系统通知
    console.log(`主题已切换到: ${newTheme === 'light' ? '浅色模式' : '深色模式'}`)
  }

  // 获取主题图标
  const getThemeIcon = () => {
    if (theme === 'dark') {
      // 月亮图标 (深色模式)
      return '🌙'
    } else {
      // 太阳图标 (浅色模式)
      return '☀️'
    }
  }

  // 获取主题文本
  const getThemeText = () => {
    return theme === 'dark' ? '深色模式' : '浅色模式'
  }

  return (
    <button 
      className="theme-toggle-button"
      onClick={handleToggle}
      aria-label={`切换到${theme === 'dark' ? '浅色' : '深色'}模式`}
      title={`当前：${getThemeText()}，点击切换`}
    >
      <span className="theme-icon">
        {getThemeIcon()}
      </span>
      <span className="theme-text">
        {getThemeText()}
      </span>
    </button>
  )
}

// 为ThemeToggle组件添加CSS样式
const style = document.createElement('style')
style.textContent = `
.theme-toggle-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background-color: var(--background-secondary);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-full, 9999px);
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.theme-toggle-button:hover {
  background-color: var(--background-primary);
  border-color: var(--primary-color);
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}

.theme-toggle-button:active {
  transform: translateY(0);
}

.theme-icon {
  font-size: 1.2rem;
  display: inline-block;
  transition: transform 0.3s ease;
}

.theme-toggle-button:hover .theme-icon {
  transform: scale(1.1);
}

.theme-text {
  font-size: 0.9rem;
  font-weight: 500;
}

/* 深色模式下的特殊样式 */
[data-theme="dark"] .theme-toggle-button {
  background-color: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 255, 255, 0.1);
}

[data-theme="dark"] .theme-toggle-button:hover {
  background-color: rgba(255, 255, 255, 0.1);
  border-color: var(--primary-color);
}

/* 动画效果 */
@keyframes themeChange {
  0% {
    opacity: 0.8;
    transform: scale(0.95);
  }
  50% {
    opacity: 1;
    transform: scale(1.05);
  }
  100% {
    opacity: 1;
    transform: scale(1);
  }
}

.theme-toggle-button.theme-changing {
  animation: themeChange 0.3s ease;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .theme-toggle-button {
    padding: 0.4rem 0.8rem;
    font-size: 0.8rem;
  }
  
  .theme-icon {
    font-size: 1.1rem;
  }
  
  .theme-text {
    font-size: 0.8rem;
  }
}

@media (max-width: 480px) {
  .theme-toggle-button {
    gap: 0.4rem;
  }
  
  .theme-text {
    display: none;
  }
}
`
document.head.appendChild(style)
