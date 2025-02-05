---
description: >-
  Java 10 是 Java 9 之后的 短期版本，虽然没有像 Java 9
  那样的模块化变革，但它仍然带来了一些重要的语言增强、GC优化、JVM性能提升等新特性
---

# Java10
## 📌 Java 10 新特性总结表格

| **类别**         | **新特性**                                    | **作用**                                     |
|----------------|--------------------------------|--------------------------------|
| **语法增强**   | `var` 关键字                    | 局部变量类型推断，减少冗余类型声明 |
| **GC 改进**   | G1 GC 性能优化                  | 降低 Full GC 触发频率，提高吞吐量 |
| **JVM 改进**   | `Application Class-Data Sharing (AppCDS)` | 缩短 JVM 启动时间，提高性能 |
| **内存管理**   | 堆内存分配改进（Thread-Local Handshakes） | 动态调整堆大小，提升并发效率 |
| **安全性**     | `Root Certificates`（默认可信 CA 证书） | Java 默认包含 CA 证书，提高安全性 |
| **Docker 支持** | `JVM Container Awareness` | 使 JVM 运行时更好地适配容器环境 |

