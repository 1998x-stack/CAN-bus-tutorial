# 参考模型

这里存放供课程讲解和单元测试复算的确定性参考实现：

- can_p0.py：经典 CAN 位时序、仲裁、错误状态等参考计算
- canopen_ch19_21.py：CANopen NMT / SDO / PDO 字段与传输示例
- olah-ch25-evidence.json 至 olah-ch27-evidence.json：历史章节证据清单（保留原位置以兼容既有检查）

入口：

~~~bash
python3 -m unittest discover -s tests -v
python3 -m reference.canopen_ch19_21
~~~

这些模型并非设备驱动，不替代芯片手册、协议一致性测试或真实总线测量。
