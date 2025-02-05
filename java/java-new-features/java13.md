---
description: Java 13 是 短期版本（非 LTS），主要在 语法增强（Text Blocks）、性能优化（ZGC 改进） 方面进行了优化。
cover: >-
  https://images.unsplash.com/photo-1736347837458-7cc3697ba57a?crop=entropy&cs=srgb&fm=jpg&ixid=M3wxOTcwMjR8MHwxfHJhbmRvbXx8fHx8fHx8fDE3Mzg3NjUzMzd8&ixlib=rb-4.0.3&q=85
coverY: 0
---

# Java13

## 📌 Java 13 新特性总结表格

| **类别**         | **新特性**                    | **作用**                        |
| -------------- | -------------------------- | ----------------------------- |
| **语法增强**       | 文本块（Text Blocks，JEP 355）   | 简化多行字符串处理                     |
| **GC 改进**      | ZGC 不再暂停 GC 线程（JEP 351）    | 提高垃圾回收效率，降低停顿                 |
| **JVM 改进**     | 动态 `AppCDS` 归档（JEP 350）    | 改进 Class-Data Sharing         |
| **语法增强**       | `switch` 语法增强（JEP 354）     | 允许 `yield` 关键字，优化 `switch` 逻辑 |
| **Socket API** | `Socket` API 重新实现（JEP 353） | 提高网络 I/O 效率                   |

## 1.文本块（Text Blocks，JEP 355）

### 作用

* 简化多行字符串处理，避免繁琐的 \n 转义字符。
* 提高 HTML、JSON、SQL 代码的可读性。

### 代码示例

```java
public class TextBlockDemo {
    public static void main(String[] args) {
        // 传统方式
        String html = "<html>\n" +
                      "    <body>\n" +
                      "        <h1>Hello, Java 13!</h1>\n" +
                      "    </body>\n" +
                      "</html>";

        // Java 13 新方式（Text Blocks）
        String htmlBlock = """
            <html>
                <body>
                    <h1>Hello, Java 13!</h1>
                </body>
            </html>
            """;

        System.out.println(htmlBlock);
    }
}
```

⚠️ 适用场景：

* HTML、SQL、JSON、XML 代码处理
* 日志记录、REST API 调试

## 2.ZGC 改进（JEP 351）

### 作用

* 应用程序可以在运行时创建类数据共享（CDS）归档文件，减少 JVM 启动时间。

```sh
# 运行应用，生成 CDS 归档
java -Xshare:dump -XX:SharedArchiveFile=app-cds.jsa -cp MyApplication.jar
```

### 适用于：

* 云计算环境
* Java 应用程序的快速启动优化

## 4.switch 语法增强（JEP 354）

### 作用

* 支持 yield 关键字，使 switch 语句能够返回值。

### 代码示例

```java
public class SwitchDemo {
    public static void main(String[] args) {
        String day = "MONDAY";

        // Java 13 新方式（使用 yield 返回值）
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

⚠️ yield 用于返回值，适用于：

* 优化 switch 逻辑
* 减少 break 关键字的使用

## 5.Socket API 重新实现（JEP 353）

作用

* 对 Socket 和 ServerSocket 进行了重新实现，提升了 I/O 处理效率，提高吞吐量。

### 代码示例

```java
ServerSocket server = new ServerSocket(8080);
Socket socket = server.accept();
System.out.println("Client connected: " + socket.getInetAddress());
```

适用于：

* 高并发服务器
* 高性能网络通信



