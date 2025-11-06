# Python数据科学环境

这个示例演示如何配置一个完整的Python数据科学开发环境，包含常用的数据科学库和工具。

## 功能特性

- ✅ Python 3.11 运行环境
- ✅ 完整的数据科学库（NumPy, Pandas, Scikit-learn等）
- ✅ Jupyter Notebook支持
- ✅ 数据可视化工具
- ✅ 机器学习库
- ✅ 代码质量工具（Black, Flake8等）

## 快速开始

1. 在VS Code中打开此目录
2. 按`Ctrl+Shift+P`，输入"Reopen in Container"
3. 等待容器构建完成（首次构建需要一些时间）
4. 运行 `python data_analysis.py` 执行数据分析示例
5. 运行 `jupyter notebook` 启动Jupyter

## 文件说明

- `.devcontainer/devcontainer.json` - 主要配置文件
- `.devcontainer/Dockerfile` - 自定义Dockerfile
- `requirements.txt` - Python依赖包列表
- `data_analysis.py` - 数据科学示例代码

## 学习要点

通过这个示例，你可以学习：

1. 自定义Dockerfile配置
2. 多语言环境配置技巧
3. 数据科学工具链集成
4. Jupyter Notebook配置
5. 端口转发和标签设置

## 扩展功能

- 访问 http://localhost:8888 使用Jupyter Notebook
- 数据目录自动挂载到容器中
- 支持Git和GitHub CLI
- 自动安装Python开发扩展