# 下单币对一个topic还是多个

下单消息我一般不建议“一个币对一个 Topic”，更推荐 全部币对放在一个订单 Topic 里，然后按币对 symbol 作为 key 分区。

也就是：

```
Topic：order-topic
Key：symbol，例如 BTC-USDT、ETH-USDT
Value：订单消息
```

这样 Kafka 会根据 symbol hash 到固定 Partition，同一个币对的订单、撤单、改单都会进入同一个 Partition，从而保证单币对内消息有序。

***

核心原因有几个。

第一，撮合最重要的是同一个币对的顺序性。

对撮合系统来说，同一个币对的下单、撤单、改单必须按顺序处理。

如果同一个币对的消息进入不同 Partition，就可能出现乱序，比如撤单先被消费，下单后被消费，导致订单状态异常。

所以一般会用 symbol 作为 Kafka message key，让同一个币对固定落到同一个 Partition。

例如：

```
order-topic
  partition-0：BTC-USDT
  partition-1：ETH-USDT
  partition-2：SOL-USDT
```

这样每个 Partition 内 Kafka 天然保证顺序。

***

第二，一个币对一个 Topic 会导致 Topic 数量爆炸。

交易所币对可能有几百甚至上千个，如果一个币对一个 Topic，就会产生大量 Topic 和 Partition。

这会增加 Kafka Controller、Broker metadata、文件句柄、内存和运维压力。后续扩容、监控、权限管理、消费组管理都会变复杂。

比如：

```
btc-usdt-order-topic
eth-usdt-order-topic
sol-usdt-order-topic
...
```

币对越多，维护成本越高。

***

第三，一个 Topic 更方便统一消费和扩容。

全部币对放在一个 order-topic 里，可以统一生产、统一消费、统一监控。

消费端可以按 Partition 分配给不同撮合 Worker。只要保证同一个币对固定在一个 Partition，就可以做到单币对有序、多币对并行。

架构上类似：

```
订单服务
  -> order-topic
      -> partition-0 -> matcher-worker-1
      -> partition-1 -> matcher-worker-2
      -> partition-2 -> matcher-worker-3
```

这样整体吞吐可以通过增加 Partition 和 Consumer 扩展。

***

第四，热点币对可以特殊处理。

如果某些币对流量特别大，比如 BTC-USDT、ETH-USDT，一个 Partition 扛不住，这时候可以把热点币对单独拆 Topic，或者单独拆撮合链路。

也就是说，普通币对走统一 Topic，热点币对独立 Topic 或独立集群隔离。

实际可以这样设计：

```
普通币对：
order-topic，按 symbol 分区

热点币对：
btc-usdt-order-topic
eth-usdt-order-topic
```

这样既避免 Topic 数量过多，又能对热点交易对单独扩容和隔离风险。

***

面试标准回答：

我更倾向于全部币对放在一个订单 Topic 里，然后用币对 symbol 作为 message key，让同一个币对的消息固定进入同一个 Partition。

这样可以保证单币对内的下单、撤单、改单消息有序，同时多币对可以分布到不同 Partition 并行消费，提升整体吞吐。

如果一个币对一个 Topic，币对数量多时会导致 Topic 和 Partition 数量膨胀，增加 Kafka metadata、Broker、Controller 和运维压力。

但是对于 BTC-USDT、ETH-USDT 这种极热点币对，如果单个 Partition 吞吐不够，可以考虑单独拆 Topic 或单独部署撮合链路，做独立扩容和风险隔离。

所以我的选择是：默认一个 order-topic + symbol 分区；热点币对再单独拆 Topic。
