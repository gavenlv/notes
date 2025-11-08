// cart-page.js
class CartPage {
  constructor(page) {
    this.page = page;
    this.cartItems = page.locator('.cart-item');
  }

  async updateItemQuantity(itemName, quantity) {
    const item = this.cartItems.filter({ hasText: itemName });
    await item.locator('.quantity-input').fill(quantity.toString());
    await item.locator('.update-button').click();
  }

  async removeItem(itemName) {
    const item = this.cartItems.filter({ hasText: itemName });
    await item.locator('.remove-button').click();
  }

  async getItemQuantity(itemName) {
    const item = this.cartItems.filter({ hasText: itemName });
    return await item.locator('.quantity-input').inputValue();
  }
}

module.exports = { CartPage };