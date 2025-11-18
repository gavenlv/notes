# Unit Testing — 从 0 到 专家 (目录)

本目录为中文指南，目标是让 0 基础读者逐步掌握单元测试，并提供每章完整可运行示例。

目录（已生成的章节文件与示例）：

1. `1-章节-介绍.md` — 基础概念与第一个测试（unittest 和 pytest）
2. `2-章节-组织与断言.md` — 组织测试、断言风格、常见断言
3. `3-章节-隔离与生命周期.md` — setup/teardown、fixtures、测试隔离
4. `4-章节-参数化.md` — 参数化测试与表驱动测试
5. `5-章节-mock依赖.md` — Mock、patch、依赖注入
6. `6-章节-TDD与测试设计.md` — TDD 流程、测试驱动设计
7. `7-章节-flaky与性能.md` — flaky tests、性能测试简介与速率稳定性
8. `8-章节-覆盖率与质量门.md` — coverage 及如何设定质量门
9. `9-章节-高级主题.md` — property-based, mutation testing 概述
10. `10-章节-CI与最佳实践.md` — 在 CI 中运行测试，实用技巧

可运行示例代码在 `testing/unit-test/code/` 下，每个章节都有对应的示例文件或子目录。

快速运行（Windows PowerShell）：

```powershell
# 从仓库根目录运行
cd d:\workspace\superset-github\notes
python -m pip install -r testing\unit-test\requirements.txt
python -m pytest testing\unit-test\code -q
```

如需我现在安装依赖并运行测试，请回复“运行并验证”。