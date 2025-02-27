---
cover: >-
  https://images.unsplash.com/photo-1736178643897-4f9cfc7b0fe5?crop=entropy&cs=srgb&fm=jpg&ixid=M3wxOTcwMjR8MHwxfHJhbmRvbXx8fHx8fHx8fDE3Mzk3OTgyMTF8&ixlib=rb-4.0.3&q=85
coverY: 0
---

# synchronized 如何保证原子性、可见性、有序性？

在 Java 并发编程中，原子性（Atomicity）、可见性（Visibility）、有序性（Orderliness） 是多线程安全的三大关键问题。synchronized 关键字能够保证这三大特性，我们分别来分析其实现原理。

## 1. synchronized 如何保证原子性？

原子性（Atomicity） 指的是 操作不可被中断，即多个线程同时访问时，某个线程的操作不会被其他线程看到未完成的部分。

synchronized 通过 “锁机制” 确保线程在执行同步代码块时，其他线程无法进入，从而保证原子性。

### 示例

```java
class AtomicExample {
    private int count = 0;

    public synchronized void increment() {
        count++; // 这一步包含 读取 -> 计算 -> 赋值，需要保证原子性
    }

    public synchronized int getCount() {
        return count;
    }
}
```

### synchronized 如何保证原子性？

#### 1. 获取锁 (monitorenter)：

* 当线程进入 synchronized 代码块时，会尝试获取 对象的监视器锁（Monitor Lock），如果获取成功，其他线程必须等待。

2\. 执行临界区代码：

* 线程独占 CPU 资源执行 count++ 操作，不会被其他线程中断。

3\. 释放锁 (monitorexit)：

* 线程执行完成后，释放锁，其他线程才能继续执行。\


#### 结论

* synchronized 保证同一时间只有一个线程可以进入同步代码块，因此可以保证原子性。

## 2. synchronized 如何保证可见性？

可见性（Visibility） 指的是 当一个线程修改了共享变量的值，其他线程能够立即看到这个修改。

synchronized 通过“Java 内存模型（JMM）”的 Happens-Before 规则 和 “锁释放 + 刷新主存”机制 确保变量的可见性。

#### 示例

```java
class VisibilityExample {
    private boolean flag = false;

    public synchronized void setFlag() {
        flag = true;
    }

    public synchronized boolean getFlag() {
        return flag;
    }
}
```

#### synchronized 如何保证可见性？

1\. 获取锁时，强制刷新主内存（Load Memory Barrier, LoadFence）：

* 线程获取 synchronized 锁时，会强制从主内存中读取最新的变量值，避免读取 CPU 缓存中的过期数据。

2\. 释放锁时，强制刷回主内存（Store Memory Barrier, StoreFence）：

* 线程释放 synchronized 锁时，会强制将修改后的变量值刷回主内存，其他线程获取该锁时会重新读取最新的值。

#### 结论：

* synchronized 保证变量在不同线程间的可见性，确保数据一致。

## 3. synchronized 如何保证有序性？

有序性（Orderliness） 指的是 程序执行的顺序按照代码的书写顺序进行，不会被 CPU 乱序优化（Reordering）。

synchronized 通过 内存屏障（Memory Barrier） + Happens-Before 规则 来保证指令不会被重排序。

#### 示例

```java
class OrderExample {
    private int a = 0, b = 0;

    public synchronized void method1() {
        a = 1; // 1️⃣
        b = 2; // 2️⃣
    }

    public synchronized void method2() {
        int x = b; // 3️⃣
        int y = a; // 4️⃣
        System.out.println("x=" + x + ", y=" + y);
    }
}
```

synchronized 如何保证有序性？

1\. Java 内存模型（JMM）会对指令进行重排序，但 synchronized 保证同一线程内的代码顺序不会被乱序优化。

2\. synchronized 通过 Happens-Before 规则 保证有序性：

* 锁释放 (monitorexit) 先于 下一个线程获取锁 (monitorenter)，保证指令执行的顺序性。

## 4.结论

* synchronized 禁止指令重排序，保证代码按顺序执行。

| 特性  | synchronized 如何保证？      | 实现机制                       |
| --- | ----------------------- | -------------------------- |
| 原子性 | 线程获取锁后，独占资源，执行完毕后释放锁    | monitorenter / monitorexit |
| 可见性 | 获取锁时强制从主内存加载数据，释放锁时写回主存 | JMM 规定 synchronized 变量必须刷新 |
| 有序性 | 禁止指令重排序，保证代码按写入顺序执行     | 内存屏障（Memory Barrier）       |

最佳实践

1\. 在并发环境下，保证线程安全时，推荐使用 synchronized 来确保 原子性、可见性和有序性。

2\. volatile 仅能保证可见性和有序性，但不能保证原子性，因此 synchronized 更加强大。

3\. 高并发场景下，如果需要可中断锁、超时获取锁，可以使用 ReentrantLock 替代 synchronized。
