// config/environment-manager.js
class EnvironmentManager {
  constructor() {
    this.environments = {
      development: {
        url: 'http://localhost:3000',
        database: 'dev_db',
        apiBaseUrl: 'http://localhost:3000/api'
      },
      staging: {
        url: process.env.STAGING_URL || 'https://staging.example.com',
        database: 'staging_db',
        apiBaseUrl: process.env.STAGING_API_URL || 'https://staging.example.com/api'
      },
      production: {
        url: process.env.PROD_URL || 'https://example.com',
        database: 'prod_db',
        apiBaseUrl: process.env.PROD_API_URL || 'https://example.com/api'
      }
    };
  }

  getEnvironment() {
    const env = process.env.TEST_ENV || 'development';
    return this.environments[env] || this.environments.development;
  }

  isCI() {
    return !!process.env.CI;
  }

  getBrowserOptions() {
    // 在CI环境中使用无头模式
    if (this.isCI()) {
      return { headless: true };
    }
    
    // 在本地开发环境中使用有头模式
    return { headless: false };
  }
}

module.exports = { EnvironmentManager };