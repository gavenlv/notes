const state = {
  profile: {
    id: null,
    username: '',
    email: '',
    avatar: ''
  },
  isAuthenticated: false,
  permissions: []
}

const getters = {
  userProfile: state => state.profile,
  userId: state => state.profile.id,
  isAuthenticated: state => state.isAuthenticated,
  userPermissions: state => state.permissions,
  hasPermission: (state) => (permission) => {
    return state.permissions.includes(permission)
  }
}

const mutations = {
  SET_USER_PROFILE(state, profile) {
    state.profile = profile
    state.isAuthenticated = true
  },
  CLEAR_USER_PROFILE(state) {
    state.profile = {
      id: null,
      username: '',
      email: '',
      avatar: ''
    }
    state.isAuthenticated = false
    state.permissions = []
  },
  SET_PERMISSIONS(state, permissions) {
    state.permissions = permissions
  }
}

const actions = {
  async login({ commit }, credentials) {
    // 模拟登录API调用
    try {
      // 这里应该是实际的API调用
      const mockResponse = {
        user: {
          id: 1,
          username: credentials.username,
          email: `${credentials.username}@example.com`,
          avatar: 'https://i.pravatar.cc/150?img=1'
        },
        permissions: ['read', 'write']
      }
      
      commit('SET_USER_PROFILE', mockResponse.user)
      commit('SET_PERMISSIONS', mockResponse.permissions)
      return { success: true }
    } catch (error) {
      return { success: false, error: error.message }
    }
  },
  
  async logout({ commit }) {
    // 模拟登出API调用
    try {
      // 这里应该是实际的API调用
      commit('CLEAR_USER_PROFILE')
      return { success: true }
    } catch (error) {
      return { success: false, error: error.message }
    }
  },
  
  async updateProfile({ commit }, profileData) {
    // 模拟更新用户资料API调用
    try {
      // 这里应该是实际的API调用
      const updatedProfile = {
        ...profileData,
        id: 1
      }
      
      commit('SET_USER_PROFILE', updatedProfile)
      return { success: true, profile: updatedProfile }
    } catch (error) {
      return { success: false, error: error.message }
    }
  }
}

export default {
  namespaced: true,
  state,
  getters,
  mutations,
  actions
}