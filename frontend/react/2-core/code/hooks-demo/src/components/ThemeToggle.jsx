import { useTheme } from '../context/ThemeContext.jsx'

/**
 * 主题切换组件
 * 提供一个按钮来切换应用的明/暗主题
 */
function ThemeToggle() {
  const { theme, toggleTheme, styles } = useTheme()

  return (
    <button
      className="theme-toggle-btn"
      onClick={toggleTheme}
      style={{
        position: 'fixed',
        bottom: '20px',
        right: '20px',
        padding: '12px 20px',
        borderRadius: '50px',
        border: `2px solid ${styles.borderColor}`,
        backgroundColor: styles.cardBackground,
        color: styles.color,
        fontSize: '14px',
        fontWeight: '600',
        cursor: 'pointer',
        boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
        transition: 'all 0.3s ease',
        zIndex: 1000
      }}
      onMouseEnter={(e) => {
        e.target.style.transform = 'scale(1.05)'
      }}
      onMouseLeave={(e) => {
        e.target.style.transform = 'scale(1)'
      }}
    >
      {theme === 'light' ? '🌙 切换暗色模式' : '☀️ 切换亮色模式'}
    </button>
  )
}

export default ThemeToggle
