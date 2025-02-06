---
description: 在 Java 中，集合（Collection）可以按照多种方式进行排序，主要包括
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

