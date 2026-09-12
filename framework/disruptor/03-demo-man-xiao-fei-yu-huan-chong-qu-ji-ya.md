# 03 · Demo：慢消费与缓冲区积压



### 1. 本节目标

上一节了解了槽位循环使用。本节通过一个慢消费者，观察：

```
生产者快速发布
    ↓
消费者处理较慢
    ↓
RingBuffer 填满
    ↓
生产者等待
    ↓
消费者推进进度
    ↓
生产者继续发布
```

为了方便观察：

* RingBuffer 容量设为 4。
* 生产者发布 8 条事件。
* 消费者每条事件模拟处理 500 毫秒。
* 记录生产者申请槽位的耗时。

本节使用 **Java 17、Disruptor 3.4.4**，依赖沿用上一节。

### 2. 完整 Demo

创建文件 `DisruptorLesson02.java`，运行 `main()`。

```
package com.isep.akka.disruptor;

import com.lmax.disruptor.BlockingWaitStrategy;
import com.lmax.disruptor.RingBuffer;
import com.lmax.disruptor.TimeoutException;
import com.lmax.disruptor.dsl.Disruptor;
import com.lmax.disruptor.dsl.ProducerType;

import java.util.concurrent.ThreadFactory;
import java.util.concurrent.TimeUnit;

public class DisruptorLesson02 {

    public static class NumberEvent {
        private long value;

        public long getValue() {
            return value;
        }

        public void setValue(long value) {
            this.value = value;
        }
    }

    public static void main(String[] args) {
        int bufferSize = 4;

        ThreadFactory threadFactory =
                task -> new Thread(task, "slow-consumer");

        Disruptor<NumberEvent> disruptor = new Disruptor<>(
                NumberEvent::new,
                bufferSize,
                threadFactory,
                ProducerType.SINGLE,
                new BlockingWaitStrategy()
        );

        disruptor.handleEventsWith((event, sequence, endOfBatch) -> {
            System.out.println(
                    "[消费开始] sequence=" + sequence
                            + ", value=" + event.getValue()
            );

            // 仅用于演示慢消费，不是生产环境的性能优化方式。
            Thread.sleep(500);

            System.out.println(
                    "[消费结束] sequence=" + sequence
                            + ", value=" + event.getValue()
            );
        });

        RingBuffer<NumberEvent> ringBuffer = disruptor.start();

        try {
            for (long value = 1; value <= 8; value++) {
                long start = System.nanoTime();

                // 没有可复用槽位时，生产者可能在这里等待。
                long sequence = ringBuffer.next();

                long waitMillis = TimeUnit.NANOSECONDS.toMillis(
                        System.nanoTime() - start
                );

                try {
                    ringBuffer.get(sequence).setValue(value);
                } finally {
                    ringBuffer.publish(sequence);
                }

                System.out.println(
                        "[发布] value=" + value
                                + ", sequence=" + sequence
                                + ", 申请槽位耗时=" + waitMillis + "ms"
                );
            }
        } finally {
            try {
                // 停止生产后，等待已发布事件处理完成。
                disruptor.shutdown(10, TimeUnit.SECONDS);
            } catch (TimeoutException e) {
                disruptor.halt();
                System.err.println("[关闭超时] 可能存在未处理事件");
            }
        }
    }
}
```

### 3. 慢消费者是怎么模拟的

```
Thread.sleep(500);
```

消费者每处理一条事件，都等待 500 毫秒。

这一行运行在消费线程中，不会直接让 main 线程休眠。

```
main 线程：发布事件
消费线程：处理事件，每条等待 500ms
```

但 main 仍可能因为缓冲区没有容量而等待。这是生产与消费之间的容量约束，不是两个线程在执行同一个 `sleep()`。

### 4. RingBuffer 填满时发生什么

假设生产者先发布了四条事件：

```
槽位 0：value=1
槽位 1：value=2
槽位 2：value=3
槽位 3：value=4
```

生产者准备发布第五条：

```
sequence=4 → 需要再次使用槽位 0
```

如果消费者尚未推进到允许复用槽位 0 的位置，生产者不能覆盖它。

因此会等待：

```
long sequence = ringBuffer.next();
```

待消费进度允许复用后，`next()` 返回，生产者才继续填写并发布第五条事件。

### 5. 等待发生在 next，不是 publish

本例记录的是：

```
long start = System.nanoTime();

long sequence = ringBuffer.next();

long waitMillis = TimeUnit.NANOSECONDS.toMillis(
        System.nanoTime() - start
);
```

这个耗时表示申请位置用了多久，不包含后面的填充、发布和打印时间。

流程为：

```
next()：申请可写位置，容量不足时等待
    ↓
get()：取得事件对象
    ↓
setValue()：填充数据
    ↓
publish()：发布
```

`publish()` 不等待消费者处理完成。

### 6. 预期现象

通常可以观察到：

```
前几次申请槽位很快
    ↓
后续某些 next() 调用明显变慢
    ↓
消费进度推进后，生产者继续发布
```

日志可能类似：

```
[发布] value=1, sequence=0, 申请槽位耗时=0ms
[消费开始] sequence=0, value=1
[发布] value=2, sequence=1, 申请槽位耗时=0ms
[发布] value=3, sequence=2, 申请槽位耗时=0ms
[发布] value=4, sequence=3, 申请槽位耗时=0ms
[消费结束] sequence=0, value=1
...
[发布] value=5, sequence=4, 申请槽位耗时=某个较大的值
```

这只是示意，不是固定输出，也不是本次运行记录。

不要假设第五条一定等待恰好 500 毫秒，或后面每条都等待 500 毫秒。

### 7. 为什么等待时间不是固定的

生产线程和消费线程会并发推进，实际耗时受线程调度、日志输出和批次边界影响。

此外，本例标准 `EventHandler` 对应的批处理器通常在处理完一批可用事件后，更新对外可见的消费进度。

因此：

```
某条 handler 执行结束
```

不一定意味着生产者在同一时刻就能复用对应槽位。

例如，消费者可能连续处理一批事件后，生产者才观察到一段容量被释放，于是接连发布多条。

### 8. BlockingWaitStrategy 决定生产者怎么等吗

不是。

```
new BlockingWaitStrategy()
```

主要用于消费者等待新事件。

本节观察的则是：

```
消费者太慢 → 容量不足 → 生产者在 next() 等待
```

这是两个不同方向的等待：

| 场景       | 谁等待 |
| -------- | --- |
| 没有新事件可处理 | 消费者 |
| 没有可复用的槽位 | 生产者 |

不能把 `BlockingWaitStrategy` 理解成所有等待行为的统一配置。

### 9. 增大容量能解决慢消费吗

把容量从 4 改为 1024，可以容纳更多尚未处理完的事件。

它能吸收更大的短时流量，但不能解决长期处理能力不足：

```
长期生产速度 > 长期消费速度
    ↓
积压持续增加
    ↓
更大的缓冲区最终也会填满
```

本例只发布 8 条。如果容量改为 8，生产者通常可以很快发布完，但仍要等待消费者逐条处理。

发布结束快，不代表业务处理结束快。

### 10. 不想等待，可以怎么做

可以使用 `tryNext()` 尝试申请容量。容量不足时，它会抛出 `InsufficientCapacityException`。

示意代码：

```
try {
    long sequence = ringBuffer.tryNext();

    try {
        ringBuffer.get(sequence).setValue(100);
    } finally {
        ringBuffer.publish(sequence);
    }
} catch (InsufficientCapacityException e) {
    // 根据业务决定拒绝、稍后重试或采用其他处理方式。
}
```

使用时需要导入：

```
import com.lmax.disruptor.InsufficientCapacityException;
```

这只是让调用方及时获知容量不足，并没有增加消费者的处理能力。

订单、资金等事件不能随意丢弃，必须根据业务要求设计容量不足时的处理方式。

### 11. 动手练习

分别修改以下配置并观察：

| 修改                    | 观察重点          |
| --------------------- | ------------- |
| 容量从 4 改为 8            | 8 条事件能否更快发布完  |
| 消费等待从 500ms 改为 1000ms | 生产者等待和整体耗时的变化 |
| 发布数量从 8 改为 16         | 是否出现多次等待      |

增加事件数量或消费耗时时，也应相应调大演示中的关闭等待时间，避免尚未完成消费就超时停止。

下一篇学习：**两个生产线程向同一个 RingBuffer 并发发布事件，以及为什么需要 `ProducerType.MULTI`。**
