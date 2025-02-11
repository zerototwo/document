---
description: 在 MySQL 中，死锁（Deadlock）是指多个事务相互持有对方所需的资源，导致它们无法继续执行的情况。MySQL 提供了多个方法来分析和解决死锁问题。
cover: >-
  https://images.unsplash.com/photo-1735325332407-73571ee7477b?crop=entropy&cs=srgb&fm=jpg&ixid=M3wxOTcwMjR8MHwxfHJhbmRvbXx8fHx8fHx8fDE3MzkyNjUwNjZ8&ixlib=rb-4.0.3&q=85
coverY: 0
---

# MySQL 死锁分析方法

## 1.查看死锁日志

MySQL 通过 SHOW ENGINE INNODB STATUS 命令可以查看最近发生的死锁信息。

```sql
SHOW ENGINE INNODB STATUS
```

示例输出

```
------------------------
LATEST DETECTED DEADLOCK
------------------------
2024-02-11 10:15:25
*** (1) TRANSACTION:
TRANSACTION 12345, ACTIVE 5 sec
LOCK WAIT for TABLE `users` LOCK in mode IX
...
*** (2) TRANSACTION:
TRANSACTION 12346, ACTIVE 3 sec
LOCK WAIT for TABLE `orders` LOCK in mode IX
...
WE ROLL BACK TRANSACTION (2)
```

关键字段解释

* LATEST DETECTED DEADLOCK：最近一次死锁的信息。
* TRANSACTION 12345：涉及死锁的事务 ID。
* LOCK WAIT：等待的锁信息。
* WE ROLL BACK TRANSACTION (2)：MySQL 选择回滚的事务。

## 2.使用 INFORMATION\_SCHEMA.INNODB\_TRX 监控事务

可以查询 INNODB\_TRX 表，查找当前运行的事务及锁等待情况。

```sql
SELECT * FROM INFORMATION_SCHEMA.INNODB_TRX;
```

示例输出

| trx\_id | trx\_state | trx\_started        | trx\_wait\_started  | trx\_table\_locks |
| ------- | ---------- | ------------------- | ------------------- | ----------------- |
| 12345   | ACTIVE     | 2024-02-11 10:15:20 | 2024-02-11 10:15:23 | users             |
| 12346   | LOCK WAIT  | 2024-02-11 10:15:22 | 2024-02-11 10:15:25 | orders            |

关键字段

* trx\_id：事务 ID。
* trx\_state：事务状态（ACTIVE、LOCK WAIT）。
* trx\_wait\_started：事务开始等待锁的时间。
* trx\_table\_locks：事务锁定的表。

## 3.查询 INNODB\_LOCKS 和 INNODB\_LOCK\_WAITS

这两个表可以帮助我们找出锁依赖关系，分析死锁发生的原因。

```sql
SELECT * FROM INFORMATION_SCHEMA.INNODB_LOCKS;
SELECT * FROM INFORMATION_SCHEMA.INNODB_LOCK_WAITS;
```

示例输出

### 🔷 INNODB\_LOCKS （当前持有的锁）

| lock\_id | lock\_trx\_id | lock\_table | lock\_mode |
| -------- | ------------- | ----------- | ---------- |
| 1001     | 12345         | users       | IX         |
| 1002     | 12346         | orders      | IX         |

### 🔷 INNODB\_LOCK\_WAITS （锁等待）

| requesting\_trx\_id | requested\_lock\_id | blocking\_trx\_id |
| ------------------- | ------------------- | ----------------- |
| 12345               | 1002                | 12346             |
| 12346               | 1001                | 12345             |

分析

* 事务 12345 持有 users 表的锁，并等待 orders 表的锁。
* 事务 12346 持有 orders 表的锁，并等待 users 表的锁。
* 形成 循环等待，导致死锁。

## 2.如何避免死锁？

### 1.调整事务执行顺序

* 统一事务的访问顺序，避免循环等待。
* 例如，所有事务都先更新 users 表，再更新 orders 表。

### 2.合理使用索引

* 确保 WHERE 条件命中索引，避免意外的行锁升级为表锁。
* 执行 EXPLAIN 检查 SQL 是否使用索引。

```sql
EXPLAIN SELECT * FROM users WHERE id = 1 FOR UPDATE;
```

### 3.减少事务粒度

* 尽量缩短事务的执行时间，避免长时间持有锁。
* 避免 SELECT ... FOR UPDATE 过多锁定数据。

### 4.使用 NOWAIT 或 SKIP LOCKED

* NOWAIT：如果锁不可用，则立即失败，不等待。
* SKIP LOCKED：跳过已锁定的行，不等待。

```sql
SELECT * FROM users WHERE status = 'pending' FOR UPDATE NOWAIT;
SELECT * FROM users WHERE status = 'pending' FOR UPDATE SKIP LOCKED;
```

### 5.分批提交

例如，每次插入 1000 条数据后提交事务，减少锁竞争。

```sql
START TRANSACTION;
INSERT INTO orders (...) VALUES (...);
COMMIT;
```

## 总结

### 1.检测死锁

* SHOW ENGINE INNODB STATUS;
* INFORMATION\_SCHEMA.INNODB\_TRX
* NNODB\_LOCKS & INNODB\_LOCK\_WAITS

### 2.分析死锁

* 事务锁等待关系
* 是否存在循环等待
* 锁的模式（行锁、表锁、意向锁）

### 3.优化死锁

* 统一事务访问顺序
* 使用索引优化 SQL
* 减少事务粒度
* NOWAIT / SKIP LOCKED
* 分批提交事务







