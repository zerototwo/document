---
cover: >-
  https://images.unsplash.com/photo-1736967439874-d0c856eacda1?crop=entropy&cs=srgb&fm=jpg&ixid=M3wxOTcwMjR8MHwxfHJhbmRvbXx8fHx8fHx8fDE3Mzk3MjQyNTJ8&ixlib=rb-4.0.3&q=85
coverY: 0
---

# Kafka 重平衡机制（Rebalance）

## 1.什么是 Kafka 的重平衡（Rebalance）

Kafka 重平衡（Rebalance） 是指 消费者组（Consumer Group）中的消费者发生变更（新增、离开、崩溃）时，Kafka 需要重新分配分区（Partition）给消费者，以保证消息的均衡消费。

### 作用：

• 维持 Consumer Group 内的 负载均衡。

• 确保 每个分区（Partition）都被某个消费者（Consumer）消费。

• 处理消费者新增 / 退出 / 崩溃 等情况。

## 2.为什么需要重平衡

Kafka 每个 Partition 只能被同一个 Consumer 组中的一个消费者消费，但在以下情况需要进行 Rebalance：

| 触发条件       | 示例                               |
| ---------- | -------------------------------- |
| 消费者崩溃 / 失联 | 一个 Consumer 进程意外宕机或网络异常          |
| 新增消费者      | 新的 Consumer 加入组，需要重新分配 Partition |
| 消费者主动退出    | 通过 Consumer.close() 退出组          |
| Topic 发生变更 | 分区（Partition）数量增加或减少             |
| Broker 故障  | Broker 宕机，Leader 重新选举            |

## 3.Kafka 重平衡的过程

### 1. 协调者（Coordinator）发现变更

• Kafka 的 Group Coordinator（协调者）监控 Consumer 组的成员变更。

• 发现 新增 / 退出 / 崩溃 事件后，触发 重平衡。

### 2. 停止消费（暂停阶段）

• 所有 Consumer 暂停消费，等待新的 Partition 分配。

### 3. Leader Consumer 选择新的分配方案

• Kafka 选出一个 Consumer Leader（消费者组的 Leader）。

• Leader 通过 分区分配策略（Partition Assignment Strategy） 重新分配 Partition。

### 4. 所有 Consumer 接受新的分配

• Consumer 组成员接受新分配的分区。

• 恢复消费，继续处理 Kafka 消息。

## 4.Kafka 重平衡的分区分配策略

Kafka 默认使用 RangeAssignor 策略，也可以更改策略：

| 策略                            | 说明                                |
| ----------------------------- | --------------------------------- |
| RangeAssignor（默认）             | 采用 范围（Range）分配，尽可能均匀地分配 Partition |
| RoundRobinAssignor            | 采用 轮询（Round Robin）分配，更适合多个 Topic  |
| StickyAssignor                | 避免频繁变更，尽量维持之前的分配策略                |
| CooperativeStickyAssignor（推荐） | 最优解，减少重平衡对消费者的影响                  |

👉 设置分区策略

```
partition.assignment.strategy=org.apache.kafka.clients.consumer.CooperativeStickyAssignor
```

## 5.Kafka 重平衡的影响

重平衡会导致：

1\. 消费短暂中断（Consumer 组内所有 Consumer 停止工作）。

2\. 数据重复消费（Consumer 可能会重新读取数据）。

3\. 性能损耗（频繁重平衡会影响 Kafka 整体吞吐量）。

## 6.如何优化 Kafka 重平衡？

### 1. 使用 CooperativeStickyAssignor

• 减少不必要的 Partition 变更，降低重平衡对 Consumer 组的影响。

```
partition.assignment.strategy=org.apache.kafka.clients.consumer.CooperativeStickyAssignor
```

### 2. 设置 session.timeout.ms & heartbeat.interval.ms

• 避免误触发 Rebalance

```
session.timeout.ms=45000   # Consumer 失联 45s 才认为超时
heartbeat.interval.ms=15000 # Consumer 每 15s 发送心跳
```

### 3. 增加 max.poll.interval.ms

• 防止 Consumer 处理慢导致退出

```
max.poll.interval.ms=300000   # Consumer 最长 5 分钟不拉取消息不会被踢出
```

### 4. 使用 Static Membership（静态成员分配）

• 避免 Consumer 退出后重新加入导致 Rebalance

```
group.instance.id=consumer-1
```

## 7.总结

| 问题             | 解决方案                                           |
| -------------- | ---------------------------------------------- |
| Kafka 发生重平衡的情况 | Consumer 崩溃、加入、退出，或者分区变化                       |
| 重平衡的影响         | 造成消费短暂中断，可能会有重复消费，影响吞吐量                        |
| 如何优化重平衡？       | 采用 StickyAssignor，优化 超时参数，使用 Static Membership |

👉 Kafka 重平衡是 必要的机制，但优化得当可以减少对消费性能的影响，提高吞吐量和稳定性 🚀
