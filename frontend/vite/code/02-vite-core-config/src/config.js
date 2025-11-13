/**
 * 获取配置信息
 * 从环境变量中提取关键配置
 */
export function getConfigInfo() {
  // 从import.meta.env获取环境变量
  const env = import.meta.env
  
  return {
    '环境模式': env.MODE,
    '基础路径': env.VITE_BASE_PATH,
    'API基础URL': env.VITE_API_BASE_URL,
    'WebSocket URL': env.VITE_WS_URL,
    '是否使用HTTPS': env.VITE_USE_HTTPS === 'true' ? '是' : '否',
    '是否生成源码映射': env.VITE_SOURCEMAP === 'true' ? '是' : '否',
    '应用标题': env.VITE_APP_TITLE,
    '环境标识': env.VITE_APP_ENV
  }
}

/**
 * 记录环境信息到控制台
 */
export function logEnvironmentInfo() {
  console.log('======== Vite 环境信息 ========')
  const configInfo = getConfigInfo()
  
  Object.entries(configInfo).forEach(([key, value]) => {
    console.log(`${key}: ${value}`)
  })
  
  console.log('==============================')
}

/**
 * 获取API配置
 * @returns {Object} API相关配置
 */
export function getApiConfig() {
  return {
    baseURL: import.meta.env.VITE_API_BASE_URL,
    timeout: 10000,
    headers: {
      'Content-Type': 'application/json',
      'X-Environment': import.meta.env.VITE_APP_ENV
    }
  }
}

/**
 * 判断是否为开发环境
 * @returns {boolean} 是否为开发环境
 */
export function isDevelopment() {
  return import.meta.env.DEV
}

/**
 * 判断是否为生产环境
 * @returns {boolean} 是否为生产环境
 */
export function isProduction() {
  return import.meta.env.PROD
}

/**
 * 获取构建时间戳
 * @returns {string} 构建时间戳
 */
export function getBuildTimestamp() {
  return import.meta.env.VITE_BUILD_TIMESTAMP || new Date().toISOString()
}

/**
 * 获取应用版本信息
 * @returns {Object} 应用版本信息
 */
export function getAppInfo() {
  return {
    name: import.meta.env.VITE_APP_NAME || 'Vite Core Demo',
    version: import.meta.env.VITE_APP_VERSION || '1.0.0',
    env: import.meta.env.VITE_APP_ENV,
    timestamp: getBuildTimestamp()
  }
}
