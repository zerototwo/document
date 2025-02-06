---
description: Java 15 是 短期版本（非 LTS），主要引入了 sealed class（密封类）、record（正式支持）、ZGC 改进、文本块增强 等新特性。
cover: >-
  https://images.unsplash.com/photo-1735467547583-d9fc4503f238?crop=entropy&cs=srgb&fm=jpg&ixid=M3wxOTcwMjR8MHwxfHJhbmRvbXx8fHx8fHx8fDE3Mzg4NDM2ODN8&ixlib=rb-4.0.3&q=85
coverY: 0
---

# Java15

## 📌 Java 15 新特性总结表格

| **类别**     | **新特性**                              | **作用**            |
| ---------- | ------------------------------------ | ----------------- |
| **数据类**    | `record` 关键字（JEP 384）                | 代替 `POJO`，简化数据类编写 |
| **语法增强**   | `sealed class`（JEP 360）              | 限制类的继承，增强安全性      |
| **GC 改进**  | ZGC 成为正式特性（JEP 377）                  | 低延迟垃圾回收，提升吞吐量     |
| **安全增强**   | `Hidden Classes`（JEP 371）            | 提供隐藏类，适用于动态代理     |
| **文本块**    | `Text Blocks`（JEP 378）               | 正式支持 `"""` 多行字符串  |
| **安全增强**   | 移除 `Nashorn` JavaScript 引擎（JEP 372）  | 进一步精简 JDK         |
| **JVM 改进** | `Foreign-Memory Access API`（JEP 383） | 安全访问堆外内存          |

## 1.record 关键字（JEP 384，正式特性）

### 作用

* 简化数据类的编写，自动生成 getter、equals()、hashCode()、toString() 方法。
* 代替 POJO 或 Lombok @Data，减少样板代码。

### 代码示例

```javascript
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

⚠️ 适用于：

* 不可变对象（Immutable Objects）
* 数据传输对象（DTO）
* 配置类、日志类

## 2.sealed class（JEP 360，预览特性）

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

* 限制类的继承范围
* 提供更安全的 API 设计

## 3.ZGC 成为正式特性（JEP 377）

### 作用

* ZGC 现在已成为 Java 15 的默认垃圾回收器（正式支持）。
* 低停顿时间，适用于大内存应用。

### 启用 ZGC

```sh
java -XX:+UseZGC MyApplication
```

⚠️ 适用于：

* 大内存 JVM 应用（>8GB）
* 低延迟 Web 服务

## 4.Hidden Classes（JEP 371）

### 作用

* 支持隐藏类，使 Java 动态代理更加安全。

### 代码示例

```java
Lookup lookup = MethodHandles.lookup();
Class<?> hiddenClass = lookup.defineHiddenClass(bytecode, true).lookupClass();
```

⚠️ 适用于：

* 动态代理
* 字节码增强
* JVM 插件开发

## 5.Text Blocks（JEP 378，正式特性）

### 作用

* 正式支持 """ 多行字符串，使代码更加清晰。

### 代码示例

```java
String html = """
    <html>
        <body>
            <h1>Hello, Java 15!</h1>
        </body>
    </html>
    """;
System.out.println(html);
```

⚠️ 适用于：

* HTML、SQL、JSON
* 日志记录

## 6.移除 Nashorn JavaScript 引擎（JEP 372）

### 作用

* Java 15 移除了 Nashorn JavaScript 引擎，精简 JDK 体积。

⚠️ 解决方案：

* 使用 GraalVM 作为 JavaScript 运行时。

## 7.Foreign-Memory Access API（JEP 383）

### 作用

* 提供安全的 API 访问堆外内存（替代 Unsafe）。

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





