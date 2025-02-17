---
cover: >-
  https://images.unsplash.com/photo-1737440227575-fd61700ff759?crop=entropy&cs=srgb&fm=jpg&ixid=M3wxOTcwMjR8MHwxfHJhbmRvbXx8fHx8fHx8fDE3Mzk3OTc4MTN8&ixlib=rb-4.0.3&q=85
coverY: 0
---

# synchronized

synchronized 是 Java 语言中最基本的同步机制，用于保证 线程安全，防止多个线程同时访问共享资源时发生数据不一致的问题。

## 1. synchronized 的三种用法

synchronized 关键字可以用于以下三种场景：

* 修饰实例方法（锁当前对象实例 this）
* 修饰静态方法（锁 Class 类对象）
* 修饰代码块（自定义锁对象，灵活性更高）

### 1.1 修饰实例方法

🔹 锁住当前实例对象 (this)，所有访问该方法的线程都必须获取该对象的锁。

```
class SynchronizedExample {
    public synchronized void syncMethod() {
        System.out.println(Thread.currentThread().getName() + " 正在执行 synchronized 方法...");
        try { Thread.sleep(1000); } catch (InterruptedException e) { e.printStackTrace(); }
    }
}
```

示例

```
public class Main {
    public static void main(String[] args) {
        SynchronizedExample obj = new SynchronizedExample();

        new Thread(obj::syncMethod, "线程1").start();
        new Thread(obj::syncMethod, "线程2").start();
    }
}
```

📌 运行结果

```
线程1 正在执行 synchronized 方法...
（1秒后）
线程2 正在执行 synchronized 方法...
```

📝 说明

• synchronized 方法锁定 当前实例对象，同一对象的线程只能顺序执行。

• 不同对象的 synchronized 方法不会互斥（即不会同步）。

### 1.2 修饰静态方法

🔹 锁住 Class 对象，所有线程在访问该类的 synchronized 静态方法时必须获得该 Class 的锁。

```
class SynchronizedStaticExample {
    public static synchronized void staticSyncMethod() {
        System.out.println(Thread.currentThread().getName() + " 正在执行 synchronized 静态方法...");
        try { Thread.sleep(1000); } catch (InterruptedException e) { e.printStackTrace(); }
    }
}
```

示例

```
public class Main {
    public static void main(String[] args) {
        new Thread(SynchronizedStaticExample::staticSyncMethod, "线程1").start();
        new Thread(SynchronizedStaticExample::staticSyncMethod, "线程2").start();
    }
}
```

📌 运行结果

```
线程1 正在执行 synchronized 静态方法...
（1秒后）
线程2 正在执行 synchronized 静态方法...
```

📝 说明

• synchronized static 方法锁住的是类对象（Class），所有实例都会受影响。

• 即使是不同实例，仍然会同步执行。

### 1.3 修饰代码块

🔹 使用自定义对象作为锁，提高灵活性。

```
class SynchronizedBlockExample {
    private final Object lock = new Object(); // 自定义锁对象

    public void syncBlockMethod() {
        synchronized (lock) {
            System.out.println(Thread.currentThread().getName() + " 正在执行 synchronized 代码块...");
            try { Thread.sleep(1000); } catch (InterruptedException e) { e.printStackTrace(); }
        }
    }
}
```

示例

```
public class Main {
    public static void main(String[] args) {
        SynchronizedBlockExample obj = new SynchronizedBlockExample();

        new Thread(obj::syncBlockMethod, "线程1").start();
        new Thread(obj::syncBlockMethod, "线程2").start();
    }
}
```

📌 运行结果

```
线程1 正在执行 synchronized 代码块...
（1秒后）
线程2 正在执行 synchronized 代码块...
```

📝 说明

• synchronized(lock) 只锁定 lock 这个对象，而不是整个实例。

• 可以使用不同的锁对象，灵活控制多个临界区。

## 2. synchronized 的底层原理

synchronized 的底层原理是依靠 JVM 内部的对象监视器（Monitor） 和 monitorenter / monitorexit 指令 来实现。

🔹 synchronized 关键字的字节码

```
public synchronized void syncMethod() { }
```

对应的 JVM 字节码指令：

```
0: aload_0
1: monitorenter  // 进入同步块，获取锁
2: ...           // 执行方法逻辑
3: monitorexit   // 退出同步块，释放锁
4: return
```

📌 说明

• monitorenter 获取锁（如果其他线程占用，则进入等待）。

• monitorexit 释放锁（必须执行，否则可能发生死锁）。

## 3. synchronized 的优缺点

| 优点           | 缺点           |
| ------------ | ------------ |
| 保证线程安全       | 竞争锁时可能导致性能下降 |
| 实现简单         | 不能中断锁等待      |
| 避免死锁（如果使用得当） | 加锁粒度较粗，影响并发性 |

## 4. synchronized vs ReentrantLock

| 对比项      | synchronized                         | ReentrantLock                            |
| -------- | ------------------------------------ | ---------------------------------------- |
| 加锁方式     | JVM 实现，基于 monitorenter / monitorexit | JDK API 实现，基于 AbstractQueuedSynchronizer |
| 是否可中断    | ❌ 不能中断等待                             | ✅ 可 lockInterruptibly()                  |
| 是否公平锁    | ❌ 非公平                                | ✅ 可选公平 / 非公平锁                            |
| 性能       | JDK 1.6 之前性能较低，1.6 以后优化（偏向锁、轻量级锁）    | 性能较高，适用于高并发                              |
| 是否支持条件变量 | ❌ 不支持                                | ✅ Condition                              |

结论

* 一般情况下，synchronized 更简单，推荐使用。
* 高并发场景（如数据库连接池）建议用 ReentrantLock。&#x20;

## 5. synchronized 优化：偏向锁、轻量级锁、自旋锁

JDK 1.6 之后，JVM 优化 synchronized 以提升性能：

1\. 偏向锁（Biased Locking）：如果一个线程获取锁，JVM 让它“偏向”于这个线程，避免锁竞争。

2\. 轻量级锁（Lightweight Locking）：如果没有竞争，使用 CAS（Compare And Swap）提高性能。

3\. 自旋锁（Spin Lock）：短时间内不释放锁时，线程自旋等待，避免 CPU 上下文切换的开销。

## 6.结论

1\. synchronized 适用于大多数线程同步场景，如对象方法锁、静态方法锁、代码块锁。

2\. 在 JDK 1.6+ 之后，synchronized 性能已大幅优化，并不比 ReentrantLock 慢。

3\. 高并发场景（大量线程竞争），推荐使用 ReentrantLock 提升性能。
