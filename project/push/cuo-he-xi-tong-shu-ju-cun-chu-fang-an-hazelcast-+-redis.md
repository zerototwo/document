---
cover: >-
  https://images.unsplash.com/photo-1737408250641-575773a9feb4?crop=entropy&cs=srgb&fm=jpg&ixid=M3wxOTcwMjR8MHwxfHJhbmRvbXx8fHx8fHx8fDE3NDAzMTYzMjN8&ixlib=rb-4.0.3&q=85
coverY: 0
---

# 撮合系统数据存储方案 (Hazelcast + Redis)

<br>

本方案基于 Hazelcast (IMap 分布式存储) + Redis (缓存 & 低延迟推送) + Kafka (事件驱动)，确保高并发交易的 实时性 和 数据一致性。

📌 Hazelcast & Redis 存储结构

<br>

Hazelcast 用于 持久化存储，Redis 用于 缓存和推送。

| 数据类型 | Hazelcast (IMap)                 | Redis (缓存 & 推送)          |
| ---- | -------------------------------- | ------------------------ |
| K线   | IMap\<Kline:{symbol}:{interval}> | ZSet\<Kline:{symbol}>    |
| 深度   | IMap\<OrderBook:{symbol}>        | ZSet\<Depth:{symbol}>    |
| 成交   | IMap\<TradeHistory:{symbol}>     | List\<Fills:{symbol}>    |
| 资金费率 | IMap\<FundingRate:{symbol}>      | Hash\<FundRate>          |
| 订单   | IMap\<Order:{userId}:{symbol}>   | Hash\<Order:{userId}>    |
| 持仓   | IMap\<Position:{userId}>         | Hash\<Position:{userId}> |
| 资产   | IMap\<Balance:{userId}>          | Hash\<Balance:{userId}>  |

📌 数据存储 & 示例代码

<br>

1\. K线数据存储

• Hazelcast：存储 长周期 K 线 (1h, 1d)

• Redis：缓存 短周期 K 线 (1m, 5m)，用于 WebSocket 推送

```java
IMap<String, List<KlineData>> klineMap = hazelcastInstance.getMap("Kline:BTC/USDT:1h");
klineMap.put("BTC/USDT", Arrays.asList(new KlineData(1700000000, "35000.50", "35200.75", "34800.25", "35150.00", "120.5")));

redisTemplate.opsForZSet().add("Kline:BTC/USDT", JSON.toJSONString(klineData), 1700000000);
```

```json
{
  "timestamp": 1700000000,
  "open": "35000.50",
  "high": "35200.75",
  "low": "34800.25",
  "close": "35150.00",
  "volume": "120.5"
}
```

2\. 深度数据存储

• Hazelcast：存储 完整订单簿

• Redis：缓存 增量深度 (increment\_depth)

```java
IMap<String, OrderBook> orderBookMap = hazelcastInstance.getMap("OrderBook:BTC/USDT");
orderBookMap.put("BTC/USDT", new OrderBook(new TreeMap<>(), new TreeMap<>()));

redisTemplate.opsForZSet().add("Depth:BTC/USDT", JSON.toJSONString(orderBook), System.currentTimeMillis());
```

```json
{
  "bids": { "35100.50": "2.5", "35099.75": "1.2" },
  "asks": { "35150.00": "3.0", "35175.20": "1.8" }
}
```

3\. 成交数据存储

• Hazelcast：存储 用户成交历史

• Redis：缓存 最近成交

```java
IMap<String, List<Trade>> tradeMap = hazelcastInstance.getMap("TradeHistory:BTC/USDT");
tradeMap.put("BTC/USDT", Arrays.asList(new Trade(1023456, "BTC/USDT", "35120.80", "0.75", 1700000500)));

redisTemplate.opsForList().leftPush("Fills:BTC/USDT", JSON.toJSONString(tradeData));
```

```json
{
  "trade_id": 1023456,
  "symbol": "BTC/USDT",
  "price": "35120.80",
  "quantity": "0.75",
  "timestamp": 1700000500
}
```

4\. 资金费率存储

• Hazelcast：存储 资金费率快照

• Redis：推送 实时资金费率

```java
IMap<String, FundingRate> fundingRateMap = hazelcastInstance.getMap("FundingRate:BTC/USDT");
fundingRateMap.put("BTC/USDT", new FundingRate("0.00075"));

redisTemplate.opsForHash().put("FundRate", "BTC/USDT", "0.00075");
```

```json
{
  "symbol": "BTC/USDT",
  "funding_rate": "0.00075"
}
```

5\. 订单数据存储

• Hazelcast：存储 所有活跃订单

• Redis：缓存 未完成订单

```java
IMap<String, Order> orderMap = hazelcastInstance.getMap("Order:123456:BTC/USDT");
orderMap.put("123456", new Order(567890, "BTC/USDT", "buy", "35100.00", "1.5", "pending"));

redisTemplate.opsForHash().put("Order:123456", "567890", JSON.toJSONString(orderData));
```

```json
{
  "order_id": 567890,
  "user_id": 123456,
  "symbol": "BTC/USDT",
  "side": "buy",
  "price": "35100.00",
  "quantity": "1.5",
  "status": "pending"
}
```

6\. 持仓数据存储

• Hazelcast：存储 用户持仓状态

• Redis：缓存 账户持仓数据

```
IMap<String, Position> positionMap = hazelcastInstance.getMap("Position:123456");
positionMap.put("123456", new Position("BTC/USDT", "long", "3.5", "35050.00", "1000.00"));

redisTemplate.opsForHash().put("Position:123456", "BTC/USDT", JSON.toJSONString(positionData));
```

```json
{
  "user_id": 123456,
  "symbol": "BTC/USDT",
  "position_side": "long",
  "quantity": "3.5",
  "entry_price": "35050.00",
  "margin": "1000.00"
}
```

7\. 资产数据存储

• Hazelcast：存储 用户资产快照

• Redis：缓存 账户余额

```java
IMap<String, Balance> balanceMap = hazelcastInstance.getMap("Balance:123456");
balanceMap.put("123456", new Balance(Map.of("USDT", "5000.00", "BTC", "0.25")));

redisTemplate.opsForHash().put("Balance:123456", "USDT", "5000.00");
redisTemplate.opsForHash().put("Balance:123456", "BTC", "0.25");
```

```json
{
  "user_id": 123456,
  "balance": { "USDT": "5000.00", "BTC": "0.25" }
}
```

📌 方案优势

1\. 🔥 高吞吐 - 订单簿 & 持仓数据直接从 Hazelcast IMap 读取，O(log N) 查找对手单，支持 百万 TPS。

2\. ⏱️ 低延迟 - Redis 缓存 + Kafka 推送，实现 <10ms 内完成 WebSocket & API 同步。

3\. 📈 数据一致性 - 订单数据 Hazelcast 持久化，撮合后通过 Kafka 事件同步 到 Redis & MySQL，保证系统稳定性。

🚀 这套 Hazelcast + Redis + Kafka 组合，能够在高并发场景下，提供稳定、高效、低延迟的交易撮合服务！

## 总结



