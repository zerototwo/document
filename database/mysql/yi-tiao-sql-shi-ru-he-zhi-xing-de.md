---
cover: >-
  https://images.unsplash.com/photo-1736252622821-a9b1bb262a57?crop=entropy&cs=srgb&fm=jpg&ixid=M3wxOTcwMjR8MHwxfHJhbmRvbXx8fHx8fHx8fDE3MzkwOTkzNzJ8&ixlib=rb-4.0.3&q=85
coverY: 0
---

# 一条 SQL 是如何执行的？

## SQL 执行流程（整体步骤）

假设有这样一条查询：

```java
SELECT * FROM users WHERE id = 1;
```

MySQL 执行这条 SQL 的过程如下：

<figure><img src="../../.gitbook/assets/image (2).png" alt=""><figcaption></figcaption></figure>

## 1.客户端连接

客户端（如 MySQL 客户端、Java 代码、PHP 代码）发送 SQL 查询到 MySQL 连接管理模块。

* 检查权限：用户身份认证，验证是否有权限执行该 SQL 语句。
* 查询缓存检查（MySQL 5.7 及以前）：

如果命中缓存：直接返回结果，MySQL 8.0 取消了查询缓存。

未命中缓存：进入 SQL 解析阶段。

## 2.解析器（Parser）

* 词法分析：将 SQL 拆分为关键字（如 SELECT、FROM、WHERE）。
* 语法分析：检查 SQL 语句是否符合 MySQL 语法。

## 3.查询优化器（Optimizer）

查询优化器的作用：

1. 选择最优执行计划（决定如何执行 SQL）。
2. 选择最优索引（避免全表扫描，提高查询速度）。
3. 优化 SQL 语句：

* 等值条件优化：如 WHERE id = 1，优先使用主键索引。
* 排序优化：避免 ORDER BY 触发文件排序（避免 Using filesort）。
* 子查询优化：将子查询转换为 JOIN 提高性能。

### 示例：优化器优化 SQL

```java
SELECT * FROM users WHERE age > 20 ORDER BY age;
```

优化器可能会选择不同的执行计划：

1. 全表扫描（慢）
2. 使用索引（快）

age 列如果有索引，优化器会选择 索引扫描 而不是 全表扫描。

## 4.执行器（Executor）

* 调用存储引擎 API 进行数据查询（如 InnoDB）。
* 读取数据并返回给客户端。

### 示例：SQL 执行流程

```sql
SELECT * FROM users WHERE id = 1;
```

1. 解析 SQL 语法
2. 优化器选择 PRIMARY KEY 索引
3. 执行器调用 InnoDB，按照 id = 1 定位数据
4. 返回查询结果

## 总结

### SQL 执行流程

1. 客户端连接（权限认证）。
2. 查询缓存检查（MySQL 8.0 取消了查询缓存）。
3. 解析器解析 SQL 语法（词法分析、语法分析）。
4. 查询优化器选择最优执行计划（索引选择、排序优化）。
5. 执行器执行 SQL，调用存储引擎。
6. 存储引擎返回数据（如 InnoDB）。

### 查询优化器的作用

* 选择最优索引，避免全表扫描。
* 优化 JOIN 查询，提高查询性能。
* 优化 ORDER BY，避免文件排序 (Using filesort)。
* 减少磁盘 I/O，提升 SQL 执行效率。







