<template>
  <div class="shopping-cart">
    <h2>购物车 ({{ cartItemCount }})</h2>
    
    <div v-if="cartItemCount === 0" class="empty-cart">
      <p>购物车为空</p>
    </div>
    
    <div v-else>
      <div class="cart-items">
        <div 
          v-for="item in cartItems" 
          :key="item.id" 
          class="cart-item"
        >
          <img :src="item.image" :alt="item.name" class="item-image" />
          <div class="item-details">
            <h3>{{ item.name }}</h3>
            <p class="price">¥{{ item.price }}</p>
          </div>
          <div class="quantity-controls">
            <button @click="updateQuantity(item.id, item.quantity - 1)" :disabled="item.quantity <= 1">-</button>
            <span>{{ item.quantity }}</span>
            <button @click="updateQuantity(item.id, item.quantity + 1)">+</button>
          </div>
          <div class="item-total">
            ¥{{ (item.price * item.quantity).toFixed(2) }}
          </div>
          <button @click="removeFromCart(item.id)" class="remove-btn">删除</button>
        </div>
      </div>
      
      <div class="cart-summary">
        <div class="total">
          总计: ¥{{ cartTotal.toFixed(2) }}
        </div>
        <button @click="checkout" :disabled="isLoading" class="checkout-btn">结算</button>
      </div>
    </div>
  </div>
</template>

<script>
import { mapState, mapGetters, mapActions } from 'vuex'

export default {
  name: 'ShoppingCartComponent',
  computed: {
    ...mapState(['isLoading']),
    ...mapGetters('products', ['cartItems', 'cartItemCount', 'cartTotal'])
  },
  methods: {
    ...mapActions('products', ['removeFromCart', 'updateCartItemQuantity', 'clearCart']),
    
    updateQuantity(productId, quantity) {
      if (quantity < 1) return
      this.updateCartItemQuantity({ productId, quantity })
    },
    
    checkout() {
      alert(`结算成功！总计: ¥${this.cartTotal.toFixed(2)}`)
      this.clearCart()
    }
  }
}
</script>

<style scoped>
.shopping-cart {
  background-color: #f9f9f9;
  padding: 20px;
  border-radius: 8px;
}

.empty-cart {
  text-align: center;
  padding: 40px 0;
  color: #999;
}

.cart-items {
  margin-bottom: 20px;
}

.cart-item {
  display: flex;
  align-items: center;
  padding: 15px;
  border-bottom: 1px solid #eee;
}

.item-image {
  width: 60px;
  height: 60px;
  object-fit: cover;
  margin-right: 15px;
}

.item-details {
  flex: 1;
}

.item-details h3 {
  margin: 0 0 5px 0;
}

.price {
  margin: 0;
  color: #42b983;
  font-weight: bold;
}

.quantity-controls {
  display: flex;
  align-items: center;
  margin: 0 20px;
}

.quantity-controls button {
  width: 30px;
  height: 30px;
  background-color: #eee;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.quantity-controls span {
  margin: 0 10px;
}

.item-total {
  width: 100px;
  text-align: right;
  font-weight: bold;
  margin-right: 20px;
}

.remove-btn {
  background-color: #ff6b6b;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
}

.cart-summary {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 20px;
  border-top: 2px solid #eee;
}

.total {
  font-size: 20px;
  font-weight: bold;
}

.checkout-btn {
  background-color: #42b983;
  color: white;
  border: none;
  padding: 12px 30px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
}

.checkout-btn:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}
</style>