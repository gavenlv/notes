import React from 'react';

const CI_CDDemo = () => {
  // 简化版本：避免复杂的代码块语法
  return (
    <div className="demo-container">
      <div className="demo-header">
        <div className="demo-icon">CI</div>
        <div className="demo-info">
          <h3>CI/CD 持续集成与部署</h3>
          <p>自动化构建、测试和部署流程</p>
        </div>
      </div>

      <div className="info-box">
        <p>CI/CD 是现代前端工程化的核心环节，可以自动化完成代码集成、测试和部署，提高开发效率，减少人为错误。</p>
      </div>

      <h4>CI/CD 最佳实践</h4>
      <ul className="feature-list">
        <li>每次代码提交都自动运行测试和构建</li>
        <li>使用环境变量管理敏感信息（API密钥等）</li>
        <li>实现自动化部署到多个环境（开发、测试、生产）</li>
        <li>使用缓存提高构建速度</li>
        <li>部署前进行安全性检查和漏洞扫描</li>
        <li>使用语义化版本控制（Semantic Versioning）</li>
      </ul>

      <div className="success-box">
        <p>✅ CI/CD 可以自动化整个开发流程，从代码提交到应用部署的全过程</p>
      </div>
    </div>
  );
};

export default CI_CDDemo;