// config/test-config.js
const testConfig = {
  environments: {
    dev: {
      baseUrl: 'http://localhost:3000',
      timeout: 30000
    },
    staging: {
      baseUrl: 'https://staging.example.com',
      timeout: 60000
    },
    production: {
      baseUrl: 'https://example.com',
      timeout: 60000
    }
  },
  browsers: ['chromium', 'firefox', 'webkit'],
  headless: true
};

module.exports = { testConfig };