---
cover: >-
  https://images.unsplash.com/photo-1735666119059-13bc55dc4aaf?crop=entropy&cs=srgb&fm=jpg&ixid=M3wxOTcwMjR8MHwxfHJhbmRvbXx8fHx8fHx8fDE3Mzg5MzQ1NTR8&ixlib=rb-4.0.3&q=85
coverY: 0
---

# ArrayList transient used in underlying array

在 ArrayList 的源码中，我们可以看到其底层数组 elementData 被标记为 transient

```java
// Java 8 `ArrayList` 源码
transient Object[] elementData;
```

## 1.transient 关键字的作用

* transient 使字段在序列化时被忽略，防止直接序列化底层数组。
* ArrayList 采用自定义序列化方式，而不是默认序列化整个 elementData 数组。

这样做的主要目的是：

* 避免序列化无用的数组空间（如未使用的容量）。
* 提高序列化效率，只存储实际元素。

## 2.ArrayList 自定义序列化方式

因为 elementData 被标记为 transient，所以 ArrayList 不会直接序列化整个数组，而是通过 writeObject() 和 readObject() 自定义序列化逻辑。

### ArrayList 自定义序列化逻辑

```java
private void writeObject(ObjectOutputStream s) throws IOException {
    // 先序列化 ArrayList 的大小（实际元素个数）
    s.defaultWriteObject();

    // 只序列化有效元素，不序列化多余的数组容量
    for (int i = 0; i < size; i++) {
        s.writeObject(elementData[i]);
    }
}

private void readObject(ObjectInputStream s) throws IOException, ClassNotFoundException {
    s.defaultReadObject();

    // 重新初始化数组（避免反序列化时浪费空间）
    elementData = new Object[size];
    
    // 反序列化实际元素
    for (int i = 0; i < size; i++) {
        elementData[i] = s.readObject();
    }
}
```

📌 核心逻辑

* 只序列化 size，而不是整个 elementData 数组。
* 仅序列化 size 长度的有效数据，而不是整个数组（可能包含大量 null）。
* 反序列化时重新分配数组大小，避免存储多余的 null 元素。

## 3.为什么不用默认序列化？

假设我们有一个 ArrayList：

```java
ArrayList<String> list = new ArrayList<>(10); // 初始容量 10
list.add("A");
list.add("B");
list.add("C");
```

如果直接序列化 elementData，会存储整个数组（长度 10），而不是实际的 3 个元素，这样会浪费空间：

```java
序列化前：
elementData = ["A", "B", "C", null, null, null, null, null, null, null]

如果直接序列化：
["A", "B", "C", null, null, null, null, null, null, null]  ❌ 存储大量 `null`

使用 `transient` 并自定义序列化：
["A", "B", "C"] ✅ 只存储有效数据
```

📌 结论

* 如果不加 transient，整个 elementData 数组都会被序列化，导致文件变大，存储无用的 null。
* 加了 transient 后，ArrayList 只序列化有效数据，提高效率。

## &#x20;4.`transient` 使 `ArrayList` 序列化更高效

| **方式**                      | **存储方式**  | **是否浪费空间**              | **性能**           |
| --------------------------- | --------- | ----------------------- | ---------------- |
| **默认序列化 `elementData`**     | 直接序列化整个数组 | ✅ **会存储未使用的 `null` 空间** | ❌ **低（占用大量空间）**  |
| **使用 `transient` + 自定义序列化** | 仅存储有效元素   | ❌ **不存储多余 `null`**      | ✅ **高（只存储必要数据）** |

##

