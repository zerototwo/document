---
description: Kafka 本身不支持强一致性事务，但可以通过幂等性、事务机制、补偿机制、回滚策略等设计分布式事务，常见方案包括：
cover: >-
  https://images.unsplash.com/photo-1737961756297-ced6badbd700?crop=entropy&cs=srgb&fm=jpg&ixid=M3wxOTcwMjR8MHwxfHJhbmRvbXx8fHx8fHx8fDE3Mzk1NTI0NjN8&ixlib=rb-4.0.3&q=85
coverY: 0
---

# 如何用 Kafka 设计分布式事务？

* Kafka 事务机制
* 基于消息队列的可靠事件最终一致性
* TCC + Kafka
* Kafka + 事务日志表
* Kafka + Outbox + CDC

## 1. Kafka 事务机制

Kafka 自身支持事务，确保生产者批量消息要么全部提交，要么全部回滚，但仅适用于 Kafka 内部事务，无法直接解决 分布式事务。

### 1.1 Kafka 事务机制

* 开启事务
* 多条消息作为一个事务提交
* 保证 Exactly-Once 语义（EOS）

### 示例

```java
KafkaProducer<String, String> producer = new KafkaProducer<>(props);

// 开启事务
producer.initTransactions();

try {
    producer.beginTransaction();
    producer.send(new ProducerRecord<>("topic1", "key1", "value1"));
    producer.send(new ProducerRecord<>("topic2", "key2", "value2"));
    producer.commitTransaction(); // 事务提交
} catch (Exception e) {
    producer.abortTransaction(); // 事务回滚
}
```

### 适用场景

* Kafka 内部事务（多个 Topic 之间的事务保证）

❌ 无法解决多个服务的分布式事务问题

## 2. 可靠消息最终一致性（基于 Kafka）

Kafka 常用于异步解耦，配合事务表或幂等处理，实现 最终一致性。

### 2.1 方案核心

1. 业务执行成功后，发送 Kafka 消息
2. 消费者保证消费成功，不成功就重试
3. 消费失败时，日志 & 补偿机制
4. 结合事务日志（Outbox）+ CDC 保证最终一致性

#### 示例：订单系统

1. 用户下单（事务提交）
2. 插入订单数据 + 发送 Kafka 消息
3. 库存服务监听 Kafka，扣减库存
4. 支付服务监听 Kafka，处理支付

#### 事务日志表

```sql
INSERT INTO order (order_id, user_id, amount, status) VALUES (1, 1001, 99.99, 'INIT');
INSERT INTO transaction_log (log_id, order_id, status) VALUES (101, 1, 'PENDING');
```

✅ 确保数据库操作 & Kafka 发送在一个事务内

```java
@Transactional
public void createOrder(Order order) {
    orderRepository.save(order); // 订单入库
    kafkaTemplate.send("order-topic", order.getId()); // 发送 Kafka 消息
}
```

📌 消费者端

```java
@KafkaListener(topics = "order-topic")
public void handleOrder(String orderId) {
    try {
        // 幂等性检查
        if (!isProcessed(orderId)) {
            processOrder(orderId);
            markProcessed(orderId);
        }
    } catch (Exception e) {
        log.error("订单处理失败", e);
        throw new KafkaProcessingException("重试"); // 触发重试
    }
}
```

✅ 消费者端保证幂等性，防止消息重复消费。

## 3. Kafka + TCC

TCC（Try-Confirm-Cancel）是一种柔性事务，结合 Kafka 确保最终一致性。

### 流程

1\. Try 阶段

* 执行业务预留资源
* 记录事务状态
* 发送 Kafka 事件

2\. Confirm 阶段

* 真正提交业务
* 消费 Kafka 消息，确认执行

3\. Cancel 阶段

* 回滚操作

### 示例

```java
@Transactional
public void tryReserveStock(String orderId) {
    stockRepository.reserveStock(orderId); // 预扣库存
    kafkaTemplate.send("reserve-stock", orderId);
}

@KafkaListener(topics = "reserve-stock")
public void confirmStock(String orderId) {
    stockRepository.confirmStock(orderId); // 确认库存扣减
}
```

✅ 适用于高一致性要求的分布式事务。

## 4. Kafka + Outbox + CDC

Kafka 可以结合 Outbox + CDC（Change Data Capture） 确保 事务操作 & 消息发送一致。

### 原理

1. 数据库事务插入业务数据 + Outbox
2. Debezium 监听 Outbox 变更，推送 Kafka
3. 消费者订阅 Kafka 处理业务

### 示例

```sql
BEGIN;
INSERT INTO order (order_id, user_id, amount) VALUES (1, 1001, 99.99);
INSERT INTO outbox (event_id, event_type, payload) VALUES (101, 'ORDER_CREATED', '{order_id:1}');
COMMIT;
```

### CDC 监听变更

```
debezium:
  connector: mysql
  database: order_db
  table.include.list: outbox
  kafka.bootstrap.servers: kafka:9092
```

✅ 确保消息 & 业务数据一致性，防止丢失消息。

## 5. Kafka + 事务日志表

结合 Kafka + 事务日志表 方式，可以确保 Kafka 事件不丢失。

### 流程

1. 事务操作完成后，记录事务日志
2. 定期检查未成功的事务
3. 重试 Kafka 发送

### 示例

```sql
BEGIN;
INSERT INTO order (order_id, user_id, amount) VALUES (1, 1001, 99.99);
INSERT INTO transaction_log (tx_id, status) VALUES (101, 'PENDING');
COMMIT;
```

✅ 结合定时任务补偿机制，防止消息丢失。

## 6. 方案对比

| 方案           | 一致性    | 吞吐量 | 适用场景        |
| ------------ | ------ | --- | ----------- |
| Kafka 内置事务   | ✅ 高    | ❌ 低 | Kafka 内部事务  |
| 可靠消息最终一致性    | ✅ 高    | ✅ 高 | 业务异步解耦      |
| TCC + Kafka  | ✅✅ 强一致 | ❌ 低 | 高一致性业务      |
| Outbox + CDC | ✅ 高    | ✅ 高 | 确保事务 & 消息一致 |
| 事务日志表        | ✅ 中    | ✅ 高 | 业务补偿机制      |

## 7. 结论

* 最终一致性事务 → 推荐 Kafka + Outbox / 事务日志表
* 高可靠事务 → 推荐 Kafka + TCC
* 吞吐量优先 → 采用 Kafka + 幂等消费

🚀 选择合适的方案，保证分布式事务安全 & 高效执行！
