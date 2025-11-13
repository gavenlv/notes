/**
 * 工具函数集合
 * 展示Vite中的模块系统和导入/导出功能
 */

/**
 * 格式化货币
 * @param {number} amount - 金额
 * @param {string} currency - 货币符号，默认为'¥'
 * @returns {string} 格式化后的货币字符串
 */
export function formatCurrency(amount, currency = '¥') {
  if (typeof amount !== 'number') {
    return `${currency}0.00`
  }
  return `${currency}${amount.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',')}`
}

/**
 * 生成唯一ID
 * @param {string} prefix - ID前缀
 * @returns {string} 唯一ID字符串
 */
export function generateId(prefix = 'id') {
  return `${prefix}-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
}

/**
 * 防抖函数
 * @param {Function} func - 要执行的函数
 * @param {number} delay - 延迟时间（毫秒）
 * @returns {Function} 防抖后的函数
 */
export function debounce(func, delay) {
  let timeoutId
  return function(...args) {
    clearTimeout(timeoutId)
    timeoutId = setTimeout(() => func.apply(this, args), delay)
  }
}

/**
 * 节流函数
 * @param {Function} func - 要执行的函数
 * @param {number} limit - 限制时间（毫秒）
 * @returns {Function} 节流后的函数
 */
export function throttle(func, limit) {
  let inThrottle
  return function(...args) {
    if (!inThrottle) {
      func.apply(this, args)
      inThrottle = true
      setTimeout(() => inThrottle = false, limit)
    }
  }
}

/**
 * 延迟函数
 * @param {number} ms - 延迟毫秒数
 * @returns {Promise} Promise对象
 */
export function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms))
}

/**
 * 深拷贝对象
 * @param {*} obj - 要拷贝的对象
 * @returns {*} 拷贝后的新对象
 */
export function deepClone(obj) {
  if (obj === null || typeof obj !== 'object') {
    return obj
  }
  
  if (obj instanceof Date) {
    return new Date(obj.getTime())
  }
  
  if (obj instanceof Array) {
    const clonedArr = []
    for (let i = 0; i < obj.length; i++) {
      clonedArr[i] = deepClone(obj[i])
    }
    return clonedArr
  }
  
  if (obj instanceof Object) {
    const clonedObj = {}
    for (const key in obj) {
      if (obj.hasOwnProperty(key)) {
        clonedObj[key] = deepClone(obj[key])
      }
    }
    return clonedObj
  }
}

/**
 * 检查是否为移动设备
 * @returns {boolean} 是否为移动设备
 */
export function isMobileDevice() {
  return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)
}

/**
 * 获取浏览器信息
 * @returns {Object} 浏览器信息对象
 */
export function getBrowserInfo() {
  const ua = navigator.userAgent
  let browserName = 'Unknown'
  let version = 'Unknown'
  let os = 'Unknown'

  // 检测浏览器
  if (ua.indexOf('Firefox') !== -1) {
    browserName = 'Firefox'
    version = ua.match(/Firefox\/(\d+\.\d+)/)[1]
  } else if (ua.indexOf('Chrome') !== -1 && ua.indexOf('Edge') === -1) {
    browserName = 'Chrome'
    version = ua.match(/Chrome\/(\d+\.\d+)/)[1]
  } else if (ua.indexOf('Safari') !== -1 && ua.indexOf('Chrome') === -1) {
    browserName = 'Safari'
    version = ua.match(/Version\/(\d+\.\d+)/)[1]
  } else if (ua.indexOf('Edge') !== -1) {
    browserName = 'Edge'
    version = ua.match(/Edge\/(\d+\.\d+)/)[1]
  }

  // 检测操作系统
  if (ua.indexOf('Windows') !== -1) {
    os = 'Windows'
  } else if (ua.indexOf('Macintosh') !== -1) {
    os = 'macOS'
  } else if (ua.indexOf('Linux') !== -1) {
    os = 'Linux'
  } else if (ua.indexOf('Android') !== -1) {
    os = 'Android'
  } else if (ua.indexOf('iPhone') !== -1 || ua.indexOf('iPad') !== -1) {
    os = 'iOS'
  }

  return {
    name: browserName,
    version,
    os,
    userAgent: ua
  }
}

/**
 * 计算两个日期之间的天数
 * @param {Date} date1 - 第一个日期
 * @param {Date} date2 - 第二个日期
 * @returns {number} 天数差
 */
export function getDaysBetween(date1, date2) {
  const oneDay = 24 * 60 * 60 * 1000
  const diffMs = Math.abs(date2 - date1)
  return Math.round(diffMs / oneDay)
}

/**
 * 检查值是否为空
 * @param {*} value - 要检查的值
 * @returns {boolean} 是否为空
 */
export function isEmpty(value) {
  if (value === null || value === undefined) return true
  if (typeof value === 'string') return value.trim() === ''
  if (Array.isArray(value)) return value.length === 0
  if (typeof value === 'object') return Object.keys(value).length === 0
  return false
}

/**
 * 安全地访问嵌套对象属性
 * @param {Object} obj - 对象
 * @param {string} path - 属性路径，如'a.b.c'
 * @param {*} defaultValue - 默认值
 * @returns {*} 属性值或默认值
 */
export function getNested(obj, path, defaultValue = undefined) {
  const keys = path.split('.')
  return keys.reduce((acc, key) => {
    return acc && acc[key] !== undefined ? acc[key] : defaultValue
  }, obj)
}

/**
 * 导出所有工具函数作为一个默认对象
 */
export default {
  formatCurrency,
  generateId,
  debounce,
  throttle,
  delay,
  deepClone,
  isMobileDevice,
  getBrowserInfo,
  getDaysBetween,
  isEmpty,
  getNested
}
