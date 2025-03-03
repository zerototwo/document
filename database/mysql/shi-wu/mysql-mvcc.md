---
description: >-
  MVCC（Multi-Version Concurrency Control，多版本并发控制）是一种 非锁定并发控制机制， InnoDB 存储引擎 通过
  MVCC 提高并发性能，同时保证事务的一致性。
cover: >-
  https://images.unsplash.com/photo-1735900415817-3892b83ddd8f?crop=entropy&cs=srgb&fm=jpg&ixid=M3wxOTcwMjR8MHwxfHJhbmRvbXx8fHx8fHx8fDE3NDEwMzY0ODR8&ixlib=rb-4.0.3&q=85
coverY: 0
---

# MySQL MVCC

## 1.MVCC 的核心思想

* 事务在执行时，会生成一个一致性视图（Consistent Read View）。
* 每个事务只能看到符合自己视图的数据，而不会看到其他事务未提交的更改。
* 通过隐藏版本字段和 Undo Log（回滚日志）维持多版本数据。

### 📌 MVCC 能解决什么问题？

| **问题**    | **MVCC 解决方式**                |
| --------- | ---------------------------- |
| **读写冲突**  | 读操作不加锁，避免阻塞写操作               |
| **数据一致性** | 通过一致性视图（Snapshot Read）保证事务隔离 |
| **并发性能**  | 读不加锁，提高数据库吞吐量                |

## 2.MVCC 关键组成

### (1) 一致性视图（Consistent Read View）

* 事务启动时，会创建一个一致性视图 (Read View)，用于确定 当前事务可见的数据版本。
* 该视图确保事务只能看到 在事务启动前已提交的数据，但看不到 其他事务未提交的更改。
* 视图的存在使得不同事务可以同时读取不同的历史数据，提高并发能力。

### (2) 版本链（Undo Log 维护历史版本）

* InnoDB 通过 Undo Log（回滚日志） 维护每一行数据的 多个版本。
* 每次修改数据时，不会直接覆盖，而是新建一个版本，并指向旧版本（版本链）。

#### &#x20;每行数据有两个隐藏字段：

| **字段**            | **作用**                |
| ----------------- | --------------------- |
| **trx\_id**       | 记录修改该数据的事务 ID         |
| **roll\_pointer** | 指向 Undo Log，用于存储旧版本数据 |

## 3.MVCC 查询 & 快照机制

### (1) 快照读（Snapshot Read）

快照读使用 MVCC，不加锁，提高并发性。

事务会 基于一致性视图（Read View）读取符合条件的数据版本，而不会阻塞其他事务。

示例：

```sql
SELECT * FROM users WHERE age > 18;
```

底层原理：

* 事务启动后，生成 Read View，确定可见的 trx\_id 范围。
* 读取数据时，只能看到 trx\_id 小于等于当前视图版本 的数据。
* 不会读取正在修改但未提交的记录。

### (2) 当前读（Current Read）

当前读绕过 MVCC，需要加锁，确保数据实时性。

示例：

```sql
SELECT * FROM users WHERE age > 18 FOR UPDATE;
UPDATE users SET age = 20 WHERE id = 1;
```

底层原理：

* 读取数据时，获取最新版本的数据，并加锁，防止其他事务修改。
* 适用于 事务需要实时获取最新数据的场景。

快照读 vs. 当前读

| 读操作 | 是否使用 MVCC  | 是否加锁   | 适用场景                           |
| --- | ---------- | ------ | ------------------------------ |
| 快照读 | ✅ 使用 MVCC  | ❌ 不加锁  | 高并发查询，普通 SELECT 语句             |
| 当前读 | ❌ 不使用 MVCC | ✅ 需要加锁 | SELECT ... FOR UPDATE 或 UPDATE |

## 4.MVCC 事务示例

示例：事务 T1 读取数据，事务 T2 修改数据

场景：

* 事务 T1 先启动，执行 SELECT \* FROM users WHERE id = 1;
* 事务 T2 修改 id = 1 的数据
* 事务 T1 仍然可以看到旧数据，而不会看到 T2 的修改

事务 T1 读取的数据受一致性视图控制，不受 T2 影响。

## 5.事务隔离级别 & MVCC

**MVCC 在不同事务隔离级别下的表现**

| **隔离级别**                 | **是否使用 MVCC** | **能否看到未提交数据** |
| ------------------------ | ------------- | ------------- |
| **READ UNCOMMITTED**     | ❌ 不使用         | ✅ 可能看到未提交数据   |
| **READ COMMITTED**       | ✅ 使用          | ❌ 只能看到已提交数据   |
| **REPEATABLE READ (默认)** | ✅ 使用          | ❌ 事务期间数据一致    |
| **SERIALIZABLE**         | ❌ 不使用         | ❌ 采用加锁机制      |

📌 **MVCC 主要在 READ COMMITTED 和 REPEATABLE READ 级别生效**，\
SERIALIZABLE 级别使用 **加锁机制**，而不使用 **MVCC**。

## 6.MVCC 优缺点

### ✅ MVCC 优势

* 读操作不加锁，避免锁竞争，提高并发能力
* 事务间可见性：未提交的数据不会影响其他事务
* 降低死锁概率，比锁机制更高效

### ❌ MVCC 缺点

* 需要维护多个版本的数据，存储开销大（需要 Undo Log）。
* 长时间运行的事务可能导致版本链过长，影响性能。
* 不适用于 SERIALIZABLE 级别，高隔离级别仍需加锁。



