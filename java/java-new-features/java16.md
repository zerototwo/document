---
description: >-
  Java 16 是 短期版本（非 LTS），但它引入了许多正式特性，包括 record 关键字（正式版）、Pattern Matching for
  instanceof、ZGC 进一步优化、Vector API 等
---

# Java16

## 📌 Java 16 新特性总结表格

| **类别**         | **新特性**                              | **作用** |
|----------------|------------------------------|------------------------------|
| **数据类**    | `record`（正式特性，JEP 395） | 代替 `POJO`，简化数据类编写 |
| **语法增强**  | `instanceof` 模式匹配（JEP 394） | `instanceof` 语法优化，自动类型转换 |
| **GC 改进**   | ZGC 并发线程处理优化（JEP 376） | 降低 GC 线程竞争，提高吞吐量 |
| **向量计算**  | `Vector API`（JEP 338） | 适用于高性能计算 |
| **JVM 优化**  | `Foreign-Memory Access API`（JEP 389） | 提供安全的堆外内存访问 |
