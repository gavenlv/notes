import React, { useState } from 'react'
import './App.css'

// 1. 容器组件与展示组件模式 (Container-Presenter Pattern)
// 展示组件 - 只负责渲染UI
const UserProfileView = ({ user, onFollow }) => {
  const initials = user.name.split(' ').map(n => n[0]).join('')
  
  return (
    <div className="user-profile">
      <div className="user-avatar">{initials}</div>
      <div className="user-info">
        <h3>{user.name}</h3>
        <p>{user.email}</p>
        <button onClick={onFollow}>
          {user.isFollowing ? 'Unfollow' : 'Follow'}
        </button>
      </div>
    </div>
  )
}

// 容器组件 - 负责状态管理和数据获取
const UserProfileContainer = () => {
  const [user, setUser] = useState({
    id: 1,
    name: 'John Doe',
    email: 'john@example.com',
    isFollowing: false
  })

  const handleFollow = () => {
    setUser(prev => ({
      ...prev,
      isFollowing: !prev.isFollowing
    }))
  }

  return (
    <UserProfileView user={user} onFollow={handleFollow} />
  )
}

// 2. 高阶组件模式 (HOC Pattern)
const withTooltip = (WrappedComponent) => {
  return ({ tooltip, ...props }) => {
    const [isVisible, setIsVisible] = useState(false)
    
    return (
      <div 
        className="with-tooltip"
        onMouseEnter={() => setIsVisible(true)}
        onMouseLeave={() => setIsVisible(false)}
      >
        <WrappedComponent {...props} />
        {isVisible && <div className="tooltip">{tooltip}</div>}
      </div>
    )
  }
}

const InfoText = ({ text }) => <span>{text}</span>
const InfoTextWithTooltip = withTooltip(InfoText)

// 3. 渲染属性模式 (Render Props Pattern)
class MouseTracker extends React.Component {
  state = {
    x: 0,
    y: 0
  }

  handleMouseMove = (event) => {
    this.setState({
      x: event.clientX,
      y: event.clientY
    })
  }

  render() {
    return (
      <div 
        className="mouse-tracker"
        onMouseMove={this.handleMouseMove}
      >
        {this.props.render(this.state)}
      </div>
    )
  }
}

// 4. 复合组件模式 (Compound Components)
class Tabs extends React.Component {
  state = {
    activeTab: 0
  }

  render() {
    const { children } = this.props
    const { activeTab } = this.state
    
    // 将子组件分为标题和内容
    const titles = React.Children.map(children, (child, index) => (
      <button 
        key={index}
        className={`tab-button ${activeTab === index ? 'active' : ''}`}
        onClick={() => this.setState({ activeTab: index })}
      >
        {child.props.title}
      </button>
    ))

    return (
      <div className="tabs">
        <div className="tabs-header">{titles}</div>
        <div className="tabs-content">
          {React.Children.toArray(children)[activeTab]}
        </div>
      </div>
    )
  }
}

const Tab = ({ children }) => <>{children}</>

// 5. 控制组件模式 (Controlled Components)
const ControlledInput = ({ value, onChange, label }) => (
  <div style={{ margin: '1rem 0' }}>
    <label>{label}: </label>
    <input 
      type="text" 
      value={value} 
      onChange={(e) => onChange(e.target.value)} 
      style={{
        padding: '0.5rem',
        borderRadius: '4px',
        border: '1px solid #ccc'
      }}
    />
  </div>
)

// 主应用组件
function App() {
  const [inputValue, setInputValue] = useState('')

  return (
    <div className="App">
      <h1>React Component Patterns</h1>
      
      {/* 1. 容器组件与展示组件模式 */}
      <section className="pattern-section">
        <h2 className="pattern-title">1. Container-Presenter Pattern</h2>
        <UserProfileContainer />
      </section>

      {/* 2. 高阶组件模式 */}
      <section className="pattern-section">
        <h2 className="pattern-title">2. Higher Order Component (HOC) Pattern</h2>
        <p>
          Hover over this text to see a 
          <InfoTextWithTooltip 
            text="tooltip" 
            tooltip="This is a tooltip implemented with HOC pattern!"
          />
        </p>
      </section>

      {/* 3. 渲染属性模式 */}
      <section className="pattern-section">
        <h2 className="pattern-title">3. Render Props Pattern</h2>
        <p>Move your mouse over the box below:</p>
        <MouseTracker 
          render={({ x, y }) => (
            <>
              <div className="tracker-dot" style={{ left: x, top: y }} />
              <div style={{ textAlign: 'center', padding: '1rem' }}>
                Mouse position: ({x}, {y})
              </div>
            </>
          )}
        />
      </section>

      {/* 4. 复合组件模式 */}
      <section className="pattern-section">
        <h2 className="pattern-title">4. Compound Components Pattern</h2>
        <Tabs>
          <Tab title="Tab 1">
            <h3>Tab 1 Content</h3>
            <p>This is the content for the first tab.</p>
          </Tab>
          <Tab title="Tab 2">
            <h3>Tab 2 Content</h3>
            <p>This is the content for the second tab.</p>
          </Tab>
          <Tab title="Tab 3">
            <h3>Tab 3 Content</h3>
            <p>This is the content for the third tab.</p>
          </Tab>
        </Tabs>
      </section>

      {/* 5. 控制组件模式 */}
      <section className="pattern-section">
        <h2 className="pattern-title">5. Controlled Components Pattern</h2>
        <ControlledInput 
          label="Enter text" 
          value={inputValue} 
          onChange={setInputValue} 
        />
        <p>You typed: {inputValue}</p>
      </section>
    </div>
  )
}

export default App