# CSS选择器

## 2.1 CSS选择器简介

### 2.1.1 什么是CSS选择器？

CSS选择器是CSS规则的第一部分，它用于选择要应用样式的HTML元素。选择器是CSS的核心概念之一，掌握选择器的使用对于编写高效、简洁的CSS代码至关重要。

选择器允许我们：
- 精确地定位HTML文档中的特定元素
- 将样式应用到一个或多个元素上
- 基于元素的属性、状态或位置来应用样式
- 创建可复用的样式规则

### 2.1.2 选择器的重要性

选择器在CSS中扮演着至关重要的角色：

1. **精确性**：使用正确的选择器可以精确地定位需要样式化的元素
2. **效率**：选择器的效率直接影响浏览器渲染页面的性能
3. **可维护性**：良好的选择器策略可以使CSS代码更易于维护和扩展
4. **代码复用**：通过选择器可以实现样式的高效复用
5. **响应式设计**：配合媒体查询，选择器可以针对不同屏幕尺寸应用不同样式

### 2.1.3 选择器的分类

CSS选择器可以分为以下几大类：

1. **基础选择器**：最基本的选择器类型
2. **组合选择器**：通过组合多个选择器来选择元素
3. **属性选择器**：基于元素的属性及其值来选择
4. **伪类选择器**：基于元素的状态或位置来选择
5. **伪元素选择器**：用于选择元素的特定部分

## 2.2 基础选择器

### 2.2.1 通用选择器

通用选择器（Universal Selector）使用星号`*`表示，它会匹配文档中的所有元素。

**语法：**
```css
* {
    property: value;
}
```

**示例：**
```css
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}
```

这个示例是一个常见的CSS重置，它会移除所有元素的默认外边距和内边距，并设置`box-sizing`为`border-box`。

**使用场景：**
- CSS重置或规范化
- 快速应用全局样式
- 覆盖浏览器默认样式

**注意事项：**
- 通用选择器的优先级最低
- 过度使用可能会影响性能，尤其是在大型文档中
- 通常仅用于全局样式重置或设置

### 2.2.2 元素选择器

元素选择器（Element Selector）也称为标签选择器，它根据HTML元素的名称来选择元素。

**语法：**
```css
元素名 {
    property: value;
}
```

**示例：**
```css
p {
    font-size: 16px;
    line-height: 1.6;
    color: #333;
}

h1 {
    color: #2c3e50;
    font-size: 2rem;
    margin-bottom: 1rem;
}

ul {
    list-style-type: none;
}
```

**使用场景：**
- 为HTML元素设置默认样式
- 对整个页面的某类元素应用一致的样式
- 重置浏览器对特定元素的默认样式

**注意事项：**
- 元素选择器的优先级低于类选择器和ID选择器
- 更改元素选择器的样式会影响文档中所有该类型的元素

### 2.2.3 ID选择器

ID选择器（ID Selector）使用井号`#`后跟ID名称来选择具有特定ID的元素。ID在HTML文档中应该是唯一的。

**语法：**
```css
#id名 {
    property: value;
}
```

**示例：**
```html
<div id="header">页面头部</div>
```

```css
#header {
    background-color: #3498db;
    color: white;
    padding: 20px;
    text-align: center;
}
```

**使用场景：**
- 选择页面中唯一的、特定的元素（如页眉、页脚、侧边栏等）
- 为JavaScript交互选择目标元素
- 需要高优先级样式的元素

**注意事项：**
- ID必须是唯一的，一个文档中不应有多个相同ID的元素
- ID选择器的优先级高于类选择器和元素选择器
- 过度使用ID选择器会降低样式的复用性，应优先使用类选择器

### 2.2.4 类选择器

类选择器（Class Selector）使用点`.`后跟类名来选择具有特定类的元素。一个类可以应用于多个元素。

**语法：**
```css
.类名 {
    property: value;
}
```

**示例：**
```html
<p class="highlight">这段文字需要高亮显示</p>
<div class="card">这是一个卡片组件</div>
<div class="card">这是另一个卡片组件</div>
```

```css
.highlight {
    background-color: #fff9c4;
    padding: 5px;
    border-left: 4px solid #ffeb3b;
}

.card {
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 15px;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}
```

**使用场景：**
- 对多个元素应用相同的样式
- 创建可复用的样式组件
- 基于功能或状态对元素进行样式化

**注意事项：**
- 类选择器的优先级高于元素选择器，但低于ID选择器
- 一个元素可以有多个类，类名之间用空格分隔
- 类名应该语义化，反映元素的功能或状态，而不是样式

### 2.2.5 多类选择器

多类选择器允许我们选择同时具有多个特定类的元素。

**语法：**
```css
.类名1.类名2 {
    property: value;
}
```

**示例：**
```html
<div class="button primary">主要按钮</div>
<div class="button secondary">次要按钮</div>
<div class="primary">仅主要样式</div>
```

```css
.button {
    padding: 10px 20px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 16px;
}

.button.primary {
    background-color: #3498db;
    color: white;
}

.button.secondary {
    background-color: #95a5a6;
    color: white;
}

.primary {
    font-weight: bold;
}
```

在这个示例中，`.button.primary`只会匹配同时有`button`和`primary`类的元素，而不会匹配只有`primary`类的元素。

**使用场景：**
- 创建基于多个类的组合样式
- 构建模块化的样式系统
- 实现类似BEM（Block, Element, Modifier）的命名约定

## 2.3 组合选择器

### 2.3.1 后代选择器

后代选择器（Descendant Selector）使用空格分隔两个或多个选择器，它会选择匹配第二个选择器的元素，只要这些元素是匹配第一个选择器的元素的后代。

**语法：**
```css
选择器1 选择器2 {
    property: value;
}
```

**示例：**
```html
<ul class="menu">
    <li>首页</li>
    <li>产品</li>
    <li>关于我们</li>
</ul>
<p>这是一个段落，<span>包含一些文本</span>。</p>
```

```css
.menu li {
    display: inline-block;
    margin-right: 20px;
    padding: 5px;
}

p span {
    color: #e74c3c;
    font-weight: bold;
}
```

在这个示例中，`.menu li`会选择`menu`类的列表中的所有列表项，而`p span`会选择所有段落中的所有`span`元素。

**使用场景：**
- 为特定容器内的元素应用样式
- 创建上下文相关的样式规则
- 避免使用过多的类名

**注意事项：**
- 后代选择器会匹配所有层级的后代元素
- 过于复杂的后代选择器可能会影响性能
- 嵌套层级不宜过深，通常不超过3-4层

### 2.3.2 子选择器

子选择器（Child Selector）使用大于号`>`分隔两个选择器，它会选择匹配第二个选择器的元素，只要这些元素是匹配第一个选择器的元素的直接子元素。

**语法：**
```css
选择器1 > 选择器2 {
    property: value;
}
```

**示例：**
```html
<div class="container">
    <p>这是直接子段落</p>
    <div>
        <p>这是间接子段落</p>
    </div>
</div>
```

```css
.container > p {
    color: #3498db;
    font-weight: bold;
}
```

在这个示例中，`.container > p`只会选择`container`类元素的直接子段落，而不会选择嵌套在其他元素内的段落。

**使用场景：**
- 精确控制直接子元素的样式
- 避免样式意外地应用到深层嵌套的元素
- 为特定层级的元素设置样式

**注意事项：**
- 子选择器只匹配直接子元素，不匹配更深层级的后代元素
- 子选择器的优先级通常高于后代选择器

### 2.3.3 相邻兄弟选择器

相邻兄弟选择器（Adjacent Sibling Selector）使用加号`+`分隔两个选择器，它会选择匹配第二个选择器的元素，只要这些元素是匹配第一个选择器的元素的直接相邻兄弟元素。

**语法：**
```css
选择器1 + 选择器2 {
    property: value;
}
```

**示例：**
```html
<h2>标题</h2>
<p>这是标题后的第一个段落</p>
<p>这是第二个段落</p>
<div>这是一个div</div>
<p>这是div后的段落</p>
```

```css
h2 + p {
    color: #e74c3c;
    font-size: 18px;
    margin-top: 10px;
}

div + p {
    font-style: italic;
}
```

在这个示例中，`h2 + p`只会选择紧跟在`h2`元素后面的那个`p`元素，而`div + p`只会选择紧跟在`div`元素后面的那个`p`元素。

**使用场景：**
- 为特定元素后的直接兄弟元素设置样式
- 创建元素之间的视觉关系
- 实现特定的布局效果

**注意事项：**
- 相邻兄弟选择器只匹配紧随其后的兄弟元素
- 兄弟元素必须共享同一个父元素

### 2.3.4 通用兄弟选择器

通用兄弟选择器（General Sibling Selector）使用波浪号`~`分隔两个选择器，它会选择匹配第二个选择器的元素，只要这些元素在匹配第一个选择器的元素之后，并且共享同一个父元素。

**语法：**
```css
选择器1 ~ 选择器2 {
    property: value;
}
```

**示例：**
```html
<h3>标题</h3>
<p>第一个段落</p>
<div>一个div</div>
<p>第二个段落</p>
<p>第三个段落</p>
```

```css
h3 ~ p {
    color: #27ae60;
    margin-left: 20px;
}
```

在这个示例中，`h3 ~ p`会选择所有在`h3`元素之后且与`h3`共享同一个父元素的`p`元素，包括中间有其他元素的情况。

**使用场景：**
- 为特定元素后的所有兄弟元素设置样式
- 创建基于元素顺序的样式规则
- 实现表单元素的样式联动

**注意事项：**
- 通用兄弟选择器匹配所有后续的兄弟元素，不考虑它们之间是否有其他元素
- 兄弟元素必须共享同一个父元素

## 2.4 属性选择器

### 2.4.1 基本属性选择器

基本属性选择器用于选择具有特定属性的元素，无论属性值是什么。

**语法：**
```css
[属性名] {
    property: value;
}
```

**示例：**
```css
[title] {
    color: #3498db;
    border-bottom: 1px dashed #3498db;
}

[disabled] {
    opacity: 0.5;
    cursor: not-allowed;
}

[href] {
    color: #e74c3c;
    text-decoration: none;
}
```

在这个示例中：
- `[title]`会选择所有具有`title`属性的元素
- `[disabled]`会选择所有具有`disabled`属性的元素
- `[href]`会选择所有具有`href`属性的元素（即所有链接）

**使用场景：**
- 为具有特定属性的元素应用统一样式
- 为表单元素（如禁用的输入框）设置样式
- 为具有标题或其他属性的元素添加视觉提示

### 2.4.2 属性等于选择器

属性等于选择器用于选择具有特定属性且属性值完全匹配的元素。

**语法：**
```css
[属性名="属性值"] {
    property: value;
}
```

**示例：**
```html
<a href="https://example.com" target="_blank">外部链接</a>
<a href="#section-1">内部链接</a>
<input type="text" placeholder="请输入...">
<input type="email" placeholder="请输入邮箱...">
```

```css
a[target="_blank"] {
    color: #27ae60;
    font-weight: bold;
}

input[type="email"] {
    border-color: #3498db;
    background-color: #ecf0f1;
}
```

在这个示例中：
- `a[target="_blank"]`会选择所有`target`属性值为`_blank`的链接
- `input[type="email"]`会选择所有`type`属性值为`email`的输入框

**使用场景：**
- 为不同类型的表单元素设置不同样式
- 区分外部链接和内部链接
- 根据数据属性的值应用不同样式

### 2.4.3 属性包含选择器

属性包含选择器用于选择具有特定属性且属性值包含指定单词的元素（单词之间用空格分隔）。

**语法：**
```css
[属性名~="属性值"] {
    property: value;
}
```

**示例：**
```html
<div class="container box">容器</div>
<div class="box highlight">高亮盒子</div>
<div class="box warning">警告盒子</div>
<p data-tags="important new">重要通知</p>
<p data-tags="update">更新内容</p>
```

```css
[class~="box"] {
    border: 1px solid #ddd;
    padding: 15px;
    margin-bottom: 10px;
}

[data-tags~="important"] {
    background-color: #fff3cd;
    border-left: 4px solid #ffc107;
}
```

在这个示例中：
- `[class~="box"]`会选择所有`class`属性值中包含`box`单词的元素
- `[data-tags~="important"]`会选择所有`data-tags`属性值中包含`important`单词的元素

**使用场景：**
- 选择具有特定类名的元素（类似于类选择器，但更灵活）
- 基于数据属性的值来应用样式
- 为带有特定标签或关键词的元素设置样式

### 2.4.4 属性开头选择器

属性开头选择器用于选择具有特定属性且属性值以指定字符串开头的元素。

**语法：**
```css
[属性名^="开头字符串"] {
    property: value;
}
```

**示例：**
```html
<a href="https://example.com">HTTPS链接</a>
<a href="http://example.com">HTTP链接</a>
<img src="icon-home.svg" alt="首页图标">
<img src="icon-settings.svg" alt="设置图标">
<div id="section-1">第一部分</div>
<div id="section-2">第二部分</div>
```

```css
a[href^="https"] {
    color: #27ae60;
    font-weight: bold;
}

img[src^="icon-"] {
    width: 32px;
    height: 32px;
}

div[id^="section-"] {
    margin-top: 30px;
    padding-top: 15px;
    border-top: 1px solid #eee;
}
```

在这个示例中：
- `a[href^="https"]`会选择所有`href`属性值以`https`开头的链接
- `img[src^="icon-"]`会选择所有`src`属性值以`icon-`开头的图片
- `div[id^="section-"]`会选择所有`id`属性值以`section-`开头的div

**使用场景：**
- 区分HTTPS和HTTP链接
- 为特定前缀的图片或资源设置样式
- 为具有特定ID格式的区块设置样式

### 2.4.5 属性结尾选择器

属性结尾选择器用于选择具有特定属性且属性值以指定字符串结尾的元素。

**语法：**
```css
[属性名$="结尾字符串"] {
    property: value;
}
```

**示例：**
```html
<a href="document.pdf">PDF文档</a>
<a href="image.jpg">图片文件</a>
<a href="video.mp4">视频文件</a>
<link rel="stylesheet" href="styles.css">
<script src="app.js"></script>
```

```css
a[href$=".pdf"] {
    color: #e74c3c;
    background-image: url("pdf-icon.png");
    padding-left: 20px;
    background-repeat: no-repeat;
}

a[href$=".jpg"] {
    color: #3498db;
    background-image: url("image-icon.png");
    padding-left: 20px;
    background-repeat: no-repeat;
}

[src$=".js"] {
    type: "module";
}
```

在这个示例中：
- `a[href$=".pdf"]`会选择所有`href`属性值以`.pdf`结尾的链接
- `a[href$=".jpg"]`会选择所有`href`属性值以`.jpg`结尾的链接
- `[src$=".js"]`会选择所有`src`属性值以`.js`结尾的元素

**使用场景：**
- 根据文件类型为链接添加不同样式和图标
- 为特定类型的资源设置样式
- 为特定后缀的文件链接提供视觉提示

### 2.4.6 属性任意位置选择器

属性任意位置选择器用于选择具有特定属性且属性值在任意位置包含指定字符串的元素。

**语法：**
```css
[属性名*="包含字符串"] {
    property: value;
}
```

**示例：**
```html
<div class="product-card">产品卡片</div>
<div class="feature-card">功能卡片</div>
<div class="contact-form">联系表单</div>
<a href="https://example.com/search?q=css">搜索链接</a>
<div data-category="electronics-phone">手机</div>
```

```css
[class*="card"] {
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    padding: 20px;
}

a[href*="search"] {
    background-color: #f8f9fa;
    color: #6c757d;
}

[data-category*="phone"] {
    border-left: 4px solid #007bff;
}
```

在这个示例中：
- `[class*="card"]`会选择所有`class`属性值中包含`card`字符串的元素
- `a[href*="search"]`会选择所有`href`属性值中包含`search`字符串的链接
- `[data-category*="phone"]`会选择所有`data-category`属性值中包含`phone`字符串的元素

**使用场景：**
- 为包含特定子字符串的类名或ID的元素设置样式
- 为URL中包含特定参数的链接设置样式
- 为数据属性中包含特定值的元素设置样式

### 2.4.7 属性选择器的组合使用

可以组合使用多个属性选择器来创建更复杂的选择条件。

**示例：**
```css
/* 选择具有href属性且以https开头、以.pdf结尾的链接 */
a[href^="https"][href$=".pdf"] {
    background-color: #e8f5e9;
    padding: 5px;
    border-radius: 4px;
}

/* 选择具有class属性包含card且data-category属性为featured的元素 */
[class*="card"][data-category="featured"] {
    border: 2px solid #ffc107;
    background-color: #fff8e1;
}

/* 选择type为checkbox且checked的输入框 */
input[type="checkbox"][checked] {
    width: 20px;
    height: 20px;
}
```

**使用场景：**
- 创建复杂的选择条件
- 精确定位特定类型的元素
- 实现高级的样式规则

## 2.5 伪类选择器

### 2.5.1 链接伪类

链接伪类用于设置链接在不同状态下的样式。

**常用链接伪类：**
- `:link` - 未访问的链接
- `:visited` - 已访问的链接
- `:hover` - 鼠标悬停在链接上
- `:active` - 链接被激活（点击时）

**语法：**
```css
选择器:伪类名 {
    property: value;
}
```

**示例：**
```css
a:link {
    color: #3498db;
    text-decoration: none;
}

a:visited {
    color: #9b59b6;
}

a:hover {
    color: #2980b9;
    text-decoration: underline;
    transform: translateY(-2px);
    transition: all 0.3s ease;
}

a:active {
    color: #1f6dad;
    transform: translateY(0);
}
```

**注意事项：**
- 为了确保伪类正确应用，应按照以下顺序声明它们：`:link` -> `:visited` -> `:hover` -> `:active`（记住LVHA顺序）
- `:visited`伪类有一些安全限制，出于隐私原因，只能设置颜色等有限的样式
- `:hover`和`:active`也可以用于非链接元素

### 2.5.2 动态伪类

动态伪类用于设置元素在不同状态下的样式，通常与用户交互相关。

**常用动态伪类：**
- `:hover` - 鼠标悬停在元素上
- `:active` - 元素被激活（点击时）
- `:focus` - 元素获得焦点（通过键盘或点击）
- `:focus-within` - 元素或其任何子元素获得焦点
- `:focus-visible` - 元素通过键盘获得焦点

**示例：**
```css
/* 按钮样式 */
button {
    padding: 10px 20px;
    border: none;
    background-color: #3498db;
    color: white;
    cursor: pointer;
    border-radius: 4px;
    transition: all 0.3s ease;
}

button:hover {
    background-color: #2980b9;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

button:active {
    transform: translateY(2px);
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* 输入框样式 */
input[type="text"] {
    padding: 8px 12px;
    border: 2px solid #ddd;
    border-radius: 4px;
    font-size: 16px;
    transition: border-color 0.3s ease;
}

input[type="text"]:focus {
    outline: none;
    border-color: #3498db;
    box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

/* 表单容器样式 */
.form-container:focus-within {
    background-color: #f8f9fa;
    border: 1px solid #3498db;
}
```

**使用场景：**
- 为按钮和交互元素添加悬停效果
- 改善表单元素的可访问性，通过`:focus`提供清晰的焦点状态
- 使用`:focus-within`为表单容器添加反馈

**可访问性提示：**
- 始终为`:focus`状态提供明显的视觉反馈
- 考虑使用`:focus-visible`来区分鼠标焦点和键盘焦点
- 避免移除`:focus`的轮廓（outline），除非提供了更好的替代样式

### 2.5.3 结构伪类

结构伪类基于元素在文档树中的位置来选择元素。

**常用结构伪类：**
- `:first-child` - 选择作为父元素的第一个子元素的元素
- `:last-child` - 选择作为父元素的最后一个子元素的元素
- `:nth-child(n)` - 选择作为父元素的第n个子元素的元素
- `:nth-last-child(n)` - 选择作为父元素的倒数第n个子元素的元素
- `:only-child` - 选择作为父元素的唯一子元素的元素
- `:first-of-type` - 选择父元素中特定类型的第一个元素
- `:last-of-type` - 选择父元素中特定类型的最后一个元素
- `:nth-of-type(n)` - 选择父元素中特定类型的第n个元素
- `:nth-last-of-type(n)` - 选择父元素中特定类型的倒数第n个元素
- `:only-of-type` - 选择父元素中特定类型的唯一元素
- `:empty` - 选择没有任何子元素（包括文本节点）的元素

**示例：**
```html
<ul class="list">
    <li>第一项</li>
    <li>第二项</li>
    <li>第三项</li>
    <li>第四项</li>
    <li>第五项</li>
</ul>

<div class="container">
    <p>第一个段落</p>
    <div>一个div</div>
    <p>第二个段落</p>
    <p>第三个段落</p>
</div>
```

```css
/* 列表样式 */
.list li:first-child {
    font-weight: bold;
    color: #3498db;
}

.list li:last-child {
    font-style: italic;
    color: #e74c3c;
}

.list li:nth-child(2) {
    background-color: #f1f1f1;
}

/* 选择奇数项 */
.list li:nth-child(odd) {
    background-color: #f9f9f9;
}

/* 选择偶数项 */
.list li:nth-child(even) {
    background-color: #f1f1f1;
}

/* 选择第1、4、7...项 */
.list li:nth-child(3n+1) {
    border-left: 4px solid #27ae60;
}

/* 容器样式 */
.container p:first-of-type {
    font-size: 18px;
    color: #3498db;
}

.container p:last-of-type {
    font-size: 14px;
    color: #7f8c8d;
}

/* 选择空元素 */
.empty-div:empty {
    background-color: #f8d7da;
    border: 1px dashed #dc3545;
    height: 100px;
}
```

**nth-child()的特殊值：**
- `n` - 匹配所有子元素（0, 1, 2, 3...）
- `odd` - 匹配奇数位置的子元素（等同于2n+1）
- `even` - 匹配偶数位置的子元素（等同于2n）
- `an+b` - 匹配位置为an+b的子元素，其中a和b是整数，n从0开始

**使用场景：**
- 创建表格的条纹样式（奇数行和偶数行不同）
- 为列表的首尾项设置特殊样式
- 创建基于位置的布局效果
- 选择特定类型的第一个或最后一个元素

### 2.5.4 表单伪类

表单伪类用于选择表单元素的不同状态。

**常用表单伪类：**
- `:enabled` - 选择可用的表单元素
- `:disabled` - 选择禁用的表单元素
- `:checked` - 选择已选中的单选按钮或复选框
- `:indeterminate` - 选择处于不确定状态的单选按钮或复选框
- `:valid` - 选择有效输入的表单元素
- `:invalid` - 选择无效输入的表单元素
- `:required` - 选择必填的表单元素
- `:optional` - 选择可选的表单元素
- `:in-range` - 选择值在范围内的输入元素
- `:out-of-range` - 选择值超出范围的输入元素

**示例：**
```html
<form>
    <div class="form-group">
        <label for="username">用户名：</label>
        <input type="text" id="username" required>
    </div>
    <div class="form-group">
        <label for="email">邮箱：</label>
        <input type="email" id="email" required>
    </div>
    <div class="form-group">
        <label for="age">年龄：</label>
        <input type="number" id="age" min="18" max="120">
    </div>
    <div class="form-group">
        <label for="bio">个人简介：</label>
        <textarea id="bio"></textarea>
    </div>
    <div class="form-group">
        <label>
            <input type="checkbox" checked> 同意服务条款
        </label>
    </div>
    <div class="form-group">
        <label>
            <input type="radio" name="gender" value="male"> 男
        </label>
        <label>
            <input type="radio" name="gender" value="female"> 女
        </label>
    </div>
    <button type="submit">提交</button>
</form>
```

```css
/* 表单基本样式 */
.form-group {
    margin-bottom: 15px;
}

label {
    display: block;
    margin-bottom: 5px;
    font-weight: bold;
}

input, textarea {
    width: 100%;
    padding: 8px;
    border: 2px solid #ddd;
    border-radius: 4px;
    transition: border-color 0.3s ease;
}

/* 必填字段样式 */
input:required {
    border-color: #3498db;
}

/* 有效输入样式 */
input:valid {
    border-color: #27ae60;
}

/* 无效输入样式 */
input:invalid {
    border-color: #e74c3c;
}

/* 选中的复选框样式 */
input[type="checkbox"]:checked {
    accent-color: #3498db;
}

/* 选中的单选按钮样式 */
input[type="radio"]:checked {
    accent-color: #3498db;
}

/* 在范围内的数值输入样式 */
input[type="number"]:in-range {
    background-color: #e8f5e9;
}

/* 超出范围的数值输入样式 */
input[type="number"]:out-of-range {
    background-color: #ffebee;
    border-color: #e74c3c;
}

/* 禁用的表单元素样式 */
input:disabled, textarea:disabled {
    background-color: #f5f5f5;
    color: #999;
    cursor: not-allowed;
}

/* 聚焦时的样式 */
input:focus, textarea:focus {
    outline: none;
    border-color: #3498db;
    box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}
```

**使用场景：**
- 为表单元素提供实时反馈（有效/无效输入）
- 区分必填和选填字段
- 为选中的选项提供视觉提示
- 为禁用的表单元素设置不同的样式

**注意事项：**
- `:valid`和`:invalid`伪类在用户与表单交互前就会生效，可能导致初始状态不佳
- 可以使用`:focus`伪类来延迟验证反馈，只在用户输入时显示
- 提供清晰的错误信息和帮助文本，而不仅仅依赖颜色来表示状态

### 2.5.5 否定伪类

否定伪类`:not()`用于选择不匹配指定选择器的元素。

**语法：**
```css
:not(选择器) {
    property: value;
}
```

**示例：**
```html
<ul class="menu">
    <li>首页</li>
    <li class="active">产品</li>
    <li>关于我们</li>
    <li>联系我们</li>
</ul>

<div class="container">
    <p>普通段落</p>
    <p class="special">特殊段落</p>
    <p>另一个普通段落</p>
</div>
```

```css
/* 选择菜单中不是活动状态的项目 */
.menu li:not(.active) {
    color: #666;
}

/* 选择活动状态的菜单项 */
.menu li.active {
    color: #3498db;
    font-weight: bold;
}

/* 选择容器中不是特殊段落的段落 */
.container p:not(.special) {
    font-size: 16px;
    line-height: 1.5;
}

/* 选择容器中不是段落的元素 */
.container :not(p) {
    border: 1px solid #ddd;
    padding: 10px;
}

/* 复杂的否定选择器 */
input:not([type="checkbox"]):not([type="radio"]):not(:disabled) {
    background-color: #fff;
    border: 2px solid #ddd;
}
```

**使用场景：**
- 排除特定元素不应用样式
- 减少需要添加的类名数量
- 创建更简洁的CSS代码
- 实现复杂的选择逻辑

**注意事项：**
- `:not()`伪类内可以包含任何简单选择器
- 可以嵌套使用多个`:not()`选择器
- 过度复杂的否定选择器可能影响性能

## 2.6 伪元素选择器

### 2.6.1 伪元素的基本概念

伪元素选择器用于选择元素的特定部分，而不是元素本身。伪元素使用双冒号`::`语法（在CSS3中引入，但单冒号`:``在大多数情况下也能工作，用于向后兼容）。

伪元素允许我们：
- 在元素内容前或后插入内容
- 选择元素的特定部分（如首行、首字母）
- 为元素创建装饰性内容
- 避免不必要的HTML标记

### 2.6.2 常用伪元素

**主要伪元素：**
- `::before` - 在元素内容前插入内容
- `::after` - 在元素内容后插入内容
- `::first-line` - 选择元素的第一行文本
- `::first-letter` - 选择元素的第一个字母
- `::selection` - 选择用户选中的文本
- `::placeholder` - 选择输入框的占位符文本

### 2.6.3 ::before和::after伪元素

`::before`和`::after`伪元素用于在元素的内容前后插入内容。它们通常与`content`属性一起使用。

**语法：**
```css
选择器::before {
    content: "内容";
    /* 其他样式 */
}

选择器::after {
    content: "内容";
    /* 其他样式 */
}
```

**示例：**
```html
<h2>重要提示</h2>
<p class="quote">这是一段引用文本，用于说明问题。</p>
<a href="#" class="external-link">外部链接</a>
<div class="badge">新</div>
```

```css
/* 在标题前添加图标 */
h2::before {
    content: "⚠️ ";
    font-size: 24px;
}

/* 在引用文本前后添加引号 */
.quote::before {
    content: "\"";
    font-size: 32px;
    color: #3498db;
    float: left;
    margin-right: 10px;
    line-height: 1;
}

.quote::after {
    content: "\"";
    font-size: 32px;
    color: #3498db;
    float: right;
    margin-left: 10px;
    line-height: 1;
}

/* 为外部链接添加图标 */
.external-link::after {
    content: " ↗";
    font-size: 12px;
}

/* 创建徽章效果 */
.badge {
    position: relative;
    display: inline-block;
    background-color: #e74c3c;
    color: white;
    padding: 5px 10px;
    border-radius: 15px;
    font-size: 12px;
}

.badge::after {
    content: "";
    position: absolute;
    top: -5px;
    right: -5px;
    width: 10px;
    height: 10px;
    background-color: #f39c12;
    border-radius: 50%;
}
```

**使用场景：**
- 添加装饰性内容（如图标、引号、分隔符）
- 创建特殊效果（如清除浮动的clearfix）
- 实现纯CSS的形状和装饰
- 为元素添加视觉提示

**注意事项：**
- 伪元素必须与`content`属性一起使用，即使内容为空字符串`""`
- 伪元素默认是内联元素，可以通过`display`属性改变其显示类型
- 伪元素是元素的子元素，不是兄弟元素
- 伪元素不能应用于替换元素（如img、input等）

### 2.6.4 ::first-line和::first-letter伪元素

`::first-line`伪元素用于选择文本块的第一行，而`::first-letter`伪元素用于选择文本块的第一个字母。

**语法：**
```css
选择器::first-line {
    /* 样式 */
}

选择器::first-letter {
    /* 样式 */
}
```

**示例：**
```html
<p class="article-text">
    这是一篇文章的第一段。这一行文字可能会因为屏幕宽度的不同而变化长度。
    但是无论如何，第一行的样式都会被特殊处理，而第一个字母也会有特殊的装饰效果。
</p>
```

```css
/* 设置文章首行样式 */
.article-text::first-line {
    font-weight: bold;
    color: #3498db;
    font-size: 1.1em;
}

/* 设置文章首字母样式 */
.article-text::first-letter {
    font-size: 4em;
    line-height: 1;
    float: left;
    margin-right: 10px;
    color: #e74c3c;
    font-family: Georgia, serif;
}
```

**使用场景：**
- 创建杂志风格的首字母大写效果（drop cap）
- 为段落首行添加强调样式
- 增强文章的排版效果

**注意事项：**
- `::first-line`和`::first-letter`只能应用于块级元素
- 可以应用的CSS属性有一定限制（如`::first-line`不能使用`float`等属性）
- `::first-line`选择的内容会根据元素宽度动态变化

### 2.6.5 ::selection伪元素

`::selection`伪元素用于设置用户选中的文本的样式。

**语法：**
```css
::selection {
    /* 样式 */
}

选择器::selection {
    /* 样式 */
}
```

**示例：**
```css
/* 全局选中文本样式 */
::selection {
    background-color: #3498db;
    color: white;
}

/* 特定元素的选中文本样式 */
h1::selection, h2::selection {
    background-color: #e74c3c;
    color: white;
}

/* 与::selection兼容的伪元素 */
::-moz-selection {
    background-color: #3498db;
    color: white;
}

h1::-moz-selection, h2::-moz-selection {
    background-color: #e74c3c;
    color: white;
}
```

**使用场景：**
- 自定义选中文本的外观，增强品牌一致性
- 提高文本在不同背景上的可读性
- 增加用户体验的个性化

**注意事项：**
- 可以设置的CSS属性有限，主要包括`color`、`background-color`、`text-shadow`等
- Firefox使用`::-moz-selection`前缀
- 避免使用过于鲜艳的颜色，影响可读性

### 2.6.6 ::placeholder伪元素

`::placeholder`伪元素用于设置输入框占位符文本的样式。

**语法：**
```css
选择器::placeholder {
    /* 样式 */
}
```

**示例：**
```html
<input type="text" placeholder="请输入用户名" class="input-field">
<input type="email" placeholder="请输入邮箱地址" class="input-field">
<textarea placeholder="请输入详细信息" class="input-field"></textarea>
```

```css
/* 设置占位符样式 */
.input-field::placeholder {
    color: #999;
    font-style: italic;
    font-size: 0.9em;
}

/* 浏览器前缀兼容性 */
.input-field::-webkit-input-placeholder {
    color: #999;
    font-style: italic;
}

.input-field::-moz-placeholder {
    color: #999;
    font-style: italic;
    opacity: 1;
}

.input-field:-ms-input-placeholder {
    color: #999;
    font-style: italic;
}

.input-field:-moz-placeholder {
    color: #999;
    font-style: italic;
    opacity: 1;
}
```

**使用场景：**
- 自定义表单占位符的外观
- 提高占位符文本的可读性
- 与表单整体设计风格保持一致

**注意事项：**
- 不同浏览器需要不同的前缀（`::-webkit-input-placeholder`, `::-moz-placeholder`, `:-ms-input-placeholder`）
- 某些移动浏览器可能对占位符样式的支持有限
- 避免使用与实际输入文本相似的颜色，以免造成混淆

## 2.7 选择器优先级

### 2.7.1 优先级的基本概念

CSS选择器优先级决定了当多个CSS规则应用于同一个元素时，哪一个规则最终会生效。了解优先级规则对于编写可维护和可预测的CSS代码至关重要。

### 2.7.2 优先级的计算规则

CSS优先级按照以下规则从高到低排序：

1. **内联样式**（style属性）- 最高优先级
2. **ID选择器** - 用#表示
3. **类选择器、属性选择器、伪类选择器** - 用.、[]、:表示
4. **元素选择器、伪元素选择器** - 用标签名、::表示

可以使用一个记忆法来记住优先级顺序：!important > 内联样式 > ID > 类/属性/伪类 > 元素/伪元素。

### 2.7.3 优先级的计算方法

优先级可以用一个四位数(a,b,c,d)来表示，其中：
- a: 表示是否使用了!important（1表示使用，0表示未使用）
- b: 表示ID选择器的数量
- c: 表示类选择器、属性选择器、伪类选择器的数量
- d: 表示元素选择器、伪元素选择器的数量

**计算示例：**

| 选择器 | 优先级 (a,b,c,d) | 说明 |
|--------|-----------------|------|
| `p` | (0,0,0,1) | 1个元素选择器 |
| `p.error` | (0,0,1,1) | 1个类选择器 + 1个元素选择器 |
| `.error` | (0,0,1,0) | 1个类选择器 |
| `#content` | (0,1,0,0) | 1个ID选择器 |
| `#content p.error` | (0,1,1,1) | 1个ID选择器 + 1个类选择器 + 1个元素选择器 |
| `a[href^="https"]` | (0,0,1,1) | 1个属性选择器 + 1个元素选择器 |
| `p:hover::first-line` | (0,0,1,2) | 1个伪类选择器 + 1个伪元素选择器 + 1个元素选择器 |
| `style=""` | (0,0,0,0) | 内联样式（特殊情况，优先级高于所有选择器） |
| `!important` | (1,0,0,0) | 最高优先级 |

**优先级比较规则：**
- 首先比较a值，a值大的优先级高
- 如果a值相同，比较b值，b值大的优先级高
- 如果b值相同，比较c值，c值大的优先级高
- 如果c值相同，比较d值，d值大的优先级高
- 如果所有值都相同，则后面定义的规则覆盖前面定义的规则

### 2.7.4 优先级的实际示例

```html
<div id="main">
    <p class="text highlight">这是一段文本</p>
</div>
```

```css
/* 优先级: (0,0,0,1) */
p {
    color: blue;
}

/* 优先级: (0,0,1,0) */
.text {
    color: red;
}

/* 优先级: (0,0,1,1) */
p.highlight {
    color: green;
}

/* 优先级: (0,1,0,1) */
#main p {
    color: purple;
}

/* 优先级: (0,1,1,1) */
#main p.text {
    color: orange;
}
```

在这个示例中，最终文本颜色将是橙色，因为`#main p.text`选择器具有最高的优先级。

### 2.7.5 优先级的最佳实践

1. **避免使用!important**：
   - `!important`会破坏优先级规则，使调试变得困难
   - 只在极少数情况下使用（如覆盖第三方库的样式）
   - 如果必须使用，添加详细注释说明原因

2. **优先使用类选择器**：
   - 类选择器提供了良好的可复用性和优先级平衡
   - 避免过度使用ID选择器，因为它们优先级较高且不可复用

3. **保持选择器简单**：
   - 避免创建过于复杂的选择器，它们难以维护且可能影响性能
   - 遵循"选择器的特异性应与样式的重要性相匹配"的原则

4. **使用BEM等命名约定**：
   - 使用像BEM（Block, Element, Modifier）这样的命名约定可以帮助保持选择器的简单性
   - BEM的命名方式通常使用单一类选择器，避免了复杂的嵌套

5. **利用级联特性**：
   - 理解并利用CSS的级联特性，而不是总是依赖高优先级选择器
   - 考虑使用更具体的HTML结构来避免复杂的选择器

## 2.8 选择器的最佳实践

### 2.8.1 选择器的性能考量

虽然现代浏览器的CSS引擎已经非常高效，但选择器的性能仍然是一个需要考虑的因素，特别是在大型项目中。

**高性能选择器：**
- 类选择器 (`.class`) - 高效且可复用
- ID选择器 (`#id`) - 非常高效但可复用性低

**性能较低的选择器：**
- 通用选择器 (`*`) - 会匹配所有元素，在大型文档中性能较差
- 后代选择器 (`A B`) - 特别是深层嵌套的后代选择器
- 属性选择器 (`[attr=value]`) - 特别是复杂的属性选择器
- 伪类和伪元素 - 某些伪类和伪元素需要额外的计算

**性能优化技巧：**
- 避免使用通用选择器，特别是在大型文档中
- 避免过度嵌套选择器，通常不超过3-4层
- 优先使用类选择器，而不是复杂的组合选择器
- 避免使用通配符属性选择器，如`[class^="btn-"]`
- 使用ID选择器来选择关键元素

### 2.8.2 可维护性和可扩展性

编写可维护和可扩展的CSS选择器对于长期项目的健康发展至关重要。

**可维护性建议：**
- 使用语义化的选择器名称，反映元素的功能而不是外观
- 保持选择器的一致性，遵循团队制定的命名约定
- 为复杂的选择器或特殊的选择策略添加注释
- 避免使用魔术数字和硬编码值

**可扩展性建议：**
- 设计模块化的CSS组件，可以在不同地方重用
- 使用CSS变量（自定义属性）来存储共享值
- 考虑使用CSS预处理器或后处理器来提高代码组织性
- 采用像BEM、ITCSS或SMACSS这样的CSS架构方法

### 2.8.3 选择器的使用场景

不同类型的选择器适合不同的使用场景，以下是一些常见场景的选择器建议：

**组件开发：**
- 优先使用类选择器
- 考虑使用BEM等命名约定
- 避免使用ID选择器以提高复用性

**内容样式化：**
- 使用元素选择器设置基本文本样式
- 使用类选择器为特定内容区块设置样式
- 考虑使用伪元素（如`::first-letter`）增强排版

**表单样式化：**
- 使用属性选择器（如`[type="text"]`）区分不同类型的输入框
- 使用表单伪类（如`:focus`, `:valid`）提供交互反馈
- 保持表单元素的可访问性

**响应式设计：**
- 结合媒体查询和选择器
- 为不同屏幕尺寸使用适当的选择器策略
- 考虑使用相对单位和弹性布局

### 2.8.4 常见的选择器错误和避免方法

**常见错误：**

1. **过度使用ID选择器：**
   ```css
   /* 不好的做法 */
   #header #navigation li a {
       color: #333;
   }
   ```
   解决方案：使用类选择器提高复用性
   ```css
   /* 更好的做法 */
   .nav-link {
       color: #333;
   }
   ```

2. **过度嵌套选择器：**
   ```css
   /* 不好的做法 */
   .container .sidebar .widget .title .icon {
       color: #3498db;
   }
   ```
   解决方案：简化选择器，使用更具描述性的类名
   ```css
   /* 更好的做法 */
   .widget-icon {
       color: #3498db;
   }
   ```

3. **使用通用选择器进行样式重置：**
   ```css
   /* 可能影响性能 */
   * {
       margin: 0;
       padding: 0;
   }
   ```
   解决方案：使用更具体的重置方法或CSS重置库
   ```css
   /* 更有针对性的重置 */
   body, h1, h2, h3, p, ul, ol {
       margin: 0;
       padding: 0;
   }
   ```

4. **使用不语义化的类名：**
   ```css
   /* 不好的做法 */
   .red-text {
       color: red;
   }
   .big-box {
       width: 300px;
   }
   ```
   解决方案：使用语义化的类名
   ```css
   /* 更好的做法 */
   .error-message {
       color: red;
   }
   .product-card {
       width: 300px;
   }
   ```

5. **滥用!important：**
   ```css
   /* 不好的做法 */
   .text {
       color: blue !important;
   }
   ```
   解决方案：使用更具体的选择器或重新组织CSS
   ```css
   /* 更好的做法 */
   .container .text {
       color: blue;
   }
   ```

## 2.9 CSS选择器实战示例

### 2.9.1 示例1：创建一个导航菜单

**HTML结构：**
```html
<nav class="main-nav">
    <ul class="nav-list">
        <li class="nav-item active"><a href="#">首页</a></li>
        <li class="nav-item"><a href="#">产品</a></li>
        <li class="nav-item"><a href="#">服务</a></li>
        <li class="nav-item"><a href="#">关于我们</a></li>
        <li class="nav-item"><a href="#">联系我们</a></li>
    </ul>
</nav>
```

**CSS样式：**
```css
/* 导航菜单容器 */
.main-nav {
    background-color: #2c3e50;
    padding: 0 20px;
}

/* 导航列表 */
.nav-list {
    list-style: none;
    margin: 0;
    padding: 0;
    display: flex;
}

/* 导航项 */
.nav-item {
    margin-right: 5px;
}

/* 导航项 - 最后一项移除右边距 */
.nav-item:last-child {
    margin-right: 0;
}

/* 导航链接 */
.nav-item a {
    display: block;
    padding: 15px 20px;
    color: white;
    text-decoration: none;
    transition: all 0.3s ease;
    position: relative;
}

/* 导航链接悬停效果 */
.nav-item a:hover {
    background-color: #34495e;
}

/* 活动状态的导航链接 */
.nav-item.active a {
    background-color: #3498db;
}

/* 为活动状态添加下划线效果 */
.nav-item.active a::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    width: 100%;
    height: 4px;
    background-color: #e74c3c;
}

/* 为非活动状态的链接添加悬停下划线效果 */
.nav-item:not(.active) a:hover::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    width: 100%;
    height: 4px;
    background-color: #e74c3c;
    transform: scaleX(0);
    transform-origin: bottom right;
    transition: transform 0.3s ease;
}

.nav-item:not(.active) a:hover::after {
    transform-origin: bottom left;
    transform: scaleX(1);
}
```

**选择器说明：**
- `.main-nav` - 类选择器，选择导航容器
- `.nav-list` - 类选择器，选择导航列表
- `.nav-item` - 类选择器，选择导航项
- `.nav-item:last-child` - 组合选择器，选择最后一个导航项
- `.nav-item a` - 后代选择器，选择导航链接
- `.nav-item.active a` - 多类选择器和后代选择器的组合，选择活动状态的导航链接
- `.nav-item.active a::after` - 伪元素选择器，为活动链接添加装饰效果
- `.nav-item:not(.active) a:hover::after` - 否定伪类、伪类和伪元素的组合，为非活动链接添加悬停效果

### 2.9.2 示例2：创建一个响应式表格

**HTML结构：**
```html
<table class="responsive-table">
    <thead>
        <tr>
            <th>产品名称</th>
            <th>价格</th>
            <th>库存</th>
            <th>评分</th>
            <th>操作</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>智能手机</td>
            <td>¥3999</td>
            <td>125</td>
            <td>4.8</td>
            <td><button class="btn">查看详情</button></td>
        </tr>
        <tr class="out-of-stock">
            <td>笔记本电脑</td>
            <td>¥8999</td>
            <td>0</td>
            <td>4.9</td>
            <td><button class="btn" disabled>缺货</button></td>
        </tr>
        <tr>
            <td>平板电脑</td>
            <td>¥2999</td>
            <td>56</td>
            <td>4.7</td>
            <td><button class="btn">查看详情</button></td>
        </tr>
    </tbody>
</table>
```

**CSS样式：**
```css
/* 表格容器 */
.responsive-table {
    width: 100%;
    border-collapse: collapse;
    margin: 20px 0;
    font-size: 16px;
    min-width: 400px;
    border-radius: 5px 5px 0 0;
    overflow: hidden;
    box-shadow: 0 0 20px rgba(0, 0, 0, 0.15);
}

/* 表格头部 */
.responsive-table thead tr {
    background-color: #3498db;
    color: #ffffff;
    text-align: left;
    font-weight: bold;
}

/* 表头单元格 */
.responsive-table th {
    padding: 12px 15px;
}

/* 表格单元格 */
.responsive-table td {
    padding: 12px 15px;
    border-bottom: 1px solid #dddddd;
}

/* 表格行 */
.responsive-table tbody tr {
    border-bottom: 1px solid #dddddd;
    transition: background-color 0.3s ease;
}

/* 表格行 - 偶数行 */
.responsive-table tbody tr:nth-child(even) {
    background-color: #f3f3f3;
}

/* 表格行 - 最后一行 */
.responsive-table tbody tr:last-of-type {
    border-bottom: 2px solid #3498db;
}

/* 表格行 - 悬停效果 */
.responsive-table tbody tr:hover {
    background-color: #f1f1f1;
}

/* 缺货行样式 */
.responsive-table tbody tr.out-of-stock {
    background-color: #ffebee;
    color: #d32f2f;
}

/* 缺货行悬停效果 */
.responsive-table tbody tr.out-of-stock:hover {
    background-color: #ffcdd2;
}

/* 按钮样式 */
.btn {
    background-color: #3498db;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    cursor: pointer;
    transition: background-color 0.3s ease;
}

/* 按钮悬停效果 */
.btn:hover:not(:disabled) {
    background-color: #2980b9;
}

/* 禁用按钮样式 */
.btn:disabled {
    background-color: #cccccc;
    cursor: not-allowed;
}

/* 响应式调整 */
@media (max-width: 768px) {
    /* 响应式表格 */
    .responsive-table {
        display: block;
        width: 100%;
    }
    
    /* 表头在移动设备上隐藏 */
    .responsive-table thead {
        display: none;
    }
    
    /* 表格行在移动设备上作为块元素 */
    .responsive-table tbody, .responsive-table tr, .responsive-table td {
        display: block;
        width: 100%;
    }
    
    /* 表格行在移动设备上添加边框 */
    .responsive-table tr {
        margin-bottom: 15px;
        border: 1px solid #ddd;
        border-radius: 5px;
    }
    
    /* 表格单元格在移动设备上添加伪元素显示标签 */
    .responsive-table td {
        text-align: right;
        position: relative;
        padding-left: 50%;
    }
    
    /* 为单元格添加标签 */
    .responsive-table td::before {
        position: absolute;
        left: 15px;
        width: 45%;
        padding-right: 10px;
        white-space: nowrap;
        font-weight: bold;
        text-align: left;
        content: attr(data-label);
    }
}
```

**选择器说明：**
- `.responsive-table` - 类选择器，选择表格容器
- `.responsive-table thead tr` - 后代选择器，选择表头行
- `.responsive-table th` - 后代选择器，选择表头单元格
- `.responsive-table td` - 后代选择器，选择表格数据单元格
- `.responsive-table tbody tr:nth-child(even)` - 结构伪类选择器，选择表格中的偶数行
- `.responsive-table tbody tr:last-of-type` - 结构伪类选择器，选择表格中的最后一行
- `.responsive-table tbody tr.out-of-stock` - 类选择器，选择缺货的行
- `.btn:hover:not(:disabled)` - 伪类选择器，选择可交互的按钮的悬停状态
- `.btn:disabled` - 伪类选择器，选择禁用的按钮
- `.responsive-table td::before` - 伪元素，为移动设备上的表格单元格添加标签

### 2.9.3 示例3：创建一个表单验证效果

**HTML结构：**
```html
<form class="validation-form">
    <div class="form-group">
        <label for="name">姓名 <span class="required">*</span></label>
        <input type="text" id="name" name="name" required>
        <div class="error-message">请输入姓名</div>
    </div>
    
    <div class="form-group">
        <label for="email">邮箱 <span class="required">*</span></label>
        <input type="email" id="email" name="email" required>
        <div class="error-message">请输入有效的邮箱地址</div>
    </div>
    
    <div class="form-group">
        <label for="password">密码 <span class="required">*</span></label>
        <input type="password" id="password" name="password" required minlength="8">
        <div class="error-message">密码长度至少为8个字符</div>
    </div>
    
    <div class="form-group">
        <label for="confirm-password">确认密码 <span class="required">*</span></label>
        <input type="password" id="confirm-password" name="confirm-password" required>
        <div class="error-message">两次输入的密码不一致</div>
    </div>
    
    <div class="form-group">
        <label>
            <input type="checkbox" name="terms" required>
            我同意服务条款和隐私政策
        </label>
        <div class="error-message">请同意服务条款</div>
    </div>
    
    <button type="submit" class="submit-btn">注册</button>
</form>
```

**CSS样式：**
```css
/* 表单容器 */
.validation-form {
    max-width: 600px;
    margin: 0 auto;
    padding: 20px;
    border-radius: 8px;
    background-color: #f9f9f9;
}

/* 表单组 */
.form-group {
    margin-bottom: 20px;
    position: relative;
}

/* 标签 */
label {
    display: block;
    margin-bottom: 5px;
    font-weight: bold;
    color: #333;
}

/* 必填标记 */
.required {
    color: #e74c3c;
}

/* 输入框 */
input[type="text"],
input[type="email"],
input[type="password"] {
    width: 100%;
    padding: 10px;
    border: 2px solid #ddd;
    border-radius: 4px;
    font-size: 16px;
    transition: border-color 0.3s ease;
}

/* 复选框 */
input[type="checkbox"] {
    margin-right: 10px;
}

/* 输入框聚焦状态 */
input:focus {
    outline: none;
    border-color: #3498db;
    box-shadow: 0 0 5px rgba(52, 152, 219, 0.2);
}

/* 有效输入状态 */
input:valid {
    border-color: #27ae60;
}

/* 无效输入状态 */
input:invalid {
    border-color: #e74c3c;
}

/* 隐藏默认的验证提示 */
input::-webkit-validation-bubble-message {
    display: none;
}

/* 错误消息 */
.error-message {
    display: none;
    color: #e74c3c;
    font-size: 14px;
    margin-top: 5px;
}

/* 无效且已交互的输入框显示错误消息 */
input:invalid:not(:placeholder-shown) + .error-message {
    display: block;
}

/* 必填字段在未填写时的样式 */
input:required:invalid:not(:focus):not(:placeholder-shown) {
    border-color: #e74c3c;
    background-color: #ffebee;
}

/* 必填字段在聚焦时的样式 */
input:required:focus:invalid {
    border-color: #f39c12;
    background-color: #fff8e1;
}

/* 复选框错误状态 */
input[type="checkbox"]:required:invalid + .error-message {
    display: block;
    margin-top: 5px;
}

/* 提交按钮 */
.submit-btn {
    background-color: #3498db;
    color: white;
    border: none;
    padding: 12px 24px;
    font-size: 16px;
    border-radius: 4px;
    cursor: pointer;
    transition: background-color 0.3s ease;
}

/* 提交按钮悬停效果 */
.submit-btn:hover {
    background-color: #2980b9;
}

/* 表单验证提示 */
.validation-form::after {
    content: "* 表示必填项";
    display: block;
    text-align: center;
    margin-top: 20px;
    color: #7f8c8d;
    font-size: 14px;
}
```

**选择器说明：**
- `.validation-form` - 类选择器，选择表单容器
- `.form-group` - 类选择器，选择表单组
- `label` - 元素选择器，选择标签
- `.required` - 类选择器，选择必填标记
- `input[type="text"]` - 属性选择器，选择文本输入框
- `input:focus` - 伪类选择器，选择聚焦状态的输入框
- `input:valid` - 伪类选择器，选择有效状态的输入框
- `input:invalid` - 伪类选择器，选择无效状态的输入框
- `.error-message` - 类选择器，选择错误消息
- `input:invalid:not(:placeholder-shown) + .error-message` - 组合选择器，当输入框无效且有内容时显示错误消息
- `.submit-btn` - 类选择器，选择提交按钮
- `.validation-form::after` - 伪元素，添加表单验证提示

## 2.10 选择器的未来发展

### 2.10.1 新的选择器提案

CSS工作组正在不断开发和标准化新的选择器功能，以下是一些正在开发中的选择器提案：

1. **:has() 伪类**
   - 用于选择包含特定子元素的父元素
   - 例如：`article:has(h2)` 选择包含h2元素的article元素

2. **:where() 和 :is() 伪类**
   - 用于对多个选择器进行分组，不影响优先级
   - 例如：`:is(header, main, footer) p` 等同于 `header p, main p, footer p`

3. **:not() 伪类的扩展**
   - 允许在`:not()`内使用更复杂的选择器列表
   - 例如：`:not(.class1, .class2)` 选择不具有class1或class2的元素

### 2.10.2 CSS选择器与性能优化

随着Web应用变得越来越复杂，选择器的性能优化变得更加重要。以下是一些优化建议：

1. **使用CSS分析工具**
   - 使用工具如Chrome DevTools的Coverage面板或CSS Lint来分析和优化选择器

2. **避免过度使用通配符**
   - 减少通用选择器和属性通配符的使用

3. **使用现代CSS特性**
   - 利用CSS Grid和Flexbox等现代布局技术减少对复杂选择器的依赖

4. **使用CSS变量**
   - 使用CSS变量来减少重复的样式声明，简化选择器结构

### 2.10.3 选择器的最佳学习资源

以下是一些学习和掌握CSS选择器的优质资源：

1. **MDN Web Docs - CSS Selectors**
   - 官方文档，提供全面的选择器参考和示例

2. **CSS-Tricks: Complete Guide to CSS Selectors**
   - 详细的选择器教程，包含实际应用示例

3. **Selectors Level 4 Specification**
   - W3C的最新选择器规范，了解选择器的未来发展

4. **CSS选择器游戏**
   - 互动式学习工具，通过游戏方式掌握选择器

5. **前端框架的选择器实现**
   - 研究React、Vue等框架中的选择器使用方式，学习最佳实践

## 2.11 总结与下一步

### 2.11.1 本章要点回顾

- **基础选择器**：通用选择器、元素选择器、ID选择器、类选择器
- **组合选择器**：后代选择器、子选择器、相邻兄弟选择器、通用兄弟选择器
- **属性选择器**：基于元素属性及其值进行选择的各种方法
- **伪类选择器**：基于元素状态或位置的选择器，如链接状态、表单状态、结构位置等
- **伪元素选择器**：用于选择元素特定部分的选择器，如内容前后、首行、首字母等
- **选择器优先级**：理解不同类型选择器的优先级计算规则
- **最佳实践**：选择器性能优化、可维护性、可扩展性的考量

### 2.11.2 下一步学习建议

- 学习CSS盒模型，了解元素的尺寸计算和布局控制
- 探索CSS布局技术，如Flexbox和Grid
- 研究CSS响应式设计原理和实现方法
- 学习CSS动画和过渡效果
- 尝试使用CSS预处理器（如Sass、Less）来提高CSS开发效率

通过本章的学习，你应该已经掌握了CSS选择器的核心概念和使用方法。选择器是CSS的基础，掌握好选择器对于编写高效、可维护的CSS代码至关重要。在实际项目中，合理选择和组合不同类型的选择器，可以创建出既美观又高效的样式规则。