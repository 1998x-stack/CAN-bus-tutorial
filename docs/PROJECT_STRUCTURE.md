# 仓库结构与兼容性策略

这个仓库同时是 GitHub Pages 静态网站、课程源代码和离线验证工程。整理时以**公开章节 URL 稳定、可直接阅读、无需前端构建**为首要约束。

## 目录职责

| 位置 | 作用 | 维护建议 |
| --- | --- | --- |
| index.html | GitHub Pages 入口、语义化内容和 SEO 信息 | 首页结构放这里；不要写长段内联样式和脚本 |
| courses.json | 章节与学习阶段的唯一清单 | 章节编号、标题、主题和路径应与实际文件同步 |
| 01.html–30.html | 章节独立网页 | 保持根目录路径不变，避免已有在线链接失效 |
| assets/css/home.css | 首页响应式样式 | 不覆盖章节全局标签，避免样式互相污染 |
| assets/js/home.js | 首页筛选、搜索与本地进度 | 不增加依赖；所有章节标题使用 textContent 插入 |
| assets/*.svg、assets/*.css、assets/css/* | 既有章节图示/样式 | 既有路径作为兼容接口；新增资源优先分类存放 |
| docs/P0_VERIFICATION.md | 技术准确性勘误、回归边界 | 不应把离线模型误写为实机合规认证 |
| docs/chapter*-evidence.json、docs/evidence/ | 章节论据与来源清单 | 保留原文件名，避免测试和章节引用断开 |
| examples/ | 教学例程与独立复算示例 | 清楚标注适用的 MCU/协议/范围 |
| reference/ | 确定性参考模型和少量历史证据文件 | 模型供单测调用，不承担在线固件职能 |
| tests/test_*.py | Python 标准库回归测试 | python3 -m unittest discover -s tests -v |
| tests/browser_*.py | Playwright 浏览器 QA | 可选运行；检查多宽度、交互和溢出 |
| .github/workflows/ | CI 测试工作流 | 路径限定的浏览器工作流减少无关运行 |

## 首页的数据约束

课程列表只有一个数据源：courses.json。chapters 中每条记录含 num（两位数字字符串）、title、topics 数组和 file（NN.html）；stages 包含 id、title、description、start、end。六阶段编号不重叠、无空档，恰好覆盖 01–30 章。首页动态渲染阶段卡片、筛选按钮和章节卡片。

用户手动点击「标记已学」后，完成的章节编号保存在 localStorage 的 can-bus-tutorial:completed:v1；点击章节链接时，最后阅读编号保存在 can-bus-tutorial:last:v1。它们不提交到仓库，也不跨设备同步。浏览器禁用 localStorage 时，目录与筛选仍可使用。

## 为什么不批量移动章节

GitHub Pages 使用项目子路径 /CAN-bus-tutorial/。既有 01.html、主题 CSS、SVG、测试脚本已被章节、工作流及外部站点引用。将它们直接移动到 chapters/、assets/images/ 或 tests/browser/ 会破坏上述地址和硬编码路径。因此本轮只做**兼容性可控的拆分与整理**：首页新增 assets/css/home.css、assets/js/home.js，且通过本文件和 README 明确其他目录职责。

未来若整体迁移，需要同步修改所有页面的相对引用、侧栏目录、测试、工作流，并为旧 01.html–30.html 提供重定向或兼容页面；不要仅改目录名。

## 发布与验证

网站是 GitHub Pages 纯静态文件；既有 30 个章节不需要 npm 构建。确认 Pages 的发布源包含 index.html、courses.json 和 assets/ 目录。

本地运行：

~~~bash
python3 -m http.server 8000
python3 -m unittest discover -s tests -v
~~~

浏览器 QA 使用 python3 tests/browser_homepage.py，需提前安装 Playwright 和 Chromium/Chrome。若首页无法加载章节，先确认浏览器从 HTTP 服务打开了正确的 courses.json，而不是直接用 file:// 访问。
