---
description: >-
  PageCache 是操作系统（OS）用来缓存磁盘数据到内存的一种技术，Kafka 充分利用 PageCache 提高读写性能，极大减少了磁盘
  IO，从而提高吞吐量。
cover: >-
  https://images.unsplash.com/photo-1738603752061-f8fb60217f23?crop=entropy&cs=srgb&fm=jpg&ixid=M3wxOTcwMjR8MHwxfHJhbmRvbXx8fHx8fHx8fDE3Mzk3ODQwMDR8&ixlib=rb-4.0.3&q=85
coverY: 0
---

# PageCache 详解（Kafka & 操作系统）

## 1.什么是 PageCache？

**PageCache = 操作系统的磁盘缓存**

* 操作系统会自动把磁盘数据缓存到内存，避免每次都直接访问磁盘，提高访问速度。
* Kafka 充分利用 PageCache，不需要自己维护缓存，而是让 OS 管理磁盘和内存之间的数据交换。

**作用**：

* 加速磁盘读取：Kafka 读取消息时，优先从 PageCache 获取数据，避免直接读磁盘，提高吞吐量。
* 提升写入性能：Kafka 顺序写入 PageCache，然后异步刷盘，写入速度更快。
* 减少磁盘 IO：Kafka 依赖 OS 自动管理 PageCache，不需要额外的数据拷贝，避免 CPU 额外负担。

## 2.Kafka 如何利用 PageCache？

Kafka **读写消息**时，依赖 Linux 的 PageCache 机制，提高性能：

| 操作                    | PageCache 机制                 | Kafka 作用            |
| --------------------- | ---------------------------- | ------------------- |
| 写入（Producer -> Kafka） | 数据先写入 PageCache，然后异步刷盘       | 避免直接写磁盘，提高写入吞吐      |
| 读取（Consumer 拉取消息）     | 先从 PageCache 读取，如果缓存命中则不访问磁盘 | 提高读取速度，减少磁盘 IO      |
| 刷盘（Flushing）          | OS 定期把 PageCache 写入磁盘        | Kafka 采用异步刷盘，优化磁盘操作 |

## 3.Kafka PageCache 读写流程

### 3.1. Kafka Producer 端写入

1. Producer 发送消息
2. Kafka 将数据写入 PageCache
3. 操作系统定期将 PageCache 数据刷入磁盘

• Kafka 默认不主动调用 fsync() 刷盘，依赖 OS 自己决定何时刷盘（减少磁盘 IO）。

**PageCache 作用：**

• 生产者（Producer）写入数据时，Kafka 只是在 PageCache 追加日志，不需要立刻落盘，写入速度非常快！

### 3.2. Kafka Consumer 端读取

1\. Consumer 从 Kafka 拉取数据

2\. Kafka 先检查 PageCache

• 如果数据在 PageCache，直接返回（快）。

• 如果数据不在 PageCache，触发磁盘 IO 读取数据（慢）。

3\. OS 自动缓存读取的数据，下次访问时直接从 PageCache 读取。

**PageCache 作用：**

• Kafka 读取大部分热点数据时，几乎不需要访问磁盘，大大减少磁盘 IO，提高消费速度。

## 4.Kafka 如何优化 PageCache？

Kafka 默认充分利用 PageCache，但我们可以调整 OS & Kafka 参数 优化性能。

### 1. 调整 PageCache 刷盘策略

Kafka 默认依赖 OS 自动刷盘（异步刷盘），但可以强制刷盘（减少数据丢失）。

```sh
log.flush.interval.messages=10000   # 每 10,000 条消息刷盘一次
log.flush.interval.ms=5000          # 每 5 秒刷盘一次
```

### 2. 增加 PageCache 内存

Kafka 依赖 OS 缓存大量数据，我们可以增加服务器的可用内存，让 PageCache 存储更多消息，减少磁盘 IO：

```sh
echo 3 > /proc/sys/vm/drop_caches  # 释放 PageCache
```

### 3. 预读优化

Kafka 预先读取大量数据，减少频繁的磁盘 IO：

```sh
log.segment.bytes=1073741824   # 调整 Kafka 日志段大小
log.retention.hours=24         # 调整日志保留时间
```

## 5.PageCache 的优缺点

| 优点                             | 缺点                          |
| ------------------------------ | --------------------------- |
| ✅ 极大减少磁盘 IO，提高吞吐量              | ❌ 服务器重启会丢失缓存，可能影响性能         |
| ✅ 写入几乎无延迟（因为写入 PageCache，而非磁盘） | ❌ 如果 PageCache 过大，可能影响其他应用  |
| ✅ 读取时，热点数据直接从内存获取，速度极快         | ❌ Kafka 本身无法控制 PageCache 释放 |

## 6.总结

* PageCache 是操作系统管理的磁盘缓存，Kafka 充分利用它减少磁盘 IO，提高读写速度。
* Kafka Producer 写入数据时，数据先进入 PageCache，不立即落盘，提升写入吞吐量。
* Kafka Consumer 读取数据时，优先从 PageCache 获取数据，避免访问磁盘，提高消费速度。
* 可以通过增加服务器内存、优化刷盘策略等方式进一步优化 PageCache。

PageCache 是 Kafka 高性能的核心优化之一，合理利用它可以显著提升吞吐量！
