# 覆盖索引（Covering Index） vs 索引下推（Index Condition Pushdown, ICP）

## 1.覆盖索引（Covering Index）

覆盖索引指的是 查询所需的字段全部在索引中，不需要回表（访问数据页），从而提高查询效率。

### 覆盖索引的优势

* 避免回表，所有查询数据都能从索引直接获取，减少磁盘 I/O。
* 查询速度更快，因为索引通常比数据页小，访问更快。
* 减少 InnoDB 二级索引的回表操作。

### 📌 示例

假设 users 表有如下结构：

```java
CREATE TABLE users (
    id INT PRIMARY KEY,
    name VARCHAR(100),
    age INT,
    city VARCHAR(100),
    INDEX idx_user (name, age, city)
);
```

执行 SQL：

```java
EXPLAIN SELECT name, age FROM users WHERE name = 'Alice' AND age = 25;
```

🔹 该查询使用索引 idx\_user(name, age, city)，且查询字段 name, age 都在索引中，因此形成 覆盖索引（Covering Index），避免回表。

#### 📌 EXPLAIN 结果

| id | select\_type | table | type | possible\_keys | key       | key\_len | ref   | rows | Extra       |
| -- | ------------ | ----- | ---- | -------------- | --------- | -------- | ----- | ---- | ----------- |
| 1  | SIMPLE       | users | ref  | idx\_user      | idx\_user | 30       | const | 1    | Using index |

💡 Using index 代表此查询为 覆盖索引，不需要回表，提高查询效率。

## 2.索引下推（Index Condition Pushdown, ICP）

索引下推（ICP）是 MySQL 5.6 引入的一种优化方式，它允许 MySQL 在存储引擎层（InnoDB）使用索引进行部分 WHERE 条件过滤，减少回表次数。

### 索引下推的作用

* 减少回表次数：先用索引过滤部分数据，减少回表的数量。
* 适用于范围查询、LIKE 前缀匹配。

### 📌 示例

```sql
EXPLAIN SELECT * FROM users WHERE name LIKE 'A%' AND age = 25;
```

🔹 该查询使用 idx\_user(name, age, city)，但 SELECT \* 需要回表取数据，MySQL 会利用索引下推，先用索引匹配 name LIKE 'A%'，再对 age = 25 进行过滤，减少回表数据量。

#### 📌 EXPLAIN 结果

| id | select\_type | table | type  | possible\_keys | key       | key\_len | ref  | rows | Extra                 |
| -- | ------------ | ----- | ----- | -------------- | --------- | -------- | ---- | ---- | --------------------- |
| 1  | SIMPLE       | users | range | idx\_user      | idx\_user | 30       | NULL | 100  | Using index condition |

💡 Using index condition 代表 索引下推（ICP）已生效，减少回表次数，提高查询效率。

## &#x20;3.总结：覆盖索引 vs. 索引下推

| **特性**         | **覆盖索引 (Covering Index)**                                        | **索引下推 (Index Condition Pushdown, ICP)**                 |
| -------------- | ---------------------------------------------------------------- | -------------------------------------------------------- |
| **作用**         | 直接使用索引获取数据，**不需要回表**                                             | 先用索引筛选部分数据，再进行回表查询                                       |
| **使用条件**       | **查询字段必须全部在索引中**                                                 | **索引范围查询 (LIKE 'A%'、BETWEEN、<、>)**                       |
| **优势**         | **避免回表，减少 I/O，查询更快**                                             | **减少回表次数，提高索引过滤能力**                                      |
| **适用场景**       | `SELECT name, age FROM users WHERE name = 'Alice' AND age = 25;` | `SELECT * FROM users WHERE name LIKE 'A%' AND age = 25;` |
| **EXPLAIN 标识** | `Using index`                                                    | `Using index condition`                                  |

## 结论

覆盖索引（Covering Index） 可以完全避免回表，适用于 查询字段全部在索引中的情况，效率最高。

索引下推（ICP） 适用于 范围查询，减少回表数据量，但仍可能需要回表。

优化建议：

* 尽量让查询字段在索引中，利用覆盖索引。
* 查询范围数据较多时，索引下推可以减少回表，提高效率。
