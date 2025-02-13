---
description: SQL 优化涉及 索引优化、查询优化、事务优化、数据库设计、并发优化 等多个方面
cover: >-
  https://images.unsplash.com/photo-1735657061792-9a8221a7144b?crop=entropy&cs=srgb&fm=jpg&ixid=M3wxOTcwMjR8MHwxfHJhbmRvbXx8fHx8fHx8fDE3Mzk0Mzk5NDN8&ixlib=rb-4.0.3&q=85
coverY: 0
---

# SQL 优化

## 1.索引优化

索引是提高查询性能的关键。优化索引可以大幅提升数据查询效率，但使用不当可能导致性能下降。

### 1.1索引基础

* 主键索引（PRIMARY KEY）：唯一标识表中的一行，自动创建聚簇索引（InnoDB）。
* 唯一索引（UNIQUE INDEX）：保证列值唯一，适用于唯一性约束字段（如邮箱、身份证）。
* 普通索引（INDEX）：加速查询，但不保证唯一性。
* 全文索引（FULLTEXT）：适用于全文检索，如文章内容搜索。
* 空间索引（SPATIAL INDEX）：适用于地理位置相关数据。

### 1.2索引优化

#### (1)最左匹配原则

* 联合索引 的查询必须遵循最左匹配原则，否则索引可能失效。

例如：CREATE INDEX idx\_user ON users(name, age, city);

* ✅ WHERE name = 'Alice' AND age = 25
* ❌ WHERE age = 25 AND city = 'Paris'（跳过 name）

#### (2)索引的失效场景

**以下情况索引可能会失效**

* LIKE '%abc'（前导 % 导致索引失效）
* OR 连接的字段未建立索引
* 对索引字段进行计算或函数操作（如 WHERE YEAR(create\_time) = 2023）
* 隐式类型转换（WHERE phone = 1234567890 但 phone 是 VARCHAR）

#### (3)覆盖索引

* 查询字段 全部在索引中，无需回表查询数据，提高查询效率。

```sql
SELECT name, age FROM users WHERE name = 'Alice';
```

* ✅ 索引覆盖，Extra 显示 Using index
* ❌ 未覆盖，需要回表

#### (4)索引下推（Index Condition Pushdown, ICP）

* MySQL 5.6+ 优化 LIKE 'A%'、BETWEEN、<、> 查询，减少回表次数。
* EXPLAIN 显示 Using index condition 说明索引下推生效。

## 2.查询优化

### 2.1EXPLAIN 执行计划

SQL 执行优化的核心工具

```sql
EXPLAIN SELECT * FROM users WHERE name = 'Alice';
```

**关键字段解释**

* type：访问类型（ALL、index、range、ref、const 等）
* possible\_keys：可能使用的索引
* key：实际使用的索引
* rows：扫描的行数（越少越好）

Extra：

* Using index（覆盖索引）
* Using index condition（索引下推）
* Using filesort（可能存在排序操作）
* Using temporary（可能创建临时表）

### 2.2查询优化技巧

#### (1)避免 SELECT ，指定查询字段

* SELECT \* 可能导致 回表查询，影响查询效率。

```sql
SELECT id, name FROM users WHERE name = 'Alice';
```

#### (2)避免 OR，使用 UNION ALL 代替

* OR 可能导致索引失效，应拆分成 UNION ALL

```sql
SELECT * FROM users WHERE name = 'Alice'
UNION ALL
SELECT * FROM users WHERE age = 25;
```

#### (3)分页查询优化

* 避免 LIMIT 100000, 10 造成 深度分页性能下降

```sql
SELECT * FROM users WHERE id >= (SELECT id FROM users ORDER BY id LIMIT 100000, 1) LIMIT 10;
```

#### (4)ORDER BY + GROUP BY 优化

* 避免 Using filesort
* ORDER BY 尽量使用索引

```sql
SELECT * FROM users ORDER BY create_time DESC LIMIT 10;
```

## 3.事务与锁优化

事务优化主要关注 锁的使用、死锁排查、并发控制。

## 3.1事务隔离级别

* READ UNCOMMITTED（读取未提交数据）
* READ COMMITTED（防止脏读）
* REPEATABLE READ（MySQL 默认，防止脏读 & 不可重复读）
* SERIALIZABLE（最高隔离级别，但性能最低）

### 3.2锁的优化

#### (1)表级锁 vs 行级锁

* 表级锁（MyISAM）：并发低，锁全表
* 行级锁（InnoDB）：支持事务，并发性能高

#### (2)间隙锁（Gap Lock）

* 防止幻读，但可能造成 死锁

#### (3)如何减少锁冲突

* 使用 SELECT … FOR UPDATE 避免锁冲突
* 合理拆分事务，减少锁持有时间
* 使用 MVCC 读已提交数据，减少锁竞争

## 4.数据库设计优化

### 4.1 规范化设计

* 第一范式（1NF）：字段原子性
* 第二范式（2NF）：消除非主键依赖
* 第三范式（3NF）：消除传递依赖

### 4.2反规范化优化

* 适当冗余，减少复杂查询
* 分库分表，提高可扩展性

## 5.并发优化

### 5.1读写分离

* 读请求走 从库，写请求走 主库
* MySQL 主从复制（binlog 复制）

### 5.2分库分表

* 分库：按业务拆分（订单、用户数据分开）
* 分表：哈希分表（user\_id % 10）

## 6.MySQL 高并发优化策略

### 6.1连接优化

* 减少数据库连接数
* 使用连接池（HikariCP、Druid）

### 6.2缓存优化

* 使用 Redis 作为缓存
* MySQL 查询缓存（MySQL 8.0 已移除）
* CDN + 负载均衡

## 总结

SQL 优化涉及 索引优化、查询优化、事务优化、数据库设计、并发优化 等多个方面。掌握 EXPLAIN 执行计划、索引优化、事务与锁、高并发架构













