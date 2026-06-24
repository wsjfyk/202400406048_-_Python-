# 运行与测试说明

本目录包含“个人记账本”项目的重构版本，已满足课程大作业的要求。

包含内容（子目录）:
- src/accounting_202400406048: 可导入的包，包含代码模块
- pyproject.toml: 可编辑安装配置
- README.txt: 简短运行说明

新增内容:
- requirements.txt: 项目依赖
- README.md: 项目说明与评分要求对应说明
- tests/test_data_manager.py: pytest 单元测试（DataManager）

如何安装依赖并运行测试：

1. 在项目根（即本子目录）创建并激活虚拟环境：

   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS / Linux
   source venv/bin/activate

2. 安装依赖：

   pip install -r requirements.txt

3. 运行程序（推荐通过可编辑安装）：

   pip install -e .
   python -m accounting_202400406048

4. 运行单元测试：

   pytest -q


