# 测试说明

## Python 回归

在仓库根目录执行：

~~~bash
python3 -m unittest discover -s tests -v
~~~

测试覆盖 CAN 位时序、错误处理、仲裁、CANopen/J1939 编码、章节结构及首页章节清单。标准库单测无需硬件或额外 Python 包。

## 首页浏览器 QA

~~~bash
python3 -m pip install playwright
python3 -m playwright install chromium
python3 tests/browser_homepage.py
~~~

检查 1440 / 768 / 390 / 360 像素布局、目录加载、阶段筛选、关键词检索、清空结果、本地阅读标记和继续阅读。截图输出到 reports/homepage/，该目录属于临时产物，不应提交。

既有 tests/browser_chapter*.py 及 tests/browser_chapters*.py 继续对应各章节，相关 GitHub Actions workflow 仍引用它们，未在本轮重命名。

**范围说明：**Python、Playwright 测试无法证明 STM32 固件可在任意硬件上编译运行，也不构成 CANopen、J1939 或 EMC/功能安全认证。
