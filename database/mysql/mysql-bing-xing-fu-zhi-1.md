---
description: 并行复制（Parallel Replication） 主要优化 传统单线程复制 的低效问题，让多个 Worker 线程 并行执行事务。其核心流程如下：
cover: >-
  https://images.unsplash.com/photo-1738432323553-b9471e2239b9?crop=entropy&cs=srgb&fm=jpg&ixid=M3wxOTcwMjR8MHwxfHJhbmRvbXx8fHx8fHx8fDE3NDA5MDM4Njd8&ixlib=rb-4.0.3&q=85
coverY: 0
---

# MySQL 并行复制

## 1. MySQL 并行复制逻辑流程

```mermaid
sequenceDiagram
    participant 主库 as 主库 (Master)
    participant IO_线程 as 从库 IO 线程
    participant Relay_Log as 从库 Relay Log
    participant SQL_线程 as 从库 SQL 线程 (调度器)
    participant Worker_1 as Worker 线程 1
    participant Worker_2 as Worker 线程 2
    participant Worker_N as Worker 线程 N

    主库->>IO_线程: 生成 binlog 并传输
    IO_线程->>Relay_Log: 写入 relay log
    SQL_线程->>Relay_Log: 读取 relay log
    SQL_线程->>SQL_线程: 解析 binlog 并拆分事务
    SQL_线程->>Worker_1: 分配事务 1
    SQL_线程->>Worker_2: 分配事务 2
    SQL_线程->>Worker_N: 分配事务 N
    Worker_1->>SQL_线程: 事务 1 执行完成
    Worker_2->>SQL_线程: 事务 2 执行完成
    Worker_N->>SQL_线程: 事务 N 执行完成
    SQL_线程->>主库: 确认事务完成
```



## 2. MySQL 并行复制核心流程

```mermaid
graph TD
    A[主库 Master] -->|Binlog 传输| B[从库 IO 线程]
    B -->|写入 Relay Log| C[从库 SQL 线程]
    C -->|读取 Relay Log| D{并行复制调度器}
    
    D -->|基于 Schema 并行| E[按数据库分配事务]
    D -->|基于 Group Commit 并行| F[按事务提交顺序分配]
    D -->|基于 Writeset 并行| G[基于冲突检测并行执行]

    E --> H1[Worker 1 执行事务]
    E --> H2[Worker 2 执行事务]
    E --> H3[Worker 3 执行事务]

    F --> I1[Worker 1 执行事务]
    F --> I2[Worker 2 执行事务]
    F --> I3[Worker 3 执行事务]

    G --> J1[Worker 1 执行事务]
    G --> J2[Worker 2 执行事务]
    G --> J3[Worker 3 执行事务]

    H1 & H2 & H3 & I1 & I2 & I3 & J1 & J2 & J3 --> Z[最终提交]
```



## 3. 详细流程解析

### (1) 主库生成 Binlog

* MySQL 主库将事务记录到 Binlog 中，并按照提交顺序存储。

### (2) 从库 IO 线程获取 Binlog

* IO 线程 连接 主库，拉取 Binlog 并存储在 Relay Log 中。

### (3) 从库 SQL 线程解析 Relay Log

* SQL 线程读取 Relay Log，解析 Binlog 并进行 事务调度。

### (4) 并行复制调度

MySQL 通过 不同的策略 进行 事务调度：

* Schema 并行复制（不同数据库事务可并行）。
* Group Commit 并行复制（按主库事务提交顺序分配）。
* Writeset 并行复制（基于冲突检测并行执行，MySQL 8.0+）。

### (5) Worker 线程并行执行

* SQL 线程将事务分配给 多个 Worker 线程。
* Worker 线程独立执行事务，提高复制吞吐量。

### (6) 事务执行完成并提交

* Worker 线程执行完毕后，通知 SQL 线程。
* SQL 线程确保事务一致性，并最终提交。

## 4. 并行复制优化建议

```sql
-- 开启多 Worker 线程
SET GLOBAL slave_parallel_workers = 8;

-- 选择并行复制模式 (基于 Group Commit)
SET GLOBAL slave_parallel_type = 'LOGICAL_CLOCK';

-- 选择 Writeset 并行复制 (MySQL 8.0)
SET GLOBAL binlog_transaction_dependency_tracking = 'WRITESET';
```

总结：

• MySQL 并行复制 通过多个 Worker 线程并行执行事务，提高吞吐量。

• 三种并行模式（Schema、Group Commit、Writeset），MySQL 8.0 推荐使用 Writeset 并行复制。

• 优化参数 可显著提升从库同步性能，减少复制延迟！
