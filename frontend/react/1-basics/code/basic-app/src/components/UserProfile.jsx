import React from 'react'

/**
 * 用户资料组件 - 展示如何接收和显示多个props
 * 
 * @param {Object} props - 组件属性
 * @param {string} props.name - 用户名
 * @param {number} props.age - 用户年龄
 * @param {string} props.email - 用户邮箱
 */
function UserProfile(props) {
  // 从props中解构出需要的属性
  const { name, age, email } = props

  // 格式化邮箱为可点击的链接
  const formattedEmail = (
    <a href={`mailto:${email}`} className="email-link">
      {email}
    </a>
  )

  return (
    <div className="user-profile">
      <div className="profile-header">
        <div className="profile-avatar">
          {/* 简单的用户名首字母头像 */}
          {name.charAt(0).toUpperCase()}
        </div>
        <h3 className="profile-name">{name}</h3>
      </div>
      <div className="profile-details">
        <div className="detail-item">
          <span className="detail-label">年龄：</span>
          <span className="detail-value">{age}岁</span>
        </div>
        <div className="detail-item">
          <span className="detail-label">邮箱：</span>
          <span className="detail-value">{formattedEmail}</span>
        </div>
      </div>
    </div>
  )
}

export default UserProfile
