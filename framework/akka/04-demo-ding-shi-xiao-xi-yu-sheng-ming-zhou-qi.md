# 04 · Demo：定时消息与生命周期

### 1. 本节目标

本节创建一个 Monitor Actor，每秒收到一次检查指令，完成三轮检查后关闭系统。

```
启动 Monitor
    ↓
注册定时器
    ↓
定时器发送 Tick 消息
    ↓
Monitor 收到 Tick，执行检查
    ↓
完成三轮，取消定时器并关闭系统
```

本节沿用 **Java 17、Akka Classic 2.6.20**。

### 2. 完整 Demo

创建文件 `Lesson03Timers.java`，运行 `main()`。

```
package com.isep.akka.lessons;

import akka.actor.AbstractActorWithTimers;
import akka.actor.ActorSystem;
import akka.actor.Props;

import java.time.Duration;

public class Lesson03Timers {

    public static void main(String[] args) {
        ActorSystem system = ActorSystem.create("lesson03");

        system.actorOf(
                Props.create(Monitor.class),
                "monitor"
        );

        // 只阻塞 main，等待系统关闭。
        system.getWhenTerminated().toCompletableFuture().join();
    }

    // 在 AbstractActor 的基础上，提供与 Actor 生命周期绑定的定时器。
    public static class Monitor extends AbstractActorWithTimers {

        // 不带参数的检查指令。
        private enum Tick { INSTANCE }

        // 定时器的标识，用于取消或替换定时器。
        private static final String TIMER_KEY = "monitor-timer";

        // 当前 Actor 已完成的检查轮数，初始为 0。
        private int rounds;

        @Override
        public void preStart() {
            System.out.println("[启动] 每秒发送一次 Tick");

            // 参数依次是：定时器标识、消息、发送间隔。
            // 消息会自动发送给当前 Monitor。
            // 这个重载首次也会等待约一秒。
            getTimers().startTimerWithFixedDelay(
                    TIMER_KEY,
                    Tick.INSTANCE,
                    Duration.ofSeconds(1)
            );
        }

        @Override
        public Receive createReceive() {
            return receiveBuilder()
                    .matchEquals(Tick.INSTANCE, ignored -> {
                        // Tick 经过邮箱调度，在这里执行实际检查。
                        // 本例仅打印日志，没有连接外部服务。
                        System.out.println(
                                "[第 " + ++rounds + " 轮] 模拟检查状态：RUNNING"
                        );

                        if (rounds == 3) {
                            // 取消定时器，不等于停止 Actor。
                            getTimers().cancel(TIMER_KEY);

                            // 发起整个 ActorSystem 的关闭。
                            getContext().getSystem().terminate();
                        }
                    })
                    .build();
        }

        @Override
        public void postStop() {
            System.out.println("[停止] Monitor 已结束");
        }
    }
}
```

### 3. AbstractActorWithTimers 是什么

前面的 Actor 继承：

```
AbstractActor
```

本节继承：

```
AbstractActorWithTimers
```

它在普通 Actor 的基础上提供 `getTimers()`，用于创建和管理属于当前 Actor 的定时器。

```
getTimers().startTimerWithFixedDelay(...);
getTimers().cancel(...);
```

这类定时器与 Actor 的生命周期绑定：Actor 停止或重启时，定时器会自动取消。

### 4. Tick 和 TIMER\_KEY 有什么区别

```
private enum Tick { INSTANCE }

private static final String TIMER_KEY = "monitor-timer";
```

这两个值用途不同：

| 内容              | 作用                      |
| --------------- | ----------------------- |
| `Tick.INSTANCE` | 发给 Actor 的消息，表示“执行一轮检查” |
| `TIMER_KEY`     | 定时器的标识，用于查找、取消或替换定时器    |

可以这样理解：

```
TIMER_KEY：管理哪个定时器
Tick：定时器每次发送什么消息
```

取消时使用 key：

```
getTimers().cancel(TIMER_KEY);
```

接收时匹配消息：

```
.matchEquals(Tick.INSTANCE, ignored -> {
    // 执行检查。
})
```

key 不需要在不同 Actor 之间全局唯一。两个 Monitor 使用相同的 key，不会互相取消对方的定时器。

### 5. 如何启动定时器

```
getTimers().startTimerWithFixedDelay(
        TIMER_KEY,
        Tick.INSTANCE,
        Duration.ofSeconds(1)
);
```

三个参数分别表示：

| 参数      | 本例值                     | 含义      |
| ------- | ----------------------- | ------- |
| key     | `TIMER_KEY`             | 定时器标识   |
| message | `Tick.INSTANCE`         | 定时发送的消息 |
| delay   | `Duration.ofSeconds(1)` | 固定延迟间隔  |

消息接收者自动是当前 Actor，不需要再传入 ActorRef。

这个重载首次发送前，也会等待约一秒。定时调度不是精确实时保证，系统负载和线程调度可能造成延迟。

#### 为什么在 preStart() 中启动

`preStart()` 用于 Actor 启动时的初始化。

本例在其中注册定时器，让 Monitor 启动后开始接收定时消息：

```
创建 Monitor → preStart() → 注册定时器
```

在默认重启生命周期下，新实例也会调用 `preStart()`，重新建立定时器。

### 6. 定时器如何触发业务

定时器不会直接调用检查方法。

实际过程为：

```
定时调度
    ↓
发送 Tick
    ↓
Monitor 的邮箱
    ↓
Akka 调度 Monitor
    ↓
匹配 Tick，执行检查逻辑
```

检查发生在这里：

```
.matchEquals(Tick.INSTANCE, ignored -> {
    System.out.println(
            "[第 " + ++rounds + " 轮] 模拟检查状态：RUNNING"
    );
})
```

因此，Tick 和其他普通消息一样，都需要等待当前 Actor 有机会处理。

同一个 Monitor 不会同时执行两个普通消息处理函数。

### 7. 每秒发送，是检查完成后再等一秒吗

**不是。**

这里的 fixed delay 针对定时发送动作，不是针对 Actor 的业务处理完成时间。

假设处理一个 Tick 需要三秒：

```
约第 1 秒：发送 Tick 1，Actor 开始处理
约第 2 秒：发送 Tick 2，进入邮箱等待
约第 3 秒：发送 Tick 3，进入邮箱等待
约第 4 秒：Tick 1 处理结束，Actor 才能处理下一条
```

后续 Tick 可能积压，不会因为同一个 Actor 串行处理就自动停止发送。

如果需求是：

```
完成本轮检查 → 等待一秒 → 开始下一轮
```

可以考虑在完成检查后，使用单次定时器安排下一条消息：

```
getTimers().startSingleTimer(
        TIMER_KEY,
        Tick.INSTANCE,
        Duration.ofSeconds(1)
);
```

如果检查是异步操作，则应在 Actor 收到业务完成消息后，再安排下一轮。

### 8. 为什么 rounds 不需要原子类型

```
private int rounds;
```

只有当前 Monitor 的消息处理逻辑访问这个字段。

即使 Tick 不断到达，Monitor 仍然一次处理一条消息：

```
处理 Tick 1：rounds = 1
处理 Tick 2：rounds = 2
处理 Tick 3：rounds = 3
```

因此这里使用普通 `int` 即可。

但不要在外部异步回调中直接修改 `rounds`，那样会绕过 Actor 的串行消息处理。

### 9. 取消定时器和停止 Actor 的区别

代码中有两个动作：

```
getTimers().cancel(TIMER_KEY);

getContext().getSystem().terminate();
```

它们的含义不同：

| 操作                                     | 作用                 |
| -------------------------------------- | ------------------ |
| `getTimers().cancel(TIMER_KEY)`        | 取消指定定时器            |
| `getContext().stop(getSelf())`         | 请求停止当前 Actor       |
| `getContext().getSystem().terminate()` | 请求关闭整个 ActorSystem |

只取消定时器，Actor 仍然存在，可以继续接收其他消息。

本例希望程序演示结束，所以同时关闭 ActorSystem。

对于 Actor 自带 Timer，取消后，该定时器已经入队但尚未交给业务处理的旧定时消息也会被过滤。不过取消不会中断当前正在执行的处理函数。

### 10. postStop() 什么时候执行

```
@Override
public void postStop() {
    System.out.println("[停止] Monitor 已结束");
}
```

Actor 停止时会调用 `postStop()`，通常用于清理 Actor 自己持有的资源。

本例没有外部资源需要释放，只打印一条日志。

需要注意：默认重启流程清理旧实例时，也会调用 `postStop()`。因此看到这个方法执行，不一定意味着 Actor 永久终止。

Actor 自带 Timer 会随生命周期自动清理，不依赖我们在 `postStop()` 中手动取消。

### 11. 重启后会不会留下多个定时器

使用本例的 `AbstractActorWithTimers` 时，旧实例的定时器会在重启时自动取消。默认重启流程中新实例执行 `preStart()`，重新注册定时器。

```
旧实例的定时器被取消
    ↓
创建新 Actor 实例
    ↓
preStart() 注册新定时器
```

此外，在同一个 Actor 内，使用相同 key 启动新定时器，会替换旧定时器。

另一种常见写法是：

```
ActorSystem.scheduler() + Cancellable
```

直接使用系统 scheduler 创建的任务，需要自行管理取消动作，通常在 `postStop()` 中调用 `cancel()`。否则 Actor 重启后，旧调度任务可能继续发送消息。

### 12. 整体执行流程

```
main 创建 ActorSystem
    ↓
创建 Monitor
    ↓
Monitor.preStart()
    └── 注册定时器
    ↓
收到 Tick 1
    └── rounds = 1，打印检查日志
    ↓
收到 Tick 2
    └── rounds = 2，打印检查日志
    ↓
收到 Tick 3
    ├── rounds = 3，打印检查日志
    ├── 取消定时器
    └── 发起系统关闭
    ↓
Monitor.postStop()
    ↓
ActorSystem 关闭完成
    ↓
main 中的 join() 返回
```

### 13. 预期输出

```
[启动] 每秒发送一次 Tick
[第 1 轮] 模拟检查状态：RUNNING
[第 2 轮] 模拟检查状态：RUNNING
[第 3 轮] 模拟检查状态：RUNNING
[停止] Monitor 已结束
```

以上是预期现象，不是本次运行记录。

### 14. 什么时候使用 Actor 定时器

如果只是定时执行一个独立方法，`@Scheduled` 通常更直接。

当定时检查还需要与其他消息共同管理状态时，Actor 定时器比较合适。例如：

```
Monitor
├── 收到 Tick：检查状态
├── 收到 Pause：暂停检查
├── 收到 Resume：恢复检查
└── 收到 Query：回复当前检查结果
```

这些消息由同一个 Actor 串行处理，使状态变化集中在同一个地方。

### 15. 动手练习

将停止条件改为五轮：

```
if (rounds == 5) {
    getTimers().cancel(TIMER_KEY);
    getContext().getSystem().terminate();
}
```

再将间隔改为两秒：

```
Duration.ofSeconds(2)
```

观察五轮检查完成后，定时器取消、Actor 停止、main 结束的过程。

下一篇学习：**Actor 抛出异常后，父 Actor 如何决定重启，以及重启与停止有什么区别。**
