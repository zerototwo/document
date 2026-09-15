# 一次 gRPC 超时排查：用 Arthas 和 MySQL 执行计划定位慢查询

### 一、问题现象

调用 stFuture 成交额及手续费统计接口时，客户端出现超时报错，请求参数如下：

```
startTime: 1782864000000
endTime:   1789516799999
orderSource: 0
```

客户端默认 deadline 为 **1 秒**。这次查询覆盖约 77 天，需要聚合大量成交明细。

### 二、用 Arthas 定位耗时

连接服务端 Java 进程后，执行：

```
trace com.cex.stfuture.server.service.impl.TradeDetailServiceImpl getFutureExchangeAmountAndFee* '#cost > 1000' -n 10
```

其中，`#cost > 1000` 表示只输出超过 1000ms 的调用，`-n 10` 表示捕获 10 次后结束。

| 执行步骤      | 耗时        | 占比     |
| --------- | --------- | ------ |
| 统计方法总耗时   | 1505.40ms | 100%   |
| Mapper 查询 | 1461.33ms | 97.07% |
| 合约乘数处理    | 41.24ms   | 2.74%  |

瓶颈集中在 Mapper 阶段，且总耗时已超过客户端的 1 秒 deadline。Mapper 耗时还包含连接获取、结果映射等开销，需要继续检查数据库。

### 三、还原 SQL，用 EXPLAIN 查看估算计划

普通版统计查询只访问 `bos_trade_detail`，不使用 `orderSource` 过滤：

```
EXPLAIN
SELECT
    SUM(token_fee) AS fee,       -- 汇总手续费
    symbol_id AS symbolId,      -- 按币对统计
    SUM(amount) AS amount       -- 汇总成交额
FROM bos_trade_detail
WHERE is_market = 0             -- 普通用户成交
  AND match_time BETWEEN        -- BETWEEN 包含两个边界
      FROM_UNIXTIME(1782864000000 / 1000)
      AND FROM_UNIXTIME(1789516799999 / 1000)
GROUP BY symbol_id;
-- FROM_UNIXTIME 使用数据库会话时区，复现时应与应用保持一致
```

两次普通 `EXPLAIN` 的关键字段：

| 字段         | 不带索引提示        | 强制联合索引                                   |
| ---------- | ------------- | ---------------------------------------- |
| `type`     | `index`       | `range`                                  |
| `key`      | `idx_symbol`  | `idx_market_match_time`                  |
| `key_len`  | 1022          | 8                                        |
| `rows`     | 384,730       | 183,048                                  |
| `filtered` | 5.56          | 100                                      |
| `Extra`    | `Using where` | `Using index condition; Using temporary` |

**字段解读：**

* `possible_keys`：优化器认为可能用于定位数据的索引，不代表最终使用。
* `key`：最终选择的索引。
* `type=index`：全索引扫描，并不是“用了索引就很快”；`range` 表示范围扫描。
* `key_len`：参与访问的索引键最大长度，单位为字节，不是索引列数。
* `rows`：估算扫描行数；`filtered`：估算经过表条件过滤后保留的百分比。
* `Using where`：需要应用过滤条件。
* `Using index condition`：使用索引条件下推，不等于覆盖索引，仍可能回表。
* `Using temporary`：需要临时表处理分组等操作，不代表一定落盘。

表中已有 `(is_market, match_time)` 联合索引，但默认计划没有选择它。仅凭估算无法判断哪个更快，需要实际执行。

### 四、用 EXPLAIN ANALYZE 验证真实耗时

MySQL 8.0.18+ 支持 `EXPLAIN ANALYZE`。将上述 SQL 的 `EXPLAIN` 替换为它即可；**它会真正执行查询**。

执行树从下往上读。下面的注释用于解释输出，不是原始执行计划的一部分。

#### 默认计划

```
-> Table scan on <temporary>
   (actual time=1564..1564 rows=18 loops=1)
   # 读取聚合结果：18 行，总耗时约 1564ms
    -> Aggregate using temporary table
       (actual time=1564..1564 rows=18 loops=1)
       # 将匹配明细按 symbol_id 聚合
        -> Filter: match_time between ...
           (cost=33315 rows=21372)
           (actual time=1388..1517 rows=93829 loops=1)
           # 估算保留 21372 行，实际保留 93829 行
           # 约 1388ms 才输出第一条符合时间条件的记录
            -> Index lookup using idx_is_market (is_market=0)
               (cost=33315 rows=192365)
               (actual time=1.75..1486 rows=449788 loops=1)
               # 通过单列索引读取所有 is_market=0 的记录
               # 实际读取 449788 行，再交给上层过滤时间
```

这次实际计划选择了 `idx_is_market`，与之前普通 `EXPLAIN` 的 `idx_symbol` 不同。因此应分别解读各次计划，不能混为同一次执行。

#### 强制联合索引后的计划

SQL 仅修改表引用：

```
FROM bos_trade_detail FORCE INDEX (idx_market_match_time)
-- 引导优化器使用 (is_market, match_time) 联合索引
```

```
-> Table scan on <temporary>
   (actual time=302..302 rows=18 loops=1)
   # 最终输出仍为 18 行，总耗时约 302ms
    -> Aggregate using temporary table
       (actual time=302..302 rows=18 loops=1)
        -> Index range scan using idx_market_match_time
           over (is_market = 0 AND match_time between ...)
           (cost=219588 rows=183048)
           (actual time=1.99..252 rows=93829 loops=1)
           # 同时利用用户类型等值条件和时间范围条件
           # 实际读取 93829 行，约 252ms 完成该节点
```

`actual time=a..b` 表示该节点返回第一行、完成执行的耗时，单位为毫秒；`rows` 是实际输出行数，`loops` 是执行次数。多次循环时，时间和行数通常按每次循环平均值展示。

**父节点时间包含子节点执行开销，不能相加。** 这里总耗时是约 302ms，不是 `252 + 302`。`cost` 则是模型估算成本，不是毫秒。

### 五、结果与调整

| 指标     | 默认实际计划  | 强制联合索引 |
| ------ | ------- | ------ |
| 读取行数   | 449,788 | 93,829 |
| 最终匹配行数 | 93,829  | 93,829 |
| 总耗时    | 1564ms  | 302ms  |

这组测量中，联合索引少读取约 **35.6 万行**，耗时降低约 **80.7%**，约快 **5.2 倍**。

估算行数与实际行数偏差明显，可以先用 `ANALYZE TABLE bos_trade_detail` 更新统计信息再复查；本案例没有提供这一步的结果，不能断言统计信息过期。

最终为普通版统计 SQL 添加了 `FORCE INDEX`，同时提供客户端超时重载。实测收益来自 stFuture 的这段时间范围；future 和其他时间范围仍需验证。部署库必须存在该索引，且应通过重复测量排除缓存和负载差异。
