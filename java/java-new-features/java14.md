---
description: Java 14 是 短期版本（非 LTS），但它引入了许多重要的新特性，包括 record 关键字、instanceof 模式匹配、G1 GC 改进等
---

# Java14

## 📌 Java 14 新特性总结表格

| **类别**     | **新特性**                                 | **作用**            |
| ---------- | --------------------------------------- | ----------------- |
| **数据类**    | `record` 关键字（JEP 359）                   | 代替 `POJO`，简化数据类编写 |
| **语法增强**   | `instanceof` 模式匹配（JEP 305）              | 省略显式类型转换，提高可读性    |
| **GC 改进**  | G1 GC NUMA 适配（JEP 366）                  | 提高多核 CPU 上的 GC 性能 |
| **异常增强**   | `NullPointerException` 提供更详细信息（JEP 358） | `NPE` 详细指示空指针来源   |
| **语法增强**   | `switch` 语法增强（JEP 361）                  | `switch` 语法成为正式特性 |
| **JVM 优化** | `Foreign-Memory Access API`（JEP 370）    | 安全访问堆外内存          |
| **调试工具**   | `JFR Event Streaming`（JEP 349）          | 提供低开销 JVM 监控      |

## 1.record 关键字（JEP 359）

### 作用

* 简化数据类的编写，自动生成 getter、equals()、hashCode()、toString() 方法。
* 代替 POJO 或 Lombok @Data，减少样板代码。

### 代码示例

```java
// 定义 record 数据类
public record User(String name, int age) {}

// 使用 record
public class RecordDemo {
    public static void main(String[] args) {
        User user = new User("Alice", 25);
        System.out.println(user.name()); // Alice
        System.out.println(user.age());  // 25
        System.out.println(user);  // User[name=Alice, age=25]
    }
}
```

⚠️ 适用于:

* 不可变对象（Immutable Objects）
* 数据传输对象（DTO）
* 配置类、日志类



## 2.instanceof 模式匹配（JEP 305）

### 作用

* instanceof 语法改进，自动进行类型转换，减少显式类型转换代码。

### 代码示例

```java
public class PatternMatchingDemo {
    public static void main(String[] args) {
        Object obj = "Hello, Java 14!";

        // 传统方式（Java 13 及以前）
        if (obj instanceof String) {
            String str = (String) obj;
            System.out.println(str.length());
        }

        // Java 14 方式（自动类型转换）
        if (obj instanceof String str) {
            System.out.println(str.length());
        }
    }
}
```

⚠️ 适用于：

* 简化 instanceof 类型检查
* 减少 cast 操作

## 3.G1 GC NUMA 适配（JEP 366）

### 作用

* G1 GC 现在更好地支持 NUMA（Non-Uniform Memory Access）架构，提高多核 CPU 的垃圾回收性能。

## 启用 G1 GC

```sh
java -XX:+UseG1GC MyApplication
```

⚠️ 适用于：

* 高并发服务器
* 多线程大规模应用

## 4.NullPointerException 详细信息（JEP 358）

### 作用

* NPE 现在提供详细的错误信息，指示具体的 null 值来源。

### 代码示例

```java
public class NPEDemo {
    public static void main(String[] args) {
        String str = null;
        System.out.println(str.length()); // 触发 NPE
    }
}
```

Java 14 NPE 输出示例

```sh
Exception in thread "main" java.lang.NullPointerException:
Cannot invoke "String.length()" because "str" is null
```

⚠️ 适用于：

* 调试 NullPointerException
* 快速定位 NPE 发生位置



## 5.switch 语法增强（JEP 361）

### 作用

* switch 语法成为正式特性，支持 表达式 和 yield 关键字。

### 代码示例

```java
public class SwitchDemo {
    public static void main(String[] args) {
        String day = "MONDAY";

        // Java 14 新方式（switch 表达式 + yield）
        int num = switch (day) {
            case "MONDAY", "FRIDAY" -> 6;
            case "SUNDAY" -> 7;
            default -> {
                System.out.println("Unknown day");
                yield 0;
            }
        };
        System.out.println(num);
    }
}
```

⚠️ 适用于：

* 优化 switch 逻辑
* 减少 break 关键字的使用

## 6.Foreign-Memory Access API（JEP 370）

### 作用

* 提供安全的 API 访问堆外内存（Unsafe 的替代方案）。

### 代码示例

```java
try (MemorySegment segment = MemorySegment.allocateNative(100)) {
    segment.set(ValueLayout.JAVA_BYTE, 0, (byte) 1);
    byte value = segment.get(ValueLayout.JAVA_BYTE, 0);
    System.out.println(value);
}
```

⚠️ 适用于：

* 高性能应用
* JVM 之外的内存管理

## 7.JFR Event Streaming（JEP 349）

### 作用

* 提供低开销的 JVM 监控工具，支持流式事件分析。

启用 JFR

```sh
java -XX:StartFlightRecording=duration=60s MyApplication
```

⚠️ 适用于：

* JVM 监控
* 性能优化





