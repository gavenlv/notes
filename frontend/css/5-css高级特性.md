# CSS高级特性

## 5.1 CSS变量

### 5.1.1 CSS变量的基本概念

CSS变量（也称为CSS自定义属性）是CSS3引入的一项强大功能，允许我们在样式表中定义可重用的值。CSS变量使样式的维护变得更加容易，特别是在处理主题、响应式设计和一致的设计系统时。

与预处理器（如Sass、Less）中的变量不同，CSS变量是在浏览器运行时计算的，这意味着它们可以被JavaScript修改，提供了更高的灵活性和动态性。

### 5.1.2 定义和使用CSS变量

**定义CSS变量：**

CSS变量使用`--`前缀定义，可以在任何CSS选择器中声明。通常，我们在`:root`选择器中定义全局变量，这样它们可以在整个文档中使用。

```css
/* 全局变量定义 */
:root {
    --primary-color: #3498db;
    --secondary-color: #2ecc71;
    --font-size: 16px;
    --spacing: 20px;
}

/* 在特定选择器中定义变量 */
.button {
    --button-background: var(--primary-color);
    --button-color: white;
}
```

**使用CSS变量：**

使用`var()`函数来引用CSS变量：

```css
body {
    font-size: var(--font-size);
    color: var(--text-color, #333); /* 设置默认值 #333 */
}

.container {
    padding: var(--spacing);
}

.button {
    background-color: var(--button-background);
    color: var(--button-color);
    padding: 10px calc(var(--spacing) / 2); /* 可以进行计算 */
}
```

### 5.1.3 CSS变量的作用域

CSS变量遵循标准的CSS级联和继承规则：

1. **全局作用域**：在`:root`或`html`选择器中定义的变量在全局范围内可用
2. **局部作用域**：在特定选择器中定义的变量只在该选择器及其子元素中可用
3. **继承性**：子元素可以继承父元素中定义的变量

```css
/* 全局变量 */
:root {
    --color: blue;
}

/* 局部变量 */
.parent {
    --color: green;
}

.child {
    color: var(--color); /* 会使用父元素的绿色 */
}

.another-element {
    color: var(--color); /* 会使用全局的蓝色 */
}
```

### 5.1.4 CSS变量的动态性

CSS变量的一个主要优势是它们可以在运行时被修改，无论是通过添加/修改CSS规则还是通过JavaScript。

**通过CSS修改变量：**

```css
/* 基础变量 */
:root {
    --theme-color: #3498db;
}

/* 在不同状态下修改变量 */
.dark-theme {
    --theme-color: #2c3e50;
}

/* 在媒体查询中修改变量 */
@media (max-width: 768px) {
    :root {
        --spacing: 15px;
        --font-size: 14px;
    }
}
```

**通过JavaScript修改变量：**

```javascript
// 获取根元素
const root = document.documentElement;

// 设置CSS变量
root.style.setProperty('--primary-color', '#e74c3c');

// 获取CSS变量的值
const primaryColor = getComputedStyle(root).getPropertyValue('--primary-color').trim();
console.log(primaryColor); // 输出: #e74c3c

// 在特定元素上设置变量
const button = document.querySelector('.special-button');
button.style.setProperty('--button-background', '#9b59b6');
```

### 5.1.5 CSS变量的应用场景

**1. 主题切换**

```css
/* 浅色主题变量 */
:root {
    --bg-color: #ffffff;
    --text-color: #333333;
    --accent-color: #3498db;
}

/* 深色主题变量 */
.dark-theme {
    --bg-color: #1a1a1a;
    --text-color: #f5f5f5;
    --accent-color: #3498db;
}

/* 使用变量的通用样式 */
body {
    background-color: var(--bg-color);
    color: var(--text-color);
    transition: background-color 0.3s, color 0.3s;
}

.button {
    background-color: var(--accent-color);
    color: white;
}
```

**2. 响应式设计**

```css
:root {
    --container-width: 1200px;
    --column-gap: 20px;
    --font-size: 16px;
}

@media (max-width: 1200px) {
    :root {
        --container-width: 960px;
    }
}

@media (max-width: 768px) {
    :root {
        --container-width: 100%;
        --column-gap: 15px;
        --font-size: 14px;
    }
}

.container {
    max-width: var(--container-width);
    margin: 0 auto;
}

.grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: var(--column-gap);
}

body {
    font-size: var(--font-size);
}
```

**3. 组件样式管理**

```css
/* 按钮组件变量 */
.button {
    --button-padding: 10px 20px;
    --button-bg: #3498db;
    --button-color: white;
    --button-border-radius: 4px;
    --button-hover-bg: #2980b9;
    
    padding: var(--button-padding);
    background-color: var(--button-bg);
    color: var(--button-color);
    border-radius: var(--button-border-radius);
    transition: background-color 0.3s;
}

.button:hover {
    background-color: var(--button-hover-bg);
}

/* 变体按钮 */
.button.secondary {
    --button-bg: #2ecc71;
    --button-hover-bg: #27ae60;
}

.button.danger {
    --button-bg: #e74c3c;
    --button-hover-bg: #c0392b;
}
```

### 5.1.6 CSS变量的浏览器兼容性

CSS变量在大多数现代浏览器中都得到了很好的支持：

- Chrome 49+
- Firefox 44+
- Safari 9.1+
- Edge 15+
- Opera 36+

对于不支持CSS变量的浏览器，可以提供回退值：

```css
.element {
    /* 回退值 */
    background-color: #3498db;
    /* CSS变量 */
    background-color: var(--primary-color);
}
```

## 5.2 CSS动画

### 5.2.1 CSS动画的基本概念

CSS动画允许我们在不使用JavaScript的情况下，通过关键帧定义元素随时间变化的样式。CSS动画由两个主要部分组成：

1. **@keyframes规则**：定义动画的关键帧和它们对应的样式
2. **动画属性**：将动画应用到元素并控制其行为（如持续时间、重复次数等）

### 5.2.2 @keyframes规则

`@keyframes`规则用于定义动画的关键帧序列。我们可以通过百分比或关键词（`from`和`to`）来指定动画在不同阶段的样式。

```css
@keyframes fadeIn {
    from {
        opacity: 0;
    }
    to {
        opacity: 1;
    }
}

@keyframes slideIn {
    0% {
        transform: translateX(-100%);
        opacity: 0;
    }
    50% {
        opacity: 0.5;
    }
    100% {
        transform: translateX(0);
        opacity: 1;
    }
}

@keyframes pulse {
    0% {
        transform: scale(1);
    }
    50% {
        transform: scale(1.1);
    }
    100% {
        transform: scale(1);
    }
}
```

### 5.2.3 动画属性

将动画应用到元素需要使用以下动画属性：

**animation-name** - 指定要使用的@keyframes名称
```css
.element {
    animation-name: fadeIn;
}
```

**animation-duration** - 指定动画完成一个周期所需的时间
```css
.element {
    animation-duration: 1s;
}
```

**animation-timing-function** - 定义动画的速度曲线
```css
.element {
    animation-timing-function: ease; /* 其他值: linear, ease-in, ease-out, ease-in-out, cubic-bezier() */
}
```

**animation-delay** - 指定动画开始前的延迟时间
```css
.element {
    animation-delay: 0.5s;
}
```

**animation-iteration-count** - 指定动画播放的次数
```css
.element {
    animation-iteration-count: 3; /* 或者 infinite 无限循环 */
}
```

**animation-direction** - 指定动画是正向播放、反向播放还是交替播放
```css
.element {
    animation-direction: normal; /* 其他值: reverse, alternate, alternate-reverse */
}
```

**animation-fill-mode** - 指定动画播放前后元素样式的应用方式
```css
.element {
    animation-fill-mode: none; /* 其他值: forwards, backwards, both */
}
```

**animation-play-state** - 控制动画的播放状态
```css
.element {
    animation-play-state: running; /* 或者 paused */
}
```

**animation简写** - 上述所有动画属性的简写形式
```css
.element {
    animation: fadeIn 1s ease 0.5s infinite alternate forwards running;
}
```

### 5.2.4 动画示例

**示例1：淡入动画**
```css
.fade-in {
    animation: fadeIn 1s ease-in forwards;
    opacity: 0; /* 初始状态 */
}

@keyframes fadeIn {
    from {
        opacity: 0;
    }
    to {
        opacity: 1;
    }
}
```

**示例2：滑动动画**
```css
.slide-in {
    animation: slideIn 0.8s ease-out forwards;
    transform: translateX(-100%);
    opacity: 0;
}

@keyframes slideIn {
    to {
        transform: translateX(0);
        opacity: 1;
    }
}
```

**示例3：脉冲动画**
```css
.pulse {
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0%, 100% {
        transform: scale(1);
    }
    50% {
        transform: scale(1.05);
    }
}
```

**示例4：旋转动画**
```css
.spin {
    animation: spin 2s linear infinite;
}

@keyframes spin {
    from {
        transform: rotate(0deg);
    }
    to {
        transform: rotate(360deg);
    }
}
```

**示例5：弹跳动画**
```css
.bounce {
    animation: bounce 1s infinite;
}

@keyframes bounce {
    0%, 20%, 50%, 80%, 100% {
        transform: translateY(0);
    }
    40% {
        transform: translateY(-30px);
    }
    60% {
        transform: translateY(-15px);
    }
}
```

### 5.2.5 动画性能优化

1. **使用变换和不透明度**
   尽量使用`transform`和`opacity`属性进行动画，因为这些属性可以在GPU上进行硬件加速，而不会触发布局重排。

2. **避免使用昂贵的属性**
   避免对`width`、`height`、`margin`、`padding`等会触发布局重排的属性进行动画。

3. **使用`will-change`属性**
   对于将要进行动画的元素，可以提前告知浏览器：
   ```css
   .animated-element {
       will-change: transform, opacity;
   }
   ```
   注意：谨慎使用此属性，只在真正需要的元素上使用。

4. **使用适当的`animation-fill-mode`**
   避免不必要的动画重置和计算。

5. **简化动画复杂度**
   过多的动画关键帧或复杂的计算会增加浏览器负担。

### 5.2.6 高级动画技术

**1. 关键帧动画的组合**

可以将多个动画组合应用到同一个元素：

```css
.element {
    animation: 
        fadeIn 1s ease forwards,
        slideIn 1s ease 0.3s forwards,
        bounce 2s ease 1.5s infinite;
}
```

**2. 路径动画**

使用CSS动画和`transform`创建沿路径运动的动画：

```css
@keyframes pathAnimation {
    0% {
        transform: translate(0, 0) rotate(0deg);
    }
    25% {
        transform: translate(200px, 0) rotate(90deg);
    }
    50% {
        transform: translate(200px, 200px) rotate(180deg);
    }
    75% {
        transform: translate(0, 200px) rotate(270deg);
    }
    100% {
        transform: translate(0, 0) rotate(360deg);
    }
}

.moving-element {
    animation: pathAnimation 8s linear infinite;
    width: 50px;
    height: 50px;
    background-color: #3498db;
    border-radius: 50%;
}
```

**3. 交错动画**

为列表或网格中的多个元素创建交错动画效果：

```css
@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.item {
    animation: fadeInUp 0.5s ease forwards;
    opacity: 0;
}

/* 为每个项目设置不同的延迟 */
.item:nth-child(1) { animation-delay: 0.1s; }
.item:nth-child(2) { animation-delay: 0.2s; }
.item:nth-child(3) { animation-delay: 0.3s; }
.item:nth-child(4) { animation-delay: 0.4s; }
.item:nth-child(5) { animation-delay: 0.5s; }
```

## 5.3 CSS过渡

### 5.3.1 CSS过渡的基本概念

CSS过渡（Transitions）允许我们在元素状态变化时平滑地改变属性值，而不是瞬间改变。这使得用户界面更加流畅和自然。

过渡与动画的主要区别是：过渡需要触发条件（如悬停、聚焦、点击等），而动画可以自动播放。

### 5.3.2 过渡属性

**transition-property** - 指定要过渡的CSS属性
```css
.element {
    transition-property: background-color; /* 或者 all 应用于所有可过渡属性 */
}
```

**transition-duration** - 指定过渡完成所需的时间
```css
.element {
    transition-duration: 0.3s;
}
```

**transition-timing-function** - 定义过渡的速度曲线
```css
.element {
    transition-timing-function: ease; /* 其他值: linear, ease-in, ease-out, ease-in-out, cubic-bezier() */
}
```

**transition-delay** - 指定过渡开始前的延迟时间
```css
.element {
    transition-delay: 0.1s;
}
```

**transition简写** - 上述所有过渡属性的简写形式
```css
.element {
    transition: background-color 0.3s ease 0.1s;
}

/* 多个属性的过渡 */
.element {
    transition: 
        background-color 0.3s ease,
        transform 0.5s ease-out 0.1s;
}

/* 所有属性的过渡 */
.element {
    transition: all 0.3s ease;
}
```

### 5.3.3 可过渡的CSS属性

大多数CSS属性都可以进行过渡，但不是所有属性。以下是一些常用的可过渡属性：

1. **颜色属性**：color, background-color, border-color, etc.
2. **尺寸属性**：width, height, max-width, max-height, etc.
3. **边距和填充**：margin, padding
4. **边框属性**：border-width, border-radius
5. **位置属性**：top, left, right, bottom (当元素定位时)
6. **变换属性**：transform
7. **透明度**：opacity
8. **阴影**：box-shadow, text-shadow
9. **字体属性**：font-size, line-height

### 5.3.4 过渡示例

**示例1：悬停效果**
```css
.button {
    padding: 10px 20px;
    background-color: #3498db;
    color: white;
    border-radius: 4px;
    transition: background-color 0.3s ease, transform 0.2s ease;
}

.button:hover {
    background-color: #2980b9;
    transform: translateY(-2px);
}
```

**示例2：图片缩放**
```css
.image-container {
    overflow: hidden;
    border-radius: 8px;
}

.image-container img {
    width: 100%;
    height: auto;
    transition: transform 0.5s ease;
}

.image-container:hover img {
    transform: scale(1.05);
}
```

**示例3：卡片效果**
```css
.card {
    background-color: white;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    transition: 
        box-shadow 0.3s ease,
        transform 0.3s ease;
}

.card:hover {
    box-shadow: 0 5px 20px rgba(0, 0, 0, 0.15);
    transform: translateY(-5px);
}
```

**示例4：导航菜单**
```css
.nav-link {
    color: #333;
    text-decoration: none;
    padding: 8px 12px;
    position: relative;
    transition: color 0.3s ease;
}

.nav-link::after {
    content: '';
    position: absolute;
    left: 0;
    bottom: 0;
    width: 0;
    height: 2px;
    background-color: #3498db;
    transition: width 0.3s ease;
}

.nav-link:hover {
    color: #3498db;
}

.nav-link:hover::after {
    width: 100%;
}
```

**示例5：渐变背景过渡**
```css
.gradient-box {
    width: 200px;
    height: 200px;
    background: linear-gradient(45deg, #3498db, #2ecc71);
    transition: background 0.5s ease;
}

.gradient-box:hover {
    background: linear-gradient(45deg, #e74c3c, #9b59b6);
}
```

### 5.3.5 过渡的性能考虑

与动画类似，在使用过渡时也应该注意性能问题：

1. **优先使用GPU加速属性**：transform和opacity
2. **避免对会触发布局重排的属性进行频繁过渡**
3. **使用具体的过渡属性而非`all`**：
   ```css
   /* 不好的做法 */
   .element {
       transition: all 0.3s ease;
   }
   
   /* 更好的做法 */
   .element {
       transition: transform 0.3s ease, opacity 0.3s ease;
   }
   ```
4. **避免嵌套过深的过渡效果**：过多的嵌套过渡可能会导致性能问题

## 5.4 CSS变换

### 5.4.1 CSS变换的基本概念

CSS变换（Transforms）允许我们修改元素的形状、大小和位置，而不影响文档流。变换可以应用2D或3D效果，如旋转、缩放、平移和倾斜。

变换是现代UI设计中常用的技术，可以创造出引人注目的视觉效果，同时保持良好的性能。

### 5.4.2 2D变换

#### 5.4.2.1 translate() - 平移
```css
.element {
    transform: translate(50px, 20px); /* X轴平移50px，Y轴平移20px */
    
    /* 单独的轴平移 */
    transform: translateX(50px); /* 仅X轴平移 */
    transform: translateY(20px); /* 仅Y轴平移 */
}
```

#### 5.4.2.2 scale() - 缩放
```css
.element {
    transform: scale(1.5); /* 宽高都放大到1.5倍 */
    transform: scale(1.2, 0.8); /* 宽度放大到1.2倍，高度缩小到0.8倍 */
    
    /* 单独的轴缩放 */
    transform: scaleX(1.5); /* 仅宽度缩放 */
    transform: scaleY(0.8); /* 仅高度缩放 */
}
```

#### 5.4.2.3 rotate() - 旋转
```css
.element {
    transform: rotate(45deg); /* 顺时针旋转45度 */
    transform: rotate(-30deg); /* 逆时针旋转30度 */
}
```

#### 5.4.2.4 skew() - 倾斜
```css
.element {
    transform: skew(10deg, 5deg); /* X轴倾斜10度，Y轴倾斜5度 */
    
    /* 单独的轴倾斜 */
    transform: skewX(10deg); /* 仅X轴倾斜 */
    transform: skewY(5deg); /* 仅Y轴倾斜 */
}
```

#### 5.4.2.5 matrix() - 矩阵变换
```css
.element {
    /* matrix(scaleX, skewY, skewX, scaleY, translateX, translateY) */
    transform: matrix(1, 0.2, 0.8, 1, 10, 20);
}
```

### 5.4.3 3D变换

3D变换与2D变换类似，但增加了Z轴（深度）维度。

#### 5.4.3.1 translate3d() - 3D平移
```css
.element {
    transform: translate3d(50px, 20px, 100px); /* X, Y, Z轴平移 */
    
    /* 单独的轴3D平移 */
    transform: translateX(50px);
    transform: translateY(20px);
    transform: translateZ(100px);
}
```

#### 5.4.3.2 scale3d() - 3D缩放
```css
.element {
    transform: scale3d(1.2, 1.1, 0.8); /* X, Y, Z轴缩放 */
    
    /* 单独的轴3D缩放 */
    transform: scaleX(1.2);
    transform: scaleY(1.1);
    transform: scaleZ(0.8);
}
```

#### 5.4.3.3 rotate3d() - 3D旋转
```css
.element {
    /* rotate3d(x, y, z, angle) - x, y, z是0或1，表示旋转轴 */
    transform: rotate3d(1, 0, 0, 45deg); /* 绕X轴旋转45度 */
    transform: rotate3d(0, 1, 0, 45deg); /* 绕Y轴旋转45度 */
    transform: rotate3d(0, 0, 1, 45deg); /* 绕Z轴旋转45度，等同于2D的rotate() */
    transform: rotate3d(1, 1, 0, 45deg); /* 绕X和Y轴之间的对角线旋转45度 */
    
    /* 特定轴的3D旋转 */
    transform: rotateX(45deg);
    transform: rotateY(45deg);
    transform: rotateZ(45deg);
}
```

#### 5.4.3.4 perspective() - 透视
```css
/* 在父元素上设置透视 */
.container {
    perspective: 1000px;
}

.element {
    transform: rotateY(45deg);
}
```

#### 5.4.3.5 perspective-origin() - 透视原点
```css
.container {
    perspective: 1000px;
    perspective-origin: 50% 50%; /* 默认值，也可以用百分比或具体值 */
}
```

#### 5.4.3.6 backface-visibility() - 背面可见性
```css
.element {
    backface-visibility: hidden; /* 隐藏元素的背面 */
}
```

### 5.4.4 变换原点

通过`transform-origin`属性，我们可以控制变换的原点（默认是元素的中心点）：

```css
.element {
    transform-origin: center; /* 默认值 */
    transform-origin: top left; /* 左上角 */
    transform-origin: bottom right; /* 右下角 */
    transform-origin: 50% 50%; /* 中心点（默认） */
    transform-origin: 20px 30px; /* 具体像素值 */
}
```

### 5.4.5 变换示例

**示例1：卡片翻转效果**
```css
.card-container {
    perspective: 1000px;
    width: 300px;
    height: 400px;
}

.card {
    position: relative;
    width: 100%;
    height: 100%;
    transition: transform 0.6s;
    transform-style: preserve-3d;
}

.card-container:hover .card {
    transform: rotateY(180deg);
}

.card-front, .card-back {
    position: absolute;
    width: 100%;
    height: 100%;
    backface-visibility: hidden;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
    font-weight: bold;
}

.card-front {
    background-color: #3498db;
    color: white;
}

.card-back {
    background-color: #2ecc71;
    color: white;
    transform: rotateY(180deg);
}
```

**示例2：3D立方体**
```css
.cube-container {
    perspective: 1000px;
    width: 200px;
    height: 200px;
    margin: 100px auto;
}

.cube {
    width: 100%;
    height: 100%;
    position: relative;
    transform-style: preserve-3d;
    animation: rotate 10s infinite linear;
}

.cube-face {
    position: absolute;
    width: 200px;
    height: 200px;
    border: 2px solid #333;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
    font-weight: bold;
    opacity: 0.8;
}

.front  { transform: translateZ(100px); background-color: #3498db; color: white; }
.back   { transform: rotateY(180deg) translateZ(100px); background-color: #e74c3c; color: white; }
.right  { transform: rotateY(90deg) translateZ(100px); background-color: #2ecc71; color: white; }
.left   { transform: rotateY(-90deg) translateZ(100px); background-color: #f39c12; color: white; }
.top    { transform: rotateX(90deg) translateZ(100px); background-color: #9b59b6; color: white; }
.bottom { transform: rotateX(-90deg) translateZ(100px); background-color: #1abc9c; color: white; }

@keyframes rotate {
    from { transform: rotateY(0deg); }
    to { transform: rotateY(360deg); }
}
```

**示例3：悬停效果**
```css
.hover-card {
    background-color: white;
    border-radius: 8px;
    padding: 20px;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.hover-card:hover {
    transform: translateY(-5px) scale(1.02);
    box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
}
```

## 5.5 CSS混合模式和滤镜

### 5.5.1 CSS混合模式

CSS混合模式（Blend Modes）允许我们定义元素与其背景或其他元素如何混合颜色。混合模式在图形设计软件中很常见，现在可以直接在CSS中使用。

#### 5.5.1.1 background-blend-mode

`background-blend-mode`用于混合元素的背景图像和背景色，或者多个背景图像之间的混合。

```css
.element {
    background-image: url('image.jpg');
    background-color: #3498db;
    background-blend-mode: overlay; /* 混合模式 */
    background-size: cover;
}

/* 多个背景图像的混合 */
.multiple-backgrounds {
    background-image: url('pattern.png'), url('image.jpg');
    background-blend-mode: multiply, overlay;
    background-size: 200px, cover;
}
```

常用的混合模式包括：normal, multiply, screen, overlay, darken, lighten, color-dodge, color-burn, hard-light, soft-light, difference, exclusion, hue, saturation, color, luminosity等。

#### 5.5.1.2 mix-blend-mode

`mix-blend-mode`用于控制元素与其下方元素的混合方式。

```css
.blended-element {
    mix-blend-mode: difference;
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
}

/* 文本与背景的混合 */
.text-blend {
    mix-blend-mode: screen;
    color: white;
    font-size: 72px;
    font-weight: bold;
}
```

### 5.5.2 CSS滤镜

CSS滤镜（Filters）允许我们对元素应用图形效果，如模糊、灰度、对比度等。滤镜可以应用于任何元素，包括图像、视频、文本等。

#### 5.5.2.1 基本滤镜

```css
.grayscale-image {
    filter: grayscale(100%); /* 完全灰度 */
}

.blur-image {
    filter: blur(5px); /* 模糊效果 */
}

.brightness-image {
    filter: brightness(1.5); /* 增加亮度 */
}

.contrast-image {
    filter: contrast(1.2); /* 增加对比度 */
}

.invert-image {
    filter: invert(100%); /* 反转颜色 */
}

.sepia-image {
    filter: sepia(0.8); /* 棕褐色调 */
}

.saturate-image {
    filter: saturate(2); /* 增加饱和度 */
}

.hue-rotate-image {
    filter: hue-rotate(90deg); /* 色相旋转 */
}

.opacity-image {
    filter: opacity(0.5); /* 透明度 */
}
```

#### 5.5.2.2 复合滤镜

可以组合多个滤镜效果：

```css
.complex-filter {
    filter: grayscale(50%) blur(2px) brightness(1.2) contrast(1.1);
}
```

#### 5.5.2.3 滤镜函数 - drop-shadow()

`drop-shadow()`滤镜创建元素的阴影，类似于`box-shadow`，但它可以跟随元素的形状（包括透明度）。

```css
.shadow-text {
    filter: drop-shadow(2px 4px 6px rgba(0, 0, 0, 0.5));
}

.transparent-png {
    filter: drop-shadow(0 0 5px rgba(0, 0, 0, 0.5));
}
```

### 5.5.3 混合模式和滤镜的应用示例

**示例1：文字特效**
```css
.text-effect {
    font-size: 64px;
    font-weight: bold;
    background-image: linear-gradient(45deg, #3498db, #e74c3c);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    filter: drop-shadow(2px 2px 4px rgba(0, 0, 0, 0.3));
}
```

**示例2：图片悬停效果**
```css
.photo-gallery img {
    transition: all 0.3s ease;
}

.photo-gallery img:hover {
    filter: brightness(1.1) contrast(1.1) saturate(1.2);
    transform: scale(1.02);
}
```

**示例3：叠加效果**
```css
.image-container {
    position: relative;
    width: 300px;
    height: 300px;
}

.background-image {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: #e74c3c;
    mix-blend-mode: overlay;
    opacity: 0.7;
}
```

## 5.6 高级选择器和伪元素技术

### 5.6.1 高级选择器

除了基本选择器和组合选择器外，CSS还提供了一些更高级的选择器：

#### 5.6.1.1 结构化伪类选择器

```css
/* 选择第一个子元素 */
.parent > :first-child {
    color: #3498db;
}

/* 选择最后一个子元素 */
.parent > :last-child {
    color: #e74c3c;
}

/* 选择第n个子元素 */
.parent > :nth-child(3) {
    color: #2ecc71;
}

/* 选择偶数/奇数子元素 */
.parent > :nth-child(even) {
    background-color: #f9f9f9;
}

.parent > :nth-child(odd) {
    background-color: #f1f1f1;
}

/* 反向选择第n个子元素 */
.parent > :nth-last-child(2) {
    font-weight: bold;
}

/* 选择第一个类型为p的子元素 */
.parent > p:first-of-type {
    font-style: italic;
}

/* 选择最后一个类型为p的子元素 */
.parent > p:last-of-type {
    text-decoration: underline;
}

/* 选择第n个类型为p的子元素 */
.parent > p:nth-of-type(2) {
    color: #9b59b6;
}

/* 选择没有子元素的元素 */
.element:empty {
    display: none;
}
```

#### 5.6.1.2 目标伪类选择器

```css
/* 选择当前锚点指向的元素 */
:target {
    background-color: #ffffcc;
    padding: 20px;
    border-left: 4px solid #3498db;
}
```

#### 5.6.1.3 语言伪类选择器

```css
/* 选择特定语言的元素 */
:lang(en) {
    font-family: Arial, sans-serif;
}

:lang(zh) {
    font-family: "Microsoft YaHei", "微软雅黑", sans-serif;
}
```

#### 5.6.1.4 否定伪类选择器

```css
/* 选择不匹配指定选择器的元素 */
li:not(.active) {
    opacity: 0.7;
}

input:not([type="submit"]):not([type="button"]) {
    width: 100%;
}
```

### 5.6.2 高级伪元素技术

#### 5.6.2.1 自定义计数器

使用CSS计数器可以自动为元素编号：

```css
/* 初始化计数器 */
.article {
    counter-reset: section;
}

/* 递增计数器 */
.article h2 {
    counter-increment: section;
}

/* 显示计数器 */
.article h2::before {
    content: "第" counter(section) "章：";
    font-weight: bold;
    color: #3498db;
}

/* 嵌套计数器 */
.article {
    counter-reset: chapter;
}

.article h2 {
    counter-reset: section;
    counter-increment: chapter;
}

.article h2::before {
    content: "第" counter(chapter) "章：";
}

.article h3 {
    counter-increment: section;
}

.article h3::before {
    content: counter(chapter) "." counter(section) " ";
}
```

#### 5.6.2.2 装饰性伪元素效果

```css
/* 自定义列表项标记 */
.custom-list li {
    position: relative;
    padding-left: 30px;
    list-style: none;
}

.custom-list li::before {
    content: "✓";
    position: absolute;
    left: 0;
    color: #2ecc71;
    font-weight: bold;
}

/* 文本引号 */
.quote {
    position: relative;
    padding: 20px;
    font-style: italic;
}

.quote::before,
.quote::after {
    font-size: 50px;
    color: #3498db;
    opacity: 0.5;
    position: absolute;
}

.quote::before {
    content: """;
    top: -10px;
    left: -10px;
}

.quote::after {
    content: """;
    bottom: -40px;
    right: -10px;
}

/* 进度指示器 */
.progress-container {
    position: relative;
    height: 4px;
    background-color: #ecf0f1;
    margin-bottom: 30px;
}

.progress-bar {
    position: absolute;
    top: 0;
    left: 0;
    height: 100%;
    width: 60%;
    background-color: #3498db;
}

.progress-bar::after {
    content: attr(data-progress) "%";
    position: absolute;
    top: -25px;
    right: -20px;
    background-color: #3498db;
    color: white;
    padding: 3px 8px;
    border-radius: 4px;
    font-size: 12px;
}
```

## 5.7 CSS高级特性的最佳实践

### 5.7.1 性能优化建议

1. **合理使用CSS变量**
   - 不要过度使用CSS变量，只在需要重用的值上使用
   - 避免在大量元素上使用不同的局部变量，这可能会降低性能

2. **动画和过渡优化**
   - 优先使用transform和opacity属性进行动画
   - 避免对会触发布局重排的属性进行动画
   - 使用will-change属性谨慎地优化动画性能
   - 对于复杂动画，考虑使用requestAnimationFrame的JavaScript实现

3. **CSS选择器优化**
   - 避免使用复杂的选择器，特别是深层嵌套的选择器
   - 避免使用通用选择器（*）和属性选择器在大型页面上
   - 优先使用类选择器而不是ID选择器（虽然ID选择器更具体，但类选择器更可重用）

4. **CSS文件优化**
   - 精简CSS，移除未使用的样式
   - 使用CSS压缩工具减小文件大小
   - 考虑使用CSS预处理器或后处理器提高开发效率

### 5.7.2 组织和维护建议

1. **使用CSS变量管理主题和设计系统**
   - 在:root中定义全局设计变量
   - 创建一致的颜色系统、间距系统和排版系统

2. **模块化CSS**
   - 使用组件化的CSS结构
   - 考虑使用BEM（Block, Element, Modifier）等命名约定

3. **文档化CSS**
   - 为复杂的CSS技巧和自定义属性添加注释
   - 考虑使用CSS文档工具记录样式指南

4. **版本控制**
   - 对CSS文件进行版本控制
   - 记录重大的CSS架构变更

### 5.7.3 可访问性考虑

1. **动画和可访问性**
   - 为动画提供关闭选项
   - 尊重prefers-reduced-motion媒体查询
   ```css
   @media (prefers-reduced-motion: reduce) {
       .animated-element {
           animation: none;
           transition: none;
       }
   }
   ```

2. **颜色对比度**
   - 确保文本和背景的对比度符合WCAG标准
   - 使用CSS变量管理颜色可以更容易地维护对比度

3. **键盘导航**
   - 确保所有交互元素都可以通过键盘访问
   - 使用:focus伪类提供明显的焦点样式

## 5.8 总结与下一步

### 5.8.1 本章要点回顾

- **CSS变量** - 学习了如何定义和使用CSS变量，以及它们在主题切换、响应式设计和组件样式管理中的应用

- **CSS动画** - 掌握了@keyframes规则和各种动画属性，能够创建复杂的动画效果

- **CSS过渡** - 理解了过渡的基本概念和属性，能够为元素状态变化添加平滑的过渡效果

- **CSS变换** - 学习了2D和3D变换，可以创建旋转、缩放、平移等视觉效果

- **混合模式和滤镜** - 了解了如何使用混合模式和滤镜创建特殊的视觉效果

- **高级选择器和伪元素技术** - 掌握了更多高级选择器和伪元素的用法，能够编写更精确和强大的CSS

### 5.8.2 下一步学习建议

- 学习CSS预处理器（如Sass、Less）和后处理器（如PostCSS）
- 探索CSS框架（如Bootstrap、Tailwind CSS）的高级特性和定制方法
- 学习CSS架构模式（如BEM、ITCSS）
- 研究Web Components和CSS Modules等现代CSS架构方案
- 探索CSS Houdini等前沿CSS技术
- 深入学习CSS性能优化技术

通过本章的学习，你应该已经掌握了CSS的各种高级特性，能够创建更加丰富和动态的用户界面。这些技术在现代Web开发中被广泛应用，可以大大提升网站的视觉吸引力和用户体验。继续深入学习和实践这些技术，你将能够成为一名更加优秀的前端开发者。