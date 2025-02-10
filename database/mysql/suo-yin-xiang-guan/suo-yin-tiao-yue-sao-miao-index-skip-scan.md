---
description: >-
  索引跳跃扫描（Index Skip Scan） 是 MySQL 8.0+ 引入的一种 优化查询 方式，它允许
  跳过联合索引的前导列，仍然使用索引进行查询，从而提高查询效率。
---

# 索引跳跃扫描（Index Skip Scan）

## 为什么需要索引跳跃扫描？

在 传统 MySQL（< 8.0） 版本中，MySQL 使用索引时必须遵守 最左前缀匹配原则：

* 如果查询条件跳过了索引的前导列，则索引通常无法使用，导致 全表扫描（Full Table Scan）。
* 索引跳跃扫描（Index Skip Scan） 允许 跳过部分前导列，仍然利用索引进行优化查询。

### 示例

#### 1.创建联合索引

```sql
CREATE INDEX idx_user ON users(department, age, name);
```

此索引包含：

* department（部门）
* age（年龄）
* name（姓名）

#### 2.传统查询（索引正常使用）

```sql
EXPLAIN SELECT * FROM users WHERE department = 'IT' AND age = 25;
```

✅ 索引生效（符合 最左前缀匹配）。

#### 3.传统情况下，索引失效的查询

```sql
EXPLAIN SELECT * FROM users WHERE age = 25;
```

❌ 在 MySQL 5.7 及以下版本中，索引失效，导致全表扫描：

* age 跳过了 department（索引的第一列），无法使用 最左匹配原则。

#### 4.MySQL 8.0+ 支持索引跳跃扫描

```sql
EXPLAIN SELECT * FROM users WHERE age = 25;
```

✅ 索引生效（Index Skip Scan）：

* MySQL 会遍历索引中的所有 department 值。
* 然后在每个 department 值下，查找 age = 25 的数据。
* 这种方式 仍然可以利用索引，而不会直接进行全表扫描。

## 索引跳跃扫描的优势

| **特性**            | **描述**                   |
| ----------------- | ------------------------ |
| **减少全表扫描**        | 即使跳过部分索引前缀列，仍然能使用索引      |
| **提高查询性能**        | 避免不必要的全表扫描，提升数据库吞吐量      |
| **MySQL 8.0+ 支持** | MySQL 8.0 及以上版本可用，旧版本不支持 |

## 索引跳跃扫描适用场景

* 索引的第一列区分度低（如 性别、状态、类别）。
* 查询只使用索引的后几列，但仍希望利用索引加速查询。
* MySQL 版本 ≥ 8.0，否则不会自动使用 索引跳跃扫描。

## 索引跳跃扫描的限制

* 不适用于所有情况，如果索引的前缀列区分度很高，索引跳跃扫描可能 并不比全表扫描更快。
* 仅适用于 B+ 树索引，不适用于哈希索引（如 Memory 引擎的 Hash 索引）。

