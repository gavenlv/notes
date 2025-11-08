// pages/home-page.js
const { BasePage } = require('./base-page');

class HomePage extends BasePage {
  constructor(page) {
    super(page);
    this.searchInput = page.locator('#search-input');
    this.searchButton = page.locator('#search-button');
    this.userMenu = page.locator('#user-menu');
  }

  async search(keyword) {
    await this.searchInput.fill(keyword);
    await this.searchButton.click();
  }

  async openUserMenu() {
    await this.userMenu.click();
  }
}

module.exports = { HomePage };