// 第5章：模板字符串与字符串增强 - 代码示例

// 5.1 模板字符串基础
// ====================

// 传统字符串 vs 模板字符串
const traditionalString = 'Hello, world!';
const templateString = `Hello, world!`;

console.log('传统字符串:', traditionalString);
console.log('模板字符串:', templateString);

// 多行字符串
const multiLineTraditional = 'Line 1\nLine 2\nLine 3';
const multiLineTemplate = `Line 1
Line 2
Line 3`;

console.log('传统多行字符串:');
console.log(multiLineTraditional);
console.log('模板多行字符串:');
console.log(multiLineTemplate);

// 字符串插值
const name = 'Alice';
const age = 30;

// 传统字符串拼接
const traditionalGreeting = 'Hello, my name is ' + name + ' and I am ' + age + ' years old.';

// 模板字符串插值
const templateGreeting = `Hello, my name is ${name} and I am ${age} years old.`;

console.log('传统拼接:', traditionalGreeting);
console.log('模板插值:', templateGreeting);

// 表达式计算
const price = 19.99;
const quantity = 3;
const tax = 0.08;

const total = `Total: $${(price * quantity * (1 + tax)).toFixed(2)}`;
console.log('计算表达式:', total);

// 使用条件表达式
const isLoggedIn = true;
const greeting = `Welcome ${isLoggedIn ? 'back' : 'guest'}!`;
console.log('条件表达式:', greeting);

// 调用函数
function formatName(first, last) {
  return `${last}, ${first}`;
}
const fullName = formatName('John', 'Doe');
const formalGreeting = `Dear ${fullName},`;
console.log('函数调用:', formalGreeting);

// 5.2 标签模板
// =============

function simpleTag(strings, ...values) {
  console.log('Strings:', strings);
  console.log('Values:', values);
  return 'Tagged result';
}

const tagResult = simpleTag`My name is ${name} and I am ${age} years old.`;

// HTML转义标签
function html(strings, ...values) {
  let result = '';
  for (let i = 0; i < values.length; i++) {
    // 转义HTML特殊字符
    const escaped = String(values[i])
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
    
    result += strings[i] + escaped;
  }
  result += strings[strings.length - 1];
  return result;
}

const userInput = '<script>alert("XSS")</script>';
const safeHtml = html`<div>${userInput}</div>`;
console.log('HTML转义:', safeHtml);

// 大写转换标签
function uppercase(strings, ...values) {
  let result = '';
  for (let i = 0; i < values.length; i++) {
    result += strings[i] + String(values[i]).toUpperCase();
  }
  result += strings[strings.length - 1];
  return result;
}

const message = uppercase`Hello ${'world'} and ${'javascript'}!`;
console.log('大写转换:', message);

// 5.3 字符串新增方法
// ===================

// includes()方法
const sentence = 'The quick brown fox jumps over the lazy dog';
console.log('includes "fox":', sentence.includes('fox'));
console.log('includes "cat":', sentence.includes('cat'));
console.log('includes "the" from index 10:', sentence.includes('the', 10));

// startsWith()和endsWith()方法
const filename = 'document.pdf';
console.log('startsWith "document":', filename.startsWith('document'));
console.log('endsWith ".pdf":', filename.endsWith('.pdf'));

// repeat()方法
console.log('*'.repeat(10));
console.log('abc'.repeat(3));

// padStart()和padEnd()方法
console.log('42'.padStart(5, '0'));
console.log('abc'.padEnd(10, '*'));

// 格式化输出示例
const items = [
  { id: 1, name: 'Apple', price: 1.99 },
  { id: 10, name: 'Banana', price: 0.99 },
  { id: 100, name: 'Cherry', price: 2.99 }
];

console.log('ID'.padEnd(6) + 'Name'.padEnd(10) + 'Price');
console.log('-'.repeat(25));
items.forEach(item => {
  console.log(
    String(item.id).padEnd(6) + 
    item.name.padEnd(10) + 
    '$' + item.price.toFixed(2)
  );
});

// trimStart()和trimEnd()方法
const paddedString = '   hello world   ';
console.log(`[${paddedString.trim()}]`);
console.log(`[${paddedString.trimStart()}]`);
console.log(`[${paddedString.trimEnd()}]`);

// 5.4 Unicode支持增强
// ===================

// Unicode码点转义
console.log('\u{41}');  // "A"
console.log('\u{1F600}'); // "😀" (笑脸表情)

// 使用String.fromCodePoint()
console.log(String.fromCodePoint(0x1F600)); // "😀"
console.log(String.fromCodePoint(0x41, 0x42, 0x43)); // "ABC"

// codePointAt()方法
const emoji = '😀';
console.log('Length:', emoji.length);
console.log('charCodeAt(0):', emoji.charCodeAt(0));
console.log('charCodeAt(1):', emoji.charCodeAt(1));
console.log('codePointAt(0):', emoji.codePointAt(0));

// 字符串遍历与for...of
const text = 'Hi 😀!';
console.log('使用for循环:');
for (let i = 0; i < text.length; i++) {
  console.log(text[i]);
}

console.log('使用for...of:');
for (const char of text) {
  console.log(char);
}

console.log('使用展开运算符:', [...text]);
console.log('使用Array.from:', Array.from(text));

// normalize()方法
const str1 = '\u00E9'; // "é" (组合形式)
const str2 = 'e\u0301'; // "e" + "´" (分解形式)

console.log('str1 === str2:', str1 === str2);
console.log('str1.normalize() === str2.normalize():', str1.normalize() === str2.normalize());

// 5.5 实际应用场景
// ================

// HTML模板生成
function generateUserCard(user) {
  return `
    <div class="user-card">
      <img src="${user.avatar}" alt="${user.name}" class="avatar">
      <div class="user-info">
        <h3>${user.name}</h3>
        <p>${user.email}</p>
        <p>Member since: ${new Date(user.joinDate).toLocaleDateString()}</p>
        <div class="status ${user.isActive ? 'active' : 'inactive'}">
          ${user.isActive ? 'Active' : 'Inactive'}
        </div>
      </div>
    </div>
  `;
}

const user = {
  name: 'John Doe',
  email: 'john@example.com',
  avatar: 'https://picsum.photos/seed/user123/100/100.jpg',
  joinDate: '2020-01-15',
  isActive: true
};

console.log('HTML模板:');
console.log(generateUserCard(user));

// SQL查询构建
function buildQuery(table, conditions = {}, fields = '*', limit = null) {
  let query = `SELECT ${fields} FROM ${table}`;
  
  if (Object.keys(conditions).length > 0) {
    const whereClause = Object.entries(conditions)
      .map(([key, value]) => `${key} = '${value}'`)
      .join(' AND ');
    query += ` WHERE ${whereClause}`;
  }
  
  if (limit) {
    query += ` LIMIT ${limit}`;
  }
  
  return query;
}

const query1 = buildQuery('users', { status: 'active', age: 25 }, 'id, name, email');
console.log('SQL查询1:', query1);

const query2 = buildQuery('products', {}, '*', 10);
console.log('SQL查询2:', query2);

// 国际化与本地化
const i18n = {
  en: {
    greeting: 'Hello, {name}!',
    farewell: 'Goodbye, {name}!',
    items: '{count} items'
  },
  zh: {
    greeting: '你好，{name}！',
    farewell: '再见，{name}！',
    items: '{count} 件商品'
  }
};

function translate(key, locale = 'en', params = {}) {
  const template = i18n[locale][key] || i18n.en[key] || key;
  
  return template.replace(/{(\w+)}/g, (match, param) => {
    return params[param] !== undefined ? params[param] : match;
  });
}

console.log('英文问候:', translate('greeting', 'en', { name: 'Alice' }));
console.log('中文问候:', translate('greeting', 'zh', { name: 'Alice' }));
console.log('英文商品数:', translate('items', 'en', { count: 5 }));
console.log('中文商品数:', translate('items', 'zh', { count: 5 }));

// 日志记录与调试
function log(level, message, data = {}) {
  const timestamp = new Date().toISOString();
  const dataStr = Object.keys(data).length > 0 
    ? `\nData: ${JSON.stringify(data, null, 2)}` 
    : '';
  
  console.log(`[${timestamp}] [${level.toUpperCase()}] ${message}${dataStr}`);
}

log('info', 'User logged in', { userId: 123, ip: '192.168.1.1' });
log('error', 'Database connection failed', { error: 'Connection timeout', retries: 3 });

// 动态样式生成
function generateCSS(theme) {
  return `
    .button {
      background-color: ${theme.primaryColor};
      color: ${theme.textColor};
      border-radius: ${theme.borderRadius}px;
      padding: ${theme.padding}px;
    }
    
    .button:hover {
      background-color: ${theme.hoverColor};
    }
    
    .card {
      background-color: ${theme.cardBackground};
      border: 1px solid ${theme.borderColor};
      box-shadow: 0 2px 4px rgba(0, 0, 0, ${theme.shadowOpacity});
    }
  `;
}

const darkTheme = {
  primaryColor: '#4a90e2',
  textColor: '#ffffff',
  borderRadius: 4,
  padding: 10,
  hoverColor: '#357abd',
  cardBackground: '#2c3e50',
  borderColor: '#34495e',
  shadowOpacity: 0.3
};

console.log('动态CSS:');
console.log(generateCSS(darkTheme));

// 5.6 实践练习
// =============

// 练习1：模板字符串应用
function generateUserProfile(user) {
  const ageGroup = user.age < 18 ? '年轻用户' : user.age <= 30 ? '青年用户' : '成熟用户';
  const joinDate = new Date(user.joined).toLocaleDateString('zh-CN');
  
  return `
    用户简介
    ========
    姓名: ${user.name}
    年龄: ${user.age}岁 (${ageGroup})
    职业: ${user.occupation}
    爱好: ${user.hobbies.join(', ')}
    加入日期: ${joinDate}
  `;
}

const userProfile = {
  name: 'Alice Johnson',
  age: 28,
  occupation: 'Web Developer',
  hobbies: ['coding', 'reading', 'hiking'],
  joined: '2020-05-15'
};

console.log('用户简介:');
console.log(generateUserProfile(userProfile));

// 练习2：标签模板应用
function currency(strings, ...values) {
  let result = '';
  
  for (let i = 0; i < values.length; i++) {
    // 获取货币代码（假设在最后一个字符串部分）
    const currencyCode = strings[i + 1].trim().split(' ')[0];
    
    // 格式化数字
    const formattedValue = typeof values[i] === 'number' 
      ? values[i].toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })
      : values[i];
    
    // 添加货币符号
    let symbol = '';
    switch (currencyCode) {
      case 'USD': symbol = '$'; break;
      case 'EUR': symbol = '€'; break;
      case 'CNY': symbol = '¥'; break;
      default: symbol = currencyCode + ' ';
    }
    
    result += strings[i] + symbol + formattedValue;
  }
  
  // 添加最后一个字符串部分（去掉货币代码）
  const lastPart = strings[strings.length - 1].replace(/^\s*\w+\s*/, '');
  result += lastPart;
  
  return result;
}

const price1 = currency`Price: ${19.99} USD`;
console.log('货币格式1:', price1);

const euroPrice = currency`Price: ${1234.567} EUR`;
console.log('货币格式2:', euroPrice);

// 练习3：字符串方法应用
function isImageFile(filename) {
  const imageExtensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'];
  const extension = filename.split('.').pop().toLowerCase();
  return imageExtensions.includes(extension);
}

function generateId(id, length = 8) {
  return String(id).padStart(length, '0');
}

function extractDomain(url) {
  try {
    const urlObj = new URL(url);
    return urlObj.hostname;
  } catch (e) {
    // 简单的URL解析（不处理所有情况）
    const match = url.match(/https?:\/\/([^\/]+)/);
    return match ? match[1] : '';
  }
}

console.log('isImageFile("photo.jpg"):', isImageFile('photo.jpg'));
console.log('isImageFile("document.pdf"):', isImageFile('document.pdf'));
console.log('generateId(123, 6):', generateId(123, 6));
console.log('extractDomain("https://www.example.com/path/page"):', extractDomain('https://www.example.com/path/page'));

// 5.7 最佳实践示例
// ==================

// 好的实践：优先使用模板字符串
const goodPractice = `Hello ${name}, you have ${count} new messages.`;

// 好的实践：避免过于复杂的表达式
const result = 10 > 5 ? (100 * 2 / 4).toFixed(2) : 'N/A';
const goodExample = `The result is ${result}`;

// 好的实践：使用includes()代替indexOf()
if (text.includes('world')) {
  console.log('Found "world" in text');
}

// 好的实践：检查文件扩展名
if (filename.endsWith('.jpg') || filename.endsWith('.png')) {
  console.log('This is an image file');
}

// 好的实践：正确处理Unicode字符
for (const char of text) {
  console.log('Character:', char);
}

// 5.8 常见问题解决方案
// ====================

// 问题1：模板字符串中的反引号
const backtickExample = `This contains a backtick: \` here`;

// 问题2：标签模板中的参数处理
function safeSql(strings, ...values) {
  let result = strings[0];
  for (let i = 0; i < values.length; i++) {
    // 转义单引号
    const escaped = String(values[i]).replace(/'/g, "''");
    result += `'${escaped}'${strings[i + 1]}`;
  }
  return result;
}

// 问题3：Unicode字符处理
for (const char of emoji) {
  console.log('Unicode character:', char);
}

// 问题4：浏览器兼容性 - String.prototype.includes polyfill
if (!String.prototype.includes) {
  String.prototype.includes = function(search, start) {
    if (typeof start !== 'number') {
      start = 0;
    }
    
    if (start + search.length > this.length) {
      return false;
    } else {
      return this.indexOf(search, start) !== -1;
    }
  };
}