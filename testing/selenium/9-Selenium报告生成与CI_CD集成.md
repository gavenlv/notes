# 第9章：Selenium报告生成与CI/CD集成

## 📖 章节介绍

本章将深入探讨Selenium测试报告生成技术与CI/CD集成方法。在现代化软件开发流程中，自动化测试不仅需要可靠执行，还需要提供清晰、详细的测试报告，并能无缝集成到持续集成和持续部署（CI/CD）流水线中。通过本章的学习，您将掌握各种测试报告生成技术，学会使用主流CI/CD工具集成测试，并了解如何设计高效的自动化测试流水线。

## 🎯 学习目标

- 理解测试报告的重要性和分类
- 掌握Extent Reports、Allure等主流报告工具的使用
- 学会生成自定义报告和报告聚合
- 了解Jenkins、GitHub Actions等CI/CD工具的测试集成
- 掌握测试结果通知和监控机制
- 学会设计完整的自动化测试流水线

## 9.1 测试报告概述

### 9.1.1 测试报告的重要性

测试报告是自动化测试流程中不可或缺的一环，它提供了关于测试执行结果的全面视图：

#### 为什么需要测试报告
1. **结果可视化**：将测试结果以直观的方式呈现
2. **问题诊断**：帮助快速定位和分析测试失败原因
3. **质量评估**：提供软件质量的量化指标
4. **历史对比**：记录测试结果的历史趋势
5. **决策支持**：为发布决策提供数据支持
6. **团队沟通**：为开发团队和利益相关者提供共享信息

#### 优秀测试报告的特点
1. **全面性**：包含测试执行的各个方面
2. **易读性**：信息结构清晰，易于理解
3. **可操作性**：提供足够信息支持问题修复
4. **可追溯性**：能够追踪测试结果到具体变更
5. **实时性**：及时反映测试执行状态
6. **可定制性**：能够根据不同需求定制报告内容

### 9.1.2 测试报告的类型

根据不同的使用场景和详细程度，测试报告可以分为多种类型：

#### 按详细程度分类
1. **概要报告**：高层次的测试结果概述
2. **详细报告**：包含每个测试用例的详细执行信息
3. **分析报告**：对测试结果进行深入分析和趋势分析
4. **缺陷报告**：针对测试失败生成的详细缺陷信息

#### 按受众分类
1. **技术报告**：面向开发和测试团队
2. **管理报告**：面向项目管理者和利益相关者
3. **客户报告**：面向最终客户或用户

#### 按时间范围分类
1. **实时报告**：测试执行过程中的实时状态
2. **单次执行报告**：单次测试运行的完整报告
3. **周期报告**：特定时间段（如每日、每周）的测试汇总报告
4. **版本报告**：特定软件版本的测试结果报告

## 9.2 TestNG默认报告

### 9.2.1 TestNG内置报告

TestNG提供了内置的报告功能，在测试执行完成后会自动生成报告：

```xml
<!-- 测试配置示例 -->
<!DOCTYPE suite SYSTEM "https://testng.org/testng-1.0.dtd">
<suite name="Sample Test Suite">
    <listeners>
        <!-- 使用默认的TestNG监听器 -->
        <listener class-name="org.testng.reporters.TestHTMLReporter"/>
        <listener class-name="org.testng.reporters.JUnitReportReporter"/>
        <listener class-name="org.testng.reporters.XMLReporter"/>
    </listeners>
    
    <test name="Sample Test">
        <classes>
            <class name="com.example.tests.SampleTestClass"/>
        </classes>
    </test>
</suite>
```

#### TestNG默认报告文件
1. **index.html**：HTML格式的概要报告
2. **emailable-report.html**：邮件友好的HTML报告
3. **testng-results.xml**：XML格式的详细结果
4. **junitreports/**：JUnit格式的XML报告

#### TestNG报告结构
```
test-output/
├── index.html                    # 概要报告
├── emailable-report.html          # 邮件报告
├── testng-results.xml             # XML格式结果
├── junitreports/                  # JUnit格式报告
│   ├── TEST-com.example.tests.SampleTestClass.xml
│   └── ...
├── failed_tests/                  # 失败测试详情
│   ├── SampleTestClass.html
│   └── ...
└── suites/                        # 测试套件详情
    ├── Sample Test Suite.html
    └── ...
```

### 9.2.2 自定义TestNG报告

通过实现TestNG的IReporter接口，可以创建自定义报告：

```java
// CustomReporter.java - 自定义报告生成器
public class CustomReporter implements IReporter {
    private static final String OUTPUT_DIR = "custom-reports";
    
    @Override
    public void generateReport(List<XmlSuite> xmlSuites, List<ISuite> suites, 
                               String outputDirectory) {
        // 创建输出目录
        new File(OUTPUT_DIR).mkdirs();
        
        // 生成JSON格式报告
        generateJsonReport(suites);
        
        // 生成Markdown格式报告
        generateMarkdownReport(suites);
        
        // 生成自定义HTML报告
        generateCustomHtmlReport(suites);
    }
    
    /**
     * 生成JSON格式报告
     */
    private void generateJsonReport(List<ISuite> suites) {
        Map<String, Object> reportData = new HashMap<>();
        reportData.put("timestamp", System.currentTimeMillis());
        reportData.put("suites", suites.size());
        
        List<Map<String, Object>> suiteResults = new ArrayList<>();
        int totalTests = 0;
        int totalPassed = 0;
        int totalFailed = 0;
        int totalSkipped = 0;
        
        for (ISuite suite : suites) {
            Map<String, Object> suiteResult = new HashMap<>();
            suiteResult.put("name", suite.getName());
            
            ISuiteResult suiteResultObj = suite.getResults().values().iterator().next();
            ITestContext testContext = suiteResultObj.getTestContext();
            
            int passed = testContext.getPassedTests().size();
            int failed = testContext.getFailedTests().size();
            int skipped = testContext.getSkippedTests().size();
            int total = passed + failed + skipped;
            
            suiteResult.put("passed", passed);
            suiteResult.put("failed", failed);
            suiteResult.put("skipped", skipped);
            suiteResult.put("total", total);
            
            // 添加失败测试详情
            List<Map<String, Object>> failedTests = new ArrayList<>();
            for (ITestResult result : testContext.getFailedTests().getAllResults()) {
                Map<String, Object> failedTest = new HashMap<>();
                failedTest.put("name", result.getName());
                failedTest.put("className", result.getTestClass().getName());
                failedTest.put("description", result.getMethod().getDescription());
                failedTest.put("error", result.getThrowable().getMessage());
                failedTests.add(failedTest);
            }
            suiteResult.put("failedTests", failedTests);
            
            suiteResults.add(suiteResult);
            
            totalTests += total;
            totalPassed += passed;
            totalFailed += failed;
            totalSkipped += skipped;
        }
        
        reportData.put("suiteResults", suiteResults);
        reportData.put("summary", Map.of(
            "total", totalTests,
            "passed", totalPassed,
            "failed", totalFailed,
            "skipped", totalSkipped,
            "passRate", totalTests > 0 ? (double) totalPassed / totalTests * 100 : 0
        ));
        
        // 写入JSON文件
        try {
            ObjectMapper mapper = new ObjectMapper();
            mapper.writerWithDefaultPrettyPrinter()
                  .writeValue(new File(OUTPUT_DIR + "/custom-report.json"), reportData);
        } catch (IOException e) {
            System.err.println("生成JSON报告失败: " + e.getMessage());
        }
    }
    
    /**
     * 生成Markdown格式报告
     */
    private void generateMarkdownReport(List<ISuite> suites) {
        StringBuilder markdown = new StringBuilder();
        
        // 报告标题
        markdown.append("# 自动化测试报告\n\n");
        markdown.append("**生成时间**: ").append(new Date()).append("\n\n");
        
        // 汇总信息
        int totalTests = 0;
        int totalPassed = 0;
        int totalFailed = 0;
        int totalSkipped = 0;
        
        for (ISuite suite : suites) {
            ISuiteResult suiteResultObj = suite.getResults().values().iterator().next();
            ITestContext testContext = suiteResultObj.getTestContext();
            
            totalTests += testContext.getAllTestMethods().length;
            totalPassed += testContext.getPassedTests().size();
            totalFailed += testContext.getFailedTests().size();
            totalSkipped += testContext.getSkippedTests().size();
        }
        
        markdown.append("## 汇总\n\n");
        markdown.append("| 总数 | 通过 | 失败 | 跳过 | 通过率 |\n");
        markdown.append("|------|------|------|------|--------|\n");
        markdown.append("| ").append(totalTests)
                  .append(" | ").append(totalPassed)
                  .append(" | ").append(totalFailed)
                  .append(" | ").append(totalSkipped)
                  .append(" | ").append(String.format("%.2f%%", 
                        totalTests > 0 ? (double) totalPassed / totalTests * 100 : 0))
                  .append(" |\n\n");
        
        // 测试套件详情
        markdown.append("## 测试套件详情\n\n");
        
        for (ISuite suite : suites) {
            markdown.append("### ").append(suite.getName()).append("\n\n");
            
            ISuiteResult suiteResultObj = suite.getResults().values().iterator().next();
            ITestContext testContext = suiteResultObj.getTestContext();
            
            int passed = testContext.getPassedTests().size();
            int failed = testContext.getFailedTests().size();
            int skipped = testContext.getSkippedTests().size();
            int total = passed + failed + skipped;
            
            markdown.append("- 总数: ").append(total).append("\n");
            markdown.append("- 通过: ").append(passed).append("\n");
            markdown.append("- 失败: ").append(failed).append("\n");
            markdown.append("- 跳过: ").append(skipped).append("\n\n");
            
            // 失败测试详情
            if (failed > 0) {
                markdown.append("#### 失败测试\n\n");
                
                for (ITestResult result : testContext.getFailedTests().getAllResults()) {
                    markdown.append("- **").append(result.getName()).append("**\n");
                    markdown.append("  - 类: `").append(result.getTestClass().getName()).append("`\n");
                    if (result.getMethod().getDescription() != null) {
                        markdown.append("  - 描述: ").append(result.getMethod().getDescription()).append("\n");
                    }
                    if (result.getThrowable() != null) {
                        markdown.append("  - 错误: `").append(result.getThrowable().getMessage()).append("`\n");
                    }
                    markdown.append("\n");
                }
            }
        }
        
        // 写入Markdown文件
        try (FileWriter writer = new FileWriter(OUTPUT_DIR + "/custom-report.md")) {
            writer.write(markdown.toString());
        } catch (IOException e) {
            System.err.println("生成Markdown报告失败: " + e.getMessage());
        }
    }
    
    /**
     * 生成自定义HTML报告
     */
    private void generateCustomHtmlReport(List<ISuite> suites) {
        StringBuilder html = new StringBuilder();
        
        // HTML头部
        html.append("<!DOCTYPE html>\n");
        html.append("<html lang=\"zh-CN\">\n");
        html.append("<head>\n");
        html.append("    <meta charset=\"UTF-8\">\n");
        html.append("    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n");
        html.append("    <title>自定义测试报告</title>\n");
        html.append("    <style>\n");
        html.append(getReportStyles());
        html.append("    </style>\n");
        html.append("</head>\n");
        html.append("<body>\n");
        
        // 报告内容
        html.append("    <div class=\"container\">\n");
        html.append("        <header>\n");
        html.append("            <h1>自动化测试报告</h1>\n");
        html.append("            <p>生成时间: ").append(new Date()).append("</p>\n");
        html.append("        </header>\n");
        
        // 汇总信息
        html.append("        <section class=\"summary\">\n");
        html.append("            <h2>测试汇总</h2>\n");
        html.append("            <div class=\"summary-cards\">\n");
        
        // 计算汇总数据
        int totalTests = 0;
        int totalPassed = 0;
        int totalFailed = 0;
        int totalSkipped = 0;
        
        for (ISuite suite : suites) {
            ISuiteResult suiteResultObj = suite.getResults().values().iterator().next();
            ITestContext testContext = suiteResultObj.getTestContext();
            
            totalTests += testContext.getAllTestMethods().length;
            totalPassed += testContext.getPassedTests().size();
            totalFailed += testContext.getFailedTests().size();
            totalSkipped += testContext.getSkippedTests().size();
        }
        
        html.append("                <div class=\"card total\">\n");
        html.append("                    <div class=\"card-value\">").append(totalTests).append("</div>\n");
        html.append("                    <div class=\"card-label\">总数</div>\n");
        html.append("                </div>\n");
        
        html.append("                <div class=\"card passed\">\n");
        html.append("                    <div class=\"card-value\">").append(totalPassed).append("</div>\n");
        html.append("                    <div class=\"card-label\">通过</div>\n");
        html.append("                </div>\n");
        
        html.append("                <div class=\"card failed\">\n");
        html.append("                    <div class=\"card-value\">").append(totalFailed).append("</div>\n");
        html.append("                    <div class=\"card-label\">失败</div>\n");
        html.append("                </div>\n");
        
        html.append("                <div class=\"card skipped\">\n");
        html.append("                    <div class=\"card-value\">").append(totalSkipped).append("</div>\n");
        html.append("                    <div class=\"card-label\">跳过</div>\n");
        html.append("                </div>\n");
        
        html.append("            </div>\n");
        html.append("            <div class=\"pass-rate\">\n");
        html.append("                <span>通过率: </span>\n");
        html.append("                <span>").append(String.format("%.2f%%", 
                    totalTests > 0 ? (double) totalPassed / totalTests * 100 : 0)).append("</span>\n");
        html.append("            </div>\n");
        html.append("        </section>\n");
        
        // 测试套件详情
        html.append("        <section class=\"suite-details\">\n");
        html.append("            <h2>测试套件详情</h2>\n");
        
        for (ISuite suite : suites) {
            html.append("            <div class=\"suite-card\">\n");
            html.append("                <div class=\"suite-header\">\n");
            html.append("                    <h3>").append(suite.getName()).append("</h3>\n");
            
            ISuiteResult suiteResultObj = suite.getResults().values().iterator().next();
            ITestContext testContext = suiteResultObj.getTestContext();
            
            int passed = testContext.getPassedTests().size();
            int failed = testContext.getFailedTests().size();
            int skipped = testContext.getSkippedTests().size();
            
            html.append("                    <div class=\"suite-stats\">\n");
            html.append("                        <span class=\"passed\">").append(passed).append(" 通过</span>\n");
            html.append("                        <span class=\"failed\">").append(failed).append(" 失败</span>\n");
            html.append("                        <span class=\"skipped\">").append(skipped).append(" 跳过</span>\n");
            html.append("                    </div>\n");
            html.append("                </div>\n");
            
            // 失败测试详情
            if (failed > 0) {
                html.append("                <div class=\"failed-tests\">\n");
                html.append("                    <h4>失败测试</h4>\n");
                
                for (ITestResult result : testContext.getFailedTests().getAllResults()) {
                    html.append("                    <div class=\"failed-test\">\n");
                    html.append("                        <h5>").append(result.getName()).append("</h5>\n");
                    html.append("                        <p><strong>类:</strong> ").append(result.getTestClass().getName()).append("</p>\n");
                    
                    if (result.getMethod().getDescription() != null) {
                        html.append("                        <p><strong>描述:</strong> ").append(result.getMethod().getDescription()).append("</p>\n");
                    }
                    
                    if (result.getThrowable() != null) {
                        html.append("                        <div class=\"error-details\">\n");
                        html.append("                            <p><strong>错误:</strong> ").append(result.getThrowable().getMessage()).append("</p>\n");
                        html.append("                            <details>\n");
                        html.append("                                <summary>堆栈跟踪</summary>\n");
                        html.append("                                <pre>").append(getStackTrace(result.getThrowable())).append("</pre>\n");
                        html.append("                            </details>\n");
                        html.append("                        </div>\n");
                    }
                    
                    html.append("                    </div>\n");
                }
                
                html.append("                </div>\n");
            }
            
            html.append("            </div>\n");
        }
        
        html.append("        </section>\n");
        html.append("    </div>\n");
        html.append("</body>\n");
        html.append("</html>\n");
        
        // 写入HTML文件
        try (FileWriter writer = new FileWriter(OUTPUT_DIR + "/custom-report.html")) {
            writer.write(html.toString());
        } catch (IOException e) {
            System.err.println("生成HTML报告失败: " + e.getMessage());
        }
    }
    
    /**
     * 获取报告样式
     */
    private String getReportStyles() {
        return """
            * {
                box-sizing: border-box;
                margin: 0;
                padding: 0;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                background-color: #f5f5f5;
            }
            
            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background-color: #fff;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            }
            
            header {
                text-align: center;
                margin-bottom: 30px;
                padding-bottom: 20px;
                border-bottom: 1px solid #eee;
            }
            
            h1 {
                color: #2c3e50;
                margin-bottom: 10px;
            }
            
            h2, h3, h4, h5 {
                color: #34495e;
                margin-top: 20px;
                margin-bottom: 10px;
            }
            
            .summary {
                margin-bottom: 40px;
            }
            
            .summary-cards {
                display: flex;
                flex-wrap: wrap;
                gap: 20px;
                margin-bottom: 20px;
            }
            
            .card {
                flex: 1;
                min-width: 150px;
                padding: 20px;
                border-radius: 8px;
                text-align: center;
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
            }
            
            .card.total {
                background-color: #3498db;
                color: white;
            }
            
            .card.passed {
                background-color: #2ecc71;
                color: white;
            }
            
            .card.failed {
                background-color: #e74c3c;
                color: white;
            }
            
            .card.skipped {
                background-color: #f39c12;
                color: white;
            }
            
            .card-value {
                font-size: 2.5em;
                font-weight: bold;
                margin-bottom: 5px;
            }
            
            .card-label {
                font-size: 1.2em;
                opacity: 0.9;
            }
            
            .pass-rate {
                text-align: center;
                font-size: 1.5em;
                font-weight: bold;
            }
            
            .pass-rate span:last-child {
                color: #2ecc71;
                margin-left: 10px;
            }
            
            .suite-details {
                margin-bottom: 40px;
            }
            
            .suite-card {
                margin-bottom: 30px;
                padding: 20px;
                border: 1px solid #ddd;
                border-radius: 8px;
                background-color: #fff;
            }
            
            .suite-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 15px;
                padding-bottom: 15px;
                border-bottom: 1px solid #eee;
            }
            
            .suite-stats {
                display: flex;
                gap: 15px;
            }
            
            .passed {
                color: #2ecc71;
                font-weight: bold;
            }
            
            .failed {
                color: #e74c3c;
                font-weight: bold;
            }
            
            .skipped {
                color: #f39c12;
                font-weight: bold;
            }
            
            .failed-tests {
                margin-top: 20px;
            }
            
            .failed-test {
                padding: 15px;
                margin-bottom: 15px;
                background-color: #fdf2f2;
                border-left: 5px solid #e74c3c;
                border-radius: 4px;
            }
            
            .error-details {
                margin-top: 10px;
            }
            
            .error-details p {
                margin-bottom: 10px;
            }
            
            details {
                margin-top: 10px;
            }
            
            summary {
                cursor: pointer;
                font-weight: bold;
                color: #7f8c8d;
            }
            
            pre {
                background-color: #f8f8f8;
                padding: 10px;
                border-radius: 4px;
                overflow-x: auto;
                font-family: 'Courier New', Courier, monospace;
                font-size: 0.9em;
            }
            
            @media (max-width: 768px) {
                .summary-cards {
                    flex-direction: column;
                }
                
                .suite-header {
                    flex-direction: column;
                    align-items: flex-start;
                }
                
                .suite-stats {
                    margin-top: 10px;
                }
            }
            """;
    }
    
    /**
     * 获取堆栈跟踪
     */
    private String getStackTrace(Throwable throwable) {
        StringWriter sw = new StringWriter();
        PrintWriter pw = new PrintWriter(sw);
        throwable.printStackTrace(pw);
        return sw.toString();
    }
}
```

### 9.2.3 使用自定义报告

在TestNG配置文件中添加自定义报告：

```xml
<!DOCTYPE suite SYSTEM "https://testng.org/testng-1.0.dtd">
<suite name="Custom Report Test Suite">
    <listeners>
        <!-- 添加自定义报告 -->
        <listener class-name="com.example.reports.CustomReporter"/>
    </listeners>
    
    <test name="Sample Test">
        <classes>
            <class name="com.example.tests.SampleTestClass"/>
        </classes>
    </test>
</suite>
```

## 9.3 Extent Reports高级应用

### 9.3.1 Extent Reports简介

Extent Reports是一个功能强大的HTML报告工具，提供了丰富的报告特性和良好的可定制性：

#### Extent Reports的优势
1. **丰富的可视化**：提供图表、仪表盘和丰富的UI元素
2. **实时报告**：支持测试执行过程中的实时报告更新
3. **多语言支持**：支持多种语言的测试报告
4. **自定义配置**：高度可定制的报告外观和行为
5. **多平台支持**：支持TestNG、JUnit等多种测试框架
6. **丰富的API**：提供丰富的API用于创建和定制报告

### 9.3.2 集成Extent Reports

首先添加Extent Reports依赖：

```xml
<!-- Extent Reports依赖 -->
<dependency>
    <groupId>com.aventstack</groupId>
    <artifactId>extentreports</artifactId>
    <version>5.0.9</version>
</dependency>

<!-- Extent Reports TestNG适配器 -->
<dependency>
    <groupId>com.aventstack</groupId>
    <artifactId>extentreports-testng-adapter</artifactId>
    <version>1.2.2</version>
</dependency>
```

#### 创建Extent Reports监听器

```java
// ExtentReportListener.java - Extent Reports监听器
public class ExtentReportListener implements IReporter, ITestListener {
    private static final String OUTPUT_FOLDER = "test-output/extent/";
    private static final String FILE_NAME = "ExtentReport.html";
    
    private ExtentReports extent;
    private ThreadLocal<ExtentTest> test = new ThreadLocal<>();
    
    @Override
    public void generateReport(List<XmlSuite> xmlSuites, List<ISuite> suites, 
                               String outputDirectory) {
        // 创建报告目录
        new File(OUTPUT_FOLDER).mkdirs();
        
        // 初始化Extent Reports
        extent = new ExtentReports();
        
        // 配置报告
        ExtentSparkReporter htmlReporter = new ExtentSparkReporter(OUTPUT_FOLDER + FILE_NAME);
        
        // 配置报告视图
        htmlReporter.config().setTheme(Theme.DARK);
        htmlReporter.config().setDocumentTitle("自动化测试报告");
        htmlReporter.config().setReportName("Selenium自动化测试");
        htmlReporter.config().setEncoding("utf-8");
        htmlReporter.config().setProtocol(Protocol.HTTPS);
        
        // 添加分析视图
        htmlReporter.viewConfigurer()
            .viewOrder()
            .as(new ViewName[] { ViewName.DASHBOARD, ViewName.TEST, ViewName.EXCEPTION, ViewName.LOG })
            .apply();
        
        extent.attachReporter(htmlReporter);
        
        // 添加系统信息
        setSystemInfo();
        
        // 构建测试节点
        buildTestNodes(suites);
        
        // 刷新报告
        extent.flush();
    }
    
    /**
     * 设置系统信息
     */
    private void setSystemInfo() {
        extent.setSystemInfo("操作系统", System.getProperty("os.name"));
        extent.setSystemInfo("Java版本", System.getProperty("java.version"));
        extent.setSystemInfo("用户", System.getProperty("user.name"));
        extent.setSystemInfo("时区", TimeZone.getDefault().getID());
        extent.setSystemInfo("主机名", getHostname());
        
        // 添加环境信息
        extent.setSystemInfo("测试环境", ConfigReader.getProperty("test.env", "QA"));
        extent.setSystemInfo("基础URL", ConfigReader.getProperty("base.url", "N/A"));
        extent.setSystemInfo("浏览器", ConfigReader.getProperty("browser", "Chrome"));
    }
    
    /**
     * 获取主机名
     */
    private String getHostname() {
        try {
            return InetAddress.getLocalHost().getHostName();
        } catch (UnknownHostException e) {
            return "Unknown";
        }
    }
    
    /**
     * 构建测试节点
     */
    private void buildTestNodes(List<ISuite> suites) {
        for (ISuite suite : suites) {
            ExtentTest suiteTest = extent.createTest(suite.getName());
            
            Map<String, ISuiteResult> results = suite.getResults();
            for (ISuiteResult result : results.values()) {
                ITestContext context = result.getTestContext();
                buildTestNodes(suiteTest, context.getFailedTests(), Status.FAIL);
                buildTestNodes(suiteTest, context.getSkippedTests(), Status.SKIP);
                buildTestNodes(suiteTest, context.getPassedTests(), Status.PASS);
            }
        }
    }
    
    /**
     * 构建特定状态的测试节点
     */
    private void buildTestNodes(ExtentTest suiteTest, IResultMap tests, Status status) {
        if (tests.size() > 0) {
            ExtentTest category;
            if (status == Status.FAIL) {
                category = suiteTest.createNode("失败测试");
            } else if (status == Status.SKIP) {
                category = suiteTest.createNode("跳过测试");
            } else {
                category = suiteTest.createNode("通过测试");
            }
            
            for (ITestResult result : tests.getAllResults()) {
                ExtentTest test = category.createNode(result.getMethod().getMethodName());
                
                // 添加测试描述
                if (result.getMethod().getDescription() != null && !result.getMethod().getDescription().isEmpty()) {
                    test.getModel().setDescription(result.getMethod().getDescription());
                }
                
                // 添加测试参数
                Object[] parameters = result.getParameters();
                if (parameters != null && parameters.length > 0) {
                    String params = Arrays.stream(parameters)
                                       .map(Objects::toString)
                                       .collect(Collectors.joining(", "));
                    test.info("参数: " + params);
                }
                
                // 添加测试信息
                test.info("类: " + result.getTestClass().getName());
                test.info("方法: " + result.getMethod().getMethodName());
                
                // 添加开始时间和结束时间
                test.getModel().setStartTime(getTime(result.getStartMillis()));
                test.getModel().setEndTime(getTime(result.getEndMillis()));
                
                // 根据状态处理测试结果
                switch (status) {
                    case FAIL:
                        test.fail(result.getThrowable());
                        addScreenshot(test, result);
                        break;
                    case SKIP:
                        test.skip(result.getThrowable());
                        break;
                    default:
                        test.pass("测试通过");
                        break;
                }
                
                // 添加日志
                addTestLogs(test, result);
            }
        }
    }
    
    /**
     * 添加截图
     */
    private void addScreenshot(ExtentTest test, ITestResult result) {
        String screenshotPath = (String) result.getTestContext().getAttribute("screenshotPath");
        if (screenshotPath != null && !screenshotPath.isEmpty()) {
            test.addScreenCaptureFromPath(screenshotPath);
        }
    }
    
    /**
     * 添加测试日志
     */
    private void addTestLogs(ExtentTest test, ITestResult result) {
        Map<String, Object> attributes = result.getTestContext().getSuite().getAttributes();
        if (attributes.containsKey("logs_" + result.getName())) {
            @SuppressWarnings("unchecked")
            List<String> logs = (List<String>) attributes.get("logs_" + result.getName());
            
            for (String log : logs) {
                test.info(log);
            }
        }
    }
    
    /**
     * 转换时间为Date对象
     */
    private Date getTime(long millis) {
        Calendar calendar = Calendar.getInstance();
        calendar.setTimeInMillis(millis);
        return calendar.getTime();
    }
    
    // ITestListener接口实现
    @Override
    public void onTestStart(ITestResult result) {
        // 测试开始时创建ExtentTest
        ExtentTest extentTest = extent.createTest(result.getMethod().getMethodName());
        if (result.getMethod().getDescription() != null) {
            extentTest.getModel().setDescription(result.getMethod().getDescription());
        }
        test.set(extentTest);
    }
    
    @Override
    public void onTestSuccess(ITestResult result) {
        test.get().pass("测试通过");
        extent.flush();
    }
    
    @Override
    public void onTestFailure(ITestResult result) {
        test.get().fail(result.getThrowable());
        addScreenshot(test.get(), result);
        extent.flush();
    }
    
    @Override
    public void onTestSkipped(ITestResult result) {
        test.get().skip(result.getThrowable());
        extent.flush();
    }
    
    @Override
    public void onTestFailedButWithinSuccessPercentage(ITestResult result) {
        test.get().fail(result.getThrowable());
        extent.flush();
    }
    
    @Override
    public void onStart(ITestContext context) {
        // 测试套件开始时初始化Extent Reports
        extent = new ExtentReports();
        
        ExtentSparkReporter htmlReporter = new ExtentSparkReporter(OUTPUT_FOLDER + FILE_NAME);
        htmlReporter.config().setTheme(Theme.DARK);
        htmlReporter.config().setDocumentTitle("自动化测试报告");
        htmlReporter.config().setReportName("Selenium自动化测试");
        
        extent.attachReporter(htmlReporter);
        setSystemInfo();
    }
    
    @Override
    public void onFinish(ITestContext context) {
        // 测试套件结束时刷新报告
        extent.flush();
    }
    
    /**
     * 记录测试步骤日志
     */
    public static void logStep(String message) {
        ExtentTest currentTest = test.get();
        if (currentTest != null) {
            currentTest.info(message);
        }
    }
    
    /**
     * 记录测试信息日志
     */
    public static void logInfo(String message) {
        ExtentTest currentTest = test.get();
        if (currentTest != null) {
            currentTest.info(message);
        }
    }
    
    /**
     * 记录测试警告日志
     */
    public static void logWarning(String message) {
        ExtentTest currentTest = test.get();
        if (currentTest != null) {
            currentTest.warning(message);
        }
    }
    
    /**
     * 记录测试错误日志
     */
    public static void logError(String message) {
        ExtentTest currentTest = test.get();
        if (currentTest != null) {
            currentTest.fail(message);
        }
    }
    
    /**
     * 添加截图
     */
    public static void addScreenshot(String screenshotPath) {
        ExtentTest currentTest = test.get();
        if (currentTest != null) {
            currentTest.addScreenCaptureFromPath(screenshotPath);
        }
    }
    
    /**
     * 添加媒体文件
     */
    public static void addMedia(String mediaPath) {
        ExtentTest currentTest = test.get();
        if (currentTest != null) {
            currentTest.addScreenCaptureFromPath(mediaPath);
        }
    }
}
```

#### 在测试基类中集成Extent Reports

```java
// ExtentBaseTest.java - 集成Extent Reports的测试基类
@Listeners({ExtentReportListener.class})
public abstract class ExtentBaseTest {
    
    protected static WebDriver driver;
    protected static ExtentReports extent;
    protected static ExtentTest test;
    
    @BeforeSuite(alwaysRun = true)
    public void setUpSuite() {
        // 初始化Extent Reports
        extent = new ExtentReports();
        
        ExtentSparkReporter htmlReporter = new ExtentSparkReporter("test-output/extent/ExtentReport.html");
        htmlReporter.config().setTheme(Theme.STANDARD);
        htmlReporter.config().setDocumentTitle("自动化测试报告");
        htmlReporter.config().setReportName("Selenium自动化测试报告");
        
        extent.attachReporter(htmlReporter);
        
        // 添加系统信息
        extent.setSystemInfo("操作系统", System.getProperty("os.name"));
        extent.setSystemInfo("Java版本", System.getProperty("java.version"));
        extent.setSystemInfo("测试环境", ConfigReader.getProperty("test.env", "QA"));
    }
    
    @BeforeClass(alwaysRun = true)
    public void setUpClass() {
        // 初始化WebDriver
        initializeDriver();
        
        // 创建测试节点
        test = extent.createTest(getClass().getSimpleName());
    }
    
    @BeforeMethod(alwaysRun = true)
    public void setUpMethod(Method method) {
        // 为每个测试方法创建子节点
        ExtentTest methodTest = test.createNode(method.getName());
        if (method.getAnnotation(Description.class) != null) {
            methodTest.getModel().setDescription(method.getAnnotation(Description.class).value());
        }
        
        // 记录测试开始
        methodTest.info("测试开始: " + method.getName());
    }
    
    @AfterMethod(alwaysRun = true)
    public void tearDownMethod(ITestResult result) {
        // 处理测试结果
        if (result.getStatus() == ITestResult.SUCCESS) {
            test.pass("测试通过: " + result.getName());
        } else if (result.getStatus() == ITestResult.FAILURE) {
            test.fail("测试失败: " + result.getName());
            
            // 添加截图
            String screenshotPath = takeScreenshot(result.getName());
            test.addScreenCaptureFromPath(screenshotPath);
            
            // 添加异常信息
            test.fail(result.getThrowable());
        } else if (result.getStatus() == ITestResult.SKIP) {
            test.skip("测试跳过: " + result.getName());
        }
        
        // 清理WebDriver
        if (driver != null) {
            driver.manage().deleteAllCookies();
        }
    }
    
    @AfterClass(alwaysRun = true)
    public void tearDownClass() {
        if (driver != null) {
            driver.quit();
        }
    }
    
    @AfterSuite(alwaysRun = true)
    public void tearDownSuite() {
        // 刷新报告
        extent.flush();
    }
    
    /**
     * 初始化WebDriver
     */
    protected void initializeDriver() {
        String browser = ConfigReader.getProperty("browser", "chrome");
        boolean headless = ConfigReader.getBooleanProperty("headless", false);
        
        switch (browser.toLowerCase()) {
            case "chrome":
                WebDriverManager.chromedriver().setup();
                ChromeOptions chromeOptions = new ChromeOptions();
                if (headless) {
                    chromeOptions.addArguments("--headless");
                }
                chromeOptions.addArguments("--no-sandbox");
                chromeOptions.addArguments("--disable-dev-shm-usage");
                driver = new ChromeDriver(chromeOptions);
                break;
                
            case "firefox":
                WebDriverManager.firefoxdriver().setup();
                FirefoxOptions firefoxOptions = new FirefoxOptions();
                if (headless) {
                    firefoxOptions.addArguments("-headless");
                }
                driver = new FirefoxDriver(firefoxOptions);
                break;
                
            default:
                throw new IllegalArgumentException("不支持的浏览器: " + browser);
        }
        
        driver.manage().window().maximize();
        driver.manage().timeouts().implicitlyWait(Duration.ofSeconds(10));
    }
    
    /**
     * 记录测试步骤
     */
    protected void logStep(String step) {
        test.info("步骤: " + step);
        System.out.println("[STEP] " + step);
    }
    
    /**
     * 记录测试信息
     */
    protected void logInfo(String info) {
        test.info("信息: " + info);
        System.out.println("[INFO] " + info);
    }
    
    /**
     * 记录测试警告
     */
    protected void logWarning(String warning) {
        test.warning("警告: " + warning);
        System.out.println("[WARNING] " + warning);
    }
    
    /**
     * 记录测试错误
     */
    protected void logError(String error) {
        test.fail("错误: " + error);
        System.out.println("[ERROR] " + error);
    }
    
    /**
     * 截图方法
     */
    protected String takeScreenshot(String testName) {
        try {
            String timestamp = new SimpleDateFormat("yyyyMMdd-HHmmss").format(new Date());
            String fileName = testName + "_" + timestamp + ".png";
            String filePath = "screenshots/" + fileName;
            
            // 确保目录存在
            new File("screenshots").mkdirs();
            
            // 截图
            File screenshot = ((TakesScreenshot) driver).getScreenshotAs(OutputType.FILE);
            FileUtils.copyFile(screenshot, new File(filePath));
            
            return filePath;
        } catch (IOException e) {
            System.err.println("截图失败: " + e.getMessage());
            return "";
        }
    }
}
```

## 9.4 Allure报告框架

### 9.4.1 Allure简介

Allure Framework是一个灵活的轻量级多语言测试报告工具，不仅可以显示非常简洁的测试结果，还允许参与开发过程的每个人提取最大限度的有用信息：

#### Allure的特点
1. **美观的报告界面**：现代化的Web界面设计
2. **丰富的分类和分组**：支持多维度测试分类
3. **详细的测试步骤**：可以记录测试执行的每个步骤
4. **丰富的附件支持**：支持截图、视频、日志等附件
5. **趋势分析**：支持测试历史趋势分析
6. **多环境支持**：支持不同环境的测试结果对比

### 9.4.2 集成Allure Reports

首先添加Allure TestNG依赖：

```xml
<!-- Allure TestNG依赖 -->
<dependency>
    <groupId>io.qameta.allure</groupId>
    <artifactId>allure-testng</artifactId>
    <version>2.22.2</version>
    <scope>test</scope>
</dependency>
```

#### 配置Maven Allure插件

```xml
<build>
    <plugins>
        <!-- Allure Maven插件 -->
        <plugin>
            <groupId>io.qameta.allure</groupId>
            <artifactId>allure-maven</artifactId>
            <version>2.12.0</version>
            <configuration>
                <reportVersion>2.13.8</reportVersion>
            </configuration>
            <executions>
                <execution>
                    <id>allure-report</id>
                    <phase>verify</phase>
                    <goals>
                        <goal>report</goal>
                    </goals>
                </execution>
            </executions>
        </plugin>
    </plugins>
</build>
```

#### 创建Allure监听器

```java
// AllureReportListener.java - Allure报告监听器
public class AllureReportListener implements ITestListener {
    
    @Override
    public void onTestStart(ITestResult result) {
        // 设置Allure测试名称和描述
        Allure.getLifecycle().updateTestCase(testResult -> {
            testResult.setName(result.getMethod().getMethodName());
            
            if (result.getMethod().getDescription() != null) {
                testResult.setDescription(result.getMethod().getDescription());
            }
            
            // 添加标签
            addTestTags(testResult, result);
            
            // 添加链接
            addTestLinks(testResult, result);
        });
    }
    
    @Override
    public void onTestSuccess(ITestResult result) {
        Allure.getLifecycle().updateTestCase(testResult -> {
            testResult.setStatus(Status.PASSED);
        });
        
        Allure.getLifecycle().stopTestCase();
        Allure.getLifecycle().writeTestCase();
    }
    
    @Override
    public void onTestFailure(ITestResult result) {
        Allure.getLifecycle().updateTestCase(testResult -> {
            testResult.setStatus(Status.FAILED);
            testResult.setStatusDetails(new StatusDetails()
                .setMessage(result.getThrowable().getMessage())
                .setTrace(getStackTrace(result.getThrowable()))
            );
            
            // 添加截图
            addScreenshot(testResult, result);
        });
        
        Allure.getLifecycle().stopTestCase();
        Allure.getLifecycle().writeTestCase();
    }
    
    @Override
    public void onTestSkipped(ITestResult result) {
        Allure.getLifecycle().updateTestCase(testResult -> {
            testResult.setStatus(Status.SKIPPED);
            if (result.getThrowable() != null) {
                testResult.setStatusDetails(new StatusDetails()
                    .setMessage(result.getThrowable().getMessage())
                    .setTrace(getStackTrace(result.getThrowable()))
                );
            }
        });
        
        Allure.getLifecycle().stopTestCase();
        Allure.getLifecycle().writeTestCase();
    }
    
    @Override
    public void onTestFailedButWithinSuccessPercentage(ITestResult result) {
        onTestFailure(result);
    }
    
    @Override
    public void onStart(ITestContext context) {
        // 设置套件信息
        Allure.getLifecycle().setTestCaseCategories(new ArrayList<>());
        Allure.getLifecycle().writeTestCaseCategories();
    }
    
    @Override
    public void onFinish(ITestContext context) {
        // 测试套件结束时的处理
    }
    
    /**
     * 添加测试标签
     */
    private void addTestLinks(ExecutableItem item, ITestResult result) {
        // 获取链接信息（可以从配置文件或注解中获取）
        String issueLink = getIssueLink(result);
        String tmsLink = getTmsLink(result);
        
        if (issueLink != null && !issueLink.isEmpty()) {
            item.setLinks(new Link(issueLink, "ISSUE", "Link to issue"));
        }
        
        if (tmsLink != null && !tmsLink.isEmpty()) {
            item.setLinks(new Link(tmsLink, "TMS", "Link to test case"));
        }
    }
    
    /**
     * 添加测试链接
     */
    private void addTestTags(ExecutableItem item, ITestResult result) {
        // 获取标签信息（可以从配置文件或注解中获取）
        List<String> tags = getTestTags(result);
        
        if (!tags.isEmpty()) {
            item.setLabels(tags.stream()
                            .map(tag -> new Label().setName("tag").setValue(tag))
                            .collect(Collectors.toList()));
        }
        
        // 添加默认标签
        item.getLabels().add(new Label().setName("package").setValue(result.getTestClass().getName()));
        item.getLabels().add(new Label().setName("testClass").setValue(result.getTestClass().getName()));
        item.getLabels().add(new Label().setName("testMethod").setValue(result.getMethod().getMethodName()));
        item.getLabels().add(new Label().setName("suite").setValue(result.getTestContext().getSuite().getName()));
    }
    
    /**
     * 添加截图
     */
    private void addScreenshot(ExecutableItem item, ITestResult result) {
        try {
            String screenshotPath = (String) result.getTestContext().getAttribute("screenshotPath");
            if (screenshotPath != null && !screenshotPath.isEmpty()) {
                Allure.addAttachment("截图", "image/png", new File(screenshotPath));
            }
        } catch (Exception e) {
            // 忽略截图添加失败
        }
    }
    
    /**
     * 获取堆栈跟踪
     */
    private String getStackTrace(Throwable throwable) {
        StringWriter sw = new StringWriter();
        PrintWriter pw = new PrintWriter(sw);
        throwable.printStackTrace(pw);
        return sw.toString();
    }
    
    /**
     * 获取问题链接
     */
    private String getIssueLink(ITestResult result) {
        // 可以从配置文件或注解中获取
        return "";
    }
    
    /**
     * 获取测试管理系统链接
     */
    private String getTmsLink(ITestResult result) {
        // 可以从配置文件或注解中获取
        return "";
    }
    
    /**
     * 获取测试标签
     */
    private List<String> getTestTags(ITestResult result) {
        List<String> tags = new ArrayList<>();
        
        // 从方法注解中获取标签
        Test testAnnotation = result.getMethod().getConstructorOrMethod().getMethod().getAnnotation(Test.class);
        if (testAnnotation != null) {
            String[] groups = testAnnotation.groups();
            if (groups.length > 0) {
                tags.addAll(Arrays.asList(groups));
            }
        }
        
        // 从配置文件中获取标签
        // ...
        
        return tags;
    }
}
```

#### 创建Allure工具类

```java
// AllureUtils.java - Allure工具类
public class AllureUtils {
    
    /**
     * 记录测试步骤
     */
    public static void logStep(String step) {
        Allure.step(step, Status.PASSED);
        System.out.println("[STEP] " + step);
    }
    
    /**
     * 记录测试信息
     */
    public static void logInfo(String info) {
        Allure.addAttachment("信息", "text/plain", info);
        System.out.println("[INFO] " + info);
    }
    
    /**
     * 记录测试警告
     */
    public static void logWarning(String warning) {
        Allure.addAttachment("警告", "text/plain", warning);
        System.out.println("[WARNING] " + warning);
    }
    
    /**
     * 记录测试错误
     */
    public static void logError(String error) {
        Allure.step(error, Status.FAILED);
        System.out.println("[ERROR] " + error);
    }
    
    /**
     * 添加文本附件
     */
    public static void addTextAttachment(String name, String content) {
        Allure.addAttachment(name, "text/plain", content);
    }
    
    /**
     * 添加HTML附件
     */
    public static void addHtmlAttachment(String name, String content) {
        Allure.addAttachment(name, "text/html", content);
    }
    
    /**
     * 添加JSON附件
     */
    public static void addJsonAttachment(String name, String json) {
        Allure.addAttachment(name, "application/json", json);
    }
    
    /**
     * 添加截图
     */
    public static void addScreenshot(String name, byte[] screenshotBytes) {
        Allure.addAttachment(name, "image/png", new ByteArrayInputStream(screenshotBytes));
    }
    
    /**
     * 添加视频
     */
    public static void addVideo(String name, byte[] videoBytes) {
        Allure.addAttachment(name, "video/mp4", new ByteArrayInputStream(videoBytes));
    }
    
    /**
     * 添加环境信息
     */
    public static void addEnvironmentInfo() {
        Allure.addAttachment("环境信息", "application/json", getEnvironmentInfo());
    }
    
    /**
     * 获取环境信息JSON
     */
    private static String getEnvironmentInfo() {
        Map<String, String> envInfo = new HashMap<>();
        envInfo.put("操作系统", System.getProperty("os.name"));
        envInfo.put("Java版本", System.getProperty("java.version"));
        envInfo.put("测试环境", ConfigReader.getProperty("test.env", "QA"));
        envInfo.put("基础URL", ConfigReader.getProperty("base.url", "N/A"));
        envInfo.put("浏览器", ConfigReader.getProperty("browser", "Chrome"));
        envInfo.put("执行时间", new SimpleDateFormat("yyyy-MM-dd HH:mm:ss").format(new Date()));
        
        try {
            return new ObjectMapper().writeValueAsString(envInfo);
        } catch (Exception e) {
            return "{}";
        }
    }
    
    /**
     * 添加测试参数
     */
    public static void addParameters(Map<String, Object> parameters) {
        for (Map.Entry<String, Object> entry : parameters.entrySet()) {
            Allure.parameter(entry.getKey(), entry.getValue());
        }
    }
    
    /**
     * 添加测试参数
     */
    public static void addParameter(String name, Object value) {
        Allure.parameter(name, value);
    }
    
    /**
     * 标记测试为失败
     */
    public static void markAsFailed(String reason) {
        Allure.step(reason, Status.FAILED);
    }
    
    /**
     * 标记测试为跳过
     */
    public static void markAsSkipped(String reason) {
        Allure.step(reason, Status.SKIPPED);
    }
    
    /**
     * 标记测试为中断
     */
    public static void markAsBroken(String reason) {
        Allure.step(reason, Status.BROKEN);
    }
    
    /**
     * 添加史诗标签
     */
    public static void setEpic(String epic) {
        Allure.epic(epic);
    }
    
    /**
     * 添加特性标签
     */
    public static void setFeature(String feature) {
        Allure.feature(feature);
    }
    
    /**
     * 添加故事标签
     */
    public static void setStory(String story) {
        Allure.story(story);
    }
    
    /**
     * 添加严重性标签
     */
    public static void setSeverity(SeverityLevel severity) {
        Allure.severity(severity);
    }
    
    /**
     * 添加所有者标签
     */
    public static void setOwner(String owner) {
        Allure.owner(owner);
    }
    
    /**
     * 添加套件标签
     */
    public static void setSuite(String suite) {
        Allure.suite(suite);
    }
    
    /**
     * 添加子套件标签
     */
    public static void setSubSuite(String subSuite) {
        Allure.subSuite(subSuite);
    }
    
    /**
     * 添加父套件标签
     */
    public static void setParentSuite(String parentSuite) {
        Allure.parentSuite(parentSuite);
    }
}
```

#### 集成Allure到测试基类

```java
// AllureBaseTest.java - 集成Allure的测试基类
@Listeners({AllureReportListener.class})
public abstract class AllureBaseTest {
    
    protected static WebDriver driver;
    
    @BeforeSuite(alwaysRun = true)
    public void setUpSuite() {
        // 添加环境信息
        AllureUtils.addEnvironmentInfo();
    }
    
    @BeforeClass(alwaysRun = true)
    public void setUpClass() {
        // 初始化WebDriver
        initializeDriver();
        
        // 设置套件信息
        AllureUtils.setSuite(getClass().getSimpleName());
    }
    
    @BeforeMethod(alwaysRun = true)
    public void setUpMethod(Method method) {
        // 设置测试特性
        AllureUtils.setFeature(getTestFeature());
        AllureUtils.setStory(getTestStory());
        AllureUtils.setSeverity(getTestSeverity());
        AllureUtils.setOwner(getTestOwner());
        
        // 添加测试参数
        AllureUtils.addParameter("浏览器", ConfigReader.getProperty("browser", "Chrome"));
        AllureUtils.addParameter("环境", ConfigReader.getProperty("test.env", "QA"));
    }
    
    @AfterMethod(alwaysRun = true)
    public void tearDownMethod(ITestResult result) {
        // 如果测试失败，添加截图
        if (result.getStatus() == ITestResult.FAILURE) {
            String screenshotPath = takeScreenshot(result.getName());
            if (!screenshotPath.isEmpty()) {
                AllureUtils.addScreenshot("失败截图", readScreenshotBytes(screenshotPath));
            }
        }
        
        // 清理WebDriver
        if (driver != null) {
            driver.manage().deleteAllCookies();
        }
    }
    
    @AfterClass(alwaysRun = true)
    public void tearDownClass() {
        if (driver != null) {
            driver.quit();
        }
    }
    
    /**
     * 初始化WebDriver
     */
    protected void initializeDriver() {
        String browser = ConfigReader.getProperty("browser", "chrome");
        boolean headless = ConfigReader.getBooleanProperty("headless", false);
        
        switch (browser.toLowerCase()) {
            case "chrome":
                WebDriverManager.chromedriver().setup();
                ChromeOptions chromeOptions = new ChromeOptions();
                if (headless) {
                    chromeOptions.addArguments("--headless");
                }
                chromeOptions.addArguments("--no-sandbox");
                chromeOptions.addArguments("--disable-dev-shm-usage");
                driver = new ChromeDriver(chromeOptions);
                break;
                
            case "firefox":
                WebDriverManager.firefoxdriver().setup();
                FirefoxOptions firefoxOptions = new FirefoxOptions();
                if (headless) {
                    firefoxOptions.addArguments("-headless");
                }
                driver = new FirefoxDriver(firefoxOptions);
                break;
                
            default:
                throw new IllegalArgumentException("不支持的浏览器: " + browser);
        }
        
        driver.manage().window().maximize();
        driver.manage().timeouts().implicitlyWait(Duration.ofSeconds(10));
    }
    
    /**
     * 记录测试步骤
     */
    protected void logStep(String step) {
        AllureUtils.logStep(step);
    }
    
    /**
     * 记录测试信息
     */
    protected void logInfo(String info) {
        AllureUtils.logInfo(info);
    }
    
    /**
     * 记录测试警告
     */
    protected void logWarning(String warning) {
        AllureUtils.logWarning(warning);
    }
    
    /**
     * 记录测试错误
     */
    protected void logError(String error) {
        AllureUtils.logError(error);
    }
    
    /**
     * 截图方法
     */
    protected String takeScreenshot(String testName) {
        try {
            String timestamp = new SimpleDateFormat("yyyyMMdd-HHmmss").format(new Date());
            String fileName = testName + "_" + timestamp + ".png";
            String filePath = "allure-results/screenshots/" + fileName;
            
            // 确保目录存在
            new File("allure-results/screenshots").mkdirs();
            
            // 截图
            File screenshot = ((TakesScreenshot) driver).getScreenshotAs(OutputType.FILE);
            FileUtils.copyFile(screenshot, new File(filePath));
            
            return filePath;
        } catch (IOException e) {
            System.err.println("截图失败: " + e.getMessage());
            return "";
        }
    }
    
    /**
     * 读取截图字节
     */
    protected byte[] readScreenshotBytes(String filePath) {
        try {
            return Files.readAllBytes(Paths.get(filePath));
        } catch (IOException e) {
            System.err.println("读取截图失败: " + e.getMessage());
            return new byte[0];
        }
    }
    
    /**
     * 获取测试特性（子类可覆盖）
     */
    protected String getTestFeature() {
        return "功能测试";
    }
    
    /**
     * 获取测试故事（子类可覆盖）
     */
    protected String getTestStory() {
        return "基础功能验证";
    }
    
    /**
     * 获取测试严重性（子类可覆盖）
     */
    protected SeverityLevel getTestSeverity() {
        return SeverityLevel.NORMAL;
    }
    
    /**
     * 获取测试所有者（子类可覆盖）
     */
    protected String getTestOwner() {
        return "测试团队";
    }
}
```

#### 生成和查看Allure报告

```bash
# 运行测试
mvn clean test

# 生成Allure报告
mvn allure:report

# 启动Allure服务查看报告
mvn allure:serve

# 或者使用allure命令行工具（需要安装allure命令行）
allure serve allure-results
```

## 9.5 CI/CD集成

### 9.5.1 Jenkins集成

Jenkins是最流行的持续集成工具之一，下面是如何在Jenkins中集成Selenium测试：

#### Jenkinsfile示例

```groovy
// Jenkinsfile - Jenkins流水线配置
pipeline {
    agent any
    
    environment {
        BROWSER = 'chrome'
        TEST_ENV = 'qa'
        BASE_URL = 'https://qa.example.com'
        REPORT_DIR = 'test-reports'
    }
    
    stages {
        stage('准备环境') {
            steps {
                echo '准备测试环境'
                
                // 清理工作空间
                cleanWs()
                
                // 拉取代码
                checkout scm
                
                // 创建报告目录
                sh 'mkdir -p ${REPORT_DIR}'
            }
        }
        
        stage('安装依赖') {
            steps {
                echo '安装测试依赖'
                
                // 安装Maven依赖
                sh 'mvn clean install -DskipTests'
                
                // 安装浏览器驱动
                sh 'webdrivermanager chrome update'
            }
        }
        
        stage('运行测试') {
            steps {
                echo '执行Selenium自动化测试'
                
                // 运行测试并生成报告
                sh "mvn test " +
                   "-Dbrowser=${BROWSER} " +
                   "-Dtest.env=${TEST_ENV} " +
                   "-Dbase.url=${BASE_URL} " +
                   "-DfailIfNoTests=false"
            }
            
            post {
                always {
                    // 归档测试报告
                    junit 'target/surefire-reports/**/*.xml'
                    
                    // 归档HTML报告
                    publishHTML([
                        allowMissing: false,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'target/surefire-reports/html',
                        reportFiles: 'index.html',
                        reportName: 'HTML报告'
                    ])
                    
                    // 归档Allure报告
                    allure([
                        includeProperties: false,
                        jdk: '',
                        properties: [],
                        reportBuildPolicy: 'ALWAYS',
                        results: [[path: 'target/allure-results']]
                    ])
                    
                    // 归档截图
                    archiveArtifacts artifacts: 'screenshots/**/*.png', allowEmptyArchive: true
                }
                
                failure {
                    // 发送通知
                    emailext(
                        subject: "测试失败 - ${env.JOB_NAME} - ${env.BUILD_NUMBER}",
                        body: """
                            <p>测试执行失败，请查看以下报告：</p>
                            <ul>
                                <li><a href="${env.JOB_URL}${env.BUILD_NUMBER}/HTML_20报告/">HTML报告</a></li>
                                <li><a href="${env.JOB_URL}${env.BUILD_NUMBER}/allure/">Allure报告</a></li>
                            </ul>
                            <p>构建信息：</p>
                            <ul>
                                <li>分支：${env.BRANCH_NAME}</li>
                                <li>提交者：${env.CHANGE_AUTHOR}</li>
                                <li>提交信息：${env.CHANGE_MESSAGE}</li>
                            </ul>
                        """,
                        to: 'test-team@example.com'
                    )
                }
            }
        }
    }
    
    post {
        always {
            echo '清理环境'
            
            // 停止所有浏览器进程
            sh 'pkill -f chrome || true'
            sh 'pkill -f firefox || true'
            
            // 停止Xvfb（如果使用无头模式）
            sh 'pkill -f Xvfb || true'
        }
        
        success {
            echo '测试执行成功'
            
            // 发送成功通知
            emailext(
                subject: "测试通过 - ${env.JOB_NAME} - ${env.BUILD_NUMBER}",
                body: """
                    <p>测试执行成功！</p>
                    <ul>
                        <li><a href="${env.JOB_URL}${env.BUILD_NUMBER}/HTML_20报告/">HTML报告</a></li>
                        <li><a href="${env.JOB_URL}${env.BUILD_NUMBER}/allure/">Allure报告</a></li>
                    </ul>
                """,
                to: 'test-team@example.com'
            )
        }
    }
}
```

#### Jenkins配置步骤

1. **安装必要的插件**：
   - Allure Jenkins Plugin
   - HTML Publisher Plugin
   - Email Extension Plugin

2. **创建流水线项目**：
   - 选择"Pipeline"类型
   - 将Jenkinsfile内容粘贴到项目配置中

3. **配置Allure报告**：
   - 在项目配置中添加"Allure Report"构建后操作
   - 设置报告路径为`target/allure-results`

4. **配置邮件通知**：
   - 在系统配置中设置SMTP服务器
   - 在项目配置中配置邮件通知规则

### 9.5.2 GitHub Actions集成

GitHub Actions是GitHub提供的CI/CD服务，下面是集成Selenium测试的示例：

#### GitHub Actions工作流文件

```yaml
# .github/workflows/selenium-tests.yml
name: Selenium自动化测试

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
  schedule:
    # 每天凌晨2点运行
    - cron: '0 2 * * *'

jobs:
  selenium-tests:
    runs-on: ubuntu-latest
    
    strategy:
      matrix:
        browser: [chrome, firefox]
        env: [qa, staging]
    
    services:
      # MySQL服务（如果需要）
      mysql:
        image: mysql:8.0
        env:
          MYSQL_ROOT_PASSWORD: password
          MYSQL_DATABASE: testdb
        options: >-
          --health-cmd="mysqladmin ping"
          --health-interval=10s
          --health-timeout=5s
          --health-retries=3
      
      # Redis服务（如果需要）
      redis:
        image: redis:6
        options: >-
          --health-cmd="redis-cli ping"
          --health-interval=10s
          --health-timeout=5s
          --health-retries=3
    
    steps:
    - name: 检出代码
      uses: actions/checkout@v3
    
    - name: 设置JDK 11
      uses: actions/setup-java@v3
      with:
        java-version: '11'
        distribution: 'temurin'
    
    - name: 缓存Maven依赖
      uses: actions/cache@v3
      with:
        path: ~/.m2
        key: ${{ runner.os }}-m2-${{ hashFiles('**/pom.xml') }}
        restore-keys: ${{ runner.os }}-m2
    
    - name: 安装Chrome和Firefox
      run: |
        # 安装Chrome
        wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
        echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
        sudo apt-get update
        sudo apt-get install -y google-chrome-stable
        
        # 安装Firefox
        sudo apt-get install -y firefox
        
        # 安装ChromeDriver
        wget -N https://chromedriver.storage.googleapis.com/LATEST_RELEASE
        CHROME_DRIVER_VERSION=$(cat LATEST_RELEASE)
        wget -N https://chromedriver.storage.googleapis.com/${CHROME_DRIVER_VERSION}/chromedriver_linux64.zip
        unzip chromedriver_linux64.zip
        chmod +x chromedriver
        sudo mv chromedriver /usr/local/bin/
        
        # 安装GeckoDriver
        GECKO_DRIVER_VERSION=$(curl -sS "https://api.github.com/repos/mozilla/geckodriver/releases/latest" | grep '"tag_name":' | sed -E 's/.*"v?([^"]+)".*/\1/')
        wget -O geckodriver.tar.gz "https://github.com/mozilla/geckodriver/releases/download/v${GECKO_DRIVER_VERSION}/geckodriver-v${GECKO_DRIVER_VERSION}-linux64.tar.gz"
        tar -xzf geckodriver.tar.gz
        chmod +x geckodriver
        sudo mv geckodriver /usr/local/bin/
        
        # 安装Xvfb（用于无头模式）
        sudo apt-get install -y xvfb
    
    - name: 运行测试
      env:
        BROWSER: ${{ matrix.browser }}
        TEST_ENV: ${{ matrix.env }}
        BASE_URL: ${{ matrix.env == 'qa' && 'https://qa.example.com' || 'https://staging.example.com' }}
      run: |
        # 启动Xvfb（用于无头模式）
        export DISPLAY=:99
        Xvfb :99 -screen 0 1920x1080x24 &
        Xvfb_pid=$!
        
        # 等待Xvfb启动
        sleep 3
        
        # 运行测试
        mvn clean test \
          -Dbrowser=${BROWSER} \
          -Dtest.env=${TEST_ENV} \
          -Dbase.url=${BASE_URL} \
          -Dheadless=true
        
        # 停止Xvfb
        kill $Xvfb_pid
    
    - name: 上传测试报告
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: test-reports-${{ matrix.browser }}-${{ matrix.env }}
        path: |
          target/surefire-reports/
          target/allure-results/
          screenshots/
    
    - name: 生成Allure报告
      if: always()
      run: |
        # 安装Allure命令行工具
        sudo npm install -g allure-commandline
        
        # 生成Allure报告
        allure generate target/allure-results -o target/allure-report --clean
    
    - name: 上传Allure报告
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: allure-report-${{ matrix.browser }}-${{ matrix.env }}
        path: target/allure-report
    
    - name: 发布Allure报告到GitHub Pages
      if: matrix.browser == 'chrome' && matrix.env == 'qa'
      uses: peaceiris/actions-gh-pages@v3
      with:
        github_token: ${{ secrets.GITHUB_TOKEN }}
        publish_dir: target/allure-report
        destination_dir: allure-report
    
    - name: 发送通知
      if: failure()
      uses: actions/github-script@v6
      with:
        script: |
          const { owner, repo } = context.repo;
          const runId = context.runId;
          const sha = context.sha;
          
          // 创建评论
          github.rest.issues.createComment({
            owner,
            repo,
            issue_number: context.issue.number,
            body: `## 测试执行失败
            
            **浏览器**: ${{ matrix.browser }}
            **环境**: ${{ matrix.env }}
            **提交**: ${sha}
            
            请查看[详细报告](https://github.com/${owner}/${repo}/actions/runs/${runId})获取更多信息。
            `
          });
```

### 9.5.3 GitLab CI/CD集成

GitLab CI/CD是GitLab提供的持续集成服务，下面是集成Selenium测试的示例：

#### GitLab CI配置文件

```yaml
# .gitlab-ci.yml
stages:
  - prepare
  - test
  - report
  - notify

variables:
  MAVEN_OPTS: "-Dmaven.repo.local=$CI_PROJECT_DIR/.m2/repository"

# 缓存Maven依赖
cache:
  paths:
    - .m2/repository/
    - target/

# 准备阶段
prepare:
  stage: prepare
  image: maven:3.8.6-openjdk-11
  script:
    - echo "准备测试环境"
    - apt-get update
    - apt-get install -y wget gnupg2 unzip
    
    # 安装Chrome和ChromeDriver
    - wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
    - echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list
    - apt-get update
    - apt-get install -y google-chrome-stable
    - LATEST_VERSION=$(wget -q -O - "https://chromedriver.storage.googleapis.com/LATEST_RELEASE")
    - wget -N https://chromedriver.storage.googleapis.com/${LATEST_VERSION}/chromedriver_linux64.zip
    - unzip chromedriver_linux64.zip
    - chmod +x chromedriver
    - mv chromedriver /usr/local/bin/
    
    # 安装Firefox和GeckoDriver
    - apt-get install -y firefox
    - GECKO_VERSION=$(curl -s "https://api.github.com/repos/mozilla/geckodriver/releases/latest" | grep '"tag_name":' | sed -E 's/.*"v?([^"]+)".*/\1/')
    - wget -O geckodriver.tar.gz "https://github.com/mozilla/geckodriver/releases/download/v${GECKO_VERSION}/geckodriver-v${GECKO_VERSION}-linux64.tar.gz"
    - tar -xzf geckodriver.tar.gz
    - chmod +x geckodriver
    - mv geckodriver /usr/local/bin/
    
    # 安装Xvfb（用于无头模式）
    - apt-get install -y xvfb
  only:
    - merge_requests
    - main
    - develop

# 测试阶段
test:chrome:
  stage: test
  image: maven:3.8.6-openjdk-11
  variables:
    BROWSER: chrome
    TEST_ENV: $CI_COMMIT_REF_NAME
    BASE_URL: $CI_COMMIT_REF_NAME == "main" && "https://staging.example.com" || "https://qa.example.com"
  before_script:
    # 启动Xvfb（用于无头模式）
    - export DISPLAY=:99
    - Xvfb :99 -screen 0 1920x1080x24 &
    - export XVFB_PID=$!
    - sleep 3
  script:
    - echo "运行Chrome浏览器测试"
    - mvn clean test -Dbrowser=chrome -Dtest.env=$TEST_ENV -Dbase.url=$BASE_URL -Dheadless=true
  after_script:
    # 停止Xvfb
    - kill $XVFB_PID || true
  artifacts:
    when: always
    paths:
      - target/surefire-reports/
      - target/allure-results/
      - screenshots/
    reports:
      junit: target/surefire-reports/*.xml
  only:
    - merge_requests
    - main
    - develop

test:firefox:
  stage: test
  image: maven:3.8.6-openjdk-11
  variables:
    BROWSER: firefox
    TEST_ENV: $CI_COMMIT_REF_NAME
    BASE_URL: $CI_COMMIT_REF_NAME == "main" && "https://staging.example.com" || "https://qa.example.com"
  before_script:
    # 启动Xvfb（用于无头模式）
    - export DISPLAY=:99
    - Xvfb :99 -screen 0 1920x1080x24 &
    - export XVFB_PID=$!
    - sleep 3
  script:
    - echo "运行Firefox浏览器测试"
    - mvn clean test -Dbrowser=firefox -Dtest.env=$TEST_ENV -Dbase.url=$BASE_URL -Dheadless=true
  after_script:
    # 停止Xvfb
    - kill $XVFB_PID || true
  artifacts:
    when: always
    paths:
      - target/surefire-reports/
      - target/allure-results/
      - screenshots/
    reports:
      junit: target/surefire-reports/*.xml
  only:
    - merge_requests
    - main
    - develop

# 报告阶段
allure-report:
  stage: report
  image: node:16
  dependencies:
    - test:chrome
    - test:firefox
  before_script:
    # 安装Allure命令行工具
    - npm install -g allure-commandline
  script:
    - echo "生成Allure报告"
    - mkdir -p target/allure-report
    - allure generate target/allure-results -o target/allure-report --clean
  artifacts:
    paths:
      - target/allure-report/
  only:
    - merge_requests
    - main
    - develop

# 通知阶段
notify-success:
  stage: notify
  image: alpine:latest
  script:
    - echo "测试执行成功"
    - apk add --no-cache curl
    - |
      curl -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
      -H "Content-Type: application/json" \
      -d '{
        "chat_id": "${TELEGRAM_CHAT_ID}",
        "text": "✅ 测试执行成功\n项目: ${CI_PROJECT_NAME}\n分支: ${CI_COMMIT_REF_NAME}\n提交者: ${CI_COMMIT_AUTHOR}\n查看报告: ${CI_JOB_URL}"
      }'
  only:
    - main
    - develop
  when: on_success

notify-failure:
  stage: notify
  image: alpine:latest
  script:
    - echo "测试执行失败"
    - apk add --no-cache curl
    - |
      curl -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
      -H "Content-Type: application/json" \
      -d '{
        "chat_id": "${TELEGRAM_CHAT_ID}",
        "text": "❌ 测试执行失败\n项目: ${CI_PROJECT_NAME}\n分支: ${CI_COMMIT_REF_NAME}\n提交者: ${CI_COMMIT_AUTHOR}\n查看详情: ${CI_JOB_URL}"
      }'
  only:
    - main
    - develop
  when: on_failure
```

## 9.6 章节总结

本章深入讲解了Selenium测试报告生成技术与CI/CD集成方法，这是将自动化测试集成到现代软件开发流程中的关键步骤。通过学习测试报告的生成、主流报告工具的使用以及CI/CD平台的集成，您现在应该能够构建完整的自动化测试流水线，提供高质量的测试报告和及时的反馈机制。

### 关键要点回顾

1. **测试报告概述**：重要性、类型、优秀报告的特点
2. **TestNG默认报告**：内置报告、自定义报告生成器
3. **Extent Reports**：集成、监听器实现、测试基类封装
4. **Allure报告**：框架特点、监听器实现、工具类封装
5. **CI/CD集成**：Jenkins、GitHub Actions、GitLab CI/CD集成方法
6. **通知机制**：邮件通知、即时通讯通知、报告归档

### 下一步学习

在下一章中，我们将学习Selenium最佳实践与性能优化，这是提高自动化测试效率和质量的关键技术。我们将深入了解测试设计的最佳实践、性能优化技巧、代码质量保证以及如何构建长期可持续的自动化测试体系。

## 9.7 实践练习

1. **自定义TestNG报告**：实现一个自定义的TestNG报告生成器，支持HTML、JSON和Markdown格式
2. **Extent Reports集成**：将Extent Reports集成到现有的测试框架中，并添加自定义功能
3. **Allure报告配置**：配置Allure报告，添加环境信息、参数和自定义分类
4. **Jenkins流水线**：创建一个Jenkins流水线，集成Selenium测试和多种报告
5. **GitHub Actions工作流**：设计一个GitHub Actions工作流，支持多浏览器、多环境的并行测试

请完成以上练习，并思考：
- 在什么情况下应该选择哪种报告工具？
- 如何设计CI/CD流水线以实现最佳的测试反馈机制？
- 如何处理测试报告中的敏感信息？

通过思考这些问题，您将更深入地理解测试报告生成和CI/CD集成的最佳实践。