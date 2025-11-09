import React from 'react'

/**
 * 产品列表组件 - 展示如何遍历和渲染数组数据
 * 
 * @param {Object} props - 组件属性
 * @param {Array} props.products - 产品数组
 */
function ProductList({ products }) {
  // 检查products是否存在且为数组
  if (!Array.isArray(products) || products.length === 0) {
    return (
      <div className="no-products">
        <p>暂无产品数据</p>
      </div>
    )
  }

  return (
    <div className="product-list">
      {products.map(product => (
        // 重要：列表项必须有唯一的key属性
        <div key={product.id} className="product-item">
          <div className="product-header">
            <h3 className="product-name">{product.name}</h3>
            <span className="product-price">¥{product.price.toFixed(2)}</span>
          </div>
          <div className="product-body">
            <p className="product-description">{product.description}</p>
          </div>
          <div className="product-footer">
            <button className="btn add-to-cart-btn">
              加入购物车
            </button>
          </div>
        </div>
      ))}
    </div>
  )
}

export default ProductList
