// examples/test/main_test.go
package test

import (
    "testing"
    "github.com/gruntwork-io/terratest/modules/terraform"
    "github.com/stretchr/testify/assert"
)

func TestInstanceTypeValidation(t *testing.T) {
    terraformOptions := &terraform.Options{
        TerraformDir: "..",
        Vars: map[string]interface{}{
            "project_name":  "test-project",
            "environment":   "dev",
            "instance_type": "invalid-type",
        },
    }

    // 预期部署会失败
    _, err := terraform.InitAndPlanE(t, terraformOptions)
    assert.Error(t, err)
}

func TestValidInstanceType(t *testing.T) {
    terraformOptions := &terraform.Options{
        TerraformDir: "..",
        Vars: map[string]interface{}{
            "project_name":  "test-project",
            "environment":   "dev",
            "instance_type": "t2.micro",
        },
    }

    defer terraform.Destroy(t, terraformOptions)
    
    terraform.InitAndApply(t, terraformOptions)
    
    instanceID := terraform.Output(t, terraformOptions, "instance_id")
    assert.NotEmpty(t, instanceID)
}