# 05 · Demo：广播消费与工作池

### 1. 本节目标

配置两个消费者，并不一定意味着每条事件只由其中一个处理。

本节对比两种模式：

| 模式    | 6 条事件、2 个消费者的处理情况    |
| ----- | -------------------- |
| 广播消费  | A、B 各处理全部 6 条，共 12 次 |
| 工作池消费 | A、B 分担 6 条，共 6 次     |

本节使用 **Java 17、Disruptor 3.4.4**。

> 工作池示例使用 3.4.4 的 `WorkHandler` 和 `handleEventsWithWorkerPool()`。Disruptor 4.x 已移除这套工作池 API，不能直接照搬。

### 2. 两种模式的区别

#### 广播消费

```
              ┌── 消费者 A：1、2、3、4、5、6
RingBuffer ───┤
              └── 消费者 B：1、2、3、4、5、6
```

适合不同消费者执行不同职责，例如：

```
一条业务事件
    ├── 更新统计
    └── 记录审计
```

#### 工作池消费

```
              ┌── Worker A：分到部分事件
RingBuffer ───┤
              └── Worker B：分到其余事件
```

适合多个 worker 执行相同职责，共同分担任务。

分配不一定均匀，也不保证轮流处理。

### 3. 完整 Demo

创建文件 `DisruptorLesson04.java`，运行 `main()`。

程序先演示广播，再演示工作池。每种模式都使用独立的 Disruptor，分别发布 6 条事件。

```
package com.isep.akka.disruptor;

import com.lmax.disruptor.BlockingWaitStrategy;
import com.lmax.disruptor.EventHandler;
import com.lmax.disruptor.RingBuffer;
import com.lmax.disruptor.TimeoutException;
import com.lmax.disruptor.WorkHandler;
import com.lmax.disruptor.dsl.Disruptor;
import com.lmax.disruptor.dsl.ProducerType;

import java.util.concurrent.ThreadFactory;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;

public class DisruptorLesson04 {

    public static class NumberEvent {
        private int value;

        public int getValue() {
            return value;
        }

        public void setValue(int value) {
            this.value = value;
        }
    }

    public static void main(String[] args) {
        broadcastDemo();
        workerPoolDemo();
    }

    private static void broadcastDemo() {
        System.out.println("=== 广播消费 ===");

        Disruptor<NumberEvent> disruptor = createDisruptor("broadcast");

        EventHandler<NumberEvent> handlerA =
                (event, sequence, endOfBatch) -> {
                    System.out.println(
                            "[广播 A] value=" + event.getValue()
                    );
                };

        EventHandler<NumberEvent> handlerB =
                (event, sequence, endOfBatch) -> {
                    System.out.println(
                            "[广播 B] value=" + event.getValue()
                    );
                };

        // 两个消费者各自处理全部事件。
        disruptor.handleEventsWith(handlerA, handlerB);

        RingBuffer<NumberEvent> ringBuffer = disruptor.start();

        try {
            publishSix(ringBuffer);
        } finally {
            shutdown(disruptor);
        }
    }

    private static void workerPoolDemo() {
        System.out.println("=== 工作池消费 ===");

        Disruptor<NumberEvent> disruptor = createDisruptor("worker");

        WorkHandler<NumberEvent> workerA = event -> {
            System.out.println(
                    "[工作池 A] value=" + event.getValue()
            );
        };

        WorkHandler<NumberEvent> workerB = event -> {
            System.out.println(
                    "[工作池 B] value=" + event.getValue()
            );
        };

        // 同一个工作池内，每条事件分配给其中一个 worker。
        disruptor.handleEventsWithWorkerPool(workerA, workerB);

        RingBuffer<NumberEvent> ringBuffer = disruptor.start();

        try {
            publishSix(ringBuffer);
        } finally {
            shutdown(disruptor);
        }
    }

    private static Disruptor<NumberEvent> createDisruptor(String prefix) {
        // 仅用于生成不同的消费线程名称。
        AtomicInteger threadNumber = new AtomicInteger();

        ThreadFactory threadFactory = task -> new Thread(
                task,
                prefix + "-" + threadNumber.incrementAndGet()
        );

        return new Disruptor<>(
                NumberEvent::new,
                8,
                threadFactory,
                // 两种模式都只有 main 线程发布事件。
                ProducerType.SINGLE,
                new BlockingWaitStrategy()
        );
    }

    private static void publishSix(RingBuffer<NumberEvent> ringBuffer) {
        for (int value = 1; value <= 6; value++) {
            long sequence = ringBuffer.next();

            try {
                ringBuffer.get(sequence).setValue(value);
            } finally {
                ringBuffer.publish(sequence);
            }
        }
    }

    private static void shutdown(Disruptor<NumberEvent> disruptor) {
        try {
            disruptor.shutdown(5, TimeUnit.SECONDS);
        } catch (TimeoutException e) {
            disruptor.halt();
            throw new IllegalStateException(
                    "关闭超时，可能存在未处理事件",
                    e
            );
        }
    }
}
```

### 4. 广播模式如何配置

```
disruptor.handleEventsWith(handlerA, handlerB);
```

这里使用的是：

```
EventHandler<NumberEvent>
```

A 和 B 各自有自己的消费进度，都会处理全部事件。

发布：

```
1、2、3、4、5、6
```

则：

```
A：处理 6 条
B：处理 6 条
```

“广播”描述的是处理关系，不表示 Disruptor 为每个消费者复制一份事件对象。

### 5. 广播消费者拿到的是同一个对象吗

对于同一个序号，A 和 B 读取的是同一个槽位中的事件对象。

```
槽位中的 NumberEvent
    ├── Handler A 读取
    └── Handler B 读取
```

本例只是读取 `value` 并打印，没有并发修改。

如果 A 修改某个字段，B 同时读取它，而两者没有依赖关系，就不能假设 B 一定看到 A 修改后的结果。

例如：

```
A：计算 result
B：打印 result
```

这种需求应配置明确的先后依赖，下一篇会介绍：

```
disruptor.handleEventsWith(calculate).then(output);
```

### 6. 广播模式有顺序保证吗

每个标准 `EventHandler` 对应的处理器，按序处理自己的事件。

因此只看 A 的日志：

```
1 → 2 → 3 → 4 → 5 → 6
```

只看 B 的日志也是如此。

但 A 和 B 之间没有先后依赖：

```
A 处理事件 1
B 处理事件 1
```

谁先发生，不固定。

A 甚至可能已经处理完多条，而 B 才开始处理第一条。

### 7. 工作池模式如何配置

```
disruptor.handleEventsWithWorkerPool(workerA, workerB);
```

这里使用的是：

```
WorkHandler<NumberEvent>
```

同一个工作池中的 worker 协调领取任务，一条事件分配给其中一个 worker。

可能出现：

```
A：1、3、5
B：2、4、6
```

也可能出现：

```
A：1、2、3、4
B：5、6
```

甚至某个 worker 处理大部分或全部事件，也不能据此判断配置错误。

**工作池保证任务分配方式，不保证均匀分配或交替执行。**

### 8. EventHandler 和 WorkHandler 的区别

| 对比项          | EventHandler              | WorkHandler                    |
| ------------ | ------------------------- | ------------------------------ |
| 本例配置方式       | `handleEventsWith()`      | `handleEventsWithWorkerPool()` |
| 同一组中每条事件由谁处理 | 每个 handler 都处理            | 其中一个 worker 处理                 |
| 回调参数         | event、sequence、endOfBatch | event                          |
| 典型用途         | 不同职责各处理一遍                 | 相同职责共同分担                       |

工作池中的“一条事件由一个 worker 处理”，不等于业务必然成功一次。

异常、进程退出和外部副作用仍需要单独处理，框架不会因此提供端到端的 exactly-once 业务保证。

### 9. 工作池能保证完成顺序吗

不能。

假设：

```
Worker A 领取事件 1，处理需要 500ms
Worker B 领取事件 2，处理需要 10ms
```

那么事件 2 可能先完成。

```
领取顺序：1 → 2
完成顺序：2 → 1
```

因此，有严格业务顺序要求的事件，不能仅依赖工作池的序号分配。

例如，同一个账户的余额变更需要按顺序处理时，应进一步考虑按账户分片，让同一账户进入同一条串行处理路径。

### 10. 为什么仍然使用 SINGLE

两个 Demo 都由 main 线程发布：

```
publishSix(ringBuffer);
```

因此配置：

```
ProducerType.SINGLE
```

消费者有两个，不影响生产者模式选择。

```
ProducerType：看发布线程
消费配置：看事件如何分配给消费者
```

这两个维度是独立的。

### 11. 慢消费者会有什么影响

#### 广播模式

A 和 B 都需要处理每条事件。

如果 A 很快、B 很慢，RingBuffer 仍然需要保留 B 尚未处理完的数据。缓冲区填满后，生产者可能等待。

#### 工作池模式

较快的 worker 可以继续领取后续任务，但较慢 worker 持有的事件仍不能被提前覆盖。

因此工作池也不意味着生产者永远不会受慢任务影响。

### 12. 预期输出

广播部分，每个数字出现两次：

```
[广播 A] value=1
[广播 B] value=1
……
[广播 A] value=6
[广播 B] value=6
```

共 12 条处理日志，A、B 之间的交错顺序可能不同。

工作池部分，每个数字出现一次：

```
[工作池 A] value=1
[工作池 B] value=2
[工作池 A] value=3
……
```

共 6 条处理日志，分配结果和打印顺序不固定。

以上为正常完成时的预期现象，不是本次运行记录。

### 13. 动手练习

在工作池 A 的处理逻辑中增加：

```
Thread.sleep(300);
```

观察 B 是否处理了更多事件，以及日志是否仍按数字递增。

再在广播 A 中增加同样的等待。正常完成时，即使 A 更慢，它仍然需要处理全部 6 条事件。

下一篇学习：**使用 `handleEventsWith(calculate).then(output)`，让输出消费者等待计算结果。**
