# 前端编码挑战及解决方案

## 1. JavaScript 核心能力

### 挑战1: 实现防抖函数 (Debounce)
**问题描述:**
实现一个防抖函数，该函数可以限制函数在指定时间内只执行一次，常用于处理滚动、窗口调整和搜索输入等频繁触发的事件。

**要求:**
- 函数接受两个参数：要防抖的函数和等待时间
- 支持立即执行选项 (leading edge)
- 支持取消功能

**解决方案:**
```javascript
function debounce(func, wait, immediate = false) {
  let timeout;
  let result;

  const debounced = function(...args) {
    const context = this;

    // 清除之前的定时器
    if (timeout) clearTimeout(timeout);

    // 立即执行
    if (immediate) {
      // 如果已经执行过，不再执行
      const callNow = !timeout;
      timeout = setTimeout(() => {
        timeout = null;
      }, wait);
      if (callNow) result = func.apply(context, args);
    } else {
      // 延迟执行
      timeout = setTimeout(() => {
        func.apply(context, args);
      }, wait);
    }

    return result;
  };

  // 取消功能
  debounced.cancel = function() {
    clearTimeout(timeout);
    timeout = null;
  };

  return debounced;
}
```

**使用示例:**
```javascript
// 应用场景：搜索输入
const searchInput = document.getElementById('search-input');
const search = debounce((value) => {
  console.log('Searching for:', value);
  // 执行搜索请求
}, 500);

searchInput.addEventListener('input', (e) => {
  search(e.target.value);
});
```

### 挑战2: 实现节流函数 (Throttle)
**问题描述:**
实现一个节流函数，该函数可以限制函数在指定时间内最多执行一次，常用于处理滚动和鼠标移动等高频事件。

**要求:**
- 函数接受两个参数：要节流的函数和时间间隔
- 支持立即执行 (leading edge)
- 支持尾部执行 (trailing edge)

**解决方案:**
```javascript
function throttle(func, wait, options = {}) {
  let timeout;
  let previous = 0;
  const { leading = true, trailing = true } = options;

  const throttled = function(...args) {
    const now = Date.now();
    const context = this;

    // 如果不允许立即执行，且是第一次执行，则设置previous为当前时间
    if (!previous && leading === false) previous = now;

    // 计算剩余时间
    const remaining = wait - (now - previous);

    if (remaining <= 0 || remaining > wait) {
      // 清除之前的定时器
      if (timeout) {
        clearTimeout(timeout);
        timeout = null;
      }
      // 执行函数
      previous = now;
      func.apply(context, args);
    } else if (!timeout && trailing === true) {
      // 设置定时器，在剩余时间后执行
      timeout = setTimeout(() => {
        previous = Date.now();
        timeout = null;
        func.apply(context, args);
      }, remaining);
    }
  };

  // 取消功能
  throttled.cancel = function() {
    clearTimeout(timeout);
    previous = 0;
    timeout = null;
  };

  return throttled;
}
```

## 2. 算法与数据结构

### 挑战3: 实现深拷贝函数
**问题描述:**
实现一个深拷贝函数，可以复制复杂的JavaScript对象，包括循环引用、函数、日期等特殊类型。

**要求:**
- 支持基本数据类型
- 支持对象、数组、函数、日期、正则表达式
- 处理循环引用
- 性能优化

**解决方案:**
```javascript
function deepClone(target, map = new WeakMap()) {
  // 处理基本数据类型和null
  if (target === null || typeof target !== 'object') {
    return target;
  }

  // 处理循环引用
  if (map.has(target)) {
    return map.get(target);
  }

  // 处理日期
  if (target instanceof Date) {
    return new Date(target);
  }

  // 处理正则表达式
  if (target instanceof RegExp) {
    return new RegExp(target.source, target.flags);
  }

  // 处理函数
  if (typeof target === 'function') {
    return target;
  }

  // 创建新的对象或数组
  const clone = Array.isArray(target) ? [] : {};

  // 存储映射关系，防止循环引用
  map.set(target, clone);

  // 递归复制属性
  for (const key in target) {
    if (Object.prototype.hasOwnProperty.call(target, key)) {
      clone[key] = deepClone(target[key], map);
    }
  }

  // 复制Symbol类型的属性
  const symbolKeys = Object.getOwnPropertySymbols(target);
  for (const key of symbolKeys) {
    clone[key] = deepClone(target[key], map);
  }

  return clone;
}
```

### 挑战4: 实现Promise.allSettled
**问题描述:**
实现Promise.allSettled方法，该方法接收一个Promise数组，返回一个新的Promise，当所有Promise都已结算（无论成功或失败）时，该Promise才会 resolve。

**要求:**
- 处理Promise数组
- 返回一个包含所有Promise结果的数组
- 每个结果对象包含status和value/reason
- 不中断执行，即使有Promise失败

**解决方案:**
```javascript
Promise.allSettled = function(promises) {
  // 确保输入是数组
  if (!Array.isArray(promises)) {
    return Promise.reject(new TypeError('Argument must be an array'));
  }

  // 转换非Promise值为Promise
  const promiseArray = promises.map(p => Promise.resolve(p));

  return new Promise((resolve) => {
    const results = [];
    let completed = 0;
    const total = promiseArray.length;

    // 如果数组为空，直接返回空结果
    if (total === 0) {
      return resolve(results);
    }

    promiseArray.forEach((promise, index) => {
      promise
        .then(value => {
          results[index] = {
            status: 'fulfilled',
            value
          };
        })
        .catch(reason => {
          results[index] = {
            status: 'rejected',
            reason
          };
        })
        .finally(() => {
          completed++;
          if (completed === total) {
            resolve(results);
          }
        });
    });
  });
};
```

## 3. DOM 操作与事件处理

### 挑战5: 实现无限滚动加载
**问题描述:**
实现一个无限滚动加载功能，当用户滚动到页面底部时，自动加载更多数据。

**要求:**
- 监听滚动事件，避免频繁触发
- 计算滚动到底部的条件
- 加载数据时显示加载状态
- 处理加载失败的情况
- 支持停止加载（如没有更多数据时）

**解决方案:**
```javascript
class InfiniteScroll {
  constructor(options) {
    this.container = options.container || window;
    this.loadMore = options.loadMore;
    this.hasMore = options.hasMore !== undefined ? options.hasMore : true;
    this.loading = false;
    this.threshold = options.threshold || 100;
    this.scrollHandler = this.throttle(this.handleScroll.bind(this), 200);

    this.init();
  }

  init() {
    this.container.addEventListener('scroll', this.scrollHandler);
  }

  handleScroll() {
    if (this.loading || !this.hasMore) return;

    const { scrollTop, scrollHeight, clientHeight } = this.container === window
      ? { 
          scrollTop: window.scrollY,
          scrollHeight: document.documentElement.scrollHeight,
          clientHeight: window.innerHeight
        }
      : this.container;

    // 计算是否滚动到底部
    if (scrollTop + clientHeight + this.threshold >= scrollHeight) {
      this.loading = true;
      this.loadMore()
        .then((hasMore) => {
          this.hasMore = hasMore !== undefined ? hasMore : this.hasMore;
          this.loading = false;
        })
        .catch(() => {
          this.loading = false;
        });
    }
  }

  // 节流函数
  throttle(func, wait) {
    let timeout;
    let previous = 0;

    return function(...args) {
      const now = Date.now();
      const remaining = wait - (now - previous);
      const context = this;

      if (remaining <= 0) {
        if (timeout) {
          clearTimeout(timeout);
          timeout = null;
        }
        previous = now;
        func.apply(context, args);
      } else if (!timeout) {
        timeout = setTimeout(() => {
          previous = Date.now();
          timeout = null;
          func.apply(context, args);
        }, remaining);
      }
    };
  }

  // 销毁实例
  destroy() {
    this.container.removeEventListener('scroll', this.scrollHandler);
  }
}
```

**使用示例:**
```javascript
const infiniteScroll = new InfiniteScroll({
  loadMore: async () => {
    // 显示加载状态
    showLoading();
    try {
      // 加载数据
      const data = await fetchData(page);
      // 渲染数据
      renderData(data);
      // 更新页码
      page++;
      // 判断是否还有更多数据
      const hasMore = data.length > 0;
      // 隐藏加载状态
      hideLoading();
      return hasMore;
    } catch (error) {
      console.error('Failed to load data:', error);
      // 显示错误信息
      showError();
      return true; // 允许重试
    }
  },
  hasMore: true,
  threshold: 200
});
```

## 4. React 相关挑战

### 挑战6: 实现一个 React 自定义 Hook - useDebounce
**问题描述:**
实现一个 React 自定义 Hook，用于防抖处理，可以延迟更新状态，常用于搜索输入等场景。

**要求:**
- 接受一个值和延迟时间
- 返回防抖后的值
- 支持清除防抖
- 组件卸载时清除定时器

**解决方案:**
```javascript
import { useState, useEffect, useRef } from 'react';

function useDebounce(value, delay) {
  // 状态存储防抖后的值
  const [debouncedValue, setDebouncedValue] = useState(value);
  // 引用存储定时器
  const timerRef = useRef(null);

  useEffect(() => {
    // 清除之前的定时器
    if (timerRef.current) {
      clearTimeout(timerRef.current);
    }

    // 设置新的定时器
    timerRef.current = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    // 组件卸载时清除定时器
    return () => {
      if (timerRef.current) {
        clearTimeout(timerRef.current);
      }
    };
  }, [value, delay]); // 依赖项: value 和 delay

  // 提供清除防抖的方法
  const clearDebounce = () => {
    if (timerRef.current) {
      clearTimeout(timerRef.current);
      timerRef.current = null;
    }
  };

  return [debouncedValue, clearDebounce];
}
```

**使用示例:**
```javascript
function SearchComponent() {
  const [searchTerm, setSearchTerm] = useState('');
  // 防抖处理，延迟 500ms
  const [debouncedSearchTerm, clearDebounce] = useDebounce(searchTerm, 500);
  const [searchResults, setSearchResults] = useState([]);
  const [loading, setLoading] = useState(false);

  // 监听防抖后的搜索词变化
  useEffect(() => {
    if (debouncedSearchTerm) {
      // 执行搜索
      const fetchSearchResults = async () => {
        setLoading(true);
        try {
          const results = await searchAPI(debouncedSearchTerm);
          setSearchResults(results);
        } catch (error) {
          console.error('Search failed:', error);
        } finally {
          setLoading(false);
        }
      };

      fetchSearchResults();
    } else {
      // 清空搜索结果
      setSearchResults([]);
    }
  }, [debouncedSearchTerm]);

  return (
    <div>
      <input
        type="text"
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        placeholder="Search..."
      />
      <button onClick={clearDebounce}>Clear Search</button>

      {loading && <div>Loading...</div>}

      <ul>
        {searchResults.map((result) => (
          <li key={result.id}>{result.title}</li>
        ))}
      </ul>
    </div>
  );
}
```

## 5. 性能优化挑战

### 挑战7: 实现图片懒加载
**问题描述:**
实现图片懒加载功能，当图片进入视口时才加载图片，以提高页面加载性能。

**要求:**
- 监听元素是否进入视口
- 支持使用 IntersectionObserver API
- 降级支持 (不支持 IntersectionObserver 时使用滚动监听)
- 处理图片加载失败的情况
- 支持延迟加载的占位符

**解决方案:**
```javascript
class ImageLazyLoad {
  constructor(options = {}) {
    this.images = document.querySelectorAll(options.selector || '.lazy-image');
    this.rootMargin = options.rootMargin || '0px';
    this.threshold = options.threshold || 0.1;
    this.loadingClass = options.loadingClass || 'lazy-loading';
    this.loadedClass = options.loadedClass || 'lazy-loaded';
    this.errorClass = options.errorClass || 'lazy-error';
    this.observer = null;

    this.init();
  }

  init() {
    // 检查是否支持 IntersectionObserver
    if ('IntersectionObserver' in window) {
      this.initIntersectionObserver();
    } else {
      this.initScrollListener();
    }
  }

  initIntersectionObserver() {
    this.observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          this.loadImage(entry.target);
          // 加载后取消观察
          this.observer.unobserve(entry.target);
        }
      });
    }, {
      rootMargin: this.rootMargin,
      threshold: this.threshold
    });

    // 开始观察所有图片
    this.images.forEach((image) => {
      this.observer.observe(image);
    });
  }

  initScrollListener() {
    // 节流函数
    const throttle = (func, wait) => {
      let timeout;
      return function() {
        const context = this;
        const args = arguments;
        if (!timeout) {
          timeout = setTimeout(() => {
            timeout = null;
            func.apply(context, args);
          }, wait);
        }
      };
    };

    // 检查图片是否在视口中
    const checkImages = throttle(() => {
      this.images.forEach((image) => {
        if (this.isInViewport(image)) {
          this.loadImage(image);
          // 移除已加载的图片
          this.images = Array.from(this.images).filter(img => img !== image);
        }
      });

      // 如果所有图片都已加载，移除滚动监听
      if (this.images.length === 0) {
        window.removeEventListener('scroll', checkImages);
        window.removeEventListener('resize', checkImages);
        window.removeEventListener('orientationchange', checkImages);
      }
    }, 200);

    // 添加事件监听
    window.addEventListener('scroll', checkImages);
    window.addEventListener('resize', checkImages);
    window.addEventListener('orientationchange', checkImages);

    // 初始检查
    checkImages();
  }

  isInViewport(element) {
    const rect = element.getBoundingClientRect();
    return (
      rect.top <= (window.innerHeight || document.documentElement.clientHeight) &&
      rect.left <= (window.innerWidth || document.documentElement.clientWidth) &&
      rect.bottom >= 0 &&
      rect.right >= 0
    );
  }

  loadImage(image) {
    // 添加加载中类
    image.classList.add(this.loadingClass);

    // 获取真实图片地址
    const src = image.getAttribute('data-src') || image.getAttribute('data-lazy');
    if (!src) {
      this.handleError(image);
      return;
    }

    // 创建新图片对象预加载
    const img = new Image();
    img.onload = () => {
      // 设置图片 src
      if (image.tagName === 'IMG') {
        image.src = src;
      } else {
        image.style.backgroundImage = `url('${src}')`;
      }

      // 移除加载中类，添加已加载类
      image.classList.remove(this.loadingClass);
      image.classList.add(this.loadedClass);
    };

    img.onerror = () => {
      this.handleError(image);
    };

    // 设置图片 src 开始加载
    img.src = src;
  }

  handleError(image) {
    // 移除加载中类，添加错误类
    image.classList.remove(this.loadingClass);
    image.classList.add(this.errorClass);

    // 如果有备用图片，尝试加载
    const fallbackSrc = image.getAttribute('data-fallback');
    if (fallbackSrc) {
      const img = new Image();
      img.onload = () => {
        if (image.tagName === 'IMG') {
          image.src = fallbackSrc;
        } else {
          image.style.backgroundImage = `url('${fallbackSrc}')`;
        }
        image.classList.remove(this.errorClass);
        image.classList.add(this.loadedClass);
      };
      img.src = fallbackSrc;
    }
  }

  // 销毁实例
  destroy() {
    if (this.observer) {
      this.observer.disconnect();
    }
    // 移除滚动监听等
    window.removeEventListener('scroll', this.checkImages);
    window.removeEventListener('resize', this.checkImages);
    window.removeEventListener('orientationchange', this.checkImages);
  }
}
```

**使用示例:**
```html
<!-- HTML -->
<img class="lazy-image" data-src="image.jpg" alt="Lazy loaded image">
<div class="lazy-image" data-src="background.jpg"></div>

<script>
  // 初始化懒加载
  const lazyLoad = new ImageLazyLoad({
    selector: '.lazy-image',
    rootMargin: '100px',
    threshold: 0.1
  });
</script>
```