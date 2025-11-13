// 导入样式文件
import './style.css'

// 导入示例模块
import { add, multiply } from './utils.js'

// 获取DOM元素
const app = document.getElementById('app')

// 创建示例内容
function createAppContent() {
  const container = document.createElement('div')
  container.className = 'app-container'
  
  // 添加标题
  const title = document.createElement('h1')
  title.textContent = 'Vite 基础示例'
  container.appendChild(title)
  
  // 添加功能介绍
  const intro = document.createElement('p')
  intro.textContent = '这是一个简单的Vite项目示例，展示了Vite的基本功能。'
  container.appendChild(intro)
  
  // 创建计算演示
  const calcDemo = document.createElement('div')
  calcDemo.className = 'calc-demo'
  
  const calcTitle = document.createElement('h3')
  calcTitle.textContent = '模块导入示例：'
  calcDemo.appendChild(calcTitle)
  
  const result1 = document.createElement('p')
  result1.textContent = `2 + 3 = ${add(2, 3)}`
  calcDemo.appendChild(result1)
  
  const result2 = document.createElement('p')
  result2.textContent = `4 × 5 = ${multiply(4, 5)}`
  calcDemo.appendChild(result2)
  
  container.appendChild(calcDemo)
  
  // 添加热更新提示
  const hotReload = document.createElement('div')
  hotReload.className = 'hot-reload-info'
  hotReload.innerHTML = `
    <h3>热更新演示</h3>
    <p>尝试修改 <code>src/main.js</code> 或 <code>src/utils.js</code> 文件，看看变化是否立即生效！</p>
  `
  container.appendChild(hotReload)
  
  return container
}

// 渲染应用
if (app) {
  app.appendChild(createAppContent())
}

// 添加一些交互
if (app) {
  app.addEventListener('click', (e) => {
    if (e.target.tagName === 'H1') {
      e.target.style.color = getRandomColor()
    }
  })
}

// 辅助函数：生成随机颜色
function getRandomColor() {
  const letters = '0123456789ABCDEF'
  let color = '#'
  for (let i = 0; i < 6; i++) {
    color += letters[Math.floor(Math.random() * 16)]
  }
  return color
}
