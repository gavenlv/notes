# 3-Tailwind CSS基础用法与第一个示例

现在我们已经安装并配置好了Tailwind CSS，接下来让我们学习它的基础用法，并创建第一个示例项目。

## 3.1 Tailwind CSS的基本使用方式

Tailwind CSS的核心是功能类（utility classes），每个功能类对应一个特定的CSS样式。使用Tailwind CSS时，我们直接在HTML元素上添加这些功能类。

### 3.1.1 功能类的命名规则

Tailwind CSS的功能类命名遵循一定的规则：

- **基础类名 + 连字符 + 数值/修饰符**：例如 `text-lg`、`p-4`、`bg-blue-500`
- **响应式前缀**：例如 `sm:text-lg`、`md:p-4`、`lg:bg-blue-500`
- **状态修饰符**：例如 `hover:text-red-500`、`focus:outline-none`

### 3.1.2 常见的基础功能类

#### 布局类
- `flex`: 弹性布局
- `grid`: 网格布局
- `block`: 块级元素
- `inline`: 行内元素
- `hidden`: 隐藏元素

#### 间距类
- `p-4`: 内边距4个单位（p = padding）
- `m-4`: 外边距4个单位（m = margin）
- `pt-4`: 上内边距4个单位（pt = padding-top）
- `mr-4`: 右外边距4个单位（mr = margin-right）

#### 颜色类
- `bg-blue-500`: 背景色为蓝色（bg = background）
- `text-red-500`: 文字颜色为红色（text = text color）
- `border-gray-300`: 边框颜色为灰色（border = border color）

#### 字体类
- `text-xl`: 字体大小为xl（text = font size）
- `font-bold`: 字体加粗（font = font weight）
- `text-center`: 文字居中（text = text alignment）

## 3.2 创建你的第一个Tailwind CSS示例

让我们创建一个简单的示例页面，展示Tailwind CSS的基本用法。

### 3.2.1 示例HTML结构

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>我的第一个Tailwind CSS示例</title>
  <!-- 引入Tailwind CSS -->
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100 min-h-screen flex items-center justify-center p-4">
  <!-- 卡片容器 -->
  <div class="max-w-md w-full bg-white rounded-lg shadow-lg overflow-hidden">
    <!-- 卡片头部 -->
    <div class="bg-blue-500 px-6 py-4">
      <h1 class="text-white text-2xl font-bold">欢迎使用Tailwind CSS</h1>
    </div>
    <!-- 卡片内容 -->
    <div class="px-6 py-4">
      <p class="text-gray-700 mb-4">
        这是一个使用Tailwind CSS创建的简单卡片示例。Tailwind CSS让我们无需编写自定义CSS，
        直接在HTML中使用预定义的功能类就能构建美观的界面。
      </p>
      <div class="flex space-x-2 mb-4">
        <span class="px-3 py-1 bg-green-100 text-green-800 text-sm font-medium rounded-full">简单易用</span>
        <span class="px-3 py-1 bg-purple-100 text-purple-800 text-sm font-medium rounded-full">高度定制</span>
        <span class="px-3 py-1 bg-yellow-100 text-yellow-800 text-sm font-medium rounded-full">响应式</span>
      </div>
      <!-- 按钮 -->
      <div class="flex space-x-4">
        <button class="bg-blue-500 hover:bg-blue-600 text-white font-medium py-2 px-4 rounded transition-colors">
          了解更多
        </button>
        <button class="bg-gray-200 hover:bg-gray-300 text-gray-800 font-medium py-2 px-4 rounded transition-colors">
          关闭
        </button>
      </div>
    </div>
    <!-- 卡片底部 -->
    <div class="px-6 py-3 bg-gray-50 text-gray-500 text-sm border-t border-gray-100">
      Tailwind CSS基础示例 © 2023
    </div>
  </div>
</body>
</html>
```

### 3.2.2 示例解析

让我们分析一下上面的代码，看看我们使用了哪些Tailwind CSS功能类：

1. **页面背景和布局**：
   - `bg-gray-100`: 设置页面背景色为浅灰色
   - `min-h-screen`: 最小高度为视口高度
   - `flex items-center justify-center`: 使用flex布局并居中内容

2. **卡片样式**：
   - `max-w-md w-full`: 设置最大宽度和宽度
   - `bg-white`: 设置背景色为白色
   - `rounded-lg`: 设置圆角
   - `shadow-lg`: 设置阴影

3. **文本样式**：
   - `text-white`: 白色文字
   - `text-2xl`: 文字大小为2xl
   - `font-bold`: 文字加粗
   - `text-gray-700`: 灰色文字

4. **间距**：
   - `px-6 py-4`: 设置水平内边距为6，垂直内边距为4
   - `mb-4`: 设置底部外边距为4

5. **按钮样式**：
   - `bg-blue-500`: 设置背景色为蓝色
   - `hover:bg-blue-600`: 鼠标悬停时背景色变为深蓝色（状态修饰符）
   - `transition-colors`: 添加颜色过渡效果

## 3.3 实践练习

现在，让我们做一些简单的练习来熟悉Tailwind CSS的基础用法：

### 练习1：修改卡片样式

尝试修改上面示例中的卡片样式，比如：
- 改变卡片的颜色主题
- 调整圆角大小
- 修改阴影效果
- 调整内边距和外边距

### 练习2：添加响应式设计

为卡片添加响应式设计，使其在不同屏幕尺寸下有不同的表现：
- 在小屏幕上（sm）让按钮垂直排列
- 在大屏幕上（lg）增加卡片宽度

## 3.4 小结

本章节我们学习了Tailwind CSS的基础用法，包括功能类的命名规则、常见的基础功能类以及如何创建第一个示例。我们通过一个简单的卡片示例展示了Tailwind CSS的强大功能，并且可以看到使用Tailwind CSS可以快速构建美观的用户界面，无需编写大量自定义CSS。

在下一章节中，我们将深入学习Tailwind CSS的核心概念和更高级的用法，帮助你更好地掌握这个强大的CSS框架。