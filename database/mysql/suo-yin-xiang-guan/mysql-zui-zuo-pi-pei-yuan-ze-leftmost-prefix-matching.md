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

## 3. 索引生效的查询

| SQL 语句                                                 | 是否使用索引 | 说明                              |
| ------------------------------------------------------ | ------ | ------------------------------- |
| `WHERE name = 'Alice'`                                 | ✅      | 匹配索引的最左列                        |
| `WHERE name = 'Alice' AND age = 25`                    | ✅      | 索引前两列匹配，索引生效                    |
| `WHERE name = 'Alice' AND age = 25 AND city = 'Paris'` | ✅      | 完整匹配，最优情况                       |
| `WHERE name LIKE 'A%'`                                 | ✅      | 前缀匹配，索引生效                       |
| `WHERE name = 'Alice' AND city = 'Paris'`              | ✅      | 部分索引生效，但 `age` 被跳过              |
| `WHERE name = 'Alice' AND age > 20`                    | ✅      | 范围查询 `age > 20` 后，`city` 不再使用索引 |

***

## &#x20;4. 索引失效的查询

| SQL 语句                              | 是否使用索引 | 说明                     |
| ----------------------------------- | ------ | ---------------------- |
| `WHERE age = 25`                    | ❌      | 跳过 `name`，索引失效         |
| `WHERE city = 'Paris'`              | ❌      | 跳过 `name` 和 `age`，索引失效 |
| `WHERE age = 25 AND city = 'Paris'` | ❌      | 跳过 `name`，索引失效         |
| `WHERE name LIKE '%Alice%'`         | ❌      | 索引失效，前缀匹配丢失            |

## 5.最左匹配原则的影响

* 查询必须从最左列开始，否则索引无法生效。
* 索引列不能被跳过，否则 MySQL 可能不会使用索引。
* 范围查询 (>, <, BETWEEN) 之后的索引列不会被使用。

## 6.结论

### 正确的用法

* 从索引的最左列开始查询。
* 使用等值匹配 (=) 时，可以利用多个索引列。
* LIKE 'xxx%'（前缀匹配）可使用索引，但 LIKE '%xxx' 不行。

### 容易踩的坑

* 跳过索引列，索引失效。
* 使用 LIKE '%xxx%'，索引失效。
* 范围查询 (>, <) 之后，索引不再生效。

