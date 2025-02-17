---
cover: >-
  https://images.unsplash.com/photo-1735657090759-883e95a7f392?crop=entropy&cs=srgb&fm=jpg&ixid=M3wxOTcwMjR8MHwxfHJhbmRvbXx8fHx8fHx8fDE3Mzk3OTczNDV8&ixlib=rb-4.0.3&q=85
coverY: 0
---

# 创建线程有几种方式？

## 方式 1：继承 Thread 类

Java 提供了 Thread 类，可以通过继承它并重写 run() 方法来创建线程。

🌟 示例

```
class MyThread extends Thread {
    @Override
    public void run() {
        System.out.println("Thread running: " + Thread.currentThread().getName());
    }
}

public class ThreadExample {
    public static void main(String[] args) {
        MyThread thread = new MyThread();
        thread.start();  // 启动线程
    }
}
```

✅ 适用场景

• 适用于 简单任务，但 Java 只允许 单继承，不适用于需要继承其他类的情况。

## 方式 2：实现 Runnable 接口

比继承 Thread 更推荐的方法，因为它支持多继承，更加灵活。

🌟 示例

```
class MyRunnable implements Runnable {
    @Override
    public void run() {
        System.out.println("Runnable thread running: " + Thread.currentThread().getName());
    }
}

public class RunnableExample {
    public static void main(String[] args) {
        Thread thread = new Thread(new MyRunnable());
        thread.start();
    }
}
```

✅ 适用场景

• 适用于任务和线程分离的场景，推荐用于多线程共享资源的情况。

## 方式 3：使用 Callable + FutureTask

如果线程需要返回值，可以使用 Callable 接口，它与 Runnable 类似，但支持 call() 方法返回结果。

🌟 示例

```
import java.util.concurrent.*;

class MyCallable implements Callable<String> {
    @Override
    public String call() throws Exception {
        return "Callable thread executed!";
    }
}

public class CallableExample {
    public static void main(String[] args) throws ExecutionException, InterruptedException {
        Callable<String> callable = new MyCallable();
        FutureTask<String> futureTask = new FutureTask<>(callable);
        Thread thread = new Thread(futureTask);
        thread.start();

        System.out.println("Thread result: " + futureTask.get()); // 获取返回值
    }
}
```

✅ 适用场景

• 适用于需要获取线程执行结果或处理异常的情况，例如异步计算。

## 方式 4：使用 线程池 (ExecutorService)

线程池可以管理多个线程，提高性能，并避免频繁创建销毁线程的开销。

🌟 示例

```
import java.util.concurrent.*;

public class ThreadPoolExample {
    public static void main(String[] args) {
        ExecutorService executor = Executors.newFixedThreadPool(3);

        for (int i = 0; i < 5; i++) {
            executor.execute(() -> {
                System.out.println("Thread from pool: " + Thread.currentThread().getName());
            });
        }

        executor.shutdown();
    }
}
```

✅ 适用场景

• 适用于高并发任务，如 Web 服务器、消息队列处理 等。

## 总结

| 方式          | 实现方式                    | 是否支持返回值 | 适用场景                  |
| ----------- | ----------------------- | ------- | --------------------- |
| 继承 Thread   | extends Thread          | ❌ 不支持   | 适用于简单任务，但 Java 只允许单继承 |
| 实现 Runnable | implements Runnable     | ❌ 不支持   | 适用于多个线程共享同一任务         |
| 实现 Callable | implements Callable\<V> | ✅ 支持    | 适用于需要返回值的任务           |
| 使用线程池       | ExecutorService         | ✅ 支持    | 适用于高并发、多任务处理          |

🚀 最佳实践

1\. 优先使用 Runnable 或 Callable，避免直接继承 Thread。

2\. 尽量使用线程池 (ExecutorService) 来管理线程，提升性能。

3\. Callable 适用于需要返回结果的异步任务，如 Web 请求或大数据计算。
