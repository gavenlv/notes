import { useState, useEffect } from 'react'
import { Routes, Route, Link, useNavigate } from 'react-router-dom'
import { useQuery, useMutation } from 'react-query'
import { Formik, Form, Field, ErrorMessage } from 'formik'
import * as Yup from 'yup'
import axios from 'axios'
import { toast } from 'react-toastify'
import _ from 'lodash'
import { format, parseISO } from 'date-fns'
import { zhCN } from 'date-fns/locale'
import './App.css'

// 模拟API函数
const fetchUsers = async () => {
  // 模拟API延迟
  await new Promise(resolve => setTimeout(resolve, 1000))
  return [
    { id: 1, name: '张三', email: 'zhangsan@example.com', createdAt: '2023-01-15T08:30:00Z' },
    { id: 2, name: '李四', email: 'lisi@example.com', createdAt: '2023-02-20T14:45:00Z' },
    { id: 3, name: '王五', email: 'wangwu@example.com', createdAt: '2023-03-10T09:15:00Z' }
  ]
}

const createUser = async (userData) => {
  await new Promise(resolve => setTimeout(resolve, 1000))
  return { ...userData, id: Date.now(), createdAt: new Date().toISOString() }
}

// 表单验证模式
const validationSchema = Yup.object({
  name: Yup.string()
    .min(2, '用户名至少需要2个字符')
    .max(50, '用户名最多50个字符')
    .required('用户名是必填项'),
  email: Yup.string()
    .email('请输入有效的邮箱地址')
    .required('邮箱是必填项'),
  password: Yup.string()
    .min(6, '密码至少需要6个字符')
    .required('密码是必填项'),
  confirmPassword: Yup.string()
    .oneOf([Yup.ref('password'), null], '两次输入的密码必须一致')
    .required('请确认密码')
})

// 1. React Router 示例
const RouterDemo = () => {
  const navigate = useNavigate()
  const [count, setCount] = useState(0)

  const handleNavigate = () => {
    navigate('/axios')
  }

  return (
    <div className="router-demo">
      <div className="library-info">
        <div className="library-icon">RR</div>
        <div>
          <div className="library-name">React Router</div>
          <div className="library-version">v6.14.2</div>
        </div>
      </div>
      
      <h3>路由功能演示</h3>
      <p>React Router 提供了声明式的路由解决方案，让单页应用的导航变得简单易用。</p>
      
      <div className="router-controls">
        <button onClick={handleNavigate}>跳转到 Axios 示例</button>
        <button onClick={() => setCount(count + 1)}>更新状态: {count}</button>
      </div>
      
      <div className="route-info">
        <p>当前路由: <code>/router</code></p>
        <p>点击顶部导航菜单体验不同的路由</p>
      </div>
    </div>
  )
}

// 2. Axios 示例
const AxiosDemo = () => {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const fetchData = async () => {
    setLoading(true)
    setError(null)
    try {
      // 使用模拟的API，实际项目中会替换为真实的API地址
      // const response = await axios.get('https://api.example.com/users')
      await new Promise(resolve => setTimeout(resolve, 1000))
      const mockData = {
        users: [
          { id: 1, name: '张三', age: 30 },
          { id: 2, name: '李四', age: 25 },
          { id: 3, name: '王五', age: 35 }
        ],
        total: 3
      }
      setData(mockData)
      toast.success('数据获取成功！')
    } catch (err) {
      setError('获取数据失败')
      toast.error('数据获取失败')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="axios-demo">
      <div className="library-info">
        <div className="library-icon">AX</div>
        <div>
          <div className="library-name">Axios</div>
          <div className="library-version">v1.4.0</div>
        </div>
      </div>
      
      <h3>HTTP 请求演示</h3>
      <p>Axios 是一个基于 Promise 的 HTTP 客户端，用于浏览器和 node.js。</p>
      
      <button onClick={fetchData} disabled={loading}>
        {loading ? '加载中...' : '获取数据'}
      </button>
      
      {error && <div className="error-message">{error}</div>}
      
      {data && (
        <div className="api-results">
          <h4>获取到的数据:</h4>
          <div className="user-list">
            {data.users.map(user => (
              <div key={user.id} className="user-item">
                <span>ID: {user.id}</span>
                <span>姓名: {user.name}</span>
                <span>年龄: {user.age}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

// 3. React Query 示例
const ReactQueryDemo = () => {
  // 使用 useQuery 获取数据
  const { data: users, isLoading, error, refetch } = useQuery(
    'users',
    fetchUsers,
    {
      staleTime: 30000 // 数据30秒内视为新鲜
    }
  )

  // 使用 useMutation 创建数据
  const createUserMutation = useMutation(createUser, {
    onSuccess: () => {
      toast.success('用户创建成功！')
      // 重新获取用户列表
      refetch()
    },
    onError: () => {
      toast.error('用户创建失败！')
    }
  })

  const handleCreateUser = () => {
    createUserMutation.mutate({
      name: `新用户${Date.now()}`,
      email: `user${Date.now()}@example.com`
    })
  }

  if (isLoading) return <div className="loading">加载中...</div>
  if (error) return <div className="error">获取数据失败</div>

  return (
    <div className="react-query-demo">
      <div className="library-info">
        <div className="library-icon">RQ</div>
        <div>
          <div className="library-name">React Query</div>
          <div className="library-version">v3.39.3</div>
        </div>
      </div>
      
      <h3>数据获取与缓存演示</h3>
      <p>React Query 提供了强大的数据获取、缓存和状态管理功能。</p>
      
      <div className="query-controls">
        <button onClick={refetch}>刷新数据</button>
        <button onClick={handleCreateUser} disabled={createUserMutation.isLoading}>
          {createUserMutation.isLoading ? '创建中...' : '创建用户'}
        </button>
      </div>
      
      <div className="query-results">
        <h4>用户列表:</h4>
        <div className="user-list">
          {users.map(user => (
            <div key={user.id} className="user-item">
              <span>姓名: {user.name}</span>
              <span>邮箱: {user.email}</span>
              <span>创建时间: {format(parseISO(user.createdAt), 'yyyy-MM-dd HH:mm:ss', { locale: zhCN })}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

// 4. Formik 表单示例
const FormikDemo = () => {
  const initialValues = {
    name: '',
    email: '',
    password: '',
    confirmPassword: ''
  }

  const handleSubmit = (values, { resetForm }) => {
    console.log('表单提交:', values)
    toast.success('表单提交成功！')
    resetForm()
  }

  return (
    <div className="formik-demo">
      <div className="library-info">
        <div className="library-icon">FK</div>
        <div>
          <div className="library-name">Formik + Yup</div>
          <div className="library-version">Formik v2.4.3 / Yup v1.2.0</div>
        </div>
      </div>
      
      <h3>表单处理与验证演示</h3>
      <p>Formik 简化了表单处理，配合 Yup 提供强大的表单验证功能。</p>
      
      <Formik
        initialValues={initialValues}
        validationSchema={validationSchema}
        onSubmit={handleSubmit}
      >
        {({ isSubmitting, values, touched, errors }) => (
          <Form className="formik-form">
            <div className="form-group">
              <label htmlFor="name">用户名</label>
              <Field
                type="text"
                id="name"
                name="name"
                className={touched.name && errors.name ? 'error' : ''}
              />
              <ErrorMessage name="name" component="div" className="error-message" />
            </div>
            
            <div className="form-group">
              <label htmlFor="email">邮箱</label>
              <Field
                type="email"
                id="email"
                name="email"
                className={touched.email && errors.email ? 'error' : ''}
              />
              <ErrorMessage name="email" component="div" className="error-message" />
            </div>
            
            <div className="form-group">
              <label htmlFor="password">密码</label>
              <Field
                type="password"
                id="password"
                name="password"
                className={touched.password && errors.password ? 'error' : ''}
              />
              <ErrorMessage name="password" component="div" className="error-message" />
            </div>
            
            <div className="form-group">
              <label htmlFor="confirmPassword">确认密码</label>
              <Field
                type="password"
                id="confirmPassword"
                name="confirmPassword"
                className={touched.confirmPassword && errors.confirmPassword ? 'error' : ''}
              />
              <ErrorMessage name="confirmPassword" component="div" className="error-message" />
            </div>
            
            <button type="submit" disabled={isSubmitting}>
              {isSubmitting ? '提交中...' : '提交'}
            </button>
          </Form>
        )}
      </Formik>
    </div>
  )
}

// 5. Lodash 工具函数示例
const LodashDemo = () => {
  const [data, setData] = useState([
    { id: 1, name: '张三', age: 30, active: true },
    { id: 2, name: '李四', age: 25, active: false },
    { id: 3, name: '王五', age: 35, active: true },
    { id: 4, name: '赵六', age: 28, active: true },
    { id: 5, name: '钱七', age: 40, active: false }
  ])

  // 使用 Lodash 函数
  const filteredUsers = _.filter(data, { active: true })
  const sortedUsers = _.sortBy(data, ['age'])
  const groupedUsers = _.groupBy(data, 'active')
  const userMap = _.keyBy(data, 'id')
  const debouncedFunction = _.debounce((value) => {
    console.log('防抖函数执行:', value)
    toast.info(`防抖执行: ${value}`)
  }, 1000)

  const handleInputChange = (e) => {
    debouncedFunction(e.target.value)
  }

  return (
    <div className="lodash-demo">
      <div className="library-info">
        <div className="library-icon">_</div>
        <div>
          <div className="library-name">Lodash</div>
          <div className="library-version">v4.17.21</div>
        </div>
      </div>
      
      <h3>实用工具函数演示</h3>
      <p>Lodash 提供了丰富的实用工具函数，简化日常开发工作。</p>
      
      <div className="lodash-examples">
        <div className="example">
          <h4>1. 防抖函数演示</h4>
          <input
            type="text"
            placeholder="输入内容测试防抖..."
            onChange={handleInputChange}
          />
        </div>
        
        <div className="example">
          <h4>2. 数据过滤 - 活跃用户</h4>
          <div className="user-list">
            {filteredUsers.map(user => (
              <div key={user.id} className="user-item">{user.name}</div>
            ))}
          </div>
        </div>
        
        <div className="example">
          <h4>3. 数据排序 - 按年龄</h4>
          <div className="user-list">
            {sortedUsers.map(user => (
              <div key={user.id} className="user-item">
                {user.name} ({user.age}岁)
              </div>
            ))}
          </div>
        </div>
        
        <div className="example">
          <h4>4. 数据分组 - 按活跃状态</h4>
          <div className="grouped-data">
            <div>
              <h5>活跃用户:</h5>
              {groupedUsers.true?.map(user => (
                <div key={user.id} className="user-item">{user.name}</div>
              ))}
            </div>
            <div>
              <h5>非活跃用户:</h5>
              {groupedUsers.false?.map(user => (
                <div key={user.id} className="user-item">{user.name}</div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

// 6. Date-fns 日期处理示例
const DateFnsDemo = () => {
  const [currentDate, setCurrentDate] = useState(new Date())
  const [targetDate, setTargetDate] = useState('2023-12-31')

  // 日期格式化
  const formattedDate = format(currentDate, 'yyyy年MM月dd日 EEEE HH:mm:ss', { locale: zhCN })
  const relativeTime = formatDistanceToNow(currentDate, { addSuffix: true, locale: zhCN })
  const isFuture = isAfter(parseISO(targetDate), new Date())

  return (
    <div className="date-fns-demo">
      <div className="library-info">
        <div className="library-icon">DF</div>
        <div>
          <div className="library-name">Date-fns</div>
          <div className="library-version">v2.30.0</div>
        </div>
      </div>
      
      <h3>日期时间处理演示</h3>
      <p>Date-fns 提供了现代化的日期时间处理函数库，支持国际化。</p>
      
      <div className="date-examples">
        <div className="date-info">
          <p>当前日期格式化:</p>
          <p className="formatted-date">{formattedDate}</p>
        </div>
        
        <div className="date-info">
          <p>相对时间:</p>
          <p className="relative-time">{relativeTime}</p>
        </div>
        
        <div className="date-input">
          <label htmlFor="targetDate">选择日期:</label>
          <input
            type="date"
            id="targetDate"
            value={targetDate}
            onChange={(e) => setTargetDate(e.target.value)}
          />
          <p>{isFuture ? '这是未来日期' : '这是过去日期'}</p>
        </div>
        
        <div className="date-operations">
          <button onClick={() => setCurrentDate(addDays(currentDate, 1))}>加1天</button>
          <button onClick={() => setCurrentDate(subDays(currentDate, 1))}>减1天</button>
          <button onClick={() => setCurrentDate(addMonths(currentDate, 1))}>加1个月</button>
          <button onClick={() => setCurrentDate(subMonths(currentDate, 1))}>减1个月</button>
        </div>
      </div>
    </div>
  )
}

// 7. Toastify 通知示例
const ToastifyDemo = () => {
  const showSuccessToast = () => {
    toast.success('操作成功！', {
      position: "top-right",
      autoClose: 3000,
      hideProgressBar: false,
      closeOnClick: true,
      pauseOnHover: true,
      draggable: true,
      progress: undefined,
    })
  }

  const showErrorToast = () => {
    toast.error('操作失败！', {
      position: "top-right",
      autoClose: 5000,
      hideProgressBar: false,
      closeOnClick: true,
      pauseOnHover: true,
      draggable: true,
      progress: undefined,
    })
  }

  const showInfoToast = () => {
    toast.info('这是一条信息通知', {
      position: "top-right",
      autoClose: 3000,
      hideProgressBar: false,
      closeOnClick: true,
      pauseOnHover: true,
      draggable: true,
      progress: undefined,
    })
  }

  const showWarningToast = () => {
    toast.warning('警告！请检查输入', {
      position: "top-right",
      autoClose: 4000,
      hideProgressBar: false,
      closeOnClick: true,
      pauseOnHover: true,
      draggable: true,
      progress: undefined,
    })
  }

  return (
    <div className="toastify-demo">
      <div className="library-info">
        <div className="library-icon">T</div>
        <div>
          <div className="library-name">React Toastify</div>
          <div className="library-version">v9.1.3</div>
        </div>
      </div>
      
      <h3>通知组件演示</h3>
      <p>React Toastify 提供了优雅的通知组件，支持多种通知类型和自定义选项。</p>
      
      <div className="toast-buttons">
        <button onClick={showSuccessToast} className="success">成功通知</button>
        <button onClick={showErrorToast} className="error">错误通知</button>
        <button onClick={showInfoToast} className="info">信息通知</button>
        <button onClick={showWarningToast} className="warning">警告通知</button>
      </div>
      
      <div className="toast-tips">
        <p>提示：点击右上角的按钮可以关闭通知</p>
        <p>提示：鼠标悬停在通知上可以暂停自动关闭</p>
      </div>
    </div>
  )
}

// 主应用组件
function App() {
  return (
    <div className="ecosystem-demo">
      <h1>React 生态系统示例</h1>
      
      {/* 导航菜单 */}
      <nav className="eco-nav">
        <Link to="/">概览</Link>
        <Link to="/router">React Router</Link>
        <Link to="/axios">Axios</Link>
        <Link to="/react-query">React Query</Link>
        <Link to="/formik">Formik + Yup</Link>
        <Link to="/lodash">Lodash</Link>
        <Link to="/date-fns">Date-fns</Link>
        <Link to="/toastify">React Toastify</Link>
      </nav>
      
      {/* 路由配置 */}
      <Routes>
        <Route path="/" element={
          <div className="overview">
            <h2>React 生态系统概览</h2>
            <p>React 生态系统包含丰富的库和工具，帮助开发者构建更好的应用程序。</p>
            
            <div className="ecosystem-grid">
              <div className="ecosystem-card">
                <h3>路由管理</h3>
                <p>React Router - 声明式的路由解决方案</p>
                <Link to="/router">查看示例</Link>
              </div>
              
              <div className="ecosystem-card">
                <h3>HTTP 客户端</h3>
                <p>Axios - 基于 Promise 的 HTTP 客户端</p>
                <Link to="/axios">查看示例</Link>
              </div>
              
              <div className="ecosystem-card">
                <h3>数据获取</h3>
                <p>React Query - 强大的数据获取和缓存库</p>
                <Link to="/react-query">查看示例</Link>
              </div>
              
              <div className="ecosystem-card">
                <h3>表单处理</h3>
                <p>Formik + Yup - 表单管理和验证</p>
                <Link to="/formik">查看示例</Link>
              </div>
              
              <div className="ecosystem-card">
                <h3>工具函数</h3>
                <p>Lodash - 实用工具函数库</p>
                <Link to="/lodash">查看示例</Link>
              </div>
              
              <div className="ecosystem-card">
                <h3>日期处理</h3>
                <p>Date-fns - 现代化日期时间库</p>
                <Link to="/date-fns">查看示例</Link>
              </div>
              
              <div className="ecosystem-card">
                <h3>UI 组件</h3>
                <p>React Toastify - 优雅的通知组件</p>
                <Link to="/toastify">查看示例</Link>
              </div>
            </div>
          </div>
        } />
        <Route path="/router" element={<RouterDemo />} />
        <Route path="/axios" element={<AxiosDemo />} />
        <Route path="/react-query" element={<ReactQueryDemo />} />
        <Route path="/formik" element={<FormikDemo />} />
        <Route path="/lodash" element={<LodashDemo />} />
        <Route path="/date-fns" element={<DateFnsDemo />} />
        <Route path="/toastify" element={<ToastifyDemo />} />
      </Routes>
    </div>
  )
}

// 导入 date-fns 的其他函数
import { addDays, subDays, addMonths, subMonths, isAfter, formatDistanceToNow } from 'date-fns'

export default App
