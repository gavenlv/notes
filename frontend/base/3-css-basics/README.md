# 第3章：CSS基础样式与布局详解

## 3.1 CSS概述与核心概念

### 3.1.1 CSS的定义与作用

CSS（Cascading Style Sheets，层叠样式表）是一种专门用于描述HTML或XML文档呈现方式的样式语言。CSS的诞生解决了网页结构与表现分离的关键问题，使网页开发更加专业化和高效。

**CSS的核心功能**：
- **视觉呈现控制**：定义网页元素的颜色、字体、大小、间距等视觉属性
- **布局管理**：控制网页元素的位置、排列方式和页面整体结构
- **响应式设计**：使网页能够适应不同设备的屏幕尺寸和特性
- **动画与过渡**：为用户界面添加动态效果和交互反馈
- **可访问性优化**：改善文本可读性、对比度和整体用户体验

### 3.1.2 CSS的核心价值

CSS的引入为Web开发带来了革命性的变化，主要体现在以下几个方面：

#### 1. 分离关注点
- **HTML负责内容和结构**：定义网页中的信息和语义关系
- **CSS负责表现和样式**：控制如何展示这些信息
- **JavaScript负责行为和交互**：添加动态功能和用户交互

这种分离使代码更加模块化，便于维护和扩展。

#### 2. 可维护性
- 集中管理样式，一处修改，多处生效
- 减少代码重复，降低维护成本
- 更容易进行设计更新和品牌调整

#### 3. 一致性
- 应用统一的设计语言和视觉风格
- 确保网站在不同页面间的视觉连贯性
- 简化团队协作和设计实施

#### 4. 响应式设计支持
- 使用媒体查询（Media Queries）适应不同屏幕尺寸
- 采用弹性布局和流体网格实现多设备兼容
- 提供最佳的跨设备用户体验

#### 5. 性能优化
- 减少HTML代码冗余，降低文件大小
- 支持CSS文件缓存，提高页面加载速度
- 减少HTTP请求数量，优化网络传输

### 3.1.3 CSS版本演进

CSS从诞生至今经历了多次版本迭代，每次更新都带来了新特性和改进：

1. **CSS 1**（1996年）：最初版本，包含基本的文本格式化和颜色控制
2. **CSS 2**（1998年）：引入盒模型、定位、浮动等高级布局功能
3. **CSS 2.1**（2011年）：CSS 2的修订版，修复了错误并提高了浏览器兼容性
4. **CSS 3**（正在开发中）：模块化更新，包括：
   - **选择器模块**：更强大的元素选择能力
   - **颜色模块**：HSL、HSLA、RGBA等新颜色格式
   - **排版模块**：字体加载、文本阴影等
   - **盒模型模块**：圆角、阴影、边框图像等
   - **布局模块**：Flexbox、Grid、多列布局等
   - **动画模块**：过渡、变换、关键帧动画等
   - **响应式模块**：媒体查询、视口设置等

目前，CSS已经成为前端开发中不可或缺的核心技术之一，与HTML和JavaScript共同构成了现代Web开发的技术基础。

## 3.2 CSS基础语法与使用方法

### 3.2.1 CSS规则的基本结构

CSS的基本构建块是规则集（Rule Set），也称为规则。每个规则由选择器和声明块组成：

```css
选择器 {
    属性名: 属性值;  /* 声明 */
    属性名: 属性值;  /* 声明 */
}
```

- **选择器**：指定要应用样式的HTML元素
- **声明块**：用大括号`{}`包围
- **声明**：由属性名和属性值组成，用冒号`:`连接
- **多个声明**：用分号`;`分隔
- **注释**：使用`/* 注释内容 */`语法

### 3.2.2 详细语法示例与说明

```css
/* 这是一个CSS规则注释 */

p {
    color: blue;           /* 文本颜色为蓝色 */
    font-size: 16px;       /* 字体大小为16像素 */
    line-height: 1.5;      /* 行高为字体大小的1.5倍 */
    margin-bottom: 10px;   /* 底部外边距为10像素 */
    background-color: #f5f5f5; /* 背景颜色 */
    padding: 15px;         /* 内边距 */
    border: 1px solid #ddd; /* 边框 */
    border-radius: 4px;    /* 圆角 */
}
```

**语法要点**：
- 选择器可以是HTML元素名、类名、ID或其他组合
- 属性名是CSS预定义的关键字
- 属性值可以是关键字、长度单位、颜色值等
- 分号在最后一个声明后可以省略，但为了一致性和避免添加新声明时出错，通常保留
- 缩进不是必须的，但良好的缩进可以提高代码可读性

### 3.2.3 CSS中的单位

CSS支持多种单位来指定长度、大小等值：

#### 绝对单位
- **px**（像素）：最常用的绝对单位，在高DPI显示器上可能是多个物理像素
- **pt**（点）：主要用于印刷，1pt = 1/72英寸
- **pc**（皮卡）：1pc = 12pt
- **mm**（毫米）：公制单位
- **cm**（厘米）：公制单位
- **in**（英寸）：英制单位，1in = 2.54cm

#### 相对单位
- **em**：相对于元素的字体大小（font-size）
- **rem**：相对于根元素（html）的字体大小
- **%**：相对于父元素的百分比
- **vh**：视口高度的1%
- **vw**：视口宽度的1%
- **vmin**：视口宽度或高度中较小值的1%
- **vmax**：视口宽度或高度中较大值的1%

**实际应用示例**：
```css
.container {
    width: 100%;           /* 相对于父元素宽度的100% */
    max-width: 1200px;     /* 最大宽度为1200像素 */
    margin: 0 auto;        /* 水平居中 */
}

.text-large {
    font-size: 2rem;       /* 根元素字体大小的2倍 */
    line-height: 1.2;      /* 无单位，表示字体大小的1.2倍 */
}

.header {
    height: 100vh;         /* 视口高度的100% */
    padding: 2rem;         /* 根元素字体大小的2倍 */
}
```
```

## 3.3 在HTML中应用CSS的方式

CSS可以通过三种不同的方式应用到HTML文档中，每种方式都有其适用场景和优缺点。

### 3.3.1 内联样式（Inline Styles）

内联样式是直接在HTML元素上使用`style`属性来定义样式。这种方式将CSS规则直接嵌入到HTML元素中。

#### 语法与示例

```html
<p style="color: red; font-size: 18px; margin-bottom: 10px;">这是一个红色的段落。</p>
```

内联样式中的CSS规则遵循相同的语法，但多个规则之间使用分号分隔，且不需要大括号包围。

#### 应用场景
- **快速测试**：临时调整元素样式进行开发调试
- **动态内容**：通过JavaScript动态设置样式
- **特殊覆盖**：需要覆盖其他样式的特定元素
- **邮件模板**：在HTML邮件中确保样式正确显示

#### 优缺点分析

**优点**：
- **最高优先级**：内联样式的优先级高于其他CSS应用方式
- **即时生效**：直接应用于特定元素，无需额外的选择器匹配
- **独立性**：不依赖于外部文件或内部样式表

**缺点**：
- **违反关注点分离原则**：样式与内容混合
- **维护困难**：需要在每个元素上单独修改样式
- **代码冗余**：相似样式在多个元素上重复定义
- **缺乏复用性**：不能在多个元素间共享样式

**最佳实践**：尽量避免使用内联样式，除非是特殊情况下的临时需求或动态样式设置。

### 3.3.2 内部样式表（Internal Style Sheet）

内部样式表是在HTML文档的`<head>`部分使用`<style>`标签来定义样式规则。这种方式将CSS集中在HTML文档的头部。

#### 语法与示例

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>内部样式表示例</title>
    <style>
        /* 文档级别样式定义 */
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f5f5f5;
            margin: 0;
            padding: 0;
        }
        
        h1 {
            color: #2c3e50;
            text-align: center;
            margin-top: 30px;
            font-size: 2.5rem;
        }
        
        p {
            color: #555;
            font-size: 16px;
            margin-bottom: 20px;
            padding: 0 20px;
        }
        
        .container {
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: white;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>欢迎使用内部样式表</h1>
        <p>这是一个使用内部样式表的示例页面。</p>
        <p>内部样式表适用于单个页面的样式定义。</p>
    </div>
</body>
</html>
```

#### 应用场景
- **单页网站**：不需要在多个页面间共享样式的独立页面
- **原型开发**：快速创建页面原型和设计验证
- **性能优化**：对于高流量页面，可以减少HTTP请求（但会增加HTML文件大小）

#### 优缺点分析

**优点**：
- **集中管理**：样式集中在一个位置，便于维护
- **无额外请求**：不产生额外的CSS文件HTTP请求
- **特定性控制**：可以针对特定页面定制样式

**缺点**：
- **不可复用**：样式不能在多个HTML页面间共享
- **增加HTML大小**：使HTML文件变大，可能影响加载速度
- **违反关注点分离**：样式与HTML仍在同一文件中

**最佳实践**：对于小型单页网站或快速原型开发可以使用内部样式表，但对于多页面网站，建议使用外部样式表。

### 3.3.3 外部样式表（External Style Sheet）

外部样式表是将CSS代码保存在单独的`.css`文件中，然后通过HTML的`<link>`标签引入。这是最推荐的CSS应用方式。

#### 实现步骤

1. **创建CSS文件**：创建一个扩展名为`.css`的文件，如`styles.css`
2. **编写CSS规则**：在CSS文件中编写样式规则
3. **在HTML中引入**：使用`<link>`标签将CSS文件链接到HTML文档

#### 详细示例

**1. CSS文件（styles.css）**：
```css
/* 全局重置 */
* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

/* 基础样式 */
body {
    font-family: 'Arial', sans-serif;
    line-height: 1.6;
    color: #333;
    background-color: #f4f4f4;
}

/* 布局组件 */
.container {
    width: 80%;
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

/* 标题样式 */
header {
    background-color: #2c3e50;
    color: white;
    padding: 20px 0;
    text-align: center;
}

header h1 {
    font-size: 2rem;
    margin-bottom: 10px;
}

/* 内容区域 */
.main-content {
    background-color: white;
    padding: 30px;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    margin-top: 20px;
}

/* 文本样式 */
h2 {
    color: #3498db;
    margin-bottom: 20px;
    padding-bottom: 10px;
    border-bottom: 2px solid #3498db;
}

p {
    margin-bottom: 15px;
    font-size: 16px;
}

/* 响应式设计 */
@media (max-width: 768px) {
    .container {
        width: 95%;
        padding: 10px;
    }
    
    header h1 {
        font-size: 1.5rem;
    }
    
    .main-content {
        padding: 20px;
    }
}
```

**2. HTML文件（index.html）**：
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>外部样式表示例</title>
    <!-- 引入外部CSS文件 -->
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <header>
        <div class="container">
            <h1>欢迎使用外部样式表</h1>
            <p>外部样式表是最推荐的CSS应用方式</p>
        </div>
    </header>
    
    <div class="container">
        <main class="main-content">
            <h2>外部样式表的优势</h2>
            <p>外部样式表允许你将所有的样式定义集中在一个单独的文件中，然后在多个HTML页面中重用这些样式。</p>
            <p>这种方式使得网站的设计更加一致，也更容易维护和更新。</p>
        </main>
    </div>
</body>
</html>
```

#### 应用场景
- **多页面网站**：需要在多个页面间共享样式的网站
- **大型项目**：需要团队协作开发的大型Web项目
- **企业级应用**：需要高度可维护性和可扩展性的应用

#### 优缺点分析

**优点**：
- **完全分离关注点**：HTML专注于内容，CSS专注于样式
- **高度可复用**：一个CSS文件可以被多个HTML页面引用
- **更好的维护性**：样式集中管理，一处修改，多处生效
- **缓存优化**：浏览器可以缓存CSS文件，减少重复下载
- **并行加载**：CSS文件可以与HTML文件并行加载
- **团队协作**：前端开发者可以专注于CSS，后端开发者可以专注于HTML

**缺点**：
- **额外的HTTP请求**：需要额外的请求来加载CSS文件
- **依赖关系**：HTML文件依赖于CSS文件才能正确显示

**最佳实践**：外部样式表是专业Web开发中最推荐的CSS应用方式，几乎适用于所有类型的项目。

### 3.3.4 样式优先级与层叠规则

当一个HTML元素通过多种方式应用了CSS样式，并且这些样式存在冲突时，CSS会根据优先级规则来决定最终应用哪个样式。

#### 优先级顺序（从高到低）

1. **内联样式**：通过元素的`style`属性定义的样式
2. **ID选择器**：使用`#id`选择器定义的样式
3. **类选择器、属性选择器和伪类选择器**：如`.class`、`[attribute]`、`:hover`等
4. **元素选择器和伪元素选择器**：如`p`、`div`、`::before`等
5. **通用选择器**：使用`*`定义的样式
6. **浏览器默认样式**：浏览器内置的默认样式

#### 优先级计算规则

CSS使用一个基于权重的计算系统来确定样式优先级：
- 内联样式：权重为1000
- ID选择器：每个ID选择器权重为100
- 类、属性和伪类选择器：每个选择器权重为10
- 元素和伪元素选择器：每个选择器权重为1

**计算示例**：
```css
/* 权重计算: 100 + 10 + 1 = 111 */
#header .nav-item a {
    color: blue;
}

/* 权重计算: 10 + 10 = 20 */
.nav .nav-item {
    color: red;
}
```

在这个例子中，第一个规则的权重更高，因此链接文本将显示为蓝色。

#### 层叠规则与`!important`

除了优先级，CSS还遵循以下层叠规则：
- 同一优先级的规则，后面定义的会覆盖前面定义的
- 可以使用`!important`标记来提升特定样式的优先级，使其覆盖所有其他样式（即使是内联样式）

**示例**：
```css
/* 即使ID选择器优先级更高，这个规则也会生效 */
.nav-item {
    color: green !important;
}

#header .nav-item {
    color: blue;
}
```

**最佳实践**：尽量避免使用`!important`，它会使样式难以维护。只有在覆盖第三方样式库或处理特殊情况时才考虑使用。

## 3.4 CSS选择器详解

CSS选择器是CSS规则的核心组成部分，它决定了哪些HTML元素会应用特定的样式规则。选择器让开发者能够精确地定位和控制页面上的元素，是实现复杂布局和交互效果的基础。

### 3.4.1 基本选择器

基本选择器是CSS中最常用、最简单的选择器类型，用于直接选择HTML元素。

#### 1. 元素选择器（Type Selector）

元素选择器使用HTML元素的标签名作为选择器，用于选择页面上所有指定类型的元素。

**语法**：
```css
元素名 { 属性: 值; }
```

**示例**：
```css
/* 选择所有段落元素 */
p {
    color: blue;
    font-size: 16px;
    line-height: 1.5;
}

/* 选择所有一级标题元素 */
h1 {
    font-size: 28px;
    font-weight: bold;
    margin-bottom: 20px;
    color: #333;
}

/* 选择所有div元素 */
div {
    display: block;
    margin-bottom: 15px;
}
```

**应用场景**：
- 为特定类型的HTML元素设置全局默认样式
- 重置或覆盖浏览器默认样式
- 为基础HTML标签定义统一的视觉风格

#### 2. 类选择器（Class Selector）

类选择器使用`.`符号后跟类名来选择元素，一个类可以应用到多个元素上，一个元素也可以有多个类。

**语法**：
```css
.类名 { 属性: 值; }
```

**详细示例**：

```css
/* 定义一个主要文本样式类 */
.text-primary {
    color: #3498db;
    font-weight: 500;
}

/* 定义一个辅助文本样式类 */
.text-muted {
    color: #7f8c8d;
    font-size: 14px;
}

/* 定义一个容器样式类 */
.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
}

/* 定义一个卡片样式类 */
.card {
    background-color: white;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    padding: 20px;
    margin-bottom: 20px;
}

/* 定义一个高亮效果类 */
.highlight {
    background-color: #ffffcc;
    padding: 2px 5px;
}
```

**HTML中使用**：
```html
<div class="container">
    <div class="card">
        <h2 class="text-primary">欢迎使用类选择器</h2>
        <p>这是一个<span class="highlight">示例</span>文本。</p>
        <p class="text-muted">这是一些辅助说明文字。</p>
    </div>
</div>
```

**优点与应用场景**：
- **可重用性**：一个类可以应用到多个元素上
- **语义化**：类名可以描述元素的用途或状态
- **组合性**：一个元素可以有多个类，实现样式的组合
- **应用场景**：定义可复用的样式组件，如按钮、卡片、表单控件等

#### 3. ID选择器（ID Selector）

ID选择器使用`#`符号后跟ID名称来选择元素，ID在一个HTML文档中应该是唯一的，每个ID只能应用于一个元素。

**语法**：
```css
#ID名 { 属性: 值; }
```

**详细示例**：

```css
/* 为网站头部定义样式 */
#header {
    background-color: #2c3e50;
    color: white;
    padding: 20px 0;
    position: sticky;
    top: 0;
    z-index: 100;
}

/* 为登录表单定义样式 */
#login-form {
    background-color: #f9f9f9;
    border: 1px solid #ddd;
    border-radius: 5px;
    padding: 25px;
    max-width: 400px;
    margin: 30px auto;
}

/* 为页脚定义样式 */
#footer {
    background-color: #34495e;
    color: white;
    padding: 40px 0;
    margin-top: 50px;
}
```

**HTML中使用**：
```html
<header id="header">
    <div class="container">
        <h1>网站标题</h1>
    </div>
</header>

<div class="container">
    <form id="login-form">
        <!-- 表单内容 -->
    </form>
</div>

<footer id="footer">
    <div class="container">
        <p>版权信息</p>
    </div>
</footer>
```

**优点与应用场景**：
- **唯一性**：选择特定的单个元素
- **高优先级**：ID选择器优先级高于类选择器
- **JavaScript交互**：常用于JavaScript获取特定元素
- **应用场景**：页面上唯一的布局组件，如头部、页脚、主导航等

**注意事项**：每个HTML文档中ID应该唯一，不要在多个元素上使用相同的ID。

#### 4. 通用选择器（Universal Selector）

通用选择器使用`*`符号，用于选择页面上的所有元素，包括HTML、body和所有子元素。

**语法**：
```css
* { 属性: 值; }
```

**详细示例**：

```css
/* 全局盒模型重置 */
* {
    box-sizing: border-box;
}

/* 全局样式重置 */
* {
    margin: 0;
    padding: 0;
}

/* 全局字体设置 */
* {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}
```

**常见组合使用**：

```css
/* 全局重置与基础样式设置 */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    line-height: 1.6;
    color: #333;
    background-color: #f5f5f5;
}
```

**优点与应用场景**：
- **全局设置**：一次性为所有元素设置基础样式
- **样式重置**：清除浏览器默认样式
- **盒模型统一**：确保所有元素使用相同的盒模型计算方式
- **性能考虑**：通用选择器可能会影响性能，应谨慎使用

**最佳实践**：
- 仅在必要时使用通用选择器
- 避免在通用选择器中设置复杂的样式计算
- 通常只用于样式重置和基础设置

### 3.4.2 组合选择器

组合选择器通过组合多个基本选择器，创建更复杂和精确的选择规则。

#### 1. 后代选择器（Descendant Selector）

后代选择器使用空格分隔两个或多个选择器，用于选择第一个选择器匹配元素内的所有后代元素。

**语法**：
```css
选择器1 选择器2 { 属性: 值; }
```

**详细示例**：

```css
/* 选择nav元素内的所有ul元素 */
nav ul {
    list-style: none;
    padding-left: 0;
}

/* 选择nav元素内的所有li元素（无论嵌套多深） */
nav li {
    margin-bottom: 10px;
}

/* 选择nav元素内的所有a元素 */
nav a {
    text-decoration: none;
    color: #333;
    display: block;
    padding: 8px 15px;
    transition: color 0.3s;
}

/* 选择container类内的所有p元素 */
.container p {
    font-size: 14px;
    line-height: 1.5;
    margin-bottom: 15px;
}

/* 选择article元素内的所有h2元素 */
article h2 {
    color: #2c3e50;
    font-size: 24px;
    margin-top: 25px;
    margin-bottom: 15px;
    padding-bottom: 10px;
    border-bottom: 2px solid #3498db;
}
```

**HTML结构示例**：
```html
<nav>
    <ul>
        <li><a href="#">首页</a></li>
        <li><a href="#">关于我们</a></li>
        <li>
            <a href="#">产品</a>
            <ul>
                <li><a href="#">产品1</a></li>
                <li><a href="#">产品2</a></li>
            </ul>
        </li>
    </ul>
</nav>

<div class="container">
    <article>
        <h2>文章标题</h2>
        <p>这是文章的第一段内容。</p>
        <p>这是文章的第二段内容。</p>
    </article>
</div>
```

**特点与应用场景**：
- **层级匹配**：匹配所有后代元素，无论嵌套深度
- **上下文相关**：为特定上下文中的元素应用样式
- **样式隔离**：避免全局样式影响特定区域内的元素
- **应用场景**：为导航、文章内容、评论区等特定区域的元素设置样式

#### 2. 子选择器（Child Selector）

子选择器使用`>`符号分隔两个选择器，用于选择第一个选择器匹配元素的直接子元素。

**语法**：
```css
选择器1 > 选择器2 { 属性: 值; }
```

**详细示例**：

```css
/* 选择nav元素的直接子元素ul */
nav > ul {
    margin-top: 0;
    display: flex;
    justify-content: space-between;
}

/* 选择nav > ul的直接子元素li */
nav > ul > li {
    position: relative;
    margin-right: 20px;
}

/* 选择article元素的直接子元素h2 */
article > h2 {
    color: #e74c3c;
    font-size: 28px;
}

/* 选择ul元素的直接子元素li */
ul > li {
    list-style-type: disc;
    margin-left: 20px;
}

/* 选择父级为.list的ul的直接子元素li */
.list > li {
    list-style-type: square;
}
```

**HTML结构示例**：
```html
<nav>
    <ul> <!-- 这是nav的直接子元素 -->
        <li>首页</li> <!-- 这是ul的直接子元素 -->
        <li>
            产品
            <ul> <!-- 这不是nav的直接子元素 -->
                <li>产品1</li> <!-- 这是内部ul的直接子元素 -->
            </ul>
        </li>
    </ul>
</nav>

<article>
    <h2>文章标题</h2> <!-- 这是article的直接子元素 -->
    <div>
        <h2>副标题</h2> <!-- 这不是article的直接子元素 -->
    </div>
</article>
```

**特点与应用场景**：
- **直接子元素匹配**：只匹配第一层嵌套的子元素
- **精确控制**：比后代选择器更加精确，避免影响深层嵌套元素
- **应用场景**：多级导航菜单、嵌套列表、组件内的直接子元素样式控制

#### 3. 相邻兄弟选择器（Adjacent Sibling Selector）

相邻兄弟选择器使用`+`符号分隔两个选择器，用于选择第一个选择器匹配元素之后的紧邻兄弟元素。

**语法**：
```css
选择器1 + 选择器2 { 属性: 值; }
```

**详细示例**：

```css
/* 选择h2元素之后的第一个p元素 */
h2 + p {
    font-size: 18px;
    font-weight: bold;
    color: #3498db;
    margin-top: 10px;
    margin-bottom: 20px;
    padding-bottom: 10px;
    border-bottom: 1px solid #ddd;
}

/* 选择div元素之后的第一个section元素 */
div + section {
    margin-top: 30px;
    padding-top: 20px;
    border-top: 2px dashed #95a5a6;
}

/* 选择class为error的元素之后的第一个input元素 */
.error + input {
    border-color: #e74c3c;
    background-color: #fdedec;
}

/* 选择label元素之后的第一个input元素 */
label + input {
    margin-left: 10px;
}
```

**HTML结构示例**：
```html
<article>
    <h2>文章标题</h2>
    <p>这是标题后的第一段，会被选中。</p>
    <p>这是第二段，不会被选中。</p>
</article>

<div>内容区域</div>
<section>下一个区域</section> <!-- 这会被选中 -->
<section>再下一个区域</section> <!-- 这不会被选中 -->

<div class="form-group">
    <label for="username">用户名：</label>
    <input type="text" id="username">
    <div class="error">用户名不能为空</div>
    <input type="password" id="password"> <!-- 这会被选中 -->
</div>
```

**特点与应用场景**：
- **紧邻匹配**：只匹配紧随其后的相邻元素
- **顺序相关**：依赖于HTML中的元素顺序
- **应用场景**：表单元素间距控制、内容区块分隔、错误消息后的元素样式等

#### 4. 通用兄弟选择器（General Sibling Selector）

通用兄弟选择器使用`~`符号分隔两个选择器，用于选择第一个选择器匹配元素之后的所有同级元素，无论它们之间是否有其他元素。

**语法**：
```css
选择器1 ~ 选择器2 { 属性: 值; }
```

**详细示例**：

```css
/* 选择h2元素后的所有同级p元素 */
h2 ~ p {
    color: #7f8c8d;
    line-height: 1.6;
    margin-bottom: 15px;
}

/* 选择article元素后的所有同级section元素 */
article ~ section {
    margin-top: 30px;
    padding-top: 20px;
    border-top: 1px solid #ddd;
}

/* 选择被选中的checkbox后的所有label元素 */
input[type="checkbox"]:checked ~ label {
    text-decoration: line-through;
    color: #7f8c8d;
    opacity: 0.7;
}

/* 选择具有error类的元素后的所有同级input元素 */
.error ~ input {
    border-color: #e74c3c;
    background-color: #fdedec;
}
```

**HTML结构示例**：
```html
<article>
    <h2>文章标题</h2>
    <p>这是标题后的第一段，会被选中。</p>
    <div>这是一个中间的div元素。</div>
    <p>这是第二段，也会被选中。</p>
    <p>这是第三段，同样会被选中。</p>
</article>

<section>第一个section，会被选中</section>
<div>中间的div</div>
<section>第二个section，也会被选中</section>

<div class="todo-item">
    <input type="checkbox" id="task1">
    <label for="task1">完成CSS学习</label>
    <div class="error">请标记任务状态</div>
    <input type="text" placeholder="备注信息">
    <input type="date">
</div>
```

**特点与应用场景**：
- **所有后续兄弟**：匹配第一个选择器后所有符合条件的同级元素
- **不要求紧邻**：元素之间可以有其他元素
- **应用场景**：
  - 表单验证后的错误提示样式
  - 待办事项列表中复选框与标签的交互
  - 内容区块之间的分隔和样式控制

### 3.4.3 伪类选择器（Pseudo-classes）

伪类选择器用于选择元素的特定状态、位置或关系，它们以冒号（`:`）开头。伪类让我们能够根据元素的动态状态或文档结构来应用样式，而不仅仅是基于其名称、ID或类。

#### 1. 状态伪类

状态伪类用于选择处于特定状态的元素。

**链接状态伪类**：
```css
/* 未访问的链接 */
a:link {
    color: #3498db;
    text-decoration: none;
}

/* 已访问的链接 */
a:visited {
    color: #9b59b6;
}

/* 鼠标悬停在链接上 */
a:hover {
    color: #e74c3c;
    text-decoration: underline;
    transition: color 0.3s ease;
}

/* 激活的链接（点击时） */
a:active {
    color: #2ecc71;
}

/* 焦点状态（键盘导航时） */
a:focus {
    outline: 2px solid #3498db;
    outline-offset: 2px;
}
```

**表单元素状态伪类**：
```css
/* 获取焦点的元素 */
input:focus,
textarea:focus,
select:focus {
    border-color: #3498db;
    box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
    outline: none;
}

/* 选中的复选框或单选按钮 */
input[type="checkbox"]:checked,
input[type="radio"]:checked {
    accent-color: #3498db;
}

/* 禁用的表单元素 */
input:disabled,
button:disabled {
    background-color: #f5f5f5;
    color: #95a5a6;
    cursor: not-allowed;
    opacity: 0.7;
}

/* 启用的表单元素 */
input:enabled {
    background-color: white;
}

/* 只读的表单元素 */
input:read-only {
    background-color: #f8f9fa;
    border-color: #dee2e6;
}

/* 必填表单元素 */
input:required,
textarea:required {
    border-left: 3px solid #e74c3c;
}

/* 有效/无效的表单元素 */
input:valid {
    border-color: #2ecc71;
}

input:invalid {
    border-color: #e74c3c;
}

/* 占位符显示时（输入框为空且未聚焦） */
input:placeholder-shown {
    background-color: #f8f9fa;
}
```

#### 2. 结构伪类

结构伪类基于元素在文档树中的位置来选择元素。

**基本结构伪类**：
```css
/* 第一个子元素 */
ul li:first-child {
    font-weight: bold;
    color: #2c3e50;
    border-top: 1px solid #ddd;
}

/* 最后一个子元素 */
ul li:last-child {
    margin-bottom: 0;
    border-bottom: none;
}

/* 唯一的子元素 */
ul:only-child {
    background-color: #f8f9fa;
    padding: 20px;
    border-radius: 5px;
}

/* 空元素 */
div:empty {
    display: none;
}
```

**`:nth-child()` 系列伪类**：
```css
/* 第n个子元素（n从1开始） */
ul li:nth-child(3) {
    color: #e74c3c;
    font-weight: bold;
}

/* 偶数子元素 */
ul li:nth-child(even) {
    background-color: #f2f2f2;
}

/* 奇数子元素 */
ul li:nth-child(odd) {
    background-color: #ffffff;
}

/* 每3个元素选择一个（3n, 3n+1, 3n+2） */
ul li:nth-child(3n) {
    border-right: 3px solid #3498db;
}

/* 倒数第n个子元素 */
ul li:nth-last-child(2) {
    margin-bottom: 20px;
    border-bottom: 2px dashed #ddd;
}

/* 第一个特定类型的子元素 */
article p:first-of-type {
    font-size: 18px;
    line-height: 1.6;
    margin-bottom: 20px;
}

/* 最后一个特定类型的子元素 */
article p:last-of-type {
    margin-bottom: 0;
}

/* 第n个特定类型的子元素 */
article p:nth-of-type(2) {
    color: #7f8c8d;
    font-style: italic;
}
```

**否定伪类**：
```css
/* 选择不匹配指定选择器的元素 */
ul li:not(.active) {
    opacity: 0.7;
}

/* 选择不是第一个子元素的元素 */
ul li:not(:first-child) {
    margin-top: 10px;
}

/* 选择不是最后一个子元素的元素 */
ul li:not(:last-child) {
    border-bottom: 1px solid #eee;
}
```

#### 3. 其他常用伪类

```css
/* 根元素（html） */
:root {
    --primary-color: #3498db;
    --secondary-color: #2ecc71;
    --text-color: #333;
    --background-color: #f5f5f5;
}

/* 目标元素（通过URL锚点选择） */
:target {
    background-color: #fffde7;
    padding: 20px;
    border-radius: 5px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

/* 语言伪类 */
p:lang(zh) {
    font-family: 'Noto Sans SC', sans-serif;
}

p:lang(en) {
    font-family: 'Segoe UI', Tahoma, sans-serif;
}

/* 选中的选项（用于下拉列表） */
option:checked {
    background-color: #3498db;
    color: white;
}
```

### 3.4.4 伪元素选择器（Pseudo-elements）

伪元素选择器用于选择元素的特定部分或创建虚拟元素，它们以双冒号（`::`）开头（CSS3标准），但为了兼容旧版本，一些伪元素也支持单冒号语法。

#### 1. 文本相关伪元素

```css
/* 段落的第一行 */
p::first-line {
    font-weight: bold;
    color: #2c3e50;
    font-size: 18px;
    line-height: 1.4;
}

/* 段落的第一个字母 */
p::first-letter {
    font-size: 3em;
    float: left;
    margin-right: 10px;
    margin-bottom: 10px;
    color: #3498db;
    font-family: Georgia, serif;
    line-height: 0.8;
}

/* 选中的文本 */
::selection {
    background-color: #ffeaa7;
    color: #2c3e50;
}

::-moz-selection { /* Firefox 兼容性 */
    background-color: #ffeaa7;
    color: #2c3e50;
}
```

**实际应用示例 - 首字下沉效果**：
```css
.article-intro::first-letter {
    font-size: 4em;
    float: left;
    margin-right: 15px;
    margin-top: -10px;
    margin-bottom: -10px;
    color: #e74c3c;
    font-family: 'Playfair Display', serif;
    font-weight: bold;
    line-height: 0.8;
}
```

#### 2. 内容插入伪元素

`::before` 和 `::after` 伪元素用于在元素内容的前后插入内容，这些内容不会出现在HTML结构中，但会在渲染时显示。

```css
/* 在h1元素内容前插入内容 */
h1::before {
    content: "★ ";
    color: #f39c12;
    font-size: 1.2em;
}

/* 在h1元素内容后插入内容 */
h1::after {
    content: " ★";
    color: #f39c12;
    font-size: 1.2em;
}

/* 为链接添加外部链接图标 */
a[target="_blank"]::after {
    content: " ↗";
    font-size: 0.8em;
    color: #7f8c8d;
}

/* 为列表项添加自定义标记 */
.custom-list li::before {
    content: "• ";
    color: #3498db;
    font-size: 1.2em;
    font-weight: bold;
    margin-right: 5px;
}

/* 清除浮动 */
.clearfix::after {
    content: "";
    display: table;
    clear: both;
}

/* 创建带三角形的提示框 */
.tooltip {
    position: relative;
    display: inline-block;
    cursor: help;
    border-bottom: 1px dashed #3498db;
}

.tooltip::after {
    content: attr(data-tooltip);
    position: absolute;
    bottom: 125%;
    left: 50%;
    transform: translateX(-50%);
    background-color: #2c3e50;
    color: white;
    padding: 8px 12px;
    border-radius: 4px;
    white-space: nowrap;
    opacity: 0;
    visibility: hidden;
    transition: opacity 0.3s, visibility 0.3s;
    z-index: 1000;
}

.tooltip::before {
    content: "";
    position: absolute;
    bottom: 115%;
    left: 50%;
    transform: translateX(-50%);
    border-left: 8px solid transparent;
    border-right: 8px solid transparent;
    border-top: 8px solid #2c3e50;
    opacity: 0;
    visibility: hidden;
    transition: opacity 0.3s, visibility 0.3s;
}

.tooltip:hover::after,
.tooltip:hover::before {
    opacity: 1;
    visibility: visible;
}
```

**HTML示例**：
```html
<h1>装饰的标题</h1>
<a href="https://example.com" target="_blank">外部链接</a>

<ul class="custom-list">
    <li>第一项</li>
    <li>第二项</li>
</ul>

<span class="tooltip" data-tooltip="这是提示文本">悬停查看提示</span>
```

#### 3. 表单相关伪元素

```css
/* 自定义复选框 */
input[type="checkbox"] {
    appearance: none;
    width: 20px;
    height: 20px;
    border: 2px solid #3498db;
    border-radius: 4px;
    cursor: pointer;
    position: relative;
}

input[type="checkbox"]:checked::after {
    content: "✓";
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    color: white;
    font-size: 14px;
    font-weight: bold;
}

input[type="checkbox"]:checked {
    background-color: #3498db;
}

/* 自定义单选按钮 */
input[type="radio"] {
    appearance: none;
    width: 20px;
    height: 20px;
    border: 2px solid #3498db;
    border-radius: 50%;
    cursor: pointer;
    position: relative;
}

input[type="radio"]:checked::after {
    content: "";
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background-color: #3498db;
}

/* 自定义滚动条（WebKit浏览器） */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}

::-webkit-scrollbar-track {
    background: #f1f1f1;
    border-radius: 4px;
}

::-webkit-scrollbar-thumb {
    background: #888;
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: #555;
}```

## CSS优先级

当多个CSS规则应用于同一个元素时，浏览器需要确定使用哪个规则。这取决于CSS的优先级（specificity）规则。

### 优先级顺序（从高到低）

1. **内联样式** - 使用元素的`style`属性
2. **ID选择器** - 以`#`开头
3. **类选择器、伪类选择器和属性选择器** - 如`.class`, `:hover`, `[type="text"]`
4. **元素选择器和伪元素选择器** - 如`p`, `::before`
5. **通用选择器** - `*`

### 计算优先级

可以使用一个四位数（a,b,c,d）来表示优先级：
- `a`：内联样式（1或0）
- `b`：ID选择器的数量
- `c`：类选择器、伪类选择器和属性选择器的数量
- `d`：元素选择器和伪元素选择器的数量

**示例**：
- `p` - 优先级：0,0,0,1
- `.container` - 优先级：0,0,1,0
- `#header` - 优先级：0,1,0,0
- `div.container` - 优先级：0,0,1,1
- `nav ul li.active` - 优先级：0,0,1,3
- `#content .article h2` - 优先级：0,1,1,1
- `style=""` - 优先级：1,0,0,0

### `!important` 标记

在声明后添加`!important`可以覆盖任何其他声明，无论其优先级如何。

```css
p { color: blue !important; }
/* 这个规则将覆盖其他所有p元素的color设置 */
```

**注意**：过度使用`!important`会使CSS难以维护，应尽量避免。优先通过优化选择器来提高优先级。

## CSS盒子模型

CSS盒模型是CSS布局的基础，它描述了元素如何在页面上显示和占用空间。

### 盒模型的组成部分

每个HTML元素都可以看作一个盒子，由以下四个部分组成：

1. **内容区（Content）** - 实际内容的区域，由`width`和`height`属性定义
2. **内边距（Padding）** - 内容与边框之间的空间，由`padding`属性定义
3. **边框（Border）** - 围绕内边距和内容的边界，由`border`属性定义
4. **外边距（Margin）** - 元素与其他元素之间的空间，由`margin`属性定义

```
                  +----------------------------+
                  |          margin           |
                  |  +----------------------+ |
                  |  |        border        | |
                  |  |  +----------------+ | |
                  |  |  |    padding     | | |
                  |  |  |  +----------+  | | |
                  |  |  |  |  content |  | | |
                  |  |  |  +----------+  | | |
                  |  |  +----------------+ | |
                  |  +----------------------+ |
                  +----------------------------+
```

### 标准盒模型 vs IE盒模型

CSS有两种盒模型：标准盒模型（W3C盒模型）和IE盒模型（替代盒模型）。

#### 标准盒模型（默认）

在标准盒模型中，`width`和`height`仅定义内容区域的尺寸，不包括内边距和边框。

```css
.element {
    width: 200px;      /* 内容区宽度 */
    padding: 20px;     /* 内边距 */
    border: 1px solid #000; /* 边框 */
    /* 元素实际占用的宽度 = 200px + 20px*2 + 1px*2 = 242px */
}
```

#### IE盒模型

在IE盒模型中，`width`和`height`包括内容区、内边距和边框。

```css
.element {
    box-sizing: border-box;
    width: 200px;      /* 包括内容区、内边距和边框的总宽度 */
    padding: 20px;     /* 内边距 */
    border: 1px solid #000; /* 边框 */
    /* 内容区宽度 = 200px - 20px*2 - 1px*2 = 158px */
}
```

### 盒模型的实际应用

在现代网页设计中，通常会将所有元素的`box-sizing`设置为`border-box`，这样更容易控制元素的实际宽度。

```css
* {
    box-sizing: border-box;
}
```

## CSS颜色

CSS提供了多种指定颜色的方法：

### 1. 颜色名称

使用预定义的颜色名称。CSS支持140多种标准颜色名称。

```css
element {
    color: red;
    background-color: blue;
    border-color: green;
}
```

### 2. 十六进制颜色值

使用六位十六进制值表示颜色，以`#`开头。前两位表示红色，中间两位表示绿色，最后两位表示蓝色。

```css
element {
    color: #ff0000;     /* 红色 */
    background-color: #00ff00; /* 绿色 */
    border-color: #0000ff;    /* 蓝色 */
}
```

也可以使用三位简化形式（每位重复）：

```css
element {
    color: #f00;     /* 等同于 #ff0000，红色 */
    background-color: #0f0; /* 等同于 #00ff00，绿色 */
    border-color: #00f;    /* 等同于 #0000ff，蓝色 */
}
```

### 3. RGB颜色值

使用`rgb()`函数表示红色、绿色和蓝色的组合。每个参数范围为0-255。

```css
element {
    color: rgb(255, 0, 0);     /* 红色 */
    background-color: rgb(0, 255, 0); /* 绿色 */
    border-color: rgb(0, 0, 255);    /* 蓝色 */
}
```

### 4. RGBA颜色值

`rgba()`函数在RGB的基础上增加了透明度参数（alpha通道），范围为0-1。0表示完全透明，1表示完全不透明。

```css
element {
    color: rgba(0, 0, 0, 1);       /* 不透明的黑色 */
    background-color: rgba(255, 0, 0, 0.5); /* 半透明的红色 */
    border-color: rgba(0, 0, 255, 0.3);    /* 30%不透明的蓝色 */
}
```

### 5. HSL颜色值

`hsl()`函数使用色相（Hue）、饱和度（Saturation）和亮度（Lightness）来定义颜色。
- 色相：0-360度的色环（0=红色，120=绿色，240=蓝色）
- 饱和度：0-100%（0%为灰色，100%为纯色）
- 亮度：0-100%（0%为黑色，50%为正常，100%为白色）

```css
element {
    color: hsl(0, 100%, 50%);     /* 红色 */
    background-color: hsl(120, 100%, 50%); /* 绿色 */
    border-color: hsl(240, 100%, 50%);    /* 蓝色 */
}
```

### 6. HSLA颜色值

`hsla()`函数在HSL的基础上增加了透明度参数。

```css
element {
    color: hsla(0, 100%, 50%, 0.7);    /* 70%不透明的红色 */
    background-color: hsla(120, 100%, 50%, 0.5); /* 半透明的绿色 */
}
```

## CSS字体和文本样式

### 字体属性

```css
p {
    /* 字体系列 */
    font-family: "Microsoft YaHei", "PingFang SC", Arial, sans-serif;
    /* 字体大小 */
    font-size: 16px;     /* 像素单位 */
    font-size: 1rem;     /* 相对根元素的字体大小 */
    font-size: 1em;      /* 相对父元素的字体大小 */
    font-size: 100%;     /* 相对父元素的字体大小 */
    
    /* 字体粗细 */
    font-weight: normal; /* 正常 */
    font-weight: bold;   /* 粗体 */
    font-weight: 300;    /* 细体 */
    font-weight: 400;    /* 正常 */
    font-weight: 600;    /* 半粗体 */
    font-weight: 700;    /* 粗体 */
    
    /* 字体样式 */
    font-style: normal;  /* 正常 */
    font-style: italic;  /* 斜体 */
    font-style: oblique; /* 倾斜 */
    
    /* 行高 */
    line-height: 1.5;    /* 无单位值（推荐），行高为字体大小的1.5倍 */
    line-height: 24px;   /* 固定像素值 */
    
    /* 简写形式 */
    font: italic bold 16px/1.5 "Microsoft YaHei", sans-serif;
}
```

### 文本属性

```css
p {
    /* 文本颜色 */
    color: #333;
    
    /* 文本对齐 */
    text-align: left;    /* 左对齐 */
    text-align: center;  /* 居中对齐 */
    text-align: right;   /* 右对齐 */
    text-align: justify; /* 两端对齐 */
    
    /* 文本装饰 */
    text-decoration: none;      /* 无装饰 */
    text-decoration: underline; /* 下划线 */
    text-decoration: overline;  /* 上划线 */
    text-decoration: line-through; /* 删除线 */
    text-decoration: underline dotted red; /* 组合值 */
    
    /* 文本转换 */
    text-transform: none;    /* 无转换 */
    text-transform: uppercase; /* 大写 */
    text-transform: lowercase; /* 小写 */
    text-transform: capitalize; /* 首字母大写 */
    
    /* 文本缩进 */
    text-indent: 2em;     /* 首行缩进2个字符 */
    
    /* 字间距 */
    letter-spacing: 1px;  /* 字符间距 */
    word-spacing: 5px;    /* 单词间距 */
    
    /* 空白处理 */
    white-space: normal;    /* 正常 */
    white-space: nowrap;    /* 不换行 */
    white-space: pre;       /* 保留空白 */
    white-space: pre-wrap;  /* 保留空白并换行 */
    
    /* 文本阴影 */
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5); /* 水平偏移、垂直偏移、模糊半径、颜色 */
}
```

## CSS布局技术

### 1. 正常文档流（Normal Flow）

默认情况下，HTML元素按照其在代码中出现的顺序从上到下、从左到右排列。块级元素（如div, p, h1-h6）占据整行，而行内元素（如span, a）只占据其内容所需的空间。

### 2. 浮动（Float）

浮动使元素脱离正常文档流，并允许其他元素围绕它排列。常用于创建多列布局。

```css
.float-left {
    float: left;
    margin-right: 20px;
}

.float-right {
    float: right;
    margin-left: 20px;
}

.clearfix::after {
    content: "";
    display: table;
    clear: both;
}
```

### 3. 定位（Positioning）

定位允许精确控制元素在页面上的位置。

#### 相对定位（Relative Positioning）

元素相对于其正常位置移动，但其原位置仍然保留。

```css
.relative {
    position: relative;
    top: 10px;
    left: 20px;
}
```

#### 绝对定位（Absolute Positioning）

元素相对于最近的定位祖先元素（position不是static的元素）定位。如果没有这样的祖先，则相对于视口定位。元素完全脱离文档流。

```css
.absolute {
    position: absolute;
    top: 50px;
    right: 30px;
}
```

#### 固定定位（Fixed Positioning）

元素相对于浏览器视口定位，即使页面滚动也保持在同一位置。

```css
.fixed {
    position: fixed;
    bottom: 20px;
    right: 20px;
}
```

#### 粘性定位（Sticky Positioning）

元素在滚动到特定位置时固定，其他时候表现为相对定位。

```css
.sticky {
    position: sticky;
    top: 0;
}
```

## CSS背景样式

```css
element {
    /* 背景颜色 */
    background-color: #f5f5f5;
    
    /* 背景图片 */
    background-image: url("image.jpg");
    
    /* 背景重复 */
    background-repeat: repeat;     /* 默认，水平和垂直重复 */
    background-repeat: repeat-x;   /* 仅水平重复 */
    background-repeat: repeat-y;   /* 仅垂直重复 */
    background-repeat: no-repeat;  /* 不重复 */
    
    /* 背景位置 */
    background-position: top left; /* 默认 */
    background-position: center;   /* 居中 */
    background-position: 50% 50%;  /* 居中（百分比） */
    background-position: 20px 30px; /* 偏移（像素） */
    
    /* 背景大小 */
    background-size: auto;         /* 默认，保持原始大小 */
    background-size: cover;        /* 覆盖整个元素，可能会裁剪 */
    background-size: contain;      /* 完全包含在元素内，可能有空白 */
    background-size: 50% 50%;      /* 宽高各为元素的50% */
    background-size: 200px 150px;  /* 固定宽高 */
    
    /* 背景附件 */
    background-attachment: scroll; /* 默认，随页面滚动 */
    background-attachment: fixed;  /* 固定，不随页面滚动 */
    background-attachment: local;  /* 随元素内容滚动 */
    
    /* 背景原点 */
    background-origin: padding-box; /* 默认，从内边距开始 */
    background-origin: border-box; /* 从边框开始 */
    background-origin: content-box; /* 从内容区域开始 */
    
    /* 背景裁剪 */
    background-clip: border-box;   /* 默认，裁剪到边框 */
    background-clip: padding-box;  /* 裁剪到内边距 */
    background-clip: content-box;  /* 裁剪到内容区域 */
    
    /* 多重背景 */
    background-image: url("image1.jpg"), url("image2.jpg");
    background-position: left top, right bottom;
    background-repeat: no-repeat, no-repeat;
    
    /* 简写形式 */
    background: #f5f5f5 url("image.jpg") no-repeat center/cover fixed;
}
```

## CSS边框样式

```css
element {
    /* 边框宽度 */
    border-width: 2px;
    border-width: thin;  /* 细边框 */
    border-width: medium; /* 中等边框 */
    border-width: thick; /* 粗边框 */
    border-width: 2px 4px 6px 8px; /* 上、右、下、左边框宽度 */
    
    /* 边框样式 */
    border-style: none;    /* 无边框 */
    border-style: solid;   /* 实线 */
    border-style: dashed;  /* 虚线 */
    border-style: dotted;  /* 点线 */
    border-style: double;  /* 双线 */
    border-style: groove;  /* 凹槽 */
    border-style: ridge;   /* 凸脊 */
    border-style: inset;   /* 内嵌 */
    border-style: outset;  /* 外凸 */
    border-style: solid dashed dotted double; /* 上、右、下、左边框样式 */
    
    /* 边框颜色 */
    border-color: #333;
    border-color: #f00 #0f0 #00f #ff0; /* 上、右、下、左边框颜色 */
    
    /* 边框圆角 */
    border-radius: 5px;
    border-radius: 10px 20px; /* 左上/右下、右上/左下 */
    border-radius: 10px 20px 30px 40px; /* 左上、右上、右下、左下 */
    border-radius: 50%; /* 圆形 */
    border-radius: 10px 50%; /* 左上/右下圆角、右上/左下圆形 */
    
    /* 简写形式 */
    border: 2px solid #333;
    border-top: 2px solid #f00;
    border-right: 4px dashed #0f0;
    border-bottom: 6px dotted #00f;
    border-left: 8px double #ff0;
    
    /* 边框阴影 */
    box-shadow: 3px 3px 5px rgba(0, 0, 0, 0.2); /* 水平偏移、垂直偏移、模糊半径、颜色 */
    box-shadow: 3px 3px 5px 2px rgba(0, 0, 0, 0.2); /* 增加扩展半径 */
    box-shadow: inset 3px 3px 5px rgba(0, 0, 0, 0.2); /* 内阴影 */
}
```

## CSS列表样式

```css
ul, ol {
    /* 列表项标记样式 */
    list-style-type: disc;      /* 默认，实心圆点（ul） */
    list-style-type: circle;    /* 空心圆点 */
    list-style-type: square;    /* 实心方块 */
    list-style-type: decimal;   /* 数字（ol） */
    list-style-type: decimal-leading-zero; /* 带前导零的数字 */
    list-style-type: lower-alpha; /* 小写字母 */
    list-style-type: upper-alpha; /* 大写字母 */
    list-style-type: lower-roman; /* 小写罗马数字 */
    list-style-type: upper-roman; /* 大写罗马数字 */
    list-style-type: none;      /* 无标记 */
    
    /* 列表项标记位置 */
    list-style-position: inside; /* 标记在列表项内容内 */
    list-style-position: outside; /* 标记在列表项内容外（默认） */
    
    /* 自定义标记图像 */
    list-style-image: url("bullet.png");
    
    /* 简写形式 */
    list-style: none inside none;
}

/* 自定义列表样式示例 */
ul.custom-bullets {
    list-style: none;
    padding: 0;
}

ul.custom-bullets li {
    padding-left: 25px;
    position: relative;
    margin-bottom: 10px;
}

ul.custom-bullets li::before {
    content: "★";
    color: #3498db;
    position: absolute;
    left: 0;
}
```

## CSS表格样式

```css
table {
    /* 表格布局算法 */
    table-layout: auto; /* 默认，列宽基于内容 */
    table-layout: fixed; /* 列宽基于表格宽度和列宽设置 */
    
    /* 边框合并 */
    border-collapse: separate; /* 默认，边框分开 */
    border-collapse: collapse; /* 边框合并 */
    
    /* 边框间距 */
    border-spacing: 2px; /* 边框之间的间距 */
    
    /* 宽度和高度 */
    width: 100%;
    
    /* 背景 */
    background-color: white;
}

th, td {
    /* 边框 */
    border: 1px solid #ddd;
    
    /* 内边距 */
    padding: 12px;
    
    /* 文本对齐 */
    text-align: left;
    
    /* 垂直对齐 */
    vertical-align: top;
    vertical-align: middle;
    vertical-align: bottom;
}

th {
    /* 表头样式 */
    background-color: #f2f2f2;
    font-weight: bold;
}

/* 斑马条纹表格 */
tr:nth-child(even) {
    background-color: #f9f9f9;
}

/* 悬停效果 */
tr:hover {
    background-color: #f5f5f5;
}
```

## 3.6 CSS优先级与特殊性

CSS优先级决定了当多个样式规则应用于同一个元素时，哪个规则会最终生效。这是CSS中一个至关重要的概念，直接影响样式的最终渲染结果。

### 3.6.1 优先级基础概念

CSS优先级是一个计算系统，用于决定当多个样式规则目标指向同一元素时，哪个规则会被浏览器采用。理解优先级有助于解决样式冲突问题，确保网页按照预期样式显示。

**优先级的核心原则**：
- 更具体的选择器优先级更高
- 优先级遵循明确的层级关系
- 优先级可以通过一定方法进行计算和比较
- 存在能够覆盖标准优先级的特殊标记

### 3.6.2 优先级顺序详解

从高到低的优先级顺序：

1. **内联样式** - 在HTML元素中使用`style`属性定义的样式
   ```html
   <p style="color: blue;">这段文字的颜色是蓝色</p>
   ```
   内联样式的优先级最高，会覆盖几乎所有其他样式规则。

2. **ID选择器** - 使用`#id`选择器定义的样式
   ```css
   #header { background-color: #f8f9fa; }
   ```
   ID选择器在非内联样式中具有最高优先级。

3. **类选择器、属性选择器和伪类选择器**
   - 类选择器：`.btn`, `.card`
   - 属性选择器：`[type="text"]`, `[href^="https"]`
   - 伪类选择器：`:hover`, `:nth-child(2)`, `:focus`

4. **类型选择器和伪元素选择器**
   - 类型选择器：`div`, `p`, `h1`
   - 伪元素选择器：`::before`, `::after`, `::first-line`

5. **通用选择器** - 使用`*`定义的样式
   ```css
   * { box-sizing: border-box; }
   ```
   通用选择器优先级最低，会被任何其他选择器覆盖。

### 3.6.3 优先级计算方法

优先级可以通过一个四元组 (a, b, c, d) 来表示，其中：

- **a** - 内联样式（最高优先级，通常为0或1）
- **b** - ID选择器数量
- **c** - 类选择器、属性选择器、伪类选择器数量
- **d** - 类型选择器、伪元素选择器数量

**计算示例**：

```css
/* 示例1: (0, 1, 0, 1) */
#header h1 { ... }
/* 1个ID选择器(#header) + 1个类型选择器(h1) */

/* 示例2: (0, 0, 3, 0) */
.btn.primary[disabled]:hover { ... }
/* 2个类选择器(.btn, .primary) + 1个属性选择器([disabled]) + 1个伪类选择器(:hover) */

/* 示例3: (0, 0, 1, 2) */
.nav > li a { ... }
/* 1个类选择器(.nav) + 2个类型选择器(li, a) + 1个组合选择器(>) */
/* 注意：组合选择器(>, +, ~, 空格)不影响优先级计算 */
```

**比较规则**：
1. 从左到右依次比较(a, b, c, d)四个值
2. 如果在某个位置的值不同，则值较大的优先级更高
3. 如果四个值都相同，则后定义的规则优先级更高（层叠顺序）

**优先级计算练习**：

| 选择器 | 优先级 (a,b,c,d) | 优先级解释 |
|-------|----------------|-----------|
| `p` | (0,0,0,1) | 1个类型选择器 |
| `.text` | (0,0,1,0) | 1个类选择器 |
| `#main` | (0,1,0,0) | 1个ID选择器 |
| `p.text` | (0,0,1,1) | 1个类选择器 + 1个类型选择器 |
| `.sidebar p.text` | (0,0,2,1) | 2个类选择器 + 1个类型选择器 |
| `#sidebar p.text` | (0,1,1,1) | 1个ID选择器 + 1个类选择器 + 1个类型选择器 |
| `p:hover` | (0,0,1,1) | 1个伪类选择器 + 1个类型选择器 |
| `div p::first-line` | (0,0,0,2) | 2个类型选择器 + 1个伪元素选择器 |
| `div[class]` | (0,0,1,1) | 1个属性选择器 + 1个类型选择器 |
| `<p style="...">` | (1,0,0,0) | 内联样式 |

### 3.6.4 !important标记

使用`!important`标记可以覆盖任何其他样式规则，使该规则具有极高的优先级。只有另一个同样使用了`!important`并且优先级更高的规则才能覆盖它。

```css
/* 常规规则 */
.error-message { color: red; }

/* 带有!important的规则 */
.critical { color: orange !important; }
```

**优先级的最高层级顺序**：
1. 内联样式 + !important
2. ID选择器 + !important
3. 类/属性/伪类选择器 + !important
4. 类型/伪元素选择器 + !important
5. 内联样式（无!important）
6. ID选择器（无!important）
7. 类/属性/伪类选择器（无!important）
8. 类型/伪元素选择器（无!important）

**`!important`的实际应用场景**：

```css
/* 示例1: 覆盖第三方库样式 */
.my-custom-styles .bootstrap-button {
    background-color: #3498db !important;
    /* 覆盖Bootstrap默认按钮颜色 */
}

/* 示例2: 错误消息强制显示红色 */
.error {
    color: #e74c3c !important;
    /* 确保错误消息始终为红色 */
}

/* 示例3: 无障碍支持 - 高对比度模式 */
@media (prefers-contrast: high) {
    :root {
        --text-color: black !important;
        --background-color: white !important;
    }
}
```

### 3.6.5 优先级实战示例

**示例1: 基本优先级比较**

HTML:
```html
<div id="container">
    <p class="text">这段文字的颜色是什么？</p>
</div>
```

CSS:
```css
/* 规则1: (0,0,0,1) */
p { color: blue; }

/* 规则2: (0,0,1,0) */
.text { color: green; }

/* 规则3: (0,1,0,1) */
#container p { color: red; }
```

**结果**：文字显示为红色，因为规则3的优先级最高(0,1,0,1) > 规则2(0,0,1,0) > 规则1(0,0,0,1)。

**示例2: 内联样式与!important**

HTML:
```html
<div class="box" style="background-color: blue;">带内联样式的盒子</div>
```

CSS:
```css
/* 规则1: (0,0,1,0) */
.box { background-color: green; }

/* 规则2: (0,0,1,0) + !important */
.box { background-color: red !important; }
```

**结果**：盒子背景为红色，因为规则2使用了`!important`，虽然内联样式通常优先级高于类选择器，但`!important`标记提高了规则2的优先级。

**示例3: 复杂选择器优先级**

HTML:
```html
<ul class="nav">
    <li class="item active"><a href="#">首页</a></li>
    <li class="item"><a href="#">产品</a></li>
</ul>
```

CSS:
```css
/* 规则1: (0,0,1,1) */
.nav a { color: #333; }

/* 规则2: (0,0,2,0) */
.item.active { color: #e74c3c; }

/* 规则3: (0,0,3,0) */
.nav .item.active { color: #3498db; }

/* 规则4: (0,0,2,1) */
.item.active a { color: #2ecc71; }
```

**结果**：首页链接显示为绿色(#2ecc71)，因为规则4直接作用于a元素且优先级为(0,0,2,1) > 规则3(0,0,3,0)（虽然规则3的c值更大，但它不直接作用于a元素）。

### 3.6.6 优先级最佳实践

1. **避免过度使用ID选择器**
   - ID选择器优先级高，难以覆盖，会导致样式复用困难
   - 优先使用类选择器，可以更好地组织和复用样式

2. **谨慎使用!important**
   - 只有在必要时使用，如覆盖第三方库样式
   - 过度使用会导致样式难以维护和调试
   - 更好的做法是通过优化选择器的特异性来解决优先级问题

3. **遵循选择器简洁原则**
   - 使用最简洁的选择器达到目的
   - 避免嵌套过深的选择器，如`.header .nav .list .item a`
   - 推荐使用语义化类名，如`.nav-link`代替`.nav a`

4. **利用CSS变量（自定义属性）**
   - CSS变量可以在不改变选择器优先级的情况下动态修改样式
   - 更容易维护和覆盖，减少对`!important`的依赖

5. **使用CSS预处理工具**
   - SCSS、Less等预处理工具可以帮助更好地组织样式，避免选择器过于复杂
   - 提供变量、混合等功能，减少优先级问题

6. **样式隔离策略**
   - 考虑使用BEM（Block Element Modifier）命名规范
   - 使用CSS Modules或CSS-in-JS技术实现样式隔离
   - 这些方法可以有效减少样式冲突和优先级问题

7. **编写清晰的样式文档**
   - 记录重要样式的优先级关系
   - 为团队制定样式规范，包括选择器使用指南

## 3.7 CSS继承机制

CSS继承是指子元素自动应用父元素的某些样式属性值的过程。理解CSS继承机制对于编写简洁高效的样式代码至关重要。

### 3.7.1 继承的基本概念

CSS继承允许我们在较高级别的元素上定义样式，然后这些样式会自动应用到其所有子元素上，除非子元素明确覆盖了这些样式。这种机制大大减少了重复代码，使样式表更加简洁高效。

**继承的工作原理**：
- 当浏览器解析样式时，会首先查看元素是否有直接应用的样式
- 如果没有直接样式，则检查该属性是否可继承
- 如果属性可继承，则使用最近的父元素的该属性值
- 如果属性不可继承或没有找到可继承的值，则使用浏览器的默认样式

### 3.7.2 可继承与不可继承属性

#### 常见的可继承属性

以下是一些通常会从父元素继承到子元素的CSS属性：

**字体相关属性**：
- `font-family` - 字体系列
- `font-size` - 字体大小
- `font-weight` - 字体粗细
- `font-style` - 字体样式（正常、斜体等）
- `font-variant` - 字体变体（小型大写字母等）
- `font-stretch` - 字体拉伸
- `line-height` - 行高

**文本相关属性**：
- `color` - 文本颜色
- `text-align` - 文本对齐方式
- `text-indent` - 文本缩进
- `text-transform` - 文本转换（大写、小写等）
- `letter-spacing` - 字母间距
- `word-spacing` - 单词间距
- `white-space` - 空白处理方式
- `text-shadow` - 文本阴影

**列表相关属性**：
- `list-style-type` - 列表项标记类型
- `list-style-position` - 列表项标记位置
- `list-style-image` - 自定义列表项标记图像

**其他可继承属性**：
- `visibility` - 可见性
- `cursor` - 鼠标指针样式
- `quotes` - 引号样式
- `direction` - 文本方向
- `lang` - 语言设置

#### 通常不会继承的属性

以下是一些通常不会从父元素继承到子元素的CSS属性：

**盒子模型属性**：
- `width`, `height` - 宽度和高度
- `margin` - 外边距
- `padding` - 内边距
- `border` - 边框相关属性
- `box-sizing` - 盒模型计算方式

**定位和布局属性**：
- `position` - 定位类型（static, relative, absolute等）
- `top`, `right`, `bottom`, `left` - 定位偏移
- `z-index` - 层叠顺序
- `display` - 显示类型
- `float`, `clear` - 浮动相关
- `flex`, `grid` - 弹性布局和网格布局相关属性
- `overflow` - 溢出处理

**背景和边框属性**：
- `background-color` - 背景颜色
- `background-image` - 背景图像
- `background-position` - 背景位置
- `background-size` - 背景大小
- `background-repeat` - 背景重复方式
- `border-radius` - 边框圆角
- `box-shadow` - 盒子阴影

**其他不可继承属性**：
- `opacity` - 透明度
- `transform` - 变换
- `transition` - 过渡
- `animation` - 动画
- `outline` - 轮廓线
- `filter` - 滤镜效果

### 3.7.3 继承控制关键字

CSS提供了几个关键字来显式控制属性的继承行为：

**`inherit`关键字**

强制元素继承其父元素的属性值，无论该属性是否默认可继承。

```css
/* 强制继承父元素的颜色值 */
.child-element {
    color: inherit;
}

/* 强制继承父元素的背景色（背景色默认不继承） */
.child-element {
    background-color: inherit;
}

/* 在按钮中继承父元素的字体大小 */
button {
    font-size: inherit;
}
```

**`initial`关键字**

将属性设置为CSS规范中定义的初始值（默认值），而不是浏览器的默认样式或继承值。

```css
/* 将元素的颜色设置为CSS规范定义的初始值（通常是black） */
element {
    color: initial;
}

/* 将元素的边距设置为CSS规范定义的初始值（通常是0） */
element {
    margin: initial;
}
```

**`unset`关键字**

根据属性是否可继承来决定行为：
- 对于可继承属性，`unset`等同于`inherit`
- 对于不可继承属性，`unset`等同于`initial`

```css
/* 对于color（可继承），等同于inherit */
element {
    color: unset;
}

/* 对于margin（不可继承），等同于initial */
element {
    margin: unset;
}
```

**`revert`关键字**

将属性重置为浏览器的默认样式，而不是CSS规范的初始值。

```css
/* 重置为浏览器默认样式 */
element {
    color: revert;
    font-family: revert;
}
```

### 3.7.4 继承实战示例

**示例1：基本继承应用**

HTML:
```html
<body style="font-family: 'Microsoft YaHei', sans-serif; color: #333;">
    <h1>标题文本会继承字体和颜色</h1>
    <p>段落文本也会继承字体和颜色。</p>
    <ul>
        <li>列表项同样继承字体和颜色</li>
    </ul>
    <div style="background-color: #f5f5f5; padding: 20px;">
        <p>这个段落会继承字体和颜色，但不会继承父div的背景色</p>
    </div>
</body>
```

**示例2：使用inherit覆盖默认行为**

HTML:
```html
<div class="parent" style="width: 500px; margin: 20px; color: blue;">
    父元素内容
    <div class="child">
        这个子元素会继承颜色（默认可继承），但不会继承宽度和外边距（默认不可继承）
    </div>
    <div class="child inherit-margin">
        这个子元素使用inherit强制继承父元素的外边距
    </div>
</div>
```

CSS:
```css
.child.inherit-margin {
    margin: inherit;
    background-color: #e8f4fd;
}
```

**示例3：控制表单元素继承**

表单元素通常不会继承某些样式，我们可以强制它们继承：

```css
/* 让表单元素继承字体 */
input, select, textarea, button {
    font-family: inherit;
    font-size: inherit;
    line-height: inherit;
    color: inherit;
}

/* 但保持其他属性不继承 */
input, select, textarea {
    box-sizing: border-box;
    padding: 8px 12px;
    border: 1px solid #ddd;
}
```

### 3.7.5 继承的最佳实践

1. **利用继承减少代码重复**
   - 在适当的父元素（如body）上设置全局字体和颜色
   - 避免在每个子元素上重复定义可继承的属性

2. **谨慎强制继承**
   - 只在必要时使用`inherit`强制继承
   - 过度使用`inherit`可能导致样式难以预测和维护

3. **理解级联与继承的关系**
   - 继承的属性会被子元素上直接定义的样式覆盖
   - 了解CSS优先级规则如何影响继承的样式

4. **为表单元素设置继承**
   - 表单元素如input、select等默认不继承字体样式
   - 显式设置这些元素继承字体可以保持UI一致性

5. **使用CSS变量增强继承能力**
   - CSS变量（自定义属性）总是可继承的
   - 可以利用这一特性创建更灵活的主题系统

6. **考虑性能影响**
   - 浏览器需要计算继承值，可能对性能有轻微影响
   - 但与减少的代码量相比，这种影响通常可以忽略不计

通过合理利用CSS继承机制，我们可以编写更简洁、更易于维护的样式代码，同时保持一致的视觉设计。理解哪些属性可以继承，如何控制继承行为，是成为优秀前端开发者的重要一步。

## 3.8 CSS注释

### 3.8.1 注释语法与基本用法

CSS注释以`/*`开始，以`*/`结束，可以放在样式表中的任何位置，不会被浏览器解析为样式规则，也不会影响CSS的执行。

```css
/* 这是一个单行注释 */
```

注释在CSS中有以下几种常见的使用方式：

**1. 单行注释**

```css
/* 这是一个单行注释 */
body {
    font-family: Arial, sans-serif;
}
```

**2. 多行注释**

对于较长的注释内容，可以使用多行注释：

```css
## 3.9 响应式设计基础

### 3.9.1 响应式设计概述

响应式网页设计（Responsive Web Design，RWD）是一种设计和开发方法，使网站能够根据用户设备的屏幕尺寸、平台和方向自动调整其布局和外观，提供最佳的浏览体验。

**响应式设计的核心原则**：

1. **流动式网格** - 使用相对单位（如百分比、em、rem）而非固定像素
2. **灵活的图像** - 确保图像能够随容器大小调整
3. **媒体查询** - 根据设备特性应用不同的样式规则
4. **媒体查询断点** - 定义何时改变布局的关键点

### 3.9.2 媒体查询基本语法

媒体查询是响应式设计的核心，它允许我们根据设备的特性（如屏幕宽度、高度、方向等）应用不同的CSS样式。

**基本语法**：

```css
@media media-type and (media-feature) {
    /* CSS规则 */
}
```

**媒体类型**：
- `all` - 适用于所有设备（默认）
- `screen` - 适用于电脑屏幕、平板电脑、智能手机等
- `print` - 适用于打印预览
- `speech` - 适用于屏幕阅读器等语音设备

**常用媒体特性**：
- `width` - 视口宽度
- `height` - 视口高度
- `orientation` - 设备方向（portrait/landscape）
- `aspect-ratio` - 视口宽高比
- `resolution` - 设备分辨率

### 3.9.3 视口设置

在实现响应式设计之前，必须在HTML文档的头部添加视口元标签，以确保移动设备正确渲染页面。

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>响应式设计示例</title>
    <style>
        /* CSS样式 */
    </style>
</head>
<body>
    <!-- HTML内容 -->
</body>
</html>
```

**视口元标签参数说明**：
- `width=device-width` - 设置页面宽度等于设备宽度
- `initial-scale=1.0` - 设置初始缩放比例为1（不缩放）
- `maximum-scale=1.0` - 禁止用户放大页面
- `user-scalable=no` - 禁止用户缩放页面（不推荐，影响可访问性）

### 3.9.4 常用响应式断点

响应式设计通常基于常见设备的屏幕宽度设置断点。以下是一些常用的断点值：

```css
/* 移动设备（默认样式，无媒体查询） */
.element {
    /* 移动设备样式 */
}

/* 平板设备（横向）或小屏笔记本 */
@media (min-width: 768px) {
    .element {
        /* 平板设备样式 */
    }
}

/* 中等屏幕 */
@media (min-width: 992px) {
    .element {
        /* 中等屏幕样式 */
    }
}

/* 大屏幕 */
@media (min-width: 1200px) {
    .element {
        /* 大屏幕样式 */
    }
}

/* 超大屏幕 */
@media (min-width: 1400px) {
    .element {
        /* 超大屏幕样式 */
    }
}
```

**断点策略**：
- **移动优先（推荐）** - 先为移动设备设计，然后使用`min-width`为更大屏幕添加样式
- **桌面优先** - 先为桌面设计，然后使用`max-width`为更小屏幕添加样式

### 3.9.5 响应式布局技术

#### 1. 流动布局（Fluid Layout）

使用相对单位（如百分比）代替固定单位，使元素能够随容器大小自动调整。

```css
.container {
    width: 100%; /* 占据父容器的100%宽度 */
    max-width: 1200px; /* 最大宽度限制 */
    margin: 0 auto; /* 水平居中 */
}

.column {
    width: 100%; /* 移动设备上单列 */
}

@media (min-width: 768px) {
    .column {
        width: 50%; /* 平板设备上两列 */
        float: left;
    }
}
```

#### 2. 弹性布局（Flexbox）

Flexbox是一种一维布局方法，特别适合处理响应式导航、卡片网格等布局。

```css
.flex-container {
    display: flex;
    flex-direction: column; /* 移动设备上垂直排列 */
    gap: 20px;
}

@media (min-width: 768px) {
    .flex-container {
        flex-direction: row; /* 平板及以上设备上水平排列 */
        flex-wrap: wrap;
    }
    
    .flex-item {
        flex: 1 1 calc(50% - 20px); /* 两列布局，考虑间距 */
    }
    
    @media (min-width: 992px) {
        .flex-item {
            flex: 1 1 calc(33.333% - 20px); /* 三列布局 */
        }
    }
}
```

#### 3. 网格布局（Grid）

Grid是一种二维布局方法，适用于创建复杂的响应式页面结构。

```css
.grid-container {
    display: grid;
    grid-template-columns: 1fr; /* 移动设备上单列 */
    gap: 20px;
}

@media (min-width: 768px) {
    .grid-container {
        grid-template-columns: repeat(2, 1fr); /* 平板设备上两列 */
    }
}

@media (min-width: 1200px) {
    .grid-container {
        grid-template-columns: repeat(4, 1fr); /* 大屏幕上四列 */
    }
}
```

#### 4. 响应式图像

确保图像在不同设备上都能正确显示：

```css
/* 基本的响应式图像 */
img {
    max-width: 100%; /* 图像最大宽度不超过容器 */
    height: auto; /* 保持图像的宽高比 */
}

/* 使用srcset提供不同分辨率的图像 */
```

HTML:
```html
<img srcset="small.jpg 600w, medium.jpg 1200w, large.jpg 1800w"
     sizes="(max-width: 600px) 100vw, (max-width: 1200px) 50vw, 33vw"
     src="fallback.jpg" alt="响应式图像">
```

### 3.9.6 响应式排版

使文本在不同屏幕尺寸上保持良好的可读性：

```css
/* 使用相对单位 */
body {
    font-size: 16px; /* 基础字体大小 */
    line-height: 1.5;
}

/* 使用媒体查询调整字体大小 */
@media (min-width: 768px) {
    body {
        font-size: 18px;
    }
}

/* 使用视口单位实现响应式文本 */
.hero-title {
    font-size: clamp(2rem, 5vw, 4rem); /* 最小2rem，最大4rem，基于5vw动态调整 */
}
```

### 3.9.7 响应式导航菜单

创建在移动设备上转变为汉堡菜单的导航：

HTML:
```html
<header class="header">
    <div class="container">
        <div class="logo">Logo</div>
        <button class="mobile-menu-toggle">
            <span></span>
            <span></span>
            <span></span>
        </button>
        <nav class="nav">
            <ul class="nav-list">
                <li class="nav-item"><a href="#">首页</a></li>
                <li class="nav-item"><a href="#">关于我们</a></li>
                <li class="nav-item"><a href="#">服务</a></li>
                <li class="nav-item"><a href="#">联系我们</a></li>
            </ul>
        </nav>
    </div>
</header>
```

CSS:
```css
/* 基本样式 */
.header {
    background-color: #333;
    color: white;
    padding: 1rem 0;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 1rem;
}

.logo {
    font-size: 1.5rem;
    font-weight: bold;
}

/* 移动菜单按钮 */
.mobile-menu-toggle {
    display: block;
    background: none;
    border: none;
    cursor: pointer;
    padding: 0.5rem;
    position: absolute;
    top: 1rem;
    right: 1rem;
}

.mobile-menu-toggle span {
    display: block;
    width: 25px;
    height: 3px;
    background-color: white;
    margin: 5px 0;
    transition: 0.4s;
}

/* 导航菜单 - 默认隐藏在移动设备上 */
.nav {
    display: none;
    margin-top: 1rem;
}

.nav-list {
    list-style: none;
    padding: 0;
    margin: 0;
}

.nav-item {
    margin-bottom: 1rem;
}

.nav-item a {
    color: white;
    text-decoration: none;
    display: block;
    padding: 0.5rem 0;
}

/* 显示菜单（通过JavaScript添加此类） */
.nav.active {
    display: block;
}

/* 平板及以上设备的样式 */
@media (min-width: 768px) {
    .header .container {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .mobile-menu-toggle {
        display: none; /* 隐藏汉堡按钮 */
    }
    
    .nav {
        display: flex; /* 显示导航 */
        margin-top: 0;
    }
    
    .nav-list {
        display: flex;
    }
    
    .nav-item {
        margin-bottom: 0;
        margin-left: 1.5rem;
    }
}
```

JavaScript:
```javascript
// 简单的移动菜单切换功能
const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
const nav = document.querySelector('.nav');

mobileMenuToggle.addEventListener('click', () => {
    nav.classList.toggle('active');
    mobileMenuToggle.classList.toggle('active');
});
```

### 3.9.8 响应式设计实战示例

**完整的响应式页面布局示例**：

HTML:
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>响应式网站示例</title>
    <style>
        /* 全局样式重置 */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Arial', sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f4f4f4;
        }
        
        .container {
            width: 100%;
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 1rem;
        }
        
        /* 头部样式 */
        header {
            background-color: #2c3e50;
            color: white;
            padding: 1rem 0;
        }
        
        .header-content {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .logo {
            font-size: 1.5rem;
            font-weight: bold;
        }
        
        /* 导航样式 */
        nav ul {
            display: none; /* 移动设备上隐藏导航 */
        }
        
        .mobile-menu-btn {
            display: block;
            background: none;
            border: none;
            color: white;
            font-size: 1.5rem;
            cursor: pointer;
        }
        
        /* 英雄区样式 */
        .hero {
            background-color: #3498db;
            color: white;
            padding: 4rem 0;
            text-align: center;
        }
        
        .hero h1 {
            margin-bottom: 1rem;
            font-size: 2.5rem;
        }
        
        .hero p {
            margin-bottom: 2rem;
            font-size: 1.2rem;
        }
        
        .btn {
            display: inline-block;
            background-color: #e74c3c;
            color: white;
            padding: 0.8rem 1.5rem;
            text-decoration: none;
            border-radius: 4px;
            transition: background-color 0.3s;
        }
        
        .btn:hover {
            background-color: #c0392b;
        }
        
        /* 特色内容样式 */
        .features {
            padding: 3rem 0;
        }
        
        .feature-card {
            background-color: white;
            padding: 2rem;
            margin-bottom: 2rem;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        
        .feature-card h2 {
            margin-bottom: 1rem;
            color: #2c3e50;
        }
        
        /* 页脚样式 */
        footer {
            background-color: #2c3e50;
            color: white;
            text-align: center;
            padding: 2rem 0;
        }
        
        /* 平板设备样式 */
        @media (min-width: 768px) {
            .feature-grid {
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 2rem;
            }
            
            .feature-card {
                margin-bottom: 0;
            }
            
            .mobile-menu-btn {
                display: none; /* 隐藏移动菜单按钮 */
            }
            
            nav ul {
                display: flex; /* 显示导航列表 */
                list-style: none;
            }
            
            nav ul li {
                margin-left: 1.5rem;
            }
            
            nav ul li a {
                color: white;
                text-decoration: none;
            }
        }
        
        /* 桌面设备样式 */
        @media (min-width: 1024px) {
            .feature-grid {
                grid-template-columns: repeat(3, 1fr);
            }
            
            .hero h1 {
                font-size: 3.5rem;
            }
        }
    </style>
</head>
<body>
    <!-- 头部 -->
    <header>
        <div class="container">
            <div class="header-content">
                <div class="logo">响应式网站</div>
                <nav>
                    <ul>
                        <li><a href="#">首页</a></li>
                        <li><a href="#">关于</a></li>
                        <li><a href="#">服务</a></li>
                        <li><a href="#">联系我们</a></li>
                    </ul>
                </nav>
                <button class="mobile-menu-btn">☰</button>
            </div>
        </div>
    </header>
    
    <!-- 英雄区 -->
    <section class="hero">
        <div class="container">
            <h1>响应式网页设计</h1>
            <p>在任何设备上都能完美展示的现代网站设计</p>
            <a href="#" class="btn">了解更多</a>
        </div>
    </section>
    
    <!-- 特色内容 -->
    <section class="features">
        <div class="container">
            <div class="feature-grid">
                <div class="feature-card">
                    <h2>移动优先</h2>
                    <p>从移动设备开始设计，然后扩展到更大的屏幕，确保在所有设备上都有良好的用户体验。</p>
                </div>
                <div class="feature-card">
                    <h2>灵活布局</h2>
                    <p>使用流式网格、弹性盒和CSS网格，创建能够自动适应不同屏幕尺寸的布局。</p>
                </div>
                <div class="feature-card">
                    <h2>媒体查询</h2>
                    <p>根据设备特性应用不同的样式规则，为不同屏幕尺寸提供最佳的视觉呈现。</p>
                </div>
            </div>
        </div>
    </section>
    
    <!-- 页脚 -->
    <footer>
        <div class="container">
            <p>&copy; 2023 响应式网站示例. 保留所有权利.</p>
        </div>
    </footer>
    
    <script>
        // 简单的移动菜单切换（实际项目中可扩展）
        document.querySelector('.mobile-menu-btn').addEventListener('click', function() {
            const navUL = document.querySelector('nav ul');
            navUL.style.display = navUL.style.display === 'flex' ? 'none' : 'flex';
            navUL.style.flexDirection = 'column';
            navUL.style.position = 'absolute';
            navUL.style.top = '60px';
            navUL.style.left = '0';
            navUL.style.width = '100%';
            navUL.style.backgroundColor = '#2c3e50';
            navUL.style.padding = '1rem';
        });
    </script>
</body>
</html>
```

### 3.9.9 响应式设计最佳实践

1. **移动优先设计**
   - 从移动设备的小屏幕开始设计，然后逐步扩展到大屏幕
   - 使用`min-width`媒体查询为更大的屏幕添加样式

2. **使用相对单位**
   - 优先使用`%`, `rem`, `em`, `vw`, `vh`等相对单位
   - 避免在布局中过多使用固定像素值

3. **保持内容可读性**
   - 确保在各种屏幕尺寸上文本都易于阅读
   - 合理设置行高、字间距和文本大小

4. **优化触摸目标**
   - 在移动设备上，确保按钮和链接足够大（至少48px）
   - 为触摸元素之间留出足够的空间

5. **性能优化**
   - 优化图像，使用响应式图像技术
   - 减少HTTP请求，合并CSS文件
   - 使用CSS压缩和最小化

6. **测试各种设备**
   - 在多种实际设备上测试网站
   - 使用浏览器开发者工具的设备模拟功能
   - 考虑不同的屏幕方向（横向和纵向）

7. **渐进增强**
   - 确保基本功能在所有浏览器中正常工作
   - 然后为支持更高级功能的浏览器添加增强体验

8. **避免过度设计**
   - 不要为了响应式而响应式，确保每个断点都有明确的设计目标
   - 避免过多的断点，这可能会使代码难以维护

通过遵循这些响应式设计原则和最佳实践，我们可以创建出在各种设备上都能提供出色用户体验的现代网站。响应式设计不再是一个选项，而是现代Web开发的标准要求。
   多行注释
   示例
*/
.container {
    max-width: 1200px;
    margin: 0 auto;
}
```

**3. 行内注释**

行内注释放在代码行的末尾，用于对特定的属性或值进行简短解释：

```css
.element {
    display: flex; /* 使用flex布局 */
    justify-content: space-between; /* 元素两端对齐 */
    padding: 1rem; /* 16px的内边距 */
}
```

### 3.8.2 注释的主要作用

**1. 代码解释与文档化**

注释可以解释复杂的样式逻辑、特殊的实现方式或设计决策，使代码更易于理解：

```css
/* 响应式导航栏样式 - 在移动设备上隐藏，通过JS切换显示 */
.nav-menu {
    display: none; /* 默认隐藏菜单 */
    position: absolute;
    top: 100%;
    left: 0;
    width: 100%;
    background-color: #fff;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    z-index: 100; /* 确保在其他元素之上 */
}
```

**2. 版本控制与变更跟踪**

注释可以用来记录样式的修改历史和版本信息：

```css
/*
 * 修改历史：
 * 2023-05-10: 增加响应式断点 - Zhang Wei
 * 2023-05-05: 优化颜色对比度 - Li Ming
 */
.primary-button {
    background-color: #007bff;
    color: white;
    padding: 10px 20px;
    border-radius: 4px;
}
```

**3. 组织代码结构**

注释可以用来划分CSS文件的不同部分，提高代码的可读性和组织性：

```css
/* ===============
   全局样式重置
   =============== */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

/* ===============
   布局组件
   =============== */
.header {
    /* 头部样式 */
}

.footer {
    /* 底部样式 */
}
```

**4. 临时禁用样式**

在开发和调试过程中，可以使用注释临时禁用特定的样式规则：

```css
.element {
    color: #333;
    /* background-color: #f0f0f0; */ /* 临时禁用背景色 */
    padding: 10px;
}
```

### 3.8.3 注释的最佳实践

**1. 保持简洁明了**

注释应该简洁地传达必要的信息，避免过于冗长或冗余的解释：

```css
/* 不好的注释 */
/* 这个类设置元素的文本颜色为红色 */
.red-text {
    color: red;
}

/* 好的注释 */
/* 错误提示文本样式 */
.error-text {
    color: #d32f2f;
}
```

**2. 遵循一致的格式**

在项目中使用一致的注释格式，可以提高代码的专业性和可读性：

```css
/*
 * 模块：用户卡片
 * 描述：显示用户基本信息的卡片组件
 * 作者：Wang Jie
 */
.user-card {
    /* 卡片样式 */
}
```

**3. 使用注释标记重要信息**

对于需要特别注意的部分，可以使用特殊标记的注释：

```css
/* TODO: 优化此样式的性能 */
.complex-animation {
    animation: fadeIn 0.5s ease-in-out;
}

/* FIXME: 修复在IE11中的显示问题 */
.flex-container {
    display: flex;
}
```

**4. 避免过多不必要的注释**

对于自明的代码，过多的注释反而会降低代码的可读性：

```css
/* 不好的做法：注释显而易见的代码 */
.header {
    width: 100%; /* 设置宽度为100% */
    height: 60px; /* 设置高度为60像素 */
    background-color: #333; /* 设置背景色为深灰色 */
}

/* 好的做法：只添加有意义的注释 */
.header {
    width: 100%;
    height: 60px;
    background-color: #333;
    position: sticky; /* 粘性定位，滚动时保持在顶部 */
}
```

**5. 使用CSS注释分隔大型样式表**

在大型项目中，可以使用注释来清晰地分隔不同的功能模块：

```css
/* ========================================================================== */
/* 1. 重置和基础样式 */
/* ========================================================================== */

/* ========================================================================== */
/* 2. 布局组件 */
/* ========================================================================== */

/* ========================================================================== */
/* 3. 响应式设计 */
/* ========================================================================== */
```

### 3.8.4 注释的限制和注意事项

**1. CSS不支持嵌套注释**

与某些编程语言不同，CSS不支持嵌套的注释结构。以下代码会导致问题：

```css
/* 外层注释 /* 这是内部注释 */ 这里的代码会被解析为CSS */
.element {
    color: red; /* 这段代码可能不会正常工作 */
}
```

正确的做法是避免嵌套注释，或使用注释标记来区分不同层次的注释：

```css
/* 外层注释 */
/* 这是另一个注释 */
.element {
    color: red;
}
```

**2. 注释不会压缩**

在生产环境中，通常会压缩CSS文件以减小文件大小。大多数CSS压缩工具会自动移除所有注释，但有些保留重要注释（以`/*!`开头的注释）。

```css
/*! 这个注释在压缩时会被保留 */
.element {
    color: red;
}

/* 这个注释在压缩时会被移除 */
.another-element {
    color: blue;
}
```

**3. 注释可能影响CSS预处理器**

在使用Sass、Less等CSS预处理器时，需要注意预处理器对注释的特殊处理规则：

- 单行注释 `// 这是注释` 在Sass/Less中有效，但编译为CSS时会被移除
- 多行注释 `/* 这是注释 */` 在Sass/Less中会保留在编译后的CSS中

### 3.8.5 实战示例：组织良好的CSS注释

下面是一个使用注释组织良好的CSS文件示例：

```css
/* ========================================================================== */
/* 网站名称：示例网站
   作者：前端开发团队
   创建日期：2023-06-01
   版本：1.0
/* ========================================================================== */

/* ========================================================================== */
/* 1. 重置样式
/* ========================================================================== */
*,
*::before,
*::after {
    margin: 0;
    padding: 0;
    box-sizing: inherit;
}

html {
    box-sizing: border-box;
    font-size: 16px; /* 1rem = 16px */
}

/* ========================================================================== */
/* 2. 全局变量
/* ========================================================================== */
:root {
    /* 颜色变量 */
    --color-primary: #2c3e50;
    --color-secondary: #3498db;
    --color-accent: #e74c3c;
    --color-text: #333;
    --color-background: #f9f9f9;
    
    /* 字体变量 */
    --font-family-primary: 'Helvetica Neue', Arial, sans-serif;
    --font-family-secondary: 'Georgia', serif;
    
    /* 间距变量 */
    --spacing-sm: 0.5rem;
    --spacing-md: 1rem;
    --spacing-lg: 2rem;
}

/* ========================================================================== */
/* 3. 布局组件
/* ========================================================================== */

/* 3.1 头部样式 */
.header {
    background-color: var(--color-primary);
    color: white;
    padding: var(--spacing-md) var(--spacing-lg);
    position: sticky;
    top: 0;
    z-index: 1000;
}

/* 3.2 导航菜单 */
.nav {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.nav__list {
    display: flex;
    list-style: none;
}

.nav__item {
    margin-left: var(--spacing-lg);
}

/* TODO: 添加移动端导航菜单样式 */

/* ========================================================================== */
/* 4. 响应式设计
/* ========================================================================== */

/* 平板设备 */
@media (max-width: 768px) {
    .container {
        padding: 0 var(--spacing-md);
    }
    
    .nav__list {
        display: none; /* 隐藏桌面导航 */
    }
    
    /* 显示移动端菜单按钮 */
    .mobile-menu-btn {
        display: block;
    }
}

/* 移动设备 */
@media (max-width: 480px) {
    html {
        font-size: 14px; /* 减小字体大小 */
    }
    
    .header {
        padding: var(--spacing-sm) var(--spacing-md);
    }
}

/* ========================================================================== */
/* 5. 工具类
/* ========================================================================== */

.text-center { text-align: center; }
.text-right { text-align: right; }
.text-left { text-align: left; }

.mt-1 { margin-top: var(--spacing-sm); }
.mt-2 { margin-top: var(--spacing-md); }
.mt-3 { margin-top: var(--spacing-lg); }

/* ========================================================================== */
/* END OF FILE
/* ========================================================================== */
```

通过合理使用注释，我们可以使CSS代码更加清晰、易于维护，并为团队协作提供更好的支持。良好的注释习惯不仅有助于当前的开发，也为未来的代码维护和扩展奠定了基础。
/* 
   这是一个
   多行注释
*/

p { 
    color: blue; /* 这是行内注释 */
}
```

## 响应式设计基础

响应式设计使网页能够适应不同的设备和屏幕尺寸。CSS媒体查询是实现响应式设计的关键。

### 媒体查询（Media Queries）

```css
/* 基本语法 */
@media media-type and (media-feature) {
    /* CSS规则 */
}

/* 常用媒体查询断点示例 */

/* 移动设备 */
@media (max-width: 767px) {
    .container {
        width: 100%;
        padding: 0 15px;
    }
    
    .menu {
        display: none;
    }
    
    .mobile-menu {
        display: block;
    }
}

/* 平板设备 */
@media (min-width: 768px) and (max-width: 991px) {
    .container {
        width: 750px;
        margin: 0 auto;
    }
}

/* 桌面设备 */
@media (min-width: 992px) and (max-width: 1199px) {
    .container {
        width: 970px;
        margin: 0 auto;
    }
}

/* 大屏幕设备 */
@media (min-width: 1200px) {
    .container {
        width: 1170px;
        margin: 0 auto;
    }
}

/* 视口方向 */
@media (orientation: landscape) {
    /* 横屏模式样式 */
}

@media (orientation: portrait) {
    /* 竖屏模式样式 */
}
```

### 视口设置

在HTML中添加适当的视口设置对于响应式设计至关重要：

```html
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
```

这个标签告诉浏览器使用设备的实际宽度，并设置初始缩放级别为1，确保页面在各种设备上都能正确显示。

## 3.10 CSS命名约定

CSS命名约定是前端开发中的重要规范，良好的命名约定可以显著提高代码的可读性、可维护性和团队协作效率。本节将详细介绍几种常用的CSS命名方法及其最佳实践。

### 3.10.1 BEM命名法

BEM（Block, Element, Modifier）是一种由Yandex团队提出的CSS命名约定，特别适合组件化开发。

#### 核心概念
- **Block（块）**：独立的、可重用的组件，具有自己的功能和意义
- **Element（元素）**：块内的子元素，依赖于块，不能独立使用
- **Modifier（修饰符）**：块或元素的状态或变体

#### 命名格式
```css
/* 块：使用简单的语义化类名 */
.block {}

/* 元素：块名 + 双下划线 + 元素名 */
.block__element {}

/* 修饰符：块名/元素名 + 双连字符 + 修饰符名 */
.block--modifier {}
.block__element--modifier {}
```

#### 实际应用示例

```html
<header class="header header--dark">
  <div class="header__logo"></div>
  <nav class="header__nav">
    <ul class="header__nav-list">
      <li class="header__nav-item"><a href="#" class="header__nav-link header__nav-link--active">首页</a></li>
      <li class="header__nav-item"><a href="#" class="header__nav-link">产品</a></li>
      <li class="header__nav-item"><a href="#" class="header__nav-link">关于我们</a></li>
    </ul>
  </nav>
  <button class="header__btn header__btn--primary">联系我们</button>
</header>
```

```css
/* 块样式 */
.header {
  padding: 20px;
  background-color: white;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* 块修饰符 - 深色主题 */
.header--dark {
  background-color: #333;
  color: white;
}

/* 元素样式 */
.header__logo {
  font-size: 24px;
  font-weight: bold;
}

.header__nav {
  margin: 0 20px;
}

.header__nav-list {
  display: flex;
  list-style: none;
  padding: 0;
}

.header__nav-item {
  margin: 0 10px;
}

.header__nav-link {
  color: inherit;
  text-decoration: none;
  padding: 5px 10px;
  transition: all 0.3s ease;
}

/* 元素修饰符 - 激活状态 */
.header__nav-link--active {
  color: #007bff;
  font-weight: bold;
}

/* 按钮元素 */
.header__btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

/* 按钮修饰符 - 主要按钮 */
.header__btn--primary {
  background-color: #007bff;
  color: white;
}
```

#### BEM的优点
1. **清晰的结构关系**：通过命名直接表达元素间的父子关系
2. **避免嵌套过深**：降低CSS选择器的复杂性
3. **高度可维护**：修改组件时只需要关注对应类名的样式
4. **良好的可扩展性**：便于添加新的组件和功能

### 3.10.2 OOCSS命名法

OOCSS（Object-Oriented CSS）是一种面向对象的CSS设计方法，强调分离结构和样式。

#### 核心原则
- **结构与样式分离**：将通用的结构和特定的样式分开
- **容器与内容分离**：内容样式不依赖于容器

#### 命名格式
```css
/* 基础对象类（结构） */
.object {
  /* 结构样式，如宽度、高度、内边距等 */
}

/* 修饰类（样式） */
.skin, .theme, .state {
  /* 样式、主题、状态等，如颜色、背景、阴影等 */
}
```

#### 实际应用示例
```css
/* 基础按钮对象（结构） */
.btn {
  display: inline-block;
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  text-align: center;
  cursor: pointer;
}

/* 主题修饰类 */
.btn--primary {
  background-color: #007bff;
  color: white;
}

.btn--success {
  background-color: #28a745;
  color: white;
}

.btn--danger {
  background-color: #dc3545;
  color: white;
}

/* 尺寸修饰类 */
.btn--small {
  padding: 4px 8px;
  font-size: 12px;
}

.btn--large {
  padding: 12px 24px;
  font-size: 16px;
}
```

### 3.10.3 SMACSS命名法

SMACSS（Scalable and Modular Architecture for CSS）是一种可扩展的模块化CSS架构。

#### 分类规则
1. **Base（基础）**：重置和默认样式
2. **Layout（布局）**：页面结构和网格系统
3. **Module（模块）**：可重用的UI组件
4. **State（状态）**：元素的不同状态
5. **Theme（主题）**：全局视觉风格

#### 命名格式
```css
/* 基础样式（无前缀） */
h1, h2, p {
  /* 默认样式 */
}

/* 布局样式（l- 前缀） */
.l-container, .l-header, .l-footer {
  /* 布局相关样式 */
}

/* 模块样式（语义化名称） */
.nav, .card, .button {
  /* 模块样式 */
}

/* 状态样式（is- 前缀） */
.is-active, .is-hidden, .is-loading {
  /* 状态样式 */
}

/* 主题样式（theme- 前缀） */
.theme-dark, .theme-light {
  /* 主题样式 */
}
```

### 3.10.4 命名约定最佳实践

#### 通用规则
1. **语义化优先**：使用描述元素用途的名称，而非样式
2. **使用小写字母**：类名全部小写
3. **使用连字符**：`.button-primary` 而非 `.buttonPrimary` 或 `.button_primary`
4. **避免缩写**：除非是广泛使用的通用缩写（如nav, btn）
5. **避免使用ID**：优先使用类，ID优先级过高且不可重用
6. **保持一致性**：在整个项目中使用相同的命名风格

#### 推荐命名模式
1. **组件名称**：使用具体的组件名称，如 `.nav`、`.card`、`.modal`
2. **子元素**：使用组件名加描述，如 `.nav-item`、`.card-title`
3. **状态**：使用 `is-` 或 `has-` 前缀，如 `.is-active`、`.has-error`
4. **修饰符**：使用描述性名称，如 `.button-primary`、`.nav-vertical`
5. **实用工具类**：使用描述性功能名称，如 `.text-center`、`.clearfix`

#### 命名反模式
1. **基于样式的命名**：如 `.red-text`、`.left-aligned`
2. **无意义的命名**：如 `.box-1`、`.div2`
3. **过度嵌套**：如 `.header .nav ul li a`
4. **驼峰命名**：如 `.buttonPrimary`（不符合CSS命名惯例）
5. **下划线命名**：如 `.button_primary`（虽然有效，但不如连字符通用）

#### 实用工具类命名
```css
/* 定位工具类 */
.pos-rel { position: relative; }
.pos-abs { position: absolute; }
.pos-fix { position: fixed; }

/* 文本对齐工具类 */
.text-left { text-align: left; }
.text-center { text-align: center; }
.text-right { text-align: right; }

/* 显示工具类 */
.d-none { display: none; }
.d-block { display: block; }
.d-inline { display: inline; }
.d-inline-block { display: inline-block; }
.d-flex { display: flex; }
.d-grid { display: grid; }

/* 边距工具类 */
.m-0 { margin: 0; }
.m-1 { margin: 0.25rem; }
.m-2 { margin: 0.5rem; }
/* 同理可扩展 padding、width、height 等工具类 */
```

### 3.10.5 项目级命名约定示例

下面是一个完整的项目命名约定示例，结合了BEM和实用工具类的优点：

```css
/* 1. 基础样式（重置和默认） */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Arial', sans-serif;
  line-height: 1.6;
  color: #333;
}

/* 2. 布局组件 */
.page-header {
  background-color: #f8f9fa;
  padding: 1rem 0;
}

.container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}

/* 3. 功能组件（使用BEM） */
.card {
  background-color: white;
  border-radius: 0.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.card__image {
  width: 100%;
  height: auto;
}

.card__content {
  padding: 1rem;
}

.card__title {
  font-size: 1.25rem;
  margin-bottom: 0.5rem;
}

.card__text {
  color: #666;
  margin-bottom: 1rem;
}

.card__button {
  display: inline-block;
  padding: 0.5rem 1rem;
  background-color: #007bff;
  color: white;
  text-decoration: none;
  border-radius: 0.25rem;
}

.card--featured {
  border: 2px solid #007bff;
}

/* 4. 状态类 */
.is-loading {
  opacity: 0.7;
  pointer-events: none;
}

.is-active {
  color: #007bff;
  font-weight: bold;
}

/* 5. 实用工具类 */
.text-center { text-align: center; }
.text-muted { color: #6c757d; }
.mb-2 { margin-bottom: 1rem; }
.mt-3 { margin-top: 1.5rem; }
```

通过遵循一致的命名约定，不仅可以提高代码的可读性和可维护性，还能促进团队协作，减少潜在的命名冲突，使CSS代码更加健壮和灵活。

## 3.11 CSS最佳实践

CSS最佳实践是前端开发中积累的经验总结，遵循这些实践可以帮助你编写高效、可维护、可扩展的CSS代码。本节将详细介绍CSS开发中的关键最佳实践。

### 3.11.1 代码组织与结构

良好的代码组织结构是可维护CSS的基础。

#### 模块化组织

将CSS代码按功能模块拆分，便于管理和维护：

```
css/
├── base/            # 基础样式
│   ├── reset.css    # CSS重置
│   ├── variables.css # CSS变量
│   └── typography.css # 排版样式
├── layout/          # 布局样式
│   ├── grid.css     # 网格系统
│   └── containers.css # 容器样式
├── components/      # 组件样式
│   ├── buttons.css  # 按钮样式
│   ├── cards.css    # 卡片样式
│   └── navigation.css # 导航样式
├── pages/           # 页面特定样式
│   ├── home.css     # 首页样式
│   └── about.css    # 关于页样式
├── utilities/       # 工具类
│   ├── spacing.css  # 间距工具类
│   └── text.css     # 文本工具类
└── main.css         # 主样式文件，用于导入其他CSS文件
```

#### 样式文件导入

在主样式文件中按顺序导入各个模块：

```css
/* main.css */
/* 1. 基础样式 */
@import 'base/variables.css';
@import 'base/reset.css';
@import 'base/typography.css';

/* 2. 布局样式 */
@import 'layout/grid.css';
@import 'layout/containers.css';

/* 3. 组件样式 */
@import 'components/buttons.css';
@import 'components/cards.css';
@import 'components/navigation.css';

/* 4. 页面特定样式 */
@import 'pages/home.css';
@import 'pages/about.css';

/* 5. 工具类 */
@import 'utilities/spacing.css';
@import 'utilities/text.css';
```

#### 逻辑分组与注释

在单个CSS文件中，使用注释将相关样式分组：

```css
/* ========================================================================== */
/* 导航组件
/* ========================================================================== */

.navbar {
  /* 样式... */
}

.navbar__logo {
  /* 样式... */
}

/* ========================================================================== */
/* 卡片组件
/* ========================================================================== */

.card {
  /* 样式... */
}

.card__title {
  /* 样式... */
}
```

### 3.11.2 性能优化

CSS性能优化对于提升页面加载速度和渲染性能至关重要。

#### 减少CSS体积

1. **删除未使用的CSS**：使用工具如PurgeCSS检测并删除未使用的样式
2. **合并CSS文件**：减少HTTP请求数量
3. **压缩CSS**：使用工具如CSSNano或csso进行压缩
4. **使用CSS预处理器**：通过变量、混合器等功能减少重复代码

#### 选择器优化

1. **避免使用通用选择器**：通用选择器`*`会匹配所有元素，影响性能
   ```css
   /* 不推荐 */
   * {
     color: #333;
   }
   
   /* 推荐 */
   body, p, h1, h2, h3, h4, h5, h6 {
     color: #333;
   }
   ```

2. **避免深层次嵌套**：CSS选择器从右到左匹配，深层次嵌套会增加匹配成本
   ```css
   /* 不推荐 */
   .header .nav ul li a {
     color: blue;
   }
   
   /* 推荐 */
   .nav-link {
     color: blue;
   }
   ```

3. **优先使用类选择器**：ID选择器虽然性能好，但不可重用，且优先级过高
   ```css
   /* 不推荐 */
   #navigation {
     display: flex;
   }
   
   /* 推荐 */
   .navigation {
     display: flex;
   }
   ```

4. **避免使用属性选择器**：属性选择器性能较差，尤其是带正则表达式的
   ```css
   /* 不推荐 */
   input[type="text"] {
     border: 1px solid #ddd;
   }
   
   /* 推荐 */
   .text-input {
     border: 1px solid #ddd;
   }
   ```

#### 样式优化

1. **使用简写属性**：减少CSS代码量
   ```css
   /* 不推荐 */
   margin-top: 10px;
   margin-right: 20px;
   margin-bottom: 10px;
   margin-left: 20px;
   
   /* 推荐 */
   margin: 10px 20px;
   ```

2. **避免使用过多的`@import`**：每个`@import`都会增加HTTP请求
   - 生产环境建议使用构建工具合并CSS文件
   - 开发环境可以使用Sass/Less的导入功能

3. **使用CSS变量**：减少重复值，便于主题切换
   ```css
   :root {
     --primary-color: #007bff;
     --secondary-color: #6c757d;
   }
   
   .btn-primary {
     background-color: var(--primary-color);
   }
   ```

4. **避免CSS表达式**：CSS表达式性能较差，且已被现代浏览器废弃

### 3.11.3 可维护性实践

编写可维护的CSS是长期项目成功的关键。

#### 命名约定

1. **遵循一致的命名约定**：如BEM、OOCSS或SMACSS
2. **使用语义化类名**：描述元素用途而非样式
   ```css
   /* 不推荐 */
   .blue-text {
     color: blue;
   }
   
   /* 推荐 */
   .error-message {
     color: blue;
   }
   ```
3. **避免使用无意义的类名**：如`.left`, `.top`, `.box1`

#### 减少特殊性

1. **避免使用ID**：ID选择器优先级过高，难以覆盖
2. **避免使用`!important`**：除非绝对必要
   - `!important`会破坏级联规则，使调试变得困难
   - 仅在覆盖第三方样式或修复特定问题时使用

#### 文档与注释

1. **为复杂组件添加文档**：说明组件的用途、结构和使用方法
2. **使用版本控制**：记录样式的变更历史
3. **遵循项目规范**：团队成员共同遵守同一套规范

### 3.11.4 响应式设计最佳实践

响应式设计是现代Web开发的重要部分。

#### 移动优先设计

1. **从移动设备开始**：先为小屏幕设计，再逐步增加大屏幕样式
2. **使用`min-width`媒体查询**：确保样式在各种屏幕尺寸下正常工作
   ```css
   /* 移动设备样式 */
   .container {
     width: 100%;
     padding: 0 15px;
   }
   
   /* 平板设备样式 */
   @media (min-width: 768px) {
     .container {
       width: 750px;
       margin: 0 auto;
     }
   }
   ```

#### 断点策略

1. **基于内容设置断点**：根据内容布局需求设置断点，而非特定设备
2. **使用相对单位**：如`em`, `rem`, `%`而非固定像素值
3. **避免固定宽度**：使用流式布局适应不同屏幕尺寸

#### 图像优化

1. **使用`srcset`和`sizes`**：为不同设备提供适当尺寸的图像
   ```html
   <img src="small.jpg" 
        srcset="medium.jpg 1000w, large.jpg 2000w"
        sizes="(max-width: 600px) 100vw, 50vw" 
        alt="Responsive image">
   ```
2. **使用CSS媒体查询加载背景图**：
   ```css
   .hero {
     background-image: url('small.jpg');
   }
   
   @media (min-width: 768px) {
     .hero {
       background-image: url('medium.jpg');
     }
   }
   ```

### 3.11.5 无障碍设计最佳实践

CSS对网页的无障碍性有重要影响。

#### 颜色对比度

1. **确保文本与背景的对比度**：满足WCAG AA标准（正常文本4.5:1，大文本3:1）
2. **不要仅依赖颜色传达信息**：结合形状、图标或文本
   ```css
   /* 不推荐 */
   .error {
     color: red;
   }
   
   /* 推荐 */
   .error {
     color: red;
     border-left: 4px solid red;
     padding-left: 10px;
   }
   ```

#### 焦点样式

1. **提供明显的焦点指示**：帮助键盘用户导航
   ```css
   a:focus, button:focus {
     outline: 3px solid #007bff;
     outline-offset: 2px;
   }
   ```
2. **不要移除默认焦点样式**：除非提供了等效的替代样式

#### 字体与排版

1. **使用相对字体大小**：允许用户调整字体大小
   ```css
   body {
     font-size: 16px; /* 基础字体大小 */
   }
   
   p {
     font-size: 1rem; /* 相对于基础字体大小 */
   }
   ```
2. **确保足够的行高**：推荐行高为1.5或更大
   ```css
   p {
     line-height: 1.6;
   }
   ```

### 3.11.6 动画与过渡最佳实践

合理的动画和过渡可以提升用户体验。

#### 性能优化

1. **使用GPU加速的属性**：优先使用`transform`和`opacity`进行动画
   ```css
   /* 高效动画 */
   .element {
     transition: transform 0.3s ease, opacity 0.3s ease;
   }
   
   /* 低效动画 */
   .element {
     transition: width 0.3s ease, height 0.3s ease;
   }
   ```

2. **使用`will-change`提示**：告诉浏览器元素即将发生变化
   ```css
   .element {
     will-change: transform, opacity;
   }
   ```

#### 可访问性考虑

1. **提供动画控制选项**：允许用户关闭动画（如尊重`prefers-reduced-motion`）
   ```css
   @media (prefers-reduced-motion: reduce) {
     * {
       animation-duration: 0.01ms !important;
       animation-iteration-count: 1 !important;
       transition-duration: 0.01ms !important;
     }
   }
   ```

2. **避免过度动画**：过多的动画可能分散用户注意力或导致不适

### 3.11.7 现代CSS特性使用最佳实践

充分利用现代CSS特性可以简化代码并提升性能。

#### CSS Grid与Flexbox

1. **合理选择布局技术**：
   - 使用`Flexbox`处理一维布局（行或列）
   - 使用`Grid`处理二维布局（行和列同时）

2. **避免过度使用框架**：现代CSS原生功能已经很强大，许多布局可以不依赖框架实现

#### CSS变量

1. **集中管理主题变量**：在`:root`中定义全局变量
   ```css
   :root {
     /* 颜色变量 */
     --primary: #007bff;
     --secondary: #6c757d;
     --success: #28a745;
     
     /* 间距变量 */
     --spacing-xs: 0.25rem;
     --spacing-sm: 0.5rem;
     --spacing-md: 1rem;
     --spacing-lg: 1.5rem;
     --spacing-xl: 2rem;
     
     /* 字体变量 */
     --font-family: 'Inter', sans-serif;
     --font-size-sm: 0.875rem;
     --font-size-base: 1rem;
     --font-size-lg: 1.125rem;
   }
   ```

2. **局部变量**：为特定组件定义局部变量
   ```css
   .theme-dark {
     --text-color: #fff;
     --background-color: #333;
   }
   ```

#### CSS函数

1. **使用CSS数学函数**：`calc()`, `clamp()`, `min()`, `max()`
   ```css
   .container {
     width: clamp(300px, 80%, 1200px);
   }
   
   .sidebar {
     width: 300px;
   }
   
   .content {
     width: calc(100% - 320px); /* 考虑间距 */
   }
   ```

2. **使用颜色函数**：`rgba()`, `hsl()`, `hsla()`, `rgb()`, `hwb()`, `color-mix()`等
   ```css
   .button {
     background-color: hsl(210, 100%, 50%);
   }
   
   .button:hover {
     background-color: hsl(210, 100%, 60%); /* 更亮的颜色 */
   }
   ```

### 3.11.8 团队协作最佳实践

在团队环境中，建立统一的CSS开发规范非常重要。

#### 制定CSS规范文档

1. **命名约定**：明确使用哪种命名方法（BEM、OOCSS等）
2. **文件结构**：定义CSS文件的组织方式
3. **注释规范**：统一注释格式和内容要求
4. **代码审查标准**：制定CSS代码审查的具体标准

#### 使用CSS预处理器

1. **选择合适的预处理器**：Sass、Less或Stylus
2. **利用预处理器功能**：变量、混合器、嵌套、继承等
   ```scss
   // Sass示例
   $primary-color: #007bff;
   $border-radius: 4px;
   
   @mixin button-base {
     padding: 0.5rem 1rem;
     border: none;
     border-radius: $border-radius;
     cursor: pointer;
   }
   
   .button-primary {
     @include button-base;
     background-color: $primary-color;
     color: white;
   }
   ```

#### 使用CSS后处理器

1. **自动添加浏览器前缀**：使用Autoprefixer
2. **自动优化CSS**：使用PostCSS的各种插件

#### 版本控制最佳实践

1. **提交小型、聚焦的变更**：便于审查和回滚
2. **添加有意义的提交消息**：描述变更的目的和内容
3. **定期合并和更新**：避免大型合并冲突

通过遵循这些CSS最佳实践，你可以编写更加高效、可维护和用户友好的CSS代码，同时提高团队协作效率和项目质量。

## 3.12 CSS练习题

通过实践练习是掌握CSS的最佳方式。本节提供了一系列练习题，从基础到进阶，帮助你巩固所学知识并提升实际应用能力。

### 3.12.1 练习题1：CSS基础选择器与样式应用

#### 目标
创建一个包含基本页面结构的HTML文件，并使用CSS选择器为不同元素应用样式。

#### HTML结构要求
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CSS选择器练习</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <!-- 1. 页头部分 -->
    <header class="site-header">
        <h1 class="site-title">我的网站</h1>
        
        <!-- 2. 导航部分 -->
        <nav class="main-nav">
            <ul class="nav-list">
                <li class="nav-item"><a href="#home" class="nav-link active">首页</a></li>
                <li class="nav-item"><a href="#about" class="nav-link">关于我们</a></li>
                <li class="nav-item"><a href="#services" class="nav-link">服务</a></li>
                <li class="nav-item"><a href="#contact" class="nav-link">联系我们</a></li>
            </ul>
        </nav>
    </header>

    <!-- 3. 主要内容区域 -->
    <main class="main-content">
        <!-- 介绍部分 -->
        <section class="section intro" id="home">
            <h2 class="section-title">欢迎来到我的网站</h2>
            <p>这是一个关于CSS选择器和基本样式应用的练习页面。通过这个练习，你可以掌握如何使用不同的选择器为HTML元素添加样式。</p>
            <p>选择器是CSS的基础，熟练掌握各种选择器可以让你精确地定位和设计页面元素。</p>
        </section>

        <!-- 关于部分 -->
        <section class="section about" id="about">
            <h2 class="section-title">关于我们</h2>
            <p>我们是一个专业的Web开发团队，致力于创建美观、实用的网站和Web应用。</p>
            <p>我们的服务包括网站设计、前端开发、后端开发和移动应用开发。</p>
        </section>

        <!-- 服务部分 -->
        <section class="section services" id="services">
            <h2 class="section-title">我们的服务</h2>
            <ul class="services-list">
                <li class="service-item">网站设计与开发</li>
                <li class="service-item">响应式网站建设</li>
                <li class="service-item">电子商务解决方案</li>
                <li class="service-item">Web应用开发</li>
                <li class="service-item">搜索引擎优化(SEO)</li>
            </ul>
        </section>

        <!-- 联系部分 -->
        <section class="section contact" id="contact">
            <h2 class="section-title">联系我们</h2>
            <form class="contact-form">
                <div class="form-group">
                    <label for="name">姓名:</label>
                    <input type="text" id="name" name="name" placeholder="请输入您的姓名">
                </div>
                <div class="form-group">
                    <label for="email">邮箱:</label>
                    <input type="email" id="email" name="email" placeholder="请输入您的邮箱">
                </div>
                <div class="form-group">
                    <label for="message">留言:</label>
                    <textarea id="message" name="message" rows="4" placeholder="请输入您的留言"></textarea>
                </div>
                <button type="submit" class="submit-btn">提交</button>
            </form>
        </section>
    </main>

    <!-- 页脚部分 -->
    <footer class="site-footer">
        <p>&copy; 2023 我的网站. 保留所有权利.</p>
    </footer>
</body>
</html>
```

#### CSS样式要求
创建一个`styles.css`文件，实现以下样式：

1. **基础样式设置**
   ```css
   /* 重置默认样式 */
   * {
       margin: 0;
       padding: 0;
       box-sizing: border-box;
   }
   
   /* 为body设置基本的字体和颜色 */
   body {
       font-family: 'Arial', 'Helvetica', sans-serif;
       line-height: 1.6;
       color: #333;
       background-color: #f4f4f4;
       padding: 0;
       margin: 0;
   }
   ```

2. **页头样式**
   ```css
   /* 为header设置背景色和内边距 */
   .site-header {
       background-color: #35424a;
       color: white;
       padding: 20px 0;
       min-height: 70px;
       border-bottom: #e8491d 3px solid;
   }
   
   .site-title {
       margin: 0;
       padding-left: 20px;
       float: left;
   }
   ```

3. **导航样式**
   ```css
   /* 导航布局 */
   .main-nav {
       float: right;
       margin-top: 15px;
       padding-right: 20px;
   }
   
   .nav-list {
       list-style: none;
   }
   
   .nav-item {
       display: inline;
       padding: 0 20px 0 20px;
   }
   
   /* 为nav中的链接添加样式 */
   .nav-link {
       color: #ffffff;
       text-decoration: none;
       text-transform: uppercase;
       font-size: 16px;
   }
   
   /* 添加hover效果 */
   .nav-link:hover {
       color: #e8491d;
       font-weight: bold;
   }
   
   /* 激活状态样式 */
   .nav-link.active {
       color: #e8491d;
       font-weight: bold;
   }
   ```

4. **内容区域样式**
   ```css
   /* 主要内容区域 */
   .main-content {
       width: 80%;
       margin: 0 auto;
       padding: 20px 0;
       overflow: hidden;
   }
   
   /* 为section设置外边距和内边距 */
   .section {
       background-color: white;
       padding: 20px;
       margin-bottom: 20px;
       border-radius: 5px;
       box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
   }
   ```

5. **特定部分样式**
   ```css
   /* 为class="intro"的section添加特殊样式 */
   .intro {
       border-left: 5px solid #35424a;
       background-color: #f8f8f8;
   }
   
   /* 为id="contact"的section添加另一种特殊样式 */
   #contact {
       border-left: 5px solid #e8491d;
   }
   ```

6. **标题样式**
   ```css
   /* 为所有h2标题设置样式 */
   h2.section-title {
       color: #35424a;
       margin-bottom: 15px;
       padding-bottom: 10px;
       border-bottom: 1px solid #eaeaea;
   }
   ```

7. **列表和表单样式**
   ```css
   /* 服务列表样式 */
   .services-list {
       list-style-position: inside;
       padding-left: 20px;
   }
   
   .service-item {
       margin-bottom: 10px;
   }
   
   /* 表单样式 */
   .contact-form {
       margin-top: 20px;
   }
   
   .form-group {
       margin-bottom: 15px;
   }
   
   label {
       display: block;
       margin-bottom: 5px;
       font-weight: bold;
   }
   
   input[type="text"],
   input[type="email"],
   textarea {
       width: 100%;
       padding: 10px;
       border: 1px solid #ddd;
       border-radius: 4px;
   }
   
   .submit-btn {
       display: inline-block;
       background-color: #e8491d;
       color: white;
       padding: 10px 15px;
       border: none;
       border-radius: 4px;
       cursor: pointer;
       font-size: 16px;
   }
   
   .submit-btn:hover {
       background-color: #35424a;
   }
   ```

8. **页脚样式**
   ```css
   /* 页脚样式 */
   .site-footer {
       background-color: #35424a;
       color: white;
       text-align: center;
       padding: 20px;
       margin-top: 20px;
   }
   ```

#### 实践提示
- 使用不同类型的选择器：元素选择器、类选择器、ID选择器、属性选择器
- 尝试使用组合选择器：后代选择器、子元素选择器、相邻兄弟选择器
- 注意CSS优先级规则，理解为什么某些样式会覆盖其他样式
- 检查页面在不同浏览器中的显示效果

### 3.12.2 练习题2：CSS盒模型与布局技术

#### 目标
创建一个三栏布局的页面，深入理解CSS盒模型的应用，并学习使用不同的布局技术。

#### HTML结构要求
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CSS盒模型与布局练习</title>
    <link rel="stylesheet" href="layout.css">
</head>
<body>
    <header class="page-header">
        <div class="container">
            <h1>盒模型与布局练习</h1>
        </div>
    </header>

    <div class="container">
        <div class="page-wrapper">
            <!-- 左侧边栏 -->
            <aside class="sidebar sidebar-left">
                <h3>左侧边栏</h3>
                <ul class="sidebar-menu">
                    <li class="menu-item">菜单项 1</li>
                    <li class="menu-item">菜单项 2</li>
                    <li class="menu-item">菜单项 3</li>
                    <li class="menu-item">菜单项 4</li>
                    <li class="menu-item">菜单项 5</li>
                </ul>
                
                <div class="sidebar-box">
                    <h4>关于我们</h4>
                    <p>这是一个关于CSS盒模型和布局技术的练习页面，展示如何创建灵活的页面结构。</p>
                </div>
            </aside>

            <!-- 主要内容区 -->
            <main class="content">
                <article class="article">
                    <h2>主要内容区域</h2>
                    <p>本练习将帮助你深入理解CSS盒模型的各个组成部分，以及如何使用不同的布局技术创建灵活的页面结构。</p>
                    
                    <div class="box-model-demo">
                        <h3>盒模型演示</h3>
                        <div class="box">内容区域</div>
                    </div>
                    
                    <h3>布局技术对比</h3>
                    <p>在现代Web开发中，我们有多种布局技术可以选择：</p>
                    
                    <div class="layout-comparison">
                        <div class="layout-item">
                            <h4>浮动布局</h4>
                            <p>传统的布局技术，使用float属性实现元素的水平排列。</p>
                        </div>
                        <div class="layout-item">
                            <h4>Flexbox布局</h4>
                            <p>一维布局模型，适合处理行或列的布局问题。</p>
                        </div>
                        <div class="layout-item">
                            <h4>Grid布局</h4>
                            <p>二维布局模型，可以同时处理行和列的布局问题。</p>
                        </div>
                    </div>
                    
                    <p>通过这个练习，你将学习如何使用这些布局技术创建响应式的页面结构，使网页在不同设备上都能良好显示。</p>
                </article>
            </main>

            <!-- 右侧边栏 -->
            <aside class="sidebar sidebar-right">
                <h3>右侧边栏</h3>
                
                <div class="sidebar-widget">
                    <h4>热门文章</h4>
                    <ul class="popular-posts">
                        <li class="post-item">CSS盒模型详解</li>
                        <li class="post-item">Flexbox布局指南</li>
                        <li class="post-item">Grid布局实战</li>
                        <li class="post-item">响应式设计原则</li>
                    </ul>
                </div>
                
                <div class="sidebar-widget">
                    <h4>订阅我们</h4>
                    <form class="subscribe-form">
                        <input type="email" placeholder="输入您的邮箱">
                        <button type="submit">订阅</button>
                    </form>
                </div>
                
                <div class="sidebar-widget">
                    <h4>关注我们</h4>
                    <div class="social-links">
                        <a href="#" class="social-link">微博</a>
                        <a href="#" class="social-link">微信</a>
                        <a href="#" class="social-link">GitHub</a>
                    </div>
                </div>
            </aside>
        </div>
    </div>

    <footer class="page-footer">
        <div class="container">
            <p>&copy; 2023 CSS布局练习. 保留所有权利.</p>
        </div>
    </footer>
</body>
</html>
```

#### CSS样式要求
创建一个`layout.css`文件，实现以下要求：

1. **重置样式与基础设置**
   ```css
   /* 重置默认样式 */
   * {
       margin: 0;
       padding: 0;
       box-sizing: border-box;
   }
   
   body {
       font-family: 'Arial', sans-serif;
       line-height: 1.6;
       color: #333;
       background-color: #f5f5f5;
   }
   ```

2. **容器样式**
   ```css
   /* 容器样式 - 宽度固定，水平居中 */
   .container {
       width: 1200px;
       margin: 0 auto;
       padding: 0 15px;
   }
   ```

3. **页头和页脚样式**
   ```css
   /* 页头样式 */
   .page-header {
       background-color: #2c3e50;
       color: white;
       padding: 20px 0;
       margin-bottom: 30px;
   }
   
   /* 页脚样式 */
   .page-footer {
       background-color: #2c3e50;
       color: white;
       padding: 20px 0;
       margin-top: 30px;
       text-align: center;
   }
   ```

4. **三栏布局 - 方法1：使用Flexbox**
   ```css
   /* 页面包装器 - 使用Flexbox实现三栏布局 */
   .page-wrapper {
       display: flex;
       gap: 20px;
   }
   
   /* 左侧边栏 - 宽度25% */
   .sidebar-left {
       width: 25%;
       background-color: #ecf0f1;
       padding: 20px;
       border-radius: 5px;
       border: 1px solid #bdc3c7;
   }
   
   /* 主要内容区 - 宽度50% */
   .content {
       width: 50%;
       background-color: white;
       padding: 20px;
       border-radius: 5px;
       border: 1px solid #bdc3c7;
       box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
   }
   
   /* 右侧边栏 - 宽度25% */
   .sidebar-right {
       width: 25%;
       background-color: #ecf0f1;
       padding: 20px;
       border-radius: 5px;
       border: 1px solid #bdc3c7;
   }
   ```

5. **三栏布局 - 方法2：使用Grid（可选实现）**
   ```css
   /* 可选：使用Grid实现三栏布局 */
   .page-wrapper.grid {
       display: grid;
       grid-template-columns: 25% 50% 25%;
       gap: 20px;
   }
   ```

6. **三栏布局 - 方法3：使用浮动（传统方法）**
   ```css
   /* 可选：使用浮动实现三栏布局 */
   .page-wrapper.float {
       overflow: hidden; /* 清除浮动 */
   }
   
   .page-wrapper.float .sidebar-left {
       width: 23%;
       float: left;
   }
   
   .page-wrapper.float .content {
       width: 50%;
       float: left;
   }
   
   .page-wrapper.float .sidebar-right {
       width: 23%;
       float: right;
   }
   ```

7. **盒模型演示**
   ```css
   /* 盒模型演示 */
   .box-model-demo {
       margin: 30px 0;
   }
   
   .box {
       width: 300px;
       height: 200px;
       padding: 20px;
       border: 5px solid #3498db;
       margin: 20px;
       background-color: #95a5a6;
       color: white;
       text-align: center;
       line-height: 160px; /* 垂直居中内容 */
       font-size: 18px;
       font-weight: bold;
   }
   ```

8. **内部内容样式**
   ```css
   /* 文章样式 */
   .article h2 {
       color: #2c3e50;
       margin-bottom: 20px;
       padding-bottom: 10px;
       border-bottom: 1px solid #ecf0f1;
   }
   
   .article p {
       margin-bottom: 15px;
   }
   
   /* 布局对比容器 */
   .layout-comparison {
       display: flex;
       gap: 15px;
       margin: 20px 0;
   }
   
   .layout-item {
       flex: 1;
       padding: 15px;
       background-color: #f8f9fa;
       border-radius: 5px;
       border: 1px solid #dee2e6;
   }
   
   .layout-item h4 {
       color: #3498db;
       margin-bottom: 10px;
   }
   ```

9. **侧边栏内容样式**
   ```css
   /* 侧边栏标题 */
   .sidebar h3 {
       color: #2c3e50;
       margin-bottom: 15px;
       padding-bottom: 10px;
       border-bottom: 1px solid #bdc3c7;
   }
   
   /* 侧边栏菜单 */
   .sidebar-menu {
       list-style: none;
       margin-bottom: 20px;
   }
   
   .menu-item {
       padding: 10px;
       border-bottom: 1px solid #bdc3c7;
   }
   
   .menu-item:hover {
       background-color: #d5dbdb;
       cursor: pointer;
   }
   
   /* 侧边栏小部件 */
   .sidebar-widget {
       margin-bottom: 25px;
       padding-bottom: 20px;
       border-bottom: 1px solid #bdc3c7;
   }
   
   .sidebar-widget:last-child {
       border-bottom: none;
       margin-bottom: 0;
       padding-bottom: 0;
   }
   
   .sidebar-widget h4 {
       color: #3498db;
       margin-bottom: 10px;
   }
   
   /* 热门文章列表 */
   .popular-posts {
       list-style: none;
   }
   
   .post-item {
       padding: 8px 0;
       border-bottom: 1px dashed #bdc3c7;
   }
   
   .post-item:last-child {
       border-bottom: none;
   }
   
   /* 订阅表单 */
   .subscribe-form input {
       width: 100%;
       padding: 8px;
       margin-bottom: 10px;
       border: 1px solid #bdc3c7;
       border-radius: 4px;
   }
   
   .subscribe-form button {
       width: 100%;
       padding: 8px;
       background-color: #3498db;
       color: white;
       border: none;
       border-radius: 4px;
       cursor: pointer;
   }
   
   /* 社交链接 */
   .social-links {
       display: flex;
       gap: 10px;
   }
   
   .social-link {
       padding: 5px 10px;
       background-color: #3498db;
       color: white;
       text-decoration: none;
       border-radius: 4px;
   }
   ```

10. **响应式调整**
    ```css
    /* 媒体查询 - 确保在窗口变小时，布局能够优雅地降级为垂直排列 */
    @media (max-width: 1200px) {
        .container {
            width: 100%;
        }
    }
    
    @media (max-width: 992px) {
        /* 三栏布局变为两栏，右侧边栏放到下方 */
        .page-wrapper {
            flex-direction: column;
        }
        
        .sidebar-left,
        .content,
        .sidebar-right {
            width: 100%;
            margin-bottom: 20px;
        }
        
        /* 恢复最后一个元素的margin */
        .sidebar-right {
            margin-bottom: 0;
        }
        
        /* 布局对比容器调整 */
        .layout-comparison {
            flex-direction: column;
        }
    }
    
    @media (max-width: 768px) {
        /* 移动设备上的额外调整 */
        .container {
            padding: 0 10px;
        }
        
        .box {
            width: 100%;
            margin: 20px 0;
        }
    }
    ```

#### 实践提示
- 尝试使用不同的布局方法（Flexbox、Grid、浮动）实现相同的布局效果
- 观察不同布局方法的优缺点
- 使用浏览器开发者工具检查盒模型各个部分（内容、内边距、边框、外边距）
- 测试页面在不同屏幕尺寸下的表现
- 尝试修改各个部分的内边距、外边距和边框，观察对整体布局的影响

### 3.12.3 练习题3：CSS响应式设计与交互效果

#### 目标
创建一个完全响应式的网页，包含导航栏、卡片布局和页脚，并实现交互效果。

#### HTML结构要求
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CSS响应式设计练习</title>
    <link rel="stylesheet" href="responsive.css">
    <!-- 引入Font Awesome图标库（可选，用于菜单图标） -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
</head>
<body>
    <!-- 页头和导航 -->
    <header class="site-header">
        <div class="container">
            <div class="header-content">
                <div class="logo">
                    <h1>响应式设计</h1>
                </div>
                
                <!-- 移动端菜单按钮 -->
                <button class="menu-toggle" id="menu-toggle">
                    <i class="fas fa-bars"></i>
                </button>
                
                <!-- 桌面导航 -->
                <nav class="main-nav" id="main-nav">
                    <ul class="nav-menu">
                        <li class="nav-item"><a href="#" class="nav-link active">首页</a></li>
                        <li class="nav-item"><a href="#features" class="nav-link">功能</a></li>
                        <li class="nav-item"><a href="#services" class="nav-link">服务</a></li>
                        <li class="nav-item"><a href="#gallery" class="nav-link">作品展示</a></li>
                        <li class="nav-item"><a href="#contact" class="nav-link">联系我们</a></li>
                    </ul>
                </nav>
            </div>
        </div>
    </header>

    <!-- 英雄区域 -->
    <section class="hero">
        <div class="container">
            <div class="hero-content">
                <h2>响应式网页设计</h2>
                <p>在任何设备上都能完美展示的现代网页设计</p>
                <a href="#features" class="btn btn-primary">了解更多</a>
            </div>
        </div>
    </section>

    <!-- 功能区域 -->
    <section class="features" id="features">
        <div class="container">
            <h2 class="section-title">主要功能</h2>
            <p class="section-subtitle">我们的响应式设计提供以下核心功能</p>
            
            <div class="features-grid">
                <!-- 功能卡片 1 -->
                <div class="feature-card">
                    <div class="feature-icon">
                        <i class="fas fa-mobile-alt"></i>
                    </div>
                    <h3>移动优先设计</h3>
                    <p>从移动设备开始设计，确保在各种屏幕尺寸上都有最佳体验。</p>
                </div>
                
                <!-- 功能卡片 2 -->
                <div class="feature-card">
                    <div class="feature-icon">
                        <i class="fas fa-tablet-alt"></i>
                    </div>
                    <h3>自适应布局</h3>
                    <p>网页布局会根据设备屏幕尺寸自动调整，提供最佳的浏览体验。</p>
                </div>
                
                <!-- 功能卡片 3 -->
                <div class="feature-card">
                    <div class="feature-icon">
                        <i class="fas fa-desktop"></i>
                    </div>
                    <h3>桌面优化</h3>
                    <p>在大屏幕设备上提供丰富的视觉体验和更多的内容展示空间。</p>
                </div>
                
                <!-- 功能卡片 4 -->
                <div class="feature-card">
                    <div class="feature-icon">
                        <i class="fas fa-paint-brush"></i>
                    </div>
                    <h3>现代设计</h3>
                    <p>采用最新的设计趋势，创造出视觉吸引力强的用户界面。</p>
                </div>
                
                <!-- 功能卡片 5 -->
                <div class="feature-card">
                    <div class="feature-icon">
                        <i class="fas fa-bolt"></i>
                    </div>
                    <h3>性能优化</h3>
                    <p>优化代码和资源加载，确保网页在各种网络条件下都能快速加载。</p>
                </div>
                
                <!-- 功能卡片 6 -->
                <div class="feature-card">
                    <div class="feature-icon">
                        <i class="fas fa-universal-access"></i>
                    </div>
                    <h3>无障碍设计</h3>
                    <p>遵循Web无障碍标准，确保所有用户都能便捷地使用网站。</p>
                </div>
            </div>
        </div>
    </section>

    <!-- 服务区域 -->
    <section class="services" id="services">
        <div class="container">
            <h2 class="section-title">我们的服务</h2>
            <p class="section-subtitle">专业的Web设计与开发服务</p>
            
            <div class="services-container">
                <!-- 服务项目 1 -->
                <div class="service-item">
                    <div class="service-image">
                        <img src="https://via.placeholder.com/600x400" alt="网站设计服务">
                    </div>
                    <div class="service-content">
                        <h3>网站设计</h3>
                        <p>为您的企业创建独特、专业的网站设计，展现品牌价值和吸引目标客户。</p>
                    </div>
                </div>
                
                <!-- 服务项目 2 -->
                <div class="service-item service-item-reverse">
                    <div class="service-image">
                        <img src="https://via.placeholder.com/600x400" alt="前端开发服务">
                    </div>
                    <div class="service-content">
                        <h3>前端开发</h3>
                        <p>使用最新的Web技术，将设计转化为功能齐全、交互丰富的网站。</p>
                    </div>
                </div>
                
                <!-- 服务项目 3 -->
                <div class="service-item">
                    <div class="service-image">
                        <img src="https://via.placeholder.com/600x400" alt="响应式开发服务">
                    </div>
                    <div class="service-content">
                        <h3>响应式开发</h3>
                        <p>确保您的网站在任何设备上都能完美展示，提供一致的用户体验。</p>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- 作品展示 -->
    <section class="gallery" id="gallery">
        <div class="container">
            <h2 class="section-title">作品展示</h2>
            <p class="section-subtitle">我们的精选项目</p>
            
            <div class="gallery-grid">
                <!-- 作品 1 -->
                <div class="gallery-item">
                    <div class="gallery-image">
                        <img src="https://via.placeholder.com/400x300" alt="项目1">
                        <div class="gallery-overlay">
                            <h3>电子商务网站</h3>
                            <a href="#" class="btn btn-secondary">查看详情</a>
                        </div>
                    </div>
                </div>
                
                <!-- 作品 2 -->
                <div class="gallery-item">
                    <div class="gallery-image">
                        <img src="https://via.placeholder.com/400x300" alt="项目2">
                        <div class="gallery-overlay">
                            <h3>企业官网</h3>
                            <a href="#" class="btn btn-secondary">查看详情</a>
                        </div>
                    </div>
                </div>
                
                <!-- 作品 3 -->
                <div class="gallery-item">
                    <div class="gallery-image">
                        <img src="https://via.placeholder.com/400x300" alt="项目3">
                        <div class="gallery-overlay">
                            <h3>教育平台</h3>
                            <a href="#" class="btn btn-secondary">查看详情</a>
                        </div>
                    </div>
                </div>
                
                <!-- 作品 4 -->
                <div class="gallery-item">
                    <div class="gallery-image">
                        <img src="https://via.placeholder.com/400x300" alt="项目4">
                        <div class="gallery-overlay">
                            <h3>旅游网站</h3>
                            <a href="#" class="btn btn-secondary">查看详情</a>
                        </div>
                    </div>
                </div>
                
                <!-- 作品 5 -->
                <div class="gallery-item">
                    <div class="gallery-image">
                        <img src="https://via.placeholder.com/400x300" alt="项目5">
                        <div class="gallery-overlay">
                            <h3>博客平台</h3>
                            <a href="#" class="btn btn-secondary">查看详情</a>
                        </div>
                    </div>
                </div>
                
                <!-- 作品 6 -->
                <div class="gallery-item">
                    <div class="gallery-image">
                        <img src="https://via.placeholder.com/400x300" alt="项目6">
                        <div class="gallery-overlay">
                            <h3>社交媒体应用</h3>
                            <a href="#" class="btn btn-secondary">查看详情</a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- 联系区域 -->
    <section class="contact" id="contact">
        <div class="container">
            <h2 class="section-title">联系我们</h2>
            <p class="section-subtitle">有任何问题？请随时联系我们</p>
            
            <div class="contact-container">
                <div class="contact-form">
                    <form>
                        <div class="form-group">
                            <label for="name">姓名:</label>
                            <input type="text" id="name" name="name" placeholder="请输入您的姓名">
                        </div>
                        <div class="form-group">
                            <label for="email">邮箱:</label>
                            <input type="email" id="email" name="email" placeholder="请输入您的邮箱">
                        </div>
                        <div class="form-group">
                            <label for="subject">主题:</label>
                            <input type="text" id="subject" name="subject" placeholder="请输入主题">
                        </div>
                        <div class="form-group">
                            <label for="message">留言:</label>
                            <textarea id="message" name="message" rows="5" placeholder="请输入您的留言"></textarea>
                        </div>
                        <button type="submit" class="btn btn-primary">发送留言</button>
                    </form>
                </div>
                
                <div class="contact-info">
                    <div class="info-item">
                        <i class="fas fa-map-marker-alt"></i>
                        <span>北京市海淀区中关村大街1号</span>
                    </div>
                    <div class="info-item">
                        <i class="fas fa-phone"></i>
                        <span>+86 123 4567 8910</span>
                    </div>
                    <div class="info-item">
                        <i class="fas fa-envelope"></i>
                        <span>info@example.com</span>
                    </div>
                    
                    <div class="social-media">
                        <h3>关注我们</h3>
                        <a href="#" class="social-link"><i class="fab fa-weibo"></i></a>
                        <a href="#" class="social-link"><i class="fab fa-weixin"></i></a>
                        <a href="#" class="social-link"><i class="fab fa-github"></i></a>
                        <a href="#" class="social-link"><i class="fab fa-linkedin"></i></a>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- 页脚 -->
    <footer class="site-footer">
        <div class="container">
            <div class="footer-content">
                <div class="footer-info">
                    <h3>响应式设计</h3>
                    <p>为现代Web提供高质量的设计与开发服务</p>
                </div>
                
                <div class="footer-links">
                    <h4>快速链接</h4>
                    <ul>
                        <li><a href="#">首页</a></li>
                        <li><a href="#features">功能</a></li>
                        <li><a href="#services">服务</a></li>
                        <li><a href="#gallery">作品展示</a></li>
                        <li><a href="#contact">联系我们</a></li>
                    </ul>
                </div>
                
                <div class="footer-newsletter">
                    <h4>订阅通讯</h4>
                    <p>订阅我们的通讯，获取最新资讯和优惠</p>
                    <form class="newsletter-form">
                        <input type="email" placeholder="您的邮箱地址">
                        <button type="submit">订阅</button>
                    </form>
                </div>
            </div>
            
            <div class="footer-bottom">
                <p>&copy; 2023 响应式设计. 保留所有权利.</p>
            </div>
        </div>
    </footer>

    <!-- 移动端菜单JavaScript -->
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const menuToggle = document.getElementById('menu-toggle');
            const mainNav = document.getElementById('main-nav');
            
            menuToggle.addEventListener('click', function() {
                mainNav.classList.toggle('active');
                
                // 切换菜单图标
                const icon = menuToggle.querySelector('i');
                if (icon.classList.contains('fa-bars')) {
                    icon.classList.remove('fa-bars');
                    icon.classList.add('fa-times');
                } else {
                    icon.classList.remove('fa-times');
                    icon.classList.add('fa-bars');
                }
            });
        });
    </script>
</body>
</html>
```

#### CSS样式要求
创建一个`responsive.css`文件，实现以下要求：

1. **重置样式与基础设置**
   ```css
   /* 重置默认样式 */
   * {
       margin: 0;
       padding: 0;
       box-sizing: border-box;
   }
   
   :root {
       --primary-color: #3498db;
       --secondary-color: #2c3e50;
       --accent-color: #e74c3c;
       --text-color: #333;
       --light-text: #7f8c8d;
       --background-color: #fff;
       --light-bg: #f5f5f5;
       --border-color: #ddd;
       --transition: all 0.3s ease;
   }
   
   body {
       font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
       line-height: 1.6;
       color: var(--text-color);
       background-color: var(--background-color);
       overflow-x: hidden;
   }
   
   a {
       color: var(--primary-color);
       text-decoration: none;
       transition: var(--transition);
   }
   
   a:hover {
       color: var(--accent-color);
   }
   
   ul {
       list-style: none;
   }
   
   .container {
       width: 100%;
       max-width: 1200px;
       margin: 0 auto;
       padding: 0 20px;
   }
   
   /* 按钮样式 */
   .btn {
       display: inline-block;
       padding: 12px 25px;
       border: none;
       border-radius: 5px;
       font-size: 16px;
       font-weight: 500;
       cursor: pointer;
       transition: var(--transition);
       text-align: center;
   }
   
   .btn-primary {
       background-color: var(--primary-color);
       color: white;
   }
   
   .btn-primary:hover {
       background-color: #2980b9;
       color: white;
   }
   
   .btn-secondary {
       background-color: transparent;
       color: white;
       border: 2px solid white;
   }
   
   .btn-secondary:hover {
       background-color: white;
       color: var(--primary-color);
   }
   
   /* 标题样式 */
   h1, h2, h3, h4, h5, h6 {
       margin-bottom: 15px;
       font-weight: 600;
       line-height: 1.2;
   }
   
   .section-title {
       font-size: 2.5rem;
       color: var(--secondary-color);
       text-align: center;
       margin-bottom: 15px;
   }
   
   .section-subtitle {
       font-size: 1.1rem;
       color: var(--light-text);
       text-align: center;
       margin-bottom: 50px;
   }
   ```

2. **头部和导航样式**
   ```css
   /* 页头样式 */
   .site-header {
       background-color: white;
       box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
       position: sticky;
       top: 0;
       z-index: 1000;
   }
   
   .header-content {
       display: flex;
       justify-content: space-between;
       align-items: center;
       padding: 20px 0;
   }
   
   .logo h1 {
       font-size: 1.8rem;
       margin: 0;
       color: var(--secondary-color);
   }
   
   /* 桌面导航 */
   .main-nav {
       display: block;
   }
   
   .nav-menu {
       display: flex;
       gap: 20px;
   }
   
   .nav-link {
       color: var(--text-color);
       font-weight: 500;
       font-size: 16px;
       position: relative;
       padding: 5px 0;
   }
   
   .nav-link.active,
   .nav-link:hover {
       color: var(--primary-color);
   }
   
   .nav-link::after {
       content: '';
       position: absolute;
       width: 0;
       height: 2px;
       bottom: 0;
       left: 0;
       background-color: var(--primary-color);
       transition: var(--transition);
   }
   
   .nav-link:hover::after,
   .nav-link.active::after {
       width: 100%;
   }
   
   /* 移动端菜单按钮 */
   .menu-toggle {
       display: none;
       background: none;
       border: none;
       font-size: 1.5rem;
       color: var(--text-color);
       cursor: pointer;
   }
   ```

3. **英雄区域样式**
   ```css
   /* 英雄区域 */
   .hero {
       background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
       color: white;
       padding: 100px 0;
       text-align: center;
   }
   
   .hero-content h2 {
       font-size: 3rem;
       margin-bottom: 20px;
   }
   
   .hero-content p {
       font-size: 1.2rem;
       margin-bottom: 30px;
       max-width: 700px;
       margin-left: auto;
       margin-right: auto;
   }
   ```

4. **功能区域样式**
   ```css
   /* 功能区域 */
   .features {
       padding: 100px 0;
       background-color: var(--background-color);
   }
   
   .features-grid {
       display: grid;
       grid-template-columns: repeat(3, 1fr);
       gap: 30px;
   }
   
   .feature-card {
       background-color: white;
       padding: 30px;
       border-radius: 10px;
       box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
       transition: var(--transition);
       text-align: center;
   }
   
   .feature-card:hover {
       transform: translateY(-5px);
       box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
   }
   
   .feature-icon {
       width: 80px;
       height: 80px;
       background-color: rgba(52, 152, 219, 0.1);
       border-radius: 50%;
       display: flex;
       align-items: center;
       justify-content: center;
       margin: 0 auto 20px;
       font-size: 1.8rem;
       color: var(--primary-color);
   }
   
   .feature-card h3 {
       font-size: 1.4rem;
       margin-bottom: 15px;
       color: var(--secondary-color);
   }
   ```

5. **服务区域样式**
   ```css
   /* 服务区域 */
   .services {
       padding: 100px 0;
       background-color: var(--light-bg);
   }
   
   .service-item {
       display: flex;
       margin-bottom: 50px;
       background-color: white;
       border-radius: 10px;
       overflow: hidden;
       box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
       transition: var(--transition);
   }
   
   .service-item:hover {
       box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
   }
   
   .service-item:last-child {
       margin-bottom: 0;
   }
   
   .service-image {
       width: 40%;
       overflow: hidden;
   }
   
   .service-image img {
       width: 100%;
       height: 100%;
       object-fit: cover;
       transition: transform 0.5s ease;
   }
   
   .service-item:hover .service-image img {
       transform: scale(1.05);
   }
   
   .service-content {
       width: 60%;
       padding: 40px;
   }
   
   .service-content h3 {
       font-size: 1.8rem;
       margin-bottom: 15px;
       color: var(--secondary-color);
   }
   
   .service-item-reverse {
       flex-direction: row-reverse;
   }
   ```

6. **作品展示区域样式**
   ```css
   /* 作品展示区域 */
   .gallery {
       padding: 100px 0;
       background-color: var(--background-color);
   }
   
   .gallery-grid {
       display: grid;
       grid-template-columns: repeat(3, 1fr);
       gap: 20px;
   }
   
   .gallery-item {
       position: relative;
       overflow: hidden;
       border-radius: 10px;
   }
   
   .gallery-image {
       position: relative;
       overflow: hidden;
   }
   
   .gallery-image img {
       width: 100%;
       height: auto;
       display: block;
       transition: transform 0.5s ease;
   }
   
   .gallery-overlay {
       position: absolute;
       top: 0;
       left: 0;
       width: 100%;
       height: 100%;
       background-color: rgba(44, 62, 80, 0.8);
       display: flex;
       flex-direction: column;
       align-items: center;
       justify-content: center;
       opacity: 0;
       transition: var(--transition);
       text-align: center;
       padding: 20px;
   }
   
   .gallery-item:hover .gallery-overlay {
       opacity: 1;
   }
   
   .gallery-item:hover .gallery-image img {
       transform: scale(1.1);
   }
   
   .gallery-overlay h3 {
       color: white;
       margin-bottom: 15px;
   }
   ```

7. **联系区域样式**
   ```css
   /* 联系区域 */
   .contact {
       padding: 100px 0;
       background-color: var(--light-bg);
   }
   
   .contact-container {
       display: grid;
       grid-template-columns: 1fr 1fr;
       gap: 40px;
   }
   
   .contact-form {
       background-color: white;
       padding: 30px;
       border-radius: 10px;
       box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
   }
   
   .form-group {
       margin-bottom: 20px;
   }
   
   .form-group label {
       display: block;
       margin-bottom: 8px;
       font-weight: 500;
       color: var(--secondary-color);
   }
   
   .form-group input,
   .form-group textarea {
       width: 100%;
       padding: 12px;
       border: 1px solid var(--border-color);
       border-radius: 5px;
       font-size: 16px;
       transition: var(--transition);
   }
   
   .form-group input:focus,
   .form-group textarea:focus {
       outline: none;
       border-color: var(--primary-color);
       box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
   }
   
   .contact-info {
       background-color: var(--secondary-color);
       color: white;
       padding: 30px;
       border-radius: 10px;
   }
   
   .contact-info h3 {
       margin-bottom: 20px;
   }
   
   .info-item {
       display: flex;
       align-items: center;
       margin-bottom: 20px;
   }
   
   .info-item i {
       width: 40px;
       height: 40px;
       background-color: rgba(255, 255, 255, 0.1);
       border-radius: 50%;
       display: flex;
       align-items: center;
       justify-content: center;
       margin-right: 15px;
       font-size: 1.1rem;
   }
   
   .social-media {
       margin-top: 30px;
   }
   
   .social-media h3 {
       margin-bottom: 15px;
   }
   
   .social-link {
       display: inline-flex;
       align-items: center;
       justify-content: center;
       width: 40px;
       height: 40px;
       background-color: rgba(255, 255, 255, 0.1);
       border-radius: 50%;
       color: white;
       margin-right: 10px;
       transition: var(--transition);
   }
   
   .social-link:hover {
       background-color: var(--primary-color);
       color: white;
   }
   ```

8. **页脚样式**
   ```css
   /* 页脚样式 */
   .site-footer {
       background-color: var(--secondary-color);
       color: white;
       padding: 70px 0 30px;
   }
   
   .footer-content {
       display: grid;
       grid-template-columns: repeat(3, 1fr);
       gap: 40px;
       margin-bottom: 40px;
   }
   
   .footer-info h3 {
       font-size: 1.5rem;
       margin-bottom: 20px;
   }
   
   .footer-links h4,
   .footer-newsletter h4 {
       font-size: 1.2rem;
       margin-bottom: 20px;
   }
   
   .footer-links ul li {
       margin-bottom: 10px;
   }
   
   .footer-links a {
       color: rgba(255, 255, 255, 0.7);
   }
   
   .footer-links a:hover {
       color: white;
       padding-left: 5px;
   }
   
   .newsletter-form {
       display: flex;
       margin-top: 15px;
   }
   
   .newsletter-form input {
       flex: 1;
       padding: 10px 15px;
       border: none;
       border-radius: 5px 0 0 5px;
       font-size: 16px;
   }
   
   .newsletter-form button {
       padding: 10px 20px;
       background-color: var(--primary-color);
       color: white;
       border: none;
       border-radius: 0 5px 5px 0;
       cursor: pointer;
       transition: var(--transition);
   }
   
   .newsletter-form button:hover {
       background-color: #2980b9;
   }
   
   .footer-bottom {
       text-align: center;
       padding-top: 30px;
       border-top: 1px solid rgba(255, 255, 255, 0.1);
   }
   ```

9. **响应式设计 - 大屏设备（≥1200px）**
   ```css
   /* 大屏设备默认样式已在上述代码中定义 */
   /* 三列卡片并排显示 */
   ```

10. **响应式设计 - 中等屏幕（992px-1199px）**
    ```css
    @media (max-width: 1199px) {
        /* 调整容器宽度 */
        .container {
            max-width: 960px;
        }
        
        /* 三列卡片保持并排，但宽度自适应 */
        .features-grid,
        .gallery-grid {
            grid-template-columns: repeat(3, 1fr);
        }
        
        /* 调整标题大小 */
        .section-title {
            font-size: 2.2rem;
        }
        
        .hero-content h2 {
            font-size: 2.8rem;
        }
    }
    ```

11. **响应式设计 - 平板设备（768px-991px）**
    ```css
    @media (max-width: 991px) {
        /* 调整容器宽度 */
        .container {
            max-width: 720px;
        }
        
        /* 改为两列卡片布局 */
        .features-grid,
        .gallery-grid,
        .footer-content {
            grid-template-columns: repeat(2, 1fr);
        }
        
        /* 联系区域改为单列 */
        .contact-container {
            grid-template-columns: 1fr;
        }
        
        /* 服务项目改为垂直排列 */
        .service-item,
        .service-item-reverse {
            flex-direction: column;
        }
        
        .service-image,
        .service-content {
            width: 100%;
        }
        
        /* 调整标题大小 */
        .section-title {
            font-size: 2rem;
        }
        
        .hero-content h2 {
            font-size: 2.5rem;
        }
    }
    ```

12. **响应式设计 - 移动设备（<768px）**
    ```css
    @media (max-width: 767px) {
        /* 调整容器宽度 */
        .container {
            max-width: 540px;
            padding: 0 15px;
        }
        
        /* 显示移动端菜单按钮 */
        .menu-toggle {
            display: block;
        }
        
        /* 隐藏桌面导航 */
        .main-nav {
            position: fixed;
            top: 70px;
            left: 0;
            width: 100%;
            background-color: white;
            box-shadow: 0 5px 10px rgba(0, 0, 0, 0.1);
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.3s ease;
        }
        
        /* 激活状态显示菜单 */
        .main-nav.active {
            max-height: 300px;
        }
        
        /* 移动端菜单样式 */
        .nav-menu {
            flex-direction: column;
            padding: 20px;
            gap: 10px;
        }
        
        .nav-item {
            width: 100%;
        }
        
        /* 改为单列卡片布局 */
        .features-grid,
        .gallery-grid,
        .footer-content {
            grid-template-columns: 1fr;
        }
        
        /* 调整标题大小 */
        .section-title {
            font-size: 1.8rem;
        }
        
        .hero-content h2 {
            font-size: 2rem;
        }
        
        /* 调整内容区域内边距 */
        .features,
        .services,
        .gallery,
        .contact {
            padding: 70px 0;
        }
        
        /* 调整按钮样式 */
        .btn {
            padding: 10px 20px;
            font-size: 14px;
        }
        
        /* 调整服务内容内边距 */
        .service-content {
            padding: 30px;
        }
        
        /* 调整订阅表单为垂直排列 */
        .newsletter-form {
            flex-direction: column;
        }
        
        .newsletter-form input,
        .newsletter-form button {
            width: 100%;
            border-radius: 5px;
            margin-bottom: 10px;
        }
        
        .newsletter-form button {
            margin-bottom: 0;
        }
    }
    ```

13. **响应式设计 - 小屏幕移动设备（<576px）**
    ```css
    @media (max-width: 575px) {
        /* 进一步调整标题大小 */
        .section-title {
            font-size: 1.6rem;
        }
        
        .hero-content h2 {
            font-size: 1.8rem;
        }
        
        /* 调整英雄区域高度 */
        .hero {
            padding: 80px 0;
        }
        
        /* 调整服务内容内边距 */
        .service-content {
            padding: 20px;
        }
        
        /* 调整联系表单和信息内边距 */
        .contact-form,
        .contact-info {
            padding: 20px;
        }
    }
    ```

#### 实践提示
- 测试页面在不同设备和屏幕尺寸下的表现
- 特别注意导航栏在移动设备上的汉堡菜单效果
- 观察卡片布局如何根据屏幕尺寸从三列变为两列再变为单列
- 检查图片和内容在各种屏幕尺寸下是否正常显示
- 尝试添加更多的交互效果，如滚动动画、悬停效果等
- 使用浏览器开发者工具的设备模拟功能来测试响应式设计

## 学习资源

### 在线文档

- [MDN Web Docs - CSS](https://developer.mozilla.org/zh-CN/docs/Web/CSS)
- [W3Schools CSS 教程](https://www.w3school.com.cn/css/index.asp)
- [CSS 参考手册 - 阮一峰](https://www.ruanyifeng.com/blog/2010/05/css_reference.html)

### 视频教程

- [HTML/CSS/JavaScript 教程](https://www.bilibili.com/video/BV1Cv41167aK)
- [CSS 高级特性实战](https://www.imooc.com/learn/1215)

### 互动学习平台

- [CSS Diner](https://flukeout.github.io/) - CSS选择器游戏
- [Flexbox Froggy](https://flexboxfroggy.com/) - Flexbox布局游戏
- [Grid Garden](https://cssgridgarden.com/) - CSS Grid布局游戏

### 工具

- [Can I Use](https://caniuse.com/) - 检查CSS特性的浏览器兼容性
- [CSS Validator](https://jigsaw.w3.org/css-validator/) - CSS代码验证工具
- [CSS Scan](https://getcssscan.com/css-selector-tester) - CSS选择器测试工具

---

本章介绍了CSS的基础知识，包括语法、选择器、优先级、盒模型、颜色、字体、布局技术等。这些是前端开发的基础，熟练掌握这些知识将帮助你创建美观、响应式的网页。在下一章中，我们将深入学习JavaScript基础知识，进一步提升前端开发能力。