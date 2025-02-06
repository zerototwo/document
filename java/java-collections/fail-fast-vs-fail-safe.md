---
description: 在 Java 中，集合（Collection）在并发环境下的迭代有两种方式：
---

# Fail-Fast vs Fail-Safe

1\. Fail-Fast（快速失败）：检测到 并发修改 时 立即抛出异常（ConcurrentModificationException）。

2\. Fail-Safe（安全失败）：允许并发修改，不会抛异常，而是返回旧数据或拷贝数据。



### 📌 Fail-Fast vs Fail-Safe 对比

| **特性**    | **Fail-Fast（快速失败）**                                                | **Fail-Safe（安全失败）**                                                 |
| --------- | ------------------------------------------------------------------ | ------------------------------------------------------------------- |
| **定义**    | 在**并发修改**时 **抛出异常**，防止不一致数据。                                       | **允许并发修改**，返回旧数据或拷贝数据。                                              |
| **适用集合**  | `ArrayList`、`HashSet`、`HashMap`（使用 `Iterator` 迭代）。                 | `CopyOnWriteArrayList`、`ConcurrentHashMap`、`ConcurrentLinkedQueue`。 |
| **实现机制**  | **直接访问原集合**，修改后 `modCount` 变化导致 `ConcurrentModificationException`。 | **遍历时使用拷贝副本**，不会影响原集合。                                              |
| **是否抛异常** | **是**（检测到修改后立即抛 `ConcurrentModificationException`）。                | **否**（允许并发修改，不抛异常）。                                                 |
| **性能**    | **高性能，但不支持并发修改**。                                                  | **线程安全，但性能比 Fail-Fast 低**（因拷贝开销）。                                   |
| **适用场景**  | 适用于**单线程遍历**，不适用于并发环境。                                             | 适用于**多线程并发**，如 **读多写少的场景**。                                         |

## 1.Fail-Fast 机制

Fail-Fast 迭代器 在遍历集合时，如果检测到集合被修改（如 add()、remove()），则立即抛出 ConcurrentModificationException。

### ✅ 代码示例

```java
import java.util.*;

public class FailFastExample {
    public static void main(String[] args) {
        List<String> list = new ArrayList<>(Arrays.asList("A", "B", "C"));

        Iterator<String> iterator = list.iterator();
        while (iterator.hasNext()) {
            System.out.println(iterator.next());
            list.add("D"); // 并发修改，抛出异常
        }
    }
}
```

### 输出

```sh
A
Exception in thread "main" java.util.ConcurrentModificationException
```

📌 适用集合

* ArrayList
* HashSet
* HashMap
* LinkedList

（所有非并发安全集合）

## 2.Fail-Safe 机制

Fail-Safe 迭代器 采用 拷贝数据（snapshot） 方式，即 遍历的是集合的副本，而非原集合，因此 不会抛异常。

### ✅ 代码示例

```java
import java.util.concurrent.*;

public class FailSafeExample {
    public static void main(String[] args) {
        CopyOnWriteArrayList<String> list = new CopyOnWriteArrayList<>(new String[]{"A", "B", "C"});

        Iterator<String> iterator = list.iterator();
        while (iterator.hasNext()) {
            System.out.println(iterator.next());
            list.add("D"); // 不会抛异常
        }
    }
}
```

### 输出

```java
A
B
C
```

📌 注意：尽管 D 被添加了，但迭代器遍历的副本不会包含 D，因此 D 不会被输出。

📌 适用集合

* CopyOnWriteArrayList
* CopyOnWriteArraySet
* ConcurrentHashMap
* ConcurrentLinkedQueue

（所有线程安全集合）

## 3.如何避免 ConcurrentModificationException



| **方法**                        | **解决方案**                                              |
| ----------------------------- | ----------------------------------------------------- |
| **使用 `Iterator.remove()`**    | **避免 `ConcurrentModificationException`，但不能 `add()`**。 |
| **使用 `CopyOnWriteArrayList`** | **使用 Fail-Safe 机制，允许并发修改**。                           |
| **使用 `ConcurrentHashMap`**    | **并发环境下替代 `HashMap`，支持线程安全迭代**。                       |

### **✅ 示例 1：使用 `Iterator.remove()`**

```java
List<String> list = new ArrayList<>(Arrays.asList("A", "B", "C"));

Iterator<String> iterator = list.iterator();
while (iterator.hasNext()) {
    if (iterator.next().equals("B")) {
        iterator.remove(); // 正确删除元素
    }
}
System.out.println(list); // [A, C]
```

📌 适用于 ArrayList、HashSet，但不能使用 add()。

### ✅ 示例 2：使用 CopyOnWriteArrayList

```java
CopyOnWriteArrayList<String> list = new CopyOnWriteArrayList<>(new String[]{"A", "B", "C"});

for (String s : list) {
    if (s.equals("B")) {
        list.add("D"); // 允许 add()，不会抛异常
    }
}
System.out.println(list); // [A, B, C, D]
```

📌 适用于 读多写少的场景，如 日志管理、缓存系统。

### ✅ 示例 3：使用 ConcurrentHashMap

```java
ConcurrentHashMap<Integer, String> map = new ConcurrentHashMap<>();
map.put(1, "A");
map.put(2, "B");

for (Integer key : map.keySet()) {
    map.put(3, "C"); // 允许修改，不会抛异常
}
System.out.println(map); // {1=A, 2=B, 3=C}
```

📌 适用于 并发环境下的 Map 操作。



## 📌 Fail-Fast vs Fail-Safe 总结

| **问题**                                      | **结论**                                                                   |
| ------------------------------------------- | ------------------------------------------------------------------------ |
| **Fail-Fast 和 Fail-Safe 的核心区别？**            | **Fail-Fast 抛异常，Fail-Safe 允许并发修改**。                                      |
| **Fail-Fast 适用于哪些集合？**                      | **ArrayList、HashSet、HashMap**（非线程安全）。                                    |
| **Fail-Safe 适用于哪些集合？**                      | **CopyOnWriteArrayList、ConcurrentHashMap**（线程安全）。                        |
| **如何避免 `ConcurrentModificationException`？** | **使用 `Iterator.remove()`、`CopyOnWriteArrayList` 或 `ConcurrentHashMap`。** |
| **什么时候使用 Fail-Safe？**                       | **多线程环境（日志管理、缓存、微服务数据共享）。**                                              |
| **什么时候使用 Fail-Fast？**                       | **单线程环境，提高性能（如单线程数据分析）。**                                                |

📌 **Fail-Fast 适用于单线程高性能处理，Fail-Safe 适用于多线程并发修改。**

