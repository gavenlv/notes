// examples/test/e2e_test.go
package test

import (
    "fmt"
    "testing"
    "time"
    "github.com/gruntwork-io/terratest/modules/terraform"
    "github.com/gruntwork-io/terratest/modules/http-helper"
)

func TestEndToEndDeployment(t *testing.T) {
    // 配置选项
    terraformOptions := &terraform.Options{
        TerraformDir: "..",
        Vars: map[string]interface{}{
            "project_name":  "e2e-test",
            "environment":   "test",
            "instance_type": "t2.micro",
        },
    }

    // 清理
    defer terraform.Destroy(t, terraformOptions)

    // 部署
    terraform.InitAndApply(t, terraformOptions)

    // 获取实例 IP
    instanceIP := terraform.Output(t, terraformOptions, "instance_ip")

    // 等待服务启动
    time.Sleep(30 * time.Second)

    // 验证 HTTP 服务
    http_helper.HttpGetWithRetry(t, fmt.Sprintf("http://%s", instanceIP), 200, "Hello", 30, 5*time.Second)
}