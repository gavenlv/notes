import { useAppContext } from '../context/AppContext';

function Navbar() {
  const { user, isDarkMode, toggleTheme, logout } = useAppContext();
  
  return (
    <nav className={isDarkMode ? 'dark' : 'light'}>
      <div className="navbar-left">
        <span style={{ fontSize: '1.2rem', fontWeight: 'bold' }}>Context Demo</span>
      </div>
      <div className="navbar-center">
        <span style={{ marginRight: '20px' }}>
          {user.isLoggedIn ? `欢迎, ${user.name}` : '请登录'}
        </span>
        <span style={{ opacity: 0.7 }}>
          主题: {isDarkMode ? '暗色' : '亮色'}
        </span>
      </div>
      <div className="navbar-right">
        <button onClick={toggleTheme} style={{ marginRight: '10px' }}>
          {isDarkMode ? '切换到亮色' : '切换到暗色'}
        </button>
        {user.isLoggedIn && (
          <button onClick={logout}>登出</button>
        )}
      </div>
    </nav>
  );
}

export default Navbar