---
description: Kafka 是高吞吐、可扩展的分布式消息队列，在大数据、流式计算、微服务解耦等领域广泛应用。
cover: >-
  https://images.unsplash.com/photo-1737562963380-3a7e45c0bf31?crop=entropy&cs=srgb&fm=jpg&ixid=M3wxOTcwMjR8MHwxfHJhbmRvbXx8fHx8fHx8fDE3Mzk2MzI1OTZ8&ixlib=rb-4.0.3&q=85
coverY: 0
---

# Kafka 架构

本文将详细解析 Kafka 的架构、组件、分区机制、存储、消费模型、高可用策略等。

## 1. Kafka 架构概览

Kafka 采用 分布式、可扩展 架构，由生产者、代理（Broker）、分区、消费者、Zookeeper 组成。

### Kafka 架构图

```
+------------------+     +------------------+     +------------------+
| Producer (P1)   |     | Producer (P2)   |     | Producer (P3)   |
+------------------+     +------------------+     +------------------+
          |                      |                      |
          v                      v                      v
  +------------------ Kafka Cluster --------------------+
  |  +------------------+   +------------------+   +------------------+  |
  |  |  Broker 1       |   |  Broker 2       |   |  Broker 3       |  |
  |  |  ┌──────────┐   |   |  ┌──────────┐   |   |  ┌──────────┐   |  |
  |  |  │Partition 0│   |   |  │Partition 1│   |   |  │Partition 2│   |  |
  |  |  │  Leader  │   |   |  │  Follower │   |   |  │  Follower │   |  |
  |  +------------------+   +------------------+   +------------------+  |
  +-----------------------------------------------------------------------+
          |                      |                      |
          v                      v                      v
  +------------------+     +------------------+     +------------------+
  | Consumer (C1)   |     | Consumer (C2)   |     | Consumer (C3)   |
  +------------------+     +------------------+     +------------------+
```

## 2. Kafka 核心组件

| 组件                   | 作用                               |
| -------------------- | -------------------------------- |
| Producer（生产者）        | 发送消息到 Kafka                      |
| Topic（主题）            | 逻辑上的消息分类（如 order\_topic）         |
| Partition（分区）        | 物理存储单位，Kafka 采用 分区并行读写           |
| Broker（代理）           | Kafka 服务器（多个 Broker 组成 Kafka 集群） |
| Consumer（消费者）        | 消费 Kafka 消息                      |
| Consumer Group（消费者组） | 多个消费者共同消费同一 Topic，提高吞吐量          |
| Zookeeper            | 管理 Kafka 元数据、Leader 选举、集群协调      |

Kafka 是分布式架构，依靠 Zookeeper 实现高可用 & 扩展性

## 3. Kafka 分区机制

Kafka 消息存储在分区（Partition） 中，支持 并行读写，提高吞吐量。

### 分区作用

• 分区（Partition）= 并行单位

• 多个消费者可以并发消费

• 提高 Kafka 读写性能

### 分区分配策略

```
Topic: order_topic
Partition 0 → Consumer 1
Partition 1 → Consumer 2
Partition 2 → Consumer 3
```

### 分区选择策略

| 策略               | 适用场景               |
| ---------------- | ------------------ |
| 随机分区（RoundRobin） | 负载均衡，默认方式          |
| Key 哈希分区（Hash）   | 相同 Key 进入同一分区，保持顺序 |
| 手动指定分区           | 指定数据路由             |

### 示例

```
ProducerRecord<String, String> record = new ProducerRecord<>("order_topic", "user123", "order_created");
producer.send(record);
```

相同 user123 订单总是进入同一分区，保证消息顺序性

## 4. Kafka 副本机制（高可用）

Kafka 每个分区有多个副本（Replica），确保 数据不丢失。

### 副本类型

| 类型          | 作用             |
| ----------- | -------------- |
| Leader 副本   | 负责读写请求         |
| Follower 副本 | 备份数据，同步 Leader |

### ISR（同步副本集合）

Kafka 只有 ISR 副本 才能成为新 Leader，保证数据一致性。

### Leader 选举

• Leader 宕机 → Follower 晋升为 Leader

• 保证 Kafka 高可用

Kafka 采用 副本 + Leader 选举 方案，确保数据安全！

## 5. Kafka 消息存储

Kafka 采用日志存储消息，支持顺序写 & 零拷贝。

### 存储结构

```
/var/kafka-logs/
 ├── order_topic-0/
 │   ├── 00000000000000000000.log  # 消息日志
 │   ├── 00000000000000000000.index  # 索引
 │   ├── leader-epoch-checkpoint  # 选举信息
```

### Kafka 存储优化

| 优化点              | 作用                |
| ---------------- | ----------------- |
| PageCache        | OS 级缓存，减少磁盘 IO    |
| 顺序写磁盘            | 避免随机 IO，性能提升 10 倍 |
| 日志分段（LogSegment） | 定期清理旧数据，防止磁盘占满    |

Kafka 存储基于磁盘，但 比内存存储（Redis）还快！

## 6. Kafka 消费模型

Kafka 消费模式 = 订阅 + 拉取（Pull），支持多消费者并发。

### 消费方式

| 模式            | 特点           |
| ------------- | ------------ |
| 单消费者（独占模式）    | 一个消费者读取所有分区  |
| 消费者组（并行消费）    | 多个消费者消费多个分区  |
| 广播模式（不同组都能消费） | 消息可以被多个消费组消费 |

### 手动提交 Offset

```
consumer.commitSync();  // 同步提交
consumer.commitAsync();  // 异步提交（提高吞吐）
```

Kafka 允许手动提交 Offset，确保消费幂等性！

## 7. Kafka 事务

Kafka 支持事务，保证多个 Topic 消息要么全部提交，要么全部回滚。

### 事务示例

```
producer.initTransactions();
producer.beginTransaction();
producer.send(new ProducerRecord<>("topic1", "key", "value"));
producer.commitTransaction();
```

事务用于确保 Kafka 消息一致性

## 8. Kafka 监控与优化

### 关键监控指标

| 指标                        | 作用      |
| ------------------------- | ------- |
| Lag（消费延迟）                 | 消费者落后程度 |
| ISR 副本数                   | 副本同步情况  |
| UnderReplicatedPartitions | 副本丢失    |

### 优化策略

| 优化项               | 作用       |
| ----------------- | -------- |
| 批量处理（batch.size）  | 提高吞吐量    |
| PageCache + 零拷贝   | 提高 IO 速度 |
| 压缩消息（Snappy/Gzip） | 减少网络传输开销 |

Kafka 优化的核心在于 分区并行 + 批量处理 + 高效存储

## 9. Kafka 面试高频问题

| 类别  | 核心问题                               |
| --- | ---------------------------------- |
| 架构  | Kafka 为什么快？Kafka 分区如何工作？           |
| 存储  | Kafka 消息存储在哪里？如何保证高吞吐？             |
| 副本  | Kafka 如何保证数据不丢失？ISR 是什么？           |
| 消费者 | Kafka 如何保证 Exactly Once？Offset 机制？ |
| 事务  | Kafka 如何实现分布式事务？                   |
