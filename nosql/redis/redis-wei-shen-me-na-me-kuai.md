---
description: Redis 以其超高性能著称，单线程架构下可以实现百万级 QPS。 其速度快的主要原因包括 纯内存操作、单线程机制、高效数据结构、IO 多路复用等。
---

# Redis 为什么那么快？

## 1. 纯内存操作

数据全部存储在内存中，读写不涉及磁盘 IO，相比数据库的磁盘读取，速度提升 几个数量级。

| 存储方式                    | 读写速度    |
| ----------------------- | ------- |
| 磁盘数据库（MySQL、PostgreSQL） | 毫秒级（ms） |
| Redis（内存存储）             | 微秒级（μs） |

### 示例

```sh
SET user:1001 "Alice"   # O(1) 读写
GET user:1001
```

内存访问 ≈ 100 ns，比磁盘快 1000 倍。

## 2. 单线程模型（避免 CPU 上下文切换）

Redis 采用单线程（Thread-Per-Core）机制，避免线程上下文切换的开销。

| 架构         | 特点        | 适用场景         |
| ---------- | --------- | ------------ |
| 多线程（MySQL） | 线程切换成本高   | 适用于复杂查询      |
| 单线程（Redis） | 无锁操作，避免竞争 | 适用于高并发、小数据操作 |

Redis 通过单线程 + IO 多路复用提升并发性能。

## 3. 高效的数据结构

Redis 使用高效的数据结构，优化存储 & 读写效率。

| 数据结构           | 存储类型      | 读写复杂度    | 适用场景     |
| -------------- | --------- | -------- | -------- |
| SDS（动态字符串）     | String    | O(1)     | 计数器、缓存   |
| ZipList（压缩列表）  | List/Hash | O(1)     | 小规模数据存储  |
| SkipList（跳表）   | ZSet      | O(log n) | 排行榜、时间序列 |
| HashTable（哈希表） | Hash      | O(1)     | 购物车、用户信息 |

### 示例

```sh
HSET user:1001 name "Alice" age 25
HGET user:1001 name  # O(1)
```

小 Key 使用 ZipList，大 Key 采用 SkipList 提高查询效率。

## 4. IO 多路复用（Epoll）

Redis 采用 epoll + 非阻塞 IO 处理 高并发请求，避免线程阻塞。

| IO 模型       | 特点       | Redis 采用 |
| ----------- | -------- | -------- |
| select/poll | 轮询查询，效率低 | ❌        |
| epoll       | 事件驱动，高并发 | ✅        |

### 示例

```
int epfd = epoll_create(1);
struct epoll_event ev;
ev.events = EPOLLIN;
epoll_ctl(epfd, EPOLL_CTL_ADD, socket_fd, &ev);
epoll_wait(epfd, &events, 10, -1);
```

Epoll 让 Redis 支持 百万级 QPS，提升吞吐量。

## 5. 采用 Pipeline（减少网络 IO）

Redis 支持 Pipeline 批量操作，减少 TCP 交互，提升吞吐量。

### 示例

```c
MULTI
SET key1 value1
SET key2 value2
SET key3 value3
EXEC
```

单次网络请求发送多个命令，减少 RTT，提升 5\~10 倍性能。

## 6. 合理的内存管理

Redis 采用 LRU、LFU 淘汰策略，避免内存溢出（OOM）。

### 示例

```sh
CONFIG SET maxmemory 512mb
CONFIG SET maxmemory-policy allkeys-lru
```

热点数据存活，低频数据自动淘汰，保证高性能。

## 7. AOF + RDB 结合（持久化优化）

Redis 采用 AOF（日志） + RDB（快照） 持久化策略，确保 数据安全 & 快速恢复。

### 示例

```sh
appendonly yes
appendfsync everysec
```

数据可靠性高，同时保证高性能。

## 8. 采用 Cluster（分布式扩展）

Redis Cluster 支持 分片存储，可扩展至 百万 QPS。

### 示例

```sh
redis-cli --cluster create 192.168.1.1:7001 192.168.1.2:7002 192.168.1.3:7003 --cluster-replicas 1
```

实现高可用 & 高吞吐量，支持 PB 级数据存储。

## 9. 结论

* 纯内存存储 → 访问速度快（微秒级）
* 单线程机制 → 避免线程切换，提升性能
* 高效数据结构 → O(1) / O(log n) 查询
* IO 多路复用 → epoll 支持百万并发
* Pipeline 批量操作 → 5\~10 倍性能提升
* 合理的内存淘汰策略 → 避免 OOM&#x20;

🚀 Redis 通过这些优化，实现了 超高吞吐量 & 低延迟存取！
