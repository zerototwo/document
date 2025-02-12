---
description: >-
  MySQL 提供 全局锁（Global Lock）、表级锁（Table Lock）、行级锁（Row Lock）
  三种不同粒度的锁机制，不同锁粒度适用于不同的业务场景。
cover: >-
  https://images.unsplash.com/photo-1735661998642-71a998eaf912?crop=entropy&cs=srgb&fm=jpg&ixid=M3wxOTcwMjR8MHwxfHJhbmRvbXx8fHx8fHx8fDE3MzkzNjM4NjZ8&ixlib=rb-4.0.3&q=85
coverY: 0
---

# 锁的粒度分类（全局锁、表级锁、行级锁）

## 1.全局锁（Global Lock）

### 概念

* 全局锁作用于整个数据库，一旦加锁，所有表的数据都不能进行写操作，只允许 SELECT 查询。
* 适用于数据库一致性备份，确保备份过程中不会有数据变更。

### 使用方式

```sql
FLUSH TABLES WITH READ LOCK;  -- 给整个数据库加全局锁
UNLOCK TABLES;  -- 释放全局锁
```

### ✅ 优点

* 确保备份数据一致性，防止备份过程中数据发生变化。
* 适用于 MyISAM，因其不支持事务，必须加全局锁确保一致性。

### ❌ 缺点

* 影响整个数据库的写入操作，所有事务的 INSERT、UPDATE、DELETE 语句都会被阻塞，影响并发性能。
* 不适用于 InnoDB，因为 InnoDB 事务支持 MVCC（多版本并发控制），可以通过快照读避免加全局锁。

### 面试常见问题

**1.全局锁适用于哪些场景？**

* 全库备份：MyISAM 表在 mysqldump 备份时默认使用全局锁，确保备份期间数据一致。
* 临时防止数据修改，确保某些查询操作期间数据不会变动。

**2.如何避免在 InnoDB 备份时使用全局锁？**

* 使用 mysqldump --single-transaction，基于 MVCC 实现一致性备份，不影响数据库写入

```sh
mysqldump --single-transaction -uroot -p database_name > backup.sql
```

## 2.表级锁（Table Lock）

### 概念

* 表级锁是 作用于单张表 的锁。
* MySQL MyISAM 存储引擎默认使用表级锁，而 InnoDB 也会在某些操作（如 ALTER TABLE）中使用表级锁。

### 使用方式

```sql
LOCK TABLES users READ;   -- 锁定 users 表，允许其他事务读取，但不能写入
LOCK TABLES users WRITE;  -- 锁定 users 表，其他事务不能读取也不能写入
UNLOCK TABLES;  -- 释放表锁
```

### ✅ 优点

* 开销小，管理简单，适用于 读多写少 的场景，如报表、日志存储等。
* 避免死锁，因为锁定的是整个表，不涉及行级锁导致的死锁问题。

### ❌ 缺点

* 影响并发性能，当表被锁住后，其他事务只能等待锁释放，无法执行写操作。
* 适用于 MyISAM，但不适用于 InnoDB，因为 MyISAM 不支持行级锁。

### 1.MyISAM 为什么使用表级锁？

* MyISAM 不支持事务，表级锁简单高效，适用于 日志存储、全文索引。
* 但写操作时，并发性能较差，因为写入会锁定整个表。

### 2.如何避免表级锁带来的并发问题？

* 使用 InnoDB 代替 MyISAM，InnoDB 支持行级锁，提高并发性能。
* 优化索引，防止查询触发表级锁，如：

```sql
ALTER TABLE users ADD INDEX idx_name(name);
```

## 3.行级锁（Row Lock）

### 概念

* 行级锁作用于单行记录，是 InnoDB 默认锁机制，通过索引访问的记录才会加行级锁。
* 行级锁使得并发操作更加高效，多个事务可以并发操作不同的行，而不会互相阻塞。

### 使用方式

```sql
SELECT * FROM users WHERE id = 1 FOR UPDATE;  -- 排他锁，其他事务不能修改该行
SELECT * FROM users WHERE id = 1 LOCK IN SHARE MODE;  -- 共享锁，其他事务可以读但不能改
```

### ✅ 优点

* 支持高并发，多个事务可以同时操作不同的行，提高数据库吞吐量。
* 适用于事务处理，如银行转账、订单管理等业务场景。

### ❌ 缺点

* 行锁开销大，每次加锁和释放锁都需要额外的存储和计算资源。
* 容易发生死锁，当多个事务以不同顺序锁定行数据时，可能会导致死锁。

### 面试常见问题

#### 1.如何查看当前有哪些行锁？

```sql
SELECT * FROM information_schema.INNODB_LOCKS;
```

#### 2.如何避免行级锁导致的死锁？

* 使用索引优化查询，减少锁定的行数

```sql
SELECT * FROM users WHERE id = 1 FOR UPDATE;
```

* 控制事务的访问顺序，防止多个事务相互等待不同的锁。
* 降低事务执行时间，减少锁持有的时间，提高并发能力。

## 总结

| 锁类型     | 作用范围  | 特点             | 适用场景                   | 示例                                             |
| ------- | ----- | -------------- | ---------------------- | ---------------------------------------------- |
| **全局锁** | 整个数据库 | 阻塞所有写入，适用于全库备份 | **全库备份**，MyISAM 数据库一致性 | `FLUSH TABLES WITH READ LOCK;`                 |
| **表级锁** | 单张表   | 影响整张表，不支持高并发   | **MyISAM、日志存储**        | `LOCK TABLES users READ;`                      |
| **行级锁** | 单行记录  | 并发能力最强，适用于事务   | **高并发写入**，如金融、电商订单系统   | `SELECT * FROM users WHERE id = 1 FOR UPDATE;` |

