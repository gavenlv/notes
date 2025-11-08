# CodeGen最佳实践指南

本指南包含了使用Playwright CodeGen时的最佳实践和推荐模式。

## 1. 选择器最佳实践

### ✅ 推荐做法
- 使用 `data-testid` 属性作为首选选择器
- 使用 `data-cy` 属性（Cypress风格）
- 使用稳定的属性，避免使用CSS类名

### ❌ 避免做法
- 使用复杂的XPath表达式
- 依赖CSS类名和样式
- 使用位置索引选择器

生成的测试文件: best-practice-tests\best-practice-data-selectors.spec.js

## 2. 页面对象模式

### ✅ 推荐做法
- 将页面元素和操作封装在页面对象类中
- 使用描述性的方法名称
- 保持页面对象的单一职责

生成的测试文件: best-practice-tests\best-practice-page-object.spec.js
页面对象文件: best-practice-tests\pages\LoginPage.js

## 3. 等待策略

### ✅ 推荐做法
- 依赖Playwright的自动等待机制
- 使用明确的等待条件
- 设置合理的超时时间

### ❌ 避免做法
- 使用固定的延时等待
- 过度等待元素出现

生成的测试文件: best-practice-tests\best-practice-wait-strategies.spec.js

## 4. 断言最佳实践

### ✅ 推荐做法
- 使用具体的断言方法
- 验证具体的属性值
- 使用适当的文本匹配策略

### ❌ 避免做法
- 使用过于通用的断言
- 只验证元素存在而不验证内容

生成的测试文件: best-practice-tests\best-practice-assertions.spec.js

## 5. 动态内容处理

### ✅ 推荐做法
- 使用正则表达式匹配动态文本
- 在截图时屏蔽动态内容
- 使用参数化测试处理多组数据

### ❌ 避免做法
- 硬编码动态生成的值
- 依赖具体的时间戳值

生成的测试文件: best-practice-tests\best-practice-dynamic-content.spec.js

## 6. 通用建议

### 代码组织
- 将测试按功能模块分组
- 使用描述性的测试名称
- 添加适当的注释说明

### 性能优化
- 并行执行测试
- 复用浏览器上下文
- 优化选择器策略

### 可维护性
- 定期重构测试代码
- 删除过时的测试
- 保持测试的简洁性

## 7. 验证标准

本最佳实践遵循以下标准：
{
  "naming": {
    "testFilePattern": "^(feature|component|page)-[a-z-]+\\.spec\\.js$",
    "testNamePattern": "^should (test|verify|check|ensure) [a-z ]+$",
    "selectorPattern": "^[a-z-]+$"
  },
  "structure": {
    "requireDescribe": true,
    "maxTestsPerFile": 10,
    "requireBeforeEach": true,
    "requireAfterEach": true
  },
  "selectors": {
    "preferDataTestId": true,
    "avoidXPath": true,
    "useAccessibleSelectors": true,
    "avoidBrittleSelectors": true
  },
  "assertions": {
    "requireExplicitAssertions": true,
    "avoidGenericAssertions": true,
    "useAppropriateTimeouts": true
  },
  "performance": {
    "maxTestDuration": 30000,
    "requireParallelExecution": true,
    "optimizeSelectorStrategy": true
  },
  "maintainability": {
    "requireComments": true,
    "usePageObjects": true,
    "avoidCodeDuplication": true,
    "useConsistentFormatting": true
  }
}

## 8. 持续改进

定期审查和更新最佳实践，确保它们符合项目需求和技术发展。