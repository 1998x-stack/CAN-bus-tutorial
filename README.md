# 🚌 CAN总线 · 从入门到精通

> 📘 30章 实战体系

一套完整的 **CAN总线 · 从入门到精通** 全中文实战课程体系，共 **30 章**。本课程以 HTML 可视化的形式呈现，从基础原理到工程实践循序渐进，适合系统性学习与复习。

## 🚀 快速开始

课程本身是纯静态HTML，但目录页会通过 `fetch('courses.json')` 加载章节数据。为了避免浏览器 `file://` 同源限制，建议在项目根目录开启本地HTTP服务器：

```bash
python3 -m http.server 8000
# 浏览器访问 http://127.0.0.1:8000/
```

单独的 `01.html` 到 `30.html` 章节文件也可以直接打开阅读。

## 📖 章节目录

| # | 章节 | 核心主题 |
|---|------|----------|
| 01 | CAN总线概述 | 发展历史、汽车电子应用、物理层特性 |
| 02 | CAN协议基础 | 分层结构、数据帧格式、远程帧/错误帧/过载帧 |
| 03 | CAN总线仲裁机制 | 位仲裁原理、CSMA/CR机制、仲裁失败处理 |
| 04 | CAN总线错误处理 | 错误类型、位/填充/CRC错误、错误状态机 |
| 05 | CAN总线位时序与同步 | 位时间结构、同步段/传播段、硬同步/重同步 |
| 06 | CAN控制器硬件 | SJA1000/MCP2515、内部寄存器、工作模式 |
| 07 | CAN收发器 | TJA1050/SN65HVD230、电气特性、共模/差模信号 |
| 08 | STM32 CAN外设 | bxCAN控制器、时钟配置、GPIO复用 |
| 09 | STM32 CAN初始化 | 初始化步骤、位时间配置、过滤器/中断配置 |
| 10 | CAN报文发送 | 发送邮箱机制、发送优先级、发送完成中断 |
| 11 | CAN报文接收 | 接收FIFO、过滤器匹配、接收中断/超时 |
| 12 | CAN中断编程 | 中断优先级、中断服务函数、调试技巧 |
| 13 | CAN过滤器深入 | 标识符列表/掩码模式、过滤器组、屏蔽位设计 |
| 14 | CAN总线网络拓扑 | 总线/星型拓扑、终端电阻、长度与速率 |
| 15 | CAN总线终端电阻 | 终端电阻作用、120Ω选择、放置位置/错误 |
| 16 | CAN总线电平与差分信号 | 显性/隐性电平、差分信号优势、共模电压 |
| 17 | CAN总线通信速率 | 125k~1Mbps、速率与距离、采样点设置 |
| 18 | CANopen协议入门 | 协议栈结构、对象字典、PDO与SDO |
| 19 | CANopen NMT与心跳 | NMT状态机、心跳报文、节点守护 |
| 20 | CANopen SDO通信 | SDO请求/响应、分段/块传输、超时处理 |
| 21 | CANopen PDO通信 | PDO映射、同步/异步PDO、触发方式 |
| 22 | J1939协议入门 | 协议栈结构、PGN与SPN、地址声明 |
| 23 | J1939多包传输 | 多包消息机制、连接管理、传输协议 |
| 24 | CAN总线测试工具 | PCAN/USBCAN、CANscope、CANstress |
| 25 | CAN总线调试技巧 | 逻辑分析仪抓包、负载率计算、故障排查 |
| 26 | CAN总线硬件设计 | PCB布局、隔离设计、ESD保护 |
| 27 | CAN总线软件架构 | 分层设计、驱动/协议/应用层 |
| 28 | CAN总线多节点通信实战 | 多节点组网、数据同步、冲突避免 |
| 29 | CAN总线低功耗设计 | 休眠唤醒、局部网络、选择性唤醒 |
| 30 | CAN总线项目实战 | STM32数据采集、上位机显示、故障诊断 |

## ✅ P0 准确性修复与回归测试

针对CAN仲裁、错误计数、位时序、STM32 bxCAN示例和CANopen SDO/PDO等关键内容，已补充可复算的参考模型与自动化回归检查。

```bash
python3 -m unittest discover -s tests -v
```

具体修复清单、计算基准与实机验证边界见 [docs/P0_VERIFICATION.md](docs/P0_VERIFICATION.md)。Python单元测试通过不代表某块STM32开发板已经完成交叉编译或硬件总线验证。

## 🔎 第 10–12 章：发送 / 接收 / 中断编程

- [第 10 章 · CAN 报文发送](10.html)：三邮箱调度、TXFP、总线仲裁、RQCP/TXOK 的区别及 TX 中断。
- [第 11 章 · CAN 报文接收](11.html)：过滤器、双 FIFO、RFLM 溢出策略、SPSC 队列与消息时效性。
- [第 12 章 · CAN 中断编程](12.html)：STM32F103 共享向量、NVIC 分组、标志处理与 ISR 周期测量。

三章共享 [阅读样式](reading.css)，每章的可独立查看的 SVG 图示位于 [assets/](assets/)；主张与参考手册的出处列在 [docs/chapter10-evidence.json](docs/chapter10-evidence.json)、[docs/chapter11-evidence.json](docs/chapter11-evidence.json)、[docs/chapter12-evidence.json](docs/chapter12-evidence.json)。

在仓库根目录执行：

```bash
python -m unittest discover -s tests -p 'test_chapters_10_12.py' -v
pip install playwright
python -m playwright install chromium
python tests/browser_chapters_10_12.py
```

浏览器检查覆盖 1440 / 768 / 390 / 360 px、章节内交互、SVG、导航和页面横向溢出。GitHub Actions 的 [Chapter 10-12 QA](.github/workflows/chapter10-12-browser.yml) 工作流可在变更时运行；能否通过以实际工作流结果为准。代码示例基于 **STM32F103 / bxCAN / STM32F10x SPL**，仍须按实际板卡和启动文件做编译、接线与总线验证。

## 📂 项目结构

```text
CAN-bus-tutorial/
├── index.html      # 课程主入口（在线阅读全部章节）
├── 01.html ~ 30.html   # 各章节正文
├── courses.json    # 课程元数据（标题/章节/主题）
└── theme.css       # 统一主题样式
```

## ✨ 课程特色

- **全中文实战体系**：面向中文读者，由浅入深，覆盖原理与工程实践
- **30 章完整内容**：系统化章节编排，形成完整知识闭环
- **可视化呈现**：HTML 图文并茂，适合快速浏览与重点回顾
- **即开即用**：无需构建、无需服务器，纯静态页面随开随看

---
*本课程由 `CAN-bus-tutorial/` 项目维护。*

## 📘 第 19–21 章：CANopen 图解与可复算实验

- [第 19 章：NMT 与心跳](19.html)：Boot-up、NMT 状态、Heartbeat/Node Guarding、消费者超时编码。
- [第 20 章：SDO 通信](20.html)：逐字节读取响应、分段 toggle、块确认与 Abort。
- [第 21 章：PDO 通信](21.html)：对象映射、SYNC 时序、传输类型与带宽下界。

三个章节各有 2 幅可独立查看的 SVG 图、浏览器内交互实验和来源清单（`docs/chapter19-evidence.json` 至 `docs/chapter21-evidence.json`）。底层计算参考模型见 `reference/canopen_ch19_21.py`。

```bash
python3 -m unittest discover -s tests -v
python3 -m reference.canopen_ch19_21
# 可选浏览器 QA：安装 playwright 与 Chromium / Chrome 后
python3 tests/browser_chapters19_21.py
```

> 示例仅用于离线字段验证，不是 CANopen 一致性测试或实机安全认证。PDO 对象可映射性、设备单位和配置时机以各设备 EDS/文档为准。
