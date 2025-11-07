# 第5章示例代码：OpenTelemetry实战应用

## 1. 微服务架构中的分布式追踪

### 1.1 API网关服务

```python
# api_gateway.py
"""
API网关服务示例
演示如何在API网关中实现OpenTelemetry追踪
"""

from flask import Flask, request, jsonify
import requests
import time
import random
from opentelemetry import trace, baggage, context
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.propagate import inject, extract

app = Flask(__name__)

# 设置资源
resource = Resource.create({
    "service.name": "api-gateway",
    "service.version": "1.0.0",
    "service.namespace": "ecommerce",
    "deployment.environment": "development"
})

# 设置追踪提供者
trace.set_tracer_provider(TracerProvider(resource=resource))
tracer = trace.get_tracer(__name__)

# 配置导出器
otlp_exporter = OTLPSpanExporter(
    endpoint="http://localhost:4317",
    insecure=True
)

span_processor = BatchSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# 自动instrument Flask和requests
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()

# 服务发现
services = {
    "user": "http://localhost:5001",
    "product": "http://localhost:5002",
    "order": "http://localhost:5003",
    "payment": "http://localhost:5004"
}

@app.route('/health')
def health_check():
    """健康检查端点"""
    return jsonify({"status": "healthy"})

@app.route('/api/users/<user_id>')
def get_user(user_id):
    """获取用户信息"""
    headers = {}
    inject(headers)  # 注入追踪上下文
    
    try:
        response = requests.get(
            f"{services['user']}/users/{user_id}",
            headers=headers,
            timeout=5
        )
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/products')
def get_products():
    """获取产品列表"""
    headers = {}
    inject(headers)  # 注入追踪上下文
    
    try:
        response = requests.get(
            f"{services['product']}/products",
            headers=headers,
            timeout=5
        )
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/orders', methods=['POST'])
def create_order():
    """创建订单"""
    data = request.get_json()
    user_id = data.get('user_id')
    items = data.get('items', [])
    
    headers = {}
    inject(headers)  # 注入追踪上下文
    
    # 验证用户
    try:
        user_response = requests.get(
            f"{services['user']}/users/{user_id}",
            headers=headers,
            timeout=5
        )
        if user_response.status_code != 200:
            return jsonify({"error": "Invalid user"}), 400
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500
    
    # 验证产品
    for item in items:
        try:
            product_response = requests.get(
                f"{services['product']}/products/{item['product_id']}",
                headers=headers,
                timeout=5
            )
            if product_response.status_code != 200:
                return jsonify({"error": f"Invalid product: {item['product_id']}"}), 400
        except requests.exceptions.RequestException as e:
            return jsonify({"error": str(e)}), 500
    
    # 创建订单
    try:
        order_response = requests.post(
            f"{services['order']}/orders",
            json={
                "user_id": user_id,
                "items": items
            },
            headers=headers,
            timeout=5
        )
        
        if order_response.status_code != 201:
            return jsonify(order_response.json()), order_response.status_code
            
        order_data = order_response.json()
        
        # 处理支付
        payment_response = requests.post(
            f"{services['payment']}/payments",
            json={
                "order_id": order_data['order_id'],
                "amount": order_data['total_amount']
            },
            headers=headers,
            timeout=5
        )
        
        if payment_response.status_code != 201:
            return jsonify(payment_response.json()), payment_response.status_code
            
        return jsonify({
            "order": order_data,
            "payment": payment_response.json()
        }), 201
        
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
```

### 1.2 用户服务

```python
# user_service.py
"""
用户服务示例
演示如何在微服务中实现OpenTelemetry追踪
"""

from flask import Flask, request, jsonify
import time
import random
import sqlite3
from opentelemetry import trace, baggage, context
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.sqlite3 import SQLite3Instrumentor

app = Flask(__name__)

# 设置资源
resource = Resource.create({
    "service.name": "user-service",
    "service.version": "1.0.0",
    "service.namespace": "ecommerce",
    "deployment.environment": "development"
})

# 设置追踪提供者
trace.set_tracer_provider(TracerProvider(resource=resource))
tracer = trace.get_tracer(__name__)

# 配置导出器
otlp_exporter = OTLPSpanExporter(
    endpoint="http://localhost:4317",
    insecure=True
)

span_processor = BatchSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# 自动instrument Flask和sqlite3
FlaskInstrumentor().instrument_app(app)
SQLite3Instrumentor().instrument()

# 初始化数据库
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            address TEXT
        )
    ''')
    
    # 插入示例数据
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    if count == 0:
        users = [
            (1, "Alice", "alice@example.com", "123 Main St"),
            (2, "Bob", "bob@example.com", "456 Oak Ave"),
            (3, "Charlie", "charlie@example.com", "789 Pine Rd")
        ]
        cursor.executemany("INSERT INTO users VALUES (?, ?, ?, ?)", users)
    
    conn.commit()
    conn.close()

init_db()

@app.route('/health')
def health_check():
    """健康检查端点"""
    return jsonify({"status": "healthy"})

@app.route('/users/<int:user_id>')
def get_user(user_id):
    """获取用户信息"""
    with tracer.start_as_current_span("database.query") as span:
        span.set_attribute("db.system", "sqlite")
        span.set_attribute("db.operation", "SELECT")
        span.set_attribute("db.statement", f"SELECT * FROM users WHERE id = {user_id}")
        
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            span.set_attribute("db.rows_affected", 1)
            return jsonify({
                "id": user[0],
                "name": user[1],
                "email": user[2],
                "address": user[3]
            })
        else:
            span.set_attribute("db.rows_affected", 0)
            return jsonify({"error": "User not found"}), 404

@app.route('/users', methods=['POST'])
def create_user():
    """创建用户"""
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    address = data.get('address', '')
    
    with tracer.start_as_current_span("database.insert") as span:
        span.set_attribute("db.system", "sqlite")
        span.set_attribute("db.operation", "INSERT")
        
        try:
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (name, email, address) VALUES (?, ?, ?)",
                (name, email, address)
            )
            user_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            span.set_attribute("db.rows_affected", 1)
            return jsonify({
                "id": user_id,
                "name": name,
                "email": email,
                "address": address
            }), 201
        except sqlite3.IntegrityError:
            span.set_attribute("db.error", "IntegrityError")
            return jsonify({"error": "Email already exists"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
```

### 1.3 产品服务

```python
# product_service.py
"""
产品服务示例
演示如何在微服务中实现OpenTelemetry追踪和指标
"""

from flask import Flask, request, jsonify
import time
import random
import sqlite3
from opentelemetry import trace, metrics
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.sqlite3 import SQLite3Instrumentor

app = Flask(__name__)

# 设置资源
resource = Resource.create({
    "service.name": "product-service",
    "service.version": "1.0.0",
    "service.namespace": "ecommerce",
    "deployment.environment": "development"
})

# 设置追踪提供者
trace.set_tracer_provider(TracerProvider(resource=resource))
tracer = trace.get_tracer(__name__)

# 配置追踪导出器
otlp_trace_exporter = OTLPSpanExporter(
    endpoint="http://localhost:4317",
    insecure=True
)

span_processor = BatchSpanProcessor(otlp_trace_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# 设置指标提供者
metric_reader = PeriodicExportingMetricReader(
    exporter=OTLPMetricExporter(
        endpoint="http://localhost:4317",
        insecure=True
    ),
    export_interval_millis=30000
)

metrics.set_meter_provider(MeterProvider(resource=resource, metric_readers=[metric_reader]))
meter = metrics.get_meter(__name__)

# 创建指标
product_views_counter = meter.create_counter(
    "product_views_total",
    description="Total number of product views"
)

search_counter = meter.create_counter(
    "product_searches_total",
    description="Total number of product searches"
)

response_time_histogram = meter.create_histogram(
    "product_service_response_time_seconds",
    description="Response time of product service in seconds"
)

# 自动instrument Flask和sqlite3
FlaskInstrumentor().instrument_app(app)
SQLite3Instrumentor().instrument()

# 初始化数据库
def init_db():
    conn = sqlite3.connect('products.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            stock INTEGER NOT NULL
        )
    ''')
    
    # 插入示例数据
    cursor.execute("SELECT COUNT(*) FROM products")
    count = cursor.fetchone()[0]
    if count == 0:
        products = [
            (1, "Laptop", "High-performance laptop", 999.99, 50),
            (2, "Smartphone", "Latest smartphone model", 699.99, 100),
            (3, "Headphones", "Noise-cancelling headphones", 199.99, 200),
            (4, "Tablet", "10-inch tablet", 399.99, 75),
            (5, "Smartwatch", "Fitness tracking smartwatch", 249.99, 150)
        ]
        cursor.executemany("INSERT INTO products VALUES (?, ?, ?, ?, ?)", products)
    
    conn.commit()
    conn.close()

init_db()

@app.route('/health')
def health_check():
    """健康检查端点"""
    return jsonify({"status": "healthy"})

@app.route('/products')
def get_products():
    """获取产品列表"""
    start_time = time.time()
    
    with tracer.start_as_current_span("database.query") as span:
        span.set_attribute("db.system", "sqlite")
        span.set_attribute("db.operation", "SELECT")
        
        conn = sqlite3.connect('products.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products")
        products = cursor.fetchall()
        conn.close()
        
        span.set_attribute("db.rows_affected", len(products))
        
        result = []
        for product in products:
            result.append({
                "id": product[0],
                "name": product[1],
                "description": product[2],
                "price": product[3],
                "stock": product[4]
            })
    
    # 记录响应时间
    response_time = time.time() - start_time
    response_time_histogram.record(response_time)
    
    return jsonify(result)

@app.route('/products/<int:product_id>')
def get_product(product_id):
    """获取单个产品信息"""
    start_time = time.time()
    
    with tracer.start_as_current_span("database.query") as span:
        span.set_attribute("db.system", "sqlite")
        span.set_attribute("db.operation", "SELECT")
        span.set_attribute("product.id", product_id)
        
        conn = sqlite3.connect('products.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
        product = cursor.fetchone()
        conn.close()
        
        if product:
            span.set_attribute("db.rows_affected", 1)
            
            # 记录产品浏览指标
            product_views_counter.add(1, {"product_id": str(product_id)})
            
            result = {
                "id": product[0],
                "name": product[1],
                "description": product[2],
                "price": product[3],
                "stock": product[4]
            }
            
            # 记录响应时间
            response_time = time.time() - start_time
            response_time_histogram.record(response_time)
            
            return jsonify(result)
        else:
            span.set_attribute("db.rows_affected", 0)
            return jsonify({"error": "Product not found"}), 404

@app.route('/products/search')
def search_products():
    """搜索产品"""
    start_time = time.time()
    query = request.args.get('q', '')
    
    with tracer.start_as_current_span("database.search") as span:
        span.set_attribute("db.system", "sqlite")
        span.set_attribute("db.operation", "SELECT")
        span.set_attribute("search.query", query)
        
        conn = sqlite3.connect('products.db')
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM products WHERE name LIKE ? OR description LIKE ?",
            (f'%{query}%', f'%{query}%')
        )
        products = cursor.fetchall()
        conn.close()
        
        span.set_attribute("db.rows_affected", len(products))
        
        # 记录搜索指标
        search_counter.add(1, {"query": query})
        
        result = []
        for product in products:
            result.append({
                "id": product[0],
                "name": product[1],
                "description": product[2],
                "price": product[3],
                "stock": product[4]
            })
    
    # 记录响应时间
    response_time = time.time() - start_time
    response_time_histogram.record(response_time)
    
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)
```

### 1.4 订单服务

```python
# order_service.py
"""
订单服务示例
演示如何在微服务中实现OpenTelemetry追踪、指标和日志
"""

from flask import Flask, request, jsonify
import time
import random
import sqlite3
import logging
from opentelemetry import trace, metrics, logs
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk.logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.sqlite3 import SQLite3Instrumentor
from opentelemetry._logs import set_logger_provider

app = Flask(__name__)

# 设置资源
resource = Resource.create({
    "service.name": "order-service",
    "service.version": "1.0.0",
    "service.namespace": "ecommerce",
    "deployment.environment": "development"
})

# 设置追踪提供者
trace.set_tracer_provider(TracerProvider(resource=resource))
tracer = trace.get_tracer(__name__)

# 配置追踪导出器
otlp_trace_exporter = OTLPSpanExporter(
    endpoint="http://localhost:4317",
    insecure=True
)

span_processor = BatchSpanProcessor(otlp_trace_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# 设置指标提供者
metric_reader = PeriodicExportingMetricReader(
    exporter=OTLPMetricExporter(
        endpoint="http://localhost:4317",
        insecure=True
    ),
    export_interval_millis=30000
)

metrics.set_meter_provider(MeterProvider(resource=resource, metric_readers=[metric_reader]))
meter = metrics.get_meter(__name__)

# 设置日志提供者
logger_provider = LoggerProvider(resource=resource)
set_logger_provider(logger_provider)

otlp_log_exporter = OTLPLogExporter(
    endpoint="http://localhost:4317",
    insecure=True
)

logger_provider.add_log_record_processor(BatchLogRecordProcessor(otlp_log_exporter))

# 配置Python日志
handler = LoggingHandler(level=logging.NOTSET, logger_provider=logger_provider)
logging.basicConfig(level=logging.NOTSET)
logger = logging.getLogger(__name__)
logger.addHandler(handler)

# 创建指标
orders_created_counter = meter.create_counter(
    "orders_created_total",
    description="Total number of orders created"
)

order_amount_histogram = meter.create_histogram(
    "order_amount_dollars",
    description="Order amount in dollars"
)

# 自动instrument Flask和sqlite3
FlaskInstrumentor().instrument_app(app)
SQLite3Instrumentor().instrument()

# 初始化数据库
def init_db():
    conn = sqlite3.connect('orders.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            status TEXT NOT NULL,
            total_amount REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY,
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders (id)
        )
    ''')
    
    conn.commit()
    conn.close()

init_db()

@app.route('/health')
def health_check():
    """健康检查端点"""
    return jsonify({"status": "healthy"})

@app.route('/orders', methods=['POST'])
def create_order():
    """创建订单"""
    data = request.get_json()
    user_id = data.get('user_id')
    items = data.get('items', [])
    
    with tracer.start_as_current_span("create_order") as span:
        span.set_attribute("order.user_id", user_id)
        span.set_attribute("order.items_count", len(items))
        
        logger.info(f"Creating order for user {user_id} with {len(items)} items")
        
        # 计算总金额
        total_amount = 0.0
        for item in items:
            total_amount += item.get('price', 0) * item.get('quantity', 1)
        
        span.set_attribute("order.total_amount", total_amount)
        
        with tracer.start_as_current_span("database.transaction") as db_span:
            db_span.set_attribute("db.system", "sqlite")
            
            try:
                conn = sqlite3.connect('orders.db')
                cursor = conn.cursor()
                
                # 插入订单
                cursor.execute(
                    "INSERT INTO orders (user_id, status, total_amount) VALUES (?, ?, ?)",
                    (user_id, "pending", total_amount)
                )
                order_id = cursor.lastrowid
                
                db_span.set_attribute("order.id", order_id)
                
                # 插入订单项
                for item in items:
                    cursor.execute(
                        "INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (?, ?, ?, ?)",
                        (order_id, item.get('product_id'), item.get('quantity', 1), item.get('price', 0))
                    )
                
                conn.commit()
                conn.close()
                
                # 记录指标
                orders_created_counter.add(1, {"status": "pending"})
                order_amount_histogram.record(total_amount)
                
                logger.info(f"Order {order_id} created successfully for user {user_id}")
                
                return jsonify({
                    "order_id": order_id,
                    "user_id": user_id,
                    "status": "pending",
                    "total_amount": total_amount,
                    "items": items
                }), 201
                
            except Exception as e:
                logger.error(f"Failed to create order for user {user_id}: {str(e)}")
                db_span.set_attribute("db.error", str(e))
                return jsonify({"error": str(e)}), 500

@app.route('/orders/<int:order_id>')
def get_order(order_id):
    """获取订单信息"""
    with tracer.start_as_current_span("get_order") as span:
        span.set_attribute("order.id", order_id)
        
        logger.info(f"Retrieving order {order_id}")
        
        with tracer.start_as_current_span("database.query") as db_span:
            db_span.set_attribute("db.system", "sqlite")
            db_span.set_attribute("db.operation", "SELECT")
            
            conn = sqlite3.connect('orders.db')
            cursor = conn.cursor()
            
            # 获取订单
            cursor.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
            order = cursor.fetchone()
            
            if not order:
                logger.warning(f"Order {order_id} not found")
                return jsonify({"error": "Order not found"}), 404
            
            # 获取订单项
            cursor.execute("SELECT * FROM order_items WHERE order_id = ?", (order_id,))
            items = cursor.fetchall()
            
            conn.close()
            
            order_items = []
            for item in items:
                order_items.append({
                    "product_id": item[2],
                    "quantity": item[3],
                    "price": item[4]
                })
            
            result = {
                "order_id": order[0],
                "user_id": order[1],
                "status": order[2],
                "total_amount": order[3],
                "created_at": order[4],
                "items": order_items
            }
            
            logger.info(f"Order {order_id} retrieved successfully")
            return jsonify(result)

@app.route('/orders/<int:order_id>/status', methods=['PUT'])
def update_order_status(order_id):
    """更新订单状态"""
    data = request.get_json()
    status = data.get('status')
    
    with tracer.start_as_current_span("update_order_status") as span:
        span.set_attribute("order.id", order_id)
        span.set_attribute("order.status", status)
        
        logger.info(f"Updating order {order_id} status to {status}")
        
        with tracer.start_as_current_span("database.update") as db_span:
            db_span.set_attribute("db.system", "sqlite")
            db_span.set_attribute("db.operation", "UPDATE")
            
            try:
                conn = sqlite3.connect('orders.db')
                cursor = conn.cursor()
                
                cursor.execute(
                    "UPDATE orders SET status = ? WHERE id = ?",
                    (status, order_id)
                )
                
                if cursor.rowcount == 0:
                    logger.warning(f"Order {order_id} not found for status update")
                    return jsonify({"error": "Order not found"}), 404
                
                conn.commit()
                conn.close()
                
                # 记录指标
                orders_created_counter.add(1, {"status": status})
                
                logger.info(f"Order {order_id} status updated to {status}")
                return jsonify({"order_id": order_id, "status": status})
                
            except Exception as e:
                logger.error(f"Failed to update order {order_id} status: {str(e)}")
                db_span.set_attribute("db.error", str(e))
                return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=True)
```

### 1.5 支付服务

```python
# payment_service.py
"""
支付服务示例
演示如何在微服务中实现OpenTelemetry追踪、指标和日志
"""

from flask import Flask, request, jsonify
import time
import random
import sqlite3
import logging
from opentelemetry import trace, metrics, logs
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk.logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.sqlite3 import SQLite3Instrumentor
from opentelemetry._logs import set_logger_provider

app = Flask(__name__)

# 设置资源
resource = Resource.create({
    "service.name": "payment-service",
    "service.version": "1.0.0",
    "service.namespace": "ecommerce",
    "deployment.environment": "development"
})

# 设置追踪提供者
trace.set_tracer_provider(TracerProvider(resource=resource))
tracer = trace.get_tracer(__name__)

# 配置追踪导出器
otlp_trace_exporter = OTLPSpanExporter(
    endpoint="http://localhost:4317",
    insecure=True
)

span_processor = BatchSpanProcessor(otlp_trace_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# 设置指标提供者
metric_reader = PeriodicExportingMetricReader(
    exporter=OTLPMetricExporter(
        endpoint="http://localhost:4317",
        insecure=True
    ),
    export_interval_millis=30000
)

metrics.set_meter_provider(MeterProvider(resource=resource, metric_readers=[metric_reader]))
meter = metrics.get_meter(__name__)

# 设置日志提供者
logger_provider = LoggerProvider(resource=resource)
set_logger_provider(logger_provider)

otlp_log_exporter = OTLPLogExporter(
    endpoint="http://localhost:4317",
    insecure=True
)

logger_provider.add_log_record_processor(BatchLogRecordProcessor(otlp_log_exporter))

# 配置Python日志
handler = LoggingHandler(level=logging.NOTSET, logger_provider=logger_provider)
logging.basicConfig(level=logging.NOTSET)
logger = logging.getLogger(__name__)
logger.addHandler(handler)

# 创建指标
payments_created_counter = meter.create_counter(
    "payments_created_total",
    description="Total number of payments created"
)

payment_amount_histogram = meter.create_histogram(
    "payment_amount_dollars",
    description="Payment amount in dollars"
)

payment_processing_time_histogram = meter.create_histogram(
    "payment_processing_time_seconds",
    description="Payment processing time in seconds"
)

# 自动instrument Flask和sqlite3
FlaskInstrumentor().instrument_app(app)
SQLite3Instrumentor().instrument()

# 初始化数据库
def init_db():
    conn = sqlite3.connect('payments.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY,
            order_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            status TEXT NOT NULL,
            payment_method TEXT,
            transaction_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/health')
def health_check():
    """健康检查端点"""
    return jsonify({"status": "healthy"})

@app.route('/payments', methods=['POST'])
def create_payment():
    """创建支付"""
    data = request.get_json()
    order_id = data.get('order_id')
    amount = data.get('amount')
    payment_method = data.get('payment_method', 'credit_card')
    
    start_time = time.time()
    
    with tracer.start_as_current_span("create_payment") as span:
        span.set_attribute("payment.order_id", order_id)
        span.set_attribute("payment.amount", amount)
        span.set_attribute("payment.method", payment_method)
        
        logger.info(f"Creating payment for order {order_id} with amount {amount}")
        
        # 模拟支付处理时间
        processing_time = random.uniform(0.5, 2.0)
        time.sleep(processing_time / 10)  # 加速模拟
        
        # 模拟支付成功率（90%成功）
        success = random.random() < 0.9
        
        with tracer.start_as_current_span("database.transaction") as db_span:
            db_span.set_attribute("db.system", "sqlite")
            
            try:
                conn = sqlite3.connect('payments.db')
                cursor = conn.cursor()
                
                status = "completed" if success else "failed"
                transaction_id = f"txn_{int(time.time())}_{random.randint(1000, 9999)}" if success else None
                
                cursor.execute(
                    "INSERT INTO payments (order_id, amount, status, payment_method, transaction_id) VALUES (?, ?, ?, ?, ?)",
                    (order_id, amount, status, payment_method, transaction_id)
                )
                
                payment_id = cursor.lastrowid
                conn.commit()
                conn.close()
                
                # 记录处理时间
                actual_processing_time = time.time() - start_time
                payment_processing_time_histogram.record(actual_processing_time)
                
                if success:
                    # 记录指标
                    payments_created_counter.add(1, {"status": "completed", "method": payment_method})
                    payment_amount_histogram.record(amount, {"status": "completed", "method": payment_method})
                    
                    logger.info(f"Payment {payment_id} for order {order_id} completed successfully")
                    
                    return jsonify({
                        "payment_id": payment_id,
                        "order_id": order_id,
                        "amount": amount,
                        "status": status,
                        "payment_method": payment_method,
                        "transaction_id": transaction_id
                    }), 201
                else:
                    # 记录指标
                    payments_created_counter.add(1, {"status": "failed", "method": payment_method})
                    
                    logger.warning(f"Payment {payment_id} for order {order_id} failed")
                    
                    return jsonify({
                        "payment_id": payment_id,
                        "order_id": order_id,
                        "amount": amount,
                        "status": status,
                        "payment_method": payment_method,
                        "error": "Payment processing failed"
                    }), 400
                    
            except Exception as e:
                logger.error(f"Failed to create payment for order {order_id}: {str(e)}")
                db_span.set_attribute("db.error", str(e))
                return jsonify({"error": str(e)}), 500

@app.route('/payments/<int:payment_id>')
def get_payment(payment_id):
    """获取支付信息"""
    with tracer.start_as_current_span("get_payment") as span:
        span.set_attribute("payment.id", payment_id)
        
        logger.info(f"Retrieving payment {payment_id}")
        
        with tracer.start_as_current_span("database.query") as db_span:
            db_span.set_attribute("db.system", "sqlite")
            db_span.set_attribute("db.operation", "SELECT")
            
            conn = sqlite3.connect('payments.db')
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM payments WHERE id = ?", (payment_id,))
            payment = cursor.fetchone()
            
            conn.close()
            
            if payment:
                logger.info(f"Payment {payment_id} retrieved successfully")
                return jsonify({
                    "payment_id": payment[0],
                    "order_id": payment[1],
                    "amount": payment[2],
                    "status": payment[3],
                    "payment_method": payment[4],
                    "transaction_id": payment[5],
                    "created_at": payment[6]
                })
            else:
                logger.warning(f"Payment {payment_id} not found")
                return jsonify({"error": "Payment not found"}), 404

@app.route('/payments/<int:payment_id>/refund', methods=['POST'])
def refund_payment(payment_id):
    """退款支付"""
    data = request.get_json()
    amount = data.get('amount')
    
    with tracer.start_as_current_span("refund_payment") as span:
        span.set_attribute("payment.id", payment_id)
        span.set_attribute("payment.refund_amount", amount)
        
        logger.info(f"Processing refund for payment {payment_id} with amount {amount}")
        
        with tracer.start_as_current_span("database.query") as db_span:
            db_span.set_attribute("db.system", "sqlite")
            db_span.set_attribute("db.operation", "SELECT")
            
            conn = sqlite3.connect('payments.db')
            cursor = conn.cursor()
            
            # 获取支付信息
            cursor.execute("SELECT * FROM payments WHERE id = ?", (payment_id,))
            payment = cursor.fetchone()
            
            if not payment:
                logger.warning(f"Payment {payment_id} not found for refund")
                return jsonify({"error": "Payment not found"}), 404
            
            if payment[3] != "completed":
                logger.warning(f"Payment {payment_id} is not completed, cannot refund")
                return jsonify({"error": "Payment is not completed"}), 400
            
            if amount > payment[2]:
                logger.warning(f"Refund amount {amount} exceeds payment amount {payment[2]}")
                return jsonify({"error": "Refund amount exceeds payment amount"}), 400
            
            # 模拟退款处理
            time.sleep(0.5)  # 模拟处理时间
            
            # 更新支付状态
            db_span.set_attribute("db.operation", "UPDATE")
            cursor.execute(
                "UPDATE payments SET status = ? WHERE id = ?",
                ("refunded", payment_id)
            )
            
            conn.commit()
            conn.close()
            
            logger.info(f"Payment {payment_id} refunded successfully")
            return jsonify({
                "payment_id": payment_id,
                "order_id": payment[1],
                "refund_amount": amount,
                "status": "refunded"
            })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004, debug=True)
```

## 2. Kubernetes环境中的OpenTelemetry部署

### 2.1 OpenTelemetry Operator部署

```yaml
# otel-operator.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: observability
---
apiVersion: operators.coreos.com/v1
kind: OperatorGroup
metadata:
  name: observability-operator-group
  namespace: observability
spec:
  targetNamespaces:
    - observability
---
apiVersion: operators.coreos.com/v1alpha1
kind: Subscription
metadata:
  name: opentelemetry-operator
  namespace: observability
spec:
  channel: stable
  name: opentelemetry-operator
  source: community-operators
  sourceNamespace: openshift-marketplace
```

### 2.2 OpenTelemetry Collector部署

```yaml
# otel-collector.yaml
apiVersion: opentelemetry.io/v1alpha1
kind: OpenTelemetryCollector
metadata:
  name: otel
  namespace: observability
spec:
  mode: deployment
  replicas: 2
  resources:
    limits:
      cpu: 200m
      memory: 500Mi
  config: |
    receivers:
      otlp:
        protocols:
          grpc:
            endpoint: 0.0.0.0:4317
          http:
            endpoint: 0.0.0.0:4318
      k8s_cluster:
        auth_type: serviceAccount
        node_condition_types:
          - Ready
          - MemoryPressure
          - DiskPressure
          - PIDPressure
          - NetworkUnavailable
      k8s_events:
        auth_type: serviceAccount
      kubeletstats:
        auth_type: serviceAccount
        endpoint: https://${env:KUBE_NODE_NAME}:10250
        insecure_skip_verify: true
        collection_interval: 20s
        api_version: v1
        metric_groups:
          - node
          - pod
          - container
      prometheus:
        config:
          scrape_configs:
            - job_name: 'kubernetes-pods'
              kubernetes_sd_configs:
                - role: pod
              relabel_configs:
                - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
                  action: keep
                  regex: true
                - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
                  action: replace
                  target_label: __metrics_path__
                  regex: (.+)
                - source_labels: [__address__, __meta_kubernetes_pod_annotation_prometheus_io_port]
                  action: replace
                  regex: ([^:]+)(?::\d+)?;(\d+)
                  replacement: $1:$2
                  target_label: __address__
    
    processors:
      batch:
        timeout: 1s
        send_batch_size: 1024
      memory_limiter:
        limit_mib: 400
      resource:
        attributes:
          - key: k8s.cluster.name
            value: "my-cluster"
            action: upsert
      k8sattributes:
        auth_type: serviceAccount
        extract:
          metadata:
            - k8s.pod.name
            - k8s.pod.uid
            - k8s.deployment.name
            - k8s.namespace.name
            - k8s.node.name
            - k8s.pod.start_time
        pod_association:
          - sources:
              - from: resource_attribute
                name: k8s.pod.uid
              - from: resource_attribute
                name: k8s.pod.ip
          - sources:
              - from: resource_attribute
                name: k8s.pod.name
              - from: resource_attribute
                name: k8s.namespace.name
    
    exporters:
      prometheus:
        endpoint: 0.0.0.0:8889
        namespace: otel
        const_labels:
          environment: production
      logging:
        loglevel: info
      jaeger:
        endpoint: jaeger-collector:14250
        tls:
          insecure: true
      elasticsearch:
        endpoints: ["http://elasticsearch:9200"]
        index: "otel-logs"
        tls:
          insecure: true
    
    service:
      pipelines:
        traces:
          receivers: [otlp, k8s_events]
          processors: [memory_limiter, k8sattributes, resource, batch]
          exporters: [jaeger, logging]
        metrics:
          receivers: [otlp, kubeletstats, k8s_cluster, prometheus]
          processors: [memory_limiter, k8sattributes, resource, batch]
          exporters: [prometheus, logging]
        logs:
          receivers: [otlp, k8s_events]
          processors: [memory_limiter, k8sattributes, resource, batch]
          exporters: [elasticsearch, logging]
      
      extensions: [health_check, pprof, zpages]
---
apiVersion: v1
kind: Service
metadata:
  name: otel-collector
  namespace: observability
  labels:
    app: otel-collector
spec:
  ports:
    - name: otlp-grpc
      port: 4317
      protocol: TCP
      targetPort: 4317
    - name: otlp-http
      port: 4318
      protocol: TCP
      targetPort: 4318
    - name: prometheus
      port: 8889
      protocol: TCP
      targetPort: 8889
    - name: health-check
      port: 13133
      protocol: TCP
      targetPort: 13133
  selector:
    app.kubernetes.io/name: otel-collector
  type: ClusterIP
```

### 2.3 自动注入配置

```yaml
# auto-instrumentation.yaml
apiVersion: opentelemetry.io/v1alpha1
kind: Instrumentation
metadata:
  name: python-instrumentation
  namespace: observability
spec:
  exporter:
    endpoint: http://otel-collector:4317
  propagators:
    - tracecontext
    - baggage
    - b3
  sampler:
    type: parentbased_traceidratio
    argument: "0.25"
  python:
    env:
      - name: OTEL_RESOURCE_ATTRIBUTES
        value: service.name=$(K8S_POD_NAME),service.namespace=$(K8S_NAMESPACE)
      - name: OTEL_EXPORTER_OTLP_ENDPOINT
        value: http://otel-collector:4317
      - name: OTEL_METRICS_EXPORTER
        value: otlp
      - name: OTEL_LOGS_EXPORTER
        value: otlp
---
apiVersion: opentelemetry.io/v1alpha1
kind: Instrumentation
metadata:
  name: java-instrumentation
  namespace: observability
spec:
  exporter:
    endpoint: http://otel-collector:4317
  propagators:
    - tracecontext
    - baggage
    - b3
  sampler:
    type: parentbased_traceidratio
    argument: "0.25"
  java:
    env:
      - name: OTEL_RESOURCE_ATTRIBUTES
        value: service.name=$(K8S_POD_NAME),service.namespace=$(K8S_NAMESPACE)
      - name: OTEL_EXPORTER_OTLP_ENDPOINT
        value: http://otel-collector:4317
      - name: OTEL_METRICS_EXPORTER
        value: otlp
      - name: OTEL_LOGS_EXPORTER
        value: otlp
---
apiVersion: opentelemetry.io/v1alpha1
kind: Instrumentation
metadata:
  name: nodejs-instrumentation
  namespace: observability
spec:
  exporter:
    endpoint: http://otel-collector:4317
  propagators:
    - tracecontext
    - baggage
    - b3
  sampler:
    type: parentbased_traceidratio
    argument: "0.25"
  nodejs:
    env:
      - name: OTEL_RESOURCE_ATTRIBUTES
        value: service.name=$(K8S_POD_NAME),service.namespace=$(K8S_NAMESPACE)
      - name: OTEL_EXPORTER_OTLP_ENDPOINT
        value: http://otel-collector:4317
      - name: OTEL_METRICS_EXPORTER
        value: otlp
      - name: OTEL_LOGS_EXPORTER
        value: otlp
```

### 2.4 示例应用部署

```yaml
# sample-app.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: sample-app
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: sample-app
  namespace: sample-app
  labels:
    app: sample-app
spec:
  replicas: 2
  selector:
    matchLabels:
      app: sample-app
  template:
    metadata:
      labels:
        app: sample-app
      annotations:
        instrumentation.opentelemetry.io/inject-python: "observability/python-instrumentation"
    spec:
      containers:
      - name: app
        image: python:3.9-slim
        command: ["python", "-c", "import time; import random; from opentelemetry import trace; tracer = trace.get_tracer(__name__); while True: with tracer.start_as_current_span('operation'): time.sleep(random.uniform(0.1, 0.5))"]
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 200m
            memory: 256Mi
---
apiVersion: v1
kind: Service
metadata:
  name: sample-app
  namespace: sample-app
  labels:
    app: sample-app
spec:
  ports:
  - port: 8080
    protocol: TCP
    targetPort: 8080
  selector:
    app: sample-app
  type: ClusterIP
```

## 3. 实验代码

### 3.1 实验1：微服务架构中的分布式追踪

```python
# experiment1.py
"""
实验1：微服务架构中的分布式追踪
目标：学习如何在微服务架构中实现分布式追踪
"""

import requests
import time
import json
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.propagate import inject

def setup_tracer():
    """设置追踪器"""
    resource = Resource.create({
        "service.name": "microservices-experiment",
        "service.version": "1.0.0",
        "environment": "experiment"
    })
    
    trace.set_tracer_provider(TracerProvider(resource=resource))
    tracer = trace.get_tracer(__name__)
    
    otlp_exporter = OTLPSpanExporter(
        endpoint="http://localhost:4317",
        insecure=True
    )
    
    span_processor = BatchSpanProcessor(otlp_exporter)
    trace.get_tracer_provider().add_span_processor(span_processor)
    
    return tracer

def check_service_health(service_name, base_url):
    """检查服务健康状态"""
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print(f"✓ {service_name}服务健康")
            return True
        else:
            print(f"✗ {service_name}服务不健康，状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ 无法连接到{service_name}服务: {e}")
        return False

def simulate_user_browsing(tracer, user_id):
    """模拟用户浏览行为"""
    with tracer.start_as_current_span(f"user_browsing_{user_id}") as span:
        span.set_attribute("user.id", user_id)
        
        # 获取产品列表
        headers = {}
        inject(headers)
        
        with tracer.start_as_current_span("get_products") as child_span:
            try:
                response = requests.get(
                    "http://localhost:5000/api/products",
                    headers=headers,
                    timeout=5
                )
                if response.status_code == 200:
                    products = response.json()
                    child_span.set_attribute("products.count", len(products))
                    print(f"用户 {user_id} 浏览了 {len(products)} 个产品")
                else:
                    print(f"用户 {user_id} 获取产品列表失败，状态码: {response.status_code}")
            except Exception as e:
                print(f"用户 {user_id} 获取产品列表异常: {e}")
        
        # 随机选择一个产品查看详情
        import random
        product_id = random.randint(1, 5)
        
        with tracer.start_as_current_span("get_product_details") as child_span:
            child_span.set_attribute("product.id", product_id)
            try:
                response = requests.get(
                    f"http://localhost:5000/api/products/{product_id}",
                    headers=headers,
                    timeout=5
                )
                if response.status_code == 200:
                    product = response.json()
                    print(f"用户 {user_id} 查看了产品: {product['name']}")
                else:
                    print(f"用户 {user_id} 获取产品详情失败，状态码: {response.status_code}")
            except Exception as e:
                print(f"用户 {user_id} 获取产品详情异常: {e}")

def simulate_order_creation(tracer, user_id):
    """模拟订单创建"""
    with tracer.start_as_current_span(f"create_order_{user_id}") as span:
        span.set_attribute("user.id", user_id)
        
        headers = {}
        inject(headers)
        
        # 创建订单
        import random
        items = [
            {"product_id": random.randint(1, 5), "quantity": random.randint(1, 3)}
            for _ in range(random.randint(1, 3))
        ]
        
        with tracer.start_as_current_span("submit_order") as child_span:
            child_span.set_attribute("order.items_count", len(items))
            try:
                response = requests.post(
                    "http://localhost:5000/api/orders",
                    json={
                        "user_id": user_id,
                        "items": items
                    },
                    headers=headers,
                    timeout=10
                )
                if response.status_code == 201:
                    order_data = response.json()
                    print(f"用户 {user_id} 成功创建订单 {order_data['order']['order_id']}")
                    return order_data
                else:
                    print(f"用户 {user_id} 创建订单失败，状态码: {response.status_code}")
                    return None
            except Exception as e:
                print(f"用户 {user_id} 创建订单异常: {e}")
                return None

def simulate_user_journey(tracer, user_id):
    """模拟完整的用户旅程"""
    with tracer.start_as_current_span(f"user_journey_{user_id}") as span:
        span.set_attribute("user.id", user_id)
        
        # 用户浏览产品
        simulate_user_browsing(tracer, user_id)
        
        # 等待一段时间
        time.sleep(random.uniform(1, 3))
        
        # 用户创建订单
        order_data = simulate_order_creation(tracer, user_id)
        
        return order_data

def generate_traces(user_count=10):
    """生成追踪数据"""
    tracer = setup_tracer()
    
    # 检查所有服务健康状态
    services = {
        "API网关": "http://localhost:5000",
        "用户服务": "http://localhost:5001",
        "产品服务": "http://localhost:5002",
        "订单服务": "http://localhost:5003",
        "支付服务": "http://localhost:5004"
    }
    
    print("检查服务健康状态...")
    all_healthy = True
    for name, url in services.items():
        if not check_service_health(name, url):
            all_healthy = False
    
    if not all_healthy:
        print("部分服务不健康，请先启动所有微服务")
        return
    
    # 模拟多个用户的完整旅程
    print(f"模拟 {user_count} 个用户的完整旅程...")
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = []
        for user_id in range(1, user_count + 1):
            futures.append(
                executor.submit(
                    simulate_user_journey,
                    tracer,
                    user_id
                )
            )
        
        # 等待所有用户旅程完成
        for future in as_completed(futures):
            future.result()
    
    print("所有用户旅程模拟完成")

def analyze_traces():
    """分析追踪数据"""
    try:
        # 这里可以添加代码从Jaeger API获取追踪数据并进行分析
        # 由于需要认证和复杂的API调用，这里只提供基本思路
        print("请访问 Jaeger UI 查看追踪数据: http://localhost:16686")
        print("在UI中，您可以:")
        print("- 查看完整的分布式追踪")
        print("- 分析服务间调用关系")
        print("- 识别性能瓶颈")
        print("- 搜索特定的追踪")
    except Exception as e:
        print(f"分析追踪数据时出错: {e}")

def main():
    print("=== 实验1：微服务架构中的分布式追踪 ===")
    
    # 生成追踪数据
    print("\n1. 生成追踪数据...")
    generate_traces(user_count=20)
    
    # 等待数据发送
    print("\n2. 等待数据发送...")
    time.sleep(10)
    
    # 分析追踪数据
    print("\n3. 分析追踪数据...")
    analyze_traces()
    
    print("\n实验1完成！")
    print("请访问以下位置查看结果:")
    print("- Jaeger UI: http://localhost:16686")
    print("- 在UI中搜索 'microservices-experiment' 服务查看追踪")

if __name__ == "__main__":
    main()
```

### 3.2 实验2：Kubernetes环境中的OpenTelemetry部署

```python
# experiment2.py
"""
实验2：Kubernetes环境中的OpenTelemetry部署
目标：学习如何在Kubernetes环境中部署和使用OpenTelemetry
"""

import os
import time
import subprocess
import requests
from kubernetes import client, config
from kubernetes.client.rest import ApiException

class KubernetesExperiment:
    def __init__(self):
        """初始化Kubernetes实验"""
        try:
            # 尝试加载集群内配置
            config.load_incluster_config()
        except:
            # 如果不在集群内，加载本地配置
            try:
                config.load_kube_config()
            except:
                print("无法加载Kubernetes配置")
                return
        
        self.v1 = client.CoreV1Api()
        self.apps_v1 = client.AppsV1Api()
        self.custom_api = client.CustomObjectsApi()
    
    def check_cluster_connection(self):
        """检查Kubernetes集群连接"""
        try:
            api_version = self.v1.get_api_resources()
            print("✓ Kubernetes集群连接成功")
            return True
        except ApiException as e:
            print(f"✗ 无法连接到Kubernetes集群: {e}")
            return False
        except Exception as e:
            print(f"✗ 检查Kubernetes集群连接时出错: {e}")
            return False
    
    def create_namespace(self, namespace_name):
        """创建命名空间"""
        namespace = client.V1Namespace(
            metadata=client.V1ObjectMeta(name=namespace_name)
        )
        
        try:
            self.v1.create_namespace(namespace)
            print(f"✓ 命名空间 {namespace_name} 创建成功")
            return True
        except ApiException as e:
            if e.status == 409:
                print(f"✓ 命名空间 {namespace_name} 已存在")
                return True
            else:
                print(f"✗ 创建命名空间 {namespace_name} 失败: {e}")
                return False
    
    def deploy_opentelemetry_operator(self):
        """部署OpenTelemetry Operator"""
        # 这里简化了部署过程，实际应用中可能需要更复杂的YAML文件
        print("部署OpenTelemetry Operator...")
        
        # 创建OperatorGroup
        operator_group = {
            "apiVersion": "operators.coreos.com/v1",
            "kind": "OperatorGroup",
            "metadata": {
                "name": "observability-operator-group",
                "namespace": "observability"
            },
            "spec": {
                "targetNamespaces": ["observability"]
            }
        }
        
        try:
            self.custom_api.create_namespaced_custom_object(
                group="operators.coreos.com",
                version="v1",
                namespace="observability",
                plural="operatorgroups",
                body=operator_group
            )
            print("✓ OperatorGroup 创建成功")
        except ApiException as e:
            if e.status == 409:
                print("✓ OperatorGroup 已存在")
            else:
                print(f"✗ 创建OperatorGroup失败: {e}")
                return False
        
        # 创建Subscription
        subscription = {
            "apiVersion": "operators.coreos.com/v1alpha1",
            "kind": "Subscription",
            "metadata": {
                "name": "opentelemetry-operator",
                "namespace": "observability"
            },
            "spec": {
                "channel": "stable",
                "name": "opentelemetry-operator",
                "source": "community-operators",
                "sourceNamespace": "openshift-marketplace"
            }
        }
        
        try:
            self.custom_api.create_namespaced_custom_object(
                group="operators.coreos.com",
                version="v1alpha1",
                namespace="observability",
                plural="subscriptions",
                body=subscription
            )
            print("✓ Subscription 创建成功")
            return True
        except ApiException as e:
            if e.status == 409:
                print("✓ Subscription 已存在")
                return True
            else:
                print(f"✗ 创建Subscription失败: {e}")
                return False
    
    def deploy_opentelemetry_collector(self):
        """部署OpenTelemetry Collector"""
        print("部署OpenTelemetry Collector...")
        
        # 创建OpenTelemetryCollector
        collector = {
            "apiVersion": "opentelemetry.io/v1alpha1",
            "kind": "OpenTelemetryCollector",
            "metadata": {
                "name": "otel",
                "namespace": "observability"
            },
            "spec": {
                "mode": "deployment",
                "replicas": 2,
                "config": """
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
      http:
        endpoint: 0.0.0.0:4318

processors:
  batch:
    timeout: 1s
    send_batch_size: 1024

exporters:
  logging:
    loglevel: info

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [batch]
      exporters: [logging]
    metrics:
      receivers: [otlp]
      processors: [batch]
      exporters: [logging]
"""
            }
        }
        
        try:
            self.custom_api.create_namespaced_custom_object(
                group="opentelemetry.io",
                version="v1alpha1",
                namespace="observability",
                plural="opentelemetrycollectors",
                body=collector
            )
            print("✓ OpenTelemetryCollector 创建成功")
            return True
        except ApiException as e:
            if e.status == 409:
                print("✓ OpenTelemetryCollector 已存在")
                return True
            else:
                print(f"✗ 创建OpenTelemetryCollector失败: {e}")
                return False
    
    def create_instrumentation(self):
        """创建Instrumentation"""
        print("创建Instrumentation...")
        
        # 创建Python Instrumentation
        python_instrumentation = {
            "apiVersion": "opentelemetry.io/v1alpha1",
            "kind": "Instrumentation",
            "metadata": {
                "name": "python-instrumentation",
                "namespace": "observability"
            },
            "spec": {
                "exporter": {
                    "endpoint": "http://otel-collector:4317"
                },
                "propagators": ["tracecontext", "baggage"],
                "sampler": {
                    "type": "parentbased_traceidratio",
                    "argument": "0.25"
                },
                "python": {
                    "env": [
                        {
                            "name": "OTEL_RESOURCE_ATTRIBUTES",
                            "value": "service.name=$(K8S_POD_NAME),service.namespace=$(K8S_NAMESPACE)"
                        },
                        {
                            "name": "OTEL_EXPORTER_OTLP_ENDPOINT",
                            "value": "http://otel-collector:4317"
                        }
                    ]
                }
            }
        }
        
        try:
            self.custom_api.create_namespaced_custom_object(
                group="opentelemetry.io",
                version="v1alpha1",
                namespace="observability",
                plural="instrumentations",
                body=python_instrumentation
            )
            print("✓ Python Instrumentation 创建成功")
            return True
        except ApiException as e:
            if e.status == 409:
                print("✓ Python Instrumentation 已存在")
                return True
            else:
                print(f"✗ 创建Python Instrumentation失败: {e}")
                return False
    
    def deploy_sample_app(self):
        """部署示例应用"""
        print("部署示例应用...")
        
        # 创建命名空间
        if not self.create_namespace("sample-app"):
            return False
        
        # 创建Deployment
        deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "sample-app",
                "namespace": "sample-app"
            },
            "spec": {
                "replicas": 2,
                "selector": {
                    "matchLabels": {
                        "app": "sample-app"
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": "sample-app"
                        },
                        "annotations": {
                            "instrumentation.opentelemetry.io/inject-python": "observability/python-instrumentation"
                        }
                    },
                    "spec": {
                        "containers": [
                            {
                                "name": "app",
                                "image": "python:3.9-slim",
                                "command": [
                                    "python", "-c",
                                    "import time; import random; from opentelemetry import trace; tracer = trace.get_tracer(__name__); while True: with tracer.start_as_current_span('operation'): time.sleep(random.uniform(0.1, 0.5))"
                                ],
                                "resources": {
                                    "requests": {
                                        "cpu": "100m",
                                        "memory": "128Mi"
                                    },
                                    "limits": {
                                        "cpu": "200m",
                                        "memory": "256Mi"
                                    }
                                }
                            }
                        ]
                    }
                }
            }
        }
        
        try:
            self.apps_v1.create_namespaced_deployment(
                namespace="sample-app",
                body=deployment
            )
            print("✓ 示例应用 Deployment 创建成功")
            return True
        except ApiException as e:
            if e.status == 409:
                print("✓ 示例应用 Deployment 已存在")
                return True
            else:
                print(f"✗ 创建示例应用 Deployment 失败: {e}")
                return False
    
    def wait_for_deployment(self, namespace, deployment_name, timeout=300):
        """等待部署完成"""
        print(f"等待 {namespace}/{deployment_name} 部署完成...")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                deployment = self.apps_v1.read_namespaced_deployment(
                    name=deployment_name,
                    namespace=namespace
                )
                
                if deployment.status.ready_replicas == deployment.spec.replicas:
                    print(f"✓ {namespace}/{deployment_name} 部署完成")
                    return True
                
                print(f"等待 {namespace}/{deployment_name} 部署中... ({deployment.status.ready_replicas}/{deployment.spec.replicas})")
                time.sleep(10)
            except ApiException as e:
                print(f"✗ 检查 {namespace}/{deployment_name} 部署状态失败: {e}")
                return False
        
        print(f"✗ {namespace}/{deployment_name} 部署超时")
        return False
    
    def check_collector_health(self):
        """检查Collector健康状态"""
        print("检查Collector健康状态...")
        
        try:
            # 获取Collector服务
            service = self.v1.read_namespaced_service(
                name="otel-collector",
                namespace="observability"
            )
            
            # 获取服务端点
            endpoints = self.v1.read_namespaced_endpoints(
                name="otel-collector",
                namespace="observability"
            )
            
            if not endpoints.subsets:
                print("✗ Collector 服务没有可用的端点")
                return False
            
            # 这里可以添加端口转发或使用Ingress来访问Collector
            print("✓ Collector 服务运行正常")
            return True
        except ApiException as e:
            print(f"✗ 检查Collector健康状态失败: {e}")
            return False
    
    def generate_traces_in_cluster(self):
        """在集群内生成追踪数据"""
        print("在集群内生成追踪数据...")
        
        # 这里可以创建一个Job来生成追踪数据
        job = {
            "apiVersion": "batch/v1",
            "kind": "Job",
            "metadata": {
                "name": "trace-generator",
                "namespace": "sample-app"
            },
            "spec": {
                "template": {
                    "metadata": {
                        "annotations": {
                            "instrumentation.opentelemetry.io/inject-python": "observability/python-instrumentation"
                        }
                    },
                    "spec": {
                        "restartPolicy": "Never",
                        "containers": [
                            {
                                "name": "trace-generator",
                                "image": "python:3.9-slim",
                                "command": [
                                    "python", "-c",
                                    """
import time
import random
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

for i in range(100):
    with tracer.start_as_current_span(f"operation-{i}") as span:
        span.set_attribute("operation.id", i)
        span.set_attribute("operation.type", "generated")
        
        # 模拟一些工作
        time.sleep(random.uniform(0.01, 0.1))
        
        # 创建子span
        with tracer.start_as_current_span(f"sub-operation-{i}") as child_span:
            child_span.set_attribute("sub.operation.id", i)
            child_span.set_attribute("sub.operation.type", "child")
            time.sleep(random.uniform(0.01, 0.05))
"""
                                ]
                            }
                        ]
                    }
                }
            }
        }
        
        try:
            self.batch_v1 = client.BatchV1Api()
            self.batch_v1.create_namespaced_job(
                namespace="sample-app",
                body=job
            )
            print("✓ 追踪生成器 Job 创建成功")
            return True
        except ApiException as e:
            if e.status == 409:
                print("✓ 追踪生成器 Job 已存在")
                return True
            else:
                print(f"✗ 创建追踪生成器 Job 失败: {e}")
                return False
    
    def cleanup(self):
        """清理资源"""
        print("清理实验资源...")
        
        # 删除示例应用
        try:
            self.apps_v1.delete_namespaced_deployment(
                name="sample-app",
                namespace="sample-app"
            )
            print("✓ 示例应用 Deployment 删除成功")
        except ApiException as e:
            print(f"✗ 删除示例应用 Deployment 失败: {e}")
        
        # 删除命名空间
        try:
            self.v1.delete_namespace("sample-app")
            print("✓ sample-app 命名空间删除成功")
        except ApiException as e:
            print(f"✗ 删除 sample-app 命名空间失败: {e}")
        
        # 这里可以添加更多清理步骤，如删除Collector等

def main():
    print("=== 实验2：Kubernetes环境中的OpenTelemetry部署 ===")
    
    # 检查是否有Kubernetes环境
    if "KUBERNETES_SERVICE_HOST" not in os.environ:
        print("此实验需要在Kubernetes环境中运行")
        print("如果您有Kubernetes集群，可以将此代码作为Job运行")
        return
    
    # 创建实验实例
    experiment = KubernetesExperiment()
    
    # 检查集群连接
    print("\n1. 检查Kubernetes集群连接...")
    if not experiment.check_cluster_connection():
        return
    
    # 创建命名空间
    print("\n2. 创建命名空间...")
    if not experiment.create_namespace("observability"):
        return
    
    # 部署OpenTelemetry Operator
    print("\n3. 部署OpenTelemetry Operator...")
    if not experiment.deploy_opentelemetry_operator():
        return
    
    # 等待Operator就绪
    print("\n4. 等待Operator就绪...")
    time.sleep(30)  # 简化等待，实际应用中应该检查状态
    
    # 部署OpenTelemetry Collector
    print("\n5. 部署OpenTelemetry Collector...")
    if not experiment.deploy_opentelemetry_collector():
        return
    
    # 等待Collector就绪
    print("\n6. 等待Collector就绪...")
    if not experiment.wait_for_deployment("observability", "otel-collector"):
        return
    
    # 创建Instrumentation
    print("\n7. 创建Instrumentation...")
    if not experiment.create_instrumentation():
        return
    
    # 部署示例应用
    print("\n8. 部署示例应用...")
    if not experiment.deploy_sample_app():
        return
    
    # 等待应用就绪
    print("\n9. 等待应用就绪...")
    if not experiment.wait_for_deployment("sample-app", "sample-app"):
        return
    
    # 检查Collector健康状态
    print("\n10. 检查Collector健康状态...")
    if not experiment.check_collector_health():
        return
    
    # 在集群内生成追踪数据
    print("\n11. 在集群内生成追踪数据...")
    if not experiment.generate_traces_in_cluster():
        return
    
    print("\n实验2完成！")
    print("请检查以下位置以验证结果:")
    print("- Collector日志: kubectl logs -n observability deployment/otel-collector")
    print("- 示例应用日志: kubectl logs -n sample-app deployment/sample-app")
    print("- 追踪数据: 需要配置后端存储如Jaeger或Prometheus")
    
    # 清理资源（可选）
    # print("\n清理实验资源...")
    # experiment.cleanup()

if __name__ == "__main__":
    main()
```

### 3.3 实验3：大规模性能测试与优化

```python
# experiment3.py
"""
实验3：大规模性能测试与优化
目标：学习如何测试和优化OpenTelemetry在大规模环境下的性能
"""

import time
import threading
import random
import requests
import json
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from opentelemetry import trace, metrics
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource

class PerformanceTest:
    def __init__(self):
        """初始化性能测试"""
        self.resource = Resource.create({
            "service.name": "performance-test",
            "service.version": "1.0.0",
            "environment": "experiment"
        })
        
        # 设置追踪
        trace.set_tracer_provider(TracerProvider(resource=self.resource))
        self.tracer = trace.get_tracer(__name__)
        
        # 设置指标
        metric_reader = PeriodicExportingMetricReader(
            exporter=OTLPMetricExporter(
                endpoint="http://localhost:4317",
                insecure=True
            ),
            export_interval_millis=15000
        )
        
        metrics.set_meter_provider(MeterProvider(resource=self.resource, metric_readers=[metric_reader]))
        self.meter = metrics.get_meter(__name__)
        
        # 创建指标
        self.test_duration_histogram = self.meter.create_histogram(
            "test_operation_duration_seconds",
            description="Duration of test operations in seconds"
        )
        
        self.spans_generated_counter = self.meter.create_counter(
            "spans_generated_total",
            description="Total number of spans generated"
        )
        
        self.test_results = []
    
    def generate_single_span(self, operation_name, duration_ms=100):
        """生成单个span"""
        start_time = time.time()
        
        with self.tracer.start_as_current_span(operation_name) as span:
            span.set_attribute("operation.name", operation_name)
            span.set_attribute("operation.duration_ms", duration_ms)
            
            # 模拟操作耗时
            time.sleep(duration_ms / 1000)
            
            # 添加事件
            span.add_event(f"{operation_name} completed", {
                "event.type": "completion",
                "event.timestamp": time.time()
            })
            
            # 记录指标
            actual_duration = time.time() - start_time
            self.test_duration_histogram.record(actual_duration, {"operation": operation_name})
            self.spans_generated_counter.add(1, {"operation": operation_name})
            
            return actual_duration
    
    def generate_nested_spans(self, depth=3, breadth=2, base_duration_ms=50):
        """生成嵌套span"""
        total_duration = 0
        
        def _generate_nested(current_depth, parent_name="root"):
            nonlocal total_duration
            
            if current_depth <= 0:
                return 0
            
            with self.tracer.start_as_current_span(f"{parent_name}-level-{current_depth}") as span:
                span.set_attribute("depth", current_depth)
                
                # 生成当前级别的span
                duration = self.generate_single_span(
                    f"{parent_name}-level-{current_depth}-main",
                    base_duration_ms
                )
                total_duration += duration
                
                # 生成子span
                for i in range(breadth):
                    child_duration = _generate_nested(
                        current_depth - 1,
                        f"{parent_name}-level-{current_depth}-child-{i}"
                    )
                    total_duration += child_duration
            
            return duration
        
        start_time = time.time()
        _generate_nested(depth)
        total_time = time.time() - start_time
        
        return total_time
    
    def simulate_service_call(self, service_name, endpoint, response_time_ms=100):
        """模拟服务调用"""
        with self.tracer.start_as_current_span(f"call-{service_name}") as span:
            span.set_attribute("service.name", service_name)
            span.set_attribute("service.endpoint", endpoint)
            
            # 模拟网络延迟
            time.sleep(response_time_ms / 1000)
            
            # 模拟可能的错误
            if random.random() < 0.05:  # 5%的错误率
                span.set_status(trace.Status(trace.StatusCode.ERROR, "Simulated service error"))
                return False
            else:
                span.set_status(trace.Status(trace.StatusCode.OK))
                return True
    
    def simulate_microservice_flow(self, services_count=5, calls_per_service=3):
        """模拟微服务流程"""
        services = [f"service-{i}" for i in range(1, services_count + 1)]
        endpoints = ["api/data", "api/process", "api/validate"]
        
        with self.tracer.start_as_current_span("microservice-flow") as span:
            span.set_attribute("services.count", services_count)
            
            for service in services:
                for _ in range(calls_per_service):
                    endpoint = random.choice(endpoints)
                    response_time = random.randint(50, 200)
                    self.simulate_service_call(service, endpoint, response_time)
    
    def run_load_test(self, threads=10, operations_per_thread=100, operation_type="single"):
        """运行负载测试"""
        print(f"开始负载测试: {threads} 线程, 每线程 {operations_per_thread} 操作, 类型: {operation_type}")
        
        start_time = time.time()
        results = []
        
        def worker_thread(thread_id):
            thread_results = []
            
            for i in range(operations_per_thread):
                op_start = time.time()
                
                if operation_type == "single":
                    duration = self.generate_single_span(f"op-{thread_id}-{i}", random.randint(50, 150))
                elif operation_type == "nested":
                    duration = self.generate_nested_spans(
                        depth=random.randint(2, 4),
                        breadth=random.randint(2, 3),
                        base_duration_ms=random.randint(20, 80)
                    )
                elif operation_type == "microservice":
                    self.simulate_microservice_flow(
                        services_count=random.randint(3, 6),
                        calls_per_service=random.randint(2, 4)
                    )
                    duration = time.time() - op_start
                else:
                    duration = self.generate_single_span(f"op-{thread_id}-{i}", 100)
                
                op_end = time.time()
                thread_results.append({
                    "thread_id": thread_id,
                    "operation_id": i,
                    "duration": op_end - op_start,
                    "span_duration": duration
                })
            
            return thread_results
        
        # 使用线程池执行测试
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = [executor.submit(worker_thread, i) for i in range(threads)]
            
            for future in as_completed(futures):
                try:
                    thread_results = future.result()
                    results.extend(thread_results)
                except Exception as e:
                    print(f"线程执行出错: {e}")
        
        total_time = time.time() - start_time
        
        # 计算统计数据
        durations = [r["duration"] for r in results]
        span_durations = [r["span_duration"] for r in results]
        
        stats = {
            "total_time": total_time,
            "total_operations": len(results),
            "operations_per_second": len(results) / total_time,
            "avg_duration": statistics.mean(durations),
            "min_duration": min(durations),
            "max_duration": max(durations),
            "p50_duration": statistics.median(durations),
            "p95_duration": sorted(durations)[int(len(durations) * 0.95)],
            "p99_duration": sorted(durations)[int(len(durations) * 0.99)],
            "avg_span_duration": statistics.mean(span_durations),
            "min_span_duration": min(span_durations),
            "max_span_duration": max(span_durations)
        }
        
        self.test_results.append({
            "test_type": operation_type,
            "threads": threads,
            "operations_per_thread": operations_per_thread,
            "stats": stats
        })
        
        return stats
    
    def compare_configurations(self):
        """比较不同配置的性能"""
        print("比较不同配置的性能...")
        
        configurations = [
            {"name": "低负载-单span", "threads": 5, "ops": 50, "type": "single"},
            {"name": "中负载-单span", "threads": 10, "ops": 100, "type": "single"},
            {"name": "高负载-单span", "threads": 20, "ops": 200, "type": "single"},
            {"name": "低负载-嵌套span", "threads": 5, "ops": 50, "type": "nested"},
            {"name": "中负载-嵌套span", "threads": 10, "ops": 100, "type": "nested"},
            {"name": "高负载-嵌套span", "threads": 20, "ops": 200, "type": "nested"},
            {"name": "低负载-微服务", "threads": 5, "ops": 30, "type": "microservice"},
            {"name": "中负载-微服务", "threads": 10, "ops": 50, "type": "microservice"},
            {"name": "高负载-微服务", "threads": 20, "ops": 100, "type": "microservice"}
        ]
        
        results = []
        
        for config in configurations:
            print(f"测试配置: {config['name']}")
            stats = self.run_load_test(
                threads=config["threads"],
                operations_per_thread=config["ops"],
                operation_type=config["type"]
            )
            
            results.append({
                "name": config["name"],
                "ops_per_second": stats["operations_per_second"],
                "avg_duration": stats["avg_duration"],
                "p95_duration": stats["p95_duration"]
            })
            
            # 等待一段时间再进行下一个测试
            time.sleep(5)
        
        # 打印比较结果
        print("\n配置比较结果:")
        print(f"{'配置':<20} {'操作/秒':<15} {'平均耗时(ms)':<15} {'P95耗时(ms)':<15}")
        print("-" * 65)
        
        for result in results:
            print(f"{result['name']:<20} {result['ops_per_second']:<15.2f} {result['avg_duration']*1000:<15.2f} {result['p95_duration']*1000:<15.2f}")
        
        return results
    
    def test_collector_performance(self):
        """测试Collector性能"""
        print("测试Collector性能...")
        
        # 测试不同的批处理大小
        batch_sizes = [128, 256, 512, 1024, 2048]
        results = []
        
        for batch_size in batch_sizes:
            print(f"测试批处理大小: {batch_size}")
            
            # 重新配置Collector的批处理大小
            # 注意: 这里只是模拟，实际应用中需要修改Collector配置
            
            # 运行测试
            stats = self.run_load_test(
                threads=10,
                operations_per_thread=100,
                operation_type="single"
            )
            
            results.append({
                "batch_size": batch_size,
                "ops_per_second": stats["operations_per_second"],
                "avg_duration": stats["avg_duration"],
                "p95_duration": stats["p95_duration"]
            })
            
            # 等待一段时间再进行下一个测试
            time.sleep(5)
        
        # 打印结果
        print("\n批处理大小比较结果:")
        print(f"{'批处理大小':<15} {'操作/秒':<15} {'平均耗时(ms)':<15} {'P95耗时(ms)':<15}")
        print("-" * 60)
        
        for result in results:
            print(f"{result['batch_size']:<15} {result['ops_per_second']:<15.2f} {result['avg_duration']*1000:<15.2f} {result['p95_duration']*1000:<15.2f}")
        
        return results
    
    def analyze_results(self):
        """分析测试结果"""
        if not self.test_results:
            print("没有测试结果可分析")
            return
        
        print("\n分析测试结果...")
        
        # 按测试类型分组
        by_type = {}
        for result in self.test_results:
            test_type = result["test_type"]
            if test_type not in by_type:
                by_type[test_type] = []
            by_type[test_type].append(result["stats"])
        
        # 计算每种类型的平均性能
        for test_type, stats_list in by_type.items():
            avg_ops_per_sec = sum(s["operations_per_second"] for s in stats_list) / len(stats_list)
            avg_duration = sum(s["avg_duration"] for s in stats_list) / len(stats_list)
            avg_p95 = sum(s["p95_duration"] for s in stats_list) / len(stats_list)
            
            print(f"\n{test_type} 类型测试平均结果:")
            print(f"  平均操作/秒: {avg_ops_per_sec:.2f}")
            print(f"  平均耗时: {avg_duration*1000:.2f}ms")
            print(f"  平均P95耗时: {avg_p95*1000:.2f}ms")

def main():
    print("=== 实验3：大规模性能测试与优化 ===")
    
    # 创建性能测试实例
    perf_test = PerformanceTest()
    
    # 1. 基本负载测试
    print("\n1. 基本负载测试...")
    basic_stats = perf_test.run_load_test(
        threads=5,
        operations_per_thread=50,
        operation_type="single"
    )
    
    print(f"基本测试结果: {basic_stats['operations_per_second']:.2f} 操作/秒")
    
    # 等待一段时间
    time.sleep(5)
    
    # 2. 不同类型操作的性能比较
    print("\n2. 不同类型操作的性能比较...")
    operation_types = ["single", "nested", "microservice"]
    comparison_results = []
    
    for op_type in operation_types:
        print(f"测试 {op_type} 类型操作...")
        stats = perf_test.run_load_test(
            threads=10,
            operations_per_thread=50,
            operation_type=op_type
        )
        
        comparison_results.append({
            "type": op_type,
            "ops_per_second": stats["operations_per_second"],
            "avg_duration": stats["avg_duration"],
            "p95_duration": stats["p95_duration"]
        })
        
        # 等待一段时间
        time.sleep(5)
    
    # 打印比较结果
    print("\n操作类型比较结果:")
    print(f"{'类型':<15} {'操作/秒':<15} {'平均耗时(ms)':<15} {'P95耗时(ms)':<15}")
    print("-" * 60)
    
    for result in comparison_results:
        print(f"{result['type']:<15} {result['ops_per_second']:<15.2f} {result['avg_duration']*1000:<15.2f} {result['p95_duration']*1000:<15.2f}")
    
    # 3. 比较不同配置
    print("\n3. 比较不同配置...")
    config_results = perf_test.compare_configurations()
    
    # 4. 分析结果
    print("\n4. 分析结果...")
    perf_test.analyze_results()
    
    print("\n实验3完成！")
    print("请检查以下位置以验证结果:")
    print("- Jaeger UI: http://localhost:16686")
    print("- Prometheus UI: http://localhost:9090")
    print("- Collector指标: http://localhost:8889/metrics")

if __name__ == "__main__":
    main()
```

## 4. 运行指南

### 4.1 微服务架构示例运行指南

1. **安装依赖**:
```bash
pip install flask requests opentelemetry-api opentelemetry-sdk opentelemetry-instrumentation-flask opentelemetry-instrumentation-requests opentelemetry-instrumentation-sqlite3 opentelemetry-exporter-otlp opentelemetry-exporter-jaeger opentelemetry-exporter-prometheus opentelemetry-sdk-extensions-aws
```

2. **启动OpenTelemetry Collector**:
```bash
# 使用Docker启动Collector
docker run -d --name otel-collector \
  -p 4317:4317 -p 4318:4318 -p 8889:8889 \
  -v $(pwd)/collector-config.yaml:/etc/otel-collector-config.yaml \
  otel/opentelemetry-collector:latest \
  --config=/etc/otel-collector-config.yaml
```

3. **启动Jaeger**:
```bash
docker run -d --name jaeger \
  -p 16686:16686 -p 14250:14250 \
  jaegertracing/all-in-one:latest
```

4. **启动微服务**:
```bash
# 在不同终端中启动各个服务
python api_gateway.py
python user_service.py
python product_service.py
python order_service.py
python payment_service.py
```

5. **运行实验**:
```bash
python experiment1.py
```

### 4.2 Kubernetes环境部署指南

1. **准备Kubernetes集群**:
   - 可以使用Minikube、Kind或任何Kubernetes集群
   - 确保有足够的资源

2. **部署OpenTelemetry Operator**:
```bash
kubectl apply -f otel-operator.yaml
```

3. **部署OpenTelemetry Collector**:
```bash
kubectl apply -f otel-collector.yaml
```

4. **部署自动注入配置**:
```bash
kubectl apply -f auto-instrumentation.yaml
```

5. **部署示例应用**:
```bash
kubectl apply -f sample-app.yaml
```

6. **运行实验**:
```bash
# 在集群内运行
kubectl create job --from=cronjob/experiment2-job
```

### 4.3 性能测试运行指南

1. **准备环境**:
   - 确保OpenTelemetry Collector正在运行
   - 确保有足够的系统资源

2. **运行性能测试**:
```bash
python experiment3.py
```

3. **监控资源使用**:
```bash
# 监控CPU和内存使用
top -p $(pgrep -f "python experiment3.py")

# 监控网络使用
iftop

# 监控磁盘I/O
iotop
```

4. **调整Collector配置**:
   - 根据测试结果调整批处理大小
   - 调整导出器配置
   - 调整处理器配置

## 5. 故障排除

### 5.1 常见问题

1. **服务无法连接**:
   - 检查端口是否正确
   - 检查防火墙设置
   - 确认服务是否正在运行

2. **追踪数据未显示**:
   - 检查Collector配置
   - 确认导出器配置正确
   - 检查后端存储是否正常

3. **性能问题**:
   - 检查批处理大小
   - 调整采样率
   - 优化span数量

### 5.2 调试技巧

1. **启用详细日志**:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

2. **检查Collector状态**:
```bash
curl http://localhost:13133
```

3. **查看Collector指标**:
```bash
curl http://localhost:8889/metrics
```

4. **使用Jaeger UI调试**:
   - 访问 http://localhost:16686
   - 搜索特定服务或追踪
   - 分析span关系和耗时
