# Day 15: E2E Testing & CI/CD

## User Story 1: Set Up E2E Testing Framework

**Title**: As a quality engineer, I want to set up a comprehensive E2E testing framework for Superset.

**Description**: 
End-to-end testing validates that Superset functions correctly from a user's perspective.

**Acceptance Criteria**:
- [ ] E2E testing framework is configured
- [ ] Test environment is set up
- [ ] Basic test scenarios are implemented
- [ ] Tests run successfully

**Step-by-Step Guide**:

1. **Install Testing Dependencies**
   ```bash
   npm install --save-dev cypress
   ```

2. **Configure Cypress**
   ```javascript
   // cypress.config.js
   const { defineConfig } = require('cypress');
   
   module.exports = defineConfig({
     e2e: {
       baseUrl: 'http://localhost:8088',
     },
   });
   ```

3. **Create Custom Commands**
   ```javascript
   // cypress/support/commands.js
   Cypress.Commands.add('login', (username, password) => {
     cy.visit('/login');
     cy.get('[data-test="username"]').type(username);
     cy.get('[data-test="password"]').type(password);
     cy.get('[data-test="login-button"]').click();
   });
   ```

**Reference Documents**:
- [Cypress Documentation](https://docs.cypress.io/)
- [E2E Testing Best Practices](https://superset.apache.org/docs/developing-e2e-tests)

---

## User Story 2: Create Dashboard Testing

**Title**: As a dashboard developer, I want to create E2E tests for dashboard functionality.

**Description**: 
Dashboard testing covers the complete workflow from creating dashboards to viewing them.

**Acceptance Criteria**:
- [ ] Dashboard creation tests pass
- [ ] Chart interaction tests work
- [ ] Filter functionality is tested

**Step-by-Step Guide**:

1. **Create Dashboard Creation Test**
   ```javascript
   // cypress/e2e/dashboard-creation.cy.js
   describe('Dashboard Creation', () => {
     it('should create a new dashboard', () => {
       cy.visit('/dashboard/new');
       
       cy.get('[data-test="dashboard-title"]').type('Test Dashboard');
       cy.get('[data-test="save-dashboard"]').click();
       
       cy.url().should('include', '/dashboard');
     });
   });
   ```

2. **Create Chart Interaction Test**
   ```javascript
   // cypress/e2e/chart-interaction.cy.js
   describe('Chart Interactions', () => {
     it('should add chart to dashboard', () => {
       cy.visit('/chart/add');
       
       cy.get('[data-test="dataset-selector"]').click();
       cy.get('[data-test="chart-type-selector"]').click();
       cy.get('[data-test="save-chart"]').click();
     });
   });
   ```

**Reference Documents**:
- [Dashboard Testing Guide](https://superset.apache.org/docs/developing-e2e-tests#dashboard-tests)

---

## User Story 3: Set Up CI/CD Pipeline

**Title**: As a DevOps engineer, I want to set up a CI/CD pipeline for Superset testing.

**Description**: 
Continuous Integration ensures that all tests run automatically on every code change.

**Acceptance Criteria**:
- [ ] CI/CD pipeline is configured
- [ ] Tests run on every commit
- [ ] Test results are reported

**Step-by-Step Guide**:

1. **Create GitHub Actions Workflow**
   ```yaml
   # .github/workflows/e2e-tests.yml
   name: E2E Tests
   
   on:
     push:
       branches: [ main ]
     pull_request:
       branches: [ main ]
   
   jobs:
     test:
       runs-on: ubuntu-latest
       
       steps:
         - uses: actions/checkout@v3
         
         - name: Set up Node.js
           uses: actions/setup-node@v3
           with:
             node-version: '16'
         
         - name: Install dependencies
           run: npm install
         
         - name: Start Superset
           run: |
             export FLASK_APP=superset
             superset db upgrade
             superset fab create-admin --username admin --password admin
             superset init
             superset run -p 8088 &
         
         - name: Run E2E tests
           run: npx cypress run
   ```

2. **Create Test Scripts**
   ```json
   // package.json
   {
     "scripts": {
       "test:e2e": "cypress run",
       "test:e2e:open": "cypress open"
     }
   }
   ```

**Reference Documents**:
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

---

## E2E Testing Best Practices

### 1. Test Organization
- Group related tests in describe blocks
- Use descriptive test names
- Keep tests independent
- Use data-test attributes for selectors

### 2. Test Data Management
- Use fixtures for test data
- Clean up test data after tests
- Use unique identifiers
- Avoid hardcoded values

### 3. Test Reliability
- Add proper waits and timeouts
- Handle async operations correctly
- Use retry mechanisms for flaky tests
- Mock external dependencies

### 4. Test Reporting
- Generate detailed test reports
- Include screenshots on failure
- Track test execution time
- Monitor test trends

## Next Steps

After completing E2E testing setup, proceed to:
- [Advanced Testing Strategies](../advanced-testing/advanced-testing.md)
- [Performance Optimization](../performance-optimization/performance-optimization.md)