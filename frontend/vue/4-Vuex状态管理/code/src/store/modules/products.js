const state = {
  items: [],
  categories: [],
  selectedCategory: '',
  cart: []
}

const getters = {
  allProducts: state => state.items,
  productCategories: state => state.categories,
  selectedCategory: state => state.selectedCategory,
  filteredProducts: (state) => {
    if (!state.selectedCategory) {
      return state.items
    }
    return state.items.filter(product => product.category === state.selectedCategory)
  },
  cartItems: state => state.cart,
  cartItemCount: state => state.cart.length,
  cartTotal: state => {
    return state.cart.reduce((total, item) => {
      return total + (item.price * item.quantity)
    }, 0)
  }
}

const mutations = {
  SET_PRODUCTS(state, products) {
    state.items = products
  },
  SET_CATEGORIES(state, categories) {
    state.categories = categories
  },
  SET_SELECTED_CATEGORY(state, category) {
    state.selectedCategory = category
  },
  ADD_TO_CART(state, product) {
    const existingItem = state.cart.find(item => item.id === product.id)
    if (existingItem) {
      existingItem.quantity++
    } else {
      state.cart.push({ ...product, quantity: 1 })
    }
  },
  REMOVE_FROM_CART(state, productId) {
    state.cart = state.cart.filter(item => item.id !== productId)
  },
  UPDATE_CART_ITEM_QUANTITY(state, { productId, quantity }) {
    const item = state.cart.find(item => item.id === productId)
    if (item) {
      item.quantity = quantity
    }
  },
  CLEAR_CART(state) {
    state.cart = []
  }
}

const actions = {
  async fetchProducts({ commit }) {
    // 模拟获取产品列表API调用
    try {
      // 这里应该是实际的API调用
      const mockProducts = [
        { id: 1, name: '笔记本电脑', price: 5999, category: '电子产品', image: 'https://via.placeholder.com/150' },
        { id: 2, name: '无线鼠标', price: 99, category: '电子产品', image: 'https://via.placeholder.com/150' },
        { id: 3, name: '机械键盘', price: 299, category: '电子产品', image: 'https://via.placeholder.com/150' },
        { id: 4, name: '办公椅', price: 899, category: '家具', image: 'https://via.placeholder.com/150' },
        { id: 5, name: '台灯', price: 199, category: '家具', image: 'https://via.placeholder.com/150' }
      ]
      
      commit('SET_PRODUCTS', mockProducts)
      return { success: true, products: mockProducts }
    } catch (error) {
      return { success: false, error: error.message }
    }
  },
  
  async fetchCategories({ commit }) {
    // 模拟获取分类列表API调用
    try {
      // 这里应该是实际的API调用
      const mockCategories = ['全部', '电子产品', '家具']
      
      commit('SET_CATEGORIES', mockCategories)
      return { success: true, categories: mockCategories }
    } catch (error) {
      return { success: false, error: error.message }
    }
  },
  
  selectCategory({ commit }, category) {
    commit('SET_SELECTED_CATEGORY', category)
  },
  
  addToCart({ commit }, product) {
    commit('ADD_TO_CART', product)
  },
  
  removeFromCart({ commit }, productId) {
    commit('REMOVE_FROM_CART', productId)
  },
  
  updateCartItemQuantity({ commit }, payload) {
    commit('UPDATE_CART_ITEM_QUANTITY', payload)
  },
  
  clearCart({ commit }) {
    commit('CLEAR_CART')
  }
}

export default {
  namespaced: true,
  state,
  getters,
  mutations,
  actions
}