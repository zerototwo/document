---
description: >-
  ArrayList.subList(int fromIndex, int toIndex) 返回指定范围内的子列表，但该子列表仍然依赖于原
  ArrayList，不是独立的副本
cover: >-
  https://images.unsplash.com/photo-1735669356374-8ea7506cd1d2?crop=entropy&cs=srgb&fm=jpg&ixid=M3wxOTcwMjR8MHwxfHJhbmRvbXx8fHx8fHx8fDE3Mzg4NzUzMDJ8&ixlib=rb-4.0.3&q=85
coverY: 0
---

# ArrayList subList()

## 1.subList() 方法语法

```java
List<E> subList(int fromIndex, int toIndex)
```

* fromIndex：起始索引（包含）
* toIndex：结束索引（不包含）
* 返回值：List 类型的视图（不创建新列表，只是原列表的一个窗口）
* 修改子列表会影响原列表，反之亦然

## 2.subList() 使用示例

```java
import java.util.ArrayList;
import java.util.List;

public class SubListExample {
    public static void main(String[] args) {
        List<String> list = new ArrayList<>(List.of("A", "B", "C", "D", "E"));

        List<String> subList = list.subList(1, 4); // 获取索引 1 到 3（不包含 4）
        System.out.println(subList); // [B, C, D]

        // 修改子列表（影响原列表）
        subList.set(0, "X");
        System.out.println(subList); // [X, C, D]
        System.out.println(list);    // [A, X, C, D, E]

        // 在子列表中删除元素（影响原列表）
        subList.remove(1);
        System.out.println(subList); // [X, D]
        System.out.println(list);    // [A, X, D, E]
    }
}
```

subList() 只是原 ArrayList 的一个窗口，并没有复制数据，因此修改 subList 也会影响原 ArrayList。

## 3.subList() 的常见问题

### 📌 原因

* subList() 依赖于原 ArrayList，当 ArrayList 结构发生变化（如 add()、remove()），subList 无法再正确访问数据，抛出 ConcurrentModificationException。

### 📌 解决方案

1.使用 new ArrayList<>(subList) 复制子列表

```java
List<String> safeSubList = new ArrayList<>(list.subList(1, 4));
list.add("F"); // 原列表可以修改
System.out.println(safeSubList); // 不受影响 [B, C, D]
```

### 2.subList() 返回的子列表不能直接转换为 ArrayList

```java
ArrayList<String> newList = (ArrayList<String>) list.subList(1, 4); // ❌ ClassCastException
```

📌 原因

* subList() 返回的是 List 视图，不是 ArrayList 实例，所以不能直接强制转换。

📌 解决方案

显式创建新 ArrayList

```java
ArrayList<String> newList = new ArrayList<>(list.subList(1, 4));
```

## 4.subList() vs List.copyOf() vs new ArrayList<>(subList)



| **方法**                           | **是否影响原列表？**            | **是否抛 `ConcurrentModificationException`？** | **是否独立？**     |
| -------------------------------- | ----------------------- | ------------------------------------------ | ------------- |
| `subList(from, to)`              | ✅ **是**（修改子列表影响原列表）     | ❌ **可能抛异常**（修改原列表后访问 `subList`）            | ❌ **依赖原列表**   |
| `new ArrayList<>(subList)`       | ❌ **否**（拷贝新列表）          | ✅ **不会抛异常**                                | ✅ **独立的列表**   |
| `List.copyOf(subList)`（Java 10+） | ❌ **否**（拷贝新列表，**不可修改**） | ✅ **不会抛异常**                                | ✅ **独立（但只读）** |

📌 结论

* subList() 适用于临时视图，但不应修改原列表。
* new ArrayList<>(subList) 适用于需要可修改的新列表。
* List.copyOf(subList) 适用于只读子列表（Java 10+）。

## 5.subList() 使用场景

✅ 提取数据子集

```java
List<Integer> numbers = new ArrayList<>(List.of(1, 2, 3, 4, 5, 6));
List<Integer> subNumbers = numbers.subList(2, 5); // 提取索引 2~4 的元素
System.out.println(subNumbers); // [3, 4, 5]
```

✅ 分页处理

```java
public static List<String> getPage(List<String> list, int page, int size) {
    int fromIndex = (page - 1) * size;
    int toIndex = Math.min(fromIndex + size, list.size());
    return new ArrayList<>(list.subList(fromIndex, toIndex)); // 复制新列表
}
```

✅ 批量处理

```java
List<Integer> batch = list.subList(0, Math.min(10, list.size())); // 获取前 10 个元素
```

## 6.结论

| **问题**                                      | **结论**                                      |
| ------------------------------------------- | ------------------------------------------- |
| **`subList()` 生成的新列表是独立的吗？**                | ❌ **不是，修改子列表会影响原列表**                        |
| **`subList()` 修改原列表会导致什么？**                 | ❌ **可能抛 `ConcurrentModificationException`** |
| **如何避免 `ConcurrentModificationException`？** | ✅ **使用 `new ArrayList<>(subList)` 复制列表**    |
| **如何生成不可修改的子列表？**                           | ✅ **使用 `List.copyOf(subList)`（Java 10+）**   |
| **什么时候使用 `subList()`？**                     | ✅ **分页处理、批量操作、数据子集提取**                      |

📌 **推荐：如果需要** **安全可修改的子列表，请使用 `new ArrayList<>(subList)`** 🚀
