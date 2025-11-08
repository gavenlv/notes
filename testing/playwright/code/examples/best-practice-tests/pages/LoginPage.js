// pages/LoginPage.js
class LoginPage {
  constructor(page) {
    this.page = page;
    
    // 选择器
    this.usernameInput = page.locator('[data-testid="username-input"]');
    this.passwordInput = page.locator('[data-testid="password-input"]');
    this.loginButton = page.locator('[data-testid="login-button"]');
    this.errorMessage = page.locator('[data-testid="error-message"]');
    this.successMessage = page.locator('[data-testid="success-message"]');
  }
  
  async goto() {
    await this.page.goto('https://example.com/login');
  }
  
  async login(username, password) {
    await this.usernameInput.fill(username);
    await this.passwordInput.fill(password);
    await this.loginButton.click();
  }
  
  async getErrorMessage() {
    await this.errorMessage.waitFor({ state: 'visible' });
    return this.errorMessage.textContent();
  }
  
  async isSuccessMessageVisible() {
    return this.successMessage.isVisible();
  }
}

module.exports = { LoginPage };