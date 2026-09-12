# 04 · Demo：多生产者并发发布

### 1. 本节目标

前面的 Demo 只有 main 线程发布事件，因此使用：

```
ProducerType.SINGLE
```

本节创建两个生产线程，共同向一个 RingBuffer 发布事件：

```
生产线程 A ──┐
             ├── RingBuffer → 消费线程
生产线程 B ──┘
```

每个生产线程发布 5 条事件，消费者总共处理 10 条。

本节使用 **Java 17、Disruptor 3.4.4**，依赖沿用前文。

### 2. 完整 Demo

创建文件 `DisruptorLesson03.java`，运行 `main()`。

```
package com.isep.akka.disruptor;

import com.lmax.disruptor.BlockingWaitStrategy;
import com.lmax.disruptor.RingBuffer;
import com.lmax.disruptor.TimeoutException;
import com.lmax.disruptor.dsl.Disruptor;
import com.lmax.disruptor.dsl.ProducerType;

import java.util.concurrent.ThreadFactory;
import java.util.concurrent.TimeUnit;

public class DisruptorLesson03 {

    public static class NumberEvent {
        private String producer;
        private int value;

        public String getProducer() {
            return producer;
        }

        public int getValue() {
            return value;
        }

        public void set(String producer, int value) {
            this.producer = producer;
            this.value = value;
        }
    }

    public static void main(String[] args) throws InterruptedException {
        ThreadFactory threadFactory =
                task -> new Thread(task, "number-consumer");

        Disruptor<NumberEvent> disruptor = new Disruptor<>(
                NumberEvent::new,
                8,
                threadFactory,
                // 两个线程可能并发发布，必须使用多生产者模式。
                ProducerType.MULTI,
                new BlockingWaitStrategy()
        );

        disruptor.handleEventsWith((event, sequence, endOfBatch) -> {
            System.out.println(
                    "[消费] sequence=" + sequence
                            + ", producer=" + event.getProducer()
                            + ", value=" + event.getValue()
            );
        });

        RingBuffer<NumberEvent> ringBuffer = disruptor.start();

        Thread producerA = new Thread(
                () -> publishFive(ringBuffer, "A"),
                "producer-a"
        );

        Thread producerB = new Thread(
                () -> publishFive(ringBuffer, "B"),
                "producer-b"
        );

        // 先启动两个线程，让它们有机会并发发布。
        producerA.start();
        producerB.start();

        // 等两个生产线程结束，之后不再发布事件。
        producerA.join();
        producerB.join();

        try {
            // 生产结束不代表消费结束，继续等待消费者处理完。
            disruptor.shutdown(5, TimeUnit.SECONDS);
        } catch (TimeoutException e) {
            disruptor.halt();
            System.err.println("[关闭超时] 可能存在未处理事件");
        }
    }

    private static void publishFive(
            RingBuffer<NumberEvent> ringBuffer,
            String producer
    ) {
        for (int value = 1; value <= 5; value++) {
            // MULTI 模式协调多个线程的序号申请。
            long sequence = ringBuffer.next();

            try {
                // 每次取得自己申请到的槽位，写入本条事件的全部字段。
                NumberEvent event = ringBuffer.get(sequence);
                event.set(producer, value);
            } finally {
                ringBuffer.publish(sequence);
            }
        }
    }
}
```

本例聚焦正常执行流程。`join()` 如果被外部中断，会抛出异常；实际应用还需要统一管理生产线程的中断、停止和资源清理。

### 3. 为什么必须使用 MULTI

本例有两个线程调用：

```
ringBuffer.next();
ringBuffer.publish(sequence);
```

它们可能同时申请序号，因此需要：

```
ProducerType.MULTI
```

多生产者模式会协调序号分配，避免并发生产者获得冲突的写入位置。

选择依据是**可能同时发布的线程数量**：

| 场景              | 模式       |
| --------------- | -------- |
| 只有 main 线程发布    | `SINGLE` |
| 两个线程并发发布        | `MULTI`  |
| 多个请求线程调用同一个发布方法 | `MULTI`  |

即使只有一个 Service 对象，只要调用它发布事件的线程可能有多个，就不能因此使用 `SINGLE`。

### 4. 为什么先 start 两次，再 join 两次

本例写法：

```
producerA.start();
producerB.start();

producerA.join();
producerB.join();
```

执行含义：

```
启动 A
    ↓
启动 B
    ↓
main 等待 A 结束，此时 B 也可以运行
    ↓
main 等待 B 结束
```

如果改成：

```
producerA.start();
producerA.join();

producerB.start();
producerB.join();
```

就会变成：

```
A 全部发布完 → 才启动 B
```

无法演示两个生产者并发发布。

即使两个线程先后启动，也不保证事件一定交替出现。线程调度可能让某个生产者先发布多条，甚至全部五条。

### 5. 两个生产者如何共享 RingBuffer

两个线程调用同一个方法：

```
publishFive(ringBuffer, "A");
publishFive(ringBuffer, "B");
```

它们共享 RingBuffer，但每次写入前都申请自己的序号：

```
long sequence = ringBuffer.next();
```

例如，某次运行可能分配为：

| sequence | 生产者 | value |
| -------- | --- | ----- |
| 0        | A   | 1     |
| 1        | B   | 1     |
| 2        | B   | 2     |
| 3        | A   | 2     |

各生产者写入自己申请到的位置，不能绕过申请机制随意修改其他槽位。

### 6. MULTI 会保护事件中的所有对象吗

不会。

`MULTI` 负责协调并发发布，不会让事件引用的任意共享对象都变成线程安全。

本例每条事件只写入：

```
String producer;
int value;
```

如果两个生产线程还共同修改一个外部 `HashMap`，仍然需要单独考虑并发安全。

发布后也不能继续修改该槽位对象：

```
申请 → 填充 → 发布 → 交给消费者处理
```

生产者不应发布完事件后，继续持有并修改它。

### 7. 为什么每次要写入全部字段

```
event.set(producer, value);
```

RingBuffer 中的对象会复用。

如果某次只更新 `value`，忘记更新 `producer`，可能保留该槽位上一次使用时的生产者名称。

例如：

```
上一次：producer=A，value=1
这一次：只修改 value=5
结果：producer 仍然是 A
```

因此，事件的每次填充都应该明确设置本次需要的字段，必要时清理旧引用。

### 8. 多生产者的消费顺序是什么

本例只有一个标准 `EventHandler`，它按连续发布的序号处理事件：

```
sequence=0 → 1 → 2 → 3……
```

但哪个生产者获得哪个序号，不固定。

可能看到：

```
A1 → B1 → A2 → B2
```

也可能看到：

```
A1 → A2 → A3 → B1
```

本例每个生产线程内部按循环依次发布，因此只看 A 自己的事件，仍然是：

```
A1 → A2 → A3 → A4 → A5
```

B 也是如此。A、B 之间的交错顺序由运行时竞争和调度决定。

### 9. 后面的序号先发布，会先消费吗

假设：

```
A 申请 sequence=0，暂时没有发布
B 申请 sequence=1，已经发布
```

本例消费者不会跳过 0，直接处理 1。

```
sequence=0：未发布 → 等待
sequence=1：已发布 → 暂不能越过前面的空缺
```

等 A 发布 0 后，消费者才能依次处理：

```
0 → 1
```

这也是为什么申请序号后不能遗漏发布，以及为什么应尽量缩短“申请到发布”之间的时间。

复杂计算、网络调用等工作，尽量在申请之前完成。

### 10. join 和 shutdown 分别等待什么

```
producerA.join();
producerB.join();
```

等待两个生产线程结束。

此时可以确定本例不会再发布事件，但消费者可能仍在处理。

```
disruptor.shutdown(5, TimeUnit.SECONDS);
```

等待已发布事件的消费进度追上，再停止消费者处理器。

因此顺序是：

```
停止生产 → 等生产线程结束 → 等消费处理完 → 关闭
```

不要把“生产线程结束”理解成“全部业务已经执行完成”。

### 11. 预期输出

一次运行可能类似：

```
[消费] sequence=0, producer=A, value=1
[消费] sequence=1, producer=B, value=1
[消费] sequence=2, producer=A, value=2
[消费] sequence=3, producer=A, value=3
[消费] sequence=4, producer=B, value=2
[消费] sequence=5, producer=A, value=4
[消费] sequence=6, producer=B, value=3
[消费] sequence=7, producer=A, value=5
[消费] sequence=8, producer=B, value=4
[消费] sequence=9, producer=B, value=5
```

正常完成时应观察到：

* 总共 10 条消费记录。
* 序号为 0～9。
* A 和 B 各有 5 条事件。
* 两个生产者的交错顺序可能变化。

以上为预期现象，不是本次运行记录。

### 12. 动手练习

增加第三个生产线程 C：

```
Thread producerC = new Thread(
        () -> publishFive(ringBuffer, "C"),
        "producer-c"
);
```

将三个线程都启动后，再分别 `join()`。

预期消费总数变为 15，生产者模式仍然是：

```
ProducerType.MULTI
```

下一篇学习：**两个消费者是各自处理全部事件，还是共同分担事件？通过广播消费和工作池 Demo 对比。**
