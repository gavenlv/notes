// dynamic-content-page.js
class DynamicContentPage {
  constructor(page) {
    this.page = page;
    this.contentArea = page.locator('#content-area');
    this.loadButton = page.locator('#load-content');
  }

  async loadContent() {
    await this.loadButton.click();
    // 等待内容加载完成
    await this.page.waitForSelector('#content-area .loaded-content', { state: 'visible' });
  }

  async waitForProgressComplete() {
    await this.page.waitForFunction(() => {
      const progress = document.querySelector('#progress');
      return progress && progress.getAttribute('value') === '100';
    });
  }
}

module.exports = { DynamicContentPage };