---
cover: >-
  https://images.unsplash.com/photo-1737385024749-ed2c9fac24cb?crop=entropy&cs=srgb&fm=jpg&ixid=M3wxOTcwMjR8MHwxfHJhbmRvbXx8fHx8fHx8fDE3NDAyMzU2OTN8&ixlib=rb-4.0.3&q=85
coverY: 0
---

# GC（垃圾回收）检测垃圾的方法

Java 垃圾回收（GC）需要 **确定哪些对象是垃圾**，然后释放内存。

JVM 主要通过以下 **两种垃圾检测算法** 来判断对象是否存活：

1. 引用计数法（Reference Counting）
2. 可达性分析法（Reachability Analysis，GC Root Tracing）

## 1. 引用计数法（Reference Counting，已淘汰）

机制

* 每个对象 有一个引用计数器，引用时 +1，释放时 -1。
* 计数为 0 的对象是垃圾，可被回收。&#x20;

### 示例

```java
public class ReferenceCountingGC {
    private Object instance;
    
    public static void main(String[] args) {
        ReferenceCountingGC obj1 = new ReferenceCountingGC();
        ReferenceCountingGC obj2 = new ReferenceCountingGC();
        
        obj1.instance = obj2; // obj1 引用 obj2
        obj2.instance = obj1; // obj2 引用 obj1

        obj1 = null;
        obj2 = null;

        System.gc(); // 理论上应该回收 obj1 和 obj2
    }
}
```

问题

* 无法检测循环引用：
* obj1 -> obj2 -> obj1，但 obj1 和 obj2 计数不为 0，导致无法回收。
* JVM 已淘汰此方法，现代 GC 使用可达性分析法。

## 2. 可达性分析法（Reachability Analysis，GC Root Tracing）

机制

* 从 GC Root 开始遍历，标记所有可达对象。
* 未被标记的对象 视为垃圾，进入垃圾回收阶段。

### GC Root

| GC Root 类型      | 说明                        |
| --------------- | ------------------------- |
| 栈帧中的局部变量        | 方法执行时的栈变量（如 main() 里的变量）。 |
| 方法区中的静态变量       | 类静态变量（static 变量）。         |
| 方法区中的常量引用       | 常量池中的引用，如字符串常量。           |
| JNI 引用的对象（本地方法） | 通过 JNI 连接的 C 代码对象。        |
| 正在执行的线程         | 存活线程不被 GC 释放。             |

### 示例

```java
public class ReachabilityAnalysis {
    private static Object gcRoot; // GC Root

    public static void main(String[] args) {
        ReachabilityAnalysis obj = new ReachabilityAnalysis();
        gcRoot = obj; // obj 由 GC Root 引用，不会被回收
        obj = null;
        System.gc(); // 这里不会回收 obj
    }
}
```

特点

* 避免循环引用问题（obj1 -> obj2 -> obj1 仍然可回收）。
* 现代 JVM GC 采用此方法。

## 3. GC 处理对象的方式

当 GC 发现 对象不可达，它不会立即回收，而是 执行以下步骤：

1\. 标记阶段（Mark）：

* 使用 可达性分析 标记存活对象。

2\. 筛选对象：

* 可达对象：不会被回收。
* 可疑对象：

&#x20;        • 若对象实现 finalize() 方法，进入 F-Queue，等待执行 finalize()。

&#x20;        • 执行 finalize() 后仍不可达，则被回收。

### 示例

```java
public class FinalizeTest {
    private static FinalizeTest instance;

    @Override
    protected void finalize() throws Throwable {
        super.finalize();
        System.out.println("finalize() 被调用");
        instance = this; // 复活对象
    }

    public static void main(String[] args) {
        instance = new FinalizeTest();
        instance = null;

        System.gc(); // 触发 GC

        if (instance != null) {
            System.out.println("对象存活");
        } else {
            System.out.println("对象被回收");
        }
    }
}
```

可能的输出

```
finalize() 被调用
对象存活
```

finalize() 只会执行一次，下一次 GC 仍然不可达就会被回收。

## 4. 引用类型判断存活

Java 提供 四种引用类型，决定对象的存活方式：

| 引用类型                   | 回收条件       | 示例                                                                          |
| ---------------------- | ---------- | --------------------------------------------------------------------------- |
| 强引用（Strong Reference）  | 永不回收       | Object obj = new Object();                                                  |
| 软引用（Soft Reference）    | 仅在内存不足时回收  | SoftReference\<Object> sr = new SoftReference<>(new Object());              |
| 弱引用（Weak Reference）    | 发生 GC 就会回收 | WeakReference\<Object> wr = new WeakReference<>(new Object());              |
| 虚引用（Phantom Reference） | 仅用于监控对象回收  | PhantomReference\<Object> pr = new PhantomReference<>(new Object(), queue); |

### 示例

```java
import java.lang.ref.*;

public class ReferenceTypes {
    public static void main(String[] args) {
        WeakReference<Object> weakRef = new WeakReference<>(new Object());
        System.gc();
        System.out.println(weakRef.get()); // 可能输出 null
    }
}
```

⚠️ 弱引用 get() 可能返回 null，因为 GC 已回收对象。

## 5. 现代 GC 如何回收垃圾

### 5.1 Minor GC（年轻代 GC）

* Eden 区满了，触发 Minor GC，存活对象移入 Survivor 区。
* 对象晋升老年代：

&#x20;           • 在 Survivor 存活多次（MaxTenuringThreshold 次数）。

&#x20;           • Survivor 无法容纳对象。

### 5.2 Major GC / Full GC（老年代 GC）

* 老年代满了，触发 Full GC。
* 触发条件：

&#x20;          • System.gc()

&#x20;          • Minor GC 后晋升失败

&#x20;          • Metaspace 满了

* 执行 Full GC 的 GC：

&#x20;          • Serial Old

&#x20;          • CMS

&#x20;          • G1

### 5.3 ZGC 和 Shenandoah GC

* 超低延迟，可在 GC 过程中 不暂停应用线程。

## 6. 总结

✅ JVM 主要使用 可达性分析法（Reachability Analysis）检测垃圾对象。

✅ 现代 JVM GC 不使用 引用计数法，避免循环引用问题。

✅ GC 处理对象时，先执行 finalize()，对象有机会复活。

✅ JVM 提供 强引用、软引用、弱引用、虚引用 影响 GC 过程。

✅ GC 主要分为 Minor GC（年轻代）和 Full GC（老年代）。 🚀
