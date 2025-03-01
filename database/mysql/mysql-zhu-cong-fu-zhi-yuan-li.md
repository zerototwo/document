---
description: >-
  MySQL
  主从复制（Replication）是一种异步或半同步的数据同步机制，允许一个主库（Master）将数据变更同步到一个或多个从库（Slave），主要用于高可用性、读写分离、灾备等场景。
cover: >-
  https://images.unsplash.com/photo-1739737991332-557aa4da4f4e?crop=entropy&cs=srgb&fm=jpg&ixid=M3wxOTcwMjR8MHwxfHJhbmRvbXx8fHx8fHx8fDE3NDA4MTYzOTF8&ixlib=rb-4.0.3&q=85
coverY: 0
---

# MySQL 主从复制原理

## 1. MySQL 复制架构

MySQL 复制是基于 Binlog（Binary Log） 的，通过 异步、半同步、同步 方式进行数据同步。基本流程如下：

1. 主库写入 Binlog（Binary Log）
2. 从库 I/O 线程拉取 Binlog
3. 从库 SQL 线程重放 Binlog

## 2. MySQL 复制的详细流程

MySQL 复制涉及以下三个关键线程：

### ① 主库（Master）

* 客户端执行 SQL 语句（INSERT、UPDATE、DELETE）
* 主库将变更记录写入 Binlog（Binary Log）
* 需要开启 binlog，否则无法复制：

```sql
SHOW VARIABLES LIKE 'log_bin';
```

结果：

```sql
+---------------+-------+
| Variable_name | Value |
+---------------+-------+
| log_bin       | ON    |
+---------------+-------+
```

* Binlog 格式（binlog\_format）：

```sql
SHOW VARIABLES LIKE 'binlog_format';
```

结果：

```sql
+---------------+--------+
| Variable_name | Value  |
+---------------+--------+
| binlog_format | ROW    |
+---------------+--------+
```

* STATEMENT：基于 SQL 语句，体积小，但某些语句无法复制。
* ROW：基于行数据变化，数据一致性好，但 Binlog 体积大。
* MIXED：自动选择 STATEMENT 或 ROW。

### ② 从库（Slave）

从库有两个关键线程：

* I/O 线程（I/O Thread）：从主库拉取 Binlog 并写入 Relay Log（中继日志）。
* SQL 线程（SQL Thread）：读取 Relay Log 并执行 SQL 语句，恢复数据。

#### (1) I/O 线程

* 从库连接主库，执行：

```sql
START SLAVE;
```

* 读取 master.info 配置：

```sql
SHOW SLAVE STATUS\G;
```

```sql
Master_Log_File: mysql-bin.000001
Read_Master_Log_Pos: 120
```

* 发送 COM\_BINLOG\_DUMP 请求，从 mysql-bin.000001 的 120 位置开始拉取 Binlog。
* 收到 Binlog 后，写入从库的 Relay Log（中继日志）。

#### (2) SQL 线程

* 读取 Relay Log 并解析 SQL 语句：

```sql
Relay_Master_Log_File: mysql-bin.000001
Exec_Master_Log_Pos: 120
```

* 将 SQL 语句执行在从库，使数据与主库一致。

## 3. MySQL 复制的类型

### ① 异步复制（Asynchronous Replication）

默认的 MySQL 复制方式：

* 主库执行完事务后立即返回，不等待从库确认。
* 如果主库宕机，部分事务可能丢失。
* 适用于 读多写少 的业务，例如 日志分析、备份。

### ② 半同步复制（Semi-Synchronous Replication）

* 主库写入 Binlog 后，必须等至少一个从库确认接收后才返回 COMMIT。
* 适用于 高可用架构，减少数据丢失风险。

开启半同步复制（Master 端）：

```sql
INSTALL PLUGIN rpl_semi_sync_master SONAME 'semisync_master.so';
SET GLOBAL rpl_semi_sync_master_enabled = ON;
```

从库端开启：

```sql
INSTALL PLUGIN rpl_semi_sync_slave SONAME 'semisync_slave.so';
SET GLOBAL rpl_semi_sync_slave_enabled = ON;
```

优点

* 保证至少一个从库收到 Binlog，提升一致性。

缺点

* 影响主库写入性能。

### ③ 全同步复制（Synchronous Replication）

* 所有从库都必须确认收到 Binlog，主库才能提交事务。
* 适用于金融级别的高一致性场景。
* MySQL 原生不支持，需要使用 Galera Cluster（如 Percona XtraDB Cluster、MariaDB Galera）。

## 4. GTID 复制（全局事务 ID）

GTID（Global Transaction ID） 是 MySQL 5.6+ 提供的复制方式，每个事务有唯一的 GTID，简化主从切换。

### 开启 GTID

```sql
SET GLOBAL enforce_gtid_consistency = ON;
SET GLOBAL gtid_mode = ON;
```

### GTID 复制优势

1. 无需手动指定 MASTER\_LOG\_FILE 和 MASTER\_LOG\_POS
2. 支持自动故障恢复（从库可以自动找到最新事务）
3. 适用于高可用架构（MHA、MySQL Group Replication）

## 5. MySQL 复制拓扑

### ① 一主多从（Master-Slave）

```sql
Master  ->  Slave1
        ->  Slave2
```

* 适用于 读写分离，提高查询性能。

### ② 多级复制（Master → Slave1 → Slave2）

```sql
Master  ->  Slave1  ->  Slave2
```

* 适用于 远程备份 或 降低主库压力。

### ③ 多主复制（Multi-Master）

```java
Master1 <-> Master2
```

* 适用于 高可用场景（但冲突解决复杂）。

### ④ MySQL Group Replication

```
Master1  <-> Master2  <-> Master3
```

• 类似于 Paxos，适用于 高一致性集群。

## 6. 监控 MySQL 复制状态ql

检查复制状态

```sql
SHOW SLAVE STATUS\G;
```

关键字段

• Seconds\_Behind\_Master：从库滞后时间

• Slave\_IO\_Running / Slave\_SQL\_Running：是否正常复制

• Relay\_Master\_Log\_File 和 Exec\_Master\_Log\_Pos 位置

重启复制

```sql
STOP SLAVE;
START SLAVE;
```

修复复制错误\


如果 SHOW SLAVE STATUS 显示：

```sql
Last_SQL_Error: Duplicate entry '1001' for key 'PRIMARY'
```

可跳过错误：

```sql
SET GLOBAL sql_slave_skip_counter = 1;
START SLAVE;
```

## 7. 总结

| 复制方式              | 特点                   | 适用场景      |
| ----------------- | -------------------- | --------- |
| 异步复制              | 事务提交后立即返回，可能丢失数据     | 读多写少、日志分析 |
| 半同步复制             | 至少一个从库确认后返回          | 数据一致性要求高  |
| GTID 复制           | 自动故障恢复，无需手动设置 Binlog | 自动化高可用    |
| 多主复制              | 多个主库可写               | 数据冲突难处理   |
| Group Replication | 自动故障转移               | 高一致性集群    |

MySQL 复制的选择取决于你的业务需求，如果你希望提高读性能，可以用 一主多从；如果想要高可用，可以用 GTID 复制 + 半同步 或 Group Replication。
