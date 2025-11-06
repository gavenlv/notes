# 第5天：构建仪表板

## 用户故事1：创建第一个仪表板

**标题**：作为一名数据分析师，我想要创建一个仪表板来展示关键指标，以便与利益相关者分享数据洞察。

**描述**：
Superset允许用户通过组合多个图表和可视化组件来创建交互式仪表板，提供数据的全面视图。

**验收标准**：
- [ ] 仪表板已创建
- [ ] 图表已添加到仪表板
- [ ] 仪表板布局合理
- [ ] 仪表板可访问
- [ ] 仪表板可共享

**分步指南**：

1. **访问仪表板界面**
   - 导航到Superset主页
   - 点击"Dashboards"菜单
   - 点击"+"按钮创建新仪表板

2. **添加图表**
   - 点击"Add Chart"按钮
   - 选择现有图表或创建新图表
   - 将图表拖拽到仪表板中

3. **自定义仪表板**
   - 调整图表大小和位置
   - 添加文本框和分隔符
   - 设置仪表板标题和描述

4. **保存和共享**
   - 点击"Save"按钮
   - 设置仪表板权限
   - 生成共享链接

**参考文档**：
- [仪表板创建指南](https://superset.apache.org/docs/creating-charts-dashboards/creating-dashboards)
- [仪表板编辑](https://superset.apache.org/docs/creating-charts-dashboards/editing-dashboards)

---

## 用户故事2：创建高级图表

**标题**：作为一名数据分析师，我想要创建具有复杂可视化的高级图表，以便呈现复杂的数据洞察。

**描述**：
Superset支持各种图表类型，包括时间序列、散点图、热力图和自定义可视化，以表示不同的数据模式。

**验收标准**：
- [ ] 创建了多种图表类型
- [ ] 图表正确显示数据
- [ ] 交互功能正常工作
- [ ] 图表具有响应性
- [ ] 性能可接受

**分步指南**：

1. **时间序列图**
   ```
   图表类型: 时间序列
   指标: SUM(sales_amount)
   时间列: order_date
   时间范围: 最近30天
   分组依据: product_category
   ```

2. **散点图**
   ```
   图表类型: 散点图
   X轴: customer_age
   Y轴: total_purchase_amount
   大小: purchase_frequency
   颜色: customer_segment
   ```

3. **热力图**
   ```
   图表类型: 热力图
   X轴: product_category
   Y轴: region
   指标: SUM(sales_amount)
   ```

4. **高级功能**
   - 启用"显示值"以显示数据标签
   - 配置配色方案
   - 设置下钻功能
   - 添加自定义工具提示

**参考文档**：
- [图表类型参考](https://superset.apache.org/docs/creating-charts-dashboards/exploring-charts)
- [高级图表配置](https://superset.apache.org/docs/creating-charts-dashboards/advanced-chart-configuration)

---

## 用户故事3：实施仪表板过滤器

**标题**：作为一名仪表板创建者，我想要在仪表板中添加交互式过滤器，以便用户可以动态探索数据。

**描述**：
过滤器允许用户通过选择特定数据子集与仪表板进行交互，使仪表板更有用且更具吸引力。

**验收标准**：
- [ ] 已向仪表板添加过滤器
- [ ] 过滤器在所有图表中生效
- [ ] 过滤器值正确填充
- [ ] 过滤器实时更新图表
- [ ] 过滤器状态已保存

**分步指南**：

1. **添加原生过滤器**
   - 在编辑模式下打开仪表板
   - 点击"添加过滤器"按钮
   - 选择过滤器类型: "原生过滤器"
   - 选择列: "product_category"
   - 配置过滤器选项

2. **配置过滤器属性**
   ```
   过滤器类型: 单选
   默认值: 全部
   搜索: 启用
   排序: 字母顺序
   ```

3. **添加交叉过滤器**
   - 启用"交叉过滤"功能
   - 配置哪些图表响应过滤器
   - 设置过滤器依赖关系

4. **高级过滤器类型**
   - 日期范围过滤器
   - 数值范围过滤器
   - 文本搜索过滤器
   - 自定义SQL过滤器

**参考文档**：
- [原生过滤器指南](https://superset.apache.org/docs/creating-charts-dashboards/native-filters)
- [交叉过滤](https://superset.apache.org/docs/creating-charts-dashboards/cross-filtering)

---

## 用户故事4：创建SQL Lab查询

**标题**：作为一名SQL开发人员，我想要使用SQL Lab编写和测试复杂查询，以便为仪表板创建自定义数据集。

**描述**：
SQL Lab提供了一个强大的界面，用于编写、测试和保存可作为图表和仪表板数据源的SQL查询。

**验收标准**：
- [ ] 可访问SQL Lab界面
- [ ] 查询成功执行
- [ ] 结果正确显示
- [ ] 查询可保存
- [ ] 保存的查询可在图表中使用

**分步指南**：

1. **访问SQL Lab**
   - 导航到SQL Lab → SQL编辑器
   - 选择数据库连接
   - 选择模式/数据库

2. **编写查询**
   ```sql
   SELECT 
       product_category,
       SUM(sales_amount) as total_sales,
       COUNT(*) as order_count,
       AVG(sales_amount) as avg_order_value
   FROM sales_data
   WHERE order_date >= '2023-01-01'
   GROUP BY product_category
   ORDER BY total_sales DESC
   ```

3. **执行和测试**
   - 点击"运行"按钮
   - 查看结果
   - 检查查询性能
   - 如有必要进行优化

4. **保存和使用查询**
   - 点击"保存"以存储查询
   - 名称: "产品销售摘要"
   - 用作图表的数据源

**参考文档**：
- [SQL Lab指南](https://superset.apache.org/docs/using-superset/sql-lab)
- [SQL最佳实践](https://superset.apache.org/docs/using-superset/sql-lab-best-practices)

---

## 用户故事5：创建计划报告

**标题**：作为一名业务用户，我想要设置计划报告，以便利益相关者自动接收定期更新。

**描述**：
Superset可以自动在预定时间生成报告并通过电子邮件发送，确保利益相关者在无需手动干预的情况下获得最新信息。

**验收标准**：
- [ ] 从仪表板创建报告
- [ ] 配置计划
- [ ] 设置电子邮件收件人
- [ ] 自动发送报告
- [ ] 报告格式正确

**分步指南**：

1. **从仪表板创建报告**
   - 打开仪表板
   - 点击"计划"按钮
   - 选择"创建报告"

2. **配置报告设置**
   ```
   报告名称: 周销售摘要
   计划: 每周一上午9:00
   格式: PDF
   收件人: sales-team@company.com
   ```

3. **设置电子邮件配置**
   - 确保在superset_config.py中配置了SMTP
   - 测试电子邮件发送
   - 配置电子邮件模板

4. **监控报告发送**
   - 检查报告日志
   - 验证电子邮件发送
   - 监控报告性能

**参考文档**：
- [计划报告](https://superset.apache.org/docs/using-superset/scheduled-reports)
- [电子邮件配置](https://superset.apache.org/docs/installation/configuring-superset#email)

---

## 仪表板最佳实践

### 1. 性能优化
- 为数据大小使用适当的图表类型
- 实现查询缓存
- 限制图表中的数据点
- 使用数据库级聚合

### 2. 用户体验
- 保持仪表板专注于特定用例
- 使用一致的配色方案
- 提供清晰的标题和描述
- 添加有用的工具提示

### 3. 数据质量
- 验证数据源
- 适当处理缺失数据
- 使用一致的日期格式
- 实施数据刷新计划

### 4. 安全性
- 应用行级安全过滤器
- 限制用户对敏感数据的访问
- 审计仪表板使用情况
- 定期审查权限

## 下一步

完成仪表板创建后，继续：
- [第6天：创建图表和可视化](./day06-charts.md)
- [第7天：SQL Lab与高级查询](./day07-sql-lab.md)