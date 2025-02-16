---
cover: >-
  https://images.unsplash.com/photo-1735732519861-3b67d0aee297?crop=entropy&cs=srgb&fm=jpg&ixid=M3wxOTcwMjR8MHwxfHJhbmRvbXx8fHx8fHx8fDE3Mzk3MDA3NTV8&ixlib=rb-4.0.3&q=85
coverY: 0
---

# Kafka 如何保证消息不丢失

Kafka 在消息可靠性方面做了多重保障，确保 消息不丢失，主要包括以下几方面：

🔥 Kafka 如何保证消息不丢失？（核心机制）

| 保障机制                     | 作用                      | 关键参数 / 机制                            |
| ------------------------ | ----------------------- | ------------------------------------ |
| 生产者（Producer）ACK 确认      | 确保消息成功发送到 Kafka         | acks=all                             |
| Producer 重试 & 幂等性        | 失败时自动重试，防止消息重复          | retries、enable.idempotence=true      |
| Broker 副本同步（Replication） | 数据多副本存储，提高可靠性           | min.insync.replicas                  |
| ISR 机制（同步副本集合）           | 只有同步副本集才能提供服务           | unclean.leader.election.enable=false |
| 数据持久化（日志存储）              | 顺序写入 + PageCache，防止消息丢失 | log.dirs                             |
| Consumer Offset 机制       | 断点续传，防止消息丢失             | enable.auto.commit=false             |
| 消费端重复消费 & 事务             | 结合事务和幂等，保证一致性           | Kafka 事务 (transactional.id)          |

## 1. 生产者（Producer）如何防止消息丢失？

Kafka Producer 通过 ACK 确认机制 + 重试机制 + 幂等性 来保证消息可靠发送：

### 1.1 ACK 机制

acks 参数决定 Producer 需要等多少个 Kafka Broker 确认，才能认为消息发送成功：

• acks=0：不等待 Broker 确认，高吞吐但可能丢数据（不可靠）

• acks=1：Leader 副本写入成功即可，Leader 崩溃时可能丢数据

• acks=all：所有同步副本（ISR）写入成功，最安全但延迟较高

👉 生产环境推荐：

```
acks=all
```

保证数据至少写入所有 同步副本（ISR），防止 Leader 崩溃导致数据丢失。

## 1.2 重试机制

如果 Producer 发送失败（如网络异常），Kafka 支持自动重试：

```
retries=5  # 失败重试 5 次
```

避免因瞬时网络波动导致消息丢失。

### 1.3 幂等性（Idempotence）

开启 enable.idempotence=true，Kafka 自动去重，防止 Producer 端 重试导致重复消息：

```
enable.idempotence=true
```

• Kafka 通过 Producer ID（PID）+ 序列号 确保 Producer 端的 消息不丢失 & 不重复。

## 2. Kafka Broker 如何保证数据不丢失

Kafka 采用 多副本机制（Replication）+ ISR 机制 保障数据存储安全。

### 2.1 副本复制机制

Kafka 每个分区（Partition）都有多个副本（Replica），其中：

• Leader 副本：处理读写请求

• Follower 副本：从 Leader 复制数据

如果 Leader 副本宕机，Kafka 会 自动选举 Follower 作为新 Leader，防止数据丢失。

### 2.2 ISR（In-Sync Replicas，同步副本集）

Kafka 维护一个 ISR 副本列表，其中：

• Leader & ISR 副本 保持数据同步

• 只有 ISR 内的副本可以被选为 Leader

👉 生产环境推荐：

```
unclean.leader.election.enable=false
```

禁止选举落后副本为 Leader，避免数据丢失。

### 2.3 min.insync.replicas 配置

控制最少有多少个 ISR 同步副本 才允许 Producer 继续写入：

```
min.insync.replicas=2
```

• 保障至少 2 个副本 有数据，Leader 崩溃时仍能恢复数据。

## 3. Kafka 持久化（Storage）如何保证数据不丢失？

Kafka 日志存储+顺序写入+PageCache，防止 磁盘 IO 造成数据丢失。

### 3.1 顺序写入

Kafka 采用 顺序写入（Append-Only Log）：

• 避免随机磁盘 IO，提升吞吐

• 写入 PageCache，异步刷盘

### 3.2 PageCache 机制

Kafka 优先写入 PageCache，然后异步刷盘：

• 数据未刷盘时，若机器崩溃可能丢失

• 设置定期刷盘，确保数据落盘

👉 生产环境推荐：

```
log.flush.interval.messages=10000  # 每 10000 条消息刷盘
log.flush.interval.ms=5000         # 每 5 秒刷盘一次
```

## 4. 消费者（Consumer）如何保证消息不丢失？

Kafka Consumer 通过 Offset 机制（手动提交 / 自动提交），保证 断点续传，防止 消费丢失。

### 4.1 Offset 机制

Kafka 每个 Consumer Group 维护 Offset：

• 自动提交（enable.auto.commit=true）

• 可能会导致消息未消费成功，Offset 仍然提交

• 手动提交（enable.auto.commit=false）

• 只有 Consumer 确认处理成功 后才提交 Offset，防止消息丢失

👉 生产环境推荐：

```
enable.auto.commit=false
```

• 消费完成后，手动提交 Offset，确保消息被成功处理。

## 5. Kafka 事务机制（Exactly-Once）

Kafka 支持事务，确保 消息不丢失 & 不重复：

1\. 事务 Producer：多个 Partition 作为一个事务提交，避免部分成功、部分失败

2\. 消费端事务：Consumer 处理完后，再提交 Offset，防止消息丢失

👉 生产环境推荐：

```
transactional.id=my-transactional-id
```

• 结合 事务+幂等性，保障 Exactly-Once 语义。

## 6.总结

Kafka 从 Producer 发送端 → Broker 存储端 → Consumer 消费端 提供全链路保障：

| 级别       | 方案                                     | 作用                |
| -------- | -------------------------------------- | ----------------- |
| Producer | ✅ acks=all                             | 确保消息写入所有 ISR 副本   |
|          | ✅ retries=5                            | 失败时自动重试，避免丢失      |
|          | ✅ enable.idempotence=true              | 幂等写入，防止重试丢失       |
| Broker   | ✅ 多副本同步（Replication）                   | 保障 Leader 宕机数据不丢失 |
|          | ✅ min.insync.replicas=2                | 确保至少 2 个副本存活      |
|          | ✅ unclean.leader.election.enable=false | 禁止落后副本选举为 Leader  |
| Storage  | ✅ 顺序写入日志（Append-Only Log）              | 避免随机 IO，保障吞吐      |
|          | ✅ PageCache 机制                         | 优先写缓存，异步刷盘        |
| Consumer | ✅ 手动提交 Offset                          | 防止消息未消费成功即丢失      |
| 事务       | ✅ Kafka 事务（Exactly-Once）               | 防止重复消费 & 丢失       |

💡 最终结论：Kafka 通过 ACK + 多副本 + ISR + 持久化 + 事务，确保消息不丢失，是高可靠分布式消息队列的首选！
