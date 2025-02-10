---
description: 最左匹配原则 是 MySQL 联合索引（Composite Index） 的一个查询优化规则，它决定了 索引的使用方式。
---

# MySQL 最左匹配原则（Leftmost Prefix Matching）

## 1.最左匹配原则的核心要点

* 必须从索引的最左列开始匹配，否则索引可能会失效。
* 不能跳过索引列，否则索引部分失效。
* 范围查询 (>, <, BETWEEN, LIKE 'xxx%') 之后的索引列不会被使用。

## 2.示例：创建联合索引

假设有一个 users 表，并创建了以下 联合索引：

```sql
CREATE INDEX idx_user ON users(name, age, city);
```

此索引按照 (name, age, city) 进行存储，索引顺序 如下：

```
name → age → city
```



