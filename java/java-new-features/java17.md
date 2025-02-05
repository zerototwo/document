---
description: >-
  Java 17 是 长期支持版本（LTS），是 Java 11 之后的重要更新。它带来了 sealed class（正式版）、Pattern
  Matching for switch、ZGC 进一步优化、Foreign Function & Memory API 等正式特性，并移除了
  Security Manager。
---

# Java17

## 📌 Java 17 新特性总结表格

| **类别**         | **新特性**                              | **作用** |
|----------------|------------------------------|------------------------------|
| **语法增强**  | `sealed class`（JEP 409） | 限制类的继承，提高安全性 |
| **语法增强**  | `Pattern Matching for switch`（JEP 406） | `switch` 语法优化，支持模式匹配 |
| **GC 改进**   | ZGC 进一步优化（JEP 403） | 提高 GC 性能，减少停顿时间 |
| **JVM 内存管理** | `Foreign Function & Memory API`（JEP 412） | 提供安全的堆外内存访问 |
| **安全性**    | 移除 `Security Manager`（JEP 411） | 清理过时的安全管理机制 |