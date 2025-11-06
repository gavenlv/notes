package com.example.gherkin;

import io.cucumber.junit.platform.engine.Cucumber;
import org.junit.platform.suite.api.ConfigurationParameter;
import org.junit.platform.suite.api.IncludeEngines;
import org.junit.platform.suite.api.SelectClasspathResource;
import org.junit.platform.suite.api.Suite;

/**
 * Cucumber测试运行器
 * 配置Cucumber测试环境和特性文件位置
 */
@Suite
@IncludeEngines("cucumber")
@SelectClasspathResource("features")
@ConfigurationParameter(key = Cucumber.GLUE_PROPERTY_NAME, value = "com.example.gherkin.stepdefinitions,com.example.gherkin.transformer")
@ConfigurationParameter(key = Cucumber.PLUGIN_PROPERTY_NAME, value = "pretty,html:target/cucumber-reports/report.html,json:target/cucumber-reports/report.json,junit:target/cucumber-reports/report.xml")
@ConfigurationParameter(key = Cucumber.OBJECT_FACTORY_PROPERTY_NAME, value = "io.cucumber.spring.SpringFactory")
public class CucumberTestRunner {
}