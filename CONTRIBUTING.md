# 内容维护与贡献指南

欢迎对错别字、链接、计算例子、图示和章节可读性提出改进。请优先让每个技术主张可复算、可定位到来源，而非只给结论。

## 编辑原则

1. 保留根目录的 01.html–30.html 公开章节 URL。引用同仓库文件时使用相对路径，确保 GitHub Pages 项目子路径下也能访问。
2. 目录数据统一更新 courses.json：num 为两位数字，file 为对应 NN.html；六个 stages 的 start/end 必须连续且覆盖所有章节。
3. 首页 HTML 只负责语义结构，样式写到 assets/css/home.css，行为写到 assets/js/home.js；课程标题和主题用 textContent 构造 DOM，避免直接拼接 HTML。
4. 技术示例明确芯片、外设和协议版本；引用规范、手册、数据表。离线示例不要声称经过实机或认证测试。
5. 新增图示尽量提供 SVG title/desc、替代文本或图注；按钮可键盘聚焦，状态用 aria-pressed 等语义描述。考虑 prefers-reduced-motion。

## 提交前

~~~bash
python3 -m unittest discover -s tests -v
# 修改首页时（安装 Playwright + 浏览器后）
python3 tests/browser_homepage.py
~~~

建议手工确认首页在 360、390、768、1440 像素下没有横向溢出，并验证 GitHub Pages 上的章节深链接、页面返回目录的入口。

## 目录与发布

请参考 docs/PROJECT_STRUCTURE.md。章节页面和历史资源路径是兼容性接口，不要在无迁移计划时随意移动。项目目前没有单独声明内容许可证；如涉及大量复制或再分发，请先确认授权范围。
