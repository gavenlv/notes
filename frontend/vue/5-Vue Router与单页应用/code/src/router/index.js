import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import About from '../views/About.vue'
import Products from '../views/Products.vue'
import ProductDetail from '../views/ProductDetail.vue'
import UserProfile from '../views/UserProfile.vue'
import Admin from '../views/Admin.vue'
import NotFound from '../views/NotFound.vue'

// 管理后台子路由组件
import AdminDashboard from '../views/admin/Dashboard.vue'
import UsersManagement from '../views/admin/Users.vue'
import ProductsManagement from '../views/admin/Products.vue'
import OrdersManagement from '../views/admin/Orders.vue'
import Settings from '../views/admin/Settings.vue'

// 模拟用户权限数据
const currentUser = {
  id: 1,
  name: 'Admin User',
  roles: ['user', 'admin']
}

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: { title: '首页' }
  },
  {
    path: '/about',
    name: 'About',
    component: About,
    meta: { title: '关于我们' }
  },
  {
    path: '/products',
    name: 'Products',
    component: Products,
    meta: { title: '产品列表' }
  },
  {
    path: '/products/:id',
    name: 'ProductDetail',
    component: ProductDetail,
    props: true,
    meta: { title: '产品详情' }
  },
  {
    path: '/user/:id',
    name: 'UserProfile',
    component: UserProfile,
    props: true,
    meta: { title: '用户资料', requiresAuth: true }
  },
  {
    path: '/admin',
    name: 'Admin',
    component: Admin,
    meta: { title: '管理后台', requiresAuth: true, requiresAdmin: true },
    children: [
      {
        path: '',
        name: 'AdminDashboard',
        component: AdminDashboard,
        meta: { title: '管理后台 - 仪表盘' }
      },
      {
        path: 'users',
        name: 'UsersManagement',
        component: UsersManagement,
        meta: { title: '管理后台 - 用户管理' }
      },
      {
        path: 'products',
        name: 'ProductsManagement',
        component: ProductsManagement,
        meta: { title: '管理后台 - 产品管理' }
      },
      {
        path: 'orders',
        name: 'OrdersManagement',
        component: OrdersManagement,
        meta: { title: '管理后台 - 订单管理' }
      },
      {
        path: 'settings',
        name: 'Settings',
        component: Settings,
        meta: { title: '管理后台 - 系统设置' }
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: NotFound,
    meta: { title: '页面未找到' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 全局前置守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  document.title = to.meta.title || 'Vue Router SPA'
  
  // 检查是否需要认证
  if (to.meta.requiresAuth) {
    // 模拟检查用户是否已登录
    const isAuthenticated = currentUser && currentUser.id
    
    if (!isAuthenticated) {
      // 未登录则重定向到首页
      next('/')
      return
    }
    
    // 检查是否需要管理员权限
    if (to.meta.requiresAdmin) {
      const isAdmin = currentUser.roles.includes('admin')
      if (!isAdmin) {
        // 没有管理员权限则重定向到首页
        next('/')
        return
      }
    }
  }
  
  // 继续导航
  next()
})

// 全局后置钩子
router.afterEach((to, from) => {
  // 可以在这里添加页面访问统计等逻辑
  console.log(`导航完成：从 ${from.path} 到 ${to.path}`)
})

export default router