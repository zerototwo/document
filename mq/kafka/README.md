---
description: Kafka 作为高吞吐、分布式、可扩展的消息队列，在面试中涉及架构、分区、副本、消息存储、消费者、事务、分布式事务、监控优化等多个方面。
---

# Kafka

## 1. Kafka 基础

| 问题                              | 核心知识点                                                                    |
| ------------------------------- | ------------------------------------------------------------------------ |
| Kafka 是什么？适用于哪些场景？              | 高吞吐、可扩展的 分布式消息队列，用于 日志收集、流式处理、解耦、事件驱动架构                                  |
| Kafka 组成架构？                     | Producer（生产者）、Broker（集群）、Topic（主题）、Partition（分区）、Consumer（消费者）、Zookeeper |
| Kafka 为什么比 RabbitMQ、RocketMQ 快？ | 顺序写磁盘（PageCache）、零拷贝（sendfile）、批量处理、分区并行读写                               |
| Kafka 的存储机制？                    | 日志分段（Log Segment）、索引文件（Index）、PageCache                                  |

### Kafka 基本命令

```
# 创建 Topic（3 分区，2 副本）
kafka-topics.sh --create --topic my_topic --partitions 3 --replication-factor 2 --bootstrap-server localhost:9092

# 生产者发送消息
kafka-console-producer.sh --topic my_topic --bootstrap-server localhost:9092

# 消费者消费消息
kafka-console-consumer.sh --topic my_topic --from-beginning --bootstrap-server localhost:9092
```

## 2. Kafka 分区（Partition）

| 问题             | 核心知识点                                       |
| -------------- | ------------------------------------------- |
| Kafka 为什么使用分区？ | 并行读写，提高吞吐量                                  |
| Kafka 分区如何分配？  | RoundRobin（轮询）、Hash 取模、StickyAssignor（粘性分配） |
| 如何选择分区数？       | 结合 生产者并发、消费者数量、吞吐量 计算                       |

📌 示例

```
// 生产者指定分区
ProducerRecord<String, String> record = new ProducerRecord<>("topic", 1, "key", "message");
producer.send(record);
```

✅ 分区越多，吞吐量越高，但不宜过多（分布式管理开销增加）

## 3. Kafka 副本机制

| 问题                        | 核心知识点                        |
| ------------------------- | ---------------------------- |
| Kafka 如何保证高可用？            | 副本（Replica）机制                |
| ISR（同步副本）和 AR（所有副本）区别？    | ISR（动态变化，主副本+存活的 follower）   |
| Kafka Leader 选举机制？        | Zookeeper 选举，ISR 中选择新 Leader |
| min.insync.replicas 参数作用？ | 确保至少 N 个副本同步，防止数据丢失          |

📌 示例

```
# 只要 2 个副本确认收到数据，才算成功
acks=all
min.insync.replicas=2
```

✅ 副本越多，数据安全性越高，但写入延迟增加

## 4. Kafka 生产者

| 问题                  | 核心知识点                                      |
| ------------------- | ------------------------------------------ |
| Kafka 生产者的工作原理？     | Producer → 分区选择 → 发送到 Broker               |
| Kafka 生产者如何保证消息可靠性？ | acks=1、acks=all（等待所有副本同步）                  |
| Kafka 生产者如何提高吞吐量？   | 批量发送（batch.size）、压缩（compression.type）、异步发送 |
| Kafka 发送失败怎么办？      | 重试（retries）+ 幂等（idempotence）               |

📌 高吞吐生产者

```
props.put("batch.size", 16384);  // 批量发送
props.put("linger.ms", 10);  // 10ms 内合并多条消息
props.put("compression.type", "snappy"); // 压缩
```

✅ 批量合并 & 压缩，吞吐量提升 3\~5 倍

## 5. Kafka 消费者

| 问题                             | 核心知识点                                                       |
| ------------------------------ | ----------------------------------------------------------- |
| Kafka 消费者如何消费数据？               | Consumer Group（组内多个消费者并行消费）                                 |
| Kafka 消费者如何保证 Exactly-Once 语义？ | 事务 + 幂等性（Idempotence）                                       |
| Kafka 消费者如何提交 Offset？          | 自动提交（enable.auto.commit=true）+ 手动提交（commitSync/commitAsync） |
| Kafka 如何保证消费顺序？                | 同一个分区由一个消费者消费                                               |

📌 手动提交 Offset

```
consumer.commitSync();  // 同步提交
consumer.commitAsync();  // 异步提交（提高吞吐量）
```

✅ 手动提交更安全，避免消息丢失

## 6. Kafka 事务

| 问题               | 核心知识点                                               |
| ---------------- | --------------------------------------------------- |
| Kafka 事务如何实现？    | Producer 事务 API（initTransaction, commitTransaction） |
| Kafka 事务的作用？     | 保证多个 Topic 消息一致性                                    |
| Kafka 事务和幂等有啥区别？ | 事务保证批量操作一致性，幂等保证消息不重复                               |

📌 事务示例

```
producer.initTransactions();
producer.beginTransaction();
producer.send(new ProducerRecord<>("topic1", "key", "value"));
producer.commitTransaction();
```

✅ 适用于金融、电商等高一致性业务

## 7. Kafka 分布式事务

| 问题                        | 核心知识点                               |
| ------------------------- | ----------------------------------- |
| Kafka 如何实现分布式事务？          | Outbox + CDC、事务日志、TCC + Kafka       |
| 如何保证 Kafka 生产者 & 消费者事务一致？ | Kafka 事务 API + Exactly Once 语义（EOS） |

📌 Kafka + Outbox

```
INSERT INTO orders (id, status) VALUES (1, 'NEW');
INSERT INTO outbox (event, payload) VALUES ('ORDER_CREATED', '{"id":1}');
```

✅ 事务日志 + CDC 确保最终一致性

## 8. Kafka 监控与优化

| 问题                | 核心知识点                                       |
| ----------------- | ------------------------------------------- |
| Kafka 监控哪些指标？     | Lag（消费延迟）、ISR 副本数、UnderReplicatedPartitions |
| Kafka 如何优化吞吐量？    | 分区扩展、批量处理、零拷贝、PageCache                     |
| Kafka 发生分区不均衡怎么办？ | Kafka Rebalance（RebalanceListener）          |

📌 监控 Lag

```
kafka-consumer-groups.sh --describe --group my_group --bootstrap-server localhost:9092
```

✅ Lag 过高说明消费速度跟不上，需扩展消费者

## 9. Kafka 高频面试真题总结

| 类别  | 核心问题                         |
| --- | ---------------------------- |
| 架构  | Kafka 为什么快？Kafka 分区如何工作？     |
| 存储  | Kafka 消息存储在哪里？如何保证高吞吐？       |
| 生产者 | 如何保证消息不丢失？如何提高写入性能？          |
| 消费者 | 如何保证 Exactly Once？Offset 机制？ |
| 事务  | Kafka 如何实现分布式事务？幂等性如何实现？     |
| 分布式 | Kafka 副本机制？如何保证 Leader 选举？   |
| 优化  | 如何优化 Kafka？Kafka 监控哪些关键指标？   |
