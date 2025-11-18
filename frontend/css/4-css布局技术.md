# CSS布局技术

## 4.1 布局基础概念

### 4.1.1 什么是CSS布局？

CSS布局是指如何在网页中排列和组织HTML元素的技术。它决定了元素在页面上的位置、大小和相互关系。良好的布局对于创建美观、功能性强且响应式的网页至关重要。

### 4.1.2 CSS布局的演变

CSS布局技术随着Web的发展而不断演变，大致经历了以下几个阶段：

1. **表格布局** - 早期Web开发中使用表格进行页面布局，但这不符合语义化要求，且难以维护
2. **浮动布局** - CSS2引入的浮动技术，成为多年来网页布局的主要方式
3. **定位布局** - 使用position属性进行精确位置控制
4. **Flexbox布局** - CSS3引入的一维弹性布局，解决了许多传统布局的问题
5. **Grid布局** - CSS3引入的二维网格布局，提供了更强大和灵活的布局能力

### 4.1.3 布局模式的选择

在实际开发中，选择合适的布局模式取决于具体需求：

- **简单内容布局** - 可以使用基本的文档流和内联/块级元素特性
- **多列布局** - 可以使用浮动、Flexbox或Grid
- **响应式布局** - Flexbox和Grid结合媒体查询是现代响应式设计的首选
- **复杂网格布局** - Grid布局提供了最强大的二维布局能力
- **组件内部布局** - Flexbox对于组件内部的一维布局非常适合

## 4.2 文档流与基本布局

### 4.2.1 文档流的概念

文档流是指HTML元素在页面上默认的排列方式。在标准文档流中，元素按照它们在HTML中的出现顺序从上到下、从左到右排列。

### 4.2.2 块级元素与行内元素

HTML元素根据其显示特性可以分为块级元素和行内元素，它们在文档流中的表现不同：

**块级元素（Block-level Elements）**
- 独占一行空间
- 可以设置宽度、高度、内边距和外边距
- 常见的块级元素：`div`, `p`, `h1`-`h6`, `ul`, `ol`, `li`, `form`, `header`, `footer`, `section`等

**行内元素（Inline Elements）**
- 不会独占一行，多个行内元素可以在同一行显示
- 不能设置宽度、高度，垂直方向的内边距和外边距不会影响行高
- 水平方向的内边距和外边距有效
- 常见的行内元素：`span`, `a`, `strong`, `em`, `img`, `input`, `button`等

**行内块元素（Inline-block Elements）**
- 兼具行内元素和块级元素的特性
- 不会独占一行
- 可以设置宽度、高度、内边距和外边距
- 通过`display: inline-block`设置

### 4.2.3 display属性

`display`属性决定了元素的显示类型，是控制布局的基础属性之一。

**常用值：**
- `block` - 块级元素
- `inline` - 行内元素
- `inline-block` - 行内块元素
- `none` - 隐藏元素
- `flex` - 弹性容器
- `grid` - 网格容器
- `table`, `table-cell` - 表格布局相关
- `list-item` - 列表项

**示例：**
```css
/* 基本显示类型 */
.block-element {
    display: block;
}

.inline-element {
    display: inline;
}

.inline-block-element {
    display: inline-block;
}

.hidden-element {
    display: none;
}

/* 现代布局显示类型 */
.flex-container {
    display: flex;
}

.grid-container {
    display: grid;
}
```

## 4.3 浮动布局

### 4.3.1 浮动的基本概念

浮动（float）是CSS中一种使元素脱离正常文档流，并使其向左或向右移动，直到其边缘碰到包含块或另一个浮动元素的边缘的技术。

浮动最初是为了实现文本围绕图片的效果而设计的，但后来被广泛用于创建多列布局。

### 4.3.2 float属性

**语法：**
```css
float: none | left | right | inherit;
```

**属性值：**
- `none` - 默认值，元素不浮动
- `left` - 元素向左浮动
- `right` - 元素向右浮动
- `inherit` - 继承父元素的float值

**示例：**
```css
.float-left {
    float: left;
    width: 300px;
    margin-right: 20px;
}

.float-right {
    float: right;
    width: 200px;
    margin-left: 20px;
}
```

### 4.3.3 浮动的特性

1. **脱离文档流** - 浮动元素会脱离正常文档流，但不会完全脱离（与绝对定位不同）
2. **文本环绕** - 普通文档流中的文本会环绕浮动元素
3. **包含块限制** - 浮动元素不会超出其包含块
4. **高度塌陷** - 父元素如果没有设置高度，其高度会塌陷（不包含浮动子元素）
5. **水平排列** - 多个浮动元素会在同一行水平排列，直到空间不足时换行

### 4.3.4 清除浮动

当元素浮动时，父元素可能会出现高度塌陷的问题，需要清除浮动来修复布局。

**clear属性：**
```css
clear: none | left | right | both | inherit;
```

**清除浮动的方法：**

**方法1：在浮动元素后添加清除元素**
```html
<div class="container">
    <div class="float-left">左侧浮动元素</div>
    <div class="float-right">右侧浮动元素</div>
    <div class="clear"></div> <!-- 清除元素 -->
</div>

<style>
.clear {
    clear: both;
}
</style>
```

**方法2：使用overflow属性**
```css
.container {
    overflow: auto; /* 或 hidden, scroll */
    zoom: 1; /* 为IE6添加 */
}
```

**方法3：使用伪元素清除浮动（推荐）**
```css
.clearfix::after {
    content: "";
    display: table;
    clear: both;
}

.clearfix {
    *zoom: 1; /* 为IE6-7添加 */
}
```

### 4.3.5 浮动布局示例

**示例1：两列布局**
```html
<div class="container">
    <div class="sidebar">侧边栏</div>
    <div class="main">主要内容</div>
</div>

<style>
.container {
    width: 100%;
    max-width: 1200px;
    margin: 0 auto;
}

.sidebar {
    float: left;
    width: 300px;
    height: 500px;
    background-color: #f1f1f1;
}

.main {
    margin-left: 320px;
    height: 500px;
    background-color: #e9e9e9;
}

/* 或者使用浮动实现 */
/* .main {
    float: left;
    width: calc(100% - 320px);
    margin-left: 20px;
    height: 500px;
    background-color: #e9e9e9;
}

.container::after {
    content: "";
    display: table;
    clear: both;
} */
</style>
```

**示例2：三列布局**
```html
<div class="container">
    <div class="left-sidebar">左侧边栏</div>
    <div class="main">主要内容</div>
    <div class="right-sidebar">右侧边栏</div>
</div>

<style>
.container {
    width: 100%;
    max-width: 1200px;
    margin: 0 auto;
}

.left-sidebar {
    float: left;
    width: 250px;
    height: 500px;
    background-color: #f1f1f1;
}

.main {
    float: left;
    width: 660px;
    margin: 0 20px;
    height: 500px;
    background-color: #e9e9e9;
}

.right-sidebar {
    float: left;
    width: 250px;
    height: 500px;
    background-color: #f1f1f1;
}

.container::after {
    content: "";
    display: table;
    clear: both;
}
</style>
```

**示例3：图片库布局**
```html
<div class="gallery">
    <div class="gallery-item"><img src="image1.jpg" alt="图片1"></div>
    <div class="gallery-item"><img src="image2.jpg" alt="图片2"></div>
    <div class="gallery-item"><img src="image3.jpg" alt="图片3"></div>
    <div class="gallery-item"><img src="image4.jpg" alt="图片4"></div>
    <div class="gallery-item"><img src="image5.jpg" alt="图片5"></div>
    <div class="gallery-item"><img src="image6.jpg" alt="图片6"></div>
</div>

<style>
.gallery {
    width: 100%;
    max-width: 1200px;
    margin: 0 auto;
}

.gallery-item {
    float: left;
    width: 31.33%;
    margin: 1%;
}

.gallery-item img {
    width: 100%;
    height: auto;
}

.gallery::after {
    content: "";
    display: table;
    clear: both;
}
</style>
```

## 4.4 定位布局

### 4.4.1 定位的基本概念

CSS定位（positioning）允许我们精确控制元素在页面上的位置。通过设置`position`属性，元素可以从正常文档流中移出，并放置在指定位置。

### 4.4.2 position属性

**语法：**
```css
position: static | relative | absolute | fixed | sticky;
```

**属性值：**
- `static` - 默认值，元素按照正常文档流排列
- `relative` - 相对定位，相对于元素在正常文档流中的位置进行偏移
- `absolute` - 绝对定位，相对于最近的定位祖先元素（不是static）进行定位
- `fixed` - 固定定位，相对于浏览器窗口进行定位，不随页面滚动
- `sticky` - 粘性定位，结合了relative和fixed的特性

### 4.4.3 相对定位（relative）

相对定位使元素相对于其在正常文档流中的原始位置进行偏移。元素仍然占据原始空间，不会影响其他元素的布局。

**特点：**
- 元素不脱离文档流
- 使用top、right、bottom、left属性进行偏移
- 可以作为绝对定位元素的包含块

**示例：**
```css
.relative-box {
    position: relative;
    top: 20px;
    left: 30px;
    width: 200px;
    height: 200px;
    background-color: #3498db;
}
```

### 4.4.4 绝对定位（absolute）

绝对定位使元素完全脱离文档流，并相对于最近的非static定位祖先元素进行定位。如果没有找到这样的祖先元素，则相对于文档的根元素（html或body）定位。

**特点：**
- 元素脱离文档流，不占据原始空间
- 使用top、right、bottom、left属性进行定位
- 会相对于最近的定位祖先元素（不是static）
- 可以创建层叠效果

**示例：**
```html
<div class="container">
    <div class="absolute-box">绝对定位元素</div>
</div>

<style>
.container {
    position: relative; /* 作为绝对定位元素的包含块 */
    width: 400px;
    height: 400px;
    background-color: #f1f1f1;
}

.absolute-box {
    position: absolute;
    top: 50px;
    right: 50px;
    width: 200px;
    height: 200px;
    background-color: #e74c3c;
}
</style>
```

### 4.4.5 固定定位（fixed）

固定定位使元素相对于浏览器窗口进行定位，元素会固定在屏幕的某个位置，不随页面滚动而移动。

**特点：**
- 元素脱离文档流，不占据原始空间
- 使用top、right、bottom、left属性进行定位
- 相对于浏览器窗口定位
- 常用于创建固定导航栏、回到顶部按钮等

**示例：**
```css
.fixed-header {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 60px;
    background-color: #2c3e50;
    color: white;
    z-index: 1000;
}

.back-to-top {
    position: fixed;
    bottom: 30px;
    right: 30px;
    width: 50px;
    height: 50px;
    background-color: #3498db;
    color: white;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    text-decoration: none;
    z-index: 999;
}
```

### 4.4.6 粘性定位（sticky）

粘性定位是CSS3新增的定位方式，它结合了相对定位和固定定位的特点。元素在正常文档流中，当页面滚动到特定位置时，元素会固定在屏幕上。

**特点：**
- 元素在正常文档流中占据空间
- 当滚动到触发点时，变为类似固定定位的效果
- 使用top、right、bottom、left属性设置触发条件
- 只在其父元素的范围内有效

**示例：**
```css
.sticky-nav {
    position: sticky;
    top: 0;
    background-color: #3498db;
    padding: 15px;
    color: white;
    z-index: 100;
}

.section-title {
    position: sticky;
    top: 60px;
    background-color: #2c3e50;
    color: white;
    padding: 10px;
}
```

### 4.4.7 z-index属性

`z-index`属性控制定位元素的堆叠顺序，值越大，元素越在顶层。

**注意事项：**
- 只对定位元素（relative、absolute、fixed、sticky）有效
- 具有相同z-index值的元素，后面的元素会覆盖前面的元素
- z-index在不同的堆叠上下文中是独立的

**示例：**
```css
.layer-1 {
    position: absolute;
    top: 10px;
    left: 10px;
    width: 200px;
    height: 200px;
    background-color: #3498db;
    z-index: 1;
}

.layer-2 {
    position: absolute;
    top: 30px;
    left: 30px;
    width: 200px;
    height: 200px;
    background-color: #e74c3c;
    z-index: 2; /* 会覆盖layer-1 */
}

.layer-3 {
    position: absolute;
    top: 50px;
    left: 50px;
    width: 200px;
    height: 200px;
    background-color: #27ae60;
    z-index: 3; /* 会覆盖layer-2 */
}
```

### 4.4.8 定位布局示例

**示例1：模态框（Modal）**
```html
<div class="modal-overlay">
    <div class="modal-content">
        <h2>模态框标题</h2>
        <p>这是一个使用绝对定位创建的模态框。</p>
        <button class="close-button">关闭</button>
    </div>
</div>

<style>
.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
}

.modal-content {
    position: relative;
    width: 90%;
    max-width: 500px;
    background-color: white;
    padding: 30px;
    border-radius: 8px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.close-button {
    position: absolute;
    top: 10px;
    right: 10px;
    background: none;
    border: none;
    font-size: 24px;
    cursor: pointer;
}
</style>
```

**示例2：下拉菜单**
```html
<div class="dropdown">
    <button class="dropdown-toggle">下拉菜单</button>
    <div class="dropdown-content">
        <a href="#">菜单项 1</a>
        <a href="#">菜单项 2</a>
        <a href="#">菜单项 3</a>
    </div>
</div>

<style>
.dropdown {
    position: relative;
    display: inline-block;
}

.dropdown-toggle {
    padding: 10px 20px;
    background-color: #3498db;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}

.dropdown-content {
    position: absolute;
    top: 100%;
    left: 0;
    min-width: 160px;
    background-color: white;
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
    border-radius: 4px;
    z-index: 10;
    display: none;
}

.dropdown:hover .dropdown-content {
    display: block;
}

.dropdown-content a {
    display: block;
    padding: 10px 15px;
    color: #333;
    text-decoration: none;
    transition: background-color 0.2s;
}

.dropdown-content a:hover {
    background-color: #f1f1f1;
}
</style>
```

## 4.5 Flexbox弹性布局

### 4.5.1 Flexbox的基本概念

Flexbox（弹性盒子）是CSS3引入的一维布局模型，它提供了一种更有效的方式来布局、对齐和分配容器中元素的空间，即使这些元素的大小是未知的或动态变化的。

Flexbox的主要优势在于能够轻松实现垂直居中、等高列、灵活的空间分配等传统布局难以实现的效果。

### 4.5.2 Flexbox的核心概念

Flexbox布局由容器和项目组成：

1. **Flex容器（Flex Container）** - 设置了`display: flex`或`display: inline-flex`的元素
2. **Flex项目（Flex Item）** - Flex容器的直接子元素

Flexbox有两根轴线：

1. **主轴（Main Axis）** - 默认是水平方向，从左到右
2. **交叉轴（Cross Axis）** - 默认是垂直方向，从上到下

### 4.5.3 Flex容器属性

**display**
```css
.container {
    display: flex; /* 或 inline-flex */
}
```

**flex-direction** - 决定主轴方向
```css
.container {
    flex-direction: row | row-reverse | column | column-reverse;
}
```

**flex-wrap** - 决定项目是否换行
```css
.container {
    flex-wrap: nowrap | wrap | wrap-reverse;
}
```

**flex-flow** - flex-direction和flex-wrap的简写
```css
.container {
    flex-flow: <flex-direction> <flex-wrap>;
}
```

**justify-content** - 决定项目在主轴上的对齐方式
```css
.container {
    justify-content: flex-start | flex-end | center | space-between | space-around | space-evenly;
}
```

**align-items** - 决定项目在交叉轴上的对齐方式
```css
.container {
    align-items: stretch | flex-start | flex-end | center | baseline;
}
```

**align-content** - 决定多行项目在交叉轴上的对齐方式
```css
.container {
    align-content: stretch | flex-start | flex-end | center | space-between | space-around;
}
```

### 4.5.4 Flex项目属性

**order** - 决定项目的排列顺序
```css
.item {
    order: <integer>; /* 默认值为0 */
}
```

**flex-grow** - 决定项目的放大比例
```css
.item {
    flex-grow: <number>; /* 默认值为0 */
}
```

**flex-shrink** - 决定项目的缩小比例
```css
.item {
    flex-shrink: <number>; /* 默认值为1 */
}
```

**flex-basis** - 决定项目在主轴上的基础大小
```css
.item {
    flex-basis: <length> | auto; /* 默认值为auto */
}
```

**flex** - flex-grow, flex-shrink和flex-basis的简写
```css
.item {
    flex: none | [ <flex-grow> <flex-shrink>? || <flex-basis> ];
}
/* 常用值 */
.item {
    flex: 1; /* 相当于 flex: 1 1 0% */
    flex: auto; /* 相当于 flex: 1 1 auto */
    flex: none; /* 相当于 flex: 0 0 auto */
}
```

**align-self** - 决定单个项目在交叉轴上的对齐方式
```css
.item {
    align-self: auto | flex-start | flex-end | center | baseline | stretch;
}
```

### 4.5.5 Flexbox布局示例

**示例1：水平居中对齐**
```html
<div class="container">
    <div class="item">项目 1</div>
    <div class="item">项目 2</div>
    <div class="item">项目 3</div>
</div>

<style>
.container {
    display: flex;
    justify-content: center;
    /* 可选：垂直居中 */
    height: 200px;
    align-items: center;
    background-color: #f1f1f1;
}

.item {
    padding: 20px;
    margin: 0 10px;
    background-color: #3498db;
    color: white;
    border-radius: 4px;
}
</style>
```

**示例2：等分布局**
```html
<div class="container">
    <div class="item">项目 1</div>
    <div class="item">项目 2</div>
    <div class="item">项目 3</div>
    <div class="item">项目 4</div>
</div>

<style>
.container {
    display: flex;
    gap: 20px; /* 项目间距 */
}

.item {
    flex: 1; /* 等比例分配空间 */
    padding: 20px;
    background-color: #3498db;
    color: white;
    border-radius: 4px;
    text-align: center;
}
</style>
```

**示例3：响应式导航栏**
```html
<nav class="navbar">
    <div class="logo">品牌名称</div>
    <ul class="nav-links">
        <li><a href="#">首页</a></li>
        <li><a href="#">产品</a></li>
        <li><a href="#">服务</a></li>
        <li><a href="#">关于我们</a></li>
    </ul>
</nav>

<style>
.navbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 15px 20px;
    background-color: #2c3e50;
    color: white;
}

.logo {
    font-size: 1.5rem;
    font-weight: bold;
}

.nav-links {
    display: flex;
    list-style: none;
    margin: 0;
    padding: 0;
}

.nav-links li {
    margin-left: 20px;
}

.nav-links a {
    color: white;
    text-decoration: none;
    padding: 8px 12px;
    border-radius: 4px;
    transition: background-color 0.3s;
}

.nav-links a:hover {
    background-color: rgba(255, 255, 255, 0.1);
}

/* 响应式设计 */
@media (max-width: 768px) {
    .navbar {
        flex-direction: column;
    }
    
    .nav-links {
        flex-direction: column;
        width: 100%;
        margin-top: 15px;
    }
    
    .nav-links li {
        margin: 5px 0;
        text-align: center;
    }
}
</style>
```

**示例4：卡片网格布局**
```html
<div class="card-container">
    <div class="card">卡片 1</div>
    <div class="card">卡片 2</div>
    <div class="card">卡片 3</div>
    <div class="card">卡片 4</div>
    <div class="card">卡片 5</div>
    <div class="card">卡片 6</div>
</div>

<style>
.card-container {
    display: flex;
    flex-wrap: wrap;
    gap: 20px;
}

.card {
    flex: 1 1 300px; /* 基础大小300px，允许放大和缩小 */
    padding: 30px;
    background-color: white;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    min-height: 200px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.2rem;
    font-weight: bold;
}
</style>
```

## 4.6 Grid网格布局

### 4.6.1 Grid的基本概念

CSS Grid（网格布局）是CSS3引入的二维布局系统，它允许我们同时处理行和列，创建复杂的布局结构。Grid布局是目前最强大的CSS布局方案，特别适合创建具有明确行和列的页面布局。

### 4.6.2 Grid的核心概念

Grid布局由容器和项目组成：

1. **Grid容器（Grid Container）** - 设置了`display: grid`或`display: inline-grid`的元素
2. **Grid项目（Grid Item）** - Grid容器的直接子元素

Grid布局的基本组成部分：

1. **网格线（Grid Lines）** - 划分网格的线，包括水平线和垂直线
2. **网格轨道（Grid Track）** - 两条相邻网格线之间的空间，即行或列
3. **网格单元格（Grid Cell）** - 相邻两条水平网格线和两条垂直网格线围成的区域
4. **网格区域（Grid Area）** - 由一个或多个网格单元格组成的矩形区域
5. **网格间距（Grid Gap）** - 网格线之间的空间

### 4.6.3 Grid容器属性

**display**
```css
.container {
    display: grid; /* 或 inline-grid */
}
```

**grid-template-columns, grid-template-rows** - 定义网格的列和行大小
```css
.container {
    grid-template-columns: <track-size> ... | <line-name> <track-size> ...;
    grid-template-rows: <track-size> ... | <line-name> <track-size> ...;
}

/* 示例 */
.container {
    grid-template-columns: 100px 1fr 2fr; /* 三列，宽度分别为100px, 1份, 2份 */
    grid-template-rows: 50px 1fr; /* 两行，高度分别为50px, 1份 */
}
```

**grid-template-areas** - 使用命名的网格区域定义布局
```css
.container {
    grid-template-areas:
        "header header header"
        "sidebar main main"
        "footer footer footer";
}
```

**grid-template** - grid-template-rows、grid-template-columns和grid-template-areas的简写
```css
.container {
    grid-template: <grid-template-rows> / <grid-template-columns>;
}
```

**column-gap, row-gap** - 设置列间距和行间距
```css
.container {
    column-gap: <length>;
    row-gap: <length>;
}
```

**gap** - column-gap和row-gap的简写
```css
.container {
    gap: <row-gap> <column-gap>;
}

/* 示例 */
.container {
    gap: 10px 20px; /* 行间距10px，列间距20px */
    gap: 15px; /* 行列间距均为15px */
}
```

**justify-items** - 设置网格项目在其单元格中沿行轴的对齐方式
```css
.container {
    justify-items: start | end | center | stretch;
}
```

**align-items** - 设置网格项目在其单元格中沿列轴的对齐方式
```css
.container {
    align-items: start | end | center | stretch;
}
```

**place-items** - justify-items和align-items的简写
```css
.container {
    place-items: <align-items> <justify-items>;
}
```

**justify-content** - 设置整个网格在容器中沿行轴的对齐方式
```css
.container {
    justify-content: start | end | center | stretch | space-around | space-between | space-evenly;
}
```

**align-content** - 设置整个网格在容器中沿列轴的对齐方式
```css
.container {
    align-content: start | end | center | stretch | space-around | space-between | space-evenly;
}
```

**place-content** - justify-content和align-content的简写
```css
.container {
    place-content: <align-content> <justify-content>;
}
```

**grid-auto-columns, grid-auto-rows** - 设置自动生成的网格轨道大小
```css
.container {
    grid-auto-columns: <track-size> ...;
    grid-auto-rows: <track-size> ...;
}
```

**grid-auto-flow** - 控制自动布局算法的工作方式
```css
.container {
    grid-auto-flow: row | column | row dense | column dense;
}
```

**grid** - 所有网格容器属性的简写
```css
.container {
    grid: <grid-template-rows> / <grid-template-columns>;
}
```

### 4.6.4 Grid项目属性

**grid-column-start, grid-column-end, grid-row-start, grid-row-end** - 指定项目在网格中的位置
```css
.item {
    grid-column-start: <number> | <name> | span <number> | span <name> | auto;
    grid-column-end: <number> | <name> | span <number> | span <name> | auto;
    grid-row-start: <number> | <name> | span <number> | span <name> | auto;
    grid-row-end: <number> | <name> | span <number> | span <name> | auto;
}

/* 简写 */
.item {
    grid-column: <start-line> / <end-line> | <start-line> / span <value>;
    grid-row: <start-line> / <end-line> | <start-line> / span <value>;
}
```

**grid-area** - 指定项目占据的网格区域
```css
.item {
    grid-area: <name> | <row-start> / <column-start> / <row-end> / <column-end>;
}
```

**justify-self** - 设置单个项目在其单元格中沿行轴的对齐方式
```css
.item {
    justify-self: start | end | center | stretch;
}
```

**align-self** - 设置单个项目在其单元格中沿列轴的对齐方式
```css
.item {
    align-self: start | end | center | stretch;
}
```

**place-self** - justify-self和align-self的简写
```css
.item {
    place-self: <align-self> <justify-self>;
}
```

### 4.6.5 Grid布局示例

**示例1：基本网格布局**
```html
<div class="grid-container">
    <div class="item item1">1</div>
    <div class="item item2">2</div>
    <div class="item item3">3</div>
    <div class="item item4">4</div>
    <div class="item item5">5</div>
    <div class="item item6">6</div>
</div>

<style>
.grid-container {
    display: grid;
    grid-template-columns: repeat(3, 1fr); /* 三列，每列等宽 */
    grid-template-rows: repeat(2, 100px); /* 两行，每行100px高 */
    gap: 10px;
}

.item {
    background-color: #3498db;
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;
    font-weight: bold;
    border-radius: 4px;
}
</style>
```

**示例2：使用grid-template-areas创建页面布局**
```html
<div class="grid-container">
    <header class="header">页眉</header>
    <aside class="sidebar">侧边栏</aside>
    <main class="main">主要内容</main>
    <aside class="right-sidebar">右侧边栏</aside>
    <footer class="footer">页脚</footer>
</div>

<style>
.grid-container {
    display: grid;
    grid-template-areas:
        "header header header"
        "sidebar main right-sidebar"
        "footer footer footer";
    grid-template-columns: 250px 1fr 250px;
    grid-template-rows: 80px 1fr 60px;
    height: 100vh;
    gap: 10px;
}

.header {
    grid-area: header;
    background-color: #2c3e50;
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
}

.sidebar {
    grid-area: sidebar;
    background-color: #3498db;
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
}

.main {
    grid-area: main;
    background-color: #ecf0f1;
    display: flex;
    align-items: center;
    justify-content: center;
}

.right-sidebar {
    grid-area: right-sidebar;
    background-color: #e74c3c;
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
}

.footer {
    grid-area: footer;
    background-color: #27ae60;
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
}
</style>
```

**示例3：响应式网格布局**
```html
<div class="gallery">
    <div class="gallery-item">项目 1</div>
    <div class="gallery-item">项目 2</div>
    <div class="gallery-item">项目 3</div>
    <div class="gallery-item">项目 4</div>
    <div class="gallery-item">项目 5</div>
    <div class="gallery-item">项目 6</div>
</div>

<style>
.gallery {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); /* 自动填充，最小宽度250px */
    gap: 20px;
}

.gallery-item {
    background-color: #3498db;
    color: white;
    padding: 30px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.2rem;
    font-weight: bold;
}

/* 响应式调整 */
@media (max-width: 600px) {
    .gallery {
        grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); /* 小屏幕上减小最小宽度 */
    }
}
</style>
```

**示例4：复杂网格布局**
```html
<div class="grid-container">
    <div class="item header">页眉</div>
    <div class="item sidebar">侧边栏</div>
    <div class="item content-1">内容块 1</div>
    <div class="item content-2">内容块 2</div>
    <div class="item content-3">内容块 3</div>
    <div class="item footer">页脚</div>
</div>

<style>
.grid-container {
    display: grid;
    grid-template-columns: 200px 1fr 1fr;
    grid-template-rows: 100px 200px 200px 100px;
    gap: 10px;
}

.header {
    grid-column: 1 / -1; /* 从第一列到最后一列 */
    background-color: #2c3e50;
    color: white;
}

.sidebar {
    grid-row: 2 / 4; /* 从第二行到第四行 */
    background-color: #3498db;
    color: white;
}

.content-1 {
    background-color: #e74c3c;
    color: white;
}

.content-2 {
    background-color: #27ae60;
    color: white;
}

.content-3 {
    grid-column: 2 / -1; /* 从第二列到最后一列 */
    background-color: #f39c12;
    color: white;
}

.footer {
    grid-column: 1 / -1; /* 从第一列到最后一列 */
    background-color: #9b59b6;
    color: white;
}

/* 通用样式 */
.item {
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.2rem;
    font-weight: bold;
    border-radius: 4px;
}
</style>
```

## 4.7 响应式布局

### 4.7.1 响应式设计的基本概念

响应式设计（Responsive Design）是一种网页设计方法，使网站能够根据用户设备（如桌面、平板、手机）的屏幕尺寸和方向自动调整布局，提供最佳的浏览体验。

响应式设计的核心原则是"一次设计，处处可用"，通过使用CSS3的媒体查询、弹性图像、流式布局等技术实现。

### 4.7.2 媒体查询（Media Queries）

媒体查询是响应式设计的核心，它允许我们根据不同的屏幕尺寸应用不同的CSS样式。

**基本语法：**
```css
@media media-type and (media-feature-rule) {
    /* CSS rules */
}
```

**媒体类型：**
- `all` - 所有设备
- `screen` - 彩色屏幕设备
- `print` - 打印设备
- `speech` - 语音合成器

**常见媒体特性：**
- `width`, `height` - 视口宽度和高度
- `min-width`, `max-width` - 最小和最大视口宽度
- `min-height`, `max-height` - 最小和最大视口高度
- `orientation` - 设备方向（portrait | landscape）
- `device-width`, `device-height` - 设备屏幕的宽度和高度
- `resolution` - 设备分辨率

**示例：**
```css
/* 基础样式 - 适用于所有屏幕尺寸 */
.container {
    width: 100%;
    padding: 20px;
}

/* 当屏幕宽度至少为768px时应用 */
@media (min-width: 768px) {
    .container {
        max-width: 750px;
        margin: 0 auto;
    }
}

/* 当屏幕宽度至少为992px时应用 */
@media (min-width: 992px) {
    .container {
        max-width: 970px;
    }
}

/* 当屏幕宽度至少为1200px时应用 */
@media (min-width: 1200px) {
    .container {
        max-width: 1170px;
    }
}

/* 针对手机竖屏的样式 */
@media (max-width: 480px) {
    .nav {
        flex-direction: column;
    }
}

/* 针对平板横屏的样式 */
@media (min-width: 768px) and (max-width: 1024px) and (orientation: landscape) {
    .sidebar {
        display: none;
    }
}
```

### 4.7.3 响应式布局技术

**1. 流体布局（Fluid Layout）**
使用百分比而不是固定像素值来设置宽度，使元素能够随屏幕宽度变化而缩放。

```css
.container {
    width: 90%;
    max-width: 1200px;
    margin: 0 auto;
}

.sidebar {
    width: 30%;
}

.main {
    width: 65%;
    margin-left: 5%;
}
```

**2. 弹性盒子（Flexbox）**
Flexbox是创建响应式布局的强大工具，特别适合一维布局。

```css
.container {
    display: flex;
    flex-wrap: wrap;
}

.item {
    flex: 1 1 250px;
    margin: 10px;
}
```

**3. 网格布局（Grid）**
Grid布局非常适合创建响应式的二维布局。

```css
.container {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 20px;
}
```

**4. 响应式图像**
使图像能够根据容器宽度自动缩放。

```css
img {
    max-width: 100%;
    height: auto;
}
```

**5. 视口元标签**
在HTML头部添加视口元标签，确保移动设备正确显示页面。

```html
<meta name="viewport" content="width=device-width, initial-scale=1.0">
```

### 4.7.4 响应式布局示例

**示例：响应式多列布局**
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>响应式布局示例</title>
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
        }
        
        .container {
            width: 100%;
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }
        
        .header {
            background-color: #2c3e50;
            color: white;
            padding: 20px 0;
            text-align: center;
        }
        
        .navigation {
            background-color: #3498db;
            padding: 10px 0;
        }
        
        .nav-list {
            display: flex;
            list-style: none;
            justify-content: center;
        }
        
        .nav-item {
            margin: 0 15px;
        }
        
        .nav-link {
            color: white;
            text-decoration: none;
            padding: 5px 10px;
            transition: background-color 0.3s;
        }
        
        .nav-link:hover {
            background-color: rgba(255, 255, 255, 0.1);
            border-radius: 4px;
        }
        
        .main-content {
            display: flex;
            flex-wrap: wrap;
            margin: 20px 0;
        }
        
        .sidebar {
            flex: 1;
            min-width: 250px;
            margin-right: 20px;
            background-color: #ecf0f1;
            padding: 20px;
            border-radius: 8px;
        }
        
        .content {
            flex: 3;
            min-width: 300px;
            background-color: #f9f9f9;
            padding: 20px;
            border-radius: 8px;
        }
        
        .footer {
            background-color: #27ae60;
            color: white;
            padding: 20px 0;
            text-align: center;
            margin-top: 20px;
        }
        
        /* 响应式设计 */
        @media (max-width: 768px) {
            .nav-list {
                flex-direction: column;
                align-items: center;
            }
            
            .nav-item {
                margin: 5px 0;
                width: 100%;
                text-align: center;
            }
            
            .sidebar {
                margin-right: 0;
                margin-bottom: 20px;
            }
        }
        
        @media (max-width: 480px) {
            .container {
                padding: 0 10px;
            }
            
            .sidebar,
            .content {
                min-width: 100%;
            }
        }
    </style>
</head>
<body>
    <header class="header">
        <div class="container">
            <h1>响应式网站</h1>
        </div>
    </header>
    
    <nav class="navigation">
        <div class="container">
            <ul class="nav-list">
                <li class="nav-item"><a href="#" class="nav-link">首页</a></li>
                <li class="nav-item"><a href="#" class="nav-link">产品</a></li>
                <li class="nav-item"><a href="#" class="nav-link">服务</a></li>
                <li class="nav-item"><a href="#" class="nav-link">关于我们</a></li>
                <li class="nav-item"><a href="#" class="nav-link">联系我们</a></li>
            </ul>
        </div>
    </nav>
    
    <div class="container">
        <div class="main-content">
            <aside class="sidebar">
                <h2>侧边栏</h2>
                <ul>
                    <li><a href="#">链接 1</a></li>
                    <li><a href="#">链接 2</a></li>
                    <li><a href="#">链接 3</a></li>
                    <li><a href="#">链接 4</a></li>
                </ul>
            </aside>
            
            <main class="content">
                <h2>主要内容</h2>
                <p>这是一个响应式布局的示例页面。在不同的屏幕尺寸下，页面布局会自动调整，以提供最佳的用户体验。</p>
                <p>当屏幕宽度较小时，导航菜单会变为垂直排列，侧边栏会移动到主要内容的上方。</p>
                <p>响应式设计使网站能够适应各种设备，包括桌面电脑、平板电脑和智能手机。</p>
            </main>
        </div>
    </div>
    
    <footer class="footer">
        <div class="container">
            <p>&copy; 2023 响应式网站示例</p>
        </div>
    </footer>
</body>
</html>
```

## 4.8 布局技术的选择与最佳实践

### 4.8.1 不同布局技术的比较

| 布局技术 | 优势 | 劣势 | 适用场景 |
|---------|------|------|----------|
| 浮动布局 | 浏览器兼容性好 | 需要清除浮动，布局复杂 | 简单的多列布局，旧项目维护 |
| 定位布局 | 精确控制元素位置 | 脱离文档流，可能导致重叠 | 元素精确定位，模态框，下拉菜单 |
| Flexbox | 一维布局强大，易于使用，响应式好 | 二维布局能力有限 | 导航栏，卡片列表，组件内部布局 |
| Grid | 二维布局强大，语法简洁 | 浏览器兼容性相对较差 | 页面整体布局，复杂网格结构 |

### 4.8.2 布局技术选择建议

1. **结合使用多种布局技术**
   - 页面整体布局可以使用Grid
   - 组件内部布局可以使用Flexbox
   - 特殊定位需求可以使用position属性

2. **考虑浏览器兼容性**
   - 如果需要支持IE10及以下，可能需要使用传统布局或提供降级方案
   - 现代项目可以优先考虑Flexbox和Grid

3. **考虑项目复杂度**
   - 简单项目可以使用基本的文档流和浮动
   - 复杂项目推荐使用Flexbox和Grid

4. **响应式设计**
   - 移动端优先设计，使用媒体查询适配不同屏幕
   - 利用Flexbox和Grid的自动伸缩特性

### 4.8.3 布局性能优化

1. **减少嵌套层级**
   - 过多的嵌套会增加渲染时间，尽量保持HTML结构扁平

2. **避免过度使用浮动**
   - 大量使用浮动可能导致布局复杂，难以维护
   - 适当使用Flexbox和Grid替代

3. **优化重排（reflow）**
   - 避免频繁操作DOM和修改布局属性
   - 使用CSS transforms替代直接修改位置属性

4. **使用CSS变量**
   - 使用CSS变量管理布局参数，便于维护和修改

5. **利用CSS Grid的自动布局**
   - Grid的auto-fit和auto-fill特性可以提高布局效率

### 4.8.4 常见布局模式及实现

**1. 两列布局**
```css
/* 使用Flexbox */
.two-columns {
    display: flex;
    gap: 20px;
}

.left-column {
    flex: 1;
    min-width: 300px;
}

.right-column {
    flex: 2;
    min-width: 400px;
}

/* 使用Grid */
.two-columns-grid {
    display: grid;
    grid-template-columns: 1fr 2fr;
    gap: 20px;
}
```

**2. 三列布局**
```css
.three-columns {
    display: grid;
    grid-template-columns: 250px 1fr 250px;
    gap: 20px;
}

/* 响应式三列布局 */
@media (max-width: 992px) {
    .three-columns {
        grid-template-columns: 1fr;
    }
    
    .center-column {
        order: -1; /* 中间列在顶部 */
    }
}
```

**3. 圣杯布局/Golden Layout**
```css
.golden-layout {
    display: grid;
    grid-template-areas:
        "header header header"
        "left-sidebar main right-sidebar"
        "footer footer footer";
    grid-template-columns: 200px 1fr 200px;
    grid-template-rows: auto 1fr auto;
    min-height: 100vh;
    gap: 10px;
}

.header { grid-area: header; }
.left-sidebar { grid-area: left-sidebar; }
.main { grid-area: main; }
.right-sidebar { grid-area: right-sidebar; }
.footer { grid-area: footer; }
```

**4. 卡片瀑布流**
```css
.masonry {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    grid-auto-rows: 50px;
    grid-gap: 20px;
}

.card {
    grid-row: auto / span var(--row-span, 6);
}

.card:nth-child(2n) {
    --row-span: 8;
}

.card:nth-child(3n) {
    --row-span: 10;
}
```

## 4.9 总结与下一步

### 4.9.1 本章要点回顾

- **文档流** - 理解块级元素和行内元素在文档流中的行为
- **浮动布局** - 使用float属性创建多列布局，注意清除浮动
- **定位布局** - 掌握relative、absolute、fixed和sticky四种定位方式
- **Flexbox布局** - 一维弹性布局，适用于导航栏、列表等
- **Grid布局** - 二维网格布局，适用于复杂页面布局
- **响应式设计** - 使用媒体查询、流体布局等技术创建适应不同设备的页面
- **布局选择** - 根据项目需求和浏览器兼容性选择合适的布局技术

### 4.9.2 下一步学习建议

- 学习CSS高级特性，如动画、过渡和变换
- 探索CSS预处理器（如Sass、Less）提高开发效率
- 研究CSS框架（如Bootstrap、Tailwind CSS）的布局系统
- 学习CSS性能优化技术
- 了解Web Components和CSS Modules等现代CSS架构方案

通过本章的学习，你应该已经掌握了CSS中各种布局技术的使用方法和最佳实践。在实际项目中，合理选择和组合使用这些布局技术，可以创建出既美观又实用的网页布局。随着CSS技术的不断发展，Flexbox和Grid等现代布局技术已经成为前端开发的主流选择，它们不仅使布局更加简单直观，还提供了更好的响应式支持。