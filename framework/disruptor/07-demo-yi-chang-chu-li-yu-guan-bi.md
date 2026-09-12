# 07 · Demo：异常处理与关闭

### 1. 本节目标

消费者处理事件时，如果抛出异常，会发生什么？

本节发布数字 1～5，并在处理数字 3 时故意抛出异常：

```
1 → 成功
2 → 成功
3 → 抛异常，记录错误
4 → 继续处理
5 → 继续处理
```

通过这个 Demo，理解异常处理器、消费进度和业务成功之间的区别。

本节使用 **Java 17、Disruptor 3.4.4**，依赖沿用前文。

### 2. 完整 Demo

创建文件 `DisruptorLesson06.java`，运行 `main()`。

```
package com.isep.akka.disruptor;

import com.lmax.disruptor.BlockingWaitStrategy;
import com.lmax.disruptor.ExceptionHandler;
import com.lmax.disruptor.RingBuffer;
import com.lmax.disruptor.TimeoutException;
import com.lmax.disruptor.dsl.Disruptor;
import com.lmax.disruptor.dsl.ProducerType;

import java.util.concurrent.ThreadFactory;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;

public class DisruptorLesson06 {

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
        // 消费线程更新，main 在关闭后读取。
        AtomicInteger successCount = new AtomicInteger();
        AtomicInteger failureCount = new AtomicInteger();

        ThreadFactory threadFactory =
                task -> new Thread(task, "number-consumer");

        Disruptor<NumberEvent> disruptor = new Disruptor<>(
                NumberEvent::new,
                8,
                threadFactory,
                ProducerType.SINGLE,
                new BlockingWaitStrategy()
        );

        // 在启动前配置异常处理器。
        disruptor.setDefaultExceptionHandler(
                new ExceptionHandler<NumberEvent>() {

                    @Override
                    public void handleEventException(
                            Throwable error,
                            long sequence,
                            NumberEvent event
                    ) {
                        failureCount.incrementAndGet();

                        System.out.println(
                                "[处理失败] sequence=" + sequence
                                        + ", value=" + event.getValue()
                                        + ", 原因=" + error.getMessage()
                        );

                        // 正常返回：本例处理器会跳过失败事件，继续后续事件。
                        // 这里没有重试，也没有回滚业务。
                    }

                    @Override
                    public void handleOnStartException(Throwable error) {
                        throw new IllegalStateException(
                                "消费者启动回调失败",
                                error
                        );
                    }

                    @Override
                    public void handleOnShutdownException(Throwable error) {
                        System.err.println(
                                "[消费者关闭回调失败] " + error.getMessage()
                        );
                    }
                }
        );

        disruptor.handleEventsWith((event, sequence, endOfBatch) -> {
            System.out.println(
                    "[开始处理] sequence=" + sequence
                            + ", value=" + event.getValue()
            );

            if (event.getValue() == 3) {
                throw new IllegalStateException("数字 3 模拟处理失败");
            }

            // 只有没有抛异常的事件才会执行到这里。
            successCount.incrementAndGet();

            System.out.println(
                    "[处理成功] value=" + event.getValue()
            );
        });

        RingBuffer<NumberEvent> ringBuffer = disruptor.start();

        try {
            for (int value = 1; value <= 5; value++) {
                long sequence = ringBuffer.next();

                try {
                    ringBuffer.get(sequence).setValue(value);
                } finally {
                    ringBuffer.publish(sequence);
                }
            }
        } finally {
            try {
                // 本例生产已经结束，等待消费进度追上。
                disruptor.shutdown(5, TimeUnit.SECONDS);
            } catch (TimeoutException e) {
                disruptor.halt();
                throw new IllegalStateException(
                        "关闭超时，可能存在未处理事件",
                        e
                );
            }
        }

        System.out.println(
                "[统计] 成功=" + successCount.get()
                        + ", 失败=" + failureCount.get()
        );
    }
}
```

### 3. 异常在哪里发生

消费者处理数字 3 时：

```
if (event.getValue() == 3) {
    throw new IllegalStateException("数字 3 模拟处理失败");
}
```

异常发生后，当前回调剩余的代码不会继续执行。

因此，这两行不会为数字 3 执行：

```
successCount.incrementAndGet();

System.out.println("[处理成功] value=" + event.getValue());
```

接下来由 Disruptor 的事件处理器调用配置的异常处理器。

### 4. ExceptionHandler 的三个方法

| 方法                            | 处理什么异常           |
| ----------------------------- | ---------------- |
| `handleEventException()`      | 事件处理回调抛出的异常      |
| `handleOnStartException()`    | 消费者生命周期启动回调抛出的异常 |
| `handleOnShutdownException()` | 消费者生命周期关闭回调抛出的异常 |

本例实际触发的是：

```
handleEventException(error, sequence, event)
```

它收到：

```
error：数字 3 模拟处理失败
sequence：2
event.value：3
```

序号从 0 开始，所以数字 3 对应序号 2。

另外两个方法用于生命周期回调，不是捕获所有启动和关闭相关异常的通用入口。例如，`shutdown()` 等待超时仍由调用方捕获。

### 5. 为什么出错后还能继续处理 4 和 5

本例异常处理器记录日志后正常返回：

```
public void handleEventException(
        Throwable error,
        long sequence,
        NumberEvent event
) {
    // 记录失败。
}
```

对于本例的标准事件处理器，异常处理器正常返回后，它会跳过失败事件，推进相应进度，继续处理后面的事件。

```
数字 3 处理失败
    ↓
调用异常处理器
    ↓
异常处理器正常返回
    ↓
继续处理数字 4、5
```

这是本例选择的处理方式，不是所有异常策略都会继续。

如果异常处理器再次抛出异常，可能导致消费处理器退出，后续事件无法继续处理。

### 6. 记录异常等于处理成功吗

不等于。

本例最终应为：

```
成功：1、2、4、5
失败：3
```

数字 3 只是被记录为失败，然后跳过。

异常处理器没有：

* 重新执行数字 3。
* 修复失败原因。
* 回滚已经发生的副作用。
* 将失败事件自动保存到持久化存储。

因此不能把“程序继续运行”理解成“业务全部成功”。

### 7. 默认情况下也会继续吗

不能这样假设。

Disruptor 3.4.4 的默认异常处理通常会将事件异常视为致命错误，记录后抛出运行时异常，可能使对应消费处理器退出。

因此，本例显式配置了异常处理器：

```
disruptor.setDefaultExceptionHandler(...);
```

实际项目中，应明确决定：

```
哪些错误允许跳过？
哪些错误需要停止？
哪些错误需要重试或人工处理？
```

对于不能丢失的业务事件，仅打印日志并继续通常不足以满足要求。

### 8. 为什么 shutdown 正常返回，仍然有失败事件

```
disruptor.shutdown(5, TimeUnit.SECONDS);
```

它等待的是已发布事件的消费进度追上，然后停止处理器。

本例数字 3 失败后，异常处理器正常返回，消费进度仍然继续推进，最终处理到数字 5。

因此可以出现：

```
shutdown 正常返回
成功 4 条
失败 1 条
```

**消费进度完成，不等于每条业务都成功。**

如果 handler 只是启动异步任务就返回，`shutdown()` 也不会自动等待那些外部异步任务完成。

### 9. shutdown 超时与事件异常有什么区别

| 情况          | 含义             | 本例处理位置                   |
| ----------- | -------------- | ------------------------ |
| 数字 3 处理失败   | 某条事件的业务回调抛异常   | `handleEventException()` |
| shutdown 超时 | 等待消费进度追上超过指定时间 | main 的 `catch`           |

消费处理器退出、业务长期阻塞等情况，都可能导致关闭等待超时。

本例超时后执行：

```
disruptor.halt();
```

它请求停止处理器，但不会保证剩余事件全部处理完，也不会强制中断正在运行的业务函数。

### 10. 依赖链中，上游失败会怎样

假设配置：

```
disruptor.handleEventsWith(calculate).then(output);
```

如果 calculate 处理失败，而异常处理器记录后返回，上游进度仍可能推进，output 随后可能处理这条失败事件。

所以：

```
then 等待上游进度
≠
then 保证上游业务成功
```

需要下游识别失败时，可以在事件中明确设置成功状态、错误信息等字段，并在每次发布时初始化，避免槽位复用留下旧状态。

### 11. 为什么不能保存 event 引用稍后重试

异常处理器收到的 `event` 仍然是 RingBuffer 槽位中的可复用对象。

如果直接把引用放到另一个异步队列：

```
保存 event 引用
    ↓
消费进度推进
    ↓
槽位被生产者复用
    ↓
稍后读取到的内容可能已经改变
```

需要异步重试时，应提取必要数据，创建独立快照。

是否持久化、如何限制重试次数、如何保证幂等，还需要按业务要求设计。

### 12. 整体执行流程

```
创建 Disruptor
    ↓
配置异常处理器和消费者
    ↓
启动，发布数字 1～5
    ↓
1、2 处理成功
    ↓
3 抛异常
    ↓
异常处理器记录失败并返回
    ↓
4、5 继续处理成功
    ↓
消费进度追上，shutdown 返回
    ↓
打印成功与失败数量
```

### 13. 预期输出

关键日志类似：

```
[处理成功] value=1
[处理成功] value=2
[处理失败] sequence=2, value=3, 原因=数字 3 模拟处理失败
[处理成功] value=4
[处理成功] value=5
[统计] 成功=4, 失败=1
```

以上为预期现象，不是本次运行记录。

### 14. 动手练习

将失败条件改为：

```
if (event.getValue() == 3 || event.getValue() == 4) {
    throw new IllegalStateException("模拟处理失败");
}
```

预期统计：

```
成功=3，失败=2
```

观察数字 5 是否仍然继续处理，并解释为什么 `shutdown()` 正常返回不能证明全部业务成功。

下一篇学习：**按账户分片，让同一账户进入同一个 Disruptor，不同分片并行处理。**
