# Hazelcast 数据存储方案

Hazelcast 主要用于存储 实时撮合相关数据，作为高性能分布式内存存储，适合 高并发读写、高可用的撮合业务。以下是 Hazelcast 在交易系统中的具体存储结构及数据类型：

📌 Hazelcast 适用场景

| 数据类型                  | Hazelcast 结构                               | 选择理由             |
| --------------------- | ------------------------------------------ | ---------------- |
| 订单簿 (Order Book)      | IMap\<String, TreeMap\<BigDecimal, Order>> | 快速查询盘口深度，支持高并发撮合 |
| 用户订单 (User Orders)    | IMap\<Long, Order>                         | 支持订单状态变更，低延迟     |
| 撮合队列 (Matching Queue) | IQueue\<ShortOrderDTO>                     | 撮合引擎高吞吐处理        |
| 用户持仓 (User Positions) | IMap\<Long, Position>                      | 支持高频查询 & 更新      |
| 用户账户 (User Balance)   | IMap\<Long, AccountBalance>                | 保证金计算 & 账户冻结查询   |
| 市场数据 (Market Data)    | IMap\<String, MarketData>                  | K 线、深度、资金费率等数据共享 |

1️⃣ 订单簿（Order Book）

\


📌 理由

• 核心撮合数据，要求 O(logN) 查找对手单

• 基于 TreeMap 存储买卖盘口，高效撮合 & 插入订单。

• 存储方式

• bids (买单按价格降序)

• asks (卖单按价格升序)

\


✅ Hazelcast 结构

```
IMap<String, TreeMap<BigDecimal, Order>> orderBook = hazelcastInstance.getMap("orderBook");
```

✅ 存储示例

```
orderBook.get("BTCUSDT").put(new BigDecimal("9590"), new Order(123, 0.5, "BUY"));
orderBook.get("BTCUSDT").put(new BigDecimal("9600"), new Order(124, 1.0, "SELL"));
```

2️⃣ 用户订单（User Orders）

\


📌 理由

• 需要支持订单状态变更（open → filled → canceled）

• Hazelcast 支持分布式事务，保证撮合后订单状态一致。

\


✅ Hazelcast 结构

```
IMap<Long, Order> userOrders = hazelcastInstance.getMap("userOrders");
```

✅ 存储示例

```
userOrders.put(1001L, new Order(1001, 0.5, "BUY", "OPEN"));
```

✅ 更新订单状态

```
Order order = userOrders.get(1001L);
order.setStatus("FILLED");
userOrders.put(1001L, order);
```

3️⃣ 撮合队列（Matching Queue）

\


📌 理由

• 撮合引擎需要高吞吐处理订单队列，适合 IQueue

• FIFO 结构，保证订单按时间顺序处理

\


✅ Hazelcast 结构

```
IQueue<ShortOrderDTO> matchingQueue = hazelcastInstance.getQueue("matchingQueue");
```

✅ 存储示例

```
matchingQueue.offer(new ShortOrderDTO(1002, "BTCUSDT", "BUY", new BigDecimal("9580"), new BigDecimal("0.5")));
```

✅ 撮合引擎消费订单

```
ShortOrderDTO order = matchingQueue.poll();
```

4️⃣ 用户持仓（User Positions）

\


📌 理由

• 持仓数据需要实时更新，适合 IMap

• 高频查询保证金、盈亏、杠杆信息

\


✅ Hazelcast 结构

```
IMap<Long, Position> userPositions = hazelcastInstance.getMap("userPositions");
```

✅ 存储示例

```
userPositions.put(1001L, new Position(1001L, "BTCUSDT", new BigDecimal("2.5"), new BigDecimal("50"), "LONG"));
```

✅ 更新用户持仓

```
Position position = userPositions.get(1001L);
position.setUnrealizedPnl(new BigDecimal("100"));
userPositions.put(1001L, position);
```

5️⃣ 用户账户（User Balance）

\


📌 理由

• 需要频繁查询可用余额 & 冻结金额

• Hazelcast 支持分布式锁，保证高并发一致性。

\


✅ Hazelcast 结构

```
IMap<Long, AccountBalance> userBalances = hazelcastInstance.getMap("userBalances");
```

✅ 存储示例

```
userBalances.put(1001L, new AccountBalance(1001L, new BigDecimal("1000.0"), new BigDecimal("50.0")));
```

✅ 更新余额

```
AccountBalance balance = userBalances.get(1001L);
balance.setAvailable(balance.getAvailable().subtract(new BigDecimal("100")));
userBalances.put(1001L, balance);
```

6️⃣ 市场数据（Market Data）

\


📌 理由

• 市场数据需要全局共享，适合 IMap

• K线、盘口深度、成交数据存储

\


✅ Hazelcast 结构

```
IMap<String, MarketData> marketData = hazelcastInstance.getMap("marketData");
```

✅ 存储示例

```
MarketData btcData = new MarketData("BTCUSDT", new BigDecimal("9580"), new BigDecimal("100"));
marketData.put("BTCUSDT", btcData);
```

✅ 更新市场数据

```
MarketData data = marketData.get("BTCUSDT");
data.setLastPrice(new BigDecimal("9590"));
marketData.put("BTCUSDT", data);
```

📌 Hazelcast 存储结构总结

| 数据类型 | 选用 Hazelcast 结构                            | 选择理由           |
| ---- | ------------------------------------------ | -------------- |
| 订单簿  | IMap\<String, TreeMap\<BigDecimal, Order>> | 快速查找最优买卖单      |
| 用户订单 | IMap\<Long, Order>                         | 订单状态变更，支持高并发   |
| 撮合队列 | IQueue\<ShortOrderDTO>                     | FIFO 结构，保证撮合顺序 |
| 用户持仓 | IMap\<Long, Position>                      | 实时计算盈亏、保证金     |
| 用户账户 | IMap\<Long, AccountBalance>                | 高并发查询账户余额      |
| 市场数据 | IMap\<String, MarketData>                  | 共享市场行情，确保数据一致性 |

Hazelcast 主要负责高性能内存存储，与 Redis 一起形成低延迟、高并发的存储体系。🚀
