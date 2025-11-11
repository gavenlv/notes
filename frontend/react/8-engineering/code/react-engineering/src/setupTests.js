// 测试环境设置文件
import '@testing-library/jest-dom'

// 全局测试配置
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(),
    removeListener: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
})

// 模拟 IntersectionObserver（用于懒加载等功能的测试）
if (!window.IntersectionObserver) {
  window.IntersectionObserver = jest.fn(() => ({
    observe: jest.fn(),
    unobserve: jest.fn(),
    disconnect: jest.fn(),
  }))
}

// 模拟 Performance API
if (!window.performance) {
  window.performance = {
    now: jest.fn(() => Date.now()),
    getEntriesByType: jest.fn(() => []),
    mark: jest.fn(),
    measure: jest.fn(),
    getEntriesByName: jest.fn(() => []),
  }
}

// 模拟 requestAnimationFrame
jest.useFakeTimers()

// 清理函数
afterEach(() => {
  jest.clearAllMocks()
  jest.resetAllMocks()
})