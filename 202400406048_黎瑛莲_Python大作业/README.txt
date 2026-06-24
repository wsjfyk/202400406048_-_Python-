重构版 记账本 - 运行说明与测试说明

1) 环境要求
- Python 3.8+
- 建议使用虚拟环境
- 依赖库：见 requirements.txt（pip install -r requirements.txt）

2) 如何安装（可编辑安装）
- 克隆仓库并切换到分支：
  git clone https://github.com/wsjfyk/202400406048_-_Python-.git
  cd 202400406048_-_Python-
  git checkout 202400406048_refactor

- 推荐创建虚拟环境并激活
  python -m venv venv
  # Windows:
  venv\\Scripts\\activate
  # macOS / Linux:
  source venv/bin/activate

- 安装依赖并可编辑安装：
  pip install -r 202400406048_黎瑛莲_Python大作业/requirements.txt
  pip install -e 202400406048_黎瑛莲_Python大作业

3) 如何运行程序
- 方式 A（推荐）：
  python -m accounting_202400406048
- 方式 B（直接运行）：
  python 202400406048_黎瑛莲_Python大作业/src/accounting_202400406048/__main__.py

首次运行会在当前工作目录生成 records.csv 作为持久化文件。

4) 运行测试（pytest）
- 进入项目子目录并运行 pytest：
  cd 202400406048_黎瑛莲_Python大作业
  pytest -q

测试文件位于：202400406048_黎瑛莲_Python大作业/tests

5) 说明
- 源码放在 src/accounting_202400406048 下，包名为 accounting_202400406048
- 仓库顶部目录名保留为你指定的作业名，用于提交与展示
