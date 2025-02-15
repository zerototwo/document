---
description: 为了提高 Redis 在 高并发、大数据量、高可用性 场景下的性能，我们可以从以下几个方面进行优化
cover: >-
  https://images.unsplash.com/photo-1738748986807-bf1e6d00d58d?crop=entropy&cs=srgb&fm=jpg&ixid=M3wxOTcwMjR8MHwxfHJhbmRvbXx8fHx8fHx8fDE3Mzk2MjQwMDN8&ixlib=rb-4.0.3&q=85
coverY: 0
---

# Redis 优化建议

## &#x20;1. 内存优化

### &#x20;1.1 选择合适的数据结构

Redis 提供多种数据结构，如 String、Hash、List、Set、ZSet，选用合适的数据结构可以大幅减少内存占用。

| 需求场景    | 建议使用的数据结构          |
| ------- | ------------------ |
| 用户信息存储  | Hash（多个字段存储一个 key） |
| 计数器/点赞数 | String + INCR      |
| 文章标签    | Set（去重存储）          |
| 排行榜     | ZSet（可按分数排序）       |
| 任务队列    | List（FIFO 任务处理）    |

### 1.2 使用 Hash 代替 String

问题：多个 String 存储相似 key，浪费内存。

优化：使用 Hash 存储多个字段，避免 key 过长占用内存。

❌ 不推荐

```
SET user:1001:name "Alice"
SET user:1001:age "25"
SET user:1001:gender "Female"
```

✅ 推荐

```
HSET user:1001 name "Alice" age "25" gender "Female"
```

📌 优点：

• 结构紧凑，节省内存。

• 单次 HGETALL 可获取多个字段，减少 I/O。

### 1.3 开启 maxmemory-policy 设置淘汰策略

当 Redis 内存达到 maxmemory 限制时，需配置合适的淘汰策略，避免 OOM（内存溢出）。

```
CONFIG SET maxmemory 1gb  # 限制最大内存
CONFIG SET maxmemory-policy allkeys-lru  # 采用 LRU 淘汰策略
```

🔹 常见淘汰策略：

| 策略              | 适用场景                |
| --------------- | ------------------- |
| noeviction      | 禁止删除数据，超出内存时返回错误    |
| allkeys-lru     | 最推荐，优先删除最近最少使用的 key |
| volatile-lru    | 仅淘汰设置过期时间的 key      |
| volatile-ttl    | 淘汰最早要过期的 key        |
| allkeys-random  | 随机删除任意 key          |
| volatile-random | 随机删除有 TTL 的 key     |

📌 建议：

• 缓存数据 选用 allkeys-lru 。

• 保证重要数据不被删除 → 采用 noeviction + 持久化方案（AOF）。

### 1.4 避免 BigKey（超大 Key）

问题：BigKey 可能导致 慢查询 & 内存膨胀。

优化：

1\. 定期扫描大 key

```
redis-cli --bigkeys
```

2\. List/ZSet 拆分

```
LRANGE list_key 0 9  # 每次读取部分数据
```

## 2. 查询优化

### 2.1 使用 Pipeline 批量查询

问题：多个请求发送 & 响应导致 RT（响应时间）高。

优化：使用 Pipeline 进行批量请求，减少网络 IO。

```
redis-cli --pipe <<EOF
SET key1 value1
SET key2 value2
SET key3 value3
EOF
```

📌 优势：

• 减少 RTT（网络往返时间），性能提升 5\~10 倍。

### 2.2 避免 keys \* 全局扫描

问题：KEYS 命令会阻塞 Redis，影响性能。

优化：使用 SCAN 进行分批遍历。

```
SCAN 0 MATCH user:* COUNT 100
```

📌 优势：

• SCAN 不阻塞，适合大规模数据查询。

### 2.3 使用 EXPIRE 设置过期时间

问题：缓存数据无过期时间，导致 Redis 存储膨胀。

优化：给缓存数据设置 TTL（Time-To-Live）。

```
SET session:1001 "token" EX 3600  # 1小时过期
```

📌 优势：

• 避免无用数据长期占用内存。

## 3. 持久化优化

### 3.1 选择合适的持久化方案

| 模式              | 作用                | 适用场景        |
| --------------- | ----------------- | ----------- |
| RDB（快照）         | 定期保存 Redis 数据到磁盘  | 秒级备份，适合灾难恢复 |
| AOF（追加日志）       | 记录每条写操作，防止数据丢失    | 数据一致性要求高的业务 |
| 混合模式（AOF + RDB） | 结合快照 & 日志，减少磁盘 IO | 最推荐方案       |

📌 建议：

• 高吞吐应用（如缓存）使用 RDB，提升性能。

• 金融/支付系统 选择 AOF 确保数据安全。

### 3.2 优化 AOF 写入方式

AOF 默认 每秒落盘，可调优 减少磁盘 IO。

```
CONFIG SET appendfsync everysec  # 每秒落盘（推荐）
CONFIG SET appendfsync no  # 让系统控制（性能高）
```

📌 建议：

• 高可靠性 选择 always（每次写入都落盘）。

• 高吞吐 选择 everysec（每秒落盘）。

## 4. 高并发优化

### 4.1 开启 Redis 线程模型优化

Redis 6.0 之后支持多线程处理 网络 IO，可以优化高并发性能。

```
CONFIG SET io-threads 4
```

📌 建议：

• 高并发业务 可设置 io-threads=4\~8，避免单线程瓶颈。

### 4.2 使用 分片集群（Redis Cluster）

问题：单机 Redis 容量 & 负载受限。

优化：使用 Redis Cluster 水平扩展，支持分片存储。

```
redis-cli --cluster create 192.168.1.1:7001 192.168.1.2:7002 192.168.1.3:7003 --cluster-replicas 1
```

📌 优势：

• 支持 数据分片，可扩展至 百万级 QPS。

## 5. 监控与调优

### &#x20;5.1 监控 Redis 性能

• 监控 Key 使用情况

```
INFO keyspace
```

• 监控 Redis 性能

```
INFO all
```

📌 建议：

• 定期 redis-cli --bigkeys 检测大 Key。

• 使用 slowlog 监控慢查询：

```
SLOWLOG GET 10
```

## 6. 结论

* 合理选择数据结构，减少内存占用。
* 避免 keys 操作，使用 SCAN 遍历大数据量。
* 开启 maxmemory-policy，防止 OOM。
* 使用 Pipeline 批量操作，减少 IO 开销。
* Redis Cluster 扩展容量 & 负载均衡。
