# 02 · Demo：RingBuffer 与基础生产消费

### 1. 本节目标

通过一个简单 Demo，学习 Disruptor 的基本使用流程：

```
创建 Disruptor
    ↓
注册消费者
    ↓
启动
    ↓
生产者发布 12 条事件
    ↓
消费者按序处理
    ↓
等待处理结束并关闭
```

RingBuffer 容量设置为 8，通过发布 12 条事件，理解槽位如何循环使用。

本节使用 **Java 17、Disruptor 3.4.4**。

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
        <groupId>com.lmax</groupId>
        <artifactId>disruptor</artifactId>
        <version>3.4.4</version>
    </dependency>
</dependencies>
```

### 3. 完整 Demo

创建文件 `DisruptorLesson01.java`，运行 `main()`。

```
package com.isep.akka.disruptor;

import com.lmax.disruptor.BlockingWaitStrategy;
import com.lmax.disruptor.RingBuffer;
import com.lmax.disruptor.TimeoutException;
import com.lmax.disruptor.dsl.Disruptor;
import com.lmax.disruptor.dsl.ProducerType;

import java.util.concurrent.ThreadFactory;
import java.util.concurrent.TimeUnit;

public class DisruptorLesson01 {

    // RingBuffer 槽位中的对象，会被重复使用。
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
        // 容量必须是 2 的幂。
        int bufferSize = 8;

        // 创建消费者使用的线程。
        // 显式声明 ThreadFactory，避免构造方法重载产生歧义。
        ThreadFactory threadFactory =
                task -> new Thread(task, "number-consumer");

        Disruptor<NumberEvent> disruptor = new Disruptor<>(
                NumberEvent::new,
                bufferSize,
                threadFactory,
                ProducerType.SINGLE,
                new BlockingWaitStrategy()
        );

        // 注册消费者，必须在 start() 之前配置。
        disruptor.handleEventsWith((event, sequence, endOfBatch) -> {
            // 本例容量为 8，可以通过序号计算槽位下标。
            long slot = sequence & (bufferSize - 1);

            System.out.println(
                    "[消费] sequence=" + sequence
                            + ", slot=" + slot
                            + ", value=" + event.getValue()
                            + ", endOfBatch=" + endOfBatch
                            + ", thread=" + Thread.currentThread().getName()
            );
        });

        // 启动消费者，取得用于发布事件的 RingBuffer。
        RingBuffer<NumberEvent> ringBuffer = disruptor.start();

        try {
            // main 是唯一的生产线程，所以使用 SINGLE。
            for (long value = 1; value <= 12; value++) {
                // 申请可写位置；没有可用容量时可能等待。
                long sequence = ringBuffer.next();

                try {
                    // 获取槽位中已经创建好的对象。
                    NumberEvent event = ringBuffer.get(sequence);

                    // 为本次事件写入数据。
                    event.setValue(value);
                } finally {
                    // 发布后，消费者才能处理这一序号的事件。
                    ringBuffer.publish(sequence);
                }
            }
        } finally {
            try {
                // 本例已停止生产，等待已发布事件处理完，再停止消费者。
                disruptor.shutdown(5, TimeUnit.SECONDS);
            } catch (TimeoutException e) {
                // 超时后请求停止处理器，可能有事件尚未处理。
                disruptor.halt();
                System.err.println("[关闭超时] 可能存在未处理事件");
            }
        }
    }
}
```

### 4. new Disruptor 的五个参数

```
Disruptor<NumberEvent> disruptor = new Disruptor<>(
        NumberEvent::new,
        bufferSize,
        threadFactory,
        ProducerType.SINGLE,
        new BlockingWaitStrategy()
);
```

| 参数            | 本例配置                   | 作用                |
| ------------- | ---------------------- | ----------------- |
| 事件工厂          | `NumberEvent::new`     | 创建槽位中的事件对象        |
| RingBuffer 容量 | `8`                    | 指定槽位数量            |
| 线程工厂          | `threadFactory`        | 创建消费者处理器使用的线程     |
| 生产者模式         | `ProducerType.SINGLE`  | 表示只有一个发布线程        |
| 等待策略          | `BlockingWaitStrategy` | 消费者没有可处理事件时采用阻塞等待 |

#### NumberEvent::new

这是 Java 方法引用，相当于：

```
() -> new NumberEvent()
```

初始化 RingBuffer 时，事件工厂为每个槽位创建对象。

容量为 8，可以理解为预先准备了 8 个 `NumberEvent`：

```
槽位 0 → NumberEvent
槽位 1 → NumberEvent
……
槽位 7 → NumberEvent
```

后面发布 12 条事件时，会复用这些对象。

#### threadFactory

```
ThreadFactory threadFactory =
        task -> new Thread(task, "number-consumer");
```

Disruptor 把需要在线程中执行的处理器作为 `task` 传入，工厂返回一个新线程。

本例只配置一个普通消费者处理器，因此使用一个消费线程。生产工作由 main 线程执行。

#### ProducerType.SINGLE

这里描述的是发布线程。

本例只有 main 调用：

```
ringBuffer.next();
ringBuffer.publish(sequence);
```

所以使用 `SINGLE`。

如果多个线程向同一个 RingBuffer 并发发布，应使用 `MULTI`，不能根据消费者数量选择这个参数。

### 5. 注册消费者

```
disruptor.handleEventsWith((event, sequence, endOfBatch) -> {
    // 处理事件。
});
```

三个参数分别是：

| 参数           | 含义             |
| ------------ | -------------- |
| `event`      | 当前槽位中的事件对象     |
| `sequence`   | 当前事件的序号        |
| `endOfBatch` | 是否为当前处理批次的最后一条 |

这一步只是配置处理规则。

真正启动消费者的是：

```
disruptor.start();
```

配置应该在启动前完成。

### 6. 发布事件的三个步骤

#### 第一步：申请序号

```
long sequence = ringBuffer.next();
```

申请下一次写入的位置。

本例序号从 0 开始递增：

```
0、1、2、3……
```

如果下一槽位尚不能安全复用，生产者可能在这里等待。

#### 第二步：填充数据

```
NumberEvent event = ringBuffer.get(sequence);
event.setValue(value);
```

`get()` 返回对应槽位已有的对象，不是每次创建一个新对象。

此时生产者正在填写数据，还没有完成发布。

#### 第三步：发布

```
ringBuffer.publish(sequence);
```

通知消费机制：这个序号的数据已经准备好，可以按序处理。

完整过程：

```
next() → get() → 填充字段 → publish()
```

消费者可能在 `publish()` 后很快开始处理，不需要等待 main 完成整个循环。

### 7. 为什么 publish 放在 finally 中

```
long sequence = ringBuffer.next();

try {
    NumberEvent event = ringBuffer.get(sequence);
    event.setValue(value);
} finally {
    ringBuffer.publish(sequence);
}
```

申请序号后，如果遗漏发布，可能留下未发布的位置，阻碍后续消费推进。

但 `finally` 不保证业务数据正确。

如果填充字段时抛异常，仍可能发布一个未完整填充的事件。因此实际业务应尽量在申请序号之前完成可能失败的计算和校验，再将准备好的结果写入槽位。

本例只是给 `long` 字段赋值，逻辑很简单。

### 8. 容量只有 8，为什么能发布 12 条

因为槽位会循环使用：

| sequence | 槽位下标 | value |
| -------- | ---- | ----- |
| 0        | 0    | 1     |
| 1        | 1    | 2     |
| 2        | 2    | 3     |
| 3        | 3    | 4     |
| 4        | 4    | 5     |
| 5        | 5    | 6     |
| 6        | 6    | 7     |
| 7        | 7    | 8     |
| 8        | 0    | 9     |
| 9        | 1    | 10    |
| 10       | 2    | 11    |
| 11       | 3    | 12    |

例如：

```
sequence = 0 使用槽位 0
    ↓
消费者处理完成，并推进消费进度
    ↓
sequence = 8 可以再次使用槽位 0
```

**循环使用不等于随意覆盖。**

Disruptor 根据消费者进度判断槽位是否可以复用。如果消费者尚未处理完，生产者需要等待。

### 9. endOfBatch 表示什么

假设消费线程检查时，序号 0～2 已连续可用，它可以处理这一批：

```
sequence=0，endOfBatch=false
sequence=1，endOfBatch=false
sequence=2，endOfBatch=true
```

随后生产者继续发布，又可以形成下一批。

因此：

```
endOfBatch=true
```

不代表所有生产工作结束，也不代表它一定是第 12 条事件。

批次边界受运行时调度影响，不应写死预期。

### 10. shutdown 和 halt 有什么区别

#### shutdown

```
disruptor.shutdown(5, TimeUnit.SECONDS);
```

在本例停止生产后，等待已发布事件的消费进度追上，再停止消费者处理器。

它关注消费进度，不是所有外部业务一定成功的证明。

例如，handler 启动异步请求后立即返回，Disruptor 不会因此自动等待该请求完成。

#### halt

```
disruptor.halt();
```

请求停止处理器，不保证处理完所有已发布事件，也不会强制中断正在执行的业务函数。

本例只在关闭等待超时后调用，并明确提示可能存在未处理事件。

### 11. 预期输出

关键内容类似：

```
[消费] sequence=0, slot=0, value=1, ...
[消费] sequence=1, slot=1, value=2, ...
……
[消费] sequence=7, slot=7, value=8, ...
[消费] sequence=8, slot=0, value=9, ...
……
[消费] sequence=11, slot=3, value=12, ...
```

重点观察：

* `sequence` 从 0 增加到 11。
* `value` 从 1 增加到 12。
* 槽位下标到 7 后重新从 0 开始。
* 消费逻辑在 `number-consumer` 线程执行。
* `endOfBatch` 的分布可能变化。

以上为预期现象，不是本次运行记录。

### 12. 动手练习

将容量改为：

```
int bufferSize = 4;
```

保持发布 12 条事件，观察槽位下标：

```
0、1、2、3、0、1、2、3……
```

然后尝试回答：如果消费者处理很慢，生产者准备再次使用槽位 0 时，它应该等待，还是覆盖旧数据？

下一篇通过慢消费者 Demo，观察 **RingBuffer 填满后，生产者在哪里等待**。
