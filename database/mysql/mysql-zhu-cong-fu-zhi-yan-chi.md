---
cover: >-
  https://images.unsplash.com/photo-1740318852936-6bcff491a617?crop=entropy&cs=srgb&fm=jpg&ixid=M3wxOTcwMjR8MHwxfHJhbmRvbXx8fHx8fHx8fDE3NDA4MTQyMzd8&ixlib=rb-4.0.3&q=85
coverY: 0
---

# MySQL 主从复制延迟

## 第一步：确认主从复制延迟的根本原因

执行：

```sql
SHOW SLAVE STATUS\G
```

重点关注以下字段：

* Seconds\_Behind\_Master：从库落后主库的时间（秒）。
* Slave\_IO\_Running：如果为 Yes，表示 I/O 线程正常；否则检查网络或 Binlog 读取问题。
* Slave\_SQL\_Running：如果为 No，说明 SQL 线程有问题，可能是大事务或锁争用导致的。
* Relay\_Log 和 Exec\_Master\_Log\_Pos 差距大：表示 SQL 线程执行慢。
* Last\_SQL\_Error：如果有错误，需解决该 SQL 语句问题。

如果 Seconds\_Behind\_Master 逐渐增加，说明从库无法跟上主库写入。

## 第二步：优化主库

主库写入压力大可能导致 Binlog 产生过快，从库处理不过来。

### 1. 降低事务开销

尽量避免大事务，推荐使用 小批量分批提交：

```sql
-- 大事务，错误示例
INSERT INTO orders (id, user_id, amount) VALUES (1, 1001, 10), (2, 1002, 20), ...;

-- 改进：使用小批量提交
START TRANSACTION;
INSERT INTO orders (id, user_id, amount) VALUES (1, 1001, 10);
INSERT INTO orders (id, user_id, amount) VALUES (2, 1002, 20);
COMMIT;
```

* 大事务的影响：MySQL 复制是基于 Binlog 的，Binlog 里的大事务需要等事务完全提交后才同步，导致从库滞后。

### 2. 选择适合的 Binlog 格式

```sql
SHOW VARIABLES LIKE 'binlog_format';
```

* ROW（行格式，默认）：适用于高并发但 Binlog 体积大，影响复制效率。
* MIXED（混合模式）：适用于大多数场景。
* STATEMENT（语句格式）：Binlog 小，但某些语句无法复制。\


可以切换为 MIXED 以减少 Binlog 开销：

```sql
SET GLOBAL binlog_format = 'MIXED';
```

### 3. 增加 Binlog 缓存

提高 binlog\_cache\_size，防止事务过多导致磁盘 I/O 瓶颈：

```sql
SET GLOBAL binlog_cache_size = 16M;
```

### 4. 启用并行复制

```sql
SET GLOBAL slave_parallel_workers = 8;  -- 适当增加并行复制线程数
SET GLOBAL slave_parallel_type = 'LOGICAL_CLOCK';  -- 让从库并行执行多个事务
```

## 第三步：优化从库

### 1. 增加从库的 InnoDB 缓存

```sql
SHOW VARIABLES LIKE 'innodb_buffer_pool_size';
```

默认较小，可以调大：

```sql
SET GLOBAL innodb_buffer_pool_size = 4G;
```

计算推荐值：

* 小型数据库（<10GB）：50% 总内存
* 中型数据库（10GB\~50GB）：60%-70% 总内存
* 大型数据库（>50GB）：80% 以上

### 2. 调整复制缓冲区

```sql
SET GLOBAL relay_log_space_limit = 4G;  -- 增大 relay log 缓存，防止从库 I/O 受限
SET GLOBAL read_buffer_size = 8M;  -- 读取 relay log 更快
SET GLOBAL read_rnd_buffer_size = 16M;
```

### 3. 启用多线程复制

MySQL 5.7 及以上版本支持多线程复制：

```sql
SET GLOBAL replica_parallel_workers = 8;
SET GLOBAL replica_parallel_type = 'DATABASE';
```

* DATABASE：按数据库并行执行
* LOGICAL\_CLOCK：按事务并行执行（MySQL 5.7+ 推荐）
* WRITESET：更高效（MySQL 8.0+）

## 第四步：优化复制架构

### 1. 采用 Binlog Server 代理

如果主库有多个从库，每个从库直接拉取 Binlog，会增加主库的压力。可以引入 Binlog Server：

```sql
主库 -> Binlog Server -> 多个从库
```

使用 MySQL Binlog Server 作为中转，主库只与 Binlog Server 交互，从库从 Binlog Server 拉取日志。

### 2. 采用半同步复制

默认 MySQL 采用 异步复制，如果主库宕机，可能导致数据不一致。可以开启 半同步复制：

```sql
INSTALL PLUGIN rpl_semi_sync_master SONAME 'semisync_master.so';
INSTALL PLUGIN rpl_semi_sync_slave SONAME 'semisync_slave.so';

SET GLOBAL rpl_semi_sync_master_enabled = ON;
SET GLOBAL rpl_semi_sync_slave_enabled = ON;
```

* 优点：保证至少一个从库收到数据后主库才返回 COMMIT，减少数据丢失。
* 缺点：主库写入速度会稍微降低。

## 3. 采用 Group Replication

如果 MySQL 复制严重滞后，可以考虑 Group Replication，提供高可用性：

```sql
CHANGE REPLICATION SOURCE TO SOURCE_AUTO_POSITION = 1;
SET GLOBAL group_replication_enable = ON;
```

* 优点：自动选主，支持多主模式。
* 缺点：需要 MySQL 8.0，配置复杂。

## 第五步：监控和调优

### 1. 监控主从复制状态

```sql
SHOW SLAVE STATUS\G;
```

自动重启复制：

```sql
STOP SLAVE;
START SLAVE;
```

如果 Slave\_IO\_Running 或 Slave\_SQL\_Running 为 No，需要检查错误：

```sql
SHOW SLAVE STATUS\G;
```

### 2. 使用 Percona Toolkit

```sql
pt-heartbeat --host=从库_IP --user=root --password=yourpassword
```

可以精准测量主从复制延迟。

## 总结

| 问题         | 解决方案                                                      |
| ---------- | --------------------------------------------------------- |
| 大事务导致复制延迟  | 分批提交，减少 INSERT/DELETE 事务量                                 |
| 从库 SQL 执行慢 | 加大 innodb\_buffer\_pool\_size，调整 slave\_parallel\_workers |
| Binlog 过大  | 改用 MIXED 格式，增大 binlog\_cache\_size                        |
| 网络传输慢      | 使用 Binlog Server 缓存日志                                     |
| 主库压力大      | 使用读写分离，ProxySQL                                           |
| 复制线程处理不过来  | 开启多线程复制 slave\_parallel\_workers=8                        |

按照这些具体措施，可以有效减少 MySQL 主从复制延迟，提高数据库性能。
