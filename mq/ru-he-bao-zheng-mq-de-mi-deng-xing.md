# 如何保证 MQ 的幂等性？

幂等性（Idempotency）指 无论一个操作执行多少次，结果都是一样的。

在 MQ（如 Kafka、RabbitMQ、RocketMQ、Redis Stream）中，如果消息被重复消费，如何避免业务逻辑被重复执行？

## 1. MQ 消息重复的原因

消息队列中的 消息重复 主要发生在：

### 1.1 生产端（Producer）重复发送

* 网络超时，生产者未收到 ACK，重试发送。
* 事务消息回查（RocketMQ）。

### 1.2. 消费端（Consumer）重复消费

* 消费 ACK 丢失，导致消息被重新投递。
* MQ 重试机制，消费者处理失败时，MQ 重新投递消息。

## 2. 幂等性的常见解决方案

| 方案                   | 适用场景                | 适用 MQ                       | 核心思路                |
| -------------------- | ------------------- | --------------------------- | ------------------- |
| 去重表（唯一键）             | 数据库操作               | Kafka / RocketMQ / RabbitMQ | 记录已处理的 msgId，防止重复消费 |
| 分布式锁（Redis/Etcd）     | 分布式场景               | Kafka / RabbitMQ            | 每个消息只允许一个消费者处理      |
| Token 机制             | 支付、扣款等敏感业务          | Kafka / RocketMQ            | 生成唯一 Token，避免重复请求   |
| 幂等操作（自然幂等）           | 数据库 Update / Delete | 适用于所有 MQ                    | 更新操作保证唯一性           |
| MQ 事务 / Exactly-Once | 流计算                 | Kafka / RocketMQ            | 事务性消息，避免重复提交        |

## 3. 方案 1：去重表（唯一键）

适用于：数据库操作（支付、订单系统）

思路

* 使用数据库唯一键（msgId）防止重复插入。
* 每次消费前检查 msgId 是否已存在，已存在则丢弃。

```sql
CREATE TABLE order_table (
    order_id VARCHAR(50) PRIMARY KEY,  -- 订单 ID 作为唯一键
    user_id VARCHAR(50),
    amount DECIMAL(10,2)
);
```

```java
public void processMessage(String msgId, Order order) {
    if (orderDao.existsById(msgId)) {
        return;  // 已处理，丢弃消息
    }
    orderDao.save(order); // 订单入库
}
```

适用于业务中涉及数据库写入的场景（如订单、支付）。

## 4. 方案 2：分布式锁

适用于：高并发场景（多个消费者处理相同消息）

思路

* 使用 Redis 分布式锁，保证 同一条消息只能被一个消费者处理。

```java
String lockKey = "mq_lock:" + msgId;
boolean acquired = redis.setIfAbsent(lockKey, "LOCK", 10, TimeUnit.SECONDS);
if (!acquired) {
    return; // 其他实例已经处理
}
try {
    processBusinessLogic();
} finally {
    redis.delete(lockKey);
}
```

✅ 适用于高并发场景，如秒杀、扣库存等业务。

## 5. 方案 3：Token 机制

适用于：分布式事务（如支付系统）

思路

* 客户端生成 Token，保证同一请求唯一。
* 服务端检查 Token 是否已使用。

```java
String token = generateUniqueToken();
if (redis.exists(token)) {
    return; // 订单已处理
}
redis.set(token, "USED", 5, TimeUnit.MINUTES);
processPayment();
```

✅ 适用于金融支付、扣款等事务性业务。

## 6. 方案 4：幂等操作（自然幂等）

适用于：数据库 Update / Delete 操作

思路

* 使用 UPDATE / DELETE 代替 INSERT，保证 多次执行结果相同。

```java
public void updateUserBalance(String userId, BigDecimal amount) {
    userDao.updateBalance(userId, amount); // SQL 内部保证幂等
}
```

✅ 适用于状态更新场景，如订单状态更新、账户余额扣减。

## 7. 方案 5：MQ 事务 / Exactly-Once

适用于：流计算（Kafka + Flink）

✅ 思路

• Kafka 事务（Exactly-Once 语义） 确保消息只被处理一次。

```java
producer.initTransactions();
try {
    producer.beginTransaction();
    producer.send(record);
    producer.commitTransaction();
} catch (Exception e) {
    producer.abortTransaction();
}
```

✅ 适用于 Kafka 事务消息，保证数据一致性。

## 8. MQ 幂等性最佳实践

| 场景    | 推荐方案               |
| ----- | ------------------ |
| 数据库插入 | 去重表（唯一索引）          |
| 高并发消费 | 分布式锁（Redis）        |
| 支付、扣款 | Token 机制           |
| 状态更新  | 自然幂等（UPDATE 语句）    |
| 流计算   | Kafka Exactly-Once |

🚀 幂等性方案应根据业务需求选择，数据库写入建议使用唯一键去重，流计算推荐 Kafka 事务。
