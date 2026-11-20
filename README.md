# CAN 总线教程 · 从原理到工程实践

[![在线阅读](https://img.shields.io/badge/GitHub%20Pages-在线阅读-20866c)](https://1998x-stack.github.io/CAN-bus-tutorial/) [![基础与回归测试](https://github.com/1998x-stack/CAN-bus-tutorial/actions/workflows/can-p0-validation.yml/badge.svg)](https://github.com/1998x-stack/CAN-bus-tutorial/actions/workflows/can-p0-validation.yml)

> 30 章中文课程 · 6 个学习阶段 · 经典 CAN / STM32 bxCAN / CANopen / J1939 / 工程实践

**[打开课程首页](https://1998x-stack.github.io/CAN-bus-tutorial/)** · [从第 01 章开始](https://1998x-stack.github.io/CAN-bus-tutorial/01.html) · [查看质量验证边界](docs/P0_VERIFICATION.md)

这个仓库提供可直接访问的静态 HTML 教程、SVG 示意图、可复算的 Python 参考模型和回归测试。学习内容覆盖协议、电气、嵌入式驱动和工程排障，不要求前端构建或运行服务端程序。

## 快速开始

在线学习：打开上面的课程首页，使用阶段筛选、关键词搜索或直接访问任意章节。首页的“标记已学”以及“继续阅读”仅在当前浏览器的 localStorage 中保存，不涉及账号和云端同步。

本地预览（请在仓库根目录运行 HTTP 服务；首页需要获取 courses.json，因此不建议直接使用 file:// 打开）：

~~~bash
python3 -m http.server 8000
# 访问 http://localhost:8000/
~~~

单独的 01.html 至 30.html 页面仍保留在仓库根目录，以保持已有 GitHub Pages 深链接稳定。

## 学习路线

| 阶段 | 章节 | 重点 | 推荐起点 |
| --- | --- | --- | --- |
| 1. 协议与信号基础 | 01–05 | 帧格式、仲裁、错误处理与位时序 | [第 01 章](01.html) |
| 2. 控制器与 STM32 | 06–12 | 外设、初始化、报文收发与中断 | [第 06 章](06.html) |
| 3. 物理层与网络设计 | 13–17 | 过滤器、拓扑、终端、差分信号与速率 | [第 13 章](13.html) |
| 4. CANopen 协议栈 | 18–21 | 对象字典、NMT、心跳、SDO 与 PDO | [第 18 章](18.html) |
| 5. J1939 与测试工具 | 22–24 | J1939、传输协议及常见测试工具 | [第 22 章](22.html) |
| 6. 调试与项目实践 | 25–30 | 故障定位、硬件与软件设计、低功耗、集成 | [第 25 章](25.html) |

**推荐阅读顺序：**新手建议按顺序从第 01 章开始；使用 STM32 的读者可优先阅读第 05、08–12 章；排查现场问题可从第 14–17、24–26 章切入。章节中的例子以实际 MCU、收发器及网络规格为准。

## 完整章节目录

| 章节 | 标题 | 关键知识点 |
| --- | --- | --- |
| [01](01.html) | [CAN总线概述](01.html) | 发展历史 · 汽车电子应用 · 物理层特性 |
| [02](02.html) | [CAN协议基础](02.html) | 分层结构 · 数据帧格式 · 远程帧/错误帧/过载帧 |
| [03](03.html) | [CAN总线仲裁机制](03.html) | 位仲裁原理 · CSMA/CR机制 · 仲裁失败处理 |
| [04](04.html) | [CAN总线错误处理](04.html) | 错误类型 · 位/填充/CRC错误 · 错误状态机 |
| [05](05.html) | [CAN总线位时序与同步](05.html) | 位时间结构 · 同步段/传播段 · 硬同步/重同步 |
| [06](06.html) | [CAN控制器硬件](06.html) | SJA1000/MCP2515 · 内部寄存器 · 工作模式 |
| [07](07.html) | [CAN收发器](07.html) | TJA1050/SN65HVD230 · 电气特性 · 共模/差模信号 |
| [08](08.html) | [STM32 CAN外设](08.html) | bxCAN控制器 · 时钟配置 · GPIO复用 |
| [09](09.html) | [STM32 CAN初始化](09.html) | 初始化步骤 · 位时间配置 · 过滤器/中断配置 |
| [10](10.html) | [CAN报文发送](10.html) | 发送邮箱机制 · 发送优先级 · 发送完成中断 |
| [11](11.html) | [CAN报文接收](11.html) | 接收FIFO · 过滤器匹配 · 接收中断/超时 |
| [12](12.html) | [CAN中断编程](12.html) | 中断优先级 · 中断服务函数 · 调试技巧 |
| [13](13.html) | [CAN过滤器深入](13.html) | 标识符列表/掩码模式 · 过滤器组 · 屏蔽位设计 |
| [14](14.html) | [CAN总线网络拓扑](14.html) | 总线/星型拓扑 · 终端电阻 · 长度与速率 |
| [15](15.html) | [CAN总线终端电阻](15.html) | 终端电阻作用 · 120Ω选择 · 放置位置/错误 |
| [16](16.html) | [CAN总线电平与差分信号](16.html) | 显性/隐性电平 · 差分信号优势 · 共模电压 |
| [17](17.html) | [CAN总线通信速率](17.html) | 125k~1Mbps · 速率与距离 · 采样点设置 |
| [18](18.html) | [CANopen协议入门](18.html) | 协议栈结构 · 对象字典 · PDO与SDO |
| [19](19.html) | [CANopen NMT与心跳](19.html) | NMT状态机 · 心跳报文 · 节点守护 |
| [20](20.html) | [CANopen SDO通信](20.html) | SDO请求/响应 · 分段/块传输 · 超时处理 |
| [21](21.html) | [CANopen PDO通信](21.html) | PDO映射 · 同步/异步PDO · 触发方式 |
| [22](22.html) | [J1939协议入门](22.html) | 协议栈结构 · PGN与SPN · 地址声明 |
| [23](23.html) | [J1939多包传输](23.html) | 多包消息机制 · 连接管理 · 传输协议 |
| [24](24.html) | [CAN总线测试工具](24.html) | PCAN/USBCAN · CANscope · CANstress |
| [25](25.html) | [CAN总线调试技巧](25.html) | 逻辑分析仪抓包 · 负载率计算 · 故障排查 |
| [26](26.html) | [CAN总线硬件设计](26.html) | PCB布局 · 隔离设计 · ESD保护 |
| [27](27.html) | [CAN总线软件架构](27.html) | 分层设计 · 驱动/协议/应用层 |
| [28](28.html) | [CAN总线多节点通信实战](28.html) | 多节点组网 · 数据同步 · 冲突避免 |
| [29](29.html) | [CAN总线低功耗设计](29.html) | 休眠唤醒 · 局部网络 · 选择性唤醒 |
| [30](30.html) | [CAN总线项目实战](30.html) | STM32数据采集 · 上位机显示 · 故障诊断 |

## 仓库结构

~~~text
CAN-bus-tutorial/
├── index.html               # GitHub Pages 首页（保留根路径）
├── 01.html ... 30.html      # 独立章节，保持原有公开 URL
├── courses.json             # 30 章目录与 6 个阶段的唯一数据源
├── assets/
│   ├── css/home.css         # 首页专用样式
│   ├── js/home.js           # 首页搜索 / 筛选 / 本地进度
│   └── *.svg, *.css, ...    # 既有章节图示与兼容样式
├── docs/                    # 技术勘误、来源证据与维护说明
├── examples/                # 教学示例与可复算代码
├── reference/               # Python 参考模型
├── tests/                   # 标准库单测和可选浏览器 QA
└── .github/workflows/       # 自动化回归与浏览器检查
~~~

详细目录职责、命名和兼容性策略见 [docs/PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md)。本次整理将首页样式、逻辑拆分到清晰的资源目录，但**不批量迁移章节 HTML、既有 SVG 或测试脚本**，以免破坏外部链接和 CI 路径。

## 测试与质量

基础与协议回归测试（使用 Python 标准库，无额外 Python 依赖）：

~~~bash
python3 -m unittest discover -s tests -v
~~~

可选的首页浏览器测试（需先安装 Playwright 和 Chromium/Chrome）：

~~~bash
python3 -m pip install playwright
python3 -m playwright install chromium
python3 tests/browser_homepage.py
~~~

浏览器测试会检查桌面/平板/手机布局、30 章加载、筛选、搜索、阅读标记与继续阅读。GitHub Actions 配置见 [.github/workflows/homepage-qa.yml](.github/workflows/homepage-qa.yml)；其余章节独立浏览器工作流仍然保留。更多命令见 [tests/README.md](tests/README.md)。

**验证边界：**通过 Python 单测不等于完成 STM32 交叉编译、硬件总线测试、CANopen 一致性测试或安全认证。实际设备应核对芯片型号、时钟树、收发器、终端电阻、EDS 与现场线束。参见 [P0 技术勘误与验证](docs/P0_VERIFICATION.md)。

## 参与维护

修改课程目录请同步维护 [courses.json](courses.json)，新增章节须保证编号、文件名与阶段范围一致；修改首页请检查无障碍键盘操作及 360/390/768/1440 像素布局。提交前运行基础测试，必要时执行对应浏览器 QA。具体说明见 [CONTRIBUTING.md](CONTRIBUTING.md)。

仓库目前未声明独立的开源许可文件；如需复制、改编或分发内容，请先确认相应使用授权。
