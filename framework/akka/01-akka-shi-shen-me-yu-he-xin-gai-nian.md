# 01 · Akka 是什么与核心概念

### 1. Akka 是什么

Akka 是基于 **Actor 模型**的并发框架。

在 Akka 中，可以将业务拆成多个 Actor。每个 Actor 负责接收消息、执行业务，并维护自己的状态。

例如，一个账户 Actor 可以处理：

```
存款消息 → 增加余额
取款消息 → 减少余额
查询消息 → 回复当前余额
```

外部通过消息请求操作账户，而不是直接修改它的余额字段。

### 2. 为什么需要 Actor

假设多个线程同时执行：

```
count++;
```

这不是一个不可分割的操作，它包含：

```
读取 count → 加 1 → 写回 count
```

两个线程可能读到相同的旧值，最终覆盖彼此的结果。

普通 Java 可以通过锁等机制解决。Actor 则通过组织状态的归属来处理这类问题：

```
发送者 A ── Add 消息 ──┐
                      ↓
                     邮箱 → Counter Actor → 修改 count
                      ↑
发送者 B ── Add 消息 ──┘
```

**同一个 Actor 一次处理一条消息。**

如果 `count` 只由这个 Actor 的消息处理逻辑访问，就不需要因为多个发送者而给它加锁。

但多个 Actor 共同修改一个外部对象时，仍然需要考虑并发问题。

### 3. ActorSystem：运行环境

`ActorSystem` 为 Actor 提供运行环境，管理 Actor 生命周期、线程调度和定时调度等资源。

```
ActorSystem system = ActorSystem.create("demo");
```

一个 ActorSystem 可以管理多个 Actor：

```
ActorSystem
├── Teacher Actor
│   ├── Counter A
│   └── Counter B
└── Monitor Actor
```

通常不需要为每个 Actor 创建一个 ActorSystem。

程序结束时，应关闭系统并释放资源：

```
system.terminate();
```

这是异步关闭请求，不代表调用返回时所有资源已经释放。

### 4. Actor：处理消息的工作单元

一个 Actor 通常包含：

* 自己的状态，例如计数值、任务进度。
* 消息处理逻辑，例如收到累加指令后修改计数。
* 生命周期逻辑，例如启动时初始化、停止时清理。

例如：

```
Counter Actor

内部状态：
    total = 0

可以处理的消息：
    Add(3)   → total 增加 3
    GetValue → 回复当前 total
```

两个 Counter Actor 各自有一份状态，使用相同的 Java 类并不意味着共享实例字段。

### 5. ActorRef：通信引用

`ActorRef` 是向 Actor 发送消息时使用的引用。

```
ActorRef counter = system.actorOf(
        Props.create(Counter.class),
        "counter"
);
```

这段代码表示：

1. 使用 `Props` 描述如何创建 Counter。
2. 由 ActorSystem 创建并管理 Actor。
3. 返回这个 Actor 的通信引用。

`counter` 不是 Counter 的 Java 实例，不能通过它直接读取内部字段。

```
counter.tell(new Add(3), ActorRef.noSender());
```

这表示向 Counter 发送一条累加消息。

多个调用方可以持有同一个 ActorRef，不会因此创建多个 Actor。

> 上面的代码用于说明概念，完整的类、消息定义和入口会在后续 Demo 中给出。

### 6. ActorSystem、Actor 和 ActorRef 的关系

| 概念          | 负责什么               |
| ----------- | ------------------ |
| ActorSystem | 提供运行环境，创建和管理 Actor |
| Actor       | 接收消息、执行业务、管理状态     |
| ActorRef    | 供外部向 Actor 发送消息    |

它们的关系可以表示为：

```
ActorSystem 创建并管理 Actor
                    ↑
调用方通过 ActorRef 发送消息
```

ActorRef 是通信入口，ActorSystem 是运行环境，实际业务由 Actor 处理。

### 7. Mailbox：邮箱

发给 Actor 的普通消息会经过邮箱，等待调度处理。

```
发送消息 → 邮箱 → 调度执行 → Actor 处理消息
```

例如：

```
Counter 邮箱：

Add(1)
Add(2)
GetValue
```

使用默认邮箱，且这些消息由同一个发送者依次直接发送时，Counter 先处理两次累加，再处理查询。

不同发送者之间没有全局顺序保证，自定义优先级邮箱也可能影响处理顺序。

### 8. Actor 是一个线程吗

**不是。**

Actor 通常由 Dispatcher 的线程池调度。

```
Dispatcher 线程池
├── 线程 1：处理 Actor A 的一条消息
├── 线程 2：处理 Actor B 的一条消息
└── 线程 3：处理 Actor C 的一条消息
```

同一个 Actor 处理下一条消息时，可能换到另一个线程。

需要区分：

| 说法                     | 是否正确 |
| ---------------------- | ---- |
| 每个 Actor 独占一个线程        | 否    |
| 同一个 Actor 一次处理一条普通消息   | 是    |
| 不同 Actor 可以并行处理消息      | 是    |
| Actor 启动的外部异步任务也自动串行执行 | 否    |

因此，在 Actor 内执行长时间阻塞操作，可能占用共享线程，影响其他 Actor。

### 9. tell：异步发送消息

发送消息的基本形式：

```
receiver.tell(message, sender);
```

| 参数或对象      | 含义            |
| ---------- | ------------- |
| `receiver` | 接收者的 ActorRef |
| `message`  | 消息内容          |
| `sender`   | 这条消息声明的发送者    |

`tell()` 不等待业务完成。

```
counter.tell(new Add(1), ActorRef.noSender());
System.out.println("发送方法已返回");
```

打印日志时，Actor 可能已经处理消息，也可能还没开始。

异步意味着调用方不等待，不意味着接收方一定在调用方下一行代码之后执行。

### 10. Actor 适合什么场景

当业务需要独立状态、消息协作和生命周期管理时，可以考虑 Actor，例如：

* 连接管理：处理心跳、超时检查和关闭指令。
* 任务协调：管理任务进度，接收完成或失败结果。
* 状态管理：由一个 Actor 维护某个业务对象的状态。
* 异常监督：由父 Actor 决定子 Actor 出错后如何处理。

如果只是一个简单的周期任务，`@Scheduled` 通常更直接。

Actor 也不会自动提供数据库事务、消息持久化或业务重试，这些能力需要单独设计。

### 11. 下一篇

下一篇通过完整的 `Lesson01Hello` Demo，学习创建 ActorSystem、创建 Actor，以及使用 `tell()` 发送第一条消息。
