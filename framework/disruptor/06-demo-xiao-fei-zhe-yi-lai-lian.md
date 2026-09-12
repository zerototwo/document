# 06 · Demo：消费者依赖链

### 1. 本节目标

上一节的广播模式中，两个消费者可以并行处理：

```
disruptor.handleEventsWith(handlerA, handlerB);
```

但如果 B 需要使用 A 的计算结果，就必须建立依赖关系。

本节实现：

```
生产者发布数字
    ↓
calculate：计算 number × 10
    ↓
output：输出计算结果
```

对应配置：

```
disruptor.handleEventsWith(calculate).then(output);
```

本节使用 **Java 17、Disruptor 3.4.4**，依赖沿用前文。

### 2. 完整 Demo

创建文件 `DisruptorLesson05.java`，运行 `main()`。

```
package com.isep.akka.disruptor;

import com.lmax.disruptor.BlockingWaitStrategy;
import com.lmax.disruptor.EventHandler;
import com.lmax.disruptor.RingBuffer;
import com.lmax.disruptor.TimeoutException;
import com.lmax.disruptor.dsl.Disruptor;
import com.lmax.disruptor.dsl.ProducerType;

import java.util.concurrent.ThreadFactory;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;

public class DisruptorLesson05 {

    public static class NumberEvent {
        private int number;
        private int result;
    }

    public static void main(String[] args) {
        AtomicInteger threadNumber = new AtomicInteger();

        ThreadFactory threadFactory = task -> new Thread(
                task,
                "pipeline-" + threadNumber.incrementAndGet()
        );

        Disruptor<NumberEvent> disruptor = new Disruptor<>(
                NumberEvent::new,
                8,
                threadFactory,
                ProducerType.SINGLE,
                new BlockingWaitStrategy()
        );

        // 第一阶段：读取原始数字，写入计算结果。
        EventHandler<NumberEvent> calculate =
                (event, sequence, endOfBatch) -> {
                    event.result = event.number * 10;

                    System.out.println(
                            "[计算] sequence=" + sequence
                                    + ", number=" + event.number
                                    + ", result=" + event.result
                    );
                };

        // 第二阶段：在上游完成对应事件后，读取结果。
        EventHandler<NumberEvent> output =
                (event, sequence, endOfBatch) -> {
                    System.out.println(
                            "[输出] sequence=" + sequence
                                    + ", result=" + event.result
                    );
                };

        // 配置先计算、后输出的依赖关系。
        disruptor.handleEventsWith(calculate).then(output);

        RingBuffer<NumberEvent> ringBuffer = disruptor.start();

        try {
            for (int number = 1; number <= 3; number++) {
                long sequence = ringBuffer.next();

                try {
                    NumberEvent event = ringBuffer.get(sequence);
                    event.number = number;

                    // 槽位会复用，为本次事件重置结果。
                    event.result = 0;
                } finally {
                    ringBuffer.publish(sequence);
                }
            }
        } finally {
            try {
                disruptor.shutdown(5, TimeUnit.SECONDS);
            } catch (TimeoutException e) {
                disruptor.halt();
                System.err.println("[关闭超时] 可能存在未处理事件");
            }
        }
    }
}
```

### 3. 事件为什么有两个字段

```
public static class NumberEvent {
    private int number;
    private int result;
}
```

两个字段分别由不同阶段负责：

| 字段       | 谁写入                   | 谁读取       |
| -------- | --------------------- | --------- |
| `number` | 生产者                   | calculate |
| `result` | 生产者初始化，calculate 计算写入 | output    |

数据流为：

```
生产者：number=2，result=0
    ↓
calculate：result=20
    ↓
output：读取 result=20
```

这里没有将计算结果发布到另一个 RingBuffer。两个消费者处理的是同一个序号对应的事件对象。

### 4. then(output) 表示什么

```
disruptor.handleEventsWith(calculate).then(output);
```

表示：

> output 必须等待 calculate 的消费进度达到对应序号，才能处理该事件。

例如，对于序号 0：

```
生产者发布 sequence=0
    ↓
calculate 处理 sequence=0，写入 result
    ↓
calculate 推进消费进度
    ↓
output 才能处理 sequence=0
```

Disruptor 通过序号、屏障及相应的内存可见性机制协调阶段，让下游能够读取上游在完成前写入的数据。

本例不需要仅为这条依赖链，把 `result` 声明成 `volatile`。

### 5. 和广播配置有什么区别

#### 没有依赖

```
disruptor.handleEventsWith(calculate, output);
```

关系为：

```
              ┌── calculate
RingBuffer ───┤
              └── output
```

output 可能先执行，也可能与 calculate 并发执行。

因此，它可能读到生产者初始化的：

```
result=0
```

不能用这种写法表达“先计算，再输出”。

#### 有依赖

```
disruptor.handleEventsWith(calculate).then(output);
```

关系为：

```
RingBuffer → calculate → output
```

对于同一事件，output 等待 calculate 完成对应处理阶段。

### 6. 两个阶段运行在同一个线程吗

本例不是。

标准配置会为 calculate 和 output 分别创建事件处理器，并通过线程工厂启动处理线程。

```
生产线程：main
计算线程：一个 pipeline 线程
输出线程：另一个 pipeline 线程
```

`then()` 配置的是阶段之间的等待关系，不是让 calculate 在自己的线程中直接调用 output。

### 7. 是否要算完全部事件才开始输出

不需要。

依赖针对消费进度，不要求生产者结束，也不要求先计算完所有事件。

可能出现：

```
calculate：事件 1 → 事件 2 → 事件 3
output：           事件 1 → 事件 2 → 事件 3
```

例如：

```
calculate 正在处理事件 2
output 同时处理已经计算完成的事件 1
```

这是流水线并行。

不过，标准批处理器可能在完成一批事件后才更新对外可见的消费进度，因此下游不一定在每条上游回调返回后立即开始。

### 8. 输出日志会严格交替吗

不一定。

可能看到：

```
[计算] sequence=0, number=1, result=10
[输出] sequence=0, result=10
[计算] sequence=1, number=2, result=20
[输出] sequence=1, result=20
```

也可能看到：

```
[计算] sequence=0, number=1, result=10
[计算] sequence=1, number=2, result=20
[计算] sequence=2, number=3, result=30
[输出] sequence=0, result=10
[输出] sequence=1, result=20
[输出] sequence=2, result=30
```

本例正常执行时，关键保证是：

* 每个阶段按序处理事件。
* 同一序号先完成计算，再进入输出阶段。
* 结果分别为 10、20、30。

以上是预期现象，不是本次运行记录。

### 9. 上游启动异步计算后立即返回，可以吗

需要特别小心。

假设 calculate 这样执行：

```
启动异步计算
    ↓
handler 立即返回
    ↓
异步计算稍后才写入 result
```

对 Disruptor 来说，handler 返回后，处理器可能推进消费进度。output 随后读取结果时，异步计算可能还没有完成。

因此：

```
then 等待上游处理进度
≠
自动等待上游启动的所有异步任务
```

异步线程之后再修改槽位对象，还可能与下游处理或槽位复用发生冲突。

本例在 calculate 回调内直接完成计算，再返回，因此满足依赖要求。

### 10. 上游抛异常，下游一定不会执行吗

不一定，取决于异常处理策略。

如果异常处理器记录错误后正常返回，处理器可能跳过失败事件并推进消费进度，下游仍可能处理该事件。

因此，依赖链不能理解为：

```
上游业务一定成功 → 下游执行
```

它协调的是阶段进度。业务需要明确表达失败状态，并让下游判断如何处理。

本例只是简单乘法，下一篇会专门演示异常处理。

### 11. output 很慢会有什么影响

生产者不能因为 calculate 已完成，就立即覆盖 output 还需要的数据。

```
calculate 完成
    ↓
output 尚未完成
    ↓
对应槽位仍不能提前复用
```

在这条通过 DSL 配置的依赖链中，末端消费者进度约束槽位复用；末端又依赖上游进度，从而保护整条链的数据处理。

如果 output 长期跟不上，RingBuffer 最终会填满，生产者可能在 `next()` 等待。

### 12. 动手练习

将计算公式改为：

```
event.result = event.number * event.number;
```

预期输出结果：

```
1、4、9
```

再在 output 中增加：

```
Thread.sleep(500);
```

观察 calculate 是否可以先处理后续事件，以及两个阶段的日志是否严格交替。

下一篇学习：**消费者处理某条事件时抛异常，后面的事件是否继续，以及如何配置异常处理器。**
