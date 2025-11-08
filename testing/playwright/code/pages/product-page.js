// product-page.js
class ProductPage {
  constructor(page) {
    this.page = page;
    this.addToCartButton = page.locator('#add-to-cart');
    this.quantityInput = page.locator('#quantity');
  }

  async addToCart(quantity = 1) {
    await this.quantityInput.fill(quantity.toString());
    await this.addToCartButton.click();
  }
}

module.exports = { ProductPage };