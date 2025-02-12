---
cover: >-
  https://images.unsplash.com/photo-1738667379581-a02dd0f0bfe5?crop=entropy&cs=srgb&fm=jpg&ixid=M3wxOTcwMjR8MHwxfHJhbmRvbXx8fHx8fHx8fDE3MzkyNjM3ODJ8&ixlib=rb-4.0.3&q=85
coverY: 0
---

# 锁机制

## 1.按模式分类（乐观锁 vs 悲观锁）

### 乐观锁（Optimistic Lock）

* 适用于读多写少的场景，不加锁，而是通过 版本号 或 时间戳 来保证数据一致性。
* 例如：CAS (Compare and Swap) 机制。

### 悲观锁（Pessimistic Lock）

* 适用于并发冲突多的场景，操作前先加锁，防止其他事务修改数据。
* 例如：SELECT ... FOR UPDATE（排它锁）。

## 2.按粒度分类（全局锁、表级锁、行级锁）

### 全局锁（Global Lock）

* 例如 FLUSH TABLES WITH READ LOCK，会锁住整个数据库，适用于备份。

### 表级锁（Table Lock）

* 特性：并发性最低，锁住整张表，不支持事务。
* 适用：MyISAM 引擎默认使用表锁，适合大量读少量写的场景。

### 行级锁（Row Lock）

* InnoDB 通过索引+锁来实现，支持高并发，但可能出现死锁。

### 页级锁

* BDB 引擎使用，介于表锁和行锁之间。

## 3.属性分类

* 共享锁（S锁）：允许多个事务读取，但不允许修改（LOCK IN SHARE MODE）。
* 排他锁（X锁）：独占资源，阻止其他事务访问（SELECT ... FOR UPDATE）。

## 4.状态分类（优化表级锁的管理）

* 意向共享锁（IS）：事务想要在某些行加共享锁，会先加 IS 锁。
* 意向排他锁（IX）：事务想要在某些行加排他锁，会先加 IX 锁。

## 5.算法分类（避免幻读，适用于 InnoDB）

* 间隙锁（Gap Lock）：锁住一个范围，防止幻读。
* 记录锁（Record Lock）：锁住单个记录，避免脏读、不可重复读。
* 临键锁（Next-Key Lock）：结合 记录锁+间隙锁，避免幻读。







