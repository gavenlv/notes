import { atom, useAtom, Provider as JotaiProvider } from 'jotai'
import { atomWithStorage } from 'jotai/utils'

// 创建主题原子
export const themeAtom = atomWithStorage('theme', 'dark')

// 创建温度原子
export const temperatureAtom = atom(20)

// 创建派生原子 - 从摄氏度转换为华氏度
export const fahrenheitAtom = atom(
  (get) => Math.round(get(temperatureAtom) * 9/5 + 32)
)

// 创建购物车原子
export const cartItemsAtom = atom([])

// 创建购物车总金额原子
export const cartTotalAtom = atom(
  (get) => get(cartItemsAtom).reduce((total, item) => {
    return total + item.price * item.quantity
  }, 0)
)

// 创建添加到购物车的操作原子
export const addToCartAtom = atom(
  null,
  (get, set, product) => {
    const currentItems = get(cartItemsAtom)
    const existingItem = currentItems.find(item => item.id === product.id)
    
    if (existingItem) {
      // 如果商品已存在，增加数量
      set(cartItemsAtom, currentItems.map(item =>
        item.id === product.id
          ? { ...item, quantity: item.quantity + 1 }
          : item
      ))
    } else {
      // 如果商品不存在，添加新商品
      set(cartItemsAtom, [...currentItems, { ...product, quantity: 1 }])
    }
  }
)

// 创建从购物车移除商品的操作原子
export const removeFromCartAtom = atom(
  null,
  (get, set, productId) => {
    set(cartItemsAtom, get(cartItemsAtom).filter(item => item.id !== productId))
  }
)

// 导出Provider
export { JotaiProvider }

// 自定义Hook使用主题
export const useTheme = () => {
  const [theme, setTheme] = useAtom(themeAtom)
  const toggleTheme = () => {
    setTheme(theme === 'dark' ? 'light' : 'dark')
  }
  return { theme, toggleTheme }
}

// 自定义Hook使用温度
export const useTemperature = () => {
  const [celsius, setCelsius] = useAtom(temperatureAtom)
  const [fahrenheit] = useAtom(fahrenheitAtom)
  
  return { celsius, fahrenheit, setCelsius }
}

// 自定义Hook使用购物车
export const useCart = () => {
  const [items, setItems] = useAtom(cartItemsAtom)
  const [total] = useAtom(cartTotalAtom)
  const [, addToCart] = useAtom(addToCartAtom)
  const [, removeFromCart] = useAtom(removeFromCartAtom)
  
  const clearCart = () => setItems([])
  
  return { items, total, addToCart, removeFromCart, clearCart }
}