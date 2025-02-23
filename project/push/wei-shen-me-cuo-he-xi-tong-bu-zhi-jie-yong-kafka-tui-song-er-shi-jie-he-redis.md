# 为什么撮合系统不直接用 Kafka 推送，而是结合 Redis？



在高频交易系统中，Kafka 负责 异步事件流处理，但由于 Kafka 设计为 高吞吐、低延迟的消息队列，它并不能很好地满足 实时推送 的需求。因此，我们需要 Redis 来补充以下功能：

Redis + Kafka 的合理分工

| 功能    | Redis                 | Kafka              |
| ----- | --------------------- | ------------------ |
| 数据存储  | 短期缓存（最近订单、深度数据）       | 长期存储（消息流、日志记录）     |
| 查询速度  | 毫秒级（O(1) 查询）          | O(log N)，更适用于事件流处理 |
| 数据一致性 | 最终一致性（短时间缓存，自动过期）     | 严格一致性（可回溯、持久化存储）   |
| 适用场景  | WebSocket/REST API 查询 | 交易日志、异步任务处理        |
| 消息模型  | 发布-订阅（Pub/Sub）        | 事件驱动，日志流           |
| 推送延迟  | <10ms（本地内存）           | 50-100ms+（分布式消息传输） |

## 为什么 Kafka 不能直接用于 WebSocket 推送？

### 1. Kafka 延迟比 Redis 高

* Kafka 主要用于日志流和异步消息处理，通常在 50-100ms 以上，而 WebSocket 需要 <10ms 的低延迟
* Redis Pub/Sub 依赖内存存储，O(1) 查询，推送基本可控在 1-5ms 级别。&#x20;

### 2. Kafka 需要消费确认（Consumer Lag）

* WebSocket 需要即刻推送，而 Kafka 是基于消费组的机制，消费确认可能导致推送延迟。
* 例如，当一个 WebSocket 连接断开后，Kafka 消费者需要重新建立连接，影响推送的实时性。

### 3. Kafka 无法主动推送给特定用户

* WebSocket 需要按 用户订阅的交易对 推送，如 BTC/USDT 或 ETH/USDT。
* Kafka 只会广播消息，而 Redis Pub/Sub 可以灵活处理用户订阅，按需推送数据。

## Kafka + Redis 的推送策略

### 1. 撮合成交后，Kafka 记录事件

* Kafka 负责撮合结果的持久化 & 事件流处理
* Kafka 可以用于 异步日志存储、风控、数据分析

### 2. Redis 负责实时推送

* Kafka 推送数据到 Redis
* Redis 基于 Pub/Sub 或 Stream 进行 WebSocket 推送
* WebSocket 服务器直接从 Redis 读取数据，减少 DB 压力

示例代码

#### 撮合成功后，Kafka 事件推送

```java
// 订单成交后，发送 Kafka 消息
public void sendTradeEvent(TradeEvent trade) {
    kafkaTemplate.send("trade_topic", trade.getOrderId(), trade);
}
```

#### Kafka 消费者写入 Redis

```java
@KafkaListener(topics = "trade_topic", groupId = "matching_group")
public void handleTradeEvent(TradeEvent trade) {
    String key = "trade:" + trade.getSymbol();
    redisTemplate.opsForList().leftPush(key, JSON.toJSONString(trade));
    redisTemplate.expire(key, 10, TimeUnit.SECONDS); // 10秒过期
}
```

#### Redis WebSocket 推送

```java
// Redis 监听撮合数据，推送给 WebSocket 订阅用户
@Cacheable(value = "trade_push", key = "#symbol")
public List<TradeEvent> getTradeData(String symbol) {
    String key = "trade:" + symbol;
    return redisTemplate.opsForList().range(key, 0, -1);
}
```

## 总结

✅ Kafka 负责撮合结果的异步存储 & 日志流

✅ Redis 负责 WebSocket 实时推送，保证低延迟（<10ms）

✅ 结合 Redis & Kafka，确保高并发推送 & 数据一致性

这样设计可以充分利用 Kafka 的高吞吐能力，同时保证 WebSocket 实时推送的低延迟和高并发能力。
