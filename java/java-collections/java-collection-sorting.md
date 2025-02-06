---
description: 在 Java 中，集合（Collection）可以按照多种方式进行排序，主要包括
cover: >-
  https://images.unsplash.com/photo-1735022734031-ae0565a2554b?crop=entropy&cs=srgb&fm=jpg&ixid=M3wxOTcwMjR8MHwxfHJhbmRvbXx8fHx8fHx8fDE3Mzg4NTYxNTN8&ixlib=rb-4.0.3&q=85
coverY: 0
---

# Java Collection Sorting

### 📌 Java 集合排序方式对比表格

| **排序方式**                  | **适用场景**                           |
| ------------------------- | ---------------------------------- |
| **`Comparable`（自然排序）**    | 适用于对象有默认排序规则，如年龄、名字。               |
| **`Comparator`（自定义排序）**   | 适用于多个排序标准，如按年龄、按名字。                |
| **Stream API 排序**         | 适用于流式数据处理，结合 `filter()`、`map()` 等。 |
| **`Collections.sort()`**  | 适用于 `List` 排序，支持 `Comparator`。     |
| **`TreeSet` / `TreeMap`** | 适用于去重 + 排序，自动维护顺序。                 |
| **`Arrays.sort()`**       | 适用于数组排序，性能较高。                      |

## 📌 1. 自然排序（Comparable 接口）

Comparable 接口 用于让对象 支持默认排序，适用于 单一排序标准。

### ✅ 代码示例

```java
import java.util.*;

class Person implements Comparable<Person> {
    String name;
    int age;

    public Person(String name, int age) {
        this.name = name;
        this.age = age;
    }

    // 实现 compareTo 方法（按年龄升序）
    @Override
    public int compareTo(Person other) {
        return Integer.compare(this.age, other.age);
    }

    @Override
    public String toString() {
        return name + " - " + age;
    }
}

public class ComparableExample {
    public static void main(String[] args) {
        List<Person> people = new ArrayList<>(List.of(
            new Person("Alice", 30),
            new Person("Bob", 25),
            new Person("Charlie", 28)
        ));

        Collections.sort(people); // 按年龄排序
        System.out.println(people); // [Bob - 25, Charlie - 28, Alice - 30]
    }
}
```

📌 适用于：

* 对象有默认排序方式（如年龄、姓名）。
* 不需要多种排序逻辑（单一标准）。

## 📌 2. 自定义排序（Comparator 接口）

Comparator 接口 允许 定义多个排序规则，适用于复杂排序场景。

### ✅ 代码示例

```java
import java.util.*;

class Person {
    String name;
    int age;

    public Person(String name, int age) {
        this.name = name;
        this.age = age;
    }

    @Override
    public String toString() {
        return name + " - " + age;
    }
}

public class ComparatorExample {
    public static void main(String[] args) {
        List<Person> people = new ArrayList<>(List.of(
            new Person("Alice", 30),
            new Person("Bob", 25),
            new Person("Charlie", 28)
        ));

        // 按姓名排序（字母顺序）
        people.sort(Comparator.comparing(p -> p.name));
        System.out.println(people); // [Alice - 30, Bob - 25, Charlie - 28]

        // 按年龄倒序排序
        people.sort(Comparator.comparingInt(p -> -p.age));
        System.out.println(people); // [Alice - 30, Charlie - 28, Bob - 25]
    }
}
```

📌 适用于：

* 对象需要多个排序方式（如按名字、按年龄）。
* 需要自定义复杂的排序逻辑。

## 📌 3. 使用 Stream API 排序

Java 8 引入 Stream API，支持 流式排序，适用于链式操作。

### ✅ 代码示例

```java
import java.util.*;
import java.util.stream.Collectors;

public class StreamSortingExample {
    public static void main(String[] args) {
        List<String> names = Arrays.asList("Charlie", "Alice", "Bob");

        // 升序排序
        List<String> sortedNames = names.stream()
            .sorted()
            .collect(Collectors.toList());
        System.out.println(sortedNames); // [Alice, Bob, Charlie]

        // 按字符串长度排序
        List<String> sortedByLength = names.stream()
            .sorted(Comparator.comparingInt(String::length))
            .collect(Collectors.toList());
        System.out.println(sortedByLength); // [Bob, Alice, Charlie]
    }
}
```

📌 适用于：

* 链式操作，结合 filter()、map() 等流式处理。
* 排序后直接返回新列表，不修改原集合。

## 📌 4. 使用 Collections.sort()

Collections.sort(List) 方法可用于 列表排序，默认使用 Comparable 或 Comparator 进行排序。

### ✅ 代码示例

```java
import java.util.*;

public class CollectionsSortExample {
    public static void main(String[] args) {
        List<Integer> numbers = Arrays.asList(5, 3, 8, 1, 2);

        // 升序排序
        Collections.sort(numbers);
        System.out.println(numbers); // [1, 2, 3, 5, 8]

        // 降序排序
        Collections.sort(numbers, Comparator.reverseOrder());
        System.out.println(numbers); // [8, 5, 3, 2, 1]
    }
}
```

📌 适用于：

* 简单列表排序（List）。
* 适用于基本类型、字符串等可比较对象。

## 📌 5. 使用 TreeSet / TreeMap 排序

TreeSet 和 TreeMap 自动按照自然顺序排序，适用于 去重 + 排序。

✅ TreeSet 例子

```java
import java.util.*;

public class TreeSetExample {
    public static void main(String[] args) {
        Set<Integer> sortedSet = new TreeSet<>(Arrays.asList(5, 3, 8, 1, 2));
        System.out.println(sortedSet); // [1, 2, 3, 5, 8]
    }
}
```

📌 适用于：

* 按照 Key 进行排序
* 自动维护有序的 Map

## 📌 6. 使用 Arrays.sort()

Arrays.sort() 适用于 数组排序，可以配合 Comparator 自定义排序。

```java
import java.util.Arrays;

public class ArraysSortExample {
    public static void main(String[] args) {
        int[] numbers = {5, 3, 8, 1, 2};

        // 升序排序
        Arrays.sort(numbers);
        System.out.println(Arrays.toString(numbers)); // [1, 2, 3, 5, 8]

        // 按字符串长度排序
        String[] words = {"Banana", "Apple", "Cherry"};
        Arrays.sort(words, (a, b) -> a.length() - b.length());
        System.out.println(Arrays.toString(words)); // [Apple, Cherry, Banana]
    }
}
```

📌 适用于：

* 数组排序（原生数据类型 int\[]、double\[] 等）。
* 比 Collections.sort() 更适用于固定大小的数组。

