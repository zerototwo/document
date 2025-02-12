---
description: >-
  在 MySQL InnoDB 存储引擎中，为了支持 事务隔离 和 并发控制，实现了多种不同类型的锁。其中，间隙锁（Gap Lock）、记录锁（Record
  Lock） 和 临键锁（Next-Key Lock） 是 MySQL 行级锁（Row-Level Lock） 的重要组成部分。
---

# 间隙锁（Gap Lock）、记录锁（Record Lock）、临键锁（Next-Key Lock）

## 1.记录锁（Record Lock）

### 定义

记录锁（Record Lock）仅锁定索引中的某一条具体记录，不会锁住前后范围的记录。

### 作用

* 主要用于保证数据一致性，防止两个事务同时修改同一条记录。
* 只锁定匹配的索引行，不会影响周围的间隙。

### 适用场景

* 当 WHERE 条件精确匹配索引时，InnoDB 只会对查询到的具体行加锁。
* 适用于**READ COMMITTED** 和 REPEATABLE READ 隔离级别。

### 示例

场景 1：使用 FOR UPDATE 加锁

```sql
SELECT * FROM users WHERE id = 10 FOR UPDATE;
```

* 效果：id=10 这行记录被加锁，其他事务不能修改或删除这条记录，但仍可插入新的记录。
* 不会锁住 id=9 或 id=11。

场景 2：多个事务操作同一行

```sql
-- 事务 A
START TRANSACTION;
SELECT * FROM users WHERE id = 10 FOR UPDATE;

-- 事务 B
START TRANSACTION;
UPDATE users SET age = 35 WHERE id = 10; -- ❌ 阻塞，等待事务 A 提交
```

事务 A 对 id=10 上了记录锁，事务 B 只能等事务 A 提交后才能执行修改。

## 2.间隙锁（Gap Lock）

### 定义

间隙锁（Gap Lock）锁定索引间的空隙，即使该间隙内没有数据，也会被锁住。

### 作用

* 防止幻读（Phantom Read），确保事务在执行过程中，数据的范围查询保持一致性。
* 适用于 REPEATABLE READ 隔离级别（MySQL 默认隔离级别）。
* 防止其他事务在锁定范围内插入新记录，但不影响已存在的记录更新。

### 适用场景

* 适用于范围查询，例如 BETWEEN、>、<。
* 只有 REPEATABLE READ 级别会使用，READ COMMITTED 隔离级别不会使用间隙锁。

### 示例

**场景 1：使用范围查询 FOR UPDATE**

```sql
SELECT * FROM users WHERE age BETWEEN 25 AND 30 FOR UPDATE;
```

**锁定范围 (25,30]，即使范围内没有数据，也会锁住该区间，防止其他事务插入新数据。**

**场景 2：事务阻塞**

```sql
-- 事务 A
START TRANSACTION;
SELECT * FROM users WHERE age > 25 FOR UPDATE;

-- 事务 B
START TRANSACTION;
INSERT INTO users (name, age) VALUES ('Tom', 28); -- ❌ 阻塞，等待事务 A 提交
```

**事务 A 锁住 age > 25 的间隙，事务 B 试图插入 age=28 失败，必须等待事务 A 结束。**

注意

* READ COMMITTED 隔离级别不会使用间隙锁，因此不会阻止新数据插入，但可能导致幻读。

## 3.临键锁（Next-Key Lock）

### 定义

临键锁（Next-Key Lock）= 记录锁 + 间隙锁，锁定当前索引记录 + 前后间隙，防止 幻读。

### 作用

* 防止幻读，保证 REPEATABLE READ 隔离级别的 一致性。
* 适用于 索引范围扫描，确保事务查询到的范围内数据不会发生变化。

### 适用场景

* 事务执行索引范围扫描时，InnoDB 会默认使用 Next-Key Lock 。
* 默认在 REPEATABLE READ 级别启用。

### 示例

**场景 1：索引范围查询**

```sql
SELECT * FROM users WHERE age = 30 FOR UPDATE;
```

**锁定的范围**

* age=30 的记录（记录锁）。
* age > 30 之间的间隙（间隙锁），防止新数据插入。

**场景 2：事务冲突**

```sql
-- 事务 A
START TRANSACTION;
SELECT * FROM users WHERE age = 30 FOR UPDATE;

-- 事务 B
START TRANSACTION;
INSERT INTO users (name, age) VALUES ('Jack', 31); -- ❌ 阻塞
```

事务 A 使用 Next-Key Lock 锁住了 age=30 及其后面的间隙，导致事务 B 无法插入 age=31。



## 4.对比总结

| **锁类型**                | **作用**                | **影响范围**        | **适用事务隔离级别**                         | **适用场景**                        |
| ---------------------- | --------------------- | --------------- | ------------------------------------ | ------------------------------- |
| **记录锁（Record Lock）**   | 锁定**单行记录**，防止并发修改     | 仅锁住**索引匹配的行**   | `READ COMMITTED` & `REPEATABLE READ` | 精确 `WHERE` 查询，如 `WHERE id = 10` |
| **间隙锁（Gap Lock）**      | 防止 **幻读**，**禁止新数据插入** | 锁住**索引间的空隙**    | `REPEATABLE READ`                    | `WHERE age > 25 FOR UPDATE`     |
| **临键锁（Next-Key Lock）** | **记录锁 + 间隙锁**，防止幻读    | 锁住**索引记录及前后间隙** | `REPEATABLE READ`                    | `WHERE age = 30 FOR UPDATE`     |

## 5.如何优化锁的使用

**避免不必要的锁**

* 使用 READ COMMITTED 级别，避免 Gap Lock 影响插入数据。
* 使用 UNIQUE INDEX 让 MySQL 只使用记录锁，不使用间隙锁。

**索引优化**

* 尽量用 主键 或 唯一索引 进行查询，避免范围锁 (Gap Lock / Next-Key Lock) 影响插入数据。
* 分批插入数据，减少锁冲突。

**事务控制**

* 尽量缩短事务时间，避免长期持有锁导致的阻塞。
* 合理使用 LOCK IN SHARE MODE 和 FOR UPDATE 控制锁粒度。

## 6.总结

* 记录锁（Record Lock）：只锁定单条数据，避免并发写入冲突。
* 间隙锁（Gap Lock）：锁住索引间的空隙，防止幻读，影响插入操作。
* 临键锁（Next-Key Lock）：记录锁 + 间隙锁，防止幻读，默认 REPEATABLE READ 级别使用。

