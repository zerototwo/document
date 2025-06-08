# Disruptor 的等待策略

Disruptor 的等待策略（WaitStrategy）决定了 消费者在没有新事件可用时如何等待，这是 Disruptor 能否实现低延迟和高吞吐的核心参数之一。不同的等待策略对延迟、吞吐和CPU资源占用影响很大，下面整理最常用的几种等待策略及其适用场景：

***

### 常见 WaitStrategy 及其特点

| 策略名称                      | 主要特点                 | 优缺点               | 适用场景                   |
| ------------------------- | -------------------- | ----------------- | ---------------------- |
| BlockingWaitStrategy      | 用锁和条件变量实现阻塞等待        | CPU 占用低，延迟高       | 普通业务、低延迟需求场景           |
| SleepingWaitStrategy      | 先自旋、后 yield，最后 sleep | 折中 CPU 占用和延迟      | 日志等对延迟不敏感场景            |
| YieldingWaitStrategy      | 多次自旋后 yield CPU      | 延迟低，CPU 占用高，多核性能好 | 对延迟极敏感场景               |
| BusySpinWaitStrategy      | 一直自旋等待，不让出 CPU       | 极低延迟，极高 CPU 占用    | 核心线程独占、低延迟极端场景         |
| LiteBlockingWaitStrategy  | Blocking 的轻量变体       | 内存占用略低，适合大规模队列    | 较少用，适合大量 RingBuffer 场景 |
| PhasedBackoffWaitStrategy | 结合自旋/yield/阻塞        | 兼顾延迟和资源占用         | 混合场景、对性能有特殊权衡          |

***

### 主要策略原理简析

\


#### 1. BlockingWaitStrategy

* 实现方式：LockSupport.park()/unpark() 或 Object.wait()/notify()
* 优点：CPU 占用最低，不会浪费资源
* 缺点：由于线程切换，延迟较高
* 典型用法：通用业务，异步日志

\


#### 2. SleepingWaitStrategy

* 实现方式：短暂自旋若干次，再 yield，最后 sleep（如 Thread.sleep(0, 1)）
* 优点：平衡延迟与资源消耗
* 缺点：延迟不如自旋型低
* 典型用法：延迟一般，资源受限

\


#### 3. YieldingWaitStrategy

* 实现方式：自旋若干次后，yield CPU
* 优点：延迟极低，多核机器效果最好
* 缺点：CPU 占用较高，单核性能下降
* 典型用法：高性能交易、低延迟场景

\


#### 4. BusySpinWaitStrategy

* 实现方式：死循环自旋，不让出 CPU
* 优点：延迟最低，适合对响应时间极度敏感的场景
* 缺点：CPU 占用极高，只能在核心线程独占时用
* 典型用法：极端低延迟、高频场景（如高频交易）

\


#### 5. PhasedBackoffWaitStrategy

* 实现方式：先自旋、再 yield、最后阻塞
* 优点：可灵活权衡性能与资源消耗
* 典型用法：需要平衡延迟和资源消耗的场景

***

### 选型建议

* 对延迟极端敏感：Yielding/BusySpin
* 资源有限但还要吞吐：Sleeping/PhasedBackoff
* 资源很有限，延迟不敏感：Blocking

***

#### 代码配置示例

```
// 生产级配置常见方式
Disruptor<MyEvent> disruptor = new Disruptor<>(
    factory,
    bufferSize,
    executor,
    ProducerType.SINGLE,
    new YieldingWaitStrategy() // 换成其他策略即可
);
```

