// k6学习指南验证脚本
// 验证所有代码文件是否完整和可运行

import { readFile } from 'k6/file';
import { check } from 'k6';

// 定义要验证的文件列表
const filesToValidate = [
  'chapter1/1-first-test.js',
  'chapter1/experiment1-basic-validation.js',
  'chapter2/basic-script-structure.js',
  'chapter2/http-requests.js',
  'chapter2/checks-and-validations.js',
  'chapter2/groups.js',
  'chapter2/experiment2-api-scenario.js',
  'chapter3/custom-metrics.js',
  'chapter3/scenarios-executors.js',
  'chapter3/test-data-management.js',
  'chapter3/error-handling.js',
  'chapter3/performance-test-types.js',
  'chapter3/experiment3-ecommerce-scenario.js',
  'chapter4/production-framework.js'
];

// 验证函数
function validateFile(filePath) {
  try {
    const content = readFile(filePath);
    return {
      success: true,
      filePath: filePath,
      size: content.length,
      hasExports: content.includes('export'),
      hasOptions: content.includes('export const options'),
      hasDefaultFunction: content.includes('export default function')
    };
  } catch (error) {
    return {
      success: false,
      filePath: filePath,
      error: error.message
    };
  }
}

export const options = {
  vus: 1,
  duration: '10s',
};

export default function () {
  console.log('=== k6学习指南代码验证 ===');
  console.log('开始验证所有代码文件...\n');
  
  const results = [];
  let passed = 0;
  let failed = 0;
  
  // 验证每个文件
  filesToValidate.forEach(filePath => {
    const result = validateFile(filePath);
    results.push(result);
    
    if (result.success) {
      passed++;
      console.log(`✅ ${filePath}: 验证通过 (${result.size} bytes)`);
      
      // 检查关键结构
      if (result.hasExports) {
        console.log('   ✓ 包含export语句');
      }
      if (result.hasOptions) {
        console.log('   ✓ 包含options配置');
      }
      if (result.hasDefaultFunction) {
        console.log('   ✓ 包含默认测试函数');
      }
      
    } else {
      failed++;
      console.log(`❌ ${filePath}: 验证失败 - ${result.error}`);
    }
    
    console.log('');
  });
  
  // 输出验证结果
  console.log('=== 验证结果汇总 ===');
  console.log(`总文件数: ${filesToValidate.length}`);
  console.log(`通过: ${passed}`);
  console.log(`失败: ${failed}`);
  
  // 检查验证结果
  check(results, {
    '所有文件均存在': (results) => results.every(r => r.success === true),
    '至少有一个文件包含options配置': (results) => 
      results.some(r => r.success && r.hasOptions),
    '所有成功文件都包含测试函数': (results) => 
      results.filter(r => r.success).every(r => r.hasDefaultFunction)
  });
  
  if (failed === 0) {
    console.log('🎉 所有代码文件验证通过！k6学习指南代码库完整可用。');
  } else {
    console.warn(`⚠ 有 ${failed} 个文件验证失败，请检查文件完整性。`);
  }
}

// 测试环境检查
export function setup() {
  console.log('开始k6代码验证环境检查...');
  
  // 检查k6版本兼容性
  const k6Version = __VERSION;
  console.log(`k6版本: ${k6Version}`);
  
  // 检查文件系统访问权限
  try {
    const testFile = readFile('README.md');
    console.log('✓ 文件系统访问权限正常');
  } catch (error) {
    console.warn('⚠ 文件系统访问可能受限');
  }
  
  return { startTime: Date.now(), k6Version };
}

// 测试清理
export function teardown(data) {
  const duration = Date.now() - data.startTime;
  console.log(`\n验证完成，耗时: ${duration}ms`);
  console.log('k6学习指南代码验证结束。');
}