# MySQL 事务的 隔离性 (Isolation) 实现原理

## **📌 1. 什么是隔离性 (Isolation)?**

隔离性 (Isolation) 指的是 **多个事务并发执行时，每个事务的操作互不干扰**，保证数据的一致性和正确性。\
如果没有适当的隔离控制，会导致数据冲突，如 **脏读、不可重复读、幻读** 等问题。

***

## **📌 2. MySQL 如何实现隔离性？**

MySQL 主要通过 **事务隔离级别** 和 **MVCC (多版本并发控制)** 机制来实现事务的隔离性。\
此外，还使用 **锁机制**（行锁、表锁、间隙锁）来避免数据竞争。

***

## **📌 3. 事务隔离级别**

MySQL 提供 **四种事务隔离级别**，级别越高，数据一致性越强，但并发性能可能下降。

| **隔离级别**                           | **脏读 (Dirty Read)** | **不可重复读 (Non-Repeatable Read)** | **幻读 (Phantom Read)** | **性能**             |
| ---------------------------------- | ------------------- | ------------------------------- | --------------------- | ------------------ |
| **READ UNCOMMITTED（读未提交）**         | ✅ 可能                | ✅ 可能                            | ✅ 可能                  | **最高并发，最低隔离**      |
| **READ COMMITTED（读已提交）**           | ❌ 不可能               | ✅ 可能                            | ✅ 可能                  | **Oracle 默认，防止脏读** |
| **REPEATABLE READ（可重复读，MySQL 默认）** | ❌ 不可能               | ❌ 不可能                           | ✅ 可能                  | **防止不可重复读**        |
| **SERIALIZABLE（可串行化）**             | ❌ 不可能               | ❌ 不可能                           | ❌ 不可能                 | **最高隔离，性能最差**      |

#### **✅ MySQL 默认事务隔离级别**

```sql
SELECT @@tx_isolation; -- 查看当前隔离级别
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ; -- 设置事务隔离级别
```

🔹 默认使用 REPEATABLE READ，解决了脏读和不可重复读，但可能存在幻读问题。

## 📌 4. 并发问题及 MySQL 解决方案

## 🔹 1. 脏读 (Dirty Read)

* 定义：事务 A 读取了事务 B 未提交 的数据，事务 B 之后回滚，导致事务 A 读取的数据无效。
* 示例：

```java
-- 事务 A 读取事务 B 的未提交数据
START TRANSACTION;
SELECT balance FROM accounts WHERE id = 1; -- 读取到事务 B 修改的数据
```

MySQL 解决方案：使用 READ COMMITTED 级别 及以上，防止脏读。

***

### 🔹 2. 不可重复读 (Non-Repeatable Read)

* 定义：事务 A 在执行过程中，多次读取同一行数据，而事务 B 在 A 读取之间修改并提交了该数据，导致事务 A 读取的结果不一致。
* 示例：

```java
-- 事务 A 先读取
SELECT balance FROM accounts WHERE id = 1;

-- 事务 B 修改数据并提交
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
COMMIT;

-- 事务 A 再次读取，数据不一致
SELECT balance FROM accounts WHERE id = 1;
```

MySQL 解决方案：使用 REPEATABLE READ 级别，确保事务内部读取到的结果不变。

### 🔹 3. 幻读 (Phantom Read)

* 定义：事务 A 读取某个范围的数据，事务 B 在该范围内插入新数据，导致事务 A 在相同查询条件下前后查询结果不一致。
* 示例：

```java
-- 事务 A 读取总行数
SELECT COUNT(*) FROM accounts WHERE balance > 1000;

-- 事务 B 插入一条符合查询条件的数据
INSERT INTO accounts (id, balance) VALUES (100, 2000);
COMMIT;

-- 事务 A 再次查询，结果变多
SELECT COUNT(*) FROM accounts WHERE balance > 1000;
```

MySQL 解决方案：

* 使用 SERIALIZABLE 级别，强制事务串行化执行。
* 间隙锁 (Gap Lock) 防止其他事务插入数据。

## 📌 5. MySQL 事务隔离的实现方式

### ✅ 1. MVCC（多版本并发控制）

MySQL 的 InnoDB 存储引擎使用 MVCC (Multi-Version Concurrency Control) 机制，结合 Undo Log，保证事务在 READ COMMITTED 和 REPEATABLE READ 级别下读取历史数据，避免加锁影响性能。

* 读取数据时，事务不会直接访问最新数据，而是使用 Undo Log 读取 历史快照，确保数据一致性。
* 事务提交后，新的数据版本可见，旧版本可被回收。

### ✅ 2. 锁机制

| **锁类型**                  | **作用**        | **适用场景**                                    |
| ------------------------ | ------------- | ------------------------------------------- |
| **行锁 (Row Lock)**        | 仅锁定特定行，提高并发性能 | **UPDATE / DELETE / SELECT ... FOR UPDATE** |
| **表锁 (Table Lock)**      | 锁住整个表，避免冲突    | **适用于 MyISAM**                              |
| **间隙锁 (Gap Lock)**       | 防止幻读，锁定范围     | **适用于 REPEATABLE READ**                     |
| **意向锁 (Intention Lock)** | 事务锁的标记，避免全表扫描 | **用于行锁优化**                                  |

### 📌 6. MySQL 隔离性总结

| **隔离级别**                 | **防止脏读** | **防止不可重复读** | **防止幻读** | **使用场景**            |
| ------------------------ | -------- | ----------- | -------- | ------------------- |
| **READ UNCOMMITTED**     | ❌ 不能     | ❌ 不能        | ❌ 不能     | 高并发环境，数据一致性要求低      |
| **READ COMMITTED**       | ✅ 可以     | ❌ 不能        | ❌ 不能     | 适用于大多数应用（Oracle 默认） |
| **REPEATABLE READ (默认)** | ✅ 可以     | ✅ 可以        | ❌ 不能     | MySQL 默认，适用于大多数场景   |
| **SERIALIZABLE**         | ✅ 可以     | ✅ 可以        | ✅ 可以     | 数据一致性要求极高的场景        |

