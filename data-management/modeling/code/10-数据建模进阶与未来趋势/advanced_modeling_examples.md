# 第10章：数据建模进阶与未来趋势 - 代码示例

## 10.1 知识图谱建模示例

### 10.1.1 使用Neo4j构建知识图谱

```cypher
-- 创建用户节点
CREATE (u:User {id: 1, name: '张三', email: 'zhangsan@example.com', age: 25, gender: '男'});
CREATE (u:User {id: 2, name: '李四', email: 'lisi@example.com', age: 30, gender: '女'});
CREATE (u:User {id: 3, name: '王五', email: 'wangwu@example.com', age: 35, gender: '男'});

-- 创建产品节点
CREATE (p:Product {id: 1, name: '智能手机', price: 2999.00, description: '高性能智能手机', stock: 100});
CREATE (p:Product {id: 2, name: '笔记本电脑', price: 5999.00, description: '轻薄笔记本电脑', stock: 50});
CREATE (p:Product {id: 3, name: '无线耳机', price: 999.00, description: '降噪无线耳机', stock: 200});
CREATE (p:Product {id: 4, name: '智能手表', price: 1999.00, description: '多功能智能手表', stock: 150});

-- 创建类别节点
CREATE (c:Category {id: 1, name: '电子产品', description: '各种电子产品'});
CREATE (c:Category {id: 2, name: '手机', description: '各种手机产品'});
CREATE (c:Category {id: 3, name: '电脑', description: '各种电脑产品'});
CREATE (c:Category {id: 4, name: '音频设备', description: '各种音频设备'});
CREATE (c:Category {id: 5, name: '智能穿戴', description: '各种智能穿戴设备'});

-- 创建品牌节点
CREATE (b:Brand {id: 1, name: '品牌A', country: '中国'});
CREATE (b:Brand {id: 2, name: '品牌B', country: '美国'});
CREATE (b:Brand {id: 3, name: '品牌C', country: '韩国'});

-- 创建订单节点
CREATE (o:Order {id: 1, order_date: '2023-01-01', total_amount: 2999.00, status: 'completed'});
CREATE (o:Order {id: 2, order_date: '2023-01-02', total_amount: 5999.00, status: 'completed'});
CREATE (o:Order {id: 3, order_date: '2023-01-03', total_amount: 2998.00, status: 'completed'});

-- 创建评价节点
CREATE (r:Review {id: 1, rating: 5, comment: '非常好用', review_date: '2023-01-04'});
CREATE (r:Review {id: 2, rating: 4, comment: '性能不错', review_date: '2023-01-05'});
CREATE (r:Review {id: 3, rating: 5, comment: '音质很好', review_date: '2023-01-06'});

-- 创建关系
-- 用户与订单关系
MATCH (u:User {id: 1}), (o:Order {id: 1}) CREATE (u)-[:PLACED]->(o);
MATCH (u:User {id: 2}), (o:Order {id: 2}) CREATE (u)-[:PLACED]->(o);
MATCH (u:User {id: 3}), (o:Order {id: 3}) CREATE (u)-[:PLACED]->(o);

-- 订单与产品关系
MATCH (o:Order {id: 1}), (p:Product {id: 1}) CREATE (o)-[:CONTAINS]->(p);
MATCH (o:Order {id: 2}), (p:Product {id: 2}) CREATE (o)-[:CONTAINS]->(p);
MATCH (o:Order {id: 3}), (p:Product {id: 3}) CREATE (o)-[:CONTAINS]->(p);
MATCH (o:Order {id: 3}), (p:Product {id: 4}) CREATE (o)-[:CONTAINS]->(p);

-- 产品与类别关系
MATCH (p:Product {id: 1}), (c:Category {id: 2}) CREATE (p)-[:BELONGS_TO]->(c);
MATCH (p:Product {id: 2}), (c:Category {id: 3}) CREATE (p)-[:BELONGS_TO]->(c);
MATCH (p:Product {id: 3}), (c:Category {id: 4}) CREATE (p)-[:BELONGS_TO]->(c);
MATCH (p:Product {id: 4}), (c:Category {id: 5}) CREATE (p)-[:BELONGS_TO]->(c);

-- 子类别与父类别关系
MATCH (c:Category {id: 2}), (c2:Category {id: 1}) CREATE (c)-[:SUB_CATEGORY_OF]->(c2);
MATCH (c:Category {id: 3}), (c2:Category {id: 1}) CREATE (c)-[:SUB_CATEGORY_OF]->(c2);
MATCH (c:Category {id: 4}), (c2:Category {id: 1}) CREATE (c)-[:SUB_CATEGORY_OF]->(c2);
MATCH (c:Category {id: 5}), (c2:Category {id: 1}) CREATE (c)-[:SUB_CATEGORY_OF]->(c2);

-- 产品与品牌关系
MATCH (p:Product {id: 1}), (b:Brand {id: 1}) CREATE (p)-[:MANUFACTURED_BY]->(b);
MATCH (p:Product {id: 2}), (b:Brand {id: 2}) CREATE (p)-[:MANUFACTURED_BY]->(b);
MATCH (p:Product {id: 3}), (b:Brand {id: 3}) CREATE (p)-[:MANUFACTURED_BY]->(b);
MATCH (p:Product {id: 4}), (b:Brand {id: 1}) CREATE (p)-[:MANUFACTURED_BY]->(b);

-- 用户与评价关系
MATCH (u:User {id: 1}), (r:Review {id: 1}) CREATE (u)-[:WROTE]->(r);
MATCH (u:User {id: 2}), (r:Review {id: 2}) CREATE (u)-[:WROTE]->(r);
MATCH (u:User {id: 3}), (r:Review {id: 3}) CREATE (u)-[:WROTE]->(r);

-- 评价与产品关系
MATCH (r:Review {id: 1}), (p:Product {id: 1}) CREATE (r)-[:ABOUT]->(p);
MATCH (r:Review {id: 2}), (p:Product {id: 2}) CREATE (r)-[:ABOUT]->(p);
MATCH (r:Review {id: 3}), (p:Product {id: 3}) CREATE (r)-[:ABOUT]->(p);

-- 用户与用户关系（朋友）
MATCH (u:User {id: 1}), (u2:User {id: 2}) CREATE (u)-[:FRIEND_WITH]->(u2);
MATCH (u:User {id: 2}), (u3:User {id: 3}) CREATE (u)-[:FRIEND_WITH]->(u3);
```

### 10.1.2 知识图谱查询示例

```cypher
-- 查询用户购买的产品
MATCH (u:User {name: '张三'})-[:PLACED]->(o:Order)-[:CONTAINS]->(p:Product)
RETURN u.name, p.name, p.price, o.order_date;

-- 查询属于电子产品类别的所有产品（包括子类）
MATCH (p:Product)-[:BELONGS_TO]->(:Category)-[:SUB_CATEGORY_OF*0..]->(c:Category {name: '电子产品'})
RETURN DISTINCT p.name, p.price;

-- 查询品牌A生产的所有产品
MATCH (p:Product)-[:MANUFACTURED_BY]->(b:Brand {name: '品牌A'})
RETURN p.name, p.price;

-- 查询产品的评价信息
MATCH (p:Product {name: '智能手机'})<-[:ABOUT]-(r:Review)<-[:WROTE]-(u:User)
RETURN u.name, r.rating, r.comment, r.review_date;

-- 查询用户的朋友购买了哪些产品（社交推荐）
MATCH (u:User {name: '张三'})-[:FRIEND_WITH]->(friend:User)-[:PLACED]->(o:Order)-[:CONTAINS]->(p:Product)
RETURN DISTINCT friend.name, p.name, p.price;

-- 查询购买了智能手机的用户还购买了哪些产品（协同过滤）
MATCH (u:User)-[:PLACED]->(o:Order)-[:CONTAINS]->(p:Product {name: '智能手机'}),
      (u)-[:PLACED]->(o2:Order)-[:CONTAINS]->(p2:Product)
WHERE p2 <> p
RETURN DISTINCT p2.name, p2.price, COUNT(u) AS buy_count
ORDER BY buy_count DESC;

-- 查询评价最高的产品
MATCH (p:Product)<-[:ABOUT]-(r:Review)
RETURN p.name, AVG(r.rating) AS avg_rating
ORDER BY avg_rating DESC
LIMIT 5;

-- 查询每个类别的产品数量
MATCH (p:Product)-[:BELONGS_TO]->(c:Category)
RETURN c.name, COUNT(p) AS product_count
ORDER BY product_count DESC;
```

### 10.1.3 使用Python操作Neo4j知识图谱

```python
from neo4j import GraphDatabase

class KnowledgeGraph:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def add_user(self, id, name, email, age, gender):
        with self.driver.session() as session:
            session.run("CREATE (u:User {id: $id, name: $name, email: $email, age: $age, gender: $gender})",