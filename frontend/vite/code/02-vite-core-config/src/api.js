// 导入第三方库
import axios from 'axios'
import { map, filter, groupBy, orderBy, debounce, uniqBy } from 'lodash-es'

// 导入配置
import { getApiConfig, isDevelopment } from './config.js'

// 创建axios实例
const apiClient = axios.create({
  ...getApiConfig(),
  // 其他axios配置
})

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    // 在发送请求之前做些什么
    console.log('API请求:', config.method?.toUpperCase(), config.url)
    return config
  },
  (error) => {
    // 对请求错误做些什么
    return Promise.reject(error)
  }
)

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => {
    // 对响应数据做点什么
    return response.data
  },
  (error) =
  {
    // 对响应错误做点什么
    console.error('API错误:', error.message)
    return Promise.reject(error)
  }
)

/**
 * 使用axios模拟API请求
 * 由于这是演示项目，我们返回模拟数据而不是实际调用API
 */
export async function fetchDataWithAxios() {
  if (isDevelopment()) {
    // 开发环境返回模拟数据
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          data: [
            { id: 1, name: '产品A', category: '电子产品', price: 2999, stock: 100 },
            { id: 2, name: '产品B', category: '电子产品', price: 1999, stock: 50 },
            { id: 3, name: '产品C', category: '家居用品', price: 299, stock: 200 },
            { id: 4, name: '产品D', category: '家居用品', price: 499, stock: 150 },
            { id: 5, name: '产品E', category: '办公用品', price: 99, stock: 300 }
          ],
          message: '获取数据成功',
          status: 'success'
        })
      }, 800) // 模拟网络延迟
    })
  }
  
  // 生产环境可以调用实际API
  try {
    return await apiClient.get('/products')
  } catch (error) {
    console.error('获取产品数据失败:', error)
    throw error
  }
}

/**
 * 使用lodash处理数据
 * 展示如何使用lodash的各种函数处理数据
 */
export function processDataWithLodash(data) {
  // 检查数据格式
  if (!data || !data.data || !Array.isArray(data.data)) {
    throw new Error('数据格式不正确')
  }
  
  const products = data.data
  
  // 1. 使用map转换数据格式
  const formattedProducts = map(products, product => ({
    ...product,
    priceFormatted: `¥${product.price.toLocaleString()}`,
    inStock: product.stock > 0,
    discountPrice: product.price * 0.9 // 模拟折扣价
  }))
  
  // 2. 使用filter筛选数据
  const inStockProducts = filter(formattedProducts, { inStock: true })
  
  // 3. 使用groupBy按类别分组
  const productsByCategory = groupBy(inStockProducts, 'category')
  
  // 4. 使用orderBy排序（按价格降序）
  const sortedProducts = orderBy(inStockProducts, ['price'], ['desc'])
  
  // 5. 计算总价和平均价格
  const totalPrice = inStockProducts.reduce((sum, product) => sum + product.price, 0)
  const averagePrice = totalPrice / inStockProducts.length
  
  // 6. 创建防抖函数示例
  const debouncedSearch = debounce((query) => {
    console.log('搜索查询:', query)
    // 实际应用中这里可以调用搜索API
  }, 300)
  
  // 返回处理结果
  return {
    formattedProducts,
    inStockProducts: inStockProducts.length,
    totalPrice: `¥${totalPrice.toLocaleString()}`,
    averagePrice: `¥${averagePrice.toFixed(2)}`,
    productsByCategory: Object.keys(productsByCategory).map(category => ({
      category,
      count: productsByCategory[category].length,
      products: productsByCategory[category].slice(0, 2) // 只返回前两个产品
    })),
    topProducts: sortedProducts.slice(0, 3), // 返回价格最高的3个产品
    // 注意：debouncedSearch函数在返回对象中不会被序列化，仅作示例
  }
}

/**
 * 获取分类列表
 */
export function getCategories(data) {
  if (!data || !data.data || !Array.isArray(data.data)) {
    return []
  }
  
  // 使用已导入的uniqBy获取唯一的分类
  const uniqueProducts = uniqBy(data.data, 'category')
  
  return uniqueProducts.map(product => product.category)
}

/**
 * 搜索产品（演示动态导入）
 */
export async function searchProducts(query) {
  // 动态导入lodash的debounce函数
  const { debounce } = await import('lodash-es')
  
  // 创建防抖搜索函数
  const debouncedSearch = debounce(async (searchQuery) => {
    try {
      console.log('执行搜索:', searchQuery)
      // 实际应用中这里可以调用搜索API
      return { results: [], query: searchQuery }
    } catch (error) {
      console.error('搜索失败:', error)
      throw error
    }
  }, 300)
  
  return debouncedSearch(query)
}
