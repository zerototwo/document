---
description: >-
  Java 11 是 Java 8 之后的长期支持版本（LTS），引入了 新 HTTP 客户端、ZGC、Lambda 语法优化 等重要特性，同时移除了
  Java EE 和 CORBA，使 JDK 更加轻量级
cover: >-
  https://images.unsplash.com/photo-1736580602062-885256588e01?crop=entropy&cs=srgb&fm=jpg&ixid=M3wxOTcwMjR8MHwxfHJhbmRvbXx8fHx8fHx8fDE3Mzg3NDgzMjJ8&ixlib=rb-4.0.3&q=85
coverY: 0
---

# Java11
## 📌 Java 11 新特性总结表格

| **类别**         | **新特性**                                | **作用** |
|----------------|--------------------------------|--------------------------------|
| **语法增强**   | Lambda 变量支持 `var` 关键字      | 让 Lambda 代码风格更统一 |
| **字符串 API** | `isBlank()` / `strip()` / `lines()` / `repeat()` | 增强字符串处理能力 |
| **新 HTTP 客户端** | `HttpClient` | 替代 `HttpURLConnection`，支持 HTTP/2 |
| **GC 改进**   | ZGC（低停顿垃圾回收器）            | 提高吞吐量，减少 Full GC |
| **并发优化**   | `Flight Recorder` & `JFR`        | 低开销 JVM 监控 |
| **安全性**     | `Root Certificates`（默认可信 CA 证书） | Java 默认包含 CA 证书 |
| **多版本 JAR** | `Launch Single-File Programs` | 直接运行 `.java` 文件 |
| **JDK 轻量化** | **移除 Java EE 和 CORBA** | 精简 JDK，提升运行效率 |