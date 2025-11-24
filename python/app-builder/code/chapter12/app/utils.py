import logging
from functools import wraps

# 创建专用的日志记录器
logger = logging.getLogger('app.utils')

def validate_product_data(func):
    """产品数据验证装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # 验证参数
        if 'price' in kwargs and kwargs['price'] < 0:
            raise ValueError("Price cannot be negative")
        
        return func(*args, **kwargs)
    return wrapper

def calculate_total_price(products):
    """计算产品总价"""
    logger.debug(f"Calculating total price for {len(products)} products")
    total = sum(product.price for product in products)
    logger.debug(f"Total price calculated: {total}")
    return total