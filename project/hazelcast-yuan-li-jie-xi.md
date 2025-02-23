---
cover: >-
  https://images.unsplash.com/photo-1737995720044-8d9bd388ff4f?crop=entropy&cs=srgb&fm=jpg&ixid=M3wxOTcwMjR8MHwxfHJhbmRvbXx8fHx8fHx8fDE3NDAzMjczOTd8&ixlib=rb-4.0.3&q=85
coverY: 0
---

# Hazelcast 原理解析

Hazelcast 是一个 分布式内存数据存储 & 计算框架，主要用于 高并发、高吞吐的实时数据存储，在交易撮合、缓存、任务调度等场景中广泛应用。Hazelcast 采用 内存分布式存储 + 事件驱动计算 + 数据持久化，提供 高可用、低延迟、高吞吐 的分布式数据存储解决方案。

## 1.Hazelcast 核心架构

Hazelcast 采用 分布式内存集群 设计，所有数据 分片存储 在多个节点上，每个节点既是 数据存储节点，也是 计算节点，避免集中式存储的瓶颈。

🌍 Hazelcast 集群架构

```
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│ Hazelcast Node 1 │    │ Hazelcast Node 2 │    │ Hazelcast Node 3 │
├──────────────────┤    ├──────────────────┤    ├──────────────────┤
│ 数据分片: A, B   │    │ 数据分片: C, D   │    │ 数据分片: E, F   │
│ 计算任务         │    │ 计算任务         │    │ 计算任务         │
│ 事件监听         │    │ 事件监听         │    │ 事件监听         │
└──────────────────┘    └──────────────────┘    └──────────────────┘
```

🔥 所有 Hazelcast 节点地位相同，无主从关系，任何节点故障都不会影响集群运行。

## 2.Hazelcast 数据存储

Hazelcast 主要采用 IMap（分布式哈希表） 存储数据，支持 自动分片 & 备份，保证数据的 高可用性 & 低延迟。

🛠 数据存储方式

• IMap（类似 Redis HashMap）：存储 Key-Value 结构数据（订单、账户信息）。

• MultiMap（一对多映射）：存储用户的多个订单、持仓信息。

• IQueue（消息队列）：用于撮合任务队列，类似 Kafka。

• ReplicatedMap（全局复制）：数据副本存在所有节点，适用于全局配置。

✅ 订单存储示例

```
// 获取 Hazelcast 实例
HazelcastInstance hazelcastInstance = Hazelcast.newHazelcastInstance();

// 获取订单 IMap（分布式存储）
IMap<Long, Order> ordersMap = hazelcastInstance.getMap("orders");

// 存储订单
ordersMap.put(12345L, new Order(12345L, "BTC/USDT", "BUY", 1000.0, 100.0));

// 获取订单
Order order = ordersMap.get(12345L);
System.out.println("订单信息：" + order);
```

🔥 订单存储在 Hazelcast IMap，分布式存储，支持并发读写。

## 3.数据分片（Partitioning）

Hazelcast 采用 一致性哈希算法 进行数据分片（Partitioning），将 Key 均匀分布到多个节点上，确保数据均衡存储 & 负载均衡。

📌 分片规则

• 数据 Key 计算哈希值

• 哈希值对分片数取模

• 将 Key 存储到相应分片

• 分片分布在不同 Hazelcast 节点

✅ 示例

```
Key = 订单ID 12345 → Hash(12345) = 6789 → Partition 10 → 存入 Node 2
Key = 订单ID 67890 → Hash(67890) = 4321 → Partition 5 → 存入 Node 1
```

🔥 这样数据均匀分布，避免某个节点过载，提高集群吞吐量。

## 4.高可用 & 备份机制

Hazelcast 采用 数据复制机制（Backup），避免节点故障导致数据丢失。

🛠 备份策略

• 同步备份：数据主副本 & 备份副本始终一致，确保数据安全。

• 异步备份：减少主存储节点压力，提高吞吐量。

• 持久化存储：结合 Native Persistence，数据可持久化到磁盘，防止丢失。

✅ 开启数据备份

```
<hazelcast>
    <map name="orders">
        <backup-count>1</backup-count>  <!-- 1 级备份 -->
        <async-backup-count>1</async-backup-count>  <!-- 异步备份 -->
    </map>
</hazelcast>
```

🔥 即使某个节点崩溃，订单数据也能从备份恢复，确保交易不中断。

## 5.事务支持（Atomicity）

Hazelcast 支持 ACID 事务，防止 数据丢失 & 并发冲突，确保交易数据一致性。

✅ 示例：撮合事务

```
TransactionContext txContext = hazelcastInstance.newTransactionContext();
txContext.beginTransaction();

try {
    IMap<Long, Order> orders = txContext.getMap("orders");
    Order order = orders.get(12345L);
    order.setStatus("FILLED");
    orders.put(order.getId(), order);
    
    txContext.commitTransaction();
} catch (Exception e) {
    txContext.rollbackTransaction();
}
```

🔥 事务确保撮合引擎不会产生 “部分成交” 或 “订单丢失” 等问题。

## 6.事件驱动（Listener & Pub/Sub）

Hazelcast 支持事件监听，当数据更新时，可以 自动触发事件，适用于 实时推送 & 自动风控。

✅ 示例：监听订单变更

```
ordersMap.addEntryListener(new EntryUpdatedListener<Long, Order>() {
    @Override
    public void entryUpdated(EntryEvent<Long, Order> event) {
        System.out.println("订单更新：" + event.getValue());
    }
}, true);
```

🔥 这样当订单撮合完成时，系统能自动推送更新给 WebSocket 进行通知。

## 7.持久化（Persistence）

Hazelcast 支持本地存储（Native Persistence），即使系统崩溃，也能恢复数据，避免订单丢失。

✅ 示例：开启持久化

```
<hazelcast>
    <persistence enabled="true">
        <base-dir>/data/hazelcast</base-dir>
        <backup-dir>/backup/hazelcast</backup-dir>
    </persistence>
</hazelcast>
```

🔥 这样 Hazelcast 能持久化存储订单数据，重启后自动恢复，不影响撮合。

## 8.Hazelcast + Redis + Kafka 组合

Hazelcast 主要用于 订单存储 & 撮合，而 Redis & Kafka 负责 推送 & 交易日志，三者结合构建 高性能交易架构。

✅ 架构设计

```
+-------------+      +------------------+
| 撮合引擎     | ---> | Hazelcast (订单存储) |
+-------------+      +------------------+
         |                      |
         v                      v
+-------------------+    +----------------+
| Redis (行情推送)  |    | Kafka (事件流)  |
+-------------------+    +----------------+
```

🔥 Hazelcast 负责存储订单，Redis 负责行情推送，Kafka 负责异步数据流，保证撮合性能 & 数据一致性。

## 总结：为什么 Hazelcast 适用于撮合系统？

| Hazelcast 优势 | 理由               |
| ------------ | ---------------- |
| ⚡ 超低延迟       | 内存存储，订单查询 <1ms   |
| 🔄 分布式存储     | 数据分片，集群水平扩展      |
| 🔐 事务 & 并发控制 | 防止订单丢失，确保一致性     |
| 🔥 事件驱动      | 订单变更可实时推送 & 风控联动 |
| 💾 持久化支持     | 崩溃后可秒级恢复订单数据     |

Hazelcast 结合 Redis & Kafka，可实现 高并发、低延迟、安全可靠 的交易撮合系统，满足百万级 TPS 需求。&#x20;
