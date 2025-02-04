---
description: Java 9 引入了多个重要的新特性，包括 模块化系统、增强的 API、GC 改进 等。以下是 Java 9 的核心特性概览：
---

# Java9

## 📌 Java 9 新特性总结表格

| **类别**       | **新特性**                                | **作用**                                  |
|--------------|--------------------------------|----------------------------------|
| **核心平台**   | **模块化系统（JPMS）**            | 解决 JAR 依赖冲突，提高安全性             |
| **集合 API**   | `List.of()` / `Set.of()` / `Map.of()` | 快速创建不可变集合                         |
| **Stream API** | `takeWhile()` / `dropWhile()` | 优化数据流处理，提高可读性                  |
| **Optional API** | `ifPresentOrElse()` / `or()` | 更灵活的 `Optional` 处理方式              |
| **HTTP 客户端** | `HttpClient`                   | 替代 `HttpURLConnection`，支持 HTTP/2      |
| **语法增强**   | 私有接口方法                     | 避免接口代码重复，提高代码封装性             |
| **语法增强**   | try-with-resources 改进        | 允许在 `try` 语句中使用已定义的资源          |
| **进程 API**   | `ProcessHandle`               | 访问系统进程信息，提高进程管理能力            |
| **GC 改进**   | G1 GC 默认启用                  | 提高吞吐量，减少 Full GC                   |
| **JAR 兼容性** | Multi-Release JAR              | 允许不同 Java 版本加载不同实现               |
| **JShell**    | Java 交互式编程                   | 提供即时执行 Java 代码的环境，适用于学习和测试  |

