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

| **类别**         | **新特性**                                          | **作用**                           |
| -------------- | ------------------------------------------------ | -------------------------------- |
| **语法增强**       | Lambda 变量支持 `var` 关键字                            | 让 Lambda 代码风格更统一                 |
| **字符串 API**    | `isBlank()` / `strip()` / `lines()` / `repeat()` | 增强字符串处理能力                        |
| **新 HTTP 客户端** | `HttpClient`                                     | 替代 `HttpURLConnection`，支持 HTTP/2 |
| **GC 改进**      | ZGC（低停顿垃圾回收器）                                    | 提高吞吐量，减少 Full GC                 |
| **并发优化**       | `Flight Recorder` & `JFR`                        | 低开销 JVM 监控                       |
| **安全性**        | `Root Certificates`（默认可信 CA 证书）                  | Java 默认包含 CA 证书                  |
| **多版本 JAR**    | `Launch Single-File Programs`                    | 直接运行 `.java` 文件                  |
| **JDK 轻量化**    | **移除 Java EE 和 CORBA**                           | 精简 JDK，提升运行效率                    |

## 1.Lambda 表达式支持 var 关键字

### 作用

* 让 Lambda 代码风格更统一，支持 final 修饰符，提高可读性。

### 代码示例

```java
List<String> list = List.of("Java", "Python", "Go");

// 传统方式（Java 8）
list.forEach(s -> System.out.println(s));

// Java 11：支持 `var` 关键字
list.forEach((var s) -> System.out.println(s));

// 可以添加修饰符
list.forEach((@Nonnull var s) -> System.out.println(s));
```

{% hint style="warning" %}
所有参数必须都使用 var，不能混用 var 和显式类型。
{% endhint %}

## 2.新增字符串方法

### 作用

* 增强字符串处理能力，提高开发效率。

### 代码示例

```java
String str = "  Java 11  ";

// `isBlank()`：判断字符串是否为空白（比 `trim().isEmpty()` 更简洁）
System.out.println(str.isBlank()); // false

// `strip()`：去除首尾空格（比 `trim()` 更好）
System.out.println(str.strip()); // "Java 11"

// `lines()`：按行拆分字符串（比 `split("\n")` 更高效）
"Java\nPython\nGo".lines().forEach(System.out::println);

// `repeat()`：重复字符串（比循环拼接更简洁）
System.out.println("Java ".repeat(3)); // Java Java Java

```

## 3.新 HTTP 客户端

### 作用

* 替代 HttpURLConnection，支持 HTTP/2 和 WebSocket，增强网络通信能力。

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

{% hint style="info" %}
• REST API 调用

• WebSocket 交互

• 异步网络请求
{% endhint %}

## 4.ZGC（低停顿垃圾回收器）

### 作用

* 减少 GC 停顿时间，提高大内存应用的吞吐量。

### 启用 ZGC

```sh
java -XX:+UnlockExperimentalVMOptions -XX:+UseZGC MyApplication
```

{% hint style="info" %}
适用于：

• 大内存 JVM 应用（>8GB）

• 低延迟服务（高并发 Web 应用）
{% endhint %}

## 5.Flight Recorder & JFR（JVM 监控）

### 作用

* 轻量级 JVM 监控工具，替代 VisualVM，对性能影响极小。

### 启用 JFR

```sh
java -XX:+UnlockCommercialFeatures -XX:+FlightRecorder -XX:StartFlightRecording=duration=60s MyApplication
```

## 6.Root Certificates（默认 CA 证书）

### 作用

* Java 11 默认包含可信 CA 证书，无需手动导入，提高 HTTPS 安全性。

{% hint style="info" %}
适用于：

• HTTPS 连接

• OAuth 认证

• SSL/TLS 证书校验
{% endhint %}

## 7.直接运行 .java 文件

### 作用

* 让 Java 代码像脚本语言一样直接运行。

### 代码示例

```java
public class Hello {
    public static void main(String[] args) {
        System.out.println("Hello, Java 11!");
    }
}
```

直接运行：

```sh
java Hello.java
```

{% hint style="info" %}
适用于小型 Java 程序（无需编译）
{% endhint %}

## 8.移除 Java EE 和 CORBA

### 作用

* Java 11 移除了 javax.xml、javax.jws、CORBA，使 JDK 更轻量级。

### 受影响的 API

| **已移除模块**       | **影响** |
|----------------------|---------|
| `java.xml.ws`       | **Web Services API**（JAX-WS） |
| `java.xml.ws.annotation` | **JAX-WS 注解支持** |
| `java.xml.bind`      | **JAXB（Java XML Binding）** |
| `java.xml.bind.annotation` | **JAXB 相关注解** |
| `java.activation`    | **JavaBeans Activation Framework** |
| `java.corba`        | **CORBA（远程方法调用）相关 API** |
| `java.transaction`   | **Java 事务 API（JTA）** |
| `java.se.ee`        | **Java EE 相关 API，影响 JPA、JTA、JAX-WS** |

---

{% hint style="info" %}
解决方案：

• 如果需要这些 API，可以使用 外部依赖（如 javax.xml.bind:jaxb-api）。
{% endhint %}



