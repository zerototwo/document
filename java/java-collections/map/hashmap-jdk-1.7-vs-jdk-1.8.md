---
cover: >-
  https://images.unsplash.com/photo-1734966901441-ac6c1fff1fd2?crop=entropy&cs=srgb&fm=jpg&ixid=M3wxOTcwMjR8MHwxfHJhbmRvbXx8fHx8fHx8fDE3Mzg5MzcwNDJ8&ixlib=rb-4.0.3&q=85
coverY: 0
---

# HashMap JDK 1.7 vs JDK 1.8

## &#x20;HashMap JDK 1.7 vs JDK 1.8 对比（详细解析）

| **特性**   | **JDK 1.7（旧）** | **JDK 1.8（新）**           |
| -------- | -------------- | ------------------------ |
| **数据结构** | 数组 + 链表        | 数组 + 链表 + 红黑树            |
| **哈希冲突** | 链地址法（头插法）      | 链地址法（尾插法），链表长度 >8 转换为红黑树 |
| **扩容方式** | 先扩容，再迁移数据      | 先迁移数据，再扩容                |
| **遍历顺序** | 可能发生死循环（并发操作）  | 不会死循环，线程更安全              |
| **性能优化** | 链表查找 O(n)      | 红黑树查找 O(log n)           |

📌 **JDK 1.8 主要优化了 Hash 冲突处理方式，引入红黑树提高查询效率，并解决了 JDK 1.7 的死循环问题**

## 1.数据结构

### JDK 1.7

* HashMap 由 数组 + 链表 组成。
* 每个元素（Entry\<K, V>）存储在 数组的某个索引（bucket） 位置，如果发生哈希冲突，则采用 链表存储冲突元素。

```java
static class Entry<K,V> implements Map.Entry<K,V> {
    final K key;
    V value;
    Entry<K,V> next;
}
```

JDK 1.7 的问题

* 如果哈希冲突严重（即多个 key 计算到同一个索引），链表会变长，查询效率退化为 O(n)。

### JDK 1.8

* 仍然采用 数组 + 链表，但新增了红黑树。
* 当 链表长度 >8 时，链表会转换为 红黑树，提高查询效率。

```java
static class Node<K,V> implements Map.Entry<K,V> {
    final int hash;
    final K key;
    V value;
    Node<K,V> next;
}
```

JDK 1.8 优势

* 链表查找 O(n) → 红黑树查找 O(log n)，性能大幅提升。

## 2.哈希冲突

### JDK 1.7

* 采用 链地址法（头插法），即新元素插入链表头部。
* 问题：并发情况下，扩容时链表可能反转，形成死循环。

```java
void transfer(Entry[] newTable) {
    for (Entry<K, V> e : table) {
        while (null != e) {
            Entry<K, V> next = e.next;
            int i = indexFor(e.hash, newTable.length);
            e.next = newTable[i]; // 头插法
            newTable[i] = e;
            e = next;
        }
    }
}
```

### JDK 1.8

* 采用 尾插法（即新元素插入链表尾部）。
* 优化：链表长度 超过 8 时转换为红黑树，提高查询效率。

```java
void transfer(Node<K, V>[] newTable) {
    for (Node<K, V> e : table) {
        while (null != e) {
            Node<K, V> next = e.next;
            int i = indexFor(e.hash, newTable.length);
            if (e instanceof TreeNode) {
                ((TreeNode<K, V>) e).split(this, newTable, i, oldCap);
            } else {
                e.next = newTable[i]; // 尾插法
                newTable[i] = e;
            }
            e = next;
        }
    }
}
```

### JDK 1.8 优势

* 尾插法解决了 JDK 1.7 的死循环问题。
* 链表过长（>8）时转换为红黑树，优化查询性能。

## 3.HashMap 扩容

### JDK 1.7扩容

* 先扩容，再迁移数据。
* 可能引发死循环（因为头插法导致顺序反转）。

### JDK 1.8扩容

* 先迁移数据，再扩容，保证数据顺序正确。
* 优化 rehash 过程，减少冲突带来的链表增长问题。

```java
if (oldCap >= 64 && oldCap > oldThr) {
    newThr = oldThr << 1; // 2 倍扩容
} else if (oldThr > 0) {
    newCap = oldThr;
}
```

JDK 1.8 优势

* 避免 JDK 1.7 扩容导致的死循环问题。
* 更高效的 rehash，减少扩容次数。

## 4.遍历顺序

### JDK 1.7

* 多线程环境下可能发生死循环。
* 因为头插法可能导致扩容时链表反转，造成无限循环。

### JDK 1.8

* 不会发生死循环，遍历顺序稳定。

### JDK 1.8 优势

* 多线程环境下更安全，避免了 JDK 1.7 的死循环问题。

## 5.性能优化

### JDK 1.7

* 链表查找性能 O(n)，哈希冲突严重时，性能下降明显。

### JDK 1.8

* 链表长度 >8 时，转换为红黑树，查询 O(log n)。
* 提高了查询性能，避免极端情况下 O(n) 查找。

### JDK 1.8 优势

* 哈希冲突少时，仍然使用链表，减少额外的存储开销。
* 冲突严重时，自动转换为红黑树，提高查找效率。





