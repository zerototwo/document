---
description: >-
  Java 12 作为短期支持版本（非 LTS），引入了 switch 表达式增强、G1 GC 改进、JVM 常量 API
  等特性，主要侧重于语言优化和性能提升。
cover: >-
  https://images.unsplash.com/photo-1736177046343-32c5d0f9bcc6?crop=entropy&cs=srgb&fm=jpg&ixid=M3wxOTcwMjR8MHwxfHJhbmRvbXx8fHx8fHx8fDE3Mzg3NTU0MzZ8&ixlib=rb-4.0.3&q=85
coverY: 0
---

# Java12

## 📌 Java 12 新特性总结表格

| **类别**     | **新特性**             | **作用**                |
| ---------- | ------------------- | --------------------- |
| **语法增强**   | `switch` 表达式（预览特性）  | `switch` 语句可以作为表达式返回值 |
| **GC 改进**  | G1 GC 改进            | 减少 Full GC 触发，提高吞吐量   |
| **GC 变更**  | Shenandoah GC（实验性）  | 低延迟垃圾回收               |
| **JVM 改进** | JVM 常量 API（JEP 334） | 改进字节码生成               |
| **安全增强**   | TLS 1.3 完整实现        | 提高 HTTPS 安全性          |
| **性能优化**   | 低开销堆分析              | 改进 JVM 性能分析           |

## 1.switch 表达式增强（JEP 325，预览特性）

## 作用

* switch 语句可以作为表达式返回值，简化代码。
* 支持 -> 语法，消除 break 关键字。

### 代码示例

```java
public class SwitchDemo {
    public static void main(String[] args) {
        String day = "MONDAY";

        // 传统方式
        int result;
        switch (day) {
            case "MONDAY":
            case "FRIDAY":
                result = 6;
                break;
            case "SUNDAY":
                result = 7;
                break;
            default:
                result = 0;
        }
        System.out.println(result);

        // Java 12 新方式
        int num = switch (day) {
            case "MONDAY", "FRIDAY" -> 6;
            case "SUNDAY" -> 7;
            default -> 0;
        };
        System.out.println(num);
    }
}
```

### ⚠️ 注意：

* switch 语句可以返回值，以前必须用 break 控制跳出。
* -> 语法 替代 case 语句中的 break，减少冗余代码。

## 2.G1 GC 改进

### 作用

* 减少 Full GC 触发频率，提高吞吐量。
* 自动调整 GC 回收策略，适用于大规模应用。

### 启用 G1 GC

```sh
java -XX:+UseG1GC MyApplication
```

⚠️ 变化点：

* 在 Java 9/10/11 中，G1 GC 可能触发 Full GC。
* Java 12 进一步优化 G1 GC，减少 Full GC 触发。

## 3.Shenandoah GC（实验性）

作用

* 比 G1 GC 停顿时间更短，适用于低延迟应用。
* 垃圾回收可以与应用线程并行执行，减少 GC 对应用性能的影响。

### 启用 Shenandoah GC

```java
java -XX:+UnlockExperimentalVMOptions -XX:+UseShenandoahGC MyApplication
```

### ⚠️ 适用场景：

* 高并发应用、金融交易系统、低延迟服务。

## 4.JVM 常量 API（JEP 334）

### 作用

* 提供新的 API 以支持更高效的字节码生成。
* 增强 JVM 对常量池的操作能力。

### 代码示例

```java
import java.lang.constant.*;

public class ConstantDemo {
    public static void main(String[] args) {
        String str = "Java 12";
        ConstantDesc constantDesc = DynamicConstantDesc.ofCanonical(str);
        System.out.println(constantDesc);
    }
}
```

⚠️ 适用于：

* 编译器优化
* JVM 字节码增强
* 运行时动态计算

## 5.TLS 1.3 完整实现

### 作用

* Java 12 默认启用 TLS 1.3，增强 HTTPS 安全性。
* 提供更快的加密握手，提高性能。

### 启用 TLS 1.3

```java
SSLContext context = SSLContext.getInstance("TLSv1.3");
System.out.println("Enabled TLS Version: " + context.getProtocol());
```

### ⚠️ 适用场景：

* HTTPS、加密通信、OAuth 认证、SSL/TLS 证书校验。

## 6.低开销堆分析

### 作用

* 提供更高效的内存分析方法，降低对 JVM 性能的影响。
* 适用于调试 GC、线程、内存管理问题。

### 启用方式

```sh
java -Xlog:heap+stats MyApplication
```

### ⚠️ 适用场景：

* 高性能服务器应用
* 生产环境 JVM 监控

