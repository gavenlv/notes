import React from 'react';

const LintingDemo = () => {
  // 正确的代码示例
  const goodCodeExample = () => {
    const message = 'Hello World';
    console.log(message);
    return message;
  };

  // 故意包含lint错误的示例（不会实际执行）
  // const badCodeExample = function() {
  //   var message = 'bad practice';
  //   console.log (message);
  //   return
  // }

  return (
    <div className="demo-container">
      <div className="demo-header">
        <div className="demo-icon">ES</div>
        <div className="demo-info">
          <h3>ESLint 代码规范</h3>
          <p>使用 ESLint 确保代码质量和一致性</p>
        </div>
      </div>

      <div className="info-box">
        <p>代码规范是工程化的基础，通过 ESLint 可以自动检测和修复代码中的问题，保持团队代码风格一致。</p>
      </div>

      <h4>ESLint 配置示例</h4>
      <div className="code-block">
        <pre>
{`// .eslintrc.json
{
  "env": {
    "browser": true,
    "es2021": true,
    "node": true,
    "jest": true
  },
  "extends": [
    "eslint:recommended",
    "plugin:react/recommended",
    "plugin:react-hooks/recommended"
  ],
  "parserOptions": {
    "ecmaFeatures": {
      "jsx": true
    },
    "ecmaVersion": "latest",
    "sourceType": "module"
  },
  "plugins": [
    "react",
    "react-refresh"
  ],
  "rules": {
    "react/react-in-jsx-scope": "off",
    "react-hooks/rules-of-hooks": "error",
    "react-hooks/exhaustive-deps": "warn",
    "no-console": "warn",
    "no-unused-vars": "warn",
    "semi": ["error", "always"],
    "quotes": ["error", "single"]
  }
}`}</pre>
      </div>

      <h4>常见的代码规范</h4>
      <ul className="feature-list">
        <li>使用单引号而非双引号</li>
        <li>使用 const 和 let 而非 var</li>
        <li>总是使用分号</li>
        <li>避免未使用的变量</li>
        <li>组件命名使用 PascalCase</li>
        <li>变量和函数命名使用 camelCase</li>
        <li>使用函数式组件和 Hooks</li>
      </ul>

      <div className="success-box">
        <p>✅ 使用 npm run lint 命令可以检查代码规范问题</p>
      </div>
    </div>
  );
};

export default LintingDemo;