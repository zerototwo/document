---
description: Java 18 于 2022 年 3 月 22 日发布，作为短期支持版本（非 LTS），带来了 编码一致性、开发者工具改进、性能优化 等正式特性
cover: >-
  https://images.unsplash.com/photo-1727206407683-490abfe0d682?crop=entropy&cs=srgb&fm=jpg&ixid=M3wxOTcwMjR8MHwxfHJhbmRvbXx8fHx8fHx8fDE3Mzg4MzQ2Mzl8&ixlib=rb-4.0.3&q=85
coverY: 0
---

# Java18

## 📌 Java 18 正式特性总结表格

| **类别**         | **新特性**                         | **作用** |
|----------------|--------------------------------------|------------------------------------------------------|
| **编码规范**   | 默认字符集 UTF-8（JEP 400）          | 统一所有 Java 平台的默认字符集为 UTF-8，避免跨平台编码问题，提高一致性。 |
| **开发工具**   | 内置简易 Web 服务器（JEP 408）       | 提供 `jwebserver`，可快速启动静态 Web 服务器，便于开发测试。 |
| **文档优化**   | Java API 文档代码片段（JEP 413）     | Javadoc 新增 `@snippet`，提升代码示例的可读性和维护性。 |
| **反射优化**   | 方法句柄优化反射机制（JEP 416）      | 使用 `MethodHandle` 重新实现 `java.lang.reflect`，提高性能。 |
| **性能优化**   | 向量 API（JEP 417）                 | 提供 SIMD 指令支持，提高数据处理和计算性能。 |
| **网络增强**   | 互联网地址解析 SPI（JEP 418）        | 允许 Java 开发者自定义 `InetAddress` 的主机解析行为。 |
| **JVM 内存管理** | 外部函数和内存 API（JEP 419）       | 改进 Java 访问非 JVM 内存的能力，替代 `Unsafe` API，提高安全性。 |
| **安全性**     | 弃用终结器（JEP 421）                | 计划移除 `finalize()`，鼓励使用 `try-with-resources` 进行资源管理。 |