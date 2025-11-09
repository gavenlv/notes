import { useState, useEffect } from 'react'

/**
 * 自定义Hook - 用于处理数据获取
 * 
 * @param {string} url - 请求的URL地址
 * @param {Object} options - fetch选项（可选）
 * @returns {Object} 包含数据、加载状态、错误和刷新函数的对象
 */
function useFetch(url, options = {}) {
  // 状态管理
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  // 数据获取函数
  const fetchData = async () => {
    // 重置状态
    setLoading(true)
    setError(null)
    
    try {
      // 添加isMounted标志，防止组件卸载后更新状态
      let isMounted = true
      
      // 发送请求
      const response = await fetch(url, options)
      
      // 检查响应状态
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      // 解析JSON数据
      const result = await response.json()
      
      // 确保组件仍然挂载后再更新状态
      if (isMounted) {
        setData(result)
      }
      
      // 组件卸载时设置isMounted为false
      return () => {
        isMounted = false
      }
    } catch (err) {
      // 错误处理
      setError(err.message)
    } finally {
      // 无论成功失败，都设置loading为false
      setLoading(false)
    }
  }

  // 刷新数据的函数（可由组件调用）
  const refresh = () => {
    fetchData()
  }

  // 使用useEffect执行副作用
  useEffect(() => {
    // 当url存在时才执行获取
    if (url) {
      const cleanup = fetchData()
      
      // 清理函数
      return cleanup
    } else {
      setLoading(false)
    }
  }, [url, JSON.stringify(options)]) // 依赖于url和options

  // 返回数据和状态
  return { data, loading, error, refresh }
}

export default useFetch
