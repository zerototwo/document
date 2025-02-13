---
description: 事务和锁的优化是 SQL 优化的关键部分，影响数据库的 并发性能、吞吐量 和 数据一致性。合理优化事务和锁可以减少阻塞，提高查询效率。
cover: >-
  https://images.unsplash.com/photo-1735586971748-96f7425c0162?crop=entropy&cs=srgb&fm=jpg&ixid=M3wxOTcwMjR8MHwxfHJhbmRvbXx8fHx8fHx8fDE3Mzk0NTQxNzN8&ixlib=rb-4.0.3&q=85
coverY: 0
---

# 事务与锁优化（Transaction & Lock Optimization）

## 1.事务优化（Transaction Optimization）

### 🔹 问题

* 事务执行时间长，会 阻塞 其他事务，影响并发性能。
* 事务涉及大量行锁，可能导致 死锁 或 锁等待。
* 大事务回滚成本高，导致 Undo Log 和 Redo Log 负担加重。

### ✅ 优化方式

**🔹 (1) 事务尽量短，减少锁占用时间**

* 问题：事务时间过长，容易导致大量锁资源被占用，影响其他事务。
* 优化：尽量缩短事务逻辑，只包含必须的 SQL 语句。

✅ 优化示例：

```sql
-- 错误示例：事务时间长，影响并发性能
START TRANSACTION;
UPDATE orders SET status = 'shipped' WHERE id = 1;
DO SLEEP(5); -- 假设这里有复杂的业务逻辑
UPDATE inventory SET stock = stock - 1 WHERE product_id = 100;
COMMIT;

-- 正确优化：减少事务时间
START TRANSACTION;
UPDATE orders SET status = 'shipped' WHERE id = 1;
UPDATE inventory SET stock = stock - 1 WHERE product_id = 100;
COMMIT;
```

**🔹 (2) 业务逻辑与事务分离**

* 问题：事务中包含大量的计算和业务逻辑，导致事务执行时间长。
* 优化：先执行查询和计算，然后再开始事务执行数据更新。

✅ 优化示例

```sql
-- 错误示例：事务中包含查询和业务逻辑，导致事务时间长
START TRANSACTION;
SELECT balance FROM accounts WHERE id = 1; -- 查询账户余额
IF balance >= 100 THEN -- 业务逻辑判断
    UPDATE accounts SET balance = balance - 100 WHERE id = 1;
    INSERT INTO transactions (user_id, amount) VALUES (1, -100);
END IF;
COMMIT;

-- 正确优化：
SELECT balance FROM accounts WHERE id = 1; -- 先查询余额
IF balance >= 100 THEN
    START TRANSACTION;
    UPDATE accounts SET balance = balance - 100 WHERE id = 1;
    INSERT INTO transactions (user_id, amount) VALUES (1, -100);
    COMMIT;
END IF;
```

**🔹 (3) 事务中避免使用不必要的 SELECT**

* 问题：如果 SELECT 查询的字段不需要事务保护，则应放到事务之外执行。
* 优化：尽量避免在事务中执行 SELECT \* FROM table，只查询必要的字段。

✅ 优化示例

```sql
-- 错误示例：事务中执行不必要的 SELECT，增加锁竞争
START TRANSACTION;
SELECT * FROM users WHERE id = 1;
UPDATE users SET balance = balance - 100 WHERE id = 1;
COMMIT;

-- 正确优化：查询在事务外执行
SELECT balance FROM users WHERE id = 1;
START TRANSACTION;
UPDATE users SET balance = balance - 100 WHERE id = 1;
COMMIT;
```

## 2.锁优化（Lock Optimization）

### 🔹 问题

* 锁粒度太大（表锁）影响并发性能。
* 不合理的索引可能导致锁范围扩大。
* 锁等待和死锁影响数据库吞吐量。

### ✅ 优化方式

#### **🔹 (1) 优先使用行锁，避免表锁**

* 问题：MyISAM 只支持 表级锁，导致并发低。InnoDB 支持 行锁，但不合理使用可能会升级为表锁。
* 优化：使用 InnoDB 存储引擎，并尽量减少不必要的表锁。

✅ 优化示例

```sql
-- 错误示例：MyISAM 表锁，所有用户更新时只能串行执行
LOCK TABLES users WRITE;
UPDATE users SET balance = balance - 100 WHERE id = 1;
UNLOCK TABLES;

-- 正确优化：使用 InnoDB 事务，行锁提高并发
START TRANSACTION;
UPDATE users SET balance = balance - 100 WHERE id = 1;
COMMIT;
```

#### 🔹 (2) 合理选择锁模式

MySQL 锁分为：

* 共享锁 (S 锁)：用于 SELECT ... LOCK IN SHARE MODE
* 排他锁 (X 锁)：用于 SELECT ... FOR UPDATE
* 意向锁 (IS/IX)：用于标记表级别意图，减少锁冲突

✅ 优化示例

```sql
-- 共享锁：其他事务可以并发读取，但不能修改
SELECT * FROM orders WHERE id = 1 LOCK IN SHARE MODE;

-- 排他锁：其他事务不能读取或修改
SELECT * FROM orders WHERE id = 1 FOR UPDATE;
```

#### 🔹 (3) 让索引避免间隙锁（Gap Lock）

* 问题：Range Scan 会导致 Next-Key Lock（间隙锁），影响并发。
* 优化：使用唯一索引，减少不必要的间隙锁。

✅ 优化示例

```sql
-- 错误示例：范围查询，导致间隙锁
SELECT * FROM orders WHERE order_date > '2024-01-01' FOR UPDATE;

-- 正确优化：使用唯一索引，避免间隙锁
SELECT * FROM orders WHERE id = 100 FOR UPDATE;
```

#### 🔹 (4) 事务提交前释放不必要的锁

* 问题：事务中可能不必要地保持锁，影响并发。
* 优化：事务执行完毕后，尽快 COMMIT 或 ROLLBACK 释放锁。

✅ 优化示例

```sql
-- 错误示例：事务未及时提交，占用锁资源
START TRANSACTION;
UPDATE orders SET status = 'shipped' WHERE id = 1;
DO SLEEP(5);  -- 业务逻辑阻塞，导致锁竞争
COMMIT;

-- 正确优化：
START TRANSACTION;
UPDATE orders SET status = 'shipped' WHERE id = 1;
COMMIT;
```

#### 🔹 (5) 避免死锁

* 问题：多个事务相互等待锁资源，造成死锁。
* 优化：

尽量让事务按照相同的顺序访问表，减少死锁概率。

分批处理数据，避免长时间占用锁。



✅ 优化示例

```sql
-- 错误示例：事务访问顺序不同，可能导致死锁
START TRANSACTION;
UPDATE users SET balance = balance - 100 WHERE id = 1;
UPDATE accounts SET balance = balance + 100 WHERE user_id = 1;
COMMIT;

START TRANSACTION;
UPDATE accounts SET balance = balance + 100 WHERE user_id = 1;
UPDATE users SET balance = balance - 100 WHERE id = 1;
COMMIT;

-- 正确优化：确保事务访问表的顺序一致
START TRANSACTION;
UPDATE users SET balance = balance - 100 WHERE id = 1;
UPDATE accounts SET balance = balance + 100 WHERE user_id = 1;
COMMIT;
```

## 总结

### ✅ 事务优化

1. 缩短事务时间，减少锁持有时间。
2. 业务逻辑与事务分离，减少不必要的锁等待。
3. 事务中避免不必要的 SELECT，提高性能。

✅ 锁优化

1. 避免表锁，优先使用行锁（InnoDB）。
2. 合理选择锁模式，避免不必要的 FOR UPDATE。
3. 减少间隙锁，使用唯一索引。
4. 事务执行完毕，及时 COMMIT，释放锁资源。
5. 避免死锁，确保事务按照相同顺序访问表。



