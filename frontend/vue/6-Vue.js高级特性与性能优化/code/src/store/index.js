import { createStore } from 'vuex'

export default createStore({
  state: {
    count: 0,
    products: []
  },
  mutations: {
    increment(state) {
      state.count++
    },
    setProducts(state, products) {
      state.products = products
    }
  },
  actions: {
    fetchProducts({ commit }) {
      // 模拟API调用
      setTimeout(() => {
        const products = [
          { id: 1, name: 'Product 1', price: 100 },
          { id: 2, name: 'Product 2', price: 200 },
          { id: 3, name: 'Product 3', price: 300 }
        ]
        commit('setProducts', products)
      }, 1000)
    }
  },
  modules: {
  }
})