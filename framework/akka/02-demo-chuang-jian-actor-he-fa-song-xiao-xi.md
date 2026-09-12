# 02 · Demo：创建 Actor 和发送消息

### 1. 本节目标

通过一个打招呼的例子，理解以下流程：

```
创建 ActorSystem
    ↓
创建 Greeter Actor，获得 ActorRef
    ↓
发送 SayHello 消息
    ↓
Greeter 收到消息，打印问候
    ↓
关闭 ActorSystem
```

本节使用 **Java 17、Akka Classic 2.6.20**。

### 2. 添加依赖

在 Maven 项目的 `pom.xml` 中添加：

```
<properties>
    <maven.compiler.source>17</maven.compiler.source>
    <maven.compiler.target>17</maven.compiler.target>
    <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
</properties>

<dependencies>
    <dependency>
        <groupId>com.typesafe.akka</groupId>
        <artifactId>akka-actor_2.13</artifactId>
        <version>2.6.20</version>
    </dependency>
</dependencies>
```

`_2.13` 表示该 Akka 包对应的 Scala 二进制版本。使用 Java API 时也需要这个依赖名称，不需要因此编写 Scala 代码。

### 3. 完整 Demo

创建文件 `Lesson01Hello.java`，运行其中的 `main()`。

```
package com.isep.akka.lessons;

import akka.actor.AbstractActor;
import akka.actor.ActorRef;
import akka.actor.ActorSystem;
import akka.actor.Props;

public class Lesson01Hello {

    // 定义消息：携带一个需要打招呼的名字。
    public record SayHello(String name) { }

    public static void main(String[] args) {
        // ActorSystem 是运行环境，可以管理多个 Actor。
        ActorSystem system = ActorSystem.create("lesson01");

        // Props 描述如何创建 Greeter。
        // ActorSystem 创建并管理 Actor，返回通信引用 ActorRef。
        // greeter 不是 Greeter 实例，不能用它直接读取 Actor 内部字段。
        ActorRef greeter = system.actorOf(
                Props.create(Greeter.class),
                "greeter"
        );

        System.out.println("[main] 准备发送消息");

        // 接收者：greeter。
        // 消息：SayHello。
        // 发送者：main 不是 Actor，这里不指定发送者 Actor。
        greeter.tell(
                new SayHello("Akka 初学者"),
                ActorRef.noSender()
        );

        // tell 返回不代表 Greeter 已经完成消息处理。
        System.out.println("[main] tell 已返回");

        // 只在 main 中等待系统关闭。
        // 不要把这种阻塞等待放到 Actor 的消息处理方法中。
        system.getWhenTerminated().toCompletableFuture().join();
    }

    public static class Greeter extends AbstractActor {

        @Override
        public Receive createReceive() {
            // 注册消息处理规则，并不是这里主动发送消息。
            return receiveBuilder()
                    .match(SayHello.class, message -> {
                        System.out.println(
                                "[Greeter] 你好，" + message.name()
                        );

                        // 打印完成后，发起整个 ActorSystem 的关闭。
                        getContext().getSystem().terminate();
                    })
                    .build();
        }
    }
}
```

### 4. 定义消息：SayHello

```
public record SayHello(String name) { }
```

`record` 是 Java 用来声明数据载体的语法，不是 Akka 特有语法。

这里定义了一种消息，它携带一个 `String` 类型的名字。

#### 创建消息

```
SayHello message = new SayHello("张三");
```

#### 读取消息内容

```
System.out.println(message.name());
```

输出：

```
张三
```

Java 会自动生成构造方法、`name()` 读取方法，以及 `equals()`、`hashCode()`、`toString()`。

注意，读取方法是 `name()`，不是 `getName()`。

`record` 不提供字段的 setter，但如果字段引用可变集合，集合内容仍然可能被修改。本例只有 `String` 字段，适合作为不可变消息。

### 5. 创建运行环境：ActorSystem

```
ActorSystem system = ActorSystem.create("lesson01");
```

创建一个名称为 `lesson01` 的 ActorSystem。

它负责提供 Actor 运行所需的资源，例如：

* 创建和管理 Actor。
* 调度消息处理。
* 管理生命周期。
* 提供定时调度能力。

这里的 `"lesson01"` 是系统名称，不是 Actor 名称。

### 6. 创建 Actor：Props 和 ActorRef

```
ActorRef greeter = system.actorOf(
        Props.create(Greeter.class),
        "greeter"
);
```

可以分成三个部分理解。

#### Props.create(Greeter.class)

```
Props.create(Greeter.class)
```

描述使用 `Greeter` 类的无参构造方法创建 Actor。

Akka 根据这个描述管理实例创建。不要自行创建 Actor 实例后直接调用业务方法。

#### system.actorOf(...)

```
system.actorOf(..., "greeter")
```

请求 ActorSystem 创建一个名为 `greeter` 的 Actor。

创建方法返回时，不代表 Actor 已完成启动和业务处理，但可以立即使用返回的引用发送消息。

#### ActorRef greeter

```
ActorRef greeter
```

保存这个 Actor 的通信引用。

关系如下：

```
ActorSystem
    │ 创建并管理
    ↓
Greeter Actor
    ↑
ActorRef 指向它，供调用方发送消息
```

`greeter` 的类型是 `ActorRef`，不是 `Greeter`，因此不能通过它直接访问 Greeter 的内部字段或业务方法。

### 7. 发送消息：tell

```
greeter.tell(
        new SayHello("Akka 初学者"),
        ActorRef.noSender()
);
```

对应方法形式：

```
receiver.tell(message, sender);
```

| 位置    | 本例内容                  | 含义           |
| ----- | --------------------- | ------------ |
| 接收者   | `greeter`             | 消息发给哪个 Actor |
| 第一个参数 | `new SayHello(...)`   | 消息内容         |
| 第二个参数 | `ActorRef.noSender()` | 不指定发送者 Actor |

`ActorRef.noSender()` 不表示消息没有接收者。接收者已经由 `greeter` 指定。

以后在 Actor 内向另一个 Actor 发消息，希望对方能够回复时，通常使用：

```
otherActor.tell(message, getSelf());
```

此时 `getSelf()` 表示当前发送消息的 Actor。

### 8. 接收消息：createReceive

```
@Override
public Receive createReceive() {
    return receiveBuilder()
            .match(SayHello.class, message -> {
                System.out.println(
                        "[Greeter] 你好，" + message.name()
                );

                getContext().getSystem().terminate();
            })
            .build();
}
```

`createReceive()` 用来定义消息处理规则。

#### receiveBuilder()

创建消息处理规则的构建器。

#### match(SayHello.class, ...)

如果收到的消息属于 `SayHello` 类型，就执行对应的 Lambda。

```
message -> {
    System.out.println(message.name());
}
```

这里的 `message` 就是收到的 `SayHello` 对象。

#### build()

将前面声明的规则构建为 `Receive`，交给 Akka 用于分派收到的消息。

这些规则不是在 main 中直接调用的。消息到达后，由 Akka 调度 Actor 执行匹配的处理逻辑。

### 9. getContext() 是什么

```
getContext().getSystem().terminate();
```

分开理解：

| 表达式            | 含义               |
| -------------- | ---------------- |
| `getContext()` | 当前 Actor 的运行上下文  |
| `getSystem()`  | 获取所属 ActorSystem |
| `terminate()`  | 发起整个系统的关闭        |

本例在打完招呼后关闭系统，因此 main 中的等待最终会结束。

```
system.getWhenTerminated().toCompletableFuture().join();
```

这行只阻塞 main 线程，等待系统关闭完成，不会阻止 Greeter 处理消息。

### 10. 整体执行顺序

```
main 线程                         Actor 调度线程
    │                                  │
创建 ActorSystem                       │
    │                                  │
创建 Greeter，取得 ActorRef             │
    │                                  │
打印“准备发送消息”                     │
    │                                  │
tell 发送 SayHello ───────────────────→ 邮箱
    │                                  │
tell 返回                         处理 SayHello
    │                                  │
打印“tell 已返回”                 打印问候
    │                                  │
等待系统关闭                      发起系统关闭
    │                                  │
    └──────── 系统关闭完成 ─────────────┘
    │
main 结束
```

图中左右两侧会并发推进，不能将它理解成所有行严格按照上下位置交替执行。

### 11. 预期输出

可能看到：

```
[main] 准备发送消息
[main] tell 已返回
[Greeter] 你好，Akka 初学者
```

也可能看到：

```
[main] 准备发送消息
[Greeter] 你好，Akka 初学者
[main] tell 已返回
```

两种顺序都正常。

**异步表示发送方不等待业务完成，不表示接收方一定在发送方下一行代码之后执行。**

以上是预期现象，不是本次运行记录。

### 12. 动手练习

将消息修改为：

```
new SayHello("张三")
```

在 Greeter 中增加线程名称输出：

```
System.out.println(
        "[Greeter] 当前线程：" + Thread.currentThread().getName()
);
```

在 main 中也打印线程名称，观察发送消息与处理消息所在线程的区别。

下一篇学习：**创建两个 Counter Actor，分别维护状态，并将查询结果回复给 Teacher。**
