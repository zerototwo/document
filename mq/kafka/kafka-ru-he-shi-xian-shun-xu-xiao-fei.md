---
description: Kafka 默认不能保证全局顺序，但 可以保证分区（Partition）内的消息顺序。因此，Kafka 的 顺序消费 主要是基于分区来实现的。
cover: >-
  https://images.unsplash.com/photo-1735447814306-8887e953a91f?crop=entropy&cs=srgb&fm=jpg&ixid=M3wxOTcwMjR8MHwxfHJhbmRvbXx8fHx8fHx8fDE3Mzk3ODE1ODJ8&ixlib=rb-4.0.3&q=85
coverY: 0
---

# Kafka 如何实现顺序消费

## Kafka 默认的顺序保证

1\. 同一个分区（Partition）内的消息是有序的：

* 生产者 按照发送顺序 追加数据到分区日志（Log）。
* 消费者 按照偏移量（Offset）顺序 依次消费消息。

2\. 不同分区间的消息无全局顺序保证：

* 多个分区并行消费，无法保证不同分区的消费顺序。



## Kafka 顺序消费的常见策略

### 方案 1：单分区（Single Partition）

适用场景：强顺序消费场景，如 订单、交易、金融结算。

#### 实现方式：

* Producer 只往 一个 Partition 发送消息。
* Consumer 只能有 一个实例 消费该 Partition。

#### 示例代码（指定单个分区）：

```java
ProducerRecord<String, String> record = new ProducerRecord<>("topic-name", 0, "key", "message");
producer.send(record);
```

#### 优缺点：

| 优点     | 缺点                   |
| ------ | -------------------- |
| 保证全局顺序 | 吞吐量受限（Kafka 只能用一个分区） |
| 实现简单   | 无法并发消费，性能低           |

### 方案 2：基于 Key 进行分区（Partition Key Hash）

适用场景：保证同一业务实体（如订单 ID）消息顺序。

#### 实现方式：

* 相同 Key 的消息 被 Kafka 发送到相同的分区。
* 消费者 按照分区顺序 消费消息。

#### 示例代码（使用 Key 保证相同分区）：

```java
ProducerRecord<String, String> record = new ProducerRecord<>("topic-name", "order_123", "message");
producer.send(record);
```

#### 优缺点：

| 优点           | 缺点             |
| ------------ | -------------- |
| 支持并发消费（多个分区） | 不保证全局顺序        |
| 单个 Key 顺序保证  | 分区数受限，可能导致分区热点 |

### 方案 3：单消费者组 + 单线程消费

适用场景：消费者业务逻辑要求严格顺序，但 分区数 > 1。

\


#### 实现方式：

* Kafka 分区数 > 1，消费者组内只有 1 个 Consumer 实例。
* Consumer 采用单线程拉取消息，按照顺序处理。

#### 示例代码（单线程拉取消息）：

```java
KafkaConsumer<String, String> consumer = new KafkaConsumer<>(props);
consumer.subscribe(Collections.singletonList("topic-name"));

while (true) {
    ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));
    for (ConsumerRecord<String, String> record : records) {
        // 按顺序处理消息
        process(record);
    }
}
```

#### 优缺点：

| 优点          | 缺点              |
| ----------- | --------------- |
| 支持多分区，提升吞吐量 | 无法并行消费，可能影响处理效率 |

### 方案 4：Kafka + 外部排序（如数据库、Redis）

适用场景：最终一致性业务，如 日志分析、延迟处理任务。

#### 实现方式：

* Kafka 消费者并行消费，将数据写入数据库 / Redis。
* 业务端 基于时间戳 / 业务 ID 进行排序。&#x20;

#### 示例代码（基于 Redis 排序）：

```java
String orderKey = "order_123";
jedis.zadd("order_queue", timestamp, message);
```

#### 优缺点：

| 优点      | 缺点                   |
| ------- | -------------------- |
| 支持高并发   | 需要额外存储（如 Redis / DB） |
| 最终一致性顺序 | 实时性较差                |

## 总结

| 方案                    | 特点                 | 适用场景        |
| --------------------- | ------------------ | ----------- |
| 单分区（Single Partition） | 最高保证顺序，但吞吐量低       | 强顺序业务（金融交易） |
| 基于 Key 进行分区           | Key 相同的消息顺序消费，支持并发 | 订单、用户操作日志   |
| 单消费者组 + 单线程消费         | 可提升吞吐量，但无法并发处理     | 严格顺序消费      |
| Kafka + 外部排序          | 适合最终一致性业务          | 日志、延迟处理任务   |

最佳实践

* 如果需要严格顺序，使用 单分区 或 单消费者。
* 如果需要并发 + 局部顺序，使用 Partition Key 控制消息落到相同分区。
* 如果能接受最终一致性，采用 数据库 / Redis 排序。\


👉 选择最适合业务的方式，保证 Kafka 顺序消费 🚀
