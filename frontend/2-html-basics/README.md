# 第2章：HTML基础

## 2.1 HTML文档结构

HTML（HyperText Markup Language）是构建网页的基础。在本章中，我们将深入了解HTML的核心概念和用法。

### 2.1.1 基本HTML结构

一个标准的HTML文档具有以下基本结构：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>页面标题</title>
</head>
<body>
    <!-- 页面内容 -->
</body>
</html>
```

让我们逐个解析这些标签的含义：

- **`<!DOCTYPE html>`**：文档类型声明，告诉浏览器这是HTML5文档
- **`<html>`**：HTML文档的根元素，所有其他元素都嵌套在其中
- **`<head>`**：包含文档的元数据，如标题、字符集、视口设置等
- **`<meta charset="UTF-8">`**：指定文档使用的字符编码，UTF-8支持几乎所有语言
- **`<meta name="viewport" content="width=device-width, initial-scale=1.0">`**：设置视口，确保页面在移动设备上正确显示
- **`<title>`**：定义页面的标题，显示在浏览器标签栏
- **`<body>`**：包含网页的可见内容

### 2.1.2 HTML标签语法

HTML标签通常由开始标签、内容和结束标签组成：

```html
<tagname>内容</tagname>
```

有些标签是自闭合的，不需要结束标签：

```html
<tagname />
```

### 2.1.3 HTML属性

标签可以有属性，提供额外信息：

```html
<tagname attribute="value">内容</tagname>
```

例如：

```html
<a href="https://www.example.com">链接文本</a>
```

## 2.2 常用HTML标签

HTML提供了许多标签用于创建不同类型的内容。让我们学习一些最常用的标签。

### 2.2.1 标题标签

HTML提供了6级标题标签，从`<h1>`到`<h6>`：

```html
<h1>这是一级标题（最重要）</h1>
<h2>这是二级标题</h2>
<h3>这是三级标题</h3>
<h4>这是四级标题</h4>
<h5>这是五级标题</h5>
<h6>这是六级标题（最不重要）</h6>
```

标题标签不仅定义了文本的外观，还提供了文档的结构，对SEO（搜索引擎优化）很重要。

### 2.2.2 段落和文本格式化

- **段落标签`<p>`**：定义一个段落
  ```html
  <p>这是一个段落。段落是文本的基本组织单位。</p>
  ```

- **换行标签`<br>`**：在文本中插入换行
  ```html
  <p>这是第一行。<br>这是第二行。</p>
  ```

- **水平线标签`<hr>`**：插入一条水平线
  ```html
  <hr>
  ```

- **文本格式化标签**：
  ```html
  <b>粗体文本</b>
  <i>斜体文本</i>
  <u>下划线文本</u>
  <s>删除线文本</s>
  <strong>重要文本（语义上的粗体）</strong>
  <em>强调文本（语义上的斜体）</em>
  ```

### 2.2.3 列表标签

HTML支持三种类型的列表：

1. **无序列表`<ul>`**：项目前面有圆点标记
   ```html
   <ul>
       <li>项目1</li>
       <li>项目2</li>
       <li>项目3</li>
   </ul>
   ```

2. **有序列表`<ol>`**：项目前面有数字标记
   ```html
   <ol>
       <li>第一步</li>
       <li>第二步</li>
       <li>第三步</li>
   </ol>
   ```

3. **定义列表`<dl>`**：包含术语和定义
   ```html
   <dl>
       <dt>HTML</dt>
       <dd>超文本标记语言，用于创建网页结构。</dd>
       <dt>CSS</dt>
       <dd>层叠样式表，用于设计网页外观。</dd>
   </dl>
   ```

### 2.2.4 链接标签

链接是网页的基本元素，使用`<a>`标签创建：

```html
<a href="https://www.example.com">访问示例网站</a>
```

链接的常用属性：

- **`href`**：链接的目标URL
- **`target`**：指定在何处打开链接
  - `_self`：在当前窗口打开（默认）
  - `_blank`：在新窗口打开
  - `_parent`：在父框架中打开
  - `_top`：在整个窗口中打开

```html
<a href="https://www.example.com" target="_blank">在新窗口中打开示例网站</a>
```

### 2.2.5 图像标签

使用`<img>`标签在网页中插入图像：

```html
<img src="image.jpg" alt="图片描述" width="300" height="200">
```

图像的常用属性：

- **`src`**：图像的URL
- **`alt`**：图像的替代文本，当图像无法显示时显示
- **`width`**：图像宽度
- **`height`**：图像高度

## 2.3 表单与交互元素

表单是网站收集用户输入的主要方式，使用`<form>`标签创建：

### 2.3.1 基本表单结构

```html
<form action="/submit-form" method="post">
    <!-- 表单元素 -->
    <input type="submit" value="提交">
</form>
```

表单的常用属性：

- **`action`**：提交表单数据的URL
- **`method`**：提交数据的HTTP方法（`get`或`post`）

### 2.3.2 常用表单元素

#### 文本输入

```html
<label for="username">用户名：</label>
<input type="text" id="username" name="username" placeholder="请输入用户名">
```

#### 密码输入

```html
<label for="password">密码：</label>
<input type="password" id="password" name="password">
```

#### 单选按钮

```html
<p>性别：</p>
<label>
    <input type="radio" name="gender" value="male" checked> 男
</label>
<label>
    <input type="radio" name="gender" value="female"> 女
</label>
```

#### 复选框

```html
<p>爱好：</p>
<label>
    <input type="checkbox" name="hobbies" value="reading"> 阅读
</label>
<label>
    <input type="checkbox" name="hobbies" value="sports"> 运动
</label>
```

#### 下拉列表

```html
<label for="country">国家：</label>
<select id="country" name="country">
    <option value="cn" selected>中国</option>
    <option value="us">美国</option>
    <option value="jp">日本</option>
</select>
```

#### 多行文本输入

```html
<label for="message">留言：</label>
<textarea id="message" name="message" rows="4" cols="50" placeholder="请输入留言..."></textarea>
```

#### 按钮

```html
<input type="submit" value="提交表单">
<input type="reset" value="重置表单">
<button type="button">普通按钮</button>
```

## 2.4 语义化HTML

语义化HTML是指使用具有明确含义的HTML标签，而不仅仅是使用`<div>`和`<span>`。语义化HTML有助于：

1. 提高代码的可读性和可维护性
2. 改善搜索引擎优化（SEO）
3. 增强网页的可访问性

### 2.4.1 语义化布局标签

HTML5引入了一系列语义化布局标签：

- **`<header>`**：定义文档的页眉
- **`<nav>`**：定义导航链接的部分
- **`<main>`**：定义文档的主要内容
- **`<article>`**：定义独立的内容块（如博客文章）
- **`<section>`**：定义文档中的一个区块
- **`<aside>`**：定义侧边栏或辅助内容
- **`<footer>`**：定义文档的页脚

### 2.4.2 语义化标签示例

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>语义化HTML示例</title>
</head>
<body>
    <header>
        <h1>我的网站</h1>
        <nav>
            <ul>
                <li><a href="#home">首页</a></li>
                <li><a href="#about">关于我们</a></li>
                <li><a href="#contact">联系我们</a></li>
            </ul>
        </nav>
    </header>
    
    <main>
        <section id="home">
            <h2>欢迎来到我的网站</h2>
            <p>这是网站的首页内容。</p>
        </section>
        <section id="about">
            <h2>关于我们</h2>
            <p>这是关于我们的内容。</p>
        </section>
        <section id="contact">
            <h2>联系我们</h2>
            <form>
                <!-- 表单内容 -->
            </form>
        </section>
    </main>
    
    <footer>
        <p>© 2023 我的网站. 保留所有权利。</p>
    </footer>
</body>
</html>
```

## 2.5 HTML5新特性

HTML5引入了许多新特性和标签，使网页开发更加丰富和强大。

### 2.5.1 新的语义化标签

如前面所述，HTML5引入了`<header>`, `<nav>`, `<main>`, `<article>`, `<section>`, `<aside>`, `<footer>`等语义化标签。

### 2.5.2 新的表单控件

HTML5添加了新的表单输入类型：

- `email`：电子邮件地址输入
- `url`：URL输入
- `number`：数字输入
- `range`：滑块控件
- `date`：日期选择器
- `time`：时间选择器
- `color`：颜色选择器

示例：

```html
<input type="email" placeholder="your@email.com">
<input type="date">
<input type="range" min="0" max="100">
```

### 2.5.3 多媒体支持

HTML5原生支持音频和视频：

```html
<audio controls>
    <source src="audio.mp3" type="audio/mpeg">
    您的浏览器不支持音频元素。
</audio>

<video controls width="320" height="240">
    <source src="video.mp4" type="video/mp4">
    您的浏览器不支持视频元素。
</video>
```

### 2.5.4 Canvas绘图

`<canvas>`元素提供了在网页上绘制图形的能力：

```html
<canvas id="myCanvas" width="200" height="100"></canvas>

<script>
    const canvas = document.getElementById('myCanvas');
    const ctx = canvas.getContext('2d');
    ctx.fillStyle = '#FF0000';
    ctx.fillRect(0, 0, 150, 75);
</script>
```

### 2.5.5 本地存储

HTML5引入了本地存储功能：

- `localStorage`：长期存储数据，没有过期时间
- `sessionStorage`：临时存储数据，当会话结束时清除

```html
<script>
    // 使用localStorage存储数据
    localStorage.setItem('username', '张三');
    
    // 从localStorage获取数据
    const username = localStorage.getItem('username');
    console.log(username); // 输出: 张三
    
    // 使用sessionStorage
    sessionStorage.setItem('token', 'abc123');
</script>
```

## 2.6 HTML验证

确保HTML代码的正确性很重要。以下是一些常见的HTML错误和最佳实践：

### 2.6.1 常见错误

1. 缺少结束标签
2. 标签嵌套不正确
3. 属性值没有用引号包围
4. 使用了不推荐的标签

### 2.6.2 HTML验证工具

可以使用在线工具验证HTML代码：

- [W3C HTML Validator](https://validator.w3.org/)
- [HTML5 Validator](https://html5.validator.nu/)

## 2.7 练习题

1. 创建一个包含标题、段落、列表和链接的HTML页面
2. 设计一个简单的联系表单，包含姓名、电子邮件和留言字段
3. 使用HTML5语义化标签创建一个基本的网页布局
4. 尝试使用Canvas绘制一个简单的图形
5. 创建一个包含音频或视频的页面

## 2.8 进一步学习资源

- [MDN HTML指南](https://developer.mozilla.org/zh-CN/docs/Web/HTML)
- [W3Schools HTML教程](https://www.w3schools.com/html/)
- [HTML5 参考手册](https://devdocs.io/html/)

接下来，让我们进入第3章，学习CSS基础！