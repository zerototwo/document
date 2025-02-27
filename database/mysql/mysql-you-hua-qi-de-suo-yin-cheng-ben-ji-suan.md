---
cover: >-
  https://images.unsplash.com/photo-1735596365888-ad6d151533f2?crop=entropy&cs=srgb&fm=jpg&ixid=M3wxOTcwMjR8MHwxfHJhbmRvbXx8fHx8fHx8fDE3NDA2OTMxMzF8&ixlib=rb-4.0.3&q=85
coverY: 0
---

# MySQL 优化器的索引成本计算

MySQL 优化器（Query Optimizer） 通过 成本模型（Cost Model） 计算不同执行计划的 代价（Cost），并选择 成本最低的索引和查询执行方式。

## 1.什么是索引成本（Index Cost）

索引成本 是指 MySQL 优化器在查询时评估不同索引的使用代价，主要影响 查询是否选择索引。



MySQL 计算索引成本的主要因素

1. IO 成本 📂：查询索引和数据的磁盘访问次数
2. CPU 成本 🖥：处理索引扫描、排序、过滤的计算量
3. 行数估算 📊：索引返回的 行数（越少越好）
4. 索引选择性 🎯：唯一索引 vs. 非唯一索引
5. 排序 & 额外操作 🔄：是否需要 filesort 或 temporary table

## 2.MySQL 计算索引成本的公式

索引成本计算的核心公式

```java
Index Cost = (IO 成本 × 访问的索引页数) + (CPU 成本 × 访问的行数)
```

## 3.MySQL 如何估算索引成本？

### 1. 估算访问行数（Rows）

MySQL 通过 ANALYZE TABLE 维护索引的统计信息，如：

* 索引的基数（Cardinality）
* 索引覆盖的行数
* 索引分布情况

#### 示例

```sql
ANALYZE TABLE users;
```

优化器查询 SHOW INDEX 查看索引信息

```sql
SHOW INDEX FROM users;
```

#### 输出示例l

| Table | Non\_unique | Key\_name | Seq\_in\_index | Column\_name | Cardinality |
| ----- | ----------- | --------- | -------------- | ------------ | ----------- |
| users | 0           | PRIMARY   | 1              | id           | 1000000     |
| users | 1           | idx\_age  | 1              | age          | 10000       |

如何计算行数？

```sql
估算行数 = (总记录数 / 索引基数)
```

如果 users 表有 1000 万行，idx\_age 索引基数为 10000：

```sql
估算行数 = 10000000 / 10000 = 1000 行
```

➡ 查询 age = 25 可能返回 1000 行

### 2. 计算 IO 成本

索引存储在 B+ 树结构，MySQL 计算索引访问 IO

• 如果索引层级 = 3（即 root → 中间节点 → 叶子节点）

• 每次查询需要访问 3 层 B+ 树

计算公式

```
IO 成本 = B+ 树高度（索引层级）× 访问的索引页数
```

• PRIMARY KEY 查询：访问 1 条记录，IO 成本 ≈ 3

• 非唯一索引查询：访问 1000 行，IO 成本 ≈ 3 + 1000

### 3. 计算 CPU 成

CPU 成本主要来源于

1\. 索引行比较

2\. WHERE 过滤

3\. 排序（ORDER BY）

4\. 分组（GROUP BY）

计算公式：

```sql
CPU 成本 = (索引扫描行数 × 计算复杂度)
```

• PRIMARY KEY 查询 id=100

```sql
CPU 成本 ≈ 1 × 计算操作

```

• 非唯一索引 age=25（1000 行）

```sql
CPU 成本 ≈ 1000 × 计算操作

```

✅ MySQL 优化器更倾向于 访问行数少的索引。

## 4.计算案例：MySQL 选择哪个索引？

示例 1：查询 id = 100

```sql
SELECT * FROM users WHERE id = 100;
```

| 索引               | 行数估算 | IO 成本 | CPU 成本   | 总成本  |
| ---------------- | ---- | ----- | -------- | ---- |
| PRIMARY KEY (id) | 1 行  | 3     | 1 × 计算操作 | 最优 ✅ |

🔹 结论：使用 PRIMARY KEY（索引代价最小）

示例 2：查询 age = 25

```sql
SELECT * FROM users WHERE age = 25;
```

| 索引              | 行数估算       | IO 成本    | CPU 成本      | 总成本 |
| --------------- | ---------- | -------- | ----------- | --- |
| idx\_age        | 1000 行     | 3 + 1000 | 1000 × 计算操作 | 高 ❌ |
| FULL TABLE SCAN | 10000000 行 | 很高 ❌     | 很高 ❌        | 最差  |

🔹 结论：MySQL 选择 idx\_age，因为 比全表扫描便宜

## 5.如何优化索引选择？

### 1. 使用 EXPLAIN 分析索引选择

```sql
EXPLAIN SELECT * FROM users WHERE age = 25;
```

查看：

• 索引是否被正确使用

• rows 估算值

• possible\_keys 可选索引

### 2. 提高索引选择性（减少扫描行数）

索引 基数（Cardinality） 高的索引更优：

```sql
ALTER TABLE users ADD INDEX idx_email(email); 
```

• 比 age 选择性更高

### 3. 使用 覆盖索引 降低 IO 成本

```sql
CREATE INDEX idx_age_name ON users (age, name);
```

查询：

```sql
SELECT name FROM users WHERE age = 25;
```

• 索引中已有 age, name，无需回表，减少 IO

### 4. 避免索引失效

错误：

```sql
SELECT * FROM users WHERE LEFT(name, 3) = 'Tom';
```

✅ 优化：

```sql
SELECT * FROM users WHERE name LIKE 'Tom%';
```

## 6.总结

| 优化点           | 方式                    |
| ------------- | --------------------- |
| 减少 IO 成本      | 使用覆盖索引，减少回表操作         |
| 减少扫描行数        | 提高索引选择性（索引基数高）        |
| 避免索引失效        | 避免 LIKE '%xxx' / 函数索引 |
| 使用 EXPLAIN 分析 | 检查索引是否被优化器正确使用        |

🎯 MySQL 优化器会选择 IO + CPU 成本最低的索引，正确的索引设计可以极大提高查询性能！🚀
