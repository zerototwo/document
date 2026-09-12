# 08 · Demo：按账户分片

### 1. 本节目标

工作池可以让多个消费者分担事件，但不同事件的完成顺序可能变化。

如果希望：

```
同一账户的事件 → 在同一个消费者中串行处理
不同账户的事件 → 有机会并行处理
```

可以按账户 ID 分片，为每个分片创建一个独立的 Disruptor。

本节使用 **Java 17、Disruptor 3.4.4**，依赖沿用前文。

### 2. 什么是分片

本例创建两个分片：

```
                    ┌── 分片 0：RingBuffer → 消费者 0
生产者 → 按账户路由 ─┤
                    └── 分片 1：RingBuffer → 消费者 1
```

通过账户 ID 计算分片编号：

```
Math.floorMod(accountId, shardCount)
```

当分片数为 2 时：

| accountId | 分片编号 |
| --------- | ---- |
| 1001      | 1    |
| 1002      | 0    |
| 1003      | 1    |
| 1004      | 0    |

同一个账户始终进入同一个分片。

但不同账户可能进入同一分片，因此不保证每个账户都有独立消费线程。

### 3. 完整 Demo

创建文件 `DisruptorLesson07.java`，运行 `main()`。

```
package com.isep.akka.disruptor;

import com.lmax.disruptor.BlockingWaitStrategy;
import com.lmax.disruptor.RingBuffer;
import com.lmax.disruptor.TimeoutException;
import com.lmax.disruptor.dsl.Disruptor;
import com.lmax.disruptor.dsl.ProducerType;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ThreadFactory;
import java.util.concurrent.TimeUnit;

public class DisruptorLesson07 {

    public static class AccountEvent {
        private long accountId;
        private String type;

        public void set(long accountId, String type) {
            this.accountId = accountId;
            this.type = type;
        }
    }

    public static void main(String[] args) {
        List<Disruptor<AccountEvent>> shards = new ArrayList<>();

        try {
            // 每个分片有独立的 RingBuffer 和消费者。
            shards.add(createShard(0));
            shards.add(createShard(1));

            // main 是唯一生产线程，按代码顺序发布。
            publish(shards, 1001L, "余额更新");
            publish(shards, 1002L, "余额更新");
            publish(shards, 1001L, "持仓更新");
            publish(shards, 1002L, "持仓更新");
        } finally {
            // 本例已停止生产，依次等待每个分片处理完。
            for (Disruptor<AccountEvent> shard : shards) {
                try {
                    shard.shutdown(5, TimeUnit.SECONDS);
                } catch (TimeoutException e) {
                    shard.halt();
                    System.err.println("[关闭超时] 某分片可能存在未处理事件");
                }
            }
        }
    }

    private static Disruptor<AccountEvent> createShard(int shardId) {
        ThreadFactory threadFactory =
                task -> new Thread(task, "account-shard-" + shardId);

        Disruptor<AccountEvent> disruptor = new Disruptor<>(
                AccountEvent::new,
                8,
                threadFactory,
                // 本例只有 main 发布。
                ProducerType.SINGLE,
                new BlockingWaitStrategy()
        );

        disruptor.handleEventsWith((event, sequence, endOfBatch) -> {
            System.out.println(
                    "[分片 " + shardId + "]"
                            + " accountId=" + event.accountId
                            + ", type=" + event.type
                            + ", sequence=" + sequence
                            + ", thread=" + Thread.currentThread().getName()
            );
        });

        disruptor.start();
        return disruptor;
    }

    private static void publish(
            List<Disruptor<AccountEvent>> shards,
            long accountId,
            String type
    ) {
        // 同一个 accountId，在分片数量不变时路由结果固定。
        int shardId = Math.floorMod(accountId, shards.size());

        RingBuffer<AccountEvent> ringBuffer =
                shards.get(shardId).getRingBuffer();

        long sequence = ringBuffer.next();

        try {
            // 每次写入完整字段，避免复用槽位时残留旧数据。
            ringBuffer.get(sequence).set(accountId, type);
        } finally {
            ringBuffer.publish(sequence);
        }
    }
}
```

本例的“余额更新”和“持仓更新”只是事件名称，用来观察路由和处理顺序，没有实际进行资金或持仓计算。

### 4. 每个分片到底是什么

分片不是同一个 RingBuffer 里的几个槽位。

本例创建了两个完整、独立的 Disruptor：

```
分片 0
├── 容量为 8 的 RingBuffer
└── account-shard-0 消费线程

分片 1
├── 容量为 8 的 RingBuffer
└── account-shard-1 消费线程
```

两个 RingBuffer 各自维护自己的序号和消费进度。

因此日志中可能同时出现：

```
分片 0：sequence=0
分片 1：sequence=0
```

它们是不同 RingBuffer 的序号，不冲突，也不能用来比较跨分片的全局顺序。

### 5. 如何选择分片

```
int shardId = Math.floorMod(accountId, shards.size());
```

本例：

```
1001 → floorMod(1001, 2) → 1
1002 → floorMod(1002, 2) → 0
```

选择对应 RingBuffer：

```
shards.get(shardId).getRingBuffer();
```

之后的发布操作与前面的 Demo 相同：

```
next → get → 填充 → publish
```

分片数量为正数时，`floorMod()` 能得到合法的非负下标；直接使用 `%` 时，负数输入可能得到负下标。

### 6. 为什么同一账户可以串行处理

本例同一账户总是进入相同分片，而每个分片只有一个标准消费者。

例如账户 1001：

```
余额更新 → 分片 1
持仓更新 → 分片 1
```

main 按顺序发布，因此分片 1 依次处理：

```
1001 余额更新
    ↓
1001 持仓更新
```

成立条件是：

* 分片数量和路由规则保持不变。
* 同一账户始终使用同一个路由键。
* 每个分片采用单个串行处理阶段。
* 业务操作在回调内完成，或另外管理异步完成顺序。

分片不会让外部异步任务自动按序完成。

### 7. 不同账户一定并行吗

不一定。

账户 1001 和 1002 分别进入不同分片，可以并行处理：

```
分片 1：1001 余额更新 → 1001 持仓更新
分片 0：1002 余额更新 → 1002 持仓更新
```

但 1001 和 1003 都进入分片 1：

```
分片 1：同时承载 1001、1003 的事件
```

它们由同一个消费者串行处理。

分片提供的是有限条并行处理路径，不是每个账户创建一个线程。

### 8. 多个生产线程会改变什么

本例只有 main 发布，因此使用：

```
ProducerType.SINGLE
```

如果实际项目由多个请求线程调用 `publish()`，每个可能被并发发布的分片都应使用：

```
ProducerType.MULTI
```

不过，`MULTI` 只协调并发发布，不会自动恢复业务时间顺序。

例如：

```
旧事件在线程 A 中延迟
新事件在线程 B 中先发布
```

即使它们进入同一分片，消费者也可能先处理新事件，再处理旧事件。

严格业务顺序还需要结合上游顺序、事件版本或业务序号判断。

### 9. 这种方式和工作池有什么区别

| 对比项           | 工作池           | 按账户分片         |
| ------------- | ------------- | ------------- |
| 分配依据          | worker 竞争领取事件 | 账户 ID 路由      |
| 同一账户是否固定处理路径  | 不保证           | 路由配置不变时固定     |
| 同一账户是否可能被并发处理 | 可能            | 本例单消费者同步处理时不会 |
| 负载特点          | worker 分担任务   | 可能出现热点分片      |

工作池适合可以独立并行执行的任务。

按键分片适合需要让某类相关事件进入同一条处理路径的场景。

### 10. 某个账户特别忙怎么办

如果一个账户产生大量事件，它所在的分片可能成为热点：

```
分片 0：事件很少
分片 1：大量热点账户事件
```

即使分片 0 空闲，也不会自动替分片 1 处理事件。

增加分片可能减少不同账户之间的竞争，但不能直接解决单个账户本身处理能力不足的问题。

如果同一账户必须严格串行，就需要评估单条处理耗时、事件合并以及上游限流等方式。

另外，本例只有一个生产线程。如果它在热点分片的 `next()` 中等待，也会延迟后续发往其他分片的事件。消费独立不等于整个生产链路完全隔离。

### 11. 可以直接修改分片数量吗

不能忽略路由变化。

例如账户 1001：

```
2 个分片：1001 % 2 = 1
3 个分片：1001 % 3 = 2
```

如果运行过程中直接增加分片，旧事件可能还在分片 1，新事件已经进入分片 2。

这可能造成同一账户跨分片并发处理。若分片还维护账户状态，也会涉及状态迁移。

本例固定两个分片，不实现动态扩容。

### 12. 预期输出

可能看到：

```
[分片 1] accountId=1001, type=余额更新, sequence=0, ...
[分片 0] accountId=1002, type=余额更新, sequence=0, ...
[分片 1] accountId=1001, type=持仓更新, sequence=1, ...
[分片 0] accountId=1002, type=持仓更新, sequence=1, ...
```

不同分片的日志可以交错，也可能一个分片先打印完。

重点观察：

* 1001 始终进入分片 1。
* 1002 始终进入分片 0。
* 本例每个账户先处理余额更新，再处理持仓更新。
* 两个分片的序号分别从 0 开始。

以上为预期现象，不是本次运行记录。

### 13. 动手练习

在关闭之前增加：

```
publish(shards, 1003L, "余额更新");
publish(shards, 1003L, "持仓更新");
```

观察账户 1003 与 1001 是否进入同一分片，并思考：为什么“账户不同”不代表“一定并行”？

下一篇整理：**Disruptor 常见问题与面试知识点。**
