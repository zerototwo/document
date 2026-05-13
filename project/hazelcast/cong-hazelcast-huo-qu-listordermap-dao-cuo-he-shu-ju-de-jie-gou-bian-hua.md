# 从 Hazelcast 获取 List\<OrderMap> 到撮合数据的结构变化

## 1.订单数据结构



订单 (OrderMap) 存储订单的基本信息，包括买卖方向、价格、数量、时间戳等。

```java
public class OrderMap {
    private Long orderId;         // 订单 ID
    private BigDecimal price;     // 订单价格
    private BigDecimal amount;    // 订单数量
    private String side;          // 订单方向（BUY / SELL）
    private Long timestamp;       // 订单创建时间（用于时间优先）
}
```

📌 JSON 示例

```json
{
    "orderId": 1,
    "price": 100.5,
    "amount": 10,
    "side": "BUY",
    "timestamp": 1700000002
}
```

## 2.订单簿数据结构 (depthMap)

订单簿 (depthMap) 用于存储买卖订单，按照 价格优先 + 时间优先（FIFO） 排序。

• 第一层 TreeMap\<BigDecimal, TreeMap\<Long, OrderMap>>

• TreeMap 自动按照价格排序（价格优先）。

• 第二层 TreeMap\<Long, OrderMap>

• TreeMap 自动按照时间戳排序（FIFO 时间优先）。

```java
// 订单簿存储结构
Map<BigDecimal, TreeMap<Long, OrderMap>> depthMap = new TreeMap<>();
```

📌 JSON 示例

```json
{
    "99.8": {
        "1700000000": {
            "orderId": 4,
            "price": 99.8,
            "amount": 15,
            "side": "BUY",
            "timestamp": 1700000000
        }
    },
    "100.5": {
        "1700000002": {
            "orderId": 1,
            "price": 100.5,
            "amount": 10,
            "side": "BUY",
            "timestamp": 1700000002
        },
        "1700000003": {
            "orderId": 2,
            "price": 100.5,
            "amount": 5,
            "side": "BUY",
            "timestamp": 1700000003
        }
    },
    "101.0": {
        "1700000001": {
            "orderId": 3,
            "price": 101.0,
            "amount": 7,
            "side": "SELL",
            "timestamp": 1700000001
        }
    }
}
```

## 3.订单撮合逻辑

撮合时：

• 卖单（side=SELL）：寻找 最高买单（price 最大的 BUY 订单） 进行撮合。

• 买单（side=BUY）：寻找 最低卖单（price 最小的 SELL 订单） 进行撮合。

```java
public List<TradeLog> matchOrders(Map<BigDecimal, TreeMap<Long, OrderMap>> depthMap) {
    List<TradeLog> tradeLogs = new ArrayList<>();

    while (!depthMap.isEmpty()) {
        // 获取最低卖单和最高买单
        Map.Entry<BigDecimal, TreeMap<Long, OrderMap>> lowestSellEntry = depthMap.firstEntry();
        Map.Entry<BigDecimal, TreeMap<Long, OrderMap>> highestBuyEntry = depthMap.lastEntry();

        if (lowestSellEntry.getKey().compareTo(highestBuyEntry.getKey()) > 0) {
            break; // 没有匹配订单
        }

        // 获取 FIFO 订单
        OrderMap buyOrder = highestBuyEntry.getValue().firstEntry().getValue();
        OrderMap sellOrder = lowestSellEntry.getValue().firstEntry().getValue();

        // 计算成交量
        BigDecimal tradeAmount = buyOrder.getAmount().min(sellOrder.getAmount());

        // 生成交易记录
        TradeLog trade = new TradeLog(buyOrder.getOrderId(), sellOrder.getOrderId(), 
                                      lowestSellEntry.getKey(), tradeAmount, System.currentTimeMillis());
        tradeLogs.add(trade);

        // 更新订单剩余数量
        buyOrder.setAmount(buyOrder.getAmount().subtract(tradeAmount));
        sellOrder.setAmount(sellOrder.getAmount().subtract(tradeAmount));

        // 移除已完全成交的订单
        if (buyOrder.getAmount().compareTo(BigDecimal.ZERO) == 0) {
            highestBuyEntry.getValue().remove(buyOrder.getOrderId());
            if (highestBuyEntry.getValue().isEmpty()) depthMap.remove(highestBuyEntry.getKey());
        }
        if (sellOrder.getAmount().compareTo(BigDecimal.ZERO) == 0) {
            lowestSellEntry.getValue().remove(sellOrder.getOrderId());
            if (lowestSellEntry.getValue().isEmpty()) depthMap.remove(lowestSellEntry.getKey());
        }
    }
    return tradeLogs;
}
```

4️⃣ 交易记录（TradeLog）

<br>

撮合成功后，订单转换为 TradeLog 结构，存入数据库。

```json
public class TradeLog {
    private Long tradeId;
    private Long buyOrderId;
    private Long sellOrderId;
    private BigDecimal price;
    private BigDecimal amount;
    private Long timestamp;
}
```

📌 JSON 示例

```json
{
    "tradeId": 10001,
    "buyOrderId": 1,
    "sellOrderId": 3,
    "price": 100.5,
    "amount": 7,
    "timestamp": 1700000005
}
```

## 5.结构变化总结

| 阶段             | 存储结构                                           | 示例 JSON                                                                  |
| -------------- | ---------------------------------------------- | ------------------------------------------------------------------------ |
| Hazelcast 获取订单 | List\<OrderMap>                                | \[ {orderId:1, price:100.5, amount:10, side:"BUY"} ]                     |
| 转换为本地订单簿       | TreeMap\<BigDecimal, TreeMap\<Long, OrderMap>> | {100.5: {1700000002 -> order1, 1700000003 -> order2\}}                   |
| 撮合匹配           | 价格优先 + 时间优先（FIFO）                              | {100.5: {1700000002 -> order1\}} vs {101.0: {1700000001 -> order3\}}     |
| 撮合后存入数据库       | TradeLog 交易记录                                  | {tradeId: 10001, buyOrderId: 1, sellOrderId: 3, price: 100.5, amount: 7} |

## 6.设计优化点

<br>

✅ 数据结构保证价格优先 + 时间优先

• TreeMap 价格排序，优先匹配最优价格的订单。

• TreeMap\<Long, OrderMap> 时间排序，保证 FIFO 撮合。

<br>

✅ 撮合算法高效

• 遍历 depthMap 只需 O(1) 获取最优订单

• O(log N) 复杂度，适合高频撮合

<br>

✅ 交易记录持久化

• 撮合成功后，写入 TradeLog，保证数据一致性

• 数据库存储 TradeLog，用于后续对账

📌 7️⃣ 结论

• 从 Hazelcast 获取订单（List\<OrderMap>）

• 转换为 depthMap（TreeMap）

• 撮合匹配（价格优先 + 时间优先）

• 存入 TradeLog（交易记录）

<br>

🚀 这种设计可高效支持交易撮合，实现高频交易撮合系统！ 🎯
