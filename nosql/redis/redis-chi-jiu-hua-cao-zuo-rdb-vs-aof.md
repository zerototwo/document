---
description: >-
  Redis 提供 RDB（Redis Database） 和 AOF（Append Only File）
  两种持久化方式，以保证数据的可靠性。两者的核心区别在于 数据存储方式、写入频率、恢复速度 等。
cover: >-
  https://images.unsplash.com/photo-1736829391323-a302d2737210?crop=entropy&cs=srgb&fm=jpg&ixid=M3wxOTcwMjR8MHwxfHJhbmRvbXx8fHx8fHx8fDE3Mzk2MjQ1Mjd8&ixlib=rb-4.0.3&q=85
coverY: 0
---

# Redis 持久化操作：RDB vs AOF

## 1. RDB（Redis Database）—— 快照持久化

### 1.1 RDB 机制

RDB 通过 周期性快照（Snapshot） 的方式，把 Redis 内存数据 写入磁盘，形成 .rdb 文件。

### 工作流程

1\. 触发 RDB（手动 SAVE / BGSAVE 或自动触发）

2\. Redis 生成子进程（fork）

3\. 子进程将数据写入 dump.rdb 文件

4\. 数据存储完成后，替换旧的 dump.rdb

#### 示例

```
# 立即触发 RDB（阻塞 Redis）
SAVE

# 后台异步生成 RDB（推荐）
BGSAVE
```

### 1.2 RDB 触发条件

| 触发方式   | 执行方式                          | 是否阻塞 Redis |
| ------ | ----------------------------- | ---------- |
| SAVE   | 主线程 执行                        | ✅ 阻塞       |
| BGSAVE | 子进程 执行                        | ❌ 不阻塞      |
| 自动触发   | 配置 save \<seconds> \<changes> | ❌ 不阻塞      |

推荐使用 BGSAVE，避免阻塞 Redis。

```sh
# 配置自动保存
save 900 1   # 900 秒（15 分钟）至少 1 次写入
save 300 10  # 300 秒（5 分钟）至少 10 次写入
save 60 10000 # 60 秒至少 10000 次写入
```

### 1.3 RDB 优缺点

| 优点           | 缺点                        |
| ------------ | ------------------------- |
| 备份 & 恢复速度快   | 可能丢失数据（最后一次 BGSAVE 之后的数据） |
| 适用于冷备（不影响性能） | Fork 进程消耗 CPU 和内存         |
| 适用于大数据量持久化   | 不适合高频数据写入                 |

#### 适用场景

• Redis 主要作为缓存（数据丢失影响小）

• 数据量大，但写入频率较低（如冷数据存储）

• 备份 & 快速恢复（如故障恢复）

## 2. AOF（Append Only File）—— 日志持久化

### 2.1 AOF 机制

AOF 通过 记录每次写入操作（类似 Binlog），实现数据的高可靠性存储。

#### &#x20;工作流程

1\. 每次 Redis 写操作（SET、HSET、LPUSH）都会记录到 AOF 文件

2\. 定期执行 fsync（同步磁盘），确保数据写入持久化

3\. Redis 重启时，通过 AOF 日志 重放操作 恢复数据

#### 示例

```sh
# 启用 AOF
appendonly yes

# 配置写入策略（推荐 everysec）
appendfsync everysec  # 每秒同步（默认）
appendfsync always     # 每次写入都同步（最安全）
appendfsync no         # 让操作系统决定何时同步（性能最高）
```

### 2.2 AOF 重写

AOF 日志随着操作次数增多，会越来越大，因此 Redis 会定期重写 AOF 文件，减少体积。

AOF 重写触发方式

| 触发方式 | 执行方式                           |
| ---- | ------------------------------ |
| 手动触发 | BGREWRITEAOF                   |
| 自动触发 | 配置 auto-aof-rewrite-percentage |

示例

```sh
# 触发 AOF 重写
BGREWRITEAOF

# 配置 AOF 自动重写（文件增长 100% 触发）
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb
```

### 2.3 AOF 优缺点

| 优点              | 缺点                 |
| --------------- | ------------------ |
| 数据可靠性高，几乎无数据丢失  | AOF 体积大，占用存储空间     |
| 重启恢复数据更完整       | 写入频率高，影响性能         |
| 适用于高可靠业务（如金融支付） | AOF 重写会消耗 CPU & 内存 |

#### 适用场景

• 业务要求高可靠性（如 金融系统、订单系统）

• 数据变更频繁，需要强一致性

• 可接受一定的写入开销

## 3. RDB vs AOF 对比

| 维度   | RDB（快照持久化）        | AOF（日志持久化）  |
| ---- | ----------------- | ----------- |
| 数据丢失 | 可能丢失 BGSAVE 之后的数据 | 几乎无丢失       |
| 写入性能 | 更高（定期保存）          | 较低（每次写入都记录） |
| 恢复速度 | 快（加载 .rdb 直接恢复）   | 慢（重放日志恢复）   |
| 存储空间 | 占用小               | 占用大         |
| 适用场景 | 缓存、数据恢复           | 高可靠系统       |

## 4. 选择建议

### 1. 仅缓存数据（可以丢失）

• ✅ 使用 RDB，定期快照，降低磁盘 IO 负担。

• 配置：

```sh
save 900 1
save 300 10
save 60 10000
```

### 2. 业务要求高可靠性

• ✅ 使用 AOF（每秒同步 appendfsync everysec）

• 配置：

```sh
appendonly yes
appendfsync everysec
```

3\. 兼顾性能 & 安全

• ✅ RDB + AOF 混合模式

• 既可以快速恢复数据，又能防止数据丢失。

```sh
# 启用 RDB & AOF
save 900 1
save 300 10
appendonly yes
appendfsync everysec
```

## 5. 结论

* RDB 适合高性能备份，适用于 缓存、数据快照
* AOF 适合高可靠业务，适用于 支付、订单系统
* 推荐混合持久化（RDB + AOF），提高数据安全性 & 性能&#x20;
