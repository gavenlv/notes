// examples/tests/vpc_test.go
package test

import (
  "testing"
  
  "github.com/gruntwork-io/terratest/modules/terraform"
  "github.com/stretchr/testify/assert"
)

func TestVPCModule(t *testing.T) {
  terraformOptions := &terraform.Options{
    TerraformDir: "../modules/vpc",
    Vars: map[string]interface{}{
      "name":       "test-vpc",
      "cidr_block": "10.0.0.0/16",
    },
  }
  
  defer terraform.Destroy(t, terraformOptions)
  terraform.InitAndApply(t, terraformOptions)
  
  // 验证 VPC 是否创建成功
  vpcID := terraform.Output(t, terraformOptions, "vpc_id")
  assert.NotEmpty(t, vpcID)
  
  // 验证互联网网关是否创建成功
  igwID := terraform.Output(t, terraformOptions, "internet_gateway_id")
  assert.NotEmpty(t, igwID)
}