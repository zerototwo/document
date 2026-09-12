# 03 · Demo：状态管理和消息回复

### 1. 本节目标

上一节学习了单向发送消息：

```
main → Greeter
```

这一节学习 Actor 之间的交互：

```
Teacher → Counter：累加、查询
Teacher ← Counter：回复结果
```

我们创建两个 Counter，各自维护独立的计数：

| Actor     | 操作       | 查询结果 |
| --------- | -------- | ---- |
| Counter A | 加 1，再加 2 | 3    |
| Counter B | 加 10     | 10   |

本节沿用 Java 17 和 Akka Classic 2.6.20，依赖配置见上一节。

### 2. 完整 Demo

创建文件 `Lesson02StateAndReply.java`，运行 `main()`。

```
package com.isep.akka.lessons;

import akka.actor.AbstractActor;
import akka.actor.ActorRef;
import akka.actor.ActorSystem;
import akka.actor.Props;

public class Lesson02StateAndReply {

    // 累加指令，amount 表示增加多少。
    public record Add(int amount) { }

    // 查询指令，不携带参数。
    public enum GetValue { INSTANCE }

    // 回复消息，携带计数器名称和查询时的值。
    public record Value(String name, int total) { }

    public static void main(String[] args) {
        ActorSystem system = ActorSystem.create("lesson02");

        // Teacher 启动后会创建两个 Counter。
        system.actorOf(Props.create(Teacher.class), "teacher");

        // 收齐回复后由 Teacher 关闭系统，main 在这里等待。
        system.getWhenTerminated().toCompletableFuture().join();
    }

    public static class Counter extends AbstractActor {

        // 每个 Counter 实例都有自己的 total，初始值为 0。
        // 只在当前 Actor 的消息处理逻辑中访问这个字段。
        private int total;

        @Override
        public Receive createReceive() {
            return receiveBuilder()
                    // 收到 Add 消息，修改当前 Counter 的状态。
                    .match(Add.class, message -> {
                        total += message.amount();
                    })
                    // 收到查询指令，向发送者回复结果。
                    .matchEquals(GetValue.INSTANCE, ignored -> {
                        // 当前查询来自 Teacher：
                        // getSender() 是 Teacher。
                        // getSelf() 是正在处理查询的 Counter。
                        getSender().tell(
                                new Value(getSelf().path().name(), total),
                                getSelf()
                        );
                    })
                    .build();
        }
    }

    public static class Teacher extends AbstractActor {

        // 已收到的查询回复数量，不是 Counter 的计数值。
        private int replies;

        @Override
        public void preStart() {
            // 创建两个子 Actor，各自有独立状态和邮箱。
            ActorRef counterA = getContext().actorOf(
                    Props.create(Counter.class),
                    "counter-a"
            );

            ActorRef counterB = getContext().actorOf(
                    Props.create(Counter.class),
                    "counter-b"
            );

            // 接收者是 Counter A，发送者是当前 Teacher。
            counterA.tell(new Add(1), getSelf());
            counterA.tell(new Add(2), getSelf());
            counterA.tell(GetValue.INSTANCE, getSelf());

            // Counter B 独立计数。
            counterB.tell(new Add(10), getSelf());
            counterB.tell(GetValue.INSTANCE, getSelf());
        }

        @Override
        public Receive createReceive() {
            return receiveBuilder()
                    .match(Value.class, value -> {
                        System.out.println(
                                "[收到回复] " + value.name()
                                        + " = " + value.total()
                        );

                        // 不依赖 A、B 的回复顺序，收齐两条后关闭。
                        if (++replies == 2) {
                            getContext().getSystem().terminate();
                        }
                    })
                    .build();
        }
    }
}
```

### 3. 先认识三种消息

Actor 之间通过消息表达请求和结果。本例有三种消息：

| 消息         | 方向                | 作用     |
| ---------- | ----------------- | ------ |
| `Add`      | Teacher → Counter | 请求累加   |
| `GetValue` | Teacher → Counter | 请求查询   |
| `Value`    | Counter → Teacher | 返回查询结果 |

#### Add：带参数的指令

```
public record Add(int amount) { }
```

创建消息：

```
new Add(2)
```

表示请求“加 2”。

Counter 通过 `amount()` 读取这个参数：

```
total += message.amount();
```

#### GetValue：不带参数的指令

```
public enum GetValue { INSTANCE }
```

这是只有一个枚举值的枚举类型。

`INSTANCE` 是自己定义的名字，不是 Java 关键字。这里用它表示“查询当前值”。

```
counterA.tell(GetValue.INSTANCE, getSelf());
```

查询本身不需要参数，因此不必每次创建新的消息对象。

#### Value：携带结果的回复

```
public record Value(String name, int total) { }
```

例如：

```
new Value("counter-a", 3)
```

表示 Counter A 的查询结果是 3。

这是结果数据，不是 Counter 实例本身。Teacher 收到它以后，通过 `name()` 和 `total()` 读取结果。

### 4. Teacher 如何创建 Counter

```
ActorRef counterA = getContext().actorOf(
        Props.create(Counter.class),
        "counter-a"
);
```

`getContext()` 是当前 Teacher 的运行上下文。

通过它调用 `actorOf()`，创建的是 **Teacher 的子 Actor**。

本例的管理关系为：

```
ActorSystem
└── Teacher
    ├── Counter A
    └── Counter B
```

这里的父子关系是 Akka 的运行时管理关系，不是 Java 类继承关系。

两次调用 `actorOf()`，即使使用相同的 Counter 类，也会创建两个不同的 Actor。

### 5. preStart() 什么时候执行

```
@Override
public void preStart() {
    // 创建 Counter，并发送消息。
}
```

`preStart()` 是 Actor 的生命周期方法。

正常启动时，Akka 会在这个 Actor 开始处理邮箱中的消息之前调用它，适合进行初始化，例如创建子 Actor、注册定时器等。

本例中：

```
创建 Teacher
    ↓
Teacher.preStart()
    ↓
创建两个 Counter，并向它们发送消息
    ↓
Teacher 开始处理邮箱中的回复
```

Counter 可以在 Teacher 的 `preStart()` 尚未结束时就开始处理消息和发送回复，但 Teacher 会等自己的 `preStart()` 完成后，再处理这些回复。

### 6. 为什么两个 Counter 的状态互不影响

Counter 内部定义：

```
private int total;
```

这是实例字段。

两个 Counter 各自有自己的实例，因此各有一份 `total`：

```
Counter A
    total = 0 → 1 → 3

Counter B
    total = 0 → 10
```

本例只有对应 Actor 的消息处理逻辑会访问自己的 `total`，所以使用普通 `int` 即可，不需要 `AtomicInteger`。

如果把它改成多个 Actor 共享的外部对象，就不能仅凭 Actor 的串行处理保证线程安全。

### 7. Counter 怎么匹配消息

#### match：按类型匹配

```
.match(Add.class, message -> {
    total += message.amount();
})
```

收到 `Add` 类型的消息时，执行累加逻辑。

其中 `message` 是当前收到的 `Add` 对象。

#### matchEquals：按值匹配

```
.matchEquals(GetValue.INSTANCE, ignored -> {
    // 回复查询结果。
})
```

收到与 `GetValue.INSTANCE` 相等的消息时，执行查询逻辑。

`ignored` 只是 Lambda 参数名，表示这里不需要读取消息内容。它不是特殊语法，也不是忽略这条消息。

### 8. Counter 如何回复 Teacher

Teacher 查询时发送：

```
counterA.tell(GetValue.INSTANCE, getSelf());
```

此时：

```
接收者：Counter A
消息：GetValue.INSTANCE
发送者：Teacher
```

Counter 处理查询时执行：

```
getSender().tell(
        new Value(getSelf().path().name(), total),
        getSelf()
);
```

对应关系变为：

```
接收者：Teacher
消息：Value
发送者：Counter A
```

几个方法的含义如下：

| 表达式                       | Counter 处理当前查询时的含义           |
| ------------------------- | ---------------------------- |
| `getSender()`             | 当前消息声明的发送者，即 Teacher         |
| `getSelf()`               | 当前 Counter 的 ActorRef        |
| `getSelf().path().name()` | 当前 Counter 的名称，如 `counter-a` |

完整往返过程：

```
Teacher
    │
    │ GetValue，发送者声明为 Teacher
    ↓
Counter A
    │
    │ Value("counter-a", 3)，发送者声明为 Counter A
    ↓
Teacher
```

**回复也是发送一条消息，不是普通方法的同步 return。**

Teacher 随后通过自己的消息处理规则接收结果：

```
.match(Value.class, value -> {
    System.out.println(value.total());
})
```

`getSender()` 与当前正在处理的消息有关，并不是永远指向某个固定 Actor。

### 9. tell 是异步，会不会先查询再累加

本例不会。

Teacher 依次向 Counter A 发送：

```
counterA.tell(new Add(1), getSelf());
counterA.tell(new Add(2), getSelf());
counterA.tell(GetValue.INSTANCE, getSelf());
```

这些消息来自同一个发送者，直接发给同一个接收者，且使用默认邮箱。

因此 Counter A 的处理顺序为：

```
Add(1) → Add(2) → GetValue
```

查询结果为 3。

但这个结论有适用范围：

| 场景                        | 顺序说明           |
| ------------------------- | -------------- |
| 本例 Teacher → Counter A    | 按上述顺序处理        |
| 不同 Actor 向同一个 Counter 发消息 | 没有跨发送者的全局顺序保证  |
| Teacher 向 Counter A、B 发消息 | A、B 可以并行处理     |
| 使用自定义优先级邮箱                | 可能改变处理顺序       |
| 消息处理中启动外部异步任务             | 任务完成顺序不由邮箱顺序保证 |

例如，`Add` 如果只是发起异步数据库更新就返回，后续 `GetValue` 可能在数据库更新完成前开始处理。

本例的加法在消息处理函数内直接完成，不存在这个问题。

### 10. 整体执行流程

```
main 创建 ActorSystem
    ↓
创建 Teacher
    ↓
Teacher.preStart()
    ├── 创建 Counter A
    └── 创建 Counter B
    ↓
Teacher 发送消息
    ├── Counter A：Add(1) → Add(2) → GetValue
    └── Counter B：Add(10) → GetValue
    ↓
两个 Counter 分别处理
    ├── A 回复 Value("counter-a", 3)
    └── B 回复 Value("counter-b", 10)
    ↓
Teacher 处理第一条 Value
    └── replies = 1
    ↓
Teacher 处理第二条 Value
    └── replies = 2，发起系统关闭
    ↓
main 等待结束，程序退出
```

虽然 Counter A 和 B 可以并行发送回复，但 Teacher 自己仍然一次处理一条消息，所以 `replies` 也可以使用普通 `int`。

### 11. 预期输出

```
[收到回复] counter-a = 3
[收到回复] counter-b = 10
```

也可能是：

```
[收到回复] counter-b = 10
[收到回复] counter-a = 3
```

两个 Counter 的回复顺序不固定，计数结果相同。

以上为预期现象，不是本次运行记录。

### 12. 动手练习

在 Counter A 的查询之前增加一条消息：

```
counterA.tell(new Add(1), getSelf());
counterA.tell(new Add(2), getSelf());
counterA.tell(new Add(5), getSelf());
counterA.tell(GetValue.INSTANCE, getSelf());
```

预期结果：

```
counter-a = 8
counter-b = 10
```

观察新增操作只影响 Counter A。然后尝试解释：为什么 Teacher 的 `replies` 和两个 Counter 的 `total` 都不需要使用 `AtomicInteger`？

下一篇学习：**通过定时器向 Actor 发送消息，并在完成三轮检查后关闭系统。**
