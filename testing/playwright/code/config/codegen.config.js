// config/codegen.config.js
/**
 * CodeGen配置文件
 * 提供CodeGen工具的各种配置选项
 */

const { devices } = require('@playwright/test');

const codegenConfig = {
  // 基本配置
  basic: {
    // 目标浏览器
    browser: 'chromium', // 'chromium' | 'firefox' | 'webkit'
    
    // 是否无头模式
    headless: false,
    
    // 视口大小
    viewport: { width: 1280, height: 720 },
    
    // 超时设置
    timeout: 30000,
    
    // 输出文件路径
    output: 'generated-test.spec.js'
  },

  // 设备模拟配置
  devices: {
    // 桌面设备
    desktop: {
      viewport: { width: 1920, height: 1080 },
      deviceScaleFactor: 1,
      isMobile: false,
      hasTouch: false,
      defaultBrowserType: 'chromium'
    },
    
    // 移动设备 - iPhone 12
    iphone12: devices['iPhone 12'],
    
    // 移动设备 - Pixel 5
    pixel5: devices['Pixel 5'],
    
    // 平板设备 - iPad
    ipad: devices['iPad (gen 7)']
  },

  // 地理位置配置
  geolocation: {
    // 北京
    beijing: {
      longitude: 116.4074,
      latitude: 39.9042,
      accuracy: 100
    },
    
    // 纽约
    newyork: {
      longitude: -74.0060,
      latitude: 40.7128,
      accuracy: 100
    },
    
    // 伦敦
    london: {
      longitude: -0.1276,
      latitude: 51.5074,
      accuracy: 100
    }
  },

  // 本地化配置
  locale: {
    // 中文
    chinese: {
      locale: 'zh-CN',
      timezoneId: 'Asia/Shanghai'
    },
    
    // 英文
    english: {
      locale: 'en-US',
      timezoneId: 'America/New_York'
    },
    
    // 日文
    japanese: {
      locale: 'ja-JP',
      timezoneId: 'Asia/Tokyo'
    }
  },

  // 网络配置
  network: {
    // 网络拦截配置
    intercept: {
      // API请求拦截
      api: {
        pattern: '**/api/**',
        mockResponse: {
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ success: true, data: [] })
        }
      },
      
      // 静态资源拦截
      static: {
        pattern: '**/*.{png,jpg,jpeg,gif,svg}',
        mockResponse: {
          status: 200,
          contentType: 'image/png',
          body: Buffer.from('') // 空图片
        }
      }
    },
    
    // 网络条件模拟
    conditions: {
      // 快速网络
      fast: {
        offline: false,
        downloadThroughput: 50 * 1024 * 1024 / 8, // 50 Mbps
        uploadThroughput: 25 * 1024 * 1024 / 8,   // 25 Mbps
        latency: 10 // 10ms
      },
      
      // 慢速网络
      slow: {
        offline: false,
        downloadThroughput: 1.5 * 1024 * 1024 / 8, // 1.5 Mbps
        uploadThroughput: 750 * 1024 / 8,          // 750 Kbps
        latency: 100 // 100ms
      },
      
      // 离线模式
      offline: {
        offline: true
      }
    }
  },

  // 认证配置
  authentication: {
    // 基本认证
    basic: {
      username: 'testuser',
      password: 'testpass'
    },
    
    // 表单认证
    form: {
      loginUrl: 'https://example.com/login',
      usernameSelector: 'input[name="username"]',
      passwordSelector: 'input[name="password"]',
      submitSelector: 'button[type="submit"]'
    },
    
    // OAuth认证
    oauth: {
      clientId: 'your-client-id',
      clientSecret: 'your-client-secret',
      redirectUri: 'https://example.com/callback'
    }
  },

  // 录制配置
  recording: {
    // 视频录制
    video: {
      enabled: true,
      dir: 'videos/',
      size: { width: 1280, height: 720 }
    },
    
    // 截图配置
    screenshot: {
      enabled: true,
      dir: 'screenshots/',
      fullPage: true
    },
    
    // 网络日志
    networkLog: {
      enabled: true,
      format: 'har', // 'har' | 'json'
      outputPath: 'network-logs/'
    }
  },

  // 代码生成配置
  codegen: {
    // 目标语言
    targetLanguage: 'javascript', // 'javascript' | 'typescript' | 'python' | 'csharp' | 'java'
    
    // 代码风格
    codeStyle: {
      indentSize: 2,
      useSemicolons: true,
      quoteStyle: 'single', // 'single' | 'double'
      trailingComma: 'es5'   // 'none' | 'es5' | 'all'
    },
    
    // 断言生成
    assertions: {
      enabled: true,
      types: ['visibility', 'text', 'count', 'attribute'],
      autoGenerate: true
    },
    
    // 等待策略
    waitStrategy: {
      beforeAction: 'visible', // 'visible' | 'attached' | 'none'
      afterNavigation: 'networkidle', // 'load' | 'domcontentloaded' | 'networkidle'
      defaultTimeout: 5000
    }
  },

  // 环境配置
  environments: {
    development: {
      baseURL: 'http://localhost:3000',
      timeout: 30000,
      slowMo: 100 // 减慢操作速度，便于观察
    },
    
    staging: {
      baseURL: 'https://staging.example.com',
      timeout: 60000,
      slowMo: 50
    },
    
    production: {
      baseURL: 'https://example.com',
      timeout: 30000,
      slowMo: 0
    }
  },

  // 测试数据配置
  testData: {
    // 用户数据
    users: {
      standard: {
        username: 'standard_user',
        password: 'secret_sauce',
        email: 'standard@example.com'
      },
      
      admin: {
        username: 'admin_user',
        password: 'admin_password',
        email: 'admin@example.com'
      },
      
      invalid: {
        username: 'invalid_user',
        password: 'wrong_password',
        email: 'invalid@example.com'
      }
    },
    
    // 产品数据
    products: {
      standard: {
        name: 'Standard Product',
        price: 29.99,
        description: 'A standard test product'
      },
      
      premium: {
        name: 'Premium Product',
        price: 99.99,
        description: 'A premium test product'
      }
    }
  },

  // 高级配置
  advanced: {
    // 并行执行配置
    parallel: {
      enabled: true,
      workers: 4,
      fullyParallel: true
    },
    
    // 重试配置
    retries: {
      count: 2,
      mode: 'default' // 'default' | 'all' | 'none'
    },
    
    // 报告配置
    reporter: [
      ['html', { outputFolder: 'playwright-report' }],
      ['json', { outputFile: 'test-results.json' }],
      ['junit', { outputFile: 'junit.xml' }]
    ],
    
    // 调试配置
    debug: {
      enabled: false,
      headless: false,
      slowMo: 1000,
      devtools: true
    }
  }
};

// 配置生成器函数
function generateCodegenCommand(options = {}) {
  const {
    url = 'https://example.com',
    browser = 'chromium',
    device = null,
    viewport = null,
    locale = null,
    geolocation = null,
    output = 'generated-test.spec.js',
    headless = false,
    ...otherOptions
  } = options;

  let command = 'npx playwright codegen';

  // 添加URL
  command += ` ${url}`;

  // 添加浏览器选项
  command += ` --browser=${browser}`;

  // 添加设备选项
  if (device) {
    command += ` --device="${device}"`;
  }

  // 添加视口选项
  if (viewport) {
    command += ` --viewport-size=${viewport.width},${viewport.height}`;
  }

  // 添加本地化选项
  if (locale) {
    command += ` --lang=${locale}`;
  }

  // 添加地理位置选项
  if (geolocation) {
    command += ` --geolocation="${geolocation.latitude},${geolocation.longitude}"`;
  }

  // 添加输出选项
  command += ` --output=${output}`;

  // 添加无头模式选项
  if (headless) {
    command += ' --headless';
  }

  // 添加其他选项
  Object.entries(otherOptions).forEach(([key, value]) => {
    if (value !== undefined && value !== null) {
      command += ` --${key}=${value}`;
    }
  });

  return command;
}

// 环境特定的配置生成器
function getEnvironmentConfig(environment = 'development') {
  const envConfig = codegenConfig.environments[environment];
  if (!envConfig) {
    throw new Error(`Unknown environment: ${environment}`);
  }

  return {
    ...codegenConfig.basic,
    ...envConfig,
    baseURL: envConfig.baseURL
  };
}

// 设备特定的配置生成器
function getDeviceConfig(deviceName = 'desktop') {
  const deviceConfig = codegenConfig.devices[deviceName];
  if (!deviceConfig) {
    throw new Error(`Unknown device: ${deviceName}`);
  }

  return deviceConfig;
}

// 导出配置和工具函数
module.exports = {
  codegenConfig,
  generateCodegenCommand,
  getEnvironmentConfig,
  getDeviceConfig
};

// 使用示例
if (require.main === module) {
  // 生成基本命令
  console.log('基本CodeGen命令:');
  console.log(generateCodegenCommand());

  // 生成移动端命令
  console.log('\n移动端CodeGen命令:');
  console.log(generateCodegenCommand({
    url: 'https://m.example.com',
    device: 'iPhone 12',
    output: 'mobile-test.spec.js'
  }));

  // 生成地理位置测试命令
  console.log('\n地理位置测试CodeGen命令:');
  console.log(generateCodegenCommand({
    url: 'https://maps.example.com',
    geolocation: { latitude: 39.9042, longitude: 116.4074 },
    locale: 'zh-CN',
    output: 'geolocation-test.spec.js'
  }));

  // 显示环境配置
  console.log('\n开发环境配置:');
  console.log(JSON.stringify(getEnvironmentConfig('development'), null, 2));
}