# 05 · Demo：异常监督、重启与停止

### 1. 本节目标

Actor 处理消息时可能抛出异常，例如状态不符合预期，或某项操作执行失败。

Akka 提供监督机制：**子 Actor 处理失败后，由父 Actor 的监督策略决定如何处理。**

本节创建 Parent 和 Worker，演示：

```
Worker 累加，count = 1
    ↓
Worker 抛出异常
    ↓
Parent 决定重启 Worker
    ↓
新 Worker 实例，count = 0
    ↓
Parent 停止 Worker
    ↓
Parent 收到终止通知，关闭系统
```

本节沿用 **Java 17、Akka Classic 2.6.20**。

### 2. 完整 Demo

创建文件 `Lesson04Supervision.java`，运行 `main()`。

```
package com.isep.akka.lessons;

import akka.actor.AbstractActor;
import akka.actor.ActorRef;
import akka.actor.ActorSystem;
import akka.actor.OneForOneStrategy;
import akka.actor.Props;
import akka.actor.SupervisorStrategy;
import akka.actor.Terminated;
import akka.japi.pf.DeciderBuilder;

import java.time.Duration;
import java.util.UUID;

public class Lesson04Supervision {

    // 三种指令：累加、查询、制造故障。
    public enum Command { ADD, GET, FAIL }

    // 返回实例标识和计数，便于观察重启前后的变化。
    public record State(String instance, int count) { }

    public static void main(String[] args) {
        ActorSystem system = ActorSystem.create("lesson04");

        system.actorOf(
                Props.create(Parent.class),
                "parent"
        );

        // 只在 main 中等待系统关闭。
        system.getWhenTerminated().toCompletableFuture().join();
    }

    public static class Worker extends AbstractActor {

        // 每次创建 Java 实例都会生成新标识。
        // 这是教学标识，不是 ActorRef。
        private final String instance =
                UUID.randomUUID().toString().substring(0, 8);

        // 普通实例字段，新实例初始为 0。
        private int count;

        @Override
        public void preStart() {
            System.out.println(
                    "[Worker 启动] instance=" + instance
                            + ", path=" + getSelf().path()
            );
        }

        @Override
        public Receive createReceive() {
            return receiveBuilder()
                    .matchEquals(Command.ADD, ignored -> {
                        count++;
                    })
                    .matchEquals(Command.GET, ignored -> {
                        // 当前 GET 来自 Parent，向它回复状态。
                        getSender().tell(
                                new State(instance, count),
                                getSelf()
                        );
                    })
                    .matchEquals(Command.FAIL, ignored -> {
                        // 故意让异常离开消息处理函数，
                        // 交给 Akka 的监督机制处理。
                        throw new IllegalStateException("教学故障");
                    })
                    .build();
        }

        @Override
        public void postStop() {
            // 默认重启流程清理旧实例时也会调用此方法。
            System.out.println(
                    "[Worker 清理] instance=" + instance
            );
        }
    }

    public static class Parent extends AbstractActor {

        // Worker 普通重启后，这个引用仍然有效。
        private ActorRef worker;

        // Parent 自己的流程状态，不受 Worker 重启影响。
        private boolean failureSent;

        @Override
        public void preStart() {
            worker = getContext().actorOf(
                    Props.create(Worker.class),
                    "worker"
            );

            // 订阅 Worker 真正终止时的通知。
            // watch 不是开启异常监督，监督来自父子关系。
            getContext().watch(worker);

            // 先累加，再查询，预期第一次回复 count=1。
            worker.tell(Command.ADD, getSelf());
            worker.tell(Command.GET, getSelf());
        }

        @Override
        public SupervisorStrategy supervisorStrategy() {
            return new OneForOneStrategy(
                    // 一分钟窗口内最多允许三次重启。
                    3,
                    Duration.ofMinutes(1),
                    DeciderBuilder
                            .match(
                                    IllegalStateException.class,
                                    error -> SupervisorStrategy.restart()
                            )
                            .matchAny(
                                    error -> SupervisorStrategy.escalate()
                            )
                            .build()
            );
        }

        @Override
        public Receive createReceive() {
            return receiveBuilder()
                    .match(State.class, state -> {
                        System.out.println(
                                "[Parent 收到状态] instance=" + state.instance()
                                        + ", count=" + state.count()
                        );

                        if (!failureSent) {
                            // 第一次回复后，进入故障演示阶段。
                            failureSent = true;

                            worker.tell(Command.FAIL, getSelf());

                            // FAIL 后面的 GET 等待 Worker 恢复后处理。
                            worker.tell(Command.GET, getSelf());
                        } else {
                            // 第二次回复来自重启后的实例。
                            // 使用原 ActorRef 请求停止 Worker。
                            System.out.println("[Parent] 主动停止 Worker");
                            getContext().stop(worker);
                        }
                    })
                    .match(Terminated.class, stopped -> {
                        System.out.println(
                                "[Parent 收到终止通知] "
                                        + stopped.actor().path()
                        );

                        getContext().getSystem().terminate();
                    })
                    .build();
        }
    }
}
```

### 3. Parent 为什么能监督 Worker

Worker 由 Parent 创建：

```
worker = getContext().actorOf(
        Props.create(Worker.class),
        "worker"
);
```

它们形成父子关系：

```
Parent
└── Worker
```

Parent 可以通过重写 `supervisorStrategy()`，声明对子 Actor 的故障处理策略。

```
@Override
public SupervisorStrategy supervisorStrategy() {
    // 返回对子 Actor 的监督策略。
}
```

这里的策略处理的是子 Actor 的失败。Parent 自己处理消息时发生失败，则由它的上级监督者决定如何处理。

### 4. 监督策略如何理解

```
return new OneForOneStrategy(
        3,
        Duration.ofMinutes(1),
        DeciderBuilder
                .match(
                        IllegalStateException.class,
                        error -> SupervisorStrategy.restart()
                )
                .matchAny(
                        error -> SupervisorStrategy.escalate()
                )
                .build()
);
```

可以拆成三个部分。

#### OneForOneStrategy

表示对发生故障的那个子 Actor 应用策略。

假设 Parent 有三个子 Actor：

```
Parent
├── Worker A
├── Worker B
└── Worker C
```

Worker A 发生本例匹配的异常并被重启时，B 和 C 不会因此一起重启。

#### 重启次数限制

```
3, Duration.ofMinutes(1)
```

表示该子 Actor 在一分钟窗口内最多允许重启三次。超过限制，会停止该子 Actor。

它不是“同一条消息重试三次”。

#### 根据异常选择处理方式

```
.match(
        IllegalStateException.class,
        error -> SupervisorStrategy.restart()
)
```

遇到 `IllegalStateException`，选择重启。

```
.matchAny(
        error -> SupervisorStrategy.escalate()
)
```

其他未匹配的异常升级给上级监督者处理。

### 5. 四种监督处理方式

| 策略           | 作用                   |
| ------------ | -------------------- |
| `resume()`   | 保留当前实例，继续处理后续消息      |
| `restart()`  | 重建 Actor 实例，继续处理后续消息 |
| `stop()`     | 停止 Actor             |
| `escalate()` | 将故障升级给上级监督者          |

#### resume：继续

保留实例，也保留已有状态。

如果消息处理到一半已经修改了字段，再抛异常，修改可能保留下来。

#### restart：重启

创建新的 Actor 实例，普通实例字段重新初始化。

它不会自动恢复之前的内存状态，也不会回滚数据库等外部副作用。

#### stop：停止

结束 Actor 的生命周期，旧 ActorRef 不能让它重新启动。

#### escalate：升级

让上级监督者决定如何处理故障，最终可能影响更大的 Actor 层级。

### 6. Demo 如何进入故障阶段

Parent 启动时发送：

```
worker.tell(Command.ADD, getSelf());
worker.tell(Command.GET, getSelf());
```

Worker 先处理 ADD：

```
count++;
```

再处理 GET，回复：

```
State(旧实例标识, 1)
```

Parent 收到第一次回复后：

```
failureSent = true;

worker.tell(Command.FAIL, getSelf());
worker.tell(Command.GET, getSelf());
```

`failureSent` 用于区分两次回复：

| 值       | 含义                   |
| ------- | -------------------- |
| `false` | 尚未发送故障指令             |
| `true`  | 已经发送，下一次回复后停止 Worker |

这个字段属于 Parent。Worker 重启不会重置它。

### 7. Worker 抛异常后发生什么

Worker 处理 FAIL：

```
throw new IllegalStateException("教学故障");
```

异常离开消息处理函数后，Akka 暂停该 Actor 的普通消息处理，由父级监督决定如何恢复。

本例中：

```
Worker 处理 FAIL
    ↓
抛出 IllegalStateException
    ↓
Parent 的策略选择 restart
    ↓
清理旧实例
    ↓
创建新实例
    ↓
恢复处理后续消息
```

后面的 GET 来自同一个 Parent，使用默认邮箱，不会抢在 FAIL 前处理。

恢复后，新实例处理 GET，返回：

```
State(新实例标识, 0)
```

### 8. 重启后哪些东西发生变化

| 内容            | 普通 restart 后 |
| ------------- | ------------ |
| ActorRef      | 保持有效         |
| Actor 路径      | 保持不变         |
| Java Actor 实例 | 重新创建         |
| 普通实例字段        | 重新初始化        |
| 导致异常的消息       | 不会自动重新处理     |

本例通过两个字段观察变化：

```
private final String instance =
        UUID.randomUUID().toString().substring(0, 8);

private int count;
```

新实例创建后：

```
instance：重新生成
count：重新初始化为 0
```

但 Parent 保存的引用仍然可以使用：

```
worker.tell(Command.GET, getSelf());
```

不需要重新创建 Worker。

### 9. 重启等于业务重试吗

**不等于。**

本例的 FAIL 消息不会因为 restart 再执行一次。

```
FAIL 失败
    ↓
重启实例
    ↓
处理后面的 GET
```

如果失败消息已经写入数据库，然后在发送结果时抛异常，Actor 重启不会撤销数据库写入。

业务重试需要单独设计，例如识别可重试错误、限制重试次数，以及通过幂等机制避免重复执行。

对于余额不足等预期业务结果，通常直接回复失败消息更合适，不必通过抛异常重启 Actor。

### 10. preStart 和 postStop 的执行顺序

本例没有覆盖默认的重启生命周期。

正常启动：

```
创建实例 → preStart()
```

普通重启：

```
旧实例：preRestart() → postStop()
    ↓
新实例：postRestart() → preStart()
```

最终停止：

```
当前实例 → postStop()
```

因此，看到 `postStop()` 日志不一定表示 Actor 永久终止，也可能是在清理重启前的旧实例。

### 11. watch 和监督有什么区别

```
getContext().watch(worker);
```

这行代码订阅 Worker 的终止通知。

Worker 真正停止后，Parent 收到：

```
Terminated
```

两种机制的区别：

| 机制        | 解决的问题                  |
| --------- | ---------------------- |
| 父子监督      | 子 Actor 失败后如何处理        |
| `watch()` | 被观察的 Actor 真正终止后，通知观察者 |

监督来自父子关系，不是 `watch()` 开启的。

`watch()` 可以观察非子 Actor。普通 restart 不会产生 `Terminated`。

### 12. 为什么最后主动 stop

Parent 收到第二次 State 后，说明重启后的 Worker 已经可以回复消息。

接着执行：

```
getContext().stop(worker);
```

这用于演示真正停止与重启的区别。

`stop()` 发起停止流程，不会触发 restart 策略，也不代表方法返回时清理已经完成。

Parent 等待 `Terminated`：

```
.match(Terminated.class, stopped -> {
    getContext().getSystem().terminate();
})
```

收到通知后再关闭系统，整个 Demo 结束。

### 13. 整体执行流程

```
main 创建 Parent
    ↓
Parent 创建 Worker，并 watch
    ↓
Worker 启动，count = 0
    ↓
Parent 发送 ADD、GET
    ↓
Worker 回复 count = 1
    ↓
Parent 发送 FAIL、GET
    ↓
Worker 处理 FAIL，抛异常
    ↓
Parent 策略选择 restart
    ↓
旧实例清理，新实例启动，count = 0
    ↓
新实例处理 GET，回复 count = 0
    ↓
Parent 主动 stop Worker
    ↓
Worker 清理并终止
    ↓
Parent 收到 Terminated
    ↓
关闭 ActorSystem
```

流程由回复消息推进，不需要依赖 `Thread.sleep()` 猜测重启何时完成。

### 14. 预期现象

关键日志类似：

```
[Worker 启动] instance=旧标识, path=...
[Parent 收到状态] instance=旧标识, count=1

出现教学故障异常日志

[Worker 清理] instance=旧标识
[Worker 启动] instance=新标识, path=...
[Parent 收到状态] instance=新标识, count=0

[Parent] 主动停止 Worker
[Worker 清理] instance=新标识
[Parent 收到终止通知] ...
```

重点观察：

* 两次状态回复中的实例标识不同。
* 计数从 1 变为 0。
* Actor 路径保持不变，原 ActorRef 仍可用。
* 普通重启时没有终止通知，最终停止后才收到通知。

以上为预期现象，不是本次运行记录；异常日志与业务日志的显示顺序可能受日志调度影响。

### 15. 动手练习

将策略中的：

```
error -> SupervisorStrategy.restart()
```

改为：

```
error -> SupervisorStrategy.resume()
```

本例 FAIL 只抛异常，没有修改计数，因此预期：

```
实例标识不变
第二次查询 count = 1
```

再改为：

```
error -> SupervisorStrategy.stop()
```

此时 Worker 会直接终止，Parent 通过 `Terminated` 关闭系统，不会收到第二次 State。

下一篇整理：**Akka 常见问题与面试知识点。**
