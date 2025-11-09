import React from 'react'

/**
 * 问候组件 - 展示props的使用和默认值
 * 
 * @param {Object} props - 组件属性
 * @param {string} props.name - 问候的名字，默认为'访客'
 */
function Greeting({ name = '访客' }) {
  // 使用JavaScript表达式生成问候语
  const greetingMessage = `你好，${name}！欢迎学习React。`

  return (
    <div className="greeting-container">
      <h3 className="greeting-text">{greetingMessage}</h3>
    </div>
  )
}

// 添加propTypes可以提供类型检查（需要react-prop-types包）
// Greeting.propTypes = {
//   name: PropTypes.string
// }

export default Greeting
