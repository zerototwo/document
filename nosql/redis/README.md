# Redis

Redis 是高并发场景下最常见的缓存数据库，面试时经常涉及基础原理、持久化、分布式、优化策略、数据结构、事务、并发控制、缓存问题等。

以下是 Redis 面试必备知识点，涵盖 30+ 高频问题，助你面试稳拿 Offer！🚀

📌 1. Redis 基础知识

| 问题              | 核心知识点                                               |
| --------------- | --------------------------------------------------- |
| Redis 是什么？      | 基于 内存存储 + 高效数据结构 + 非阻塞 IO 的高性能 NoSQL                |
| Redis 支持哪些数据类型？ | String、List、Set、ZSet、Hash、HyperLogLog、Bitmap、Stream |
| Redis 为什么快？     | 内存存储、单线程架构、IO 多路复用（epoll）、高效数据结构、Pipeline           |

📌 必背命令

```
SET key value   # 存储数据
GET key         # 获取数据
EXPIRE key 60   # 设置过期时间
DEL key         # 删除 key
```

📌 2. Redis 持久化

| 问题               | 核心知识点                       |
| ---------------- | --------------------------- |
| Redis 持久化方式有哪些？  | RDB（快照） & AOF（日志）           |
| RDB vs AOF 区别？   | RDB 适合备份，恢复快；AOF 适合高可靠性，恢复慢 |
| Redis 如何保证数据不丢失？ | AOF everysec 结合 RDB         |
| 如何优化 AOF？        | AOF 日志压缩 BGREWRITEAOF       |

📌 持久化配置

```
save 900 1    # 900秒（15分钟）至少1次写入
appendonly yes  # 开启 AOF
appendfsync everysec  # 每秒持久化
```

📌 3. Redis 过期策略 & 淘汰策略

| 问题                    | 核心知识点               |
| --------------------- | ------------------- |
| Redis 过期数据如何删除？       | 惰性删除 + 定期删除         |
| Redis 淘汰策略有哪些？        | LRU、LFU、TTL 规则      |
| 如何避免 Redis OOM（内存溢出）？ | 设置 maxmemory + 淘汰策略 |

📌 内存管理

```
CONFIG SET maxmemory 512mb
CONFIG SET maxmemory-policy allkeys-lru
```

📌 4. Redis 事务

| 问题             | 核心知识点                 |
| -------------- | --------------------- |
| Redis 事务是什么？   | MULTI、EXEC 组成的命令批处理机制 |
| Redis 事务支持回滚吗？ | ❌ 不支持，EXEC 后不会回滚      |
| 事务如何保证原子性？     | 所有命令串行执行，不被打断         |
| 事务和 Lua 脚本的区别？ | Lua 更快，减少网络开销         |

📌 事务示例

```
MULTI
SET key1 value1
SET key2 value2
EXEC
```

📌 5. Redis 并发控制

| 问题              | 核心知识点                 |
| --------------- | --------------------- |
| Redis 是单线程的吗？   | ✅ 是（6.0 之后支持多线程 IO）   |
| 如何解决高并发问题？      | 分布式锁、pipeline、Cluster |
| Redis 分布式锁如何实现？ | SETNX / RedLock       |

📌 分布式锁

```
SET lock_key "lock" NX PX 5000
```

📌 6. Redis 复制、哨兵、集群

| 问题                     | 核心知识点       |
| ---------------------- | ----------- |
| Redis 主从复制原理？          | 全量同步 + 增量同步 |
| Redis 哨兵模式是什么？         | 自动主从切换（高可用） |
| Redis Cluster（集群）如何工作？ | 分片存储，多主多从   |

📌 主从复制

```
slaveof 192.168.1.1 6379
```

📌 Redis 集群

```
redis-cli --cluster create 192.168.1.1:7001 192.168.1.2:7002 192.168.1.3:7003 --cluster-replicas 1
```

📌 7. 缓存问题

| 问题        | 核心知识点            |
| --------- | ---------------- |
| 缓存穿透如何解决？ | 缓存空值、BloomFilter |
| 缓存击穿如何解决？ | 热点 Key 加锁、永不过期   |
| 缓存雪崩如何解决？ | 不同 Key 过期时间随机化   |

📌 缓存击穿示例

```
SET key value EX 3600 NX
```

📌 8. Redis 优化

| 问题             | 核心知识点                    |
| -------------- | ------------------------ |
| 如何优化 Redis 查询？ | Pipeline 批量处理            |
| 如何优化大 Key？     | 拆分 Key，使用 Hash           |
| 如何优化持久化？       | AOF 配置 everysec          |
| 如何优化高并发？       | Cluster 分片，Epoll IO 多路复用 |

📌 批量查询

```
MGET key1 key2 key3
```

📌 Pipeline

```
MULTI
SET key1 value1
SET key2 value2
EXEC
```

📌 9. Redis 面试真题总结

| 类别   | 核心问题                        |
| ---- | --------------------------- |
| 基础原理 | Redis 为什么快？单线程如何支持高并发？      |
| 持久化  | RDB vs AOF，哪种方式更适合高可靠性？     |
| 分布式  | 主从复制、哨兵、Cluster 的区别？        |
| 事务   | Redis 事务如何保证原子性？支持回滚吗？      |
| 锁    | Redis 如何实现分布式锁？SETNX 有哪些问题？ |
| 优化   | 如何解决 Redis OOM？             |
| 缓存问题 | 如何解决缓存穿透、缓存击穿、缓存雪崩？         |

📌 10. 面试技巧

✅ 原理 + 代码实践，掌握核心命令

✅ 多角度分析问题，如 缓存雪崩 既可 加锁 也可 双层缓存

✅ 结合业务场景，如支付系统更关注 数据一致性（AOF），游戏排行更关注 排序查询（ZSet）

🚀 掌握这些 Redis 知识点，轻松拿下后端面试 Offer！ 🎯
