---
description: 索引优化是 MySQL 查询优化的核心，它可以显著提升 SQL 查询性能。合理使用索引 能够减少数据扫描量，降低 I/O 负担，提高查询效率
---

# 索引优化

## 1.为什么要优化索引？

### 问题：没有索引时，MySQL 如何查找数据？

* 全表扫描（Full Table Scan, FTS）：逐行遍历数据表，导致查询速度慢。
* 数据量大时，查询时间急剧上升。
* 影响事务、锁机制：在高并发环境下，全表扫描可能导致锁争用。

### 索引优化的目标

* 减少数据扫描量，提高查询速度。
* 降低 I/O 负担，减少磁盘访问。
* 提高事务并发能力，减少锁冲突。

## 2.索引优化策略

### 3.1避免索引失效

#### 最左匹配原则（Leftmost Prefix Matching）

* MySQL 从左到右 依次匹配索引中的列，跳过某一列，后续索引失效。

#### 示例

假设有联合索引：

```sql
CREATE INDEX idx_user ON users(name, age, city);
```

查询索引匹配情况：

```sql
SELECT * FROM users WHERE name = 'Alice';  -- ✅ 索引有效
SELECT * FROM users WHERE name = 'Alice' AND age = 25;  -- ✅ 索引有效
SELECT * FROM users WHERE name = 'Alice' AND city = 'Paris';  -- ❌ age 被跳过，索引部分失效
SELECT * FROM users WHERE city = 'Paris';  -- ❌ name 被跳过，索引失效
```

#### 优化建议：

* 按照索引顺序查询，避免跳过中间列。
* 单独查询 city 字段时，应该创建 city 单列索引。

### 3.2LIKE 查询优化

* LIKE '%xxx%' 前缀通配符会导致索引失效。
* LIKE 'xxx%' 前缀匹配索引有效。

#### 示例

```sql
SELECT * FROM users WHERE name LIKE '%Alice%';  -- ❌ 索引失效（前导 %）
SELECT * FROM users WHERE name LIKE 'Alice%';  -- ✅ 索引有效（前缀匹配）
```

#### 优化建议：

* 尽量避免 %xxx% 形式的模糊查询。
* 可以使用 FULLTEXT 索引进行全文搜索：

```sql
ALTER TABLE articles ADD FULLTEXT(title, content);
SELECT * FROM articles WHERE MATCH(title, content) AGAINST('MySQL优化');
```

### 3.3避免索引函数计算

* 索引列不能参与计算，否则索引失效。

#### 示例

```sql
SELECT * FROM users WHERE YEAR(birth_date) = 2000;  -- ❌ 索引失效
SELECT * FROM users WHERE birth_date BETWEEN '2000-01-01' AND '2000-12-31';  -- ✅ 索引有效
```

#### 优化建议：

* 避免 WHERE 子句中的索引列进行计算。
* 使用范围查询替代函数计算。

### 3.4覆盖索引（Covering Index）

避免回表查询，提升查询速度。

#### 示例

```sql
CREATE INDEX idx_user ON users(name, age);
```

```sql
SELECT name, age FROM users WHERE name = 'Alice';  -- ✅ 覆盖索引，不回表
SELECT * FROM users WHERE name = 'Alice';  -- ❌ 需要回表
```

#### 优化建议：

* 尽量让查询字段包含在索引中，避免 SELECT \*。

### 3.5索引下推（Index Condition Pushdown, ICP）

MySQL 5.6+ 引入 索引下推优化（ICP），减少回表次数，提高查询效率。

#### 示例

```sql
SELECT * FROM users WHERE name LIKE 'A%' AND age > 20;
```

## 4.如何分析 SQL 是否使用索引

使用 EXPLAIN 关键字查看查询执行计划：

```sql
EXPLAIN SELECT * FROM users WHERE name = 'Alice' AND age > 20;
```

#### 重要字段解读

| 字段                 | 含义                                                         |
| ------------------ | ---------------------------------------------------------- |
| **type**           | 访问类型（ALL 表示全表扫描，ref/range 表示索引扫描）                          |
| **possible\_keys** | 可能使用的索引                                                    |
| **key**            | 实际使用的索引                                                    |
| **rows**           | 预计扫描的行数，越少越好                                               |
| **Extra**          | 其他优化信息，如 `Using index`（覆盖索引）、`Using index condition`（索引下推） |

## 总结

### 索引优化策略

* 使用 最左匹配原则，避免索引失效。
* 避免 LIKE '%xxx%'，使用 FULLTEXT 代替。
* 避免索引列参与计算，使用 范围查询 代替。
* 利用覆盖索引，减少回表查询。
* 使用索引下推，减少 I/O 负担。

### 索引优化工具

* EXPLAIN 分析索引使用情况
* SHOW INDEX FROM table 查看表的索引
* OPTIMIZE TABLE 维护索引



