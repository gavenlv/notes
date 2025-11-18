# 第7章代码示例 - Selenium数据驱动与参数化测试

本目录包含第7章"Selenium数据驱动与参数化测试"的代码示例，涵盖以下内容：

## 代码示例说明

### 1. 数据驱动测试示例
- **ExcelDataProviderTest.java** - 演示Excel作为数据源
- **CSVDataProviderTest.java** - 演示CSV作为数据源
- **JSONDataProviderTest.java** - 演示JSON作为数据源
- **DatabaseDataProviderTest.java** - 演示数据库作为数据源

### 2. TestNG参数化示例
- **TestNGParameterTest.java** - 演示TestNG参数化
- **TestNGDataProviderTest.java** - 演示TestNG数据提供者
- **TestNGFactoryTest.java** - 演示TestNG工厂模式

### 3. 自定义数据提供者示例
- **CustomDataProvider.java** - 自定义数据提供者
- **DataValidationTest.java** - 数据验证测试
- **DataTransformationTest.java** - 数据转换测试

### 4. 测试数据管理示例
- **TestDataGenerator.java** - 测试数据生成器
- **TestDataCleaner.java** - 测试数据清理器
- **TestDataValidator.java** - 测试数据验证器

### 5. 实用工具类
- **ExcelUtils.java** - Excel处理工具
- **CSVUtils.java** - CSV处理工具
- **JSONUtils.java** - JSON处理工具
- **DatabaseUtils.java** - 数据库连接工具

## 运行说明

1. 使用Maven运行测试：`mvn test`
2. 使用TestNG运行：`mvn test -DsuiteXmlFile=testng.xml`
3. 在IDE中直接运行测试类

## 环境要求

- Java 11+
- Maven 3.6+
- Chrome浏览器
- ChromeDriver（由WebDriverManager自动管理）
- MySQL数据库（可选，用于数据库数据提供者示例）

## 项目结构

```
src/test/java/com/example/selenium/tests/
├── ExcelDataProviderTest.java      # Excel数据提供者测试
├── CSVDataProviderTest.java        # CSV数据提供者测试
├── JSONDataProviderTest.java       # JSON数据提供者测试
├── DatabaseDataProviderTest.java    # 数据库数据提供者测试
├── TestNGParameterTest.java         # TestNG参数化测试
├── TestNGDataProviderTest.java     # TestNG数据提供者测试
├── TestNGFactoryTest.java           # TestNG工厂模式测试
├── DataValidationTest.java         # 数据验证测试
├── DataTransformationTest.java      # 数据转换测试
└── ComplexScenarioTest.java        # 复杂场景测试

src/main/java/com/example/selenium/utils/
├── ExcelUtils.java                  # Excel处理工具
├── CSVUtils.java                    # CSV处理工具
├── JSONUtils.java                   # JSON处理工具
├── DatabaseUtils.java               # 数据库连接工具
├── TestDataGenerator.java           # 测试数据生成器
├── TestDataCleaner.java             # 测试数据清理器
└── TestDataValidator.java           # 测试数据验证器

src/test/resources/
├── test-data.xlsx                   # Excel测试数据
├── test-data.csv                    # CSV测试数据
├── test-data.json                   # JSON测试数据
├── test-config.properties           # 测试配置
└── db-config.properties             # 数据库配置
```

## 设计原则

1. **数据与逻辑分离** - 测试数据与测试逻辑分离
2. **可维护性** - 测试数据易于管理和维护
3. **可扩展性** - 支持多种数据源格式
4. **数据验证** - 对测试数据进行验证
5. **错误处理** - 处理数据读取和解析错误

## 最佳实践

1. 使用有意义的测试数据，提高测试覆盖率
2. 对敏感数据进行脱敏处理
3. 为测试数据建立版本控制
4. 实现测试数据的清理机制
5. 使用参数化测试减少重复代码
6. 为数据驱动测试提供清晰的命名约定
7. 实现测试数据的生成和验证工具
8. 考虑测试数据的性能影响