import { useState, useEffect } from 'react'

/**
 * 自定义Hook - localStorage
 * 在localStorage中持久化存储状态
 * 
 * @param {string} key - localStorage的键名
 * @param {*} initialValue - 初始值
 * @returns {[*， Function]} 当前值和设置值的函数
 */
export function useLocalStorage(key, initialValue) {
  // 获取初始值
  const getInitialValue = () => {
    try {
      // 从localStorage中获取值
      const storedValue = localStorage.getItem(key)
      
      // 如果值存在，解析JSON
      if (storedValue !== null) {
        return JSON.parse(storedValue)
      }
      
      // 如果初始值是一个函数，调用它
      if (typeof initialValue === 'function') {
        return initialValue()
      }
      
      // 返回初始值
      return initialValue
    } catch (error) {
      // 如果出错，记录错误并返回初始值
      console.error(`Error reading localStorage key "${key}":`, error)
      
      // 如果初始值是一个函数，调用它
      if (typeof initialValue === 'function') {
        return initialValue()
      }
      
      return initialValue
    }
  }

  // 初始化状态
  const [storedValue, setStoredValue] = useState(getInitialValue)

  // 更新localStorage和状态
  const setValue = (value) => {
    try {
      // 允许值是一个函数
      const valueToStore =
        value instanceof Function ? value(storedValue) : value
      
      // 更新状态
      setStoredValue(valueToStore)
      
      // 更新localStorage
      localStorage.setItem(key, JSON.stringify(valueToStore))
      
      // 触发自定义事件，方便其他组件监听变化
      window.dispatchEvent(new Event('localStorageChange'))
    } catch (error) {
      // 记录错误
      console.error(`Error setting localStorage key "${key}":`, error)
    }
  }

  // 监听其他标签页的localStorage变化
  useEffect(() => {
    const handleStorageChange = (event) => {
      if (event.key === key && event.newValue !== null) {
        try {
          setStoredValue(JSON.parse(event.newValue))
        } catch (error) {
          console.error(`Error parsing localStorage value for key "${key}":`, error)
        }
      }
    }

    // 监听storage事件
    window.addEventListener('storage', handleStorageChange)
    
    // 监听自定义的localStorageChange事件
    const handleCustomChange = () => {
      try {
        const storedValue = localStorage.getItem(key)
        if (storedValue !== null) {
          setStoredValue(JSON.parse(storedValue))
        }
      } catch (error) {
        console.error(`Error reading localStorage key "${key}" in custom event handler:`, error)
      }
    }
    
    window.addEventListener('localStorageChange', handleCustomChange)
    
    // 清理函数
    return () => {
      window.removeEventListener('storage', handleStorageChange)
      window.removeEventListener('localStorageChange', handleCustomChange)
    }
  }, [key])

  // 返回状态和更新函数
  return [storedValue, setValue]
}

/**
 * 删除localStorage中的项
 * @param {string} key - 要删除的键名
 */
export function removeLocalStorage(key) {
  try {
    localStorage.removeItem(key)
    window.dispatchEvent(new Event('localStorageChange'))
  } catch (error) {
    console.error(`Error removing localStorage key "${key}":`, error)
  }
}

/**
 * 清空所有localStorage项
 */
export function clearLocalStorage() {
  try {
    localStorage.clear()
    window.dispatchEvent(new Event('localStorageChange'))
  } catch (error) {
    console.error('Error clearing localStorage:', error)
  }
}

/**
 * 获取localStorage中的所有键
 * @returns {string[]} 所有键的数组
 */
export function getLocalStorageKeys() {
  try {
    return Object.keys(localStorage)
  } catch (error) {
    console.error('Error getting localStorage keys:', error)
    return []
  }
}

/**
 * 检查localStorage是否可用
 * @returns {boolean} localStorage是否可用
 */
export function isLocalStorageAvailable() {
  try {
    const testKey = '__localStorage_test__'
    localStorage.setItem(testKey, testKey)
    localStorage.removeItem(testKey)
    return true
  } catch (error) {
    return false
  }
}

/**
 * 获取localStorage使用情况
 * @returns {Object} 包含使用情况信息的对象
 */
export function getLocalStorageInfo() {
  try {
    let totalSize = 0
    let itemCount = 0
    
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i)
      if (key) {
        const value = localStorage.getItem(key)
        // 近似计算大小（每个字符约2字节）
        totalSize += (key.length + value.length) * 2
        itemCount++
      }
    }
    
    return {
      itemCount,
      totalSize,
      totalSizeMB: (totalSize / 1024 / 1024).toFixed(4),
      isAvailable: true
    }
  } catch (error) {
    return {
      itemCount: 0,
      totalSize: 0,
      totalSizeMB: '0',
      isAvailable: false,
      error: error.message
    }
  }
}
