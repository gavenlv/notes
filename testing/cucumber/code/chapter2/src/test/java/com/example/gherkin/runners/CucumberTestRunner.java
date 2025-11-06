package com.example.gherkin.runners;

import io.cucumber.junit.Cucumber;
import io.cucumber.junit.CucumberOptions;
import org.junit.runner.RunWith;

/**
 * Cucumber测试运行器
 * 用于执行Gherkin特性文件
 */
@RunWith(Cucumber.class)
@CucumberOptions(
    features = "src/test/resources/features",  // 特性文件路径
    glue = "com.example.gherkin.stepdefinitions",  // 步骤定义包路径
    plugin = {
        "pretty",  // 控制台输出格式
        "html:target/cucumber-reports/report.html",  // HTML报告
        "json:target/cucumber-reports/report.json",  // JSON报告
        "junit:target/cucumber-reports/report.xml"   // JUnit格式报告
    },
    monochrome = true,  // 控制台输出单色显示
    strict = true,  // 严格模式，未定义的步骤会导致测试失败
    dryRun = false,  // 非干运行模式，实际执行测试
    tags = {"not @ignore"}  // 排除标记为@ignore的场景
)
public class CucumberTestRunner {
    // 测试运行器类，不需要实现任何方法
}