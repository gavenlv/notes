# CSS基础

## 什么是CSS？

CSS（Cascading Style Sheets，层叠样式表）是一种用于描述HTML或XML文档呈现方式的样式语言。CSS定义了网页元素的外观，包括颜色、字体、布局等，使开发者能够将网页的结构（HTML）与表现（样式）分离。

**CSS的核心价值**：
- **分离关注点**：HTML负责结构，CSS负责样式
- **可维护性**：集中管理样式，易于修改
- **一致性**：应用统一的设计风格
- **响应式设计**：适应不同设备和屏幕尺寸

## CSS基础语法

CSS的基本单位是规则集（rule set），也称为规则。每个规则由选择器（selector）和声明块（declaration block）组成。

### 规则集的基本结构

```css
选择器 {  
    属性名: 属性值;  /* 声明 */  
    属性名: 属性值;  /* 声明 */
}
```

### 示例

```css
/* 为所有段落设置样式 */
p {
    color: blue;           /* 文本颜色为蓝色 */
    font-size: 16px;       /* 字体大小为16像素 */
    line-height: 1.5;      /* 行高为字体大小的1.5倍 */
    margin-bottom: 10px;   /* 底部外边距为10像素 */
}
```

## 如何在HTML中使用CSS

CSS可以通过三种方式应用到HTML文档中：

### 1. 内联样式（Inline Styles）

直接在HTML元素中使用`style`属性。

```html
<p style="color: red; font-size: 18px;">这是一个红色的段落。</p>
```

**优点**：优先级最高，直接应用到特定元素
**缺点**：样式与结构混合，不易维护，违反关注点分离原则

### 2. 内部样式表（Internal Style Sheet）

在HTML文档的`<head>`部分使用`<style>`标签定义样式。

```html
<head>
    <style>
        p {
            color: green;
            font-size: 16px;
        }
        h1 {
            color: blue;
            text-align: center;
        }
    </style>
</head>
```

**优点**：集中在一个HTML文件中，适用于单个页面
**缺点**：样式不能在多个页面间共享

### 3. 外部样式表（External Style Sheet）

将CSS代码保存在单独的`.css`文件中，然后在HTML文档中通过`<link>`标签引入。

**步骤**：
1. 创建CSS文件（例如：`styles.css`）
2. 在HTML文档的`<head>`部分添加链接

```html
<head>
    <link rel="stylesheet" href="styles.css">
</head>
```

**优点**：
- 样式与结构完全分离
- 可在多个HTML页面间共享
- 提高加载速度（浏览器可以缓存CSS文件）
- 便于团队协作和维护

**推荐做法**：优先使用外部样式表，这是专业开发中的标准做法。

## CSS选择器

选择器用于指定要应用样式的HTML元素。CSS提供了多种选择器，以适应不同的选择需求。

### 基本选择器

#### 1. 元素选择器（Type Selector）

使用HTML元素名称选择所有指定类型的元素。

```css
p { color: blue; }
/* 选择所有段落元素 */

h1 { font-size: 24px; }
/* 选择所有一级标题元素 */
```

#### 2. 类选择器（Class Selector）

使用`.`符号后跟类名选择所有包含该类的元素。类可以在多个元素上使用。

```css
.text-primary { color: #3498db; }
/* 选择所有class="text-primary"的元素 */

.container { max-width: 1200px; margin: 0 auto; }
/* 选择所有class="container"的元素 */
```

HTML中使用：
```html
<p class="text-primary">这是一个主要文本。</p>
<div class="container">这是一个容器。</div>
```

#### 3. ID选择器（ID Selector）

使用`#`符号后跟ID选择具有特定ID的元素。ID在一个HTML文档中应该是唯一的。

```css
#header { background-color: #333; color: white; }
/* 选择id="header"的元素 */

#login-form { border: 1px solid #ccc; padding: 20px; }
/* 选择id="login-form"的元素 */
```

HTML中使用：
```html
<header id="header">网站头部</header>
<form id="login-form">登录表单</form>
```

#### 4. 通用选择器（Universal Selector）

使用`*`选择页面上的所有元素。

```css
* { box-sizing: border-box; }
/* 为所有元素设置盒模型为border-box */

* { margin: 0; padding: 0; }
/* 重置所有元素的外边距和内边距 */
```

### 组合选择器

#### 1. 后代选择器（Descendant Selector）

使用空格分隔两个选择器，选择第一个选择器匹配元素的所有后代元素。

```css
nav ul { list-style: none; }
/* 选择nav元素内的所有ul元素 */

.container p { font-size: 14px; }
/* 选择container类内的所有p元素 */
```

#### 2. 子选择器（Child Selector）

使用`>`分隔两个选择器，选择第一个选择器匹配元素的直接子元素。

```css
nav > ul { margin-top: 0; }
/* 选择nav元素的直接子元素ul */

article > h2 { color: #e74c3c; }
/* 选择article元素的直接子元素h2 */
```

#### 3. 相邻兄弟选择器（Adjacent Sibling Selector）

使用`+`分隔两个选择器，选择第一个选择器匹配元素之后紧邻的同级元素。

```css
h1 + p { font-style: italic; }
/* 选择h1元素后紧邻的p元素 */

div + .box { border-top: 2px solid #333; }
/* 选择div元素后紧邻的box类元素 */
```

#### 4. 通用兄弟选择器（General Sibling Selector）

使用`~`分隔两个选择器，选择第一个选择器匹配元素之后的所有同级元素。

```css
h2 ~ p { color: #7f8c8d; }
/* 选择h2元素后的所有同级p元素 */

input:checked ~ label { text-decoration: line-through; }
/* 选择被选中的input后的所有label元素 */
```

### 伪类和伪元素选择器

#### 伪类（Pseudo-classes）

伪类用于选择元素的特定状态或关系。它们以冒号（`:`）开头。

常见的伪类：

```css
/* 链接状态 */
a:link { color: #3498db; }      /* 未访问的链接 */
a:visited { color: #9b59b6; }   /* 已访问的链接 */
a:hover { color: #e74c3c; }     /* 鼠标悬停在链接上 */
a:active { color: #2ecc71; }    /* 激活的链接（点击时） */

/* 表单元素状态 */
input:focus { border-color: #3498db; }
/* 元素获取焦点时 */

input:checked { /* 选中的复选框或单选按钮 */ }
input:disabled { /* 禁用的表单元素 */ }

/* 结构伪类 */
ul li:first-child { font-weight: bold; }
/* 列表中的第一个子项 */
ul li:last-child { margin-bottom: 0; }
/* 列表中的最后一个子项 */
ul li:nth-child(2) { color: red; }
/* 列表中的第二个子项 */
ul li:nth-child(even) { background-color: #f2f2f2; }
/* 列表中的偶数子项 */
ul li:nth-child(odd) { background-color: #fff; }
/* 列表中的奇数子项 */
```

#### 伪元素（Pseudo-elements）

伪元素用于选择元素的特定部分。它们以双冒号（`::`）开头，但有些旧版伪元素也支持单冒号。

```css
/* 文本相关伪元素 */
p::first-line { font-weight: bold; }
/* 段落的第一行 */
p::first-letter { font-size: 2em; float: left; margin-right: 5px; }
/* 段落的第一个字母 */

h1::before { content: "★ "; }
/* 在h1元素内容前插入内容 */
h1::after { content: " ★"; }
/* 在h1元素内容后插入内容 */

/* 选择文本 */
::selection { background-color: #ffeaa7; }
/* 选中的文本 */
```

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

## CSS的特殊性和继承

### CSS继承

某些CSS属性会从父元素继承到子元素，而其他属性则不会。

**通常会继承的属性**：
- 字体相关：`font-family`, `font-size`, `font-weight`, `font-style`
- 文本相关：`color`, `line-height`, `text-align`, `text-indent`
- 列表相关：`list-style-type`, `list-style-position`

**通常不会继承的属性**：
- 盒子模型：`width`, `height`, `margin`, `padding`, `border`
- 定位：`position`, `top`, `left`, `bottom`, `right`
- 背景：`background-color`, `background-image`
- 布局：`display`, `float`, `clear`

可以使用以下关键字控制继承：

```css
/* 强制继承父元素的值 */
child-element {
    color: inherit;
}

/* 设置为默认值 */
element {
    color: initial;
}

/* 应用浏览器默认样式 */
element {
    color: unset;
}
```

## CSS注释

CSS注释以`/*`开始，以`*/`结束，可以跨越多行。

```css
/* 这是一个单行注释 */

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

## CSS命名约定

良好的CSS命名约定可以提高代码的可读性和可维护性。

### BEM命名法

BEM（Block, Element, Modifier）是一种流行的CSS命名约定。

- **Block**：独立的、可重用的组件
- **Element**：块内的子元素，依赖于块
- **Modifier**：块或元素的状态或变体

```css
/* 块 */
.header {}

/* 元素 */
.header__logo {}
.header__nav {}
.header__link {}

/* 修饰符 */
.header--dark {}
.header__link--active {}
```

### 其他命名约定

- **使用连字符**：`.button-primary` 而不是 `.buttonPrimary` 或 `.button_primary`
- **语义化命名**：`.nav-item` 而不是 `.item` 或 `.blue-text`
- **避免ID**：优先使用类，因为ID不能重用且优先级过高
- **保持一致性**：在整个项目中使用相同的命名风格

## CSS最佳实践

### 代码组织

1. **按逻辑分组**：将相关的样式分组（如布局、组件、响应式等）
2. **使用注释**：为不同的部分添加注释，提高代码可读性
3. **模块化**：将CSS拆分为多个文件，分别处理不同的功能（如`reset.css`, `layout.css`, `components.css`等）

### 性能优化

1. **减少CSS体积**：删除未使用的CSS，合并文件
2. **使用CSS预处理器**：如Sass、Less可以减少重复代码
3. **避免使用通用选择器**：通用选择器(`*`)会匹配所有元素，影响性能
4. **避免深层次嵌套**：减少选择器的复杂性，降低优先级计算的负担
5. **使用简写属性**：如`margin`, `padding`, `background`等

### 可维护性

1. **遵循一致的命名约定**：如BEM
2. **使用有意义的类名**：避免使用无意义的名称（如`.left`, `.top`）
3. **避免使用`!important`**：除非绝对必要
4. **合理使用CSS变量**：便于主题切换和全局样式管理
5. **编写响应式CSS**：使用媒体查询确保在不同设备上的良好体验

## 练习题

### 练习题1：CSS基础选择器

创建一个HTML文件，包含以下元素：
- 一个`header`元素，带有`class="site-header"`
- 一个`nav`元素，包含一个无序列表，列表项包含链接
- 一个`main`元素，包含3个`section`
- 每个`section`包含一个`h2`标题和几个段落
- 为第一个`section`添加`class="intro"`
- 为第三个`section`添加`id="contact"`

然后创建一个CSS文件，实现以下样式：
1. 为`body`设置基本的字体和颜色
2. 为`header`设置背景色和内边距
3. 为`nav`中的链接添加样式，并添加`hover`效果
4. 为`section`设置外边距和内边距
5. 为`class="intro"`的`section`添加特殊样式
6. 为`id="contact"`的`section`添加另一种特殊样式
7. 为所有`h2`标题设置样式

### 练习题2：CSS盒模型和布局

创建一个HTML文件，实现以下布局：
1. 一个容器`div`，宽度固定，水平居中
2. 容器内有三个子`div`，分别是：
   - 左侧边栏（宽度25%）
   - 主要内容区（宽度50%）
   - 右侧边栏（宽度25%）
3. 使用浮动或Flexbox实现水平排列
4. 为每个区域添加内边距和边框
5. 确保在窗口变小时，布局能够优雅地降级为垂直排列

### 练习题3：CSS响应式设计

创建一个简单的响应式网页，包含：
1. 一个顶部导航栏
2. 一个主要内容区，包含三列卡片布局
3. 一个页脚

使用媒体查询实现以下效果：
- 在大屏幕上（≥1200px）：三列卡片并排
- 在中等屏幕上（992px-1199px）：三列卡片保持并排，但宽度自适应
- 在平板上（768px-991px）：改为两列卡片布局
- 在移动设备上（<768px）：改为单列卡片布局，导航栏变为汉堡菜单

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