# CAN 教程 P0 技术勘误与可执行验证

本修复范围：经典CAN、bxCAN和CANopen对象的已确认P0问题。这里的Python模型只用于验证确定性的数值关系和字段编码，不等于ISO合规测试或MCU驱动。

## 运行

在仓库根目录执行：

    python3 -m unittest discover -s tests -v

CI：.github/workflows/can-p0-validation.yml

## 复算样例

| 核验 | 输入 | 预期 |
| --- | --- | --- |
| 500 kbps / 87.5% | 16 MHz, BRP=2, BS1=13, BS2=2 | 500000 bit/s, 87.5% |
| 500 kbps / 83.33% | 36 MHz, BRP=4, BS1=14, BS2=3 | 500000 bit/s, 83.33% |
| 原示例错误速率 | 36 MHz, BRP=4, BS1=8, BS2=7 | 562500 bit/s（不是500k） |
| 标准仲裁 | ID=0x100 vs 0x200 | 0x100胜出，不增加错误计数 |
| 错误状态 | TEC=128, REC=0 | error-passive |
| Bus Off | TEC=256 | bus-off |
| SDO上传 | command 0x4F | 成功，1字节 |
| SDO中止 | command 0x80 | abort |
| TPDO映射 | 0x606C:00 32位 | 0x606C0020 |
| 小端车速 | Byte1=B8, Byte2=0B, factor=0.01 | 30.00 km/h |
| 标准8字节帧 | 含帧间隔，不含填充 | 111 bit |

## 已修复的课程

- 03：仲裁失败和TEC/REC区分
- 04：CRC计算输入范围；错误计数与Bus Off恢复
- 05：16TQ采样点计算、传播延迟补偿说明
- 08、09：36MHz的500kbps配置、SPL初始化、PB8/PB9引脚复用
- 10：发送邮箱与仲裁区分，避免错误寄存器等待和数据越界
- 20：0x4F是SDO成功上传1字节，0x80才是中止
- 21：CiA402速度实际值0x606C，位置实际值0x6064，0x6041是状态字
- 27：修复自定义小端车速示例并检查DLC
- 30：HAL句柄作用域、准确的波特率、过滤器和诊断响应

## 验收边界

- 参考Python函数及回归用例可在没有CAN硬件的情况下执行。
- STM32 SPL/HAL片段须结合**具体MCU型号**、头文件版本、GPIO重映射和时钟树进行交叉编译与实机测试；它们不是单文件可独立编译的项目。
- CANopen设备是否支持动态PDO映射、对象访问权限及其物理单位，均以设备的EDS和协议配置为准。
- 总线负载计算不包含填充位、错误帧、重传；真实网络应使用硬件时间戳与CAN分析仪复核。
- 不在车辆/工业现网直接注入示例数据。0x621仅为隔离台架演示ID，不代表全局安全或无冲突。

规范核验入口：
- Bosch CAN 2.0 specification / ISO 11898-1 数据链路层
- ST STM32F1 Reference Manual RM0008 和STM32F1 HAL/SPL对应版本
- CiA 301 CANopen application layer and communication profile
- CiA 402 drive and motion control device profile
