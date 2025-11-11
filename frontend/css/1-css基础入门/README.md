# CSS基础入门

## 1.1 CSS简介与基础概念

### 1.1.1 什么是CSS？

CSS（Cascading Style Sheets，层叠样式表）是一种用于描述HTML或XML文档呈现方式的样式语言。CSS的主要作用是将网页内容与其表现形式分离，使网页开发更加灵活和高效。

**为什么需要CSS？**
- **内容与样式分离**：HTML负责内容结构，CSS负责视觉表现
- **提高开发效率**：一次定义，多处复用
- **增强可维护性**：样式集中管理，便于更新
- **改善用户体验**：精致的样式和动效能提升用户体验
- **响应式设计**：轻松适配不同屏幕尺寸

### 1.1.2 CSS的发展历史

CSS自诞生以来经历了多个版本的演进：

- **CSS 1**（1996年）：基础的选择器和属性
- **CSS 2**（1998年）：引入定位、z-index、媒体查询等重要特性
- **CSS 2.1**（2011年）：CSS 2的修订版，修复错误并澄清规范
- **CSS 3**（2001年开始分模块发布）：模块化开发，包含选择器、颜色、盒模型、动画等大量新特性
- **CSS 4+**（持续更新中）：各模块独立发展，如Grid Layout、Flexbox等

### 1.1.3 CSS在网页开发中的角色

在现代网页开发中，CSS与HTML和JavaScript共同构成了前端开发的三大基石：

| 技术 | 主要职责 | 示例 |
|------|----------|------|
| HTML | 内容结构 | `<div>`, `<p>`, `<img>` |
| CSS | 视觉样式 | 颜色、字体、布局、动画 |
| JavaScript | 交互行为 | 事件处理、动态内容 |

## 1.2 CSS的基本语法

### 1.2.1 CSS规则结构

CSS规则由**选择器**和**声明块**组成：

```css
选择器 {  
  属性名1: 属性值1;  
  属性名2: 属性值2;  
  /* 更多声明 */
}
```

- **选择器**：指定要应用样式的HTML元素
- **声明块**：由花括号`{}`包围的一组声明
- **声明**：由属性名和属性值组成，用冒号`:`分隔，用分号`;`结束

**实例：**
```css
h1 {  
  color: blue;  
  font-size: 24px;  
  font-weight: bold;
}
```

### 1.2.2 CSS注释

CSS注释用于解释代码，不会被浏览器解析：

```css
/* 这是一条单行注释 */

/*
这是一条
多行注释
*/

p {  
  color: red; /* 这是一条行内注释 */
}
```

### 1.2.3 CSS属性与值的基本规则

- **属性名**：始终以小写字母开头，多个单词用连字符`-`连接（如`font-size`）
- **属性值**：根据属性类型不同，值的形式也不同
  - 关键字：如`red`, `bold`, `center`
  - 数值：如`12px`, `50%`, `2em`
  - URL：如`url('image.jpg')`
  - 颜色：如`#FF0000`, `rgb(255,0,0)`, `hsl(0,100%,50%)`
- **分号**：每个声明末尾必须有分号
- **空格**：CSS忽略多余的空格，但适当的空格可以提高可读性

## 1.3 CSS的引入方式

### 1.3.1 行内样式

直接在HTML元素的`style`属性中定义CSS样式：

```html
<p style="color: blue; font-size: 18px;">这是一个使用行内样式的段落。</p>
```

**优缺点：**
- **优点**：优先级最高，适用于特定元素的样式调整
- **缺点**：样式与内容耦合，不易维护，复用性差

**最佳实践**：尽量避免使用行内样式，除非是临时调整或特定场景。

### 1.3.2 内部样式表

在HTML文档的`<head>`标签内使用`<style>`标签定义CSS：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>内部样式表示例</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
        }
        h1 {
            color: #2c3e50;
            text-align: center;
        }
    </style>
</head>
<body>
    <h1>内部样式表示例</h1>
    <p>这是一个使用内部样式表的页面。</p>
</body>
</html>
```

**优缺点：**
- **优点**：样式与内容部分分离，适用于单个HTML文件
- **缺点**：样式仅限于当前页面，不能跨页面复用

**最佳实践**：适用于单页应用或小型项目，大型项目推荐使用外部样式表。

### 1.3.3 外部样式表

将CSS代码保存为独立的`.css`文件，然后在HTML中通过`<link>`标签引入：

**HTML文件：**
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>外部样式表示例</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <h1>外部样式表示例</h1>
    <p>这是一个使用外部样式表的页面。</p>
</body>
</html>
```

**CSS文件 (styles.css)：**
```css
body {
    font-family: 'Microsoft YaHei', sans-serif;
    background-color: #f5f5f5;
    margin: 0;
    padding: 20px;
}

h1 {
    color: #3498db;
    border-bottom: 2px solid #3498db;
    padding-bottom: 10px;
}
```

**优缺点：**
- **优点**：样式与内容完全分离，可跨页面复用，易于维护
- **缺点**：需要额外的HTTP请求（可通过合并和压缩优化）

**最佳实践**：推荐用于所有项目，特别是大型项目，便于团队协作和代码维护。

### 1.3.4 @import规则

在CSS文件中引入其他CSS文件：

```css
/* 主CSS文件 */
@import url("reset.css");
@import url("layout.css");

body {
    font-family: Arial, sans-serif;
}
```

**优缺点：**
- **优点**：可以组织和模块化CSS代码
- **缺点**：可能影响页面加载性能，因为@import是串行加载的

**最佳实践**：在性能要求不高的场景下使用，或考虑使用CSS预处理器如Sass/Less来替代。

### 1.3.5 样式优先级比较

不同引入方式的优先级从高到低：
1. 行内样式（直接在元素上的style属性）
2. 内部样式表（`<style>`标签内的样式）
3. 外部样式表（通过`<link>`引入的样式）
4. 浏览器默认样式

**注意**：这种优先级关系仅在选择器相同的情况下成立。实际上，CSS优先级由选择器的特殊性、重要性和源代码顺序共同决定。

## 1.4 CSS颜色表示方法

### 1.4.1 颜色关键字

直接使用预定义的颜色名称：

```css
p {
    color: red;
    background-color: lightblue;
}
```

CSS支持的颜色关键字有140多个，包括：
- 基本颜色：red, green, blue, yellow, black, white等
- 扩展颜色：lightblue, darkgreen, gold, silver等

**注意**：虽然方便，但颜色关键字数量有限，且不同浏览器可能有细微差异。

### 1.4.2 十六进制表示法

使用十六进制（hex）值表示颜色，以`#`开头，后跟6位十六进制数字（0-9, A-F）：

```css
p {
    color: #FF0000;  /* 红色 */
    background-color: #00FF00;  /* 绿色 */
    border: 2px solid #0000FF;  /* 蓝色边框 */
}
```

**简写形式**：如果每两位数字相同，可以简写为3位：
```css
#FF0000 → #F00
#112233 → #123
#AABBCC → #ABC
```

### 1.4.3 RGB和RGBA表示法

**RGB**（Red, Green, Blue）：使用红、绿、蓝三原色的数值（0-255）表示：

```css
p {
    color: rgb(255, 0, 0);  /* 红色 */
    background-color: rgb(0, 255, 0);  /* 绿色 */
    border: 2px solid rgb(0, 0, 255);  /* 蓝色 */
}
```

**RGBA**：在RGB的基础上添加透明度通道（Alpha），取值范围0-1：

```css
p {
    color: rgba(255, 0, 0, 1);  /* 不透明红色 */
    background-color: rgba(0, 0, 255, 0.5);  /* 半透明蓝色 */
    border: 2px solid rgba(0, 255, 0, 0.3);  /* 透明度为0.3的绿色 */
}
```

### 1.4.4 HSL和HSLA表示法

**HSL**（Hue, Saturation, Lightness）：使用色相、饱和度和亮度表示：

```css
p {
    color: hsl(0, 100%, 50%);  /* 红色（色相0度） */
    background-color: hsl(120, 100%, 50%);  /* 绿色（色相120度） */
    border: 2px solid hsl(240, 100%, 50%);  /* 蓝色（色相240度） */
}
```

**参数说明**：
- **Hue**（色相）：取值范围0-360，对应色轮上的颜色（0=红，120=绿，240=蓝）
- **Saturation**（饱和度）：取值范围0%-100%，0%为灰色，100%为纯色
- **Lightness**（亮度）：取值范围0%-100%，0%为黑色，50%为正常，100%为白色

**HSLA**：在HSL的基础上添加透明度通道：

```css
p {
    color: hsla(0, 100%, 50%, 0.8);  /* 透明度为0.8的红色 */
    background-color: hsla(240, 100%, 50%, 0.3);  /* 透明度为0.3的蓝色 */
}
```

### 1.4.5 颜色表示法选择指南

| 表示法 | 适用场景 | 优点 |
|--------|----------|------|
| 颜色关键字 | 简单样式，快速开发 | 语法简洁，易于记忆 |
| 十六进制 | 常用表示法，精确控制 | 浏览器支持广泛，语法简洁 |
| RGB | 需要精确控制三原色 | 直观表示三原色组合 |
| RGBA | 需要透明度控制 | 可以精确控制透明度 |
| HSL | 需要按色相、饱和度、亮度调整 | 更符合人类感知，便于调整色调 |
| HSLA | 需要透明度和HSL控制 | 结合HSL的优点和透明度控制 |

**最佳实践**：
- 对于简单样式，使用颜色关键字或十六进制
- 对于需要透明度的样式，使用RGBA或HSLA
- 对于需要频繁调整色调的场景，推荐使用HSL/HSLA
- 项目中应保持颜色表示法的一致性

## 1.5 CSS字体与文本样式

### 1.5.1 字体基础属性

#### font-family

指定字体系列，浏览器会按顺序尝试使用：

```css
body {
    font-family: 'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
}
```

**注意**：
- 包含空格的字体名称需要用引号包围
- 应提供多个备选字体，最后通常以通用字体族结束（serif, sans-serif, monospace, cursive, fantasy）
- 中文字体通常放在前面，英文字体放在后面

#### font-size

设置字体大小，常用单位：

```css
p {
    font-size: 16px;  /* 像素 */
    font-size: 1em;   /* 相对父元素 */
    font-size: 1rem;  /* 相对根元素(html) */
    font-size: 100%;  /* 百分比 */
    font-size: 12pt;  /* 点（打印样式常用） */
}
```

**最佳实践**：
- 正文文本一般设置为16px，这是浏览器默认值，也是可读性最佳的值
- 推荐使用相对单位（em, rem, %）以提高响应式设计的灵活性
- 使用rem作为主要单位可以更好地支持用户的字体大小偏好设置

#### font-weight

设置字体粗细：

```css
p.normal {
    font-weight: normal;  /* 等同于400 */
}
p.bold {
    font-weight: bold;    /* 等同于700 */
}

/* 数值表示法（100-900，以100为步长） */
h1 {
    font-weight: 900;  /* 最粗 */
}
```

**注意**：并非所有字体都支持所有粗细级别，浏览器会根据可用字重进行回退。

#### font-style

设置字体样式：

```css
p.normal {
    font-style: normal;
}
p.italic {
    font-style: italic;  /* 斜体 */
}
p.oblique {
    font-style: oblique; /* 倾斜（与italic相似但通常是人工倾斜） */
}
```

### 1.5.2 文本样式属性

#### text-align

设置文本水平对齐方式：

```css
h1 {
    text-align: center;  /* 居中对齐 */
}
p {
    text-align: left;    /* 左对齐（默认） */
}
blockquote {
    text-align: right;   /* 右对齐 */
}
.article {
    text-align: justify; /* 两端对齐 */
}
```

#### line-height

设置行高（行间距）：

```css
p {
    line-height: 1.6;  /* 无单位，推荐使用，相对于字体大小 */
    line-height: 24px; /* 固定像素值 */
    line-height: 160%; /* 百分比，相对于字体大小 */
}
```

**最佳实践**：
- 正文文本的行高通常设置为1.5-1.8之间
- 使用无单位的数值可以让行高随着字体大小自动调整
- 过小的行高会降低可读性，过大的行高会浪费空间

#### text-decoration

设置文本装饰：

```css
a {
    text-decoration: none;        /* 无装饰（常用于移除链接下划线） */
}
p.underline {
    text-decoration: underline;   /* 下划线 */
}
p.overline {
    text-decoration: overline;    /* 上划线 */
}
p.strikethrough {
    text-decoration: line-through; /* 删除线 */
}

/* 复合属性 */
p.complex {
    text-decoration: wavy underline red; /* 波浪形红色下划线 */
}
```

#### text-transform

控制文本大小写：

```css
.uppercase {
    text-transform: uppercase;  /* 全部大写 */
}
.lowercase {
    text-transform: lowercase;  /* 全部小写 */
}
.capitalize {
    text-transform: capitalize; /* 首字母大写 */
}
```

#### text-indent

设置文本首行缩进：

```css
.paragraph {
    text-indent: 2em;  /* 缩进2个字符宽度 */
    text-indent: 40px; /* 缩进固定像素值 */
}
```

#### letter-spacing 和 word-spacing

控制字母间距和单词间距：

```css
.wide-letters {
    letter-spacing: 2px; /* 字母间距 */
}
.wide-words {
    word-spacing: 10px; /* 单词间距 */
}
.compact {
    letter-spacing: -0.5px; /* 减小字母间距 */
}
```

### 1.5.3 字体加载与优化

#### Web字体（@font-face）

使用自定义字体：

```css
@font-face {
    font-family: 'MyCustomFont';
    src: url('fonts/myfont.woff2') format('woff2'),
         url('fonts/myfont.woff') format('woff');
    font-weight: normal;
    font-style: normal;
}

body {
    font-family: 'MyCustomFont', sans-serif;
}
```

**字体格式说明**：
- `woff2`：现代压缩格式，支持现代浏览器
- `woff`：较旧但广泛支持的格式
- `ttf`/`otf`：原始字体格式，兼容性好但文件较大

#### 字体显示策略

使用`font-display`属性控制字体加载期间的行为：

```css
@font-face {
    font-family: 'MyCustomFont';
    src: url('fonts/myfont.woff2') format('woff2');
    font-display: swap; /* 推荐使用 */
}
```

**font-display值说明**：
- `auto`：浏览器默认行为
- `block`：先显示不可见文本，加载完成后显示字体（可能导致闪烁）
- `swap`：立即使用后备字体，加载完成后切换（推荐）
- `fallback`：短暂隐藏文本，然后使用后备字体，最后切换
- `optional`：可能不加载自定义字体（如果下载会导致性能问题）

**最佳实践**：
- 始终提供后备字体
- 优化字体文件大小（使用WOFF2格式，考虑子集化）
- 优先使用`font-display: swap`以提高用户体验
- 考虑使用系统字体栈作为备选，减少外部字体依赖

## 1.6 CSS盒模型基础

### 1.6.1 盒模型的基本概念

CSS盒模型是CSS布局的基础，描述了元素在页面上所占空间的计算方式。每个HTML元素都可以看作是一个矩形的盒子，包含以下部分：

1. **内容区域（Content）**：显示实际内容的部分，由width和height属性控制
2. **内边距（Padding）**：内容与边框之间的空间
3. **边框（Border）**：围绕内边距的边界线
4. **外边距（Margin）**：盒子与其他元素之间的空间

![盒模型示意图]

### 1.6.2 标准盒模型与IE盒模型

CSS中有两种盒模型：

**标准盒模型（content-box）**：
- width/height仅包括内容区域
- 总宽度 = width + padding-left + padding-right + border-left + border-right
- 总高度 = height + padding-top + padding-bottom + border-top + border-bottom

**IE盒模型（border-box）**：
- width/height包括内容区域、内边距和边框
- 内容宽度 = width - padding-left - padding-right - border-left - border-right
- 内容高度 = height - padding-top - padding-bottom - border-top - border-bottom

使用box-sizing属性切换盒模型：

```css
/* 标准盒模型（默认） */
.element {
    box-sizing: content-box;
}

/* IE盒模型（推荐使用） */
.element {
    box-sizing: border-box;
}

/* 为所有元素设置IE盒模型（最佳实践） */
* {
    box-sizing: border-box;
}
```

**最佳实践**：推荐在项目中使用`box-sizing: border-box`，因为它更符合直觉，使宽度和高度的计算更加可预测。

### 1.6.3 内边距（Padding）

内边距是内容与边框之间的空间，可以使用一个到四个值来设置：

```css
/* 单个值：四个边的内边距都相同 */
padding: 10px;

/* 两个值：上下内边距 | 左右内边距 */
padding: 5px 10px;

/* 三个值：上内边距 | 左右内边距 | 下内边距 */
padding: 5px 10px 15px;

/* 四个值：上 | 右 | 下 | 左（顺时针方向） */
padding: 5px 10px 15px 20px;

/* 单独设置各个边 */
padding-top: 5px;
padding-right: 10px;
padding-bottom: 15px;
padding-left: 20px;
```

**注意**：内边距会影响元素的总宽度和高度（在标准盒模型中）。

### 1.6.4 边框（Border）

边框围绕着内边距，可以设置样式、宽度和颜色：

```css
/* 简写属性 */
border: 2px solid red;

/* 分别设置 */
border-width: 2px;
border-style: solid;
border-color: red;

/* 设置特定边的边框 */
border-top: 1px dashed blue;
border-bottom: 3px double green;

/* 设置圆角 */
border-radius: 5px;
border-radius: 5px 10px;
/* 椭圆角 */
border-radius: 50% / 20%;
/* 完全圆形 */
border-radius: 50%;
```

**border-style常用值**：
- `solid`：实线
- `dashed`：虚线
- `dotted`：点线
- `double`：双线
- `none`：无边框（默认）
- `hidden`：隐藏边框

### 1.6.5 外边距（Margin）

外边距是元素与其他元素之间的空间，设置方式与内边距类似：

```css
/* 单个值：四个边的外边距都相同 */
margin: 10px;

/* 两个值：上下外边距 | 左右外边距 */
margin: 5px 10px;

/* 三个值：上外边距 | 左右外边距 | 下外边距 */
margin: 5px 10px 15px;

/* 四个值：上 | 右 | 下 | 左（顺时针方向） */
margin: 5px 10px 15px 20px;

/* 单独设置各个边 */
margin-top: 5px;
margin-right: 10px;
margin-bottom: 15px;
margin-left: 20px;

/* 水平居中 */
.element {
    margin: 0 auto;
}
```

**特殊情况**：
- **外边距合并（Margin Collapse）**：当两个垂直方向相邻的元素都设置了外边距时，它们的外边距会合并成一个较大的值（而不是相加）
- **负值外边距**：可以使用负值来重叠元素或扩大布局空间
- **自动外边距**：`margin: auto` 可以使块级元素水平居中

## 1.7 CSS背景样式

### 1.7.1 背景颜色（background-color）

设置元素的背景颜色：

```css
.element {
    background-color: #f0f0f0;
    background-color: rgb(240, 240, 240);
    background-color: rgba(240, 240, 240, 0.8);  /* 半透明 */
    background-color: transparent;  /* 透明 */
}
```

### 1.7.2 背景图像（background-image）

设置元素的背景图像：

```css
.element {
    background-image: url('images/background.jpg');
}

/* 多背景图像 */
.multi-bg {
    background-image: url('images/overlay.png'), url('images/background.jpg');
}
```

### 1.7.3 背景重复（background-repeat）

控制背景图像如何重复：

```css
.element {
    background-repeat: repeat;        /* 水平和垂直都重复（默认） */
    background-repeat: repeat-x;      /* 仅水平重复 */
    background-repeat: repeat-y;      /* 仅垂直重复 */
    background-repeat: no-repeat;     /* 不重复 */
    background-repeat: space;         /* 平铺但不留间隙 */
    background-repeat: round;         /* 平铺但可能缩放以适应 */
}
```

### 1.7.4 背景位置（background-position）

控制背景图像的起始位置：

```css
.element {
    /* 关键字 */
    background-position: top left;    /* 左上角（默认） */
    background-position: center center; /* 居中 */
    background-position: bottom right; /* 右下角 */
    
    /* 像素值 */
    background-position: 10px 20px;   /* 从左上角向右10px，向下20px */
    
    /* 百分比 */
    background-position: 50% 50%;     /* 居中（等同于center center） */
    
    /* 混合使用 */
    background-position: center 20px; /* 水平居中，垂直方向向下20px */
}
```

### 1.7.5 背景大小（background-size）

控制背景图像的大小：

```css
.element {
    /* 关键字 */
    background-size: auto;            /* 原始大小（默认） */
    background-size: cover;           /* 覆盖整个元素，保持宽高比，可能裁剪 */
    background-size: contain;         /* 完全包含在元素内，保持宽高比 */
    
    /* 像素值 */
    background-size: 100px 200px;     /* 宽100px，高200px */
    
    /* 百分比 */
    background-size: 50% 75%;         /* 宽为元素50%，高为元素75% */
    
    /* 单个值（宽度），高度自动保持比例 */
    background-size: 100px;           /* 宽100px，高自动 */
    background-size: 50%;             /* 宽为元素50%，高自动 */
}
```

### 1.7.6 背景附件（background-attachment）

控制背景图像的滚动行为：

```css
.element {
    background-attachment: scroll;    /* 随页面滚动（默认） */
    background-attachment: fixed;     /* 固定在视口中，不随页面滚动 */
    background-attachment: local;     /* 随元素内容滚动 */
}
```

### 1.7.7 背景简写属性

可以使用`background`属性一次性设置多个背景相关属性：

```css
.element {
    background: color image repeat attachment position/size origin clip;
}

/* 示例 */
.my-element {
    background: #f0f0f0 url('image.jpg') no-repeat fixed center/cover;
}
```

**注意**：当使用简写属性时，`background-size`必须紧跟在`background-position`后面，并用斜杠`/`分隔。

### 1.7.8 背景最佳实践

1. **性能优化**：
   - 压缩背景图像
   - 使用适当的图像格式（JPG、PNG、WebP）
   - 对于小图标，考虑使用CSS Sprites或SVG

2. **响应式背景**：
   - 使用`background-size: cover`或`contain`使背景适应不同设备
   - 考虑在不同屏幕尺寸下使用不同的背景图像

3. **可访问性**：
   - 确保背景与前景文本有足够的对比度
   - 如果背景是图像，考虑添加半透明叠加层以提高文本可读性

## 1.8 CSS基础实战示例

### 1.8.1 创建一个简单的个人简介页面

**HTML结构**：
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>个人简介</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <div class="container">
        <header class="header">
            <h1>张三</h1>
            <p>Web前端开发者</p>
        </header>
        
        <section class="about">
            <h2>关于我</h2>
            <p>我是一名热爱Web开发的前端工程师，拥有3年工作经验。精通HTML、CSS、JavaScript，以及现代前端框架如React和Vue。我喜欢创建美观、易用且性能出色的网站和应用程序。</p>
        </section>
        
        <section class="skills">
            <h2>技能</h2>
            <ul>
                <li>HTML5 & CSS3</li>
                <li>JavaScript & ES6+</li>
                <li>React & Vue</li>
                <li>响应式设计</li>
                <li>前端性能优化</li>
            </ul>
        </section>
        
        <footer class="footer">
            <p>联系我：example@email.com</p>
        </footer>
    </div>
</body>
</html>
```

**CSS样式**：
```css
/* 全局重置和基础样式 */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Microsoft YaHei', Arial, sans-serif;
    line-height: 1.6;
    color: #333;
    background-color: #f5f5f5;
}

/* 容器样式 */
.container {
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
}

/* 头部样式 */
.header {
    text-align: center;
    padding: 40px 0;
    background-color: #3498db;
    color: white;
    border-radius: 10px;
    margin-bottom: 30px;
}

.header h1 {
    font-size: 2.5rem;
    margin-bottom: 10px;
}

.header p {
    font-size: 1.2rem;
    opacity: 0.9;
}

/* 内容区块样式 */
section {
    background-color: white;
    padding: 30px;
    margin-bottom: 20px;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

section h2 {
    color: #2c3e50;
    margin-bottom: 20px;
    padding-bottom: 10px;
    border-bottom: 2px solid #3498db;
}

/* 技能列表样式 */
.skills ul {
    list-style-type: none;
}

.skills li {
    padding: 10px 0;
    padding-left: 25px;
    position: relative;
}

.skills li::before {
    content: '✓';
    color: #27ae60;
    position: absolute;
    left: 0;
    font-weight: bold;
}

/* 页脚样式 */
.footer {
    text-align: center;
    padding: 20px;
    color: #7f8c8d;
    font-size: 0.9rem;
}

/* 响应式调整 */
@media (max-width: 600px) {
    .container {
        padding: 10px;
    }
    
    .header h1 {
        font-size: 2rem;
    }
    
    section {
        padding: 20px;
    }
}
```

### 1.8.2 创建一个漂亮的卡片组件

**HTML结构**：
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CSS卡片示例</title>
    <link rel="stylesheet" href="card.css">
</head>
<body>
    <div class="card-container">
        <div class="card">
            <div class="card-image">
                <img src="https://picsum.photos/600/400?random=1" alt="风景照片">
            </div>
            <div class="card-content">
                <h3>风景卡片</h3>
                <p>这是一个展示自然风景的卡片示例。使用CSS可以创建出精美的卡片设计，包含图片、标题和描述文字。</p>
                <a href="#" class="card-button">查看详情</a>
            </div>
        </div>
        
        <div class="card">
            <div class="card-image">
                <img src="https://picsum.photos/600/400?random=2" alt="城市照片">
            </div>
            <div class="card-content">
                <h3>城市卡片</h3>
                <p>这是一个展示城市景观的卡片示例。卡片设计在现代网页中非常流行，能够有效地组织和展示信息。</p>
                <a href="#" class="card-button">查看详情</a>
            </div>
        </div>
        
        <div class="card">
            <div class="card-image">
                <img src="https://picsum.photos/600/400?random=3" alt="美食照片">
            </div>
            <div class="card-content">
                <h3>美食卡片</h3>
                <p>这是一个展示美食的卡片示例。通过精心的设计，可以让卡片在悬停时有动画效果，提升用户体验。</p>
                <a href="#" class="card-button">查看详情</a>
            </div>
        </div>
    </div>
</body>
</html>
```

**CSS样式**：
```css
/* 全局重置 */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Microsoft YaHei', Arial, sans-serif;
    background-color: #f8f9fa;
    padding: 20px;
}

/* 卡片容器 */
.card-container {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 30px;
    max-width: 1200px;
    margin: 0 auto;
}

/* 卡片基础样式 */
.card {
    background-color: white;
    border-radius: 10px;
    overflow: hidden;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

/* 卡片悬停效果 */
.card:hover {
    transform: translateY(-10px);
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
}

/* 卡片图片 */
.card-image {
    height: 200px;
    overflow: hidden;
}

.card-image img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.5s ease;
}

.card:hover .card-image img {
    transform: scale(1.1);
}

/* 卡片内容 */
.card-content {
    padding: 20px;
}

.card-content h3 {
    color: #333;
    margin-bottom: 15px;
    font-size: 1.5rem;
}

.card-content p {
    color: #666;
    line-height: 1.6;
    margin-bottom: 20px;
}

/* 卡片按钮 */
.card-button {
    display: inline-block;
    padding: 10px 20px;
    background-color: #3498db;
    color: white;
    text-decoration: none;
    border-radius: 5px;
    font-weight: 500;
    transition: background-color 0.3s ease;
}

.card-button:hover {
    background-color: #2980b9;
}

/* 响应式调整 */
@media (max-width: 768px) {
    .card-container {
        grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
        gap: 20px;
    }
}

@media (max-width: 480px) {
    .card-container {
        grid-template-columns: 1fr;
    }
    
    .card-image {
        height: 180px;
    }
}
```

## 1.9 CSS基础最佳实践

### 1.9.1 编码规范与组织

1. **使用一致的命名约定**：
   - 选择一种命名约定并保持一致（如BEM、SMACSS等）
   - 使用有意义的类名，避免无意义的命名（如`left-col`, `big-text`）
   - 类名应使用小写字母，单词之间用连字符分隔

2. **CSS文件组织**：
   - 按功能模块化组织CSS（重置、基础、组件、布局、页面特定样式）
   - 使用CSS预处理器（如Sass、Less）进行高级组织
   - 大型项目考虑使用CSS模块化或CSS-in-JS

3. **代码格式化**：
   - 每个属性单独一行
   - 使用缩进（2或4个空格）提高可读性
   - 大括号使用一致的风格
   - 颜色、尺寸等数值使用一致的表示法

### 1.9.2 性能优化

1. **减少CSS体积**：
   - 使用CSS压缩工具（如csso、clean-css）
   - 删除未使用的CSS（使用工具如purgecss）
   - 合并多个CSS文件减少HTTP请求

2. **选择器优化**：
   - 避免过度嵌套选择器（最多3-4层）
   - 避免使用通用选择器（*）
   - 优先使用类选择器，减少ID和标签选择器的使用

3. **关键CSS**：
   - 将首屏渲染所需的CSS内联到HTML中
   - 使用媒体查询拆分非关键CSS

4. **字体优化**：
   - 使用系统字体栈作为备选
   - 优化Web字体加载（使用WOFF2格式，适当的字体显示策略）

### 1.9.3 可维护性

1. **注释**：
   - 为复杂的样式添加注释
   - 使用注释标记不同的样式区块
   - 注释关键的设计决策

2. **变量**：
   - 使用CSS变量（Custom Properties）存储颜色、字体大小等共享值
   - 定义主题变量方便切换

3. **重用样式**：
   - 创建可重用的工具类
   - 避免重复代码，使用组合继承方式

4. **响应式设计**：
   - 采用移动优先的设计方法
   - 使用相对单位（rem, em, %）而非固定像素值
   - 合理设置媒体查询断点

### 1.9.4 可访问性

1. **颜色对比度**：
   - 确保文本与背景有足够的对比度（至少4.5:1）
   - 不要仅依赖颜色来传达信息

2. **语义化HTML**：
   - 使用正确的HTML元素结构
   - CSS应增强而不是破坏语义

3. **键盘可访问性**：
   - 确保所有交互元素都可通过键盘访问
   - 提供明显的焦点样式

4. **动画和过渡**：
   - 为动画提供用户偏好设置（prefers-reduced-motion）
   - 避免可能导致不适的动画效果

### 1.9.5 开发工作流

1. **使用构建工具**：
   - 配置自动编译、压缩和优化CSS的工作流
   - 使用PostCSS进行现代CSS转换

2. **版本控制**：
   - 将CSS文件纳入版本控制
   - 编写有意义的提交信息

3. **测试**：
   - 在不同浏览器中测试CSS
   - 使用工具检查CSS兼容性

4. **文档**：
   - 为团队项目创建CSS指南文档
   - 记录组件样式和设计系统

## 1.10 下一步学习方向

恭喜你完成了CSS基础入门的学习！以下是推荐的后续学习方向：

1. **CSS选择器**：学习各种高级选择器，如属性选择器、伪类、伪元素等
2. **CSS盒模型**：深入理解标准盒模型和替代盒模型的区别和应用
3. **CSS布局技术**：学习Flexbox、Grid等现代布局技术
4. **CSS高级特性**：如CSS变量、动画与过渡、变换效果等
5. **响应式设计**：学习媒体查询和响应式设计原则
6. **CSS预处理器**：如Sass、Less的使用
7. **CSS架构模式**：如BEM、SMACSS等
8. **性能优化**：深入学习CSS性能优化技巧

继续学习，你将掌握更多CSS高级技巧，能够创建更加精美和交互性强的网页！

---

**作者提示**：本章节内容涵盖了CSS的基础知识，通过实践示例帮助你理解和应用这些概念。在继续学习高级内容之前，建议先完成本章的实战示例，确保你已经掌握了基础概念和语法。