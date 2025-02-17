---
description: >-
  Redis 采用定期删除（惰性删除 + 定期删除）的策略来管理数据的生命周期，防止内存溢出（OOM）。当内存达到上限时，Redis 还会根据
  内存淘汰策略（Eviction Policy） 进行数据清理。
---

# Redis 删除策略

## &#x20;1. Redis 过期键删除策略

Redis 允许为 Key 设置过期时间（TTL），到期后该 Key 需要被删除。删除方式有以下三种：

| 策略                      | 原理                      | 优缺点                       |
| ----------------------- | ----------------------- | ------------------------- |
| 惰性删除（Lazy Deletion）     | 仅在访问 Key 时才检查是否过期，过期则删除 | ✅ 低 CPU 占用，❌ 可能存在大量无效 Key |
| 定期删除（Active Expiration） | 每秒扫描一部分过期 Key，随机删除      | ✅ 避免内存占用过高，❌ 增加 CPU 开销    |
| 内存淘汰（Eviction）          | 当内存不足时，执行数据淘汰策略         | ✅ 适用于高并发，❌ 需要选择合适策略防止误删   |

### 1.1 惰性删除（Lazy Deletion）

• 当客户端查询某个 Key 时，Redis 发现其 TTL 过期，则删除该 Key。

• 适用场景：低访问频率的 Key，不会影响 Redis 性能。

#### 示例

```
SET key1 "value1" EX 10   # 10 秒后过期
GET key1  # 10 秒内访问正常
GET key1  # 10 秒后访问，发现过期，Redis 直接删除
```

⚠️ 问题：如果 Key 长时间不被访问，会占用 Redis 内存，导致 OOM（内存溢出）。

### 1.2定期删除（Active Expiration）

• Redis 每秒执行 10 次定期任务，随机检查部分 Key 是否过期，并删除过期 Key。

• 避免大量 Key 积累导致 OOM，但增加了 CPU 开销。

#### 参数优化

```
# 允许 Redis 每次最多清理 100 个过期键，默认 10
CONFIG SET active-expire-keys 100
```

⚠️ 问题：

• 定期任务无法删除所有过期 Key，可能导致部分 Key 仍然占用内存。

• 适用于大多数场景，但高吞吐业务可能仍需配合内存淘汰策略。

### 2. Redis 内存淘汰策略（Eviction Policy）

当 Redis 内存达到 maxmemory 限制，且无法回收过期 Key 时，会根据淘汰策略清理数据，保证 Redis 可用。

| 淘汰策略            | 描述                        | 适用场景                   |
| --------------- | ------------------------- | ---------------------- |
| noeviction（默认）  | 只返回错误，不删除数据               | 适用于严格数据存储，如金融系统        |
| allkeys-lru     | \*\*删除最久未使用（LRU）\*\*的 Key | 适用于缓存模式（如 Web Session） |
| volatile-lru    | 仅删除设置过期时间的 Key，按 LRU 规则淘汰 | 适用于定期过期缓存              |
| allkeys-random  | 随机删除任意 Key                | 适用于无固定热点数据             |
| volatile-random | 随机删除可过期的 Key              | 适用于短期存储业务              |
| volatile-ttl    | 优先删除 TTL 最短的 Key          | 适用于精准控制过期数据            |

📌 示例

```
CONFIG SET maxmemory-policy allkeys-lru  # 启用 LRU 淘汰策略
CONFIG SET maxmemory 500mb  # 设置 Redis 最大内存
```

⚠️ 重要建议

• 推荐使用 allkeys-lru 以保证热点数据存活。

• 对业务重要数据，避免设置 TTL，防止误删除。

## 3. Redis 删除策略总结

| 策略类型  | 策略名称         | 适用场景                | 优缺点                         |
| ----- | ------------ | ------------------- | --------------------------- |
| 过期键删除 | 惰性删除         | 低访问频率的数据            | ✅ 低 CPU 占用，❌ 可能导致 OOM       |
| 过期键删除 | 定期删除         | 适用于大部分业务            | ✅ 避免大量过期 Key 占用，❌ 增加 CPU 开销 |
| 内存淘汰  | noeviction   | 关键数据存储，如订单、金融业务     | ✅ 避免误删，❌ 超出内存后报错            |
| 内存淘汰  | allkeys-lru  | 高并发缓存，如 CDN、Web 服务器 | ✅ 淘汰最少使用 Key，❌ 热点数据有丢失风险    |
| 内存淘汰  | volatile-ttl | 定期过期缓存              | ✅ 只删除短期数据，❌ 影响 TTL 逻辑       |

## 4. Redis 删除策略最佳实践

* 高并发缓存 → allkeys-lru（保留热点数据）
* 数据存储（NoSQL） → noeviction（保证数据不丢失）
* 短期数据存储 → volatile-ttl（优先清理即将过期数据）
* 定时任务 + 监控，防止 OOM 和 Redis 扩容。
