import { create } from 'zustand'

// 创建用户状态store
export const useUserStore = create((set) => ({
  user: null,
  login: (userData) => set({ user: userData }),
  logout: () => set({ user: null }),
  updateProfile: (updates) => set((state) => ({
    user: state.user ? { ...state.user, ...updates } : null
  }))
}))

// 创建计数器状态store
export const useCounterStore = create((set) => ({
  count: 0,
  increment: () => set((state) => ({ count: state.count + 1 })),
  decrement: () => set((state) => ({ count: state.count - 1 })),
  reset: () => set({ count: 0 })
}))

// 创建产品列表store
export const useProductStore = create((set) => ({
  products: [
    { id: 1, name: 'React Book', price: 29.99, inStock: true },
    { id: 2, name: 'Redux Guide', price: 39.99, inStock: true },
    { id: 3, name: 'Zustand Tutorial', price: 19.99, inStock: false }
  ],
  addProduct: (product) => set((state) => ({
    products: [...state.products, { ...product, id: Date.now() }]
  })),
  toggleStock: (productId) => set((state) => ({
    products: state.products.map(product =>
      product.id === productId
        ? { ...product, inStock: !product.inStock }
        : product
    )
  }))
}))