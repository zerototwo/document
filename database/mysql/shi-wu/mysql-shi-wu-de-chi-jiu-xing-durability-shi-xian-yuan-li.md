---
description: >-
  持久性（Durability）是 ACID 事务特性中的最后一个特性，指 一旦事务提交后，数据就会被永久保存，即使系统崩溃或断电，数据也不会丢失。MySQL
  通过多种机制确保事务的持久性，其中 Redo Log（重做日志） 是关键的实现方式。
---

# MySQL 事务的持久性 (Durability) 实现原理

## 持久性如何实现

### 1.Redo Log（重做日志）

* 核心作用：记录已经提交事务的变更信息，保证崩溃恢复后数据一致。

原理：

* 事务执行时，数据先写入 Redo Log（WAL 机制），并标记为 prepare 状态。
* 事务提交后，Redo Log 标记为 commit 状态，此时即使系统崩溃，也能恢复数据。
* MySQL 后台线程定期将 Redo Log 持久化到数据文件（刷盘），确保数据安全。

### 2.WAL 机制（Write-Ahead Logging）

MySQL 采用 WAL 机制，即

* 先写日志，再写数据，保证数据不会丢失。
* 当事务提交时，MySQL 先写入 Redo Log，再更新数据页。

### 3.Double Write（双写缓冲）

为了防止 MySQL 写入一半数据丢失，InnoDB 采用 Double Write 机制：

1. 数据页先写入 InnoDB 的 Double Write Buffer。
2. 然后再写入数据文件，保证数据不会部分丢失。

### 4.File System Buffer（操作系统缓存）

MySQL 不能直接操作磁盘，而是依赖操作系统缓存：

* 数据先进入 OS 缓冲区，然后才真正写入磁盘。
* fsync() 调用确保数据真正写入磁盘，保证数据不丢失。

## MySQL 持久性流程总结

1. 事务执行前，先写入 Redo Log，并标记 prepare 状态。
2. 事务提交后，将 Redo Log 标记 commit 状态，并调用 fsync 刷盘。
3. 后台线程 周期性将数据写入数据页，最终落盘，完成事务提交。

## 持久性与性能的权衡

innodb\_flush\_log\_at\_trx\_commit 参数控制持久性：

* 0：不立即刷盘，性能高但可能丢数据（非强持久性）。
* 1：每次事务提交都刷盘，最安全，默认值。
* 2：提交时写入 OS 缓冲区，但不立即刷盘，适合高性能场景。

## 结论

* 持久性保证事务数据不会丢失，即使崩溃也可恢复。
* Redo Log、WAL 机制、Double Write 共同保证数据可靠性。
* 可以通过 innodb\_flush\_log\_at\_trx\_commit 调整持久性与性能的权衡。
