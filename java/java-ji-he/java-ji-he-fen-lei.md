---
description: >-
  Java 集合（Java Collections Framework，简称 JCF）是 Java 语言中
  最重要的数据结构之一。它提供了一整套用于存储、操作数据的 通用
  API，使开发者能够轻松管理数据集合，如列表（List）、集合（Set）、队列（Queue）、映射（Map） 等。
cover: >-
  https://images.unsplash.com/photo-1735491428084-853fb91c09e7?crop=entropy&cs=srgb&fm=jpg&ixid=M3wxOTcwMjR8MHwxfHJhbmRvbXx8fHx8fHx8fDE3Mzg0MjU4NDF8&ixlib=rb-4.0.3&q=85
coverY: 0
---

# Java集合分类

## Java 集合框架概述

Java 集合框架的核心是 Collection 接口（及其子接口）和 Map 接口，它们构成了 Java 最常用的数据存储结构。

• Collection：用于存储单个元素的容器，包括 List、Set 和 Queue。

• Map：用于存储键值对，比如 HashMap 和 TreeMap。

### Collection

```mermaid
graph LR;

    %% 🎀 Cute Collection Framework
    subgraph "🎀 Cute Java Collection Framework"
        C1["📦 <b>Collection</b>"]
        C2["📜 <b>List</b>"]
        C3["🔢 <b>Set</b>"]
        C4["📤 <b>Queue</b>"]
    end

    %% 📋 Cute List Implementations
    subgraph "📋 Cute List"
        C2 -->|Implements| L1["📂 <b>ArrayList</b>"]
        C2 -->|Implements| L2["🔗 <b>LinkedList</b>"]
        C2 -->|Implements| L3["📦 <b>Vector</b>"]
        L3 -->|Subclass| L4["📚 <b>Stack</b>"]
        C2 -->|Thread-Safe| L5["🛡 <b>CopyOnWriteArrayList</b>"]
    end

    %% 📌 Cute Set Implementations
    subgraph "📌 Cute Set"
        C3 -->|Implements| S1["♻️ <b>HashSet</b>"]
        C3 -->|Implements| S2["📜 <b>LinkedHashSet</b>"]
        C3 -->|Implements| S3["🌳 <b>SortedSet</b>"]
        S3 -->|Implements| S4["🌲 <b>TreeSet</b>"]
        C3 -->|Thread-Safe| S5["🛡 <b>CopyOnWriteArraySet</b>"]
    end

    %% 🛤 Cute Queue Implementations
    subgraph "🛤 Cute Queue"
        C4 -->|Implements| Q1["🔗 <b>LinkedList</b>"]
        C4 -->|Implements| Q2["📊 <b>PriorityQueue</b>"]
        C4 -->|Thread-Safe| Q3["⚡ <b>ConcurrentLinkedQueue</b>"]
        C4 -->|Thread-Safe| Q4["📥 <b>LinkedBlockingQueue</b>"]
        C4 -->|Thread-Safe| Q5["📤 <b>ArrayBlockingQueue</b>"]
        C4 -->|Thread-Safe| Q6["🎯 <b>PriorityBlockingQueue</b>"]
    end

    %% 🌈 Cute Q版 Styling (可爱风格)
    classDef cuteStyle fill:#FFFAE3,stroke:#FFAC33,stroke-width:3px,rx:15px,ry:15px,shadow:3px,font-size:16px,font-weight:bold;
    classDef listStyle fill:#D6EAF8,stroke:#3498DB,stroke-width:3px,rx:12px,ry:12px,shadow:5px,font-size:16px,font-weight:bold;
    classDef setStyle fill:#FADBD8,stroke:#E74C3C,stroke-width:3px,rx:12px,ry:12px,shadow:5px,font-size:16px,font-weight:bold;
    classDef queueStyle fill:#D5F5E3,stroke:#2ECC71,stroke-width:3px,rx:12px,ry:12px,shadow:5px,font-size:16px,font-weight:bold;

    %% 🎀 Apply Cute Styles
    class C1,C2,C3,C4 cuteStyle;
    class L1,L2,L3,L4,L5 listStyle;
    class S1,S2,S3,S4,S5 setStyle;
    class Q1,Q2,Q3,Q4,Q5,Q6 queueStyle;
```

### Map

```mermaid
graph TD;

    %% 🗂 Cute Java Map
    subgraph "🗂 Cute Java Map"
        M1["📜 <b>Map</b>"]
        M2["🌲 <b>SortedMap</b>"]
        
        M1 -->|Implements| M3["♻️ <b>HashMap</b>"]
        M3 -->|Subclass| M4["📝 <b>LinkedHashMap</b>"]
        M1 -->|Implements| M5["🗑 <b>WeakHashMap</b>"]
        M1 -->|Implements| M6["👥 <b>IdentityHashMap</b>"]
        M1 -->|Thread-Safe| M7["🛡 <b>Hashtable</b>"]
        M1 -->|Thread-Safe| M8["⚡ <b>ConcurrentHashMap</b>"]

        %% 🔥 Fix: SortedMap Implements Map
        M1 -->|Implements| M2
        M2 -->|Implements| M9["🌳 <b>TreeMap</b>"]
    end

    %% 🌈 Cute Styling (Q版可爱风格)
    classDef qStyle fill:#f9f,stroke:#9370DB,stroke-width:3px,rx:15px,ry:15px,shadow:3px,font-size:14px;
    classDef mapStyle fill:#FFFAE3,stroke:#FFAC33,stroke-width:3px,rx:12px,ry:12px,shadow:5px,font-size:16px,font-weight:bold;
    
    %% 🎨 Apply Cute Styles
    class M1,M2 qStyle;
    class M3,M4,M5,M6,M7,M8,M9 mapStyle;
```

## 接口特点

### List

List 允许元素 重复，且有序存储，适用于需要频繁 随机访问 数据的场景。

| 实现类                  | 底层数据结构 | 线程安全   | 特点        |
| -------------------- | ------ | ------ | --------- |
| ArrayList            | 动态数组   | ❌ 不安全  | 查询快、增删慢   |
| LinkedList           | 双向链表   | ❌ 不安全  | 查询慢、增删快   |
| Vector               | 动态数组   | ✅ 线程安全 | 老旧类，不推荐使用 |
| CopyOnWriteArrayList | 动态数组   | ✅ 线程安全 | 适用于 读多写少  |

#### List选型建议

• 查询多、修改少 ➝ ArrayList

• 插入/删除频繁 ➝ LinkedList

• 多线程环境 ➝ CopyOnWriteArrayList

### Set

Set 主要用于存储 唯一值，不允许元素重复，底层通常使用 哈希表或红黑树。

| 实现类                 | 底层结构           | 排序     | 线程安全   |
| ------------------- | -------------- | ------ | ------ |
| HashSet             | HashMap（Key）   | ❌ 无序   | ❌ 不安全  |
| LinkedHashSet       | HashMap + 双向链表 | ✅ 插入顺序 | ❌ 不安全  |
| TreeSet             | 红黑树（TreeMap）   | ✅ 排序   | ❌ 不安全  |
| CopyOnWriteArraySet | 动态数组           | ❌ 无序   | ✅ 线程安全 |

#### Set 选型建议

• 唯一性但无序 ➝ HashSet

• 唯一性且按插入顺序 ➝ LinkedHashSet

• 唯一性且需要排序 ➝ TreeSet

• 线程安全 ➝ CopyOnWriteArraySet

### Queue

Queue 主要用于 先进先出（FIFO） 结构，适合任务调度、消息队列等场景。

| 实现类                   | 底层结构 | 线程安全   | 特点           |
| --------------------- | ---- | ------ | ------------ |
| LinkedList（队列）        | 双向链表 | ❌ 不安全  | 支持 FIFO、LIFO |
| PriorityQueue         | 堆    | ❌ 不安全  | 元素优先级排序      |
| ConcurrentLinkedQueue | 链表   | ✅ 线程安全 | 无锁并发队列       |
| LinkedBlockingQueue   | 链表   | ✅ 线程安全 | 支持容量限制       |
| ArrayBlockingQueue    | 链表   | ✅ 线程安全 | 定长阻塞队列       |

#### Queue 选型建议

• 普通 FIFO 队列 ➝ LinkedList

• 优先级队列 ➝ PriorityQueue

• 高并发队列 ➝ ConcurrentLinkedQueue

• 阻塞队列 ➝ LinkedBlockingQueue

### Map（键值对存储）

Map 主要用于存储 Key-Value 对象，适用于 快速查找、缓存、索引。

| 实现类               | 底层结构           | 排序         | 线程安全   |
| ----------------- | -------------- | ---------- | ------ |
| HashMap           | 数组 + 链表 + 红黑树  | ❌ 无序       | ❌ 不安全  |
| LinkedHashMap     | HashMap + 双向链表 | ✅ 插入顺序     | ❌ 不安全  |
| TreeMap           | 红黑树            | ✅ 按 Key 排序 | ❌ 不安全  |
| ConcurrentHashMap | CAS + 分段锁      | ❌ 无序       | ✅ 线程安全 |

#### Map 选型建议

• 无序存储 ➝ HashMap

• 有序存储（按插入顺序） ➝ LinkedHashMap

• 排序存储（按 Key 排序） ➝ TreeMap

• 线程安全 ➝ ConcurrentHashMap



## 总结

Java 集合框架为不同的应用场景提供了 多种数据结构，根据 数据特点、访问方式、并发需求 选择合适的实现类，可以提高 程序性能。
