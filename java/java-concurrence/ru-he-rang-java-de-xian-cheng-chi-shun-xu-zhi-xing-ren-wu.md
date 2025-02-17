---
cover: >-
  https://images.unsplash.com/photo-1736230990003-a98eea26ea1f?crop=entropy&cs=srgb&fm=jpg&ixid=M3wxOTcwMjR8MHwxfHJhbmRvbXx8fHx8fHx8fDE3Mzk3OTcxNzZ8&ixlib=rb-4.0.3&q=85
coverY: 0
---

# 如何让Java的线程池顺序执行任务

## 方法 1：使用单线程线程池（SingleThreadExecutor）

Executors.newSingleThreadExecutor() 创建的线程池只有一个线程，任务会按照提交的顺序执行。

🌟 示例

```
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class SingleThreadExecutorExample {
    public static void main(String[] args) {
        ExecutorService executorService = Executors.newSingleThreadExecutor();

        for (int i = 1; i <= 5; i++) {
            int taskNumber = i;
            executorService.submit(() -> {
                System.out.println("Executing task " + taskNumber + " by " + Thread.currentThread().getName());
                try { Thread.sleep(1000); } catch (InterruptedException e) { e.printStackTrace(); }
            });
        }

        executorService.shutdown();
    }
}
```

✅ 运行结果（任务按照提交顺序执行）

```
Executing task 1 by pool-1-thread-1
Executing task 2 by pool-1-thread-1
Executing task 3 by pool-1-thread-1
Executing task 4 by pool-1-thread-1
Executing task 5 by pool-1-thread-1
```

📌 适用场景：

• 适用于需要严格保证任务执行顺序的场景，比如日志写入、消息处理等。

## 方法 2：使用 ArrayBlockingQueue 限制任务并按 FIFO 顺序执行

ThreadPoolExecutor 允许自定义任务队列，如果使用 ArrayBlockingQueue，任务会按照 FIFO（先进先出）顺序执行。

🌟 示例

```
import java.util.concurrent.*;

public class OrderedThreadPoolExample {
    public static void main(String[] args) {
        ThreadPoolExecutor executor = new ThreadPoolExecutor(
            1, 1, 0L, TimeUnit.MILLISECONDS,
            new ArrayBlockingQueue<>(10),  // 使用 FIFO 队列
            Executors.defaultThreadFactory(),
            new ThreadPoolExecutor.AbortPolicy()
        );

        for (int i = 1; i <= 5; i++) {
            int taskNumber = i;
            executor.execute(() -> {
                System.out.println("Executing task " + taskNumber + " by " + Thread.currentThread().getName());
                try { Thread.sleep(1000); } catch (InterruptedException e) { e.printStackTrace(); }
            });
        }

        executor.shutdown();
    }
}
```

📌 适用场景：

• 适用于需要保证任务按顺序入队 & 出队的场景。

## 方法 3：使用 SynchronousQueue 严格按顺序提交

SynchronousQueue 本质上不存储元素，任务提交后必须被线程池立刻处理，因此能够严格控制任务按顺序执行。

🌟 示例

```
import java.util.concurrent.*;

public class SynchronousQueueThreadPoolExample {
    public static void main(String[] args) {
        ThreadPoolExecutor executor = new ThreadPoolExecutor(
            1, 1, 0L, TimeUnit.MILLISECONDS,
            new SynchronousQueue<>(),  // 任务提交后必须立即执行，否则会阻塞
            Executors.defaultThreadFactory(),
            new ThreadPoolExecutor.AbortPolicy()
        );

        for (int i = 1; i <= 5; i++) {
            int taskNumber = i;
            executor.execute(() -> {
                System.out.println("Executing task " + taskNumber + " by " + Thread.currentThread().getName());
                try { Thread.sleep(1000); } catch (InterruptedException e) { e.printStackTrace(); }
            });
        }

        executor.shutdown();
    }
}
```

📌 适用场景：

• 适用于需要精确控制任务顺序，但不允许任务积压的场景。

## 方法 4：使用 ScheduledThreadPoolExecutor 顺序调度任务

ScheduledThreadPoolExecutor 可以按照固定的间隔时间提交任务，确保任务按顺序执行。

🌟 示例

```
import java.util.concurrent.*;

public class ScheduledThreadPoolExample {
    public static void main(String[] args) {
        ScheduledExecutorService executor = Executors.newScheduledThreadPool(1);

        for (int i = 1; i <= 5; i++) {
            int taskNumber = i;
            executor.schedule(() -> {
                System.out.println("Executing task " + taskNumber + " by " + Thread.currentThread().getName());
            }, taskNumber * 1, TimeUnit.SECONDS); // 每秒执行一个任务
        }

        executor.shutdown();
    }
}
```

📌 适用场景：

• 适用于定时任务，如日志归档、数据同步等场景。

## 总结

| 方式               | 线程池类型                                   | 任务执行顺序     | 适用场景          |
| ---------------- | --------------------------------------- | ---------- | ------------- |
| 单线程线程池           | Executors.newSingleThreadExecutor()     | 严格按照提交顺序   | 适用于日志、消息处理等任务 |
| FIFO 任务队列        | ThreadPoolExecutor + ArrayBlockingQueue | 保证 FIFO 出队 | 适用于有序数据处理     |
| SynchronousQueue | ThreadPoolExecutor + SynchronousQueue   | 任务提交后立即执行  | 适用于严格顺序执行任务   |
| 定时任务             | ScheduledThreadPoolExecutor             | 按设定间隔执行    | 适用于定时任务       |

🔹 推荐方案

• 保证严格顺序 👉 SingleThreadExecutor

• 控制任务排队 👉 ThreadPoolExecutor + ArrayBlockingQueue

• 精准控制提交顺序 👉 ThreadPoolExecutor + SynchronousQueue

• 按固定间隔执行 👉 ScheduledThreadPoolExecutor

🚀 最佳实践

1\. 优先使用 SingleThreadExecutor，简单易用，保证任务顺序。

2\. 避免 CachedThreadPool，它是无界队列，任务执行顺序不可控。

3\. 对高吞吐场景，使用 ArrayBlockingQueue 限制任务队列，确保任务按照 FIFO 处理。
