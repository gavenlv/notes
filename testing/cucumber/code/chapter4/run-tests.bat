@echo off
echo 运行第4章：数据驱动测试示例
echo ================================

echo.
echo 1. 清理并编译项目...
call mvn clean compile

echo.
echo 2. 运行所有测试...
call mvn test

echo.
echo 3. 测试报告已生成在 target/cucumber-reports/ 目录中
echo.

echo 4. 运行特定特性文件测试...
echo.
echo 运行产品搜索功能测试:
call mvn test -Dcucumber.filter.tags="@product-search"

echo.
echo 运行银行账户管理测试:
call mvn test -Dcucumber.filter.tags="@bank-account"

echo.
echo 运行API测试:
call mvn test -Dcucumber.filter.tags="@api-testing"

echo.
echo 运行场景大纲测试:
call mvn test -Dcucumber.filter.tags="@scenario-outline"

echo.
echo 运行参数转换器测试:
call mvn test -Dcucumber.filter.tags="@parameter-transformer"

echo.
echo 运行数据表测试:
call mvn test -Dcucumber.filter.tags="@data-table"

echo.
echo 测试完成!
pause