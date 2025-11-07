# 简单统计面板插件

这是一个Grafana简单统计面板插件的示例，用于学习如何开发自定义Grafana面板插件。

## 功能特性

- 显示简单的统计数值
- 自定义前缀和后缀
- 配置阈值和颜色
- 显示趋势指示
- 响应式设计

## 安装步骤

1. 安装依赖：
   ```bash
   npm install
   ```

2. 构建插件：
   ```bash
   npm run build
   ```

3. 将插件复制到Grafana插件目录：
   ```bash
   sudo cp -r dist /var/lib/grafana/plugins/simple-stat-panel
   ```

4. 重启Grafana：
   ```bash
   sudo systemctl restart grafana-server
   ```

## 开发步骤

1. 克隆插件模板：
   ```bash
   npx @grafana/toolkit plugin:create simple-stat-panel
   ```

2. 进入插件目录：
   ```bash
   cd simple-stat-panel
   ```

3. 开发模式运行：
   ```bash
   npm run dev
   ```

4. 在Grafana中测试插件

## 使用方法

1. 创建新面板
2. 选择"简单统计面板"
3. 配置数据源和查询
4. 自定义显示选项

## 配置选项

- **标题**: 自定义面板标题
- **前缀**: 数值前显示的前缀字符
- **后缀**: 数值后显示的后缀字符
- **小数位数**: 数值显示的小数位数
- **显示趋势**: 是否显示数值趋势
- **警告阈值**: 警告级别阈值
- **危险阈值**: 危险级别阈值

## 开发说明

### 文件结构

```
simple-stat-panel/
├── src/
│   ├── SimpleStatPanel.tsx    # 主面板组件
│   ├── SimpleStatEditor.tsx   # 面板编辑器
│   ├── types.ts               # 类型定义
│   └── module.ts              # 插件入口
├── dist/                      # 构建输出
├── plugin.json                # 插件元数据
├── package.json               # 依赖和脚本
└── README.md                  # 插件文档
```

### 核心组件

1. **SimpleStatPanel**: 渲染统计值的主要组件
2. **SimpleStatEditor**: 配置面板的编辑器组件
3. **Types**: TypeScript类型定义
4. **Module**: 插件导出和配置

### 自定义扩展

要扩展此插件，可以：

1. 添加新的显示选项到`types.ts`
2. 在`SimpleStatPanel.tsx`中实现新的渲染逻辑
3. 在`SimpleStatEditor.tsx`中添加新的配置选项
4. 更新`module.ts`中的面板选项配置

## 故障排除

1. **插件未显示**:
   - 确认插件已正确安装到Grafana插件目录
   - 重启Grafana服务
   - 检查Grafana日志中的错误信息

2. **插件编译错误**:
   - 检查Node.js和npm版本
   - 删除node_modules并重新安装依赖
   - 清除构建缓存

3. **面板无数据**:
   - 检查数据源配置
   - 验证查询语句
   - 确认数据格式

## 参考资料

- [Grafana插件开发文档](https://grafana.com/docs/grafana/latest/developers/plugins/)
- [React官方文档](https://reactjs.org/)
- [TypeScript官方文档](https://www.typescriptlang.org/)