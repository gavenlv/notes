package com.example.gherkin.runners;

import io.cucumber.junit.Cucumber;
import io.cucumber.junit.CucumberOptions;
import org.junit.runner.RunWith;

/**
 * Cucumber测试运行器
 */
@RunWith(Cucumber.class)
@CucumberOptions(
        features = {"src/test/resources/features"},
        glue = {"com.example.gherkin.stepdefinitions", "com.example.gherkin.hooks"},
        plugin = {
                "pretty",
                "html:target/cucumber-html-report",
                "json:target/cucumber.json",
                "junit:target/cucumber-junit-report.xml"
        },
        tags = {"not @ignore"},
        monochrome = true,
        strict = true
)
public class CucumberTestRunner {
}