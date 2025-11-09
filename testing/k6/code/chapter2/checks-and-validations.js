// 第2章：检查点和验证示例
// 演示各种验证方法和检查点使用

import http from 'k6/http';
import { check } from 'k6';

const BASE_URL = 'https://httpbin.test.k6.io';

export const options = {
  vus: 3,
  duration: '2m',
  thresholds: {
    checks: ['rate>0.95'], // 检查点通过率阈值
  },
};

export default function () {
  const response = http.get(`${BASE_URL}/json`);
  
  // 1. 基本状态检查
  check(response, {
    'status is 200': (r) => r.status === 200,
    'response time < 2s': (r) => r.timings.duration < 2000,
  });
  
  // 2. 响应头检查
  check(response, {
    'has content type header': (r) => r.headers['Content-Type'] !== undefined,
    'content type is json': (r) => r.headers['Content-Type'].includes('application/json'),
  });
  
  // 3. JSON响应检查
  check(response, {
    'response is valid JSON': (r) => {
      try {
        JSON.parse(r.body);
        return true;
      } catch {
        return false;
      }
    },
    
    'JSON contains slideshow': (r) => {
      const json = r.json();
      return json.slideshow !== undefined;
    },
    
    'slideshow has title': (r) => {
      const json = r.json();
      return json.slideshow && json.slideshow.title !== undefined;
    },
    
    'slideshow has slides': (r) => {
      const json = r.json();
      return json.slideshow && 
             json.slideshow.slides && 
             Array.isArray(json.slideshow.slides);
    },
    
    'slides count > 0': (r) => {
      const json = r.json();
      return json.slideshow && 
             json.slideshow.slides && 
             json.slideshow.slides.length > 0;
    },
  });
  
  // 4. 复杂逻辑检查
  check(response, {
    'first slide has required fields': (r) => {
      const json = r.json();
      if (!json.slideshow || !json.slideshow.slides) return false;
      
      const firstSlide = json.slideshow.slides[0];
      return firstSlide && 
             firstSlide.title !== undefined && 
             firstSlide.type !== undefined;
    },
    
    'all slides have type': (r) => {
      const json = r.json();
      if (!json.slideshow || !json.slideshow.slides) return false;
      
      return json.slideshow.slides.every(slide => slide.type !== undefined);
    },
  });
  
  // 5. 正则表达式检查
  check(response, {
    'contains JSON keyword': (r) => /"slideshow"/.test(r.body),
    'contains valid structure': (r) => /"title"\s*:"/.test(r.body),
  });
  
  // 6. 错误处理检查
  try {
    const errorResponse = http.get(`${BASE_URL}/status/404`);
    
    check(errorResponse, {
      '404 status is handled': (r) => r.status === 404,
      '404 response is valid': (r) => r.body.length > 0,
    });
    
  } catch (error) {
    // 处理网络错误等异常情况
    console.log('Error occurred:', error.message);
  }
  
  // 7. 性能指标检查
  check(response, {
    'DNS lookup time reasonable': (r) => r.timings.lookup < 1000,
    'TCP connection time reasonable': (r) => r.timings.connect < 500,
    'TTFB reasonable': (r) => r.timings.waiting < 2000,
    'data transfer time reasonable': (r) => r.timings.receiving < 1000,
  });
  
  // 8. 自定义检查函数
  function validateSlideStructure(slide) {
    return slide && 
           typeof slide.title === 'string' &&
           typeof slide.type === 'string' &&
           slide.title.length > 0 &&
           slide.type.length > 0;
  }
  
  check(response, {
    'slides have valid structure': (r) => {
      const json = r.json();
      if (!json.slideshow || !json.slideshow.slides) return false;
      
      return json.slideshow.slides.every(validateSlideStructure);
    },
  });
}