import { createStore } from 'vuex'
import userModule from './modules/user'
import productsModule from './modules/products'

export default createStore({
  state: {
    // 全局状态
    isLoading: false,
    errorMessage: ''
  },
  getters: {
    // 全局 getters
    isLoading: state => state.isLoading,
    hasError: state => !!state.errorMessage,
    errorMessage: state => state.errorMessage
  },
  mutations: {
    // 全局 mutations
    SET_LOADING(state, status) {
      state.isLoading = status
    },
    SET_ERROR(state, message) {
      state.errorMessage = message
    }
  },
  actions: {
    // 全局 actions
    setError({ commit }, message) {
      commit('SET_ERROR', message)
    },
    setLoading({ commit }, status) {
      commit('SET_LOADING', status)
    }
  },
  modules: {
    // 模块化状态管理
    user: userModule,
    products: productsModule
  }
})