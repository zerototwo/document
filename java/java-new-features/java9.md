---
description: Java 9 引入了多个重要的新特性，包括 模块化系统、增强的 API、GC 改进 等。以下是 Java 9 的核心特性概览：
---

# Java9

## 📌 Java 9 新特性总结表格

| **类别**           | **新特性**                               | **作用**                           |
| ---------------- | ------------------------------------- | -------------------------------- |
| **核心平台**         | **模块化系统（JPMS）**                       | 解决 JAR 依赖冲突，提高安全性                |
| **集合 API**       | `List.of()` / `Set.of()` / `Map.of()` | 快速创建不可变集合                        |
| **Stream API**   | `takeWhile()` / `dropWhile()`         | 优化数据流处理，提高可读性                    |
| **Optional API** | `ifPresentOrElse()` / `or()`          | 更灵活的 `Optional` 处理方式             |
| **HTTP 客户端**     | `HttpClient`                          | 替代 `HttpURLConnection`，支持 HTTP/2 |
| **语法增强**         | 私有接口方法                                | 避免接口代码重复，提高代码封装性                 |
| **语法增强**         | try-with-resources 改进                 | 允许在 `try` 语句中使用已定义的资源            |
| **进程 API**       | `ProcessHandle`                       | 访问系统进程信息，提高进程管理能力                |
| **GC 改进**        | G1 GC 默认启用                            | 提高吞吐量，减少 Full GC                 |
| **JAR 兼容性**      | Multi-Release JAR                     | 允许不同 Java 版本加载不同实现               |
| **JShell**       | Java 交互式编程                            | 提供即时执行 Java 代码的环境，适用于学习和测试       |

## 1.Java 平台模块系统（JPMS）

### 作用

* 解决 JAR 依赖冲突（JAR Hell）
* 提高 安全性，限制包的访问
* 使 Java 运行时更小巧，适用于 IoT 设备

### 代码示例

#### （1）创建 module-info.java

```java
module com.example.app {
    requires java.logging;   // 依赖 logging 模块
    exports com.example.api; // 允许外部访问的包
}
```

#### （2）定义模块内的类

```javascript
package com.example.api;

public class Hello {
    public static void sayHello() {
        System.out.println("Hello, Java 9 Modules!");
    }
}
```

#### （3）使用模块

```java
import com.example.api.Hello;

public class Main {
    public static void main(String[] args) {
        Hello.sayHello();
    }
}
```

## 2.JShell：交互式 Java REPL

### 作用

* 提供 即时运行 Java 代码 的环境
* 适用于 测试、调试、学习

### 代码示例

```java
jshell> int x = 5;
jshell> System.out.println(x * x);
25
```

退出 JShell

```java
jshell> /exit
```

## 3.新集合工厂方法

### 作用

* 轻松创建 不可变集合
* 避免 Collections.unmodifiableList() 的冗长代码

```java
List<String> list = List.of("Java", "Python", "Go");
Set<Integer> set = Set.of(1, 2, 3, 4);
Map<Integer, String> map = Map.of(1, "A", 2, "B", 3, "C");

System.out.println(list);
System.out.println(set);
System.out.println(map);
```

{% hint style="danger" %}
注意：

• 这些集合不可修改（UnsupportedOperationException）

• 元素不能重复（否则会抛 IllegalArgumentException）
{% endhint %}

## 4.Stream API 增强

### 作用

* 增强 Stream 操作，优化数据处理

### 代码示例

```java
List<Integer> numbers = List.of(1, 2, 3, 4, 5, 6);

// takeWhile()：获取满足条件的前缀元素
List<Integer> takeWhileList = numbers.stream()
        .takeWhile(n -> n < 4)
        .collect(Collectors.toList());

System.out.println(takeWhileList); // [1, 2, 3]

// dropWhile()：删除满足条件的前缀元素
List<Integer> dropWhileList = numbers.stream()
        .dropWhile(n -> n < 4)
        .collect(Collectors.toList());

System.out.println(dropWhileList); // [4, 5, 6]
```

## 5.Optional 类增强

### 作用

* 避免 null 引发的 NullPointerException
* 提供更灵活的 空值处理

### 代码示例

```java
Optional<String> name = Optional.of("Java 9");

// ifPresentOrElse()
name.ifPresentOrElse(
        System.out::println, 
        () -> System.out.println("No value present")
);

// or()
String defaultValue = name.or(() -> Optional.of("Default")).get();
System.out.println(defaultValue); // Java 9
```

## 6.HTTP/2 客户端

### 作用

* 取代 HttpURLConnection
* 支持 异步请求、WebSocket

### 代码示例

```java
HttpClient client = HttpClient.newHttpClient();
HttpRequest request = HttpRequest.newBuilder()
        .uri(URI.create("https://jsonplaceholder.typicode.com/todos/1"))
        .GET()
        .build();

HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());
System.out.println(response.body());
```

## 7.私有接口方法

### 作用

* 允许在接口中定义 私有方法，避免代码重复

### 代码示例

```java
interface Logger {
    default void logInfo(String message) {
        log(message, "INFO");
    }
    
    private void log(String message, String level) {
        System.out.println("[" + level + "] " + message);
    }
}
```

## 8.try-with-resources 改进

### 作用

* 允许在 try 语句中 使用已定义的资源，无需额外声明

### 代码示例

```java
BufferedReader reader = new BufferedReader(new FileReader("test.txt"));

try (reader) {
    System.out.println(reader.readLine());
} // 资源会自动关闭
```

## 9.进程 API 改进

### 作用

* 提供 ProcessHandle 访问 系统进程信息

### 代码示例

```java
ProcessHandle currentProcess = ProcessHandle.current();
System.out.println("PID: " + currentProcess.pid());
System.out.println("Command: " + currentProcess.info().command().orElse("Unknown"));
```

## 10.G1 GC 作为默认垃圾回收器

### 作用

* 降低 Full GC 停顿
* 提高吞吐量

### 启用 G1 GC

```sh
java -XX:+UseG1GC MyApplication
```





