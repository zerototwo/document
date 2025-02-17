---
description: >-
  Kafka 作为 高吞吐的分布式消息系统，其存储机制至关重要，能够持久化存储数据并高效读取。Kafka 的存储机制主要依赖于 日志分段（Log
  Segments）、索引文件（Index）、PageCache 以及零拷贝技术，从而 保证数据持久化、高效查询和高吞吐量。
cover: >-
  https://images.unsplash.com/photo-1732282602306-fe466828e1e8?crop=entropy&cs=srgb&fm=jpg&ixid=M3wxOTcwMjR8MHwxfHJhbmRvbXx8fHx8fHx8fDE3Mzk3ODY4ODZ8&ixlib=rb-4.0.3&q=85
coverY: 0
---

# Kafka 存储机制

## 1.Kafka 存储数据的基本单位

Kafka 以 **Topic（主题）为单位组织数据**，每个 Topic 会被**划分成多个 Partition（分区）**，每个 Partition **顺序存储消息。**

### Kafka 存储的基本结构

存储路径（每个 Partition 存储在一个独立的目录中）

```
/kafka-logs/
└── topic-name/
    ├── 0/  # Partition 0
    │   ├── 00000000000000000000.log
    │   ├── 00000000000000000000.index
    │   ├── 00000000000000000000.timeindex
    │   ├── 00000000000000001000.log
    │   ├── ...
    ├── 1/  # Partition 1
    ├── 2/  # Partition 2
```

### Kafka 存储的核心机制

### 1. 日志分段（Log Segment）

Kafka 顺序写入日志文件（Append-Only Log），并 定期滚动（Roll）创建新的日志文件，避免单个文件过大。

日志文件

* 每个 Partition 由多个日志文件组成。
* 日志文件按照 offset 递增，文件名表示日志的起始 offset。
* 日志写满（默认 1GB）或超时（默认 7 天）后，Kafka 会新建一个日志文件。

```
00000000000000000000.log   # 包含 offset 0~999
00000000000000001000.log   # 包含 offset 1000~1999
```

### 2. 索引文件（Index & TimeIndex）

Kafka 为了**高效查找消息**，每个日志文件都会有相应的 索引文件：

| 索引类型         | 作用                    | 示例文件                           |
| ------------ | --------------------- | ------------------------------ |
| Offset Index | 通过 消息 offset 快速定位日志文件 | 00000000000000000000.index     |
| Time Index   | 通过 消息时间戳查找消息          | 00000000000000000000.timeindex |

#### 示例（Offset 索引）

• Kafka 不会为 每条消息 建立索引，而是 每隔 N 条消息建立一个索引，减少索引大小。

```
Offset Index:
offset: 0  →  文件位置: 0
offset: 1000 →  文件位置: 8096
offset: 2000 →  文件位置: 16384
```

#### 示例（Time 索引）

• 基于时间戳查找消息，适用于消费时间范围查询。

```
Time Index:
timestamp: 1678291840000  →  offset: 1000
timestamp: 1678291860000  →  offset: 2000
```

## 3. PageCache 机制

Kafka **不直接读写磁盘**，**而是借助 Linux PageCache** 提高读写性能：

1. 写入数据时，数据先写入 PageCache，再由操作系统异步刷盘。
2. 读取数据时，Kafka 优先从 PageCache 读取，避免磁盘 IO。

**作用：**

• 减少磁盘 IO，提升读写性能。

• 借助 OS 管理缓存，Kafka 本身无需维护复杂的缓存系统。

### 4. 零拷贝（Zero Copy）

Kafka 采用 sendfile() 系统调用，让数据 直接从 PageCache 发送到网络，避免 CPU 多次拷贝。

💡 作用：

• 减少 CPU 负载（数据无需在用户态 & 内核态之间拷贝）。

• 提高吞吐量（直接从 PageCache 发送给 Consumer）。

5\. 数据清理 & 过期策略\



Kafka 提供两种数据清理策略，防止日志无限增长：

| 策略   | 作用                    | 配置参数                         |
| ---- | --------------------- | ---------------------------- |
| 基于时间 | 保留数据 X 天，超过时间自动删除     | log.retention.hours=168      |
| 基于大小 | 每个日志文件最大 1GB，超出后创建新文件 | log.segment.bytes=1073741824 |

👉 生产环境推荐

```
log.retention.hours=72   # 日志保留 72 小时
log.segment.bytes=512MB  # 每个日志段 512MB
```

## 6.Kafka 数据存储优化

### 1. 增加 PageCache 缓存

Kafka 依赖 OS PageCache 进行缓存，建议增加服务器内存，减少磁盘 IO。

```
echo 3 > /proc/sys/vm/drop_caches  # 释放 PageCache
```

### 2. 调整 Segment 过期策略

```
log.retention.hours=72   # 保留 72 小时数据
log.segment.bytes=512MB  # 控制单个日志文件大小
```

### 3. 使用 sendfile() 零拷贝

Kafka 默认启用 sendfile() ，减少 CPU 负载，建议保持默认配置。

## 7.总结

| 存储机制                  | 作用                       |
| --------------------- | ------------------------ |
| 日志分段（Log Segment）     | 顺序写入，提高写入吞吐量             |
| 索引（Index & TimeIndex） | 加速消息查找，支持 Offset & 时间查询  |
| PageCache 缓存          | 减少磁盘 IO，提升读写速度           |
| 零拷贝（Zero Copy）        | 数据直接从 PageCache 发送，提高吞吐量 |
| 数据清理（Retention）       | 防止磁盘占满，可按时间/大小删除旧数据      |

💡 Kafka 的高性能存储机制 依赖 顺序写入、PageCache、索引优化、零拷贝，确保 消息持久化存储 & 高效读取 。
