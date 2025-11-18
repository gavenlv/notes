# 第5章 — Mock 与依赖隔离

目标：
- 理解什么时候需要 mock（外部系统、时间、随机性、网络等）。
- 学会使用 `unittest.mock` 的 `patch`、`Mock`、`MagicMock`。

概念解析
- Mock：模拟对象行为以隔离测试，避免依赖真实外部资源。
- patch：临时替换模块/类/函数中的符号（字符串路径）。

示例：网络请求的封装函数 `fetch_title(url)`，在测试中 mock `requests.get`。
示例代码位于 `testing/unit-test/code/chapter5/`。

最佳实践
- 仅 mock 外部边界（网络、数据库、文件系统）；不要过度 mock 纯业务逻辑。
- patch 的路径应以被测试代码的导入路径为准（即 patch 你代码中实际引用的名字）。

练习
- 为超时、非 200 状态码等场景添加测试。