import { useState } from 'react'
import { useTheme } from '../context/ThemeContext.jsx'
import useFetch from '../hooks/useFetch.js'

function DataFetchingDemo() {
  const { styles } = useTheme()
  const [endpoint, setEndpoint] = useState('users') // 'users', 'posts', 'comments'
  
  // 模拟API URL
  const API_URL = `https://jsonplaceholder.typicode.com/${endpoint}`
  
  // 使用自定义的useFetch Hook
  const { data, loading, error, refresh } = useFetch(API_URL)

  // 格式化显示数据的函数
  const formatDataDisplay = () => {
    if (!data) return null
    
    // 根据不同的endpoint返回不同的显示内容
    switch (endpoint) {
      case 'users':
        return data.slice(0, 5).map(user => (
          <div key={user.id} className="data-card" style={{ borderColor: styles.borderColor }}>
            <h4 style={{ color: styles.primaryColor }}>{user.name}</h4>
            <p>Email: {user.email}</p>
            <p>Website: {user.website}</p>
            <p>Company: {user.company.name}</p>
          </div>
        ))
      case 'posts':
        return data.slice(0, 5).map(post => (
          <div key={post.id} className="data-card" style={{ borderColor: styles.borderColor }}>
            <h4 style={{ color: styles.primaryColor }}>{post.title}</h4>
            <p>{post.body}</p>
            <p>User ID: {post.userId}</p>
          </div>
        ))
      case 'comments':
        return data.slice(0, 5).map(comment => (
          <div key={comment.id} className="data-card" style={{ borderColor: styles.borderColor }}>
            <h4 style={{ color: styles.primaryColor }}>{comment.name}</h4>
            <p>Email: {comment.email}</p>
            <p>{comment.body}</p>
            <p>Post ID: {comment.postId}</p>
          </div>
        ))
      default:
        return <p>Unknown data format</p>
    }
  }

  // 获取endpoint的描述
  const getEndpointDescription = () => {
    switch (endpoint) {
      case 'users':
        return '用户信息（包含姓名、邮箱、网站等）'
      case 'posts':
        return '文章信息（包含标题、内容等）'
      case 'comments':
        return '评论信息（包含评论者、内容等）'
      default:
        return '未知数据'
    }
  }

  return (
    <div className="data-fetching-demo">
      <h2 style={{ color: styles.primaryColor }}>useFetch Hook 数据获取演示</h2>
      <p className="demo-description">
        这个演示展示了如何使用自定义的useFetch Hook来获取API数据，包括处理加载状态、错误状态和数据展示。
      </p>

      {/* 数据源选择器 */}
      <div className="endpoint-selector" style={{ backgroundColor: styles.backgroundColor, borderColor: styles.borderColor }}>
        <h3 style={{ color: styles.secondaryColor }}>选择数据源</h3>
        <div className="endpoint-buttons">
          <button 
            className={`endpoint-btn ${endpoint === 'users' ? 'active' : ''}`}
            onClick={() => setEndpoint('users')}
            style={{
              backgroundColor: endpoint === 'users' ? styles.primaryColor : 'transparent',
              color: endpoint === 'users' ? '#fff' : styles.color,
              borderColor: styles.borderColor
            }}
          >
            用户
          </button>
          <button 
            className={`endpoint-btn ${endpoint === 'posts' ? 'active' : ''}`}
            onClick={() => setEndpoint('posts')}
            style={{
              backgroundColor: endpoint === 'posts' ? styles.primaryColor : 'transparent',
              color: endpoint === 'posts' ? '#fff' : styles.color,
              borderColor: styles.borderColor
            }}
          >
            文章
          </button>
          <button 
            className={`endpoint-btn ${endpoint === 'comments' ? 'active' : ''}`}
            onClick={() => setEndpoint('comments')}
            style={{
              backgroundColor: endpoint === 'comments' ? styles.primaryColor : 'transparent',
              color: endpoint === 'comments' ? '#fff' : styles.color,
              borderColor: styles.borderColor
            }}
          >
            评论
          </button>
        </div>
        <p className="endpoint-info">当前获取: {getEndpointDescription()}</p>
        <p className="endpoint-url">API URL: {API_URL}</p>
      </div>

      {/* 数据操作控制 */}
      <div className="data-controls">
        <button 
          onClick={refresh}
          disabled={loading}
          className="refresh-btn"
          style={{
            backgroundColor: styles.secondaryColor,
            color: '#fff',
            borderColor: styles.secondaryColor,
            opacity: loading ? 0.6 : 1
          }}
        >
          {loading ? '加载中...' : '刷新数据'}
        </button>
      </div>

      {/* 加载状态 */}
      {loading && (
        <div className="loading-state" style={{ backgroundColor: styles.backgroundColor, borderColor: styles.borderColor }}>
          <div className="loading-spinner"></div>
          <p>正在加载数据，请稍候...</p>
        </div>
      )}

      {/* 错误状态 */}
      {error && (
        <div className="error-state" style={{ backgroundColor: styles.backgroundColor, borderColor: '#e53e3e' }}>
          <h3 style={{ color: '#e53e3e' }}>获取数据失败</h3>
          <p className="error-message">{error}</p>
          <button 
            onClick={refresh}
            className="retry-btn"
            style={{
              backgroundColor: '#e53e3e',
              color: '#fff',
              borderColor: '#e53e3e'
            }}
          >
            重试
          </button>
        </div>
      )}

      {/* 数据展示 */}
      {data && !loading && (
        <div className="data-display" style={{ borderColor: styles.borderColor }}>
          <h3 style={{ color: styles.secondaryColor }}>数据展示（显示前5条）</h3>
          <div className="data-grid">
            {formatDataDisplay()}
          </div>
          <p className="data-count">总共获取到 {data.length} 条数据</p>
        </div>
      )}

      {/* useFetch Hook 代码解释 */}
      <div className="code-explanation" style={{ backgroundColor: styles.backgroundColor, borderColor: styles.borderColor }}>
        <h3 style={{ color: styles.secondaryColor }}>自定义Hook useFetch 代码示例</h3>
        <pre><code>
{`// 自定义Hook - 用于数据获取
function useFetch(url, options = {}) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let isMounted = true;

    async function fetchData() {
      setLoading(true);
      try {
        const response = await fetch(url, options);
        if (!response.ok) throw new Error('Failed to fetch');
        const result = await response.json();
        if (isMounted) {
          setData(result);
        }
      } catch (err) {
        if (isMounted) {
          setError(err.message);
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    }

    fetchData();
    return () => { isMounted = false; };
  }, [url, JSON.stringify(options)]);

  return { data, loading, error, refresh: fetchData };
}

// 使用方式
const { data, loading, error, refresh } = useFetch('https://api.example.com/data');`}
        </code></pre>
      </div>
    </div>
  )
}

export default DataFetchingDemo
