---
cover: >-
  https://images.unsplash.com/photo-1735786115686-7b707ef43dce?crop=entropy&cs=srgb&fm=jpg&ixid=M3wxOTcwMjR8MHwxfHJhbmRvbXx8fHx8fHx8fDE3NDAxMjQ5NTF8&ixlib=rb-4.0.3&q=85
coverY: 0
---

# JUC线程池: FutureTask详解

## 1.FutureTask简介 <a href="#futuretask-jian-jie" id="futuretask-jian-jie"></a>

FutureTask 为 Future 提供了基础实现，如获取任务执行结果(get)和取消任务(cancel)等。如果任务尚未完成，获取任务执行结果时将会阻塞。一旦执行结束，任务就不能被重启或取消(除非使用runAndReset执行计算)。FutureTask 常用来封装 Callable 和 Runnable，也可以作为一个任务提交到线程池中执行。除了作为一个独立的类之外，此类也提供了一些功能性函数供我们创建自定义 task 类使用。FutureTask 的线程安全由CAS来保证。



## 2.类关系 <a href="#futuretask-lei-guan-xi" id="futuretask-lei-guan-xi"></a>

<figure><img src="../../.gitbook/assets/image (4).png" alt=""><figcaption></figcaption></figure>

## 3.FutureTask源码解析 <a href="#futuretask-yuan-ma-jie-xi" id="futuretask-yuan-ma-jie-xi"></a>

### 3.1Callable接口

Callable是个泛型接口，泛型V就是要call()方法返回的类型。对比Runnable接口，Runnable不会返回数据也不能抛出异常。

```java
@FunctionalInterface
public interface Callable<V> {
    /**
     * Computes a result, or throws an exception if unable to do so.
     *
     * @return computed result
     * @throws Exception if unable to compute a result
     */
    V call() throws Exception;
}
```

### 3.2Future接口

Future接口代表异步计算的结果，通过Future接口提供的方法可以查看异步计算是否执行完成，或者等待执行结果并获取执行结果，同时还可以取消执行。Future接口的定义如下:

```java
public interface Future<V> {
    boolean cancel(boolean mayInterruptIfRunning);
    boolean isCancelled();
    boolean isDone();
    V get() throws InterruptedException, ExecutionException;
    V get(long timeout, TimeUnit unit)
        throws InterruptedException, ExecutionException, TimeoutException;
}
```

* cancel():用来取消异步任务的执行
* isCanceled():判断任务是否被取消，如果任务在结束(正常执行结束或者执行异常结束)前被取消则返回true，否则返回false。
* isDone():判断任务是否已经完成，如果完成则返回true，否则返回false。需要注意的是：任务执行过程中发生异常、任务被取消也属于任务已完成，也会返回true。
* get():获取任务执行结果，如果任务还没完成则会阻塞等待直到任务执行完成。
* get(long timeout,Timeunit unit):带超时时间的get()版本，如果阻塞等待过程中超时则会抛出TimeoutException异常

### 3.3核心属性

```java
//内部持有的callable任务，运行完毕后置空
private Callable<V> callable;

//从get()中返回的结果或抛出的异常
private Object outcome; // non-volatile, protected by state reads/writes

//运行callable的线程
private volatile Thread runner;

//使用Treiber栈保存等待线程
private volatile WaitNode waiters;

//任务状态
private volatile int state;
private static final int NEW          = 0;
private static final int COMPLETING   = 1;
private static final int NORMAL       = 2;
private static final int EXCEPTIONAL  = 3;
private static final int CANCELLED    = 4;
private static final int INTERRUPTING = 5;
private static final int INTERRUPTED  = 6;
```

其中需要注意的是state是volatile类型的，也就是说只要有任何一个线程修改了这个变量，那么其他所有的线程都会知道最新的值。7种状态具体表示：

* NEW:表示是个新的任务或者还没被执行完的任务。这是初始状态。
* COMPLETING:任务已经执行完成或者执行任务的时候发生异常，但是任务执行结果或者异常原因还没有保存到outcome字段(outcome字段用来保存任务执行结果，如果发生异常，则用来保存异常原因)的时候，状态会从NEW变更到COMPLETING。但是这个状态会时间会比较短，属于中间状态。
* NORMAL:任务已经执行完成并且任务执行结果已经保存到outcome字段，状态会从COMPLETING转换到NORMAL。这是一个最终态
* EXCEPTIONAL:任务执行发生异常并且异常原因已经保存:到outcome字段中后，状态会从COMPLETING转换到EXCEPTIONAL。这是一个最终态。
* CANCELLED:任务还没开始执行或者已经开始执行但是还没有执行完成的时候，用户调用了cancel(false)方法取消任务且不中断任务执行线程，这个时候状态会从NEW转化为CANCELLED状态。这是一个最终态。
* INTERRUPTING:任务还没开始执行或者已经执行但是还没有执行完成的时候，用户调用了cancel(true)方法取消任务并且要中断任务执行线程但是还没有中断任务执行线程之前，状态会从NEW转化为INTERRUPTING。这是一个中间状态。
* INTERRUPTED:调用interrupt()中断任务执行线程之后状态会从INTERRUPTING转换到INTERRUPTED。这是一个最终态。 有一点需要注意的是，所有值大于COMPLETING的状态都表示任务已经执行完成(任务正常执行完成，任务执行异常或者任务被取消)。

各个状态之间的可能转换关系如下图所示:

![](<../../.gitbook/assets/image (6).png>)

### &#x20;3.4构造函数

* FutureTask(Callable\<V> callable)

```java
public FutureTask(Callable<V> callable) {
    if (callable == null)
        throw new NullPointerException();
    this.callable = callable;
    this.state = NEW;       // ensure visibility of callable
}
```

这个构造函数会把传入的Callable变量保存在this.callable字段中，该字段定义为`private Callable<V> callable`;用来保存底层的调用，在被执行完成以后会指向null,接着会初始化state字段为NEW。

* FutureTask(Runnable runnable, V result)

```java
public FutureTask(Runnable runnable, V result) {
    this.callable = Executors.callable(runnable, result);
    this.state = NEW;       // ensure visibility of callable
}
```

这个构造函数会把传入的Runnable封装成一个Callable对象保存在callable字段中，同时如果任务执行成功的话就会返回传入的result。这种情况下如果不需要返回值的话可以传入一个null。

顺带看下Executors.callable()这个方法，这个方法的功能是把Runnable转换成Callable，代码如下:

```java
public static <T> Callable<T> callable(Runnable task, T result) {
    if (task == null)
       throw new NullPointerException();
    return new RunnableAdapter<T>(task, result);
}
```

可以看到这里采用的是适配器模式，调用`RunnableAdapter<T>(task, result)`方法来适配，实现如下:

```java
static final class RunnableAdapter<T> implements Callable<T> {
    final Runnable task;
    final T result;
    RunnableAdapter(Runnable task, T result) {
        this.task = task;
        this.result = result;
    }
    public T call() {
        task.run();
        return result;
    }
}
```

个适配器很简单，就是简单的实现了Callable接口，在call()实现中调用Runnable.run()方法，然后把传入的result作为任务的结果返回。

在new了一个FutureTask对象之后，接下来就是在另一个线程中执行这个Task,无论是通过直接new一个Thread还是通过线程池，执行的都是run()方法，接下来就看看run()方法的实现。

### 3.5核心方法 - run()

```java
public void run() {
    //新建任务，CAS替换runner为当前线程
    if (state != NEW ||
        !UNSAFE.compareAndSwapObject(this, runnerOffset,
                                     null, Thread.currentThread()))
        return;
    try {
        Callable<V> c = callable;
        if (c != null && state == NEW) {
            V result;
            boolean ran;
            try {
                result = c.call();
                ran = true;
            } catch (Throwable ex) {
                result = null;
                ran = false;
                setException(ex);
            }
            if (ran)
                set(result);//设置执行结果
        }
    } finally {
        // runner must be non-null until state is settled to
        // prevent concurrent calls to run()
        runner = null;
        // state must be re-read after nulling runner to prevent
        // leaked interrupts
        int s = state;
        if (s >= INTERRUPTING)
            handlePossibleCancellationInterrupt(s);//处理中断逻辑
    }
}
```

**说明：**

* 运行任务，如果任务状态为NEW状态，则利用CAS修改为当前线程。执行完毕调用set(result)方法设置执行结果。set(result)源码如下：

```java
protected void set(V v) {
    if (UNSAFE.compareAndSwapInt(this, stateOffset, NEW, COMPLETING)) {
        outcome = v;
        UNSAFE.putOrderedInt(this, stateOffset, NORMAL); // final state
        finishCompletion();//执行完毕，唤醒等待线程
    }
}
```

* 首先利用cas修改state状态为COMPLETING，设置返回结果，然后使用 lazySet(UNSAFE.putOrderedInt)的方式设置state状态为NORMAL。结果设置完毕后，调用finishCompletion()方法唤醒等待线程，源码如下：

```java
private void finishCompletion() {
    // assert state > COMPLETING;
    for (WaitNode q; (q = waiters) != null;) {
        if (UNSAFE.compareAndSwapObject(this, waitersOffset, q, null)) {//移除等待线程
            for (;;) {//自旋遍历等待线程
                Thread t = q.thread;
                if (t != null) {
                    q.thread = null;
                    LockSupport.unpark(t);//唤醒等待线程
                }
                WaitNode next = q.next;
                if (next == null)
                    break;
                q.next = null; // unlink to help gc
                q = next;
            }
            break;
        }
    }
    //任务完成后调用函数，自定义扩展
    done();

    callable = null;        // to reduce footprint
}
```

* 回到run方法，如果在 run 期间被中断，此时需要调用handlePossibleCancellationInterrupt方法来处理中断逻辑，确保任何中断(例如cancel(true))只停留在当前run或runAndReset的任务中，源码如下：

```java
private void handlePossibleCancellationInterrupt(int s) {
    //在中断者中断线程之前可能会延迟，所以我们只需要让出CPU时间片自旋等待
    if (s == INTERRUPTING)
        while (state == INTERRUPTING)
            Thread.yield(); // wait out pending interrupt
}
```

### 3.6核心方法 - get() <a href="#he-xin-fang-fa-get" id="he-xin-fang-fa-get"></a>

```java
//获取执行结果
public V get() throws InterruptedException, ExecutionException {
    int s = state;
    if (s <= COMPLETING)
        s = awaitDone(false, 0L);
    return report(s);
}
```

说明：FutureTask 通过get()方法获取任务执行结果。如果任务处于未完成的状态(`state <= COMPLETING`)，就调用awaitDone方法(后面单独讲解)等待任务完成。任务完成后，通过report方法获取执行结果或抛出执行期间的异常。report源码如下：

```java
//返回执行结果或抛出异常
private V report(int s) throws ExecutionException {
    Object x = outcome;
    if (s == NORMAL)
        return (V)x;
    if (s >= CANCELLED)
        throw new CancellationException();
    throw new ExecutionException((Throwable)x);
}
```

### 3.7核心方法 - awaitDone(boolean timed, long nanos) <a href="#he-xin-fang-fa-awaitdonebooleantimedlongnanos" id="he-xin-fang-fa-awaitdonebooleantimedlongnanos"></a>

```java
public boolean cancel(boolean mayInterruptIfRunning) {
    //如果当前Future状态为NEW，根据参数修改Future状态为INTERRUPTING或CANCELLED
    if (!(state == NEW &&
          UNSAFE.compareAndSwapInt(this, stateOffset, NEW,
              mayInterruptIfRunning ? INTERRUPTING : CANCELLED)))
        return false;
    try {    // in case call to interrupt throws exception
        if (mayInterruptIfRunning) {//可以在运行时中断
            try {
                Thread t = runner;
                if (t != null)
                    t.interrupt();
            } finally { // final state
                UNSAFE.putOrderedInt(this, stateOffset, INTERRUPTED);
            }
        }
    } finally {
        finishCompletion();//移除并唤醒所有等待线程
    }
    return true;
}
```

说明：尝试取消任务。如果任务已经完成或已经被取消，此操作会失败。

* 如果当前Future状态为NEW，根据参数修改Future状态为INTERRUPTING或CANCELLED。
*   如果当前状态不为NEW，则根据参数mayInterruptIfRunning决定是否在任务运行中也可以中断。中断操作完成后，调用finishCompletion移除并唤醒所有等待线程。



## 4.FutureTask示例

下面演示了使用 FutureTask 的三种常见方式示例，分别是：

1. Future + ExecutorService
2. FutureTask + ExecutorService
3. FutureTask + Thread

### 1. Future + ExecutorService

这是最常见的做法，直接通过 ExecutorService 提交一个实现了 Callable 接口的任务，返回一个 Future 对象。

```java
import java.util.concurrent.*;

public class FutureExample {
    public static void main(String[] args) {
        // 1. 创建线程池
        ExecutorService executor = Executors.newFixedThreadPool(1);

        // 2. 提交Callable任务，得到Future
        Future<String> future = executor.submit(() -> {
            // 模拟耗时操作
            Thread.sleep(1000);
            return "Result from Future";
        });

        // 3. 可以在此执行其他操作
        System.out.println("Doing other tasks...");

        try {
            // 4. 通过future.get()等待任务执行完毕并获取结果
            String result = future.get();
            System.out.println("Result: " + result);
        } catch (InterruptedException | ExecutionException e) {
            e.printStackTrace();
        }

        // 5. 关闭线程池
        executor.shutdown();
    }
}
```

要点：

• 使用 submit(Callable) 提交任务后，立即返回 Future 对象，后续可通过 future.get() 获取结果或执行取消操作。

• 任务的执行依赖线程池来管理。

### 2. FutureTask + ExecutorService

FutureTask 同样实现了 Future 和 Runnable，可以将其作为一个可执行任务提交给线程池。

```java
import java.util.concurrent.*;

public class FutureTaskWithExecutorExample {
    public static void main(String[] args) {
        // 1. 创建线程池
        ExecutorService executor = Executors.newFixedThreadPool(1);

        // 2. 创建FutureTask
        FutureTask<String> futureTask = new FutureTask<>(() -> {
            Thread.sleep(1000);
            return "Result from FutureTask";
        });

        // 3. 提交FutureTask给线程池
        executor.submit(futureTask);

        // 4. 可以在此执行其他操作
        System.out.println("Doing other tasks...");

        try {
            // 5. 等待任务执行完毕并获取结果
            String result = futureTask.get();
            System.out.println("Result: " + result);
        } catch (InterruptedException | ExecutionException e) {
            e.printStackTrace();
        }

        // 6. 关闭线程池
        executor.shutdown();
    }
}
```

要点：

• FutureTask 是 Runnable 的实现类，也实现了 Future，可以提交给任何需要 Runnable 的地方（如线程池）。

• 和直接提交 Callable 获得 Future 的区别在于，这里我们可以直接对 FutureTask 做更多控制（比如手动调用 run()、取消、状态判断等）。

### 3. FutureTask + Thread

如果不想使用线程池，也可以直接用 FutureTask + Thread 的方式启动线程：

```java
import java.util.concurrent.*;

public class FutureTaskWithThreadExample {
    public static void main(String[] args) {
        // 1. 创建FutureTask
        FutureTask<String> futureTask = new FutureTask<>(() -> {
            Thread.sleep(1000);
            return "Result from FutureTask + Thread";
        });

        // 2. 用Thread来执行FutureTask
        Thread thread = new Thread(futureTask);
        thread.start();

        // 3. 可以在此执行其他操作
        System.out.println("Doing other tasks...");

        try {
            // 4. 等待任务执行完毕并获取结果
            String result = futureTask.get();
            System.out.println("Result: " + result);
        } catch (InterruptedException | ExecutionException e) {
            e.printStackTrace();
        }
    }
}
```

要点：

• FutureTask 既可以提交给线程池，也可单独作为一个任务由 Thread 来执行。

• 不依赖线程池时，需要自行管理线程的创建与销毁。

总结

• Future + ExecutorService：最常见的异步编程方式，通过线程池提交 Callable 任务，得到 Future。

• FutureTask + ExecutorService：FutureTask 兼具 Runnable 与 Future 特性，可灵活地进行任务的提交、取消与结果获取。

• FutureTask + Thread：适用于无需线程池、单独启动一个线程来执行任务的场景。

三种方式都能实现异步执行并获取执行结果，核心区别主要在于对线程的管理方式（线程池 vs. 手动创建）以及对任务控制的灵活度。

\
