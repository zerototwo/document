---
description: >-
  Java 17 是 长期支持版本（LTS），是 Java 11 之后的重要更新。它带来了 sealed class（正式版）、Pattern
  Matching for switch、ZGC 进一步优化、Foreign Function & Memory API 等正式特性，并移除了
  Security Manager。
cover: >-
  https://images.unsplash.com/photo-1736244032196-5d604770aba8?crop=entropy&cs=srgb&fm=jpg&ixid=M3wxOTcwMjR8MHwxfHJhbmRvbXx8fHx8fHx8fDE3Mzg3NzIzNTN8&ixlib=rb-4.0.3&q=85
coverY: 0
---

# Java17

## 📌 Java 17 新特性总结表格

| **类别**       | **新特性**                                  | **作用**               |
| ------------ | ---------------------------------------- | -------------------- |
| **语法增强**     | `sealed class`（JEP 409）                  | 限制类的继承，提高安全性         |
| **语法增强**     | `Pattern Matching for switch`（JEP 406）   | `switch` 语法优化，支持模式匹配 |
| **JVM 内存管理** | `Foreign Function & Memory API`（JEP 412） | 提供安全的堆外内存访问          |
| **安全性**      | 移除 `Security Manager`（JEP 411）           | 清理过时的安全管理机制          |

## 1.sealed class（JEP 409，正式特性）

### 作用

* 限制类的继承范围，防止随意扩展，提高安全性。

### 代码示例

```java
// 密封类，指定允许的子类
public sealed class Shape permits Circle, Rectangle {}

final class Circle extends Shape {}

final class Rectangle extends Shape {}
```

⚠️ 适用于：

* API 设计
* 提高代码安全性

## 2.Pattern Matching for switch（JEP 406）

作用

* switch 语法改进，支持模式匹配，优化数据结构处理。

### 代码示例

```java
public class SwitchPatternMatchingDemo {
    static void test(Object obj) {
        switch (obj) {
            case Integer i -> System.out.println("Integer: " + i);
            case String s -> System.out.println("String: " + s);
            case null -> System.out.println("Null value");
            default -> System.out.println("Other: " + obj);
        }
    }

    public static void main(String[] args) {
        test(42);
        test("Hello");
        test(null);
    }
}
```

⚠️ 适用于：

* 简化 switch 代码
* 减少 instanceof 判断

## 3.Foreign Function & Memory API（JEP 412）

### 作用

* 允许 Java 直接调用本地 C 代码，无需 JNI，提高跨语言互操作性。

### 代码示例

```
try (Arena arena = Arena.ofConfined()) {
    MemorySegment segment = arena.allocate(100);
    segment.set(ValueLayout.JAVA_BYTE, 0, (byte) 1);
    byte value = segment.get(ValueLayout.JAVA_BYTE, 0);
    System.out.println(value);
}
```

⚠️ 适用于：

* 高性能计算
* JVM 之外的内存管理

## 4.移除 Security Manager（JEP 411）

### 作用

* Java 17 移除了 Security Manager，减少了 JVM 的安全管理机制。

⚠️ 影响

* 部分旧应用可能需要额外安全配置
* 推荐使用 Java 模块系统进行权限管理

