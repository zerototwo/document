# Kafka 如何保证消息只被消费一次（Exactly-Once）

Kafka 默认情况下 只能保证 At-Least-Once（至少一次） 或 At-Most-Once（至多一次），但要实现 Exactly-Once（恰好一次），需要 结合 Kafka 事务（Transactional API）和幂等性（Idempotent Producer）。

🔥 Kafka 消费语义：**At-Most-Once**、**At-Least-Once**、**Exactly-Once**

| 消费语义                | 机制                              | 可能问题         |
| ------------------- | ------------------------------- | ------------ |
| At-Most-Once（至多一次）  | 消费前提交 Offset                    | 可能丢失消息       |
| At-Least-Once（至少一次） | 先消费消息，再提交 Offset                | 可能重复消费       |
| Exactly-Once（恰好一次）  | Kafka 事务（Transactional API）+ 幂等 | 保证每条消息只被处理一次 |

## 1. 幂等 Producer（Idempotent Producer）

Kafka 允许 Producer 开启幂等性（Idempotence），确保 消息不会因为重试而重复发送。

### 1.1 开启 Producer 幂等性

```
enable.idempotence=true
```

• Kafka 会为每条消息 分配一个 Producer ID（PID） 和 序列号。

• Broker 端自动去重，即使 Producer 重试 也不会生成重复消息。

👉 作用：防止 Producer 端因网络波动导致的重复发送问题。

## 2. Kafka 事务（Transactional API）

Kafka 提供事务（Transactions），可以 保证多个分区写入 & 消费的原子性，从而保证 消费仅被处理一次。

### 2.1 开启事务 Producer

```
transactional.id=my-transaction-id
```

• Producer 端 以 事务方式提交消息，确保多个分区的写入 要么全部成功，要么全部失败。

• Consumer 端 只有 事务提交成功，才会消费这批数据。

## 3. Exactly-Once 消费端处理

Kafka 默认是 At-Least-Once 语义，但可以通过 事务提交 Offset + 幂等写入目标存储，确保 消费不会重复。

### 3.1 Consumer 端手动提交 Offset

```
enable.auto.commit=false
```

• Kafka 默认是自动提交 Offset，但如果 消费失败，Offset 也会提交，导致消息丢失。

• 改为手动提交，只有在成功处理数据后才提交 Offset，确保数据被正确消费。

## 4. 事务性 Consumer + 幂等写入

消费端需要满足：

1\. 消费完成后，确保数据成功存入数据库（MySQL / Redis）

2\. 消费成功后，手动提交 Kafka Offset

🔥 Kafka Exactly-Once 方案总结

| 方案              | 作用                     | 关键参数 / 机制                          |
| --------------- | ---------------------- | ---------------------------------- |
| 幂等 Producer     | 防止 Producer 重试导致的重复发送  | enable.idempotence=true            |
| 事务 Producer     | 确保 Producer 端提交数据的原子性  | transactional.id=my-transaction-id |
| 事务性 Consumer    | 确保 Consumer 只消费一次，不会重复 | enable.auto.commit=false           |
| 幂等写入（数据库/Redis） | 避免消费端因失败而重复写入          | 业务端幂等处理                            |

## 5.结论

Kafka 默认不支持 Exactly-Once，但可以通过 幂等 Producer + 事务 + 手动提交 Offset，实现 消息只被消费一次：

1\. 开启幂等 Producer：防止 Producer 重试导致的重复消息

2\. 使用事务 Producer：确保 Producer 端写入多个分区的原子性

3\. 手动提交 Offset：确保 Kafka 消息处理完成后才提交 Offset，避免重复消费

4\. 幂等写入目标存储：确保数据库 / Redis 端不会因为 Consumer 重试而插入重复数据

💡 最终保证 Kafka 实现 Exactly-Once 语义，避免重复消费！ 🚀
