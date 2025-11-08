# 第5章：JSON与XML数据处理

## 5.1 JSON数据处理基础

### 5.1.1 JSONPath详解

JSONPath是一种用于从JSON文档中提取数据的表达式语言，类似于XPath用于XML。REST Assured内置了强大的JSONPath支持：

```java
// 基本JSONPath表达式
// 获取根对象的属性
.body("name", equalTo("John Doe"))
.body("age", equalTo(30))

// 获取嵌套对象的属性
.body("address.city", equalTo("New York"))
.body("contact.email", containsString("@"))

// 获取数组元素
.body("users[0].name", equalTo("Alice"))
.body("items[2].price", greaterThan(10.0))

// 获取数组所有元素
.body("users[*].name", hasItems("Alice", "Bob", "Charlie"))
.body("items[*].price", everyItem(greaterThan(0)))

// 获取数组长度
.body("users.size()", equalTo(10))
.body("items.size()", greaterThan(0))

// 数组切片
.body("users[0:3].name", hasSize(3))
.body("items[-1].price", greaterThan(20.0))  // 最后一个元素

// 条件筛选
.body("users[?(@.age > 30)]", hasSize(greaterThan(0)))
.body("items[?(@.price > 50 && @.category == 'electronics')]", hasSize(1))

// 递归搜索
.body("$..name", hasItem("John Doe"))
.body("$..price", hasItems(10.0, 25.5, 99.99))

// JSONPath运算符
.body("price * quantity", equalTo(199.8))
.body("items[?(@.price * @.quantity > 100)]", hasSize(greaterThan(0)))

// 使用JsonPath API直接提取数据
String name = get("/api/users/1").path("name");
List<String> emails = get("/api/users").path("users[*].email");
Map<String, Object> address = get("/api/users/1").path("address");
```

### 5.1.2 JSON处理高级技巧

```java
// 复杂JSONPath表达式
@Test
public void testComplexJsonPath() {
    given()
        .when()
        .get("/api/products")
    .then()
        .statusCode(200)
        // 获取特定条件的产品
        .body("products[?(@.category == 'electronics' && @.price > 100)].name", 
            hasItem("Smartphone"))
        
        // 获取嵌套数组中的特定元素
        .body("products[?(@.specs.display.type == 'OLED')].name", 
            hasItem("Premium TV"))
        
        // 使用正则表达式匹配
        .body("products[?(@.sku =~ /ELEC-.*/)].name", 
            hasItems("Smartphone", "Tablet"))
        
        // 复杂条件组合
        .body("products[?(@.rating >= 4.5 && @.reviews.size() > 10)].name", 
            hasItem("Premium Laptop"));
}

// 使用JsonPath API进行复杂处理
@Test
public void testJsonPathApi() {
    Response response = given()
        .when()
        .get("/api/orders")
        .then()
        .statusCode(200)
        .extract()
        .response();
    
    JsonPath jsonPath = response.jsonPath();
    
    // 获取所有订单的总金额
    List<Double> amounts = jsonPath.getList("orders.totalAmount");
    double total = amounts.stream().mapToDouble(Double::doubleValue).sum();
    
    // 获取特定客户的订单
    List<Map<String, Object>> customerOrders = jsonPath.get(
        "orders.findAll { it.customerId == 12345 }");
    
    // 获取最近3天的订单
    List<Map<String, Object>> recentOrders = jsonPath.get(
        "orders.findAll { it.orderDate >= '2023-11-05' }");
    
    // 获取订单中包含特定产品的所有订单
    List<Map<String, Object>> ordersWithProduct = jsonPath.get(
        "orders.findAll { it.items.find { it.productId == 'PROD-123' } != null }");
    
    // 验证计算结果
    assertTrue(total > 0, "Total amount should be greater than 0");
    assertTrue(customerOrders.size() > 0, "Customer should have orders");
    assertTrue(recentOrders.size() >= 0, "Should have recent orders");
}

// 使用Groovy GPath语法进行高级处理
@Test
public void testGroovyGPathSyntax() {
    given()
        .when()
        .get("/api/complex-data")
    .then()
        .statusCode(200)
        // 使用Groovy闭包进行条件过滤
        .body("users.findAll { it.age > 30 && it.address.city == 'New York' }.size()", 
            equalTo(5))
        
        // 使用Groovy方法进行转换
        .body("users.collect { it.name.toUpperCase()}", 
            hasItems("JOHN DOE", "JANE SMITH"))
        
        // 使用Groovy进行排序
        .body("users.sort { it.age }.collect { it.name }[0]", 
            equalTo("Youngest User"))
        
        // 使用Groovy进行分组
        .body("users.groupBy { it.department }.collectEntries { k, v -> [k, v.size()] }", 
            hasEntry("IT", 15));
}
```

## 5.2 XML数据处理基础

### 5.2.1 XPath详解

XPath是用于在XML文档中定位节点的语言，REST Assured提供了强大的XPath支持：

```java
// 基本XPath表达式
// 绝对路径
.then().body(hasXPath("/root/user/name", equalTo("John Doe")))
.then().body(hasXPath("/catalog/book[1]/title", equalTo("Title 1")))

// 相对路径
.then().body(hasXPath("//title", hasItems("Title 1", "Title 2", "Title 3")))
.then().body(hasXPath("//book/@category", hasItems("fiction", "non-fiction")))

// 条件筛选
.then().body(hasXPath("//book[price>35]/title", hasItem("Learning XML")))
.then().body(hasXPath("//book[@category='web']/title", hasItems("XQuery Kick Start")))

// 节点数量
.then().body(hasXPath("count(//book)", equalTo("4")))
.then().body(hasXPath("count(//book[price>10])", greaterThan("0")))

// 文本内容
.then().body(hasXPath("//book[1]/title/text()", equalTo("Title 1")))
.then().body(hasXPath("string(//book[1]/title)", equalTo("Title 1")))

// 属性值
.then().body(hasXPath("//book[1]/@category", equalTo("web")))
.then().body(hasXPath("//book/@category", hasItems("web", "fiction", "children")))

// 使用命名空间
.then().body(hasXPath("//ns:user/ns:name", 
    namespace("ns", "http://example.com/namespace"),
    equalTo("John")))
```

### 5.2.2 XML处理高级技巧

```java
// 复杂XPath表达式
@Test
public void testComplexXPath() {
    given()
        .when()
        .get("/api/products.xml")
    .then()
        .statusCode(200)
        
        // 多条件筛选
        .body(hasXPath("//product[category='electronics' and price>100]/name", 
            hasItem("Smartphone")))
        
        // 使用函数
        .body(hasXPath("//product[contains(name, 'Phone')]/name", 
            hasItems("Smartphone", "iPhone")))
        
        // 使用轴选择器
        .body(hasXPath("//product[price>100]/ancestor::catalog/@version", 
            equalTo("2.0")))
        
        // 数值计算
        .body(hasXPath("sum(//product/price)", greaterThan("1000")))
        
        // 字符串操作
        .body(hasXPath("concat(//user/firstName, ' ', //user/lastName)", 
            equalTo("John Doe")));
}

// XML与命名空间处理
@Test
public void testXmlNamespaceHandling() {
    given()
        .when()
        .get("/api/namespace-data.xml")
    .then()
        .statusCode(200)
        
        // 定义多个命名空间
        .body(hasXPath("//ns:user/ns:name", 
            Map.of(
                "ns", "http://example.com/namespace",
                "xsi", "http://www.w3.org/2001/XMLSchema-instance"
            ),
            equalTo("John")))
        
        // 使用默认命名空间
        .body(hasXPath("//name", 
            namespace("", "http://example.com/default-namespace"),
            equalTo("Default Value")));
}
```

## 5.3 JSON与XML序列化/反序列化

### 5.3.1 对象序列化与反序列化

```java
// Java模型类
public class User {
    private int id;
    private String name;
    private String email;
    private Address address;
    private List<String> roles;
    private Date createdAt;
    
    // 构造函数、getter和setter方法
}

public class Address {
    private String street;
    private String city;
    private String zipCode;
    private GeoLocation coordinates;
    
    // 构造函数、getter和setter方法
}

public class GeoLocation {
    private double latitude;
    private double longitude;
    
    // 构造函数、getter和setter方法
}

// JSON序列化
@Test
public void testJsonSerialization() {
    Address address = new Address("123 Main St", "New York", "10001", 
        new GeoLocation(40.7128, -74.0060));
    
    User user = new User(1, "John Doe", "john.doe@example.com", 
        address, Arrays.asList("user", "admin"), new Date());
    
    given()
        .contentType(ContentType.JSON)
        .body(user)  // 自动序列化为JSON
    .when()
        .post("/api/users")
    .then()
        .statusCode(201)
        .body("id", notNullValue())
        .body("name", equalTo(user.getName()))
        .body("email", equalTo(user.getEmail()))
        .body("address.city", equalTo(user.getAddress().getCity()))
        .body("roles", hasItems(user.getRoles().toArray()));
}

// XML序列化
@Test
public void testXmlSerialization() {
    User user = new User(1, "John Doe", "john.doe@example.com", 
        new Address("123 Main St", "New York", "10001", null),
        Arrays.asList("user", "admin"), new Date());
    
    given()
        .contentType(ContentType.XML)
        .body(user, ObjectMapperType.JAXB)  // 使用JAXB序列化为XML
    .when()
        .post("/api/users")
    .then()
        .statusCode(201)
        .body(hasXPath("//user/name", equalTo("John Doe")))
        .body(hasXPath("//user/email", equalTo("john.doe@example.com")));
}

// 反序列化
@Test
public void testDeserialization() {
    User createdUser = given()
        .contentType(ContentType.JSON)
        .body(createUserJson())
    .when()
        .post("/api/users")
    .then()
        .statusCode(201)
        .extract()
        .as(User.class);  // 反序列化为Java对象
    
    // 验证反序列化的对象
    assertNotNull(createdUser.getId());
    assertEquals("John Doe", createdUser.getName());
    assertEquals("john.doe@example.com", createdUser.getEmail());
    assertNotNull(createdUser.getAddress());
    assertEquals("New York", createdUser.getAddress().getCity());
    assertTrue(createdUser.getRoles().contains("user"));
}
```

### 5.3.2 自定义序列化配置

```java
// 使用Jackson自定义配置
@Test
public void testCustomJacksonSerialization() {
    ObjectMapper mapper = new ObjectMapper();
    
    // 配置序列化选项
    mapper.setSerializationInclusion(JsonInclude.Include.NON_NULL);
    mapper.configure(SerializationFeature.INDENT_OUTPUT, true);
    mapper.configure(SerializationFeature.WRITE_DATES_AS_TIMESTAMPS, false);
    mapper.setDateFormat(new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss.SSSZ"));
    
    // 注册自定义模块
    SimpleModule module = new SimpleModule();
    module.addSerializer(Date.class, new CustomDateSerializer());
    mapper.registerModule(module);
    
    User user = createUser();
    
    given()
        .contentType(ContentType.JSON)
        .body(mapper.writeValueAsString(user))
    .when()
        .post("/api/users")
    .then()
        .statusCode(201);
}

// 自定义日期序列化器
public class CustomDateSerializer extends JsonSerializer<Date> {
    private SimpleDateFormat dateFormat = new SimpleDateFormat("yyyy-MM-dd");
    
    @Override
    public void serialize(Date date, JsonGenerator gen, SerializerProvider provider) 
            throws IOException {
        gen.writeString(dateFormat.format(date));
    }
}

// 使用Gson自定义配置
@Test
public void testCustomGsonSerialization() {
    Gson gson = new GsonBuilder()
        .setDateFormat("yyyy-MM-dd")
        .excludeFieldsWithoutExposeAnnotation()
        .setPrettyPrinting()
        .create();
    
    User user = createUser();
    
    given()
        .contentType(ContentType.JSON)
        .body(gson.toJson(user))
    .when()
        .post("/api/users")
    .then()
        .statusCode(201);
}

// JAXB XML自定义配置
@XmlRootElement(name = "user")
@XmlAccessorType(XmlAccessType.FIELD)
public class JaxbUser {
    @XmlAttribute
    private int id;
    
    @XmlElement
    private String name;
    
    @XmlElement
    private String email;
    
    @XmlElement(name = "address")
    private JaxbAddress address;
    
    @XmlElementWrapper(name = "roles")
    @XmlElement(name = "role")
    private List<String> roles;
    
    @XmlElement(name = "created_at")
    @XmlJavaTypeAdapter(DateAdapter.class)
    private Date createdAt;
    
    // 构造函数、getter和setter方法
}

// 自定义日期适配器
public class DateAdapter extends XmlAdapter<String, Date> {
    private SimpleDateFormat dateFormat = new SimpleDateFormat("yyyy-MM-dd");
    
    @Override
    public Date unmarshal(String v) throws Exception {
        return dateFormat.parse(v);
    }
    
    @Override
    public String marshal(Date v) throws Exception {
        return dateFormat.format(v);
    }
}
```

## 5.4 数据转换与处理

### 5.4.1 JSON数据转换

```java
// 提取并转换JSON数据
@Test
public void testJsonDataTransformation() {
    Response response = given()
        .when()
        .get("/api/products")
        .then()
        .statusCode(200)
        .extract()
        .response();
    
    JsonPath jsonPath = response.jsonPath();
    
    // 获取所有产品价格并计算总和
    List<Double> prices = jsonPath.getList("products[*].price");
    double totalRevenue = prices.stream().mapToDouble(Double::doubleValue).sum();
    
    // 获取特定分类的产品并转换为对象列表
    List<Map<String, Object>> electronicsProducts = jsonPath.get(
        "products.findAll { it.category == 'electronics' }");
    
    List<Product> electronics = electronicsProducts.stream()
        .map(map -> convertMapToProduct(map))
        .collect(Collectors.toList());
    
    // 按价格排序产品
    List<Map<String, Object>> sortedProducts = jsonPath.get(
        "products.sort { it.price }");
    
    // 分组产品按分类
    Map<String, List<Map<String, Object>>> groupedProducts = jsonPath.get(
        "products.groupBy { it.category }");
    
    // 验证转换结果
    assertTrue(totalRevenue > 0, "Total revenue should be positive");
    assertFalse(electronics.isEmpty(), "Should have electronics products");
    assertTrue(sortedProducts.size() > 0, "Should have sorted products");
    assertFalse(groupedProducts.isEmpty(), "Should have grouped products");
}

// 使用JsonPath进行复杂数据操作
@Test
public void testComplexJsonOperations() {
    given()
        .when()
        .get("/api/complex-data")
    .then()
        .statusCode(200)
        
        // 计算订单总数
        .body("orders.size()", greaterThan(0))
        
        // 计算所有订单的总金额
        .body("orders.collect { it.items.collect { it.price * it.quantity }.sum() }.sum()", 
            greaterThan(0.0))
        
        // 找出最贵的订单
        .body("orders.max { it.totalAmount }.id", notNullValue())
        
        // 计算每个客户的平均订单金额
        .body("orders.groupBy { it.customerId }.collectEntries { k, v -> [k, v.sum { it.totalAmount } / v.size()] }", 
            notNullValue())
        
        // 找出包含特定产品的所有订单
        .body("orders.findAll { it.items.find { it.productId == 'PROD-123' } != null }.size()", 
            greaterThan(0));
}

// 自定义JSON转换方法
public static class JsonDataConverter {
    
    public static List<User> extractUsers(Response response) {
        JsonPath jsonPath = response.jsonPath();
        List<Map<String, Object>> userMaps = jsonPath.getList("users[*]");
        
        return userMaps.stream()
            .map(JsonDataConverter::convertMapToUser)
            .collect(Collectors.toList());
    }
    
    public static User extractUser(Response response, String jsonPath) {
        JsonPath path = response.jsonPath();
        Map<String, Object> userMap = path.getMap(jsonPath);
        
        return convertMapToUser(userMap);
    }
    
    public static double calculateTotalAmount(Response response) {
        JsonPath jsonPath = response.jsonPath();
        List<Double> amounts = jsonPath.getList("orders[*].totalAmount");
        
        return amounts.stream()
            .mapToDouble(Double::doubleValue)
            .sum();
    }
    
    private static User convertMapToUser(Map<String, Object> map) {
        User user = new User();
        user.setId((Integer) map.get("id"));
        user.setName((String) map.get("name"));
        user.setEmail((String) map.get("email"));
        
        // 转换嵌套对象
        Map<String, Object> addressMap = (Map<String, Object>) map.get("address");
        if (addressMap != null) {
            Address address = new Address();
            address.setStreet((String) addressMap.get("street"));
            address.setCity((String) addressMap.get("city"));
            address.setZipCode((String) addressMap.get("zipCode"));
            user.setAddress(address);
        }
        
        // 转换列表
        List<String> roles = (List<String>) map.get("roles");
        if (roles != null) {
            user.setRoles(new ArrayList<>(roles));
        }
        
        // 转换日期
        String createdAtStr = (String) map.get("createdAt");
        if (createdAtStr != null) {
            try {
                SimpleDateFormat format = new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss");
                user.setCreatedAt(format.parse(createdAtStr));
            } catch (ParseException e) {
                // 处理日期解析错误
            }
        }
        
        return user;
    }
}
```

### 5.4.2 XML数据转换

```java
// 提取并转换XML数据
@Test
public void testXmlDataTransformation() {
    Response response = given()
        .when()
        .get("/api/products.xml")
        .then()
        .statusCode(200)
        .extract()
        .response();
    
    // 使用XmlPath提取数据
    XmlPath xmlPath = response.xmlPath();
    
    // 获取所有产品名称
    List<String> productNames = xmlPath.getList("catalog.product.name");
    
    // 获取所有产品价格并转换为Double
    List<Double> productPrices = xmlPath.getList("catalog.product.price.doubleValue()");
    
    // 计算总收入
    double totalRevenue = productPrices.stream()
        .mapToDouble(Double::doubleValue)
        .sum();
    
    // 获取特定分类的产品
    List<Node> electronicsProducts = xmlPath.getNodeList("catalog.product[category='electronics']");
    
    // 转换为Product对象
    List<Product> products = electronicsProducts.stream()
        .map(XmlDataConverter::convertNodeToProduct)
        .collect(Collectors.toList());
    
    // 验证转换结果
    assertFalse(productNames.isEmpty(), "Should have product names");
    assertTrue(totalRevenue > 0, "Total revenue should be positive");
    assertFalse(products.isEmpty(), "Should have electronics products");
}

// 使用XPath进行复杂XML操作
@Test
public void testComplexXmlOperations() {
    given()
        .when()
        .get("/api/orders.xml")
    .then()
        .statusCode(200)
        
        // 计算订单总数
        .body(hasXPath("count(//order)", greaterThan("0")))
        
        // 计算总金额
        .body(hasXPath("sum(//order/totalAmount)", greaterThan("0")))
        
        // 获取总金额最大的订单
        .body(hasXPath("//order[totalAmount = max(//order/totalAmount)]/id", 
            notNullValue()))
        
        // 按状态分组订单
        .body(hasXPath("count(//order[status='pending'])", notNullValue()))
        .body(hasXPath("count(//order[status='completed'])", notNullValue()))
        .body(hasXPath("count(//order[status='cancelled'])", notNullValue()));
        
        // 找出包含特定产品的订单
        .body(hasXPath("//order[items/item/productId='PROD-123']/id", 
            notNullValue()));
}

// 自定义XML转换方法
public static class XmlDataConverter {
    
    public static List<Product> extractProducts(Response response) {
        XmlPath xmlPath = response.xmlPath();
        List<Node> productNodes = xmlPath.getNodeList("//product");
        
        return productNodes.stream()
            .map(XmlDataConverter::convertNodeToProduct)
            .collect(Collectors.toList());
    }
    
    public static Product extractProduct(Response response, String xpath) {
        XmlPath xmlPath = response.xmlPath();
        Node productNode = xmlPath.getNode(xpath);
        
        return convertNodeToProduct(productNode);
    }
    
    private static Product convertNodeToProduct(Node node) {
        Product product = new Product();
        
        // 使用XmlPath从节点中提取数据
        XmlPath nodePath = new XmlPath(node.asString());
        
        product.setId(nodePath.getInt("@id"));
        product.setName(nodePath.getString("name"));
        product.setCategory(nodePath.getString("category"));
        product.setPrice(nodePath.getDouble("price"));
        
        // 处理规格（嵌套元素）
        if (nodePath.getNode("specs") != null) {
            ProductSpecs specs = new ProductSpecs();
            specs.setColor(nodePath.getString("specs/color"));
            specs.setSize(nodePath.getString("specs/size"));
            specs.setWeight(nodePath.getDouble("specs/weight"));
            product.setSpecs(specs);
        }
        
        // 处理属性
        List<String> attributes = nodePath.getList("attributes/attribute");
        if (!attributes.isEmpty()) {
            product.setAttributes(new ArrayList<>(attributes));
        }
        
        return product;
    }
}
```

## 5.5 高级数据结构处理

### 5.5.1 复杂嵌套结构处理

```java
// 处理深度嵌套的JSON结构
@Test
public void testDeeplyNestedJsonStructures() {
    given()
        .when()
        .get("/api/complex-nested-data")
    .then()
        .statusCode(200)
        
        // 验证深度嵌套属性
        .body("data.users[0].profile.personal.fullName.firstName", equalTo("John"))
        .body("data.users[0].profile.personal.fullName.lastName", equalTo("Doe"))
        .body("data.users[0].profile.contact.addresses[0].street", notNullValue())
        .body("data.users[0].profile.contact.addresses[0].city", notNullValue())
        
        // 验证数组中的嵌套对象
        .body("data.users[0].orders[*].items[*].product.details.specs.size()", 
            everyItem(greaterThan(0)))
        
        // 验证深度嵌套数组
        .body("data.categories[0].subcategories[0].items[0].metadata.tags[0]", 
            notNullValue());
}

// 动态结构处理
@Test
public void testDynamicJsonStructures() {
    Response response = given()
        .when()
        .get("/api/dynamic-data")
        .then()
        .statusCode(200)
        .extract()
        .response();
    
    JsonPath jsonPath = response.jsonPath();
    Map<String, Object> root = jsonPath.get("$");
    
    // 处理动态属性
    for (Map.Entry<String, Object> entry : root.entrySet()) {
        String key = entry.getKey();
        Object value = entry.getValue();
        
        if (value instanceof Map) {
            // 处理嵌套对象
            processNestedObject(key, (Map<String, Object>) value);
        } else if (value instanceof List) {
            // 处理数组
            processArray(key, (List<Object>) value);
        } else {
            // 处理基本类型
            processBasicType(key, value);
        }
    }
}

private void processNestedObject(String key, Map<String, Object> object) {
    // 验证对象必需字段
    if (object.containsKey("id")) {
        assertNotNull(object.get("id"), "Object should have an id");
    }
    
    // 递归处理嵌套结构
    for (Map.Entry<String, Object> entry : object.entrySet()) {
        if (entry.getValue() instanceof Map) {
            processNestedObject(key + "." + entry.getKey(), (Map<String, Object>) entry.getValue());
        } else if (entry.getValue() instanceof List) {
            processArray(key + "." + entry.getKey(), (List<Object>) entry.getValue());
        }
    }
}

private void processArray(String key, List<Object> array) {
    for (int i = 0; i < array.size(); i++) {
        Object item = array.get(i);
        if (item instanceof Map) {
            processNestedObject(key + "[" + i + "]", (Map<String, Object>) item);
        } else if (item instanceof List) {
            processArray(key + "[" + i + "]", (List<Object>) item);
        }
    }
}

private void processBasicType(String key, Object value) {
    // 根据键名验证值的类型和格式
    if (key.endsWith("Id") || key.endsWith("ID")) {
        assertTrue(value instanceof Integer || value instanceof String,
            "ID field should be Integer or String");
    } else if (key.endsWith("Date") || key.endsWith("At")) {
        if (value instanceof String) {
            assertTrue(((String) value).matches("\\d{4}-\\d{2}-\\d{2}.*"),
                "Date field should match date pattern");
        }
    } else if (key.endsWith("Email") || key.endsWith("email")) {
        if (value instanceof String) {
            assertTrue(((String) value).matches("[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}"),
                "Email field should match email pattern");
        }
    }
}
```

### 5.5.2 多态与类型转换

```java
// 处理多态JSON结构
@JsonTypeInfo(use = JsonTypeInfo.Id.NAME, property = "type")
@JsonSubTypes({
    @JsonSubTypes.Type(value = CreditCardPayment.class, name = "credit_card"),
    @JsonSubTypes.Type(value = PayPalPayment.class, name = "paypal"),
    @JsonSubTypes.Type(value = BankTransferPayment.class, name = "bank_transfer")
})
public abstract class Payment {
    private String id;
    private double amount;
    private Date createdAt;
    
    // 公共方法和抽象方法
    public abstract boolean validate();
    
    // getter和setter方法
}

public class CreditCardPayment extends Payment {
    private String cardNumber;
    private String cardholderName;
    private String expiryDate;
    private String cvv;
    
    @Override
    public boolean validate() {
        // 验证信用卡信息的逻辑
        return true;
    }
    
    // getter和setter方法
}

// 处理多态JSON反序列化
@Test
public void testPolymorphicJsonDeserialization() {
    String paymentsJson = "[\n" +
        "  {\"type\": \"credit_card\", \"amount\": 100.0, \"cardNumber\": \"4111...\"},\n" +
        "  {\"type\": \"paypal\", \"amount\": 50.0, \"email\": \"user@example.com\"},\n" +
        "  {\"type\": \"bank_transfer\", \"amount\": 200.0, \"accountNumber\": \"12345\"}\n" +
        "]";
    
    ObjectMapper mapper = new ObjectMapper();
    
    // 配置多态类型处理
    mapper.registerModule(new ParameterNamesModule());
    mapper.registerModule(new Jdk8Module());
    mapper.registerModule(new JavaTimeModule());
    
    try {
        List<Payment> payments = mapper.readValue(paymentsJson, 
            new TypeReference<List<Payment>>() {});
        
        // 验证反序列化结果
        assertEquals(3, payments.size());
        assertTrue(payments.get(0) instanceof CreditCardPayment);
        assertTrue(payments.get(1) instanceof PayPalPayment);
        assertTrue(payments.get(2) instanceof BankTransferPayment);
        
        // 验证每个支付方式
        for (Payment payment : payments) {
            assertTrue(payment.validate());
            assertTrue(payment.getAmount() > 0);
            assertNotNull(payment.getCreatedAt());
        }
    } catch (Exception e) {
        fail("Failed to deserialize polymorphic JSON: " + e.getMessage());
    }
}

// 类型转换处理
@Test
public void testTypeConversionHandling() {
    given()
        .when()
        .get("/api/mixed-data-types")
    .then()
        .statusCode(200)
        
        // 处理数字类型转换
        .body("integerValue", instanceOf(Integer.class))
        .body("floatValue", instanceOf(Double.class))
        
        // 处理字符串到数字的转换
        .body("numericString", isA(String.class))
        
        // 处理布尔值的各种表示
        .body("booleanValue", instanceOf(Boolean.class))
        .body("booleanString", isA(String.class))
        
        // 处理日期和时间
        .body("dateString", isA(String.class))
        .body("timestampString", isA(String.class));
}

// 自定义类型转换
public class CustomTypeConverter {
    
    public static Date convertStringToDate(String dateString) {
        List<String> dateFormats = Arrays.asList(
            "yyyy-MM-dd",
            "yyyy-MM-dd'T'HH:mm:ss",
            "yyyy-MM-dd'T'HH:mm:ss.SSS",
            "MM/dd/yyyy",
            "dd/MM/yyyy"
        );
        
        for (String format : dateFormats) {
            try {
                return new SimpleDateFormat(format).parse(dateString);
            } catch (ParseException e) {
                // 尝试下一个格式
            }
        }
        
        throw new IllegalArgumentException("Unable to parse date: " + dateString);
    }
    
    public static Double convertToDouble(Object value) {
        if (value instanceof Number) {
            return ((Number) value).doubleValue();
        } else if (value instanceof String) {
            try {
                return Double.parseDouble((String) value);
            } catch (NumberFormatException e) {
                return null;
            }
        }
        return null;
    }
    
    public static Boolean convertToBoolean(Object value) {
        if (value instanceof Boolean) {
            return (Boolean) value;
        } else if (value instanceof String) {
            String strValue = ((String) value).toLowerCase();
            return "true".equals(strValue) || "yes".equals(strValue) || "1".equals(strValue);
        } else if (value instanceof Number) {
            return ((Number) value).intValue() != 0;
        }
        return false;
    }
}
```

## 5.6 大数据量处理

### 5.6.1 流式处理

```java
// 处理大型JSON响应
@Test
public void testLargeJsonResponseHandling() {
    // 使用流式处理避免内存溢出
    given()
        .when()
        .get("/api/large-dataset")
    .then()
        .statusCode(200)
        .header("Content-Type", containsString("application/json"))
    .extract()
    .asInputStream();  // 获取输入流而不是完全加载到内存
    
    // 或者使用响应体字符串处理但限制大小
    given()
        .when()
        .get("/api/large-dataset")
    .then()
        .statusCode(200)
        .body(matchesPattern(".*\"total\":\\d+,.*"))  // 验证部分内容而不是全部
        .body(matchesPattern(".*\"items\":\\[.*"));  // 确认数组存在
}

// 分页处理大型数据集
@Test
public void testPaginatedDataProcessing() {
    int pageSize = 100;
    int maxPages = 10;
    List<User> allUsers = new ArrayList<>();
    
    for (int page = 1; page <= maxPages; page++) {
        Response response = given()
            .queryParam("page", page)
            .queryParam("size", pageSize)
        .when()
            .get("/api/users")
        .then()
            .statusCode(200)
            .extract()
            .response();
        
        // 提取用户数据
        List<User> pageUsers = JsonPath.from(response.asString())
            .getList("users", User.class);
        
        if (pageUsers.isEmpty()) {
            break; // 没有更多数据
        }
        
        allUsers.addAll(pageUsers);
        
        // 处理当前页数据（例如验证）
        for (User user : pageUsers) {
            assertNotNull(user.getId());
            assertNotNull(user.getName());
            assertNotNull(user.getEmail());
        }
    }
    
    // 验证处理了足够的数据
    assertTrue(allUsers.size() > 0, "Should have processed at least some users");
}

// 使用JsonPath的流式API处理大型JSON
@Test
public void testJsonPathStreamProcessing() {
    Response response = given()
        .when()
        .get("/api/large-products")
    .then()
        .statusCode(200)
        .extract()
        .response();
    
    JsonPath jsonPath = response.jsonPath();
    
    // 使用流式处理查找特定产品
    List<Product> expensiveProducts = jsonPath.getList(
        "products.findAll { it.price > 1000 }", Product.class);
    
    // 使用流式处理统计信息
    Double averagePrice = jsonPath.getDouble(
        "products.collect { it.price }.sum() / products.size()");
    
    // 使用流式处理分类统计
    Map<String, Integer> categoryCounts = jsonPath.getMap(
        "products.groupBy { it.category }.collectEntries { k, v -> [k, v.size()] }");
    
    // 验证结果
    assertFalse(expensiveProducts.isEmpty(), "Should have expensive products");
    assertTrue(averagePrice > 0, "Average price should be positive");
    assertFalse(categoryCounts.isEmpty(), "Should have category counts");
}
```

### 5.6.2 性能优化技巧

```java
// 使用JsonPath直接提取特定字段而不是完整响应
@Test
public void testEfficientFieldExtraction() {
    // 不推荐：加载整个响应到内存
    Response fullResponse = given()
        .when()
        .get("/api/users")
        .then()
        .statusCode(200)
        .extract()
        .response();
    
    // 推荐：只提取需要的字段
    List<String> userNames = given()
        .when()
        .get("/api/users")
        .then()
        .statusCode(200)
        .extract()
        .jsonPath()
        .getList("users.name");
    
    // 只验证特定字段
    given()
        .when()
        .get("/api/users")
    .then()
        .statusCode(200)
        .body("users.size()", greaterThan(0))
        .body("users[0].name", notNullValue())
        .body("users[0].email", notNullValue());
}

// 使用JSONPath的缓存量提取
@Test
public void testCachedJsonPathExtraction() {
    Response response = given()
        .when()
        .get("/api/complex-data")
        .then()
        .statusCode(200)
        .extract()
        .response();
    
    // 缓存JsonPath对象以避免重复解析
    JsonPath jsonPath = response.jsonPath();
    
    // 多次使用同一个JsonPath对象
    int userCount = jsonPath.getInt("users.size()");
    List<String> userNames = jsonPath.getList("users.name");
    List<Double> userBalances = jsonPath.getList("users.balance");
    
    // 验证结果
    assertTrue(userCount > 0);
    assertFalse(userNames.isEmpty());
    assertFalse(userBalances.isEmpty());
    
    // 使用缓存的JsonPath进行复杂查询
    List<User> premiumUsers = jsonPath.getList(
        "users.findAll { it.subscription.plan == 'premium' }", User.class);
}

// 使用预编译的JSONPath表达式
public class PrecompiledJsonPaths {
    public static final JsonPath USER_NAME_PATH = JsonPath.compile("$.users[*].name");
    public static final JsonPath PREMIUM_USERS_PATH = JsonPath.compile(
        "$.users.findAll { it.subscription.plan == 'premium' }");
    public static final JsonPath TOTAL_REVENUE_PATH = JsonPath.compile(
        "$.orders.collect { it.totalAmount }.sum()");
    
    public static List<String> extractUserNames(String jsonResponse) {
        return USER_NAME_PATH.extract(jsonResponse).getList("$");
    }
    
    public static List<User> extractPremiumUsers(String jsonResponse) {
        return PREMIUM_USERS_PATH.extract(jsonResponse).getList("$", User.class);
    }
    
    public static Double extractTotalRevenue(String jsonResponse) {
        return TOTAL_REVENUE_PATH.extract(jsonResponse).getDouble("$");
    }
}
```

## 5.7 实践练习

### 练习1：复杂JSON处理

创建一个测试，处理包含以下元素的JSON响应：
- 多层嵌套结构
- 数组中的对象
- 动态属性
- 不同数据类型

### 练习2：XML数据处理

创建一个测试，处理包含以下元素的XML响应：
- 命名空间
- 属性和元素
- 嵌套结构
- 条件筛选

### 练习3：性能优化

实现一个测试，处理大型数据集，使用以下技巧：
- 分页处理
- 流式处理
- 选择性字段提取
- JsonPath缓存

## 5.8 总结

本章深入探讨了REST Assured中的JSON与XML数据处理技术，包括：

1. **JSON数据处理基础** - 掌握JSONPath表达式和高级处理技巧
2. **XML数据处理基础** - 学习XPath表达式和高级XML处理
3. **对象序列化/反序列化** - 了解JSON和XML与Java对象之间的转换
4. **数据转换与处理** - 掌握复杂的数据转换和处理技术
5. **高级数据结构处理** - 学习处理嵌套结构、动态结构和多态
6. **大数据量处理** - 掌握流式处理和性能优化技巧

通过本章的学习，您应该能够处理各种复杂的JSON和XML数据结构，进行高效的数据提取和转换，并优化大数据量处理的性能。在下一章中，我们将学习身份验证与安全测试的技术。