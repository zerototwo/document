---
description: 并发优化主要关注 高并发场景下的数据库性能提升，避免资源争夺、减少锁竞争、提高吞吐量。以下是 MySQL 在高并发环境下的优化策略。
---

# 并发优化

## 1.读写分离

适用场景：读多写少 的应用，如电商网站、新闻门户。

### (1) 读写分离架构

* 主库（Master）：处理 写操作（INSERT、UPDATE、DELETE）。
* 从库（Slave）：处理 读操作（SELECT）。
* 客户端（应用层）：通过 负载均衡（如 MySQL Proxy）将查询分发到不同的从库。

示例

```sql
-- 只查询从库（避免影响主库）
SELECT * FROM users WHERE id = 1;
```

**注意点**

* 主从同步延迟：从库数据可能会滞后，影响数据一致性。

解决方案：

* 半同步复制（Semi-sync Replication）：主库等待至少一个从库确认再提交事务。
* Group Replication：实现多主架构，提高数据一致性。

## 2.数据分片（分库 & 分表）

当单库数据量 超过 5000 万行 或 单表数据超过 10GB 时，查询和索引维护性能下降，适合使用 分库分表 进行优化。

### **(1) 分库**

* 垂直分库（按业务拆分）：

**适用场景**：将不同业务的数据放入不同数据库，如 订单库、用户库、日志库。

示例

* user\_db 存储用户数据
* order\_db 存储订单数据

优势

* 每个数据库负载减少，事务冲突降低。
* 业务数据隔离，便于维护和扩展。

水平分库（按 ID 取模拆分）

* 适用场景：单表数据量过大，如 用户表、订单表。
* 示例：

```sql
-- 逻辑分表，创建多个物理表
CREATE TABLE users_0 LIKE users;
CREATE TABLE users_1 LIKE users;
```

### (2) 分表

* 范围分表：按时间、地理区域拆分，如 orders\_2023、orders\_2024。
* 哈希分表：user\_id % 4，分配到 users\_0 \~ users\_3。

**❗ 注意点**

* 分库分表后，事务一致性维护变难，需引入 分布式事务（如 TCC、SAGA）。
* 跨表查询变复杂，需使用 分片中间件（如 MyCat、ShardingSphere）。

## 3.事务优化

目标：减少事务持有锁的时间，避免锁争夺，提高并发能力。

### (1) 控制事务范围

* 事务时间越长，占用锁的时间越长，容易造成死锁，影响并发性能

优化策略：

* 事务内减少查询时间
* 尽量避免人工等待（如 DO SLEEP()）
* 适时提交事务，避免长期持锁

**示例**

```sql
-- ❌ 事务时间长，影响并发
START TRANSACTION;
UPDATE orders SET status = 'shipped' WHERE user_id = 1;
DO SLEEP(5); -- 业务逻辑阻塞
COMMIT;

-- ✅ 优化事务，减少锁持有时间
UPDATE orders SET status = 'shipped' WHERE user_id = 1;
COMMIT;
```

### (2) 合理使用锁

* 行锁 > 表锁 > 全局锁，尽量避免表锁，提高并发性能。
* 适用场景：

行锁（推荐）：InnoDB，只锁定需要的行，提高并发能力。

表锁（避免）：MyISAM，整个表锁定，适合日志存储。

间隙锁（Gap Lock）：防止 幻读，事务隔离级别 REPEATABLE READ 时生效。

示例

```sql
-- ❌ 表锁（会阻塞所有写入）
LOCK TABLES orders WRITE;

-- ✅ 行锁（仅锁定目标记录）
SELECT * FROM orders WHERE id = 1 FOR UPDATE;
```

## 4.连接池优化

目标：减少数据库连接创建/销毁的开销，提高并发能力。

✅ 使用连接池

优势：

* 复用连接，避免频繁创建/销毁连接的开销。
* 提高吞吐量，减少数据库压力。

示例

```sql
# MySQL 连接池配置（示例）
[mysqld]
max_connections = 1000
wait_timeout = 28800
interactive_timeout = 28800
```







