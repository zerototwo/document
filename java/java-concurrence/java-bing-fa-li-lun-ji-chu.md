---
cover: >-
  https://images.unsplash.com/photo-1737222561123-269af6be3e15?crop=entropy&cs=srgb&fm=jpg&ixid=M3wxOTcwMjR8MHwxfHJhbmRvbXx8fHx8fHx8fDE3Mzk4MDQwNTB8&ixlib=rb-4.0.3&q=85
coverY: 0
---

# Java 并发 - 理论基础

* 多线程的出现是要解决什么问题的?
* 线程不安全是指什么? 举例说明
* 并发出现线程不安全的本质什么? 可见性，原子性和有序性。
* Java是怎么解决并发问题的? 3个关键字，JMM和8个Happens-Before
* 线程安全是不是非真即假? 不是
* 线程安全有哪些实现思路?
* 如何理解并发和并行的区别?

## 1.为什么需要多线程 <a href="#wei-shen-me-xu-yao-duo-xian-cheng" id="wei-shen-me-xu-yao-duo-xian-cheng"></a>

众所周知，CPU、内存、I/O 设备的速度是有极大差异的，为了合理利用 CPU 的高性能，平衡这三者的速度差异，计算机体系结构、操作系统、编译程序都做出了贡献，主要体现为:

* CPU 增加了缓存，以均衡与内存的速度差异；**导致** `可见性`问题
* 操作系统增加了进程、线程，以分时复用 CPU，进而均衡 CPU 与 I/O 设备的速度差异；**导致** `原子性`问题
* 编译程序优化指令执行次序，使得缓存能够得到更加合理地利用。**导致** `有序性`问题

## 2.线程不安全示例

如果多个线程对同一个共享数据进行访问而不采取同步操作的话，那么操作的结果是不一致的。

以下代码演示了 1000 个线程同时对 cnt 执行自增操作，操作结束之后它的值有可能小于 1000。\


```java
public class ThreadUnsafeExample {

    private int cnt = 0;

    public void add() {
        cnt++;
    }

    public int get() {
        return cnt;
    }
}
```

```java
public static void main(String[] args) throws InterruptedException {
    final int threadSize = 1000;
    ThreadUnsafeExample example = new ThreadUnsafeExample();
    final CountDownLatch countDownLatch = new CountDownLatch(threadSize);
    ExecutorService executorService = Executors.newCachedThreadPool();
    for (int i = 0; i < threadSize; i++) {
        executorService.execute(() -> {
            example.add();
            countDownLatch.countDown();
        });
    }
    countDownLatch.await();
    executorService.shutdown();
    System.out.println(example.get());
}
```

结果

```
997
```

## 3.并发出现问题的根源: 并发三要素 <a href="#bing-fa-chu-xian-wen-ti-de-gen-yuan-bing-fa-san-yao-su" id="bing-fa-chu-xian-wen-ti-de-gen-yuan-bing-fa-san-yao-su"></a>

上述代码输出为什么不是1000? 并发出现问题的根源是什么?

### 3.1可见性: CPU缓存引起 <a href="#ke-jian-xing-cpu-huan-cun-yin-qi" id="ke-jian-xing-cpu-huan-cun-yin-qi"></a>

可见性：一个线程对共享变量的修改，另外一个线程能够立刻看到。

举个简单的例子，看下面这段代码：

```
//线程1执行的代码
int i = 0;
i = 10;
 
//线程2执行的代码
j = i;
```

假若执行线程1的是CPU1，执行线程2的是CPU2。由上面的分析可知，当线程1执行 i =10这句时，会先把i的初始值加载到CPU1的高速缓存中，然后赋值为10，那么在CPU1的高速缓存当中i的值变为10了，却没有立即写入到主存当中。

此时线程2执行 j = i，它会先去主存读取i的值并加载到CPU2的缓存当中，注意此时内存当中i的值还是0，那么就会使得j的值为0，而不是10.

这就是可见性问题，线程1对变量i修改了之后，线程2没有立即看到线程1修改的值。

### 3.2原子性: 分时复用引起

原子性：即一个操作或者多个操作 要么全部执行并且执行的过程不会被任何因素打断，要么就都不执行。

举个简单的例子，看下面这段代码：

```java
int i = 1;

// 线程1执行
i += 1;

// 线程2执行
i += 1;
```

这里需要注意的是：`i += 1`需要三条 CPU 指令

1. 将变量 i 从内存读取到 CPU寄存器；
2. 在CPU寄存器中执行 i + 1 操作；
3. 将最后的结果i写入内存（缓存机制导致可能写入的是 CPU 缓存而不是内存）。

由于CPU分时复用（线程切换）的存在，线程1执行了第一条指令后，就切换到线程2执行，假如线程2执行了这三条指令后，再切换会线程1执行后续两条指令，将造成最后写到内存中的i值是2而不是3。

### 3.3有序性: 重排序引起

有序性：即程序执行的顺序按照代码的先后顺序执行。举个简单的例子，看下面这段代码：

```java
int i = 0;              
boolean flag = false;
i = 1;                //语句1  
flag = true;          //语句2
```

上面代码定义了一个int型变量，定义了一个boolean类型变量，然后分别对两个变量进行赋值操作。从代码顺序上看，语句1是在语句2前面的，那么JVM在真正执行这段代码的时候会保证语句1一定会在语句2前面执行吗? 不一定，为什么呢? 这里可能会发生指令重排序（Instruction Reorder）。

在执行程序时为了提高性能，编译器和处理器常常会对指令做重排序。重排序分三种类型：

* 编译器优化的重排序。编译器在不改变单线程程序语义的前提下，可以重新安排语句的执行顺序。
* 指令级并行的重排序。现代处理器采用了指令级并行技术（Instruction-Level Parallelism， ILP）来将多条指令重叠执行。如果不存在数据依赖性，处理器可以改变语句对应机器指令的执行顺序。
* 内存系统的重排序。由于处理器使用缓存和读 / 写缓冲区，这使得加载和存储操作看上去可能是在乱序执行。

从 java 源代码到最终实际执行的指令序列，会分别经历下面三种重排序：

<figure><img src="../../.gitbook/assets/image.png" alt=""><figcaption></figcaption></figure>

上述的 1 属于编译器重排序，2 和 3 属于处理器重排序。这些重排序都可能会导致多线程程序出现内存可见性问题。对于编译器，JMM 的编译器重排序规则会禁止特定类型的编译器重排序（不是所有的编译器重排序都要禁止）。对于处理器重排序，JMM 的处理器重排序规则会要求 java 编译器在生成指令序列时，插入特定类型的内存屏障（memory barriers，intel 称之为 memory fence）指令，通过内存屏障指令来禁止特定类型的处理器重排序（不是所有的处理器重排序都要禁止）。

## 4.JAVA是怎么解决并发问题的: JMM(Java内存模型) <a href="#java-shi-zen-me-jie-jue-bing-fa-wen-ti-de-jmmjava-nei-cun-mo-xing" id="java-shi-zen-me-jie-jue-bing-fa-wen-ti-de-jmmjava-nei-cun-mo-xing"></a>

### **4.1知识点**

JMM本质上可以理解为，Java 内存模型规范了 JVM 如何提供按需禁用缓存和编译优化的方法。具体来说，这些方法包括：

* volatile、synchronized 和 final 三个关键字
* Happens-Before 规则

### **4.2可见性，有序性，原子性**

* 原子性

在Java中，对基本数据类型的变量的读取和赋值操作是原子性操作，即这些操作是不可被中断的，要么执行，要么不执行。 请分析以下哪些操作是原子性操作：

```java
x = 10;        //语句1: 直接将数值10赋值给x，也就是说线程执行这个语句的会直接将数值10写入到工作内存中
y = x;         //语句2: 包含2个操作，它先要去读取x的值，再将x的值写入工作内存，虽然读取x的值以及 将x的值写入工作内存 这2个操作都是原子性操作，但是合起来就不是原子性操作了。
x++;           //语句3： x++包括3个操作：读取x的值，进行加1操作，写入新的值。
x = x + 1;     //语句4： 同语句3
```

上面4个语句只有语句1的操作具备原子性。

也就是说，只有简单的读取、赋值（而且必须是将数字赋值给某个变量，变量之间的相互赋值不是原子操作）才是原子操作。

从上面可以看出，Java内存模型只保证了基本读取和赋值是原子性操作，如果要实现更大范围操作的原子性，可以通过synchronized和Lock来实现。由于synchronized和Lock能够保证任一时刻只有一个线程执行该代码块，那么自然就不存在原子性问题了，从而保证了原子性。

* 可见性

Java提供了volatile关键字来保证可见性。

当一个共享变量被volatile修饰时，它会保证修改的值会立即被更新到主存，当有其他线程需要读取时，它会去内存中读取新值。

而普通的共享变量不能保证可见性，因为普通共享变量被修改之后，什么时候被写入主存是不确定的，当其他线程去读取时，此时内存中可能还是原来的旧值，因此无法保证可见性。

另外，通过synchronized和Lock也能够保证可见性，synchronized和Lock能保证同一时刻只有一个线程获取锁然后执行同步代码，并且在释放锁之前会将对变量的修改刷新到主存当中。因此可以保证可见性。

* 有序性

在Java里面，可以通过volatile关键字来保证一定的“有序性”（具体原理在下一节讲述）。另外可以通过synchronized和Lock来保证有序性，很显然，synchronized和Lock保证每个时刻是有一个线程执行同步代码，相当于是让线程顺序执行同步代码，自然就保证了有序性。当然JMM是通过Happens-Before 规则来保证有序性的。



## 5.关键字: volatile、synchronized 和 final <a href="#guan-jian-zi-volatilesynchronized-he-final" id="guan-jian-zi-volatilesynchronized-he-final"></a>

* [关键字: synchronized详解](https://pdai.tech/md/java/thread/java-thread-x-key-synchronized.html)
* [关键字: volatile详解](https://pdai.tech/md/java/thread/java-thread-x-key-volatile.html)
* [关键字: final详解](https://pdai.tech/md/java/thread/java-thread-x-key-final.html)

### 5.1Happens-Before 规则 <a href="#happensbefore-gui-ze" id="happensbefore-gui-ze"></a>

上面提到了可以用 volatile 和 synchronized 来保证有序性。除此之外，JVM 还规定了先行发生原则，让一个操作无需控制就能先于另一个操作完成。

#### 5.1.1**单一线程原则**

在一个线程内，在程序前面的操作先行发生于后面的操作。\
![](<../../.gitbook/assets/image (1).png>)

\


#### 5.1.2**管程锁定规则**

#### 一个 unlock 操作先行发生于后面对同一个锁的 lock 操作。

#### <img src="../../.gitbook/assets/image (2).png" alt="" data-size="original"> 

#### 5.1.3**volatile 变量规则**

对一个 volatile 变量的写操作先行发生于后面对这个变量的读操作。

<img src="../../.gitbook/assets/image (3).png" alt="" data-size="original">

\
5.1.4**线程启动规则**

Thread 对象的 start() 方法调用先行发生于此线程的每一个动作。

<figure><img src="../../.gitbook/assets/image (4).png" alt=""><figcaption></figcaption></figure>

#### **5.1.5线程加入规则**

Thread 对象的结束先行发生于 join() 方法返回。

<figure><img src="../../.gitbook/assets/image (5).png" alt=""><figcaption></figcaption></figure>

#### 5.1.6**线程中断规则**

对线程 interrupt() 方法的调用先行发生于被中断线程的代码检测到中断事件的发生，可以通过 interrupted() 方法检测到是否有中断发生。

#### 5.1.7**对象终结规则**

一个对象的初始化完成(构造函数执行结束)先行发生于它的 finalize() 方法的开始。

#### 5.1.8传递性

如果操作 A 先行发生于操作 B，操作 B 先行发生于操作 C，那么操作 A 先行发生于操作 C。\


## 6.线程安全: 不是一个非真即假的命题 <a href="#xian-cheng-an-quan-bu-shi-yi-ge-fei-zhen-ji-jia-de-ming-ti" id="xian-cheng-an-quan-bu-shi-yi-ge-fei-zhen-ji-jia-de-ming-ti"></a>

一个类在可以被多个线程安全调用时就是线程安全的。

线程安全不是一个非真即假的命题，可以将共享数据按照安全程度的强弱顺序分成以下五类: 不可变、绝对线程安全、相对线程安全、线程兼容和线程对立。

### 1.不可变 <a href="#id-1-bu-ke-bian" id="id-1-bu-ke-bian"></a>

不可变(Immutable)的对象一定是线程安全的，不需要再采取任何的线程安全保障措施。只要一个不可变的对象被正确地构建出来，永远也不会看到它在多个线程之中处于不一致的状态。

多线程环境下，应当尽量使对象成为不可变，来满足线程安全。

不可变的类型:

* final关键字修饰的基本数据类型
* String
* 枚举类型
* Number 部分子类，如 Long 和 Double 等数值包装类型，BigInteger 和 BigDecimal 等大数据类型。但同为 Number 的原子类 AtomicInteger 和 AtomicLong 则是可变的。

对于集合类型，可以使用 Collections.unmodifiableXXX() 方法来获取一个不可变的集合。

```java
public class ImmutableExample {
    public static void main(String[] args) {
        Map<String, Integer> map = new HashMap<>();
        Map<String, Integer> unmodifiableMap = Collections.unmodifiableMap(map);
        unmodifiableMap.put("a", 1);
    }
}
```

```
Exception in thread "main" java.lang.UnsupportedOperationException
    at java.util.Collections$UnmodifiableMap.put(Collections.java:1457)
    at ImmutableExample.main(ImmutableExample.java:9)
```

Collections.unmodifiableXXX() 先对原始的集合进行拷贝，需要对集合进行修改的方法都直接抛出异常。

```java
public V put(K key, V value) {
    throw new UnsupportedOperationException();
}
```

