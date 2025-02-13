---
description: >-
  SQL 查询优化是数据库性能优化的重要环节，主要涉及如何减少查询的执行时间，提高数据库的吞吐量。查询优化可以从多个方面入手，包括索引优化、SQL
  语句改写、避免不必要的计算、减少锁争用等
---

# 查询优化（SQL Query Optimization）

## 1.避免 SELECT \*

### 🔹 原因：

* SELECT \* 会返回表中所有列，可能会查询大量不必要的数据，增加 I/O 和内存消耗。
* 影响索引优化，可能导致无法使用 覆盖索引（Covering Index）。
* 可能增加数据传输的网络开销，影响查询效率。

### ✅ 优化方式

* 仅查询必要的字段，例如：

```sql
SELECT id, name, age FROM users WHERE id = 1;
```

## 2.WHERE 条件优化

### 🔹 原因：

* WHERE 条件的顺序和优化策略会影响 SQL 的执行计划。
* 不合理的条件可能导致全表扫描，而不是索引扫描。

### ✅ 优化方式

* 索引优化：确保 WHERE 子句使用索引字段。
* 避免函数运算：避免对索引列进行计算或函数操作，否则索引无法生效：

```sql
-- 错误示例：会导致全表扫描
SELECT * FROM users WHERE YEAR(created_at) = 2024;

-- 正确优化：使用范围查询
SELECT * FROM users WHERE created_at BETWEEN '2024-01-01' AND '2024-12-31';
```

### 避免隐式转换

```sql
-- 错误示例：索引失效，因 `id` 是 INT，但传入字符串
SELECT * FROM users WHERE id = '100';

-- 正确优化：
SELECT * FROM users WHERE id = 100;

```

## 3.避免使用 OR，改用 UNION ALL / IN

### 🔹 原因：

* OR 可能导致索引失效，影响查询效率。

### ✅ 优化方式

* 改用 IN 代替 OR：

```sql
-- 错误示例：
SELECT * FROM users WHERE id = 1 OR id = 2 OR id = 3;

-- 正确优化：
SELECT * FROM users WHERE id IN (1, 2, 3);
```

使用 UNION ALL 替代 OR：

```sql
-- 错误示例：
SELECT * FROM users WHERE age = 20 OR name = 'Alice';

-- 正确优化：
SELECT * FROM users WHERE age = 20
UNION ALL
SELECT * FROM users WHERE name = 'Alice';
```

## 4.LIMIT 进行分页优化

### 🔹 问题：

* LIMIT 可能会导致 查询效率低下，特别是 LIMIT N, M 形式，数据库仍需要扫描前 N+M 条数据。

### ✅ 优化方式

使用索引进行分页：

```sql
-- 错误示例：
SELECT * FROM users ORDER BY created_at LIMIT 100000, 10;

-- 正确优化：基于索引查询
SELECT * FROM users WHERE id > 100000 ORDER BY created_at LIMIT 10;
```

## 5.JOIN 关联查询优化

### 🔹 原因：

* 避免笛卡尔积：如果 JOIN 语句没有 ON 连接条件，可能导致大量无用数据产生。
* 小表驱动大表：尽量让数据量小的表作为驱动表，减少扫描次数。

### ✅ 优化方式

* 确保 ON 连接字段有索引：

```sql
-- 错误示例：没有索引，可能导致全表扫描
SELECT * FROM orders o
JOIN users u ON o.user_id = u.id;

-- 正确优化：为 `user_id` 和 `id` 添加索引
CREATE INDEX idx_user_id ON orders(user_id);
CREATE INDEX idx_id ON users(id);
```

## 6.使用覆盖索引（Covering Index）

### 🔹 原理：

* 覆盖索引 指的是索引包含了查询的所有字段，避免回表，提高查询效率。

### ✅ 优化方式

* 创建合适的索引

```sql
-- 假设查询如下：
SELECT id, name FROM users WHERE age = 30;

-- 仅 age 有索引时，仍需要回表：
CREATE INDEX idx_age ON users(age);

-- 创建联合索引，避免回表：
CREATE INDEX idx_age_name ON users(age, name);
```

查看 EXPLAIN 是否显示 Using index

```sql
EXPLAIN SELECT id, name FROM users WHERE age = 30;
```

## 7.优化 GROUP BY / DISTINCT

### 🔹 问题：

* GROUP BY 和 DISTINCT 可能导致排序和文件临时表，影响性能。

### ✅ 优化方式

* 避免 ORDER BY 影响 GROUP BY：

```sql
-- 错误示例：
SELECT age, COUNT(*) FROM users GROUP BY age ORDER BY age;

-- 正确优化：
SELECT age, COUNT(*) FROM users GROUP BY age;
```

使用索引优化 GROUP BY

```sql
CREATE INDEX idx_age ON users(age);
```

## 8.避免 ORDER BY 影响性能

### 🔹 问题：

* ORDER BY 可能导致数据库需要 额外的排序操作，影响性能。

✅ 优化方式

* 利用索引排序

```sql
-- 错误示例：
SELECT * FROM users ORDER BY created_at DESC;

-- 正确优化：
CREATE INDEX idx_created_at ON users(created_at DESC);
```

* 使用 LIMIT 避免大数据排序

```sql
-- 错误示例：
SELECT * FROM orders ORDER BY amount DESC;

-- 正确优化：
SELECT * FROM orders ORDER BY amount DESC LIMIT 100;
```

## 9.优化 EXISTS 与 NOT EXISTS

### 🔹 问题：

* NOT IN 可能导致全表扫描，影响查询性能。

### ✅ 优化方式

* 使用 EXISTS 代替 NOT IN

```sql
-- 错误示例：
SELECT * FROM users WHERE id NOT IN (SELECT user_id FROM orders);

-- 正确优化：
SELECT * FROM users u WHERE NOT EXISTS (
  SELECT 1 FROM orders o WHERE o.user_id = u.id
);
```

## 结论

SQL 查询优化的核心思想是 减少不必要的计算，充分利用索引，减少锁竞争，并 优化 SQL 语句结构。通过 EXPLAIN 语句分析执行计划，能够有效发现 SQL 语句的性能瓶颈，并针对性优化。





