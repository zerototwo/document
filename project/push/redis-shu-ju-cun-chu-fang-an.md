# Redis 数据存储方案

在交易系统中，不同数据类型 具有不同的查询、更新和推送需求，因此 合理选择 Redis 数据结构，可以提升查询效率、减少存储开销、确保数据推送的实时性。以下是完整的数据存储方案及选择理由：

## 1.K线数据（ZSET - Sorted Set）

📌 理由：

• 时间序列数据，适合按时间戳排序，可快速获取最近 N 根 K 线。

• 支持高效插入 & 查询 (ZADD 添加、ZRANGE 取最近记录)。

• 适用于 按时间筛选，避免 LIST 结构遍历查询的开销。\


✅ 示例存储

```
ZADD market:kline:BTCUSDT:1m 1700000000 '{"open": 9500, "high": 9600, "low": 9450, "close": 9550, "volume": 100}'
```

## 2.盘口深度（ZSET - Sorted Set）

📌 理由：

• 盘口数据按 买卖价格排序，可以高效查找最优买/卖单。

• 撮合时可直接 增量更新 (ZINCRBY 修改订单量，ZREM 移除成交订单)。

• 低延迟撮合 & 推送，保证交易深度的实时性。

✅ 示例存储

```
ZADD market:depth:BTCUSDT:bids 9590 '{"price": 9590, "amount": 5}'
ZADD market:depth:BTCUSDT:asks 9600 '{"price": 9600, "amount": 3}
```

## 3.成交数据（LIST - Linked List）

📌 理由：

• FIFO 结构，适合存储最近成交记录，确保交易信息的实时性。

• LPUSH 插入，LTRIM 限制数据量，确保仅存最近 1000 条数据，节省内存。

✅ 示例存储

```
LPUSH market:trades:BTCUSDT '{"price": 9580, "amount": 1.2, "time": 1700000000}'
LTRIM market:trades:BTCUSDT 0 999  # 仅保留最近 1000 条成交记录
```

## 4.合约信息（HASH - Key-Value Mapping）

📌 理由：

• 合约参数是静态数据，适合 HASH 存储，支持字段级查询 (HGET)。

• 避免 JSON 解析开销，每个字段可单独更新 (HSET 只更新杠杆字段，不影响其他字段)。

\


✅ 示例存储

```
HSET contract:BTCUSDT leverage 125
HSET contract:BTCUSDT min_order_size 0.001
```

## 5.用户订单（HASH - Key-Value Mapping）

📌 理由：

• 订单详情需要 频繁更新（open → filled → canceled），适合 HASH 结构化存储。

• 避免 JSON 解析，查询 & 更新效率更高 (HSET 更新状态字段)。

\


✅ 示例存储

```
HSET user:orders:1001 order_id 789123 status "open"
HSET user:orders:1001 filled_amount 0.5
```

## 6.用户持仓（HASH - Key-Value Mapping）

\


📌 理由：

• 持仓数据是 用户的快照数据，支持字段级更新，适用于 HASH 存储。

• 例如 持仓盈亏、保证金等频繁更新，无需解析整个 JSON。

\


✅ 示例存储

```
HSET user:position:1001 unrealized_pnl 100.5
HSET user:position:1001 leverage 50
```

## 7.用户资产（HASH - Key-Value Mapping）

📌 理由：

• 账户余额 需要频繁更新（入金、交易、提现等），适合 HASH。

• 支持字段级查询 & 更新，避免 JSON 解析，提高查询效率。

✅ 示例存储

```
HSET user:balance:1001 available 1000.5
HSET user:balance:1001 frozen 50
```

## 整体存储方案总结

| 数据类型 | 选用 Redis 结构 | 选择理由              |
| ---- | ----------- | ----------------- |
| K线数据 | ZSET        | 时间序列数据，按时间排序      |
| 盘口深度 | ZSET        | 按价格排序，方便撮合        |
| 成交数据 | LIST        | 追加 & 查询最近 N 条     |
| 合约信息 | HASH        | 结构化存储，支持字段级更新     |
| 用户订单 | HASH        | 订单详情，支持状态更新       |
| 用户持仓 | HASH        | 结构化数据，高效查询 & 更新   |
| 用户资产 | HASH        | 账户余额快照，减少 JSON 解析 |

这套存储方案在 存储效率、查询速度、推送性能 之间达到了最佳平衡，确保交易系统高效运行 🚀
