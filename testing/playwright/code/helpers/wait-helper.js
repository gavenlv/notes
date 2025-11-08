// wait-helper.js
class WaitHelper {
  static async waitForElementVisible(page, selector, timeout = 30000) {
    await page.waitForSelector(selector, { state: 'visible', timeout });
  }

  static async waitForElementAttached(page, selector, timeout = 30000) {
    await page.waitForSelector(selector, { state: 'attached', timeout });
  }

  static async waitForNetworkIdle(page, timeout = 30000) {
    await page.waitForLoadState('networkidle', { timeout });
  }
}

module.exports = { WaitHelper };