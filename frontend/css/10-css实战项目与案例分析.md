# 第10章：CSS实战项目与案例分析

通过前九章的学习，我们已经掌握了CSS的基础知识、高级特性、性能优化以及现代工具的使用。本章将通过实际项目案例，展示如何将这些知识综合应用到真实场景中，帮助你从理论走向实践，成为一名优秀的前端开发者。

## 10.1 项目规划与架构设计

在开始编写CSS代码之前，良好的规划和架构设计是项目成功的关键。

### 10.1.1 CSS架构设计原则

- **一致性原则**：确保整个项目的样式风格统一
- **可扩展性原则**：设计能够轻松扩展和维护的样式系统
- **模块化原则**：将样式拆分为独立的、可复用的模块
- **关注点分离**：将布局、组件样式、主题等关注点分开管理
- **响应式优先**：从移动设备开始设计，然后逐步扩展到桌面设备

### 10.1.2 样式系统设计

构建一个完整的样式系统包括以下几个方面：

1. **设计令牌（Design Tokens）**：定义颜色、字体、间距等基础设计元素
2. **排版系统**：建立一致的字体层级和排版规则
3. **组件库**：设计可复用的UI组件
4. **布局系统**：提供灵活的页面布局解决方案
5. **主题系统**：支持多种主题（如浅色/深色模式）

### 10.1.3 项目结构示例

```
src/
├── assets/           # 静态资源
├── components/       # UI组件
│   ├── Button/       # 按钮组件
│   ├── Card/         # 卡片组件
│   └── ...
├── layouts/          # 布局组件
│   ├── Header/       # 头部布局
│   ├── Footer/       # 底部布局
│   └── ...
├── pages/            # 页面组件
│   ├── Home/         # 首页
│   ├── About/        # 关于页
│   └── ...
└── styles/           # 全局样式
    ├── base/         # 基础样式
    ├── utils/        # 工具类
    ├── theme/        # 主题样式
    └── index.scss    # 主样式入口
```

## 10.2 企业官网设计与实现

企业官网是展示公司形象和产品的重要窗口，我们将通过一个企业官网案例，展示如何构建专业、美观的网站。

### 10.2.1 设计规划

**目标受众**：潜在客户、合作伙伴、求职者
**设计风格**：专业、现代、简洁
**关键页面**：首页、关于我们、产品服务、团队介绍、联系我们
**响应式要求**：适配手机、平板和桌面设备

### 10.2.2 颜色方案设计

企业官网通常需要专业且可信的形象，我们可以使用以下颜色方案：

```scss
// 主色调：蓝色（代表专业、信任）
$primary: #1E40AF;
$primary-light: #3B82F6;
$primary-dark: #1E3A8A;

// 辅助色：中性色和强调色
$secondary: #F97316;
$success: #10B981;
$warning: #FBBF24;
$danger: #EF4444;

// 中性色
$white: #FFFFFF;
$gray-50: #F9FAFB;
$gray-100: #F3F4F6;
$gray-200: #E5E7EB;
$gray-300: #D1D5DB;
$gray-400: #9CA3AF;
$gray-500: #6B7280;
$gray-600: #4B5563;
$gray-700: #374151;
$gray-800: #1F2937;
$gray-900: #111827;
```

### 10.2.3 排版系统设计

良好的排版对于企业官网至关重要，我们将建立清晰的字体层级：

```scss
// 字体定义
$font-family-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
$font-family-display: 'Montserrat', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;

// 字体大小系统（响应式）
$font-sizes: (
  xs: (
    mobile: 0.75rem,
    tablet: 0.75rem,
    desktop: 0.75rem
  ),
  sm: (
    mobile: 0.875rem,
    tablet: 0.875rem,
    desktop: 0.875rem
  ),
  base: (
    mobile: 1rem,
    tablet: 1rem,
    desktop: 1rem
  ),
  lg: (
    mobile: 1.125rem,
    tablet: 1.125rem,
    desktop: 1.125rem
  ),
  xl: (
    mobile: 1.25rem,
    tablet: 1.25rem,
    desktop: 1.25rem
  ),
  '2xl': (
    mobile: 1.5rem,
    tablet: 1.5rem,
    desktop: 1.75rem
  ),
  '3xl': (
    mobile: 1.75rem,
    tablet: 2rem,
    desktop: 2.25rem
  ),
  '4xl': (
    mobile: 2rem,
    tablet: 2.5rem,
    desktop: 3rem
  ),
  '5xl': (
    mobile: 2.5rem,
    tablet: 3rem,
    desktop: 3.5rem
  )
);

// 行高系统
$line-heights: (
  tight: 1.25,
  normal: 1.5,
  relaxed: 1.75,
  loose: 2
);

// 字重系统
$font-weights: (
  thin: 100,
  light: 300,
  regular: 400,
  medium: 500,
  semibold: 600,
  bold: 700,
  extrabold: 800,
  black: 900
);
```

### 10.2.4 组件设计与实现

**1. 导航组件**

导航组件需要具有响应式设计，在移动设备上转换为汉堡菜单：

```scss
.header {
  background-color: $white;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 100;
  
  .nav-container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem;
    max-width: 1200px;
    margin: 0 auto;
  }
  
  .logo {
    font-size: 1.5rem;
    font-weight: 700;
    color: $primary;
    text-decoration: none;
  }
  
  .nav {
    display: flex;
    gap: 1.5rem;
    
    a {
      color: $gray-700;
      text-decoration: none;
      font-weight: 500;
      transition: color 0.2s ease;
      
      &:hover {
        color: $primary;
      }
      
      &.active {
        color: $primary;
        position: relative;
        
        &::after {
          content: '';
          position: absolute;
          bottom: -4px;
          left: 0;
          width: 100%;
          height: 2px;
          background-color: $primary;
        }
      }
    }
  }
  
  .mobile-menu-button {
    display: none;
    background: none;
    border: none;
    cursor: pointer;
    font-size: 1.5rem;
    color: $gray-700;
  }
}

// 响应式设计
@media (max-width: 768px) {
  .header {
    .nav {
      display: none;
      position: absolute;
      top: 100%;
      left: 0;
      right: 0;
      background-color: $white;
      flex-direction: column;
      padding: 1rem;
      box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .nav.open {
      display: flex;
    }
    
    .mobile-menu-button {
      display: block;
    }
  }
}
```

**2. 英雄区域组件**

英雄区域是网站的第一印象，需要具有视觉冲击力：

```scss
.hero {
  background: linear-gradient(135deg, $primary 0%, $primary-dark 100%);
  color: $white;
  padding: 5rem 0;
  text-align: center;
  position: relative;
  overflow: hidden;
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-image: url('../images/hero-pattern.svg');
    background-size: cover;
    opacity: 0.1;
  }
  
  .container {
    position: relative;
    z-index: 1;
    max-width: 900px;
    margin: 0 auto;
    padding: 0 1rem;
  }
  
  h1 {
    font-family: $font-family-display;
    font-size: map-get(map-get($font-sizes, '5xl'), desktop);
    font-weight: 800;
    line-height: map-get($line-heights, tight);
    margin-bottom: 1.5rem;
  }
  
  p {
    font-size: map-get(map-get($font-sizes, 'xl'), desktop);
    line-height: map-get($line-heights, relaxed);
    margin-bottom: 2.5rem;
    opacity: 0.9;
  }
  
  .cta-buttons {
    display: flex;
    justify-content: center;
    gap: 1rem;
    flex-wrap: wrap;
  }
}

// 响应式调整
@media (max-width: 768px) {
  .hero {
    padding: 3rem 0;
    
    h1 {
      font-size: map-get(map-get($font-sizes, '4xl'), mobile);
    }
    
    p {
      font-size: map-get(map-get($font-sizes, 'lg'), mobile);
    }
  }
}
```

### 10.2.5 布局系统实现

使用CSS Grid和Flexbox构建响应式布局：

```scss
// 容器类
.container {
  width: 100%;
  padding-right: 1rem;
  padding-left: 1rem;
  margin-right: auto;
  margin-left: auto;
  
  // 响应式容器宽度
  @media (min-width: 576px) {
    max-width: 540px;
  }
  
  @media (min-width: 768px) {
    max-width: 720px;
  }
  
  @media (min-width: 992px) {
    max-width: 960px;
  }
  
  @media (min-width: 1200px) {
    max-width: 1140px;
  }
}

// 行类
.row {
  display: flex;
  flex-wrap: wrap;
  margin-right: -0.5rem;
  margin-left: -0.5rem;
}

// 列类
.col,
.col-1, .col-2, .col-3, .col-4, .col-5, .col-6,
.col-7, .col-8, .col-9, .col-10, .col-11, .col-12,
.col-sm-1, .col-sm-2, .col-sm-3, .col-sm-4, .col-sm-5, .col-sm-6,
.col-sm-7, .col-sm-8, .col-sm-9, .col-sm-10, .col-sm-11, .col-sm-12,
.col-md-1, .col-md-2, .col-md-3, .col-md-4, .col-md-5, .col-md-6,
.col-md-7, .col-md-8, .col-md-9, .col-md-10, .col-md-11, .col-md-12,
.col-lg-1, .col-lg-2, .col-lg-3, .col-lg-4, .col-lg-5, .col-lg-6,
.col-lg-7, .col-lg-8, .col-lg-9, .col-lg-10, .col-lg-11, .col-lg-12 {
  position: relative;
  width: 100%;
  padding-right: 0.5rem;
  padding-left: 0.5rem;
}

// 基础列宽
.col-1 { width: 8.333333%; }
.col-2 { width: 16.666667%; }
.col-3 { width: 25%; }
.col-4 { width: 33.333333%; }
.col-5 { width: 41.666667%; }
.col-6 { width: 50%; }
.col-7 { width: 58.333333%; }
.col-8 { width: 66.666667%; }
.col-9 { width: 75%; }
.col-10 { width: 83.333333%; }
.col-11 { width: 91.666667%; }
.col-12 { width: 100%; }

// 响应式列（平板）
@media (min-width: 768px) {
  .col-md-1 { width: 8.333333%; }
  .col-md-2 { width: 16.666667%; }
  .col-md-3 { width: 25%; }
  .col-md-4 { width: 33.333333%; }
  .col-md-5 { width: 41.666667%; }
  .col-md-6 { width: 50%; }
  .col-md-7 { width: 58.333333%; }
  .col-md-8 { width: 66.666667%; }
  .col-md-9 { width: 75%; }
  .col-md-10 { width: 83.333333%; }
  .col-md-11 { width: 91.666667%; }
  .col-md-12 { width: 100%; }
}

// 响应式列（桌面）
@media (min-width: 1200px) {
  .col-lg-1 { width: 8.333333%; }
  .col-lg-2 { width: 16.666667%; }
  .col-lg-3 { width: 25%; }
  .col-lg-4 { width: 33.333333%; }
  .col-lg-5 { width: 41.666667%; }
  .col-lg-6 { width: 50%; }
  .col-lg-7 { width: 58.333333%; }
  .col-lg-8 { width: 66.666667%; }
  .col-lg-9 { width: 75%; }
  .col-lg-10 { width: 83.333333%; }
  .col-lg-11 { width: 91.666667%; }
  .col-lg-12 { width: 100%; }
}
```

## 10.3 电商网站设计与实现

电商网站需要注重用户体验和转化率，我们将通过一个电商网站案例，展示如何优化产品展示和购物流程。

### 10.3.1 设计规划

**目标受众**：购物者、潜在客户
**设计风格**：现代、直观、有吸引力
**关键页面**：首页、产品列表、产品详情、购物车、结账流程
**特殊要求**：产品筛选、分类浏览、搜索功能、购物车交互

### 10.3.2 产品卡片组件

产品卡片是电商网站的核心组件，需要清晰展示产品信息并吸引用户点击：

```scss
.product-card {
  background-color: $white;
  border-radius: 0.5rem;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  height: 100%;
  display: flex;
  flex-direction: column;
  
  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 10px 15px rgba(0, 0, 0, 0.1);
  }
  
  .product-image {
    position: relative;
    padding-top: 100%; // 正方形比例
    overflow: hidden;
    
    img {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      object-fit: cover;
      transition: transform 0.5s ease;
    }
    
    &:hover img {
      transform: scale(1.05);
    }
    
    .product-badge {
      position: absolute;
      top: 0.5rem;
      right: 0.5rem;
      background-color: $secondary;
      color: $white;
      padding: 0.25rem 0.5rem;
      border-radius: 0.25rem;
      font-size: 0.75rem;
      font-weight: 600;
    }
  }
  
  .product-info {
    padding: 1rem;
    flex-grow: 1;
    display: flex;
    flex-direction: column;
  }
  
  .product-category {
    font-size: 0.75rem;
    color: $gray-500;
    margin-bottom: 0.5rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }
  
  .product-title {
    font-size: 1rem;
    font-weight: 600;
    color: $gray-900;
    margin-bottom: 0.5rem;
    text-decoration: none;
    line-height: 1.4;
    height: 3.5rem; // 固定高度，保持卡片对齐
    overflow: hidden;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
  }
  
  .product-price {
    font-size: 1.125rem;
    font-weight: 700;
    color: $primary;
    margin-bottom: 1rem;
  }
  
  .product-actions {
    display: flex;
    gap: 0.5rem;
    margin-top: auto;
  }
  
  .add-to-cart-btn {
    flex-grow: 1;
    background-color: $primary;
    color: $white;
    border: none;
    padding: 0.5rem;
    border-radius: 0.25rem;
    font-weight: 500;
    cursor: pointer;
    transition: background-color 0.2s ease;
    
    &:hover {
      background-color: $primary-dark;
    }
  }
  
  .view-details-btn {
    padding: 0.5rem;
    border: 1px solid $gray-300;
    border-radius: 0.25rem;
    background-color: $white;
    cursor: pointer;
    transition: all 0.2s ease;
    
    &:hover {
      border-color: $primary;
      color: $primary;
    }
  }
}
```

### 10.3.3 产品列表页面布局

产品列表页面需要包含筛选、排序功能和响应式网格布局：

```scss
.product-listing {
  .layout {
    display: grid;
    grid-template-columns: 280px 1fr;
    gap: 2rem;
    
    @media (max-width: 768px) {
      grid-template-columns: 1fr;
    }
  }
  
  .sidebar {
    background-color: $white;
    padding: 1.5rem;
    border-radius: 0.5rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    
    h3 {
      font-size: 1.125rem;
      font-weight: 600;
      margin-bottom: 1rem;
      color: $gray-900;
    }
    
    .filter-section {
      margin-bottom: 1.5rem;
      
      &:last-child {
        margin-bottom: 0;
      }
      
      h4 {
        font-size: 0.875rem;
        font-weight: 600;
        margin-bottom: 0.75rem;
        color: $gray-700;
      }
      
      ul {
        list-style: none;
        padding: 0;
        margin: 0;
        
        li {
          margin-bottom: 0.5rem;
          
          &:last-child {
            margin-bottom: 0;
          }
          
          label {
            display: flex;
            align-items: center;
            cursor: pointer;
            font-size: 0.875rem;
            color: $gray-600;
            
            input[type="checkbox"] {
              margin-right: 0.5rem;
              accent-color: $primary;
            }
            
            &:hover {
              color: $primary;
            }
          }
        }
      }
    }
    
    .filter-actions {
      display: flex;
      gap: 0.5rem;
      margin-top: 1.5rem;
      padding-top: 1.5rem;
      border-top: 1px solid $gray-200;
      
      button {
        flex: 1;
        padding: 0.5rem;
        border: 1px solid $gray-300;
        border-radius: 0.25rem;
        background-color: $white;
        font-size: 0.875rem;
        cursor: pointer;
        transition: all 0.2s ease;
        
        &:first-child {
          background-color: $primary;
          color: $white;
          border-color: $primary;
          
          &:hover {
            background-color: $primary-dark;
          }
        }
        
        &:last-child:hover {
          border-color: $gray-400;
        }
      }
    }
  }
  
  .product-grid {
    .results-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 1.5rem;
      padding-bottom: 1rem;
      border-bottom: 1px solid $gray-200;
      
      h1 {
        font-size: 1.5rem;
        font-weight: 700;
        color: $gray-900;
        margin: 0;
      }
      
      .sort-options {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        
        label {
          font-size: 0.875rem;
          color: $gray-600;
        }
        
        select {
          padding: 0.5rem;
          border: 1px solid $gray-300;
          border-radius: 0.25rem;
          font-size: 0.875rem;
          background-color: $white;
        }
      }
    }
    
    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
      gap: 1.5rem;
      
      @media (min-width: 768px) {
        grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
      }
      
      @media (min-width: 1200px) {
        grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
      }
    }
    
    .pagination {
      display: flex;
      justify-content: center;
      margin-top: 3rem;
      gap: 0.25rem;
      
      button {
        width: 2.5rem;
        height: 2.5rem;
        display: flex;
        align-items: center;
        justify-content: center;
        border: 1px solid $gray-300;
        background-color: $white;
        border-radius: 0.25rem;
        cursor: pointer;
        font-size: 0.875rem;
        transition: all 0.2s ease;
        
        &:hover:not(:disabled) {
          border-color: $primary;
          color: $primary;
        }
        
        &:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }
        
        &.active {
          background-color: $primary;
          color: $white;
          border-color: $primary;
        }
      }
    }
  }
}
```

### 10.3.4 购物车交互设计

购物车功能需要流畅的动画和清晰的视觉反馈：

```scss
.cart {
  .cart-items {
    background-color: $white;
    border-radius: 0.5rem;
    overflow: hidden;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    margin-bottom: 2rem;
    
    .cart-header {
      display: grid;
      grid-template-columns: 3fr 1fr 1fr 1fr auto;
      gap: 1rem;
      padding: 1rem 1.5rem;
      background-color: $gray-50;
      border-bottom: 1px solid $gray-200;
      font-size: 0.875rem;
      font-weight: 600;
      color: $gray-600;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      
      @media (max-width: 768px) {
        display: none;
      }
    }
    
    .cart-item {
      display: grid;
      grid-template-columns: 3fr 1fr 1fr 1fr auto;
      gap: 1rem;
      padding: 1.5rem;
      border-bottom: 1px solid $gray-200;
      align-items: center;
      transition: background-color 0.2s ease;
      
      &:hover {
        background-color: $gray-50;
      }
      
      &:last-child {
        border-bottom: none;
      }
      
      @media (max-width: 768px) {
        grid-template-columns: 1fr;
        gap: 1rem;
      }
      
      .item-details {
        display: flex;
        align-items: center;
        gap: 1rem;
        
        @media (max-width: 768px) {
          flex-direction: column;
          text-align: center;
        }
        
        .item-image {
          width: 80px;
          height: 80px;
          border-radius: 0.25rem;
          overflow: hidden;
          flex-shrink: 0;
          
          img {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        object-fit: cover;
        transition: transform 0.5s ease;
      }
      
      &:hover img {
        transform: scale(1.05);
      }
    }
    
    .card-content {
      padding: 1rem;
      
      .card-title {
        font-size: 1.125rem;
        font-weight: 600;
        color: $gray-900;
        margin-bottom: 0.5rem;
      }
      
      .card-text {
        font-size: 0.875rem;
        color: $gray-600;
        margin-bottom: 1rem;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
      }
      
      .card-actions {
        display: flex;
        gap: 0.5rem;
      }
      
      .btn {
        padding: 0.5rem 1rem;
        border-radius: 0.25rem;
        font-size: 0.875rem;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s ease;
        text-decoration: none;
        display: inline-block;
        
        &.primary {
          background-color: $primary;
          color: $white;
          border: none;
          
          &:hover {
            background-color: $primary-dark;
          }
        }
        
        &.secondary {
          background-color: $white;
          color: $gray-700;
          border: 1px solid $gray-300;
          
          &:hover {
            border-color: $primary;
            color: $primary;
          }
        }
      }
    }
  }
}
```

### 10.5.6 响应式表单设计

为不同屏幕尺寸优化的表单设计：

```scss
.form-container {
  max-width: 100%;
  margin: 0 auto;
  padding: 1rem;
  
  @media (min-width: 768px) {
    max-width: 600px;
    padding: 2rem;
  }
  
  @media (min-width: 1200px) {
    max-width: 800px;
  }
  
  .form-title {
    font-size: 1.5rem;
    font-weight: 700;
    color: $gray-900;
    margin-bottom: 1.5rem;
    text-align: center;
    
    @media (min-width: 768px) {
      text-align: left;
    }
  }
  
  .form-group {
    margin-bottom: 1.5rem;
    
    .form-label {
      display: block;
      font-size: 0.875rem;
      font-weight: 600;
      color: $gray-700;
      margin-bottom: 0.5rem;
    }
    
    .form-input {
      width: 100%;
      padding: 0.75rem 1rem;
      border: 1px solid $gray-300;
      border-radius: 0.5rem;
      font-size: 1rem;
      transition: border-color 0.2s ease, box-shadow 0.2s ease;
      
      &:focus {
        outline: none;
        border-color: $primary;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
      }
      
      &::placeholder {
        color: $gray-400;
      }
      
      // 触摸优化 - 增加点击区域
      
      &[type="checkbox"],
      &[type="radio"] {
        width: auto;
        height: auto;
        margin-right: 0.5rem;
        min-width: 1.25rem;
        min-height: 1.25rem;
      }
    }
    
    .form-textarea {
      width: 100%;
      padding: 0.75rem 1rem;
      border: 1px solid $gray-300;
      border-radius: 0.5rem;
      font-size: 1rem;
      resize: vertical;
      min-height: 120px;
      transition: border-color 0.2s ease, box-shadow 0.2s ease;
      
      &:focus {
        outline: none;
        border-color: $primary;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
      }
    }
    
    .form-select {
      width: 100%;
      padding: 0.75rem 1rem;
      border: 1px solid $gray-300;
      border-radius: 0.5rem;
      font-size: 1rem;
      background-color: $white;
      appearance: none;
      background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='M6 8l4 4 4-4'/%3e%3c/svg%3e");
      background-position: right 0.75rem center;
      background-repeat: no-repeat;
      background-size: 1.5em 1.5em;
      transition: border-color 0.2s ease, box-shadow 0.2s ease;
      
      &:focus {
        outline: none;
        border-color: $primary;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
      }
    }
    
    .form-check {
      display: flex;
      align-items: center;
      margin-bottom: 0.5rem;
      
      .form-check-input {
        width: 1.25rem;
        height: 1.25rem;
        margin-right: 0.5rem;
        accent-color: $primary;
      }
      
      .form-check-label {
        font-size: 0.875rem;
        color: $gray-700;
      }
    }
  }
  
  .form-row {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
    
    @media (min-width: 768px) {
      flex-direction: row;
    }
    
    .form-group {
      flex: 1;
      margin-bottom: 0;
    }
  }
  
  .form-actions {
    margin-top: 2rem;
    
    .btn {
      width: 100%;
      padding: 0.75rem 1.5rem;
      border-radius: 0.5rem;
      font-size: 1rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s ease;
      text-decoration: none;
      display: inline-block;
      text-align: center;
      
      @media (min-width: 768px) {
        width: auto;
      }
      
      &.primary {
        background-color: $primary;
        color: $white;
        border: none;
        
        &:hover {
          background-color: $primary-dark;
        }
      }
      
      &.secondary {
        background-color: $white;
        color: $gray-700;
        border: 1px solid $gray-300;
        
        &:hover {
          border-color: $primary;
          color: $primary;
        }
      }
    }
  }
}
```

## 10.6 无障碍设计实战

无障碍设计确保所有用户（包括残障人士）都能使用网站，这不仅是道德要求，也是许多国家的法律要求。

### 10.6.1 无障碍设计原则

- **感知性（Perceivable）**：信息和用户界面组件必须以用户可以感知的方式呈现
- **可操作性（Operable）**：用户界面组件和导航必须可操作
- **可理解性（Understandable）**：信息和用户界面操作必须可理解
- **鲁棒性（Robust）**：内容必须足够健壮，能被各种用户代理可靠地解释

### 10.6.2 语义化HTML结构

```html
\u003c!-- 语义化HTML示例 --\u003e
\u003cheader class="site-header"\u003e
  \u003ch1 class="site-title"\u003e网站标题\u003c/h1\u003e
  \u003cnav aria-label="主导航"\u003e
    \u003cul class="nav-list"\u003e
      \u003cli\u003e\u003ca href="/"\u003e首页\u003c/a\u003e\u003c/li\u003e
      \u003cli\u003e\u003ca href="/about"\u003e关于我们\u003c/a\u003e\u003c/li\u003e
      \u003cli\u003e\u003ca href="/contact"\u003e联系我们\u003c/a\u003e\u003c/li\u003e
    \u003c/ul\u003e
  \u003c/nav\u003e
\u003c/header\u003e

\u003cmain\u003e
  \u003csection aria-labelledby="products-heading"\u003e
    \u003ch2 id="products-heading"\u003e我们的产品\u003c/h2\u003e
    \u003c!-- 产品内容 --\u003e
  \u003c/section\u003e
\u003c/main\u003e

\u003cfooter class="site-footer"\u003e
  \u003c!-- 页脚内容 --\u003e
\u003c/footer\u003e
```

### 10.6.3 无障碍CSS样式

```scss
// 无障碍样式增强

// 1. 焦点样式优化
*:focus-visible {
  outline: 3px solid $primary;
  outline-offset: 2px;
}

// 2. 颜色对比度优化
.text-high-contrast {
  color: $gray-900;
  background-color: $white;
}

// 3. 跳过导航链接
.skip-link {
  position: absolute;
  top: -100px;
  left: 0;
  background-color: $primary;
  color: $white;
  padding: 0.75rem 1rem;
  text-decoration: none;
  z-index: 1000;
  border-radius: 0 0 0.25rem 0.25rem;
  transition: top 0.3s ease;
  
  &:focus {
    top: 0;
  }
}

// 4. 高对比度模式支持
@media (prefers-contrast: high) {
  :root {
    --primary-color: #0033cc;
    --text-color: #000000;
    --background-color: #ffffff;
  }
  
  body {
    background-color: var(--background-color);
    color: var(--text-color);
  }
  
  a {
    color: var(--primary-color);
    text-decoration: underline;
    text-decoration-thickness: 2px;
  }
}

// 5. 减少动画模式支持
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}

// 6. 可访问的表单样式
.form-input:focus,
.form-textarea:focus,
.form-select:focus {
  outline: 3px solid $primary;
  outline-offset: 2px;
  border-color: transparent;
}

// 7. 键盘导航指示器
.tab-nav {
  li {
    
    &:focus-within {
      position: relative;
      
      &::before {
        content: '';
        position: absolute;
        top: -0.5rem;
        left: -0.5rem;
        right: -0.5rem;
        bottom: -0.5rem;
        border: 2px dashed $primary;
        border-radius: 0.25rem;
      }
    }
  }
}

// 8. 视觉指示器
.visually-hidden {
  position: absolute !important;
  width: 1px !important;
  height: 1px !important;
  padding: 0 !important;
  margin: -1px !important;
  overflow: hidden !important;
  clip: rect(0, 0, 0, 0) !important;
  white-space: nowrap !important;
  border: 0 !important;
}

// 9. 错误状态增强
.input-error {
  border-color: $danger !important;
  
  &:focus {
    box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1) !important;
    outline-color: $danger !important;
  }
}

// 10. 无障碍按钮样式
.btn {
  min-height: 3rem;
  min-width: 3rem;
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  line-height: 1.5;
  
  // 触摸优化
  touch-action: manipulation;
  
  // 确保按钮有足够的对比度
  
  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
  
  // 图标按钮额外样式
  
  &.icon-btn {
    padding: 0.75rem;
    min-width: 2.5rem;
    min-height: 2.5rem;
  }
}
```

## 10.7 CSS与JavaScript交互实战

现代Web应用需要CSS和JavaScript的紧密配合，我们将通过一些实用示例，展示如何实现动态样式和交互效果。

### 10.7.1 主题切换实现

```scss
// CSS主题变量定义
:root {
  // 浅色主题变量
  --primary: #1E40AF;
  --primary-light: #3B82F6;
  --primary-dark: #1E3A8A;
  --secondary: #F97316;
  --background: #FFFFFF;
  --surface: #F9FAFB;
  --text-primary: #111827;
  --text-secondary: #4B5563;
  --text-muted: #9CA3AF;
  --border: #E5E7EB;
  --success: #10B981;
  --warning: #FBBF24;
  --danger: #EF4444;
}

// 深色主题类
.dark-theme {
  --primary: #3B82F6;
  --primary-light: #60A5FA;
  --primary-dark: #2563EB;
  --secondary: #FB923C;
  --background: #0F172A;
  --surface: #1E293B;
  --text-primary: #F8FAFC;
  --text-secondary: #CBD5E1;
  --text-muted: #94A3B8;
  --border: #334155;
  --success: #34D399;
  --warning: #FCD34D;
  --danger: #F87171;
}

// 应用主题变量的全局样式
body {
  background-color: var(--background);
  color: var(--text-primary);
  transition: background-color 0.3s ease, color 0.3s ease;
}

// 使用主题变量的组件样式
.card {
  background-color: var(--surface);
  border: 1px solid var(--border);
  border-radius: 0.5rem;
  padding: 1.5rem;
  transition: background-color 0.3s ease, border-color 0.3s ease;
}

.btn {
  background-color: var(--primary);
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: background-color 0.3s ease;
  
  &:hover {
    background-color: var(--primary-dark);
  }
}

.text-secondary {
  color: var(--text-secondary);
}

.border {
  border-color: var(--border);
}
```

JavaScript实现主题切换：

```javascript
// 主题切换功能
function setupThemeToggle() {
  const themeToggle = document.getElementById('theme-toggle');
  const html = document.documentElement;
  
  // 检查本地存储中的主题偏好
  const savedTheme = localStorage.getItem('theme');
  
  // 检查系统偏好
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  
  // 设置初始主题
  if (savedTheme === 'dark' || (!savedTheme && prefersDark)) {
    html.classList.add('dark-theme');
  } else {
    html.classList.remove('dark-theme');
  }
  
  // 更新主题切换按钮图标
  updateThemeToggleIcon();
  
  // 添加点击事件监听器
  themeToggle.addEventListener('click', () => {
    html.classList.toggle('dark-theme');
    
    // 保存主题偏好到本地存储
    const currentTheme = html.classList.contains('dark-theme') ? 'dark' : 'light';
    localStorage.setItem('theme', currentTheme);
    
    // 更新按钮图标
    updateThemeToggleIcon();
  });
  
  // 监听系统主题变化
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
    if (!localStorage.getItem('theme')) { // 只有在用户没有明确设置主题时才响应系统变化
      if (e.matches) {
        html.classList.add('dark-theme');
      } else {
        html.classList.remove('dark-theme');
      }
      updateThemeToggleIcon();
    }
  });
}

function updateThemeToggleIcon() {
  const themeToggle = document.getElementById('theme-toggle');
  const isDark = document.documentElement.classList.contains('dark-theme');
  
  // 移除所有图标类
  themeToggle.classList.remove('fa-sun', 'fa-moon');
  
  // 添加当前主题对应的图标
  if (isDark) {
    themeToggle.classList.add('fa-sun');
    themeToggle.setAttribute('aria-label', '切换到浅色模式');
  } else {
    themeToggle.classList.add('fa-moon');
    themeToggle.setAttribute('aria-label', '切换到深色模式');
  }
}

// 在DOM加载完成后初始化
document.addEventListener('DOMContentLoaded', setupThemeToggle);
```

### 10.7.2 滚动触发动画

```scss
// 滚动触发动画样式
.fade-in {
  opacity: 0;
  transform: translateY(20px);
  transition: opacity 0.6s ease, transform 0.6s ease;
  
  &.animate {
    opacity: 1;
    transform: translateY(0);
  }
}

.slide-in-left {
  opacity: 0;
  transform: translateX(-30px);
  transition: opacity 0.6s ease, transform 0.6s ease;
  
  &.animate {
    opacity: 1;
    transform: translateX(0);
  }
}

.slide-in-right {
  opacity: 0;
  transform: translateX(30px);
  transition: opacity 0.6s ease, transform 0.6s ease;
  
  &.animate {
    opacity: 1;
    transform: translateX(0);
  }
}

// 交错动画延迟
.delay-1 {
  transition-delay: 0.1s;
}

.delay-2 {
  transition-delay: 0.2s;
}

.delay-3 {
  transition-delay: 0.3s;
}

.delay-4 {
  transition-delay: 0.4s;
}

.delay-5 {
  transition-delay: 0.5s;
}
```

JavaScript实现滚动触发：

```javascript
// 滚动触发动画
function setupScrollAnimations() {
  const animatedElements = document.querySelectorAll('.fade-in, .slide-in-left, .slide-in-right');
  
  // 检查元素是否在视口中
  function isInViewport(element) {
    const rect = element.getBoundingClientRect();
    const windowHeight = window.innerHeight || document.documentElement.clientHeight;
    const windowWidth = window.innerWidth || document.documentElement.clientWidth;
    
    // 定义一个稍微大一点的视口区域，以便提前触发动画
    const triggerTop = 0;
    const triggerBottom = windowHeight * 0.8;
    const triggerLeft = 0;
    const triggerRight = windowWidth * 0.8;
    
    return (
      rect.top <= triggerBottom &&
      rect.bottom >= triggerTop &&
      rect.left <= triggerRight &&
      rect.right >= triggerLeft
    );
  }
  
  // 为元素添加动画类
  function animateOnScroll() {
    animatedElements.forEach(element => {
      if (isInViewport(element)) {
        element.classList.add('animate');
      }
    });
  }
  
  // 初始检查
  animateOnScroll();
  
  // 监听滚动事件
  window.addEventListener('scroll', animateOnScroll);
  
  // 监听窗口大小变化
  window.addEventListener('resize', animateOnScroll);
  
  // 监听页面加载完成
  window.addEventListener('load', animateOnScroll);
}

// 在DOM加载完成后初始化
document.addEventListener('DOMContentLoaded', setupScrollAnimations);
```

### 10.7.3 交互式导航菜单

```scss
// 交互式导航样式
.nav {
  background-color: var(--background);
  border-bottom: 1px solid var(--border);
  position: sticky;
  top: 0;
  z-index: 100;
  transition: background-color 0.3s ease, box-shadow 0.3s ease, padding 0.3s ease;
  
  // 滚动时的导航栏样式
  &.scrolled {
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    padding-top: 0.5rem;
    padding-bottom: 0.5rem;
    background-color: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px);
    
    // 深色模式下的滚动样式
    .dark-theme & {
      background-color: rgba(15, 23, 42, 0.95);
    }
  }
  
  .container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem;
    max-width: 1200px;
    margin: 0 auto;
  }
  
  .logo {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--primary);
    text-decoration: none;
  }
  
  .nav-links {
    display: flex;
    gap: 1.5rem;
    
    @media (max-width: 768px) {
      position: fixed;
      top: 60px;
      left: 0;
      right: 0;
      background-color: var(--background);
      flex-direction: column;
      align-items: center;
      padding: 2rem;
      gap: 1.5rem;
      box-shadow: 0 10px 15px rgba(0, 0, 0, 0.1);
      transform: translateY(-150%);
      transition: transform 0.3s ease;
      z-index: 99;
      
      &.open {
        transform: translateY(0);
      }
    }
    
    a {
      color: var(--text-secondary);
      text-decoration: none;
      font-weight: 500;
      transition: color 0.2s ease;
      position: relative;
      
      &:hover {
        color: var(--primary);
      }
      
      &.active {
        color: var(--primary);
        
        &::after {
          content: '';
          position: absolute;
          bottom: -6px;
          left: 0;
          width: 100%;
          height: 2px;
          background-color: var(--primary);
        }
      }
    }
  }
  
  .menu-toggle {
    display: none;
    background: none;
    border: none;
    cursor: pointer;
    font-size: 1.5rem;
    color: var(--text-primary);
    
    @media (max-width: 768px) {
      display: block;
    }
  }
}
```

JavaScript实现导航交互：

```javascript
// 交互式导航菜单
function setupInteractiveNav() {
  const nav = document.querySelector('.nav');
  const navLinks = document.querySelector('.nav-links');
  const menuToggle = document.querySelector('.menu-toggle');
  const navItems = document.querySelectorAll('.nav-links a');
  
  // 滚动监听 - 导航栏样式变化
  function handleScroll() {
    if (window.scrollY > 20) {
      nav.classList.add('scrolled');
    } else {
      nav.classList.remove('scrolled');
    }
  }
  
  // 移动端菜单切换
  function toggleMenu() {
    navLinks.classList.toggle('open');
    
    // 更新按钮图标和无障碍属性
    const isOpen = navLinks.classList.contains('open');
    if (isOpen) {
      menuToggle.innerHTML = '<i class="fas fa-times"></i>';
      menuToggle.setAttribute('aria-expanded', 'true');
      // 禁用背景滚动
      document.body.style.overflow = 'hidden';
    } else {
      menuToggle.innerHTML = '<i class="fas fa-bars"></i>';
      menuToggle.setAttribute('aria-expanded', 'false');
      // 启用背景滚动
      document.body.style.overflow = '';
    }
  }
  
  // 平滑滚动到锚点
  function setupSmoothScroll() {
    navItems.forEach(item => {
      item.addEventListener('click', (e) => {
        const href = item.getAttribute('href');
        
        // 如果是锚点链接
        if (href.startsWith('#')) {
          e.preventDefault();
          
          // 关闭移动端菜单
          if (navLinks.classList.contains('open')) {
            toggleMenu();
          }
          
          // 找到目标元素
          const targetId = href;
          const targetElement = document.querySelector(targetId);
          
          if (targetElement) {
            // 计算滚动位置，考虑导航栏高度
            const navHeight = nav.offsetHeight;
            const targetPosition = targetElement.getBoundingClientRect().top + window.pageYOffset - navHeight;
            
            // 平滑滚动
            window.scrollTo({
              top: targetPosition,
              behavior: 'smooth'
            });
            
            // 更新URL（不刷新页面）
            history.pushState(null, null, targetId);
          }
        }
      });
    });
  }
  
  // 设置当前活动链接
  function setActiveLink() {
    const scrollPosition = window.scrollY;
    
    // 检查每个部分
    document.querySelectorAll('section[id]').forEach(section => {
      const sectionTop = section.offsetTop - 100;
      const sectionHeight = section.offsetHeight;
      const sectionId = section.getAttribute('id');
      
      if (scrollPosition >= sectionTop && scrollPosition < sectionTop + sectionHeight) {
        // 移除所有活动类
        navItems.forEach(item => {
          item.classList.remove('active');
        });
        
        // 添加当前活动类
        const activeItem = document.querySelector(`.nav-links a[href="#${sectionId}"]`);
        if (activeItem) {
          activeItem.classList.add('active');
        }
      }
    });
  }
  
  // 初始化事件监听器
  window.addEventListener('scroll', handleScroll);
  window.addEventListener('scroll', setActiveLink);
  menuToggle.addEventListener('click', toggleMenu);
  setupSmoothScroll();
  
  // 初始调用
  handleScroll();
  setActiveLink();
  
  // 设置无障碍属性
  menuToggle.setAttribute('aria-label', '打开导航菜单');
  menuToggle.setAttribute('aria-expanded', 'false');
  navLinks.setAttribute('role', 'menu');
  navItems.forEach(item => {
    item.setAttribute('role', 'menuitem');
  });
}

// 在DOM加载完成后初始化
document.addEventListener('DOMContentLoaded', setupInteractiveNav);
```

## 10.8 项目实战总结与最佳实践

通过前面的案例分析，我们已经掌握了如何在实际项目中应用CSS技术。下面是一些关键的最佳实践总结。

### 10.8.1 代码组织与维护

- **模块化设计**：将CSS拆分为独立的功能模块，每个模块负责特定的功能
- **文件结构**：建立清晰的文件结构，按功能、组件或页面组织CSS文件
- **命名规范**：采用一致的命名规范（如BEM、ITCSS、OOCSS等）
- **注释文档**：为复杂样式添加注释，说明设计决策和实现细节
- **版本控制**：使用Git等版本控制系统管理CSS代码变更

### 10.8.2 性能优化策略

- **减少CSS体积**：删除未使用的CSS，合并和压缩样式文件
- **减少重排和重绘**：优先使用transform和opacity进行动画
- **使用CSS变量**：提高样式的可维护性和灵活性
- **优化选择器**：使用高效的CSS选择器，避免深层次嵌套
- **利用CSS containment**：限制样式计算和布局操作的范围
- **延迟加载非关键CSS**：优先加载首屏必要样式

### 10.8.3 响应式设计最佳实践

- **移动优先**：从移动设备开始设计，然后逐步增强到桌面设备
- **流式布局**：使用相对单位和灵活的布局技术
- **断点策略**：基于内容而非设备设置媒体查询断点
- **响应式图像**：使用srcset和sizes属性优化图像加载
- **触摸友好**：确保交互元素足够大，适合触摸操作
- **可访问性**：确保在所有设备上都具有良好的可访问性

### 10.8.4 团队协作建议

- **设计系统**：建立统一的设计系统，确保品牌一致性
- **编码规范**：制定团队CSS编码规范和最佳实践文档
- **代码审查**：定期进行CSS代码审查，确保代码质量
- **自动化工具**：使用linting工具和自动化流程确保代码质量
- **持续集成**：将CSS质量检查集成到CI/CD流程中

### 10.8.5 未来趋势展望

- **CSS Grid和Flexbox**：这两种布局技术已成为现代Web布局的标准
- **CSS变量**：提供动态主题和配置能力
- **CSS-in-JS**：将CSS与JavaScript结合，提供更好的组件封装
- **CSS Houdini**：提供底层API，让开发者能够扩展CSS的能力
- **Container Queries**：元素级别的响应式设计，基于父容器而不是视口
- **CSS动画和过渡**：继续发展，提供更丰富的交互体验
- **性能优化**：CSS将更加注重性能，提供更多性能优化的工具和技术

## 总结

本章通过实际项目案例，展示了如何将CSS知识应用到真实场景中。从企业官网到电商网站，从单页应用到移动端设计，我们覆盖了各种常见的Web项目类型。通过这些实战案例，我们学习了：

1. 如何规划和设计CSS架构
2. 如何实现不同类型项目的布局和组件
3. 如何优化移动端和桌面端的用户体验
4. 如何确保网站的无障碍性
5. 如何实现CSS与JavaScript的交互
6. 如何遵循性能优化和最佳实践

通过不断的实践和学习，你可以成为一名优秀的前端开发者，能够构建出既美观又实用的Web应用。记住，CSS是一门不断发展的技术，保持学习的态度，关注最新的CSS特性和最佳实践，你的技能将会不断提升。

祝你在CSS的学习和实践中取得成功！
 {
            width: 100%;
            height: 100%;
            object-fit: cover;
          }
        }
        
        .item-info {
          
          .item-title {
            font-weight: 600;
            color: $gray-900;
            margin-bottom: 0.25rem;
            text-decoration: none;
            
            &:hover {
              color: $primary;
            }
          }
          
          .item-variant {
            font-size: 0.875rem;
            color: $gray-500;
          }
        }
      }
      
      .item-price {
        font-weight: 600;
        color: $gray-900;
        
        @media (max-width: 768px) {
          font-size: 0.875rem;
        }
      }
      
      .item-quantity {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        
        button {
          width: 2rem;
          height: 2rem;
          border: 1px solid $gray-300;
          background-color: $white;
          border-radius: 0.25rem;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: all 0.2s ease;
          
          &:hover:not(:disabled) {
            border-color: $primary;
            color: $primary;
          }
          
          &:disabled {
            opacity: 0.5;
            cursor: not-allowed;
          }
        }
        
        input {
          width: 3rem;
          height: 2rem;
          border: 1px solid $gray-300;
          border-radius: 0.25rem;
          text-align: center;
          font-size: 0.875rem;
        }
      }
      
      .item-subtotal {
        font-weight: 700;
        color: $primary;
        
        @media (max-width: 768px) {
          font-size: 0.875rem;
        }
      }
      
      .item-remove {
        button {
          width: 2rem;
          height: 2rem;
          border: none;
          background-color: transparent;
          color: $gray-400;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          border-radius: 0.25rem;
          transition: all 0.2s ease;
          
          &:hover {
            background-color: $gray-100;
            color: $danger;
          }
        }
      }
    }
    
    .empty-cart {
      padding: 4rem 2rem;
      text-align: center;
      
      .empty-icon {
        font-size: 3rem;
        color: $gray-300;
        margin-bottom: 1rem;
      }
      
      h3 {
        font-size: 1.25rem;
        font-weight: 600;
        color: $gray-700;
        margin-bottom: 0.5rem;
      }
      
      p {
        color: $gray-500;
        margin-bottom: 1.5rem;
      }
    }
  }
  
  .cart-summary {
    background-color: $white;
    border-radius: 0.5rem;
    padding: 1.5rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    
    h2 {
      font-size: 1.25rem;
      font-weight: 700;
      color: $gray-900;
      margin-bottom: 1.5rem;
      padding-bottom: 1rem;
      border-bottom: 1px solid $gray-200;
    }
    
    .summary-row {
      display: flex;
      justify-content: space-between;
      margin-bottom: 1rem;
      font-size: 0.875rem;
      
      &.total {
        margin-top: 1.5rem;
        padding-top: 1.5rem;
        border-top: 1px solid $gray-200;
        font-size: 1rem;
        font-weight: 700;
        color: $gray-900;
      }
      
      .label {
        color: $gray-600;
      }
    }
    
    .checkout-btn {
      width: 100%;
      background-color: $primary;
      color: $white;
      border: none;
      padding: 1rem;
      border-radius: 0.25rem;
      font-size: 1rem;
      font-weight: 600;
      cursor: pointer;
      transition: background-color 0.2s ease;
      margin-top: 1rem;
      
      &:hover {
        background-color: $primary-dark;
      }
      
      &:disabled {
        background-color: $gray-400;
        cursor: not-allowed;
      }
    }
  }
}
```

## 10.4 单页应用设计与实现

单页应用（SPA）需要流畅的交互体验和动态加载内容，我们将通过一个Dashboard案例，展示如何构建现代化的单页应用界面。

### 10.4.1 设计规划

**目标受众**：应用用户、数据分析师
**设计风格**：现代、简洁、高效
**关键组件**：侧边导航、顶部工具栏、数据卡片、图表、表格、模态框
**特殊要求**：深色模式支持、动态内容加载、数据可视化

### 10.4.2 布局结构实现

Dashboard布局需要包含固定的侧边导航和可滚动的主内容区域：

```scss
.dashboard {
  display: flex;
  min-height: 100vh;
  background-color: $gray-50;
  
  .sidebar {
    width: 250px;
    background-color: $white;
    box-shadow: 1px 0 3px rgba(0, 0, 0, 0.1);
    position: fixed;
    top: 0;
    left: 0;
    bottom: 0;
    overflow-y: auto;
    z-index: 10;
    transition: transform 0.3s ease;
    
    @media (max-width: 768px) {
      transform: translateX(-100%);
      
      &.open {
        transform: translateX(0);
      }
    }
    
    .sidebar-header {
      padding: 1.5rem 1rem;
      border-bottom: 1px solid $gray-200;
      
      .logo {
        font-size: 1.25rem;
        font-weight: 700;
        color: $primary;
        text-decoration: none;
        display: flex;
        align-items: center;
        gap: 0.5rem;
      }
    }
    
    .sidebar-nav {
      padding: 1rem 0;
      
      .nav-section {
        margin-bottom: 1rem;
        
        .section-title {
          font-size: 0.75rem;
          font-weight: 600;
          color: $gray-500;
          text-transform: uppercase;
          letter-spacing: 0.05em;
          padding: 0 1rem 0.5rem;
        }
        
        .nav-item {
          
          a {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            padding: 0.75rem 1rem;
            color: $gray-700;
            text-decoration: none;
            font-size: 0.875rem;
            transition: all 0.2s ease;
            
            .nav-icon {
              font-size: 1rem;
              width: 1.25rem;
              text-align: center;
            }
            
            &:hover {
              background-color: $gray-50;
              color: $primary;
            }
            
            &.active {
              background-color: rgba(59, 130, 246, 0.1);
              color: $primary;
              border-left: 3px solid $primary;
              font-weight: 500;
            }
          }
        }
      }
    }
    
    .sidebar-footer {
      padding: 1rem;
      border-top: 1px solid $gray-200;
      margin-top: auto;
      
      .user-profile {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        
        .user-avatar {
          width: 3rem;
          height: 3rem;
          border-radius: 50%;
          overflow: hidden;
          
          img {
            width: 100%;
            height: 100%;
            object-fit: cover;
          }
        }
        
        .user-info {
          
          .user-name {
            font-weight: 600;
            color: $gray-900;
            font-size: 0.875rem;
            margin-bottom: 0.125rem;
          }
          
          .user-role {
            font-size: 0.75rem;
            color: $gray-500;
          }
        }
      }
    }
  }
  
  .main-content {
    flex: 1;
    margin-left: 250px;
    transition: margin-left 0.3s ease;
    
    @media (max-width: 768px) {
      margin-left: 0;
    }
    
    .header {
      background-color: $white;
      padding: 1rem;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
      display: flex;
      justify-content: space-between;
      align-items: center;
      position: sticky;
      top: 0;
      z-index: 5;
      
      .header-left {
        display: flex;
        align-items: center;
        gap: 1rem;
        
        .menu-toggle {
          background: none;
          border: none;
          font-size: 1.25rem;
          color: $gray-700;
          cursor: pointer;
          display: none;
          
          @media (max-width: 768px) {
            display: block;
          }
        }
        
        .page-title {
          font-size: 1.25rem;
          font-weight: 600;
          color: $gray-900;
          
          @media (max-width: 768px) {
            font-size: 1rem;
          }
        }
      }
      
      .header-right {
        display: flex;
        align-items: center;
        gap: 1rem;
        
        .header-action {
          background: none;
          border: none;
          color: $gray-700;
          font-size: 1.25rem;
          cursor: pointer;
          position: relative;
          padding: 0.5rem;
          border-radius: 0.25rem;
          transition: all 0.2s ease;
          
          &:hover {
            background-color: $gray-100;
            color: $primary;
          }
          
          .badge {
            position: absolute;
            top: 0;
            right: 0;
            width: 0.75rem;
            height: 0.75rem;
            background-color: $danger;
            border-radius: 50%;
          }
        }
        
        .theme-toggle {
          background: none;
          border: none;
          color: $gray-700;
          font-size: 1.25rem;
          cursor: pointer;
          padding: 0.5rem;
          border-radius: 0.25rem;
          transition: all 0.2s ease;
          
          &:hover {
            background-color: $gray-100;
            color: $primary;
          }
        }
      }
    }
    
    .content {
      padding: 1.5rem;
      
      @media (max-width: 768px) {
        padding: 1rem;
      }
    }
  }
}

// 深色模式支持
body.dark-mode {
  .dashboard {
    background-color: #1f2937;
    
    .sidebar {
      background-color: #111827;
      box-shadow: 1px 0 3px rgba(0, 0, 0, 0.3);
      
      .sidebar-header {
        border-bottom-color: #374151;
      }
      
      .sidebar-nav {
        .nav-section {
          .section-title {
            color: #6b7280;
          }
          
          .nav-item {
            a {
              color: #d1d5db;
              
              &:hover {
                background-color: #374151;
              }
              
              &.active {
                background-color: rgba(59, 130, 246, 0.2);
              }
            }
          }
        }
      }
      
      .sidebar-footer {
        border-top-color: #374151;
        
        .user-info {
          .user-name {
            color: #f9fafb;
          }
          
          .user-role {
            color: #9ca3af;
          }
        }
      }
    }
    
    .main-content {
      .header {
        background-color: #111827;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
        
        .header-left {
          .page-title {
            color: #f9fafb;
          }
        }
        
        .header-right {
          .header-action {
            color: #d1d5db;
            
            &:hover {
              background-color: #374151;
            }
          }
          
          .theme-toggle {
            color: #d1d5db;
            
            &:hover {
              background-color: #374151;
            }
          }
        }
      }
    }
  }
}
```

### 10.4.3 数据卡片组件

Dashboard通常包含数据卡片来展示关键指标：

```scss
.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
  
  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
  
  .stat-card {
    background-color: $white;
    border-radius: 0.5rem;
    padding: 1.5rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    display: flex;
    align-items: center;
    gap: 1rem;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    
    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .stat-icon {
      width: 3.5rem;
      height: 3.5rem;
      border-radius: 0.5rem;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.5rem;
      flex-shrink: 0;
      
      &.primary {
        background-color: rgba(59, 130, 246, 0.1);
        color: $primary;
      }
      
      &.secondary {
        background-color: rgba(249, 115, 22, 0.1);
        color: $secondary;
      }
      
      &.success {
        background-color: rgba(16, 185, 129, 0.1);
        color: $success;
      }
      
      &.warning {
        background-color: rgba(251, 191, 36, 0.1);
        color: $warning;
      }
    }
    
    .stat-content {
      flex: 1;
      
      .stat-value {
        font-size: 1.875rem;
        font-weight: 700;
        color: $gray-900;
        margin-bottom: 0.25rem;
      }
      
      .stat-label {
        font-size: 0.875rem;
        color: $gray-500;
        margin-bottom: 0.5rem;
      }
      
      .stat-change {
        display: flex;
        align-items: center;
        gap: 0.25rem;
        font-size: 0.75rem;
        font-weight: 600;
        
        &.positive {
          color: $success;
        }
        
        &.negative {
          color: $danger;
        }
      }
    }
  }
}

// 深色模式样式
body.dark-mode {
  .stats-cards {
    .stat-card {
      background-color: #111827;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
      
      &:hover {
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.4);
      }
      
      .stat-content {
        .stat-value {
          color: #f9fafb;
        }
        
        .stat-label {
          color: #9ca3af;
        }
      }
    }
  }
}
```

### 10.4.4 表格组件实现

数据表格需要支持排序、筛选和分页功能：

```scss
.data-table {
  background-color: $white;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  
  .table-header {
    padding: 1rem 1.5rem;
    border-bottom: 1px solid $gray-200;
    display: flex;
    justify-content: space-between;
    align-items: center;
    
    h3 {
      font-size: 1.125rem;
      font-weight: 600;
      color: $gray-900;
      margin: 0;
    }
    
    .table-actions {
      display: flex;
      gap: 0.75rem;
      
      .search-box {
        position: relative;
        
        input {
          padding: 0.5rem 0.75rem 0.5rem 2rem;
          border: 1px solid $gray-300;
          border-radius: 0.25rem;
          font-size: 0.875rem;
          width: 15rem;
          
          &:focus {
            outline: none;
            border-color: $primary;
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
          }
        }
        
        .search-icon {
          position: absolute;
          left: 0.75rem;
          top: 50%;
          transform: translateY(-50%);
          color: $gray-400;
          font-size: 0.875rem;
        }
      }
      
      .filter-btn {
        background-color: $white;
        border: 1px solid $gray-300;
        padding: 0.5rem 0.75rem;
        border-radius: 0.25rem;
        font-size: 0.875rem;
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        transition: all 0.2s ease;
        
        &:hover {
          border-color: $primary;
          color: $primary;
        }
      }
    }
  }
  
  .table-wrapper {
    overflow-x: auto;
    
    table {
      width: 100%;
      border-collapse: collapse;
      
      thead {
        background-color: $gray-50;
        
        th {
          padding: 1rem 1.5rem;
          text-align: left;
          font-size: 0.875rem;
          font-weight: 600;
          color: $gray-600;
          text-transform: uppercase;
          letter-spacing: 0.05em;
          border-bottom: 1px solid $gray-200;
          white-space: nowrap;
          
          &.sortable {
            cursor: pointer;
            user-select: none;
            position: relative;
            padding-right: 2rem;
            
            &::after {
              content: '\f0dc';
              font-family: 'Font Awesome 5 Free';
              font-weight: 900;
              position: absolute;
              right: 1.5rem;
              top: 50%;
              transform: translateY(-50%);
              color: $gray-400;
              font-size: 0.75rem;
            }
            
            &.sorted-asc::after {
              content: '\f0de';
              color: $primary;
            }
            
            &.sorted-desc::after {
              content: '\f0dd';
              color: $primary;
            }
            
            &:hover::after {
              color: $gray-600;
            }
          }
        }
      }
      
      tbody {
        
        tr {
          transition: background-color 0.2s ease;
          
          &:hover {
            background-color: $gray-50;
          }
          
          &:nth-child(even) {
            background-color: $gray-50;
            
            &:hover {
              background-color: #f3f4f6;
            }
          }
          
          td {
            padding: 1rem 1.5rem;
            font-size: 0.875rem;
            color: $gray-700;
            border-bottom: 1px solid $gray-200;
            vertical-align: middle;
            
            &.status {
              
              span {
                padding: 0.25rem 0.5rem;
                border-radius: 9999px;
                font-size: 0.75rem;
                font-weight: 600;
                
                &.status-active {
                  background-color: rgba(16, 185, 129, 0.1);
                  color: $success;
                }
                
                &.status-pending {
                  background-color: rgba(251, 191, 36, 0.1);
                  color: $warning;
                }
                
                &.status-inactive {
                  background-color: rgba(107, 114, 128, 0.1);
                  color: $gray-600;
                }
              }
            }
            
            &.actions {
              white-space: nowrap;
              
              .action-btn {
                background: none;
                border: none;
                padding: 0.25rem 0.5rem;
                color: $gray-500;
                cursor: pointer;
                border-radius: 0.25rem;
                transition: all 0.2s ease;
                
                &:hover {
                  color: $primary;
                }
                
                &.edit:hover {
                  color: $primary;
                }
                
                &.delete:hover {
                  color: $danger;
                }
              }
            }
          }
        }
        
        .empty-row {
          
          td {
            text-align: center;
            padding: 3rem;
            color: $gray-500;
            font-style: italic;
          }
        }
      }
    }
  }
  
  .table-footer {
    padding: 1rem 1.5rem;
    border-top: 1px solid $gray-200;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.875rem;
    color: $gray-600;
    
    .pagination {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      
      button {
        width: 2rem;
        height: 2rem;
        display: flex;
        align-items: center;
        justify-content: center;
        border: 1px solid $gray-300;
        background-color: $white;
        border-radius: 0.25rem;
        cursor: pointer;
        font-size: 0.875rem;
        transition: all 0.2s ease;
        
        &:hover:not(:disabled) {
          border-color: $primary;
          color: $primary;
        }
        
        &:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }
        
        &.active {
          background-color: $primary;
          color: $white;
          border-color: $primary;
        }
      }
    }
  }
}

// 深色模式样式
body.dark-mode {
  .data-table {
    background-color: #111827;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
    
    .table-header {
      border-bottom-color: #374151;
      
      h3 {
        color: #f9fafb;
      }
      
      .table-actions {
        .search-box {
          input {
            background-color: #374151;
            border-color: #4b5563;
            color: #f9fafb;
            
            &::placeholder {
              color: #9ca3af;
            }
            
            &:focus {
              border-color: $primary;
              box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
            }
          }
          
          .search-icon {
            color: #9ca3af;
          }
        }
        
        .filter-btn {
          background-color: #374151;
          border-color: #4b5563;
          color: #d1d5db;
        }
      }
    }
    
    .table-wrapper {
      table {
        thead {
          background-color: #1f2937;
          
          th {
            border-bottom-color: #374151;
            color: #9ca3af;
          }
        }
        
        tbody {
          tr {
            &:hover {
              background-color: #1f2937;
            }
            
            &:nth-child(even) {
              background-color: #1f2937;
              
              &:hover {
                background-color: #374151;
              }
            }
            
            td {
              border-bottom-color: #374151;
              color: #d1d5db;
            }
          }
          
          .empty-row {
            td {
              color: #9ca3af;
            }
          }
        }
      }
    }
    
    .table-footer {
      border-top-color: #374151;
      color: #9ca3af;
      
      .pagination {
        button {
          background-color: #374151;
          border-color: #4b5563;
          color: #d1d5db;
        }
      }
    }
  }
}
```

## 10.5 移动端优先设计实战

随着移动设备的普及，移动端优先设计已成为现代Web开发的标准方法。我们将通过一个移动端优先的应用案例，展示如何设计和实现响应式界面。

### 10.5.1 设计原则

- **内容优先**：确保核心内容在小屏幕上清晰可见
- **渐进增强**：从基本功能开始，然后为大屏幕添加增强功能
- **触摸友好**：确保按钮和可交互元素足够大，适合触摸操作
- **性能优化**：优化移动设备上的加载速度和渲染性能
- **简化导航**：在小屏幕上使用汉堡菜单或底部导航栏

### 10.5.2 视口设置

```html
\u003cmeta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no"\u003e
```

### 10.5.3 基础样式重置

为移动设备优化的基础样式重置：

```scss
// 移动优先的基础样式重置
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

html {
  font-size: 16px;
  -webkit-text-size-adjust: 100%; // 防止iOS缩放文本
  scroll-behavior: smooth;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  line-height: 1.5;
  color: #333;
  background-color: #fff;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  overflow-x: hidden; // 防止横向滚动
}

// 触摸优化
button, a {
  -webkit-tap-highlight-color: transparent; // 移除iOS触摸高亮
}

// 图像响应式
img {
  max-width: 100%;
  height: auto;
}

// 表单元素样式
input, button, textarea, select {
  font-family: inherit;
  font-size: 1rem;
}

// 滚动优化
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
}

::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: #555;
}
```

### 10.5.4 移动端导航实现

底部导航栏是移动应用中常见的导航模式：

```scss
// 底部导航栏（仅在移动设备显示）
.mobile-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 3.5rem;
  background-color: $white;
  box-shadow: 0 -1px 3px rgba(0, 0, 0, 0.1);
  display: flex;
  justify-content: space-around;
  align-items: center;
  z-index: 100;
  padding-bottom: env(safe-area-inset-bottom); // 适配iPhone刘海屏
  
  @media (min-width: 768px) {
    display: none;
  }
  
  .nav-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    flex: 1;
    color: $gray-500;
    text-decoration: none;
    font-size: 0.75rem;
    padding: 0.25rem 0;
    
    .nav-icon {
      font-size: 1.25rem;
      margin-bottom: 0.25rem;
    }
    
    &.active {
      color: $primary;
      font-weight: 600;
    }
  }
}

// 确保内容不被底部导航栏遮挡
body {
  padding-bottom: 3.5rem;
  
  @media (min-width: 768px) {
    padding-bottom: 0;
  }
}
```

### 10.5.5 响应式卡片网格

在移动设备上单列显示，在大屏幕上多列显示：

```scss
.card-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
  padding: 1rem;
  
  // 平板设备
  @media (min-width: 768px) {
    grid-template-columns: repeat(2, 1fr);
    gap: 1.5rem;
    padding: 1.5rem;
  }
  
  // 桌面设备
  @media (min-width: 1200px) {
    grid-template-columns: repeat(3, 1fr);
    gap: 2rem;
    padding: 2rem;
    max-width: 1400px;
    margin: 0 auto;
  }
  
  .card {
    background-color: $white;
    border-radius: 0.5rem;
    overflow: hidden;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    
    &:hover {
      transform: translateY(-4px);
      box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
    }
    
    .card-image {
      position: relative;
      padding-top: 75%; // 4:3 比例
      overflow: hidden;
      
      img