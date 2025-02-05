---
description: Java 14 是 短期版本（非 LTS），但它引入了许多重要的新特性，包括 record 关键字、instanceof 模式匹配、G1 GC 改进等
---

# Java14

## 📌 Java 14 新特性总结表格

| **类别**          | **新特性**                              | **作用** |
|-----------------|------------------------------|------------------------------|
| **数据类**    | `record` 关键字（JEP 359） | 代替 `POJO`，简化数据类编写 |
| **语法增强**    | `instanceof` 模式匹配（JEP 305） | 省略显式类型转换，提高可读性 |
| **GC 改进**    | G1 GC NUMA 适配（JEP 366） | 提高多核 CPU 上的 GC 性能 |
| **异常增强**    | `NullPointerException` 提供更详细信息（JEP 358） | `NPE` 详细指示空指针来源 |
| **语法增强**    | `switch` 语法增强（JEP 361） | `switch` 语法成为正式特性 |
| **JVM 优化**   | `Foreign-Memory Access API`（JEP 370） | 安全访问堆外内存 |
| **调试工具**   | `JFR Event Streaming`（JEP 349） | 提供低开销 JVM 监控 |