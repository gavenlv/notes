// 导入样式文件
import './style.css'

// 导入环境变量和模块
import { getConfigInfo, logEnvironmentInfo } from './config.js'
import { fetchDataWithAxios, processDataWithLodash } from './api.js'

// 获取DOM元素
const app = document.getElementById('app')

// 初始化应用
function initApp() {
  if (!app) return
  
  // 创建应用容器
  const container = document.createElement('div')
  container.className = 'app-container'
  
  // 添加标题
  const title = document.createElement('h1')
  title.textContent = 'Vite 核心功能与配置示例'
  container.appendChild(title)
  
  // 创建环境信息展示区域
  createEnvironmentInfoSection(container)
  
  // 创建API调用演示区域
  createApiDemoSection(container)
  
  // 创建别名和路径解析演示
  createAliasDemoSection(container)
  
  // 添加代理配置说明
  createProxyInfoSection(container)
  
  // 添加到DOM
  app.appendChild(container)
}

// 创建环境信息展示区域
function createEnvironmentInfoSection(container) {
  const envSection = document.createElement('section')
  envSection.className = 'section env-section'
  
  const title = document.createElement('h2')
  title.textContent = '环境变量信息'
  envSection.appendChild(title)
  
  const configInfo = getConfigInfo()
  const infoList = document.createElement('ul')
  infoList.className = 'info-list'
  
  Object.entries(configInfo).forEach(([key, value]) => {
    const item = document.createElement('li')
    item.innerHTML = `
      <span class="info-key">${key}:</span> 
      <span class="info-value">${value}</span>
    `
    infoList.appendChild(item)
  })
  
  envSection.appendChild(infoList)
  container.appendChild(envSection)
  
  // 记录环境信息到控制台
  logEnvironmentInfo()
}

// 创建API调用演示区域
function createApiDemoSection(container) {
  const apiSection = document.createElement('section')
  apiSection.className = 'section api-section'
  
  const title = document.createElement('h2')
  title.textContent = 'API调用演示'
  apiSection.appendChild(title)
  
  const button = document.createElement('button')
  button.textContent = '调用模拟API'
  button.className = 'demo-button'
  apiSection.appendChild(button)
  
  const resultDiv = document.createElement('div')
  resultDiv.id = 'api-result'
  resultDiv.className = 'api-result'
  apiSection.appendChild(resultDiv)
  
  // 添加按钮点击事件
  button.addEventListener('click', async () => {
    resultDiv.textContent = '正在请求...'
    
    try {
      // 模拟API请求和数据处理
      const mockData = await fetchDataWithAxios()
      const processedData = processDataWithLodash(mockData)
      
      resultDiv.innerHTML = `
        <h4>处理后的结果:</h4>
        <pre>${JSON.stringify(processedData, null, 2)}</pre>
      `
    } catch (error) {
      resultDiv.textContent = `错误: ${error.message}`
      resultDiv.style.color = '#f5222d'
    }
  })
  
  container.appendChild(apiSection)
}

// 创建别名和路径解析演示
function createAliasDemoSection(container) {
  const aliasSection = document.createElement('section')
  aliasSection.className = 'section alias-section'
  
  const title = document.createElement('h2')
  title.textContent = '路径别名演示'
  aliasSection.appendChild(title)
  
  const description = document.createElement('p')
  description.textContent = '在vite.config.js中配置了以下别名:'
  aliasSection.appendChild(description)
  
  const aliasList = document.createElement('ul')
  aliasList.className = 'alias-list'
  
  const aliases = [
    { alias: '@', path: 'src/' },
    { alias: '@assets', path: 'src/assets/' },
    { alias: '@components', path: 'src/components/' }
  ]
  
  aliases.forEach(item => {
    const li = document.createElement('li')
    li.innerHTML = `
      <code>${item.alias}</code> 映射到 
      <code>${item.path}</code>
    `
    aliasList.appendChild(li)
  })
  
  aliasSection.appendChild(aliasList)
  container.appendChild(aliasSection)
}

// 创建代理配置说明
function createProxyInfoSection(container) {
  const proxySection = document.createElement('section')
  proxySection.className = 'section proxy-section'
  
  const title = document.createElement('h2')
  title.textContent = '代理配置说明'
  proxySection.appendChild(title)
  
  const description = document.createElement('p')
  description.innerHTML = 
    'Vite配置了API代理，将请求从 <code>/api</code> 转发到配置的API服务器。<br>' +
    '还配置了WebSocket代理，支持实时通信功能。'
  proxySection.appendChild(description)
  
  container.appendChild(proxySection)
}

// 启动应用
initApp()

// 展示HMR功能
if (import.meta.hot) {
  import.meta.hot.accept()
  
  import.meta.hot.on('vite:beforeUpdate', () => {
    console.log('页面即将更新...')
  })
  
  import.meta.hot.on('vite:afterUpdate', () => {
    console.log('页面已更新')
  })
}
