---
description: >-
  CAP
  定理指出，在分布式系统中，一致性（C）、可用性（A）、分区容忍性（P）三者不能同时满足，只能取其二。这是由计算机网络的物理限制和分布式系统的特性决定的。
---

# CAP 理论与 BASE 模型

## 1. CAP 三个核心特性

| 特性                            | 定义                       | 解释                             |
| ----------------------------- | ------------------------ | ------------------------------ |
| 一致性（Consistency, C）           | 所有节点对外提供的数据必须是最新的、完全一致的。 | 任何节点返回的数据必须是最新的，即写入后所有副本都立即同步。 |
| 可用性（Availability, A）          | 任何请求都必须获得一个非错误的响应。       | 即使部分节点故障，系统仍能响应请求。             |
| 分区容忍性（Partition Tolerance, P） | 系统能在部分节点通信失败的情况下继续运行。    | 即使网络分区（机器间无法通信），系统仍需保证基本可用。    |

## 2. 为什么 CAP 不能三者兼得？

由于分布式系统一定会遇到网络分区（P），CAP 变成了 C 和 A 的取舍！

在分布式环境中，机器之间的通信一定存在延迟、故障、丢包等问题，导致：

1. 某些节点可能无法同步数据（违反 C）。
2. 部分节点可能无法响应请求（违反 A）。

当网络发生分区时（P），你必须在一致性（C）和可用性（A）之间做选择：

* 选择 C（强一致性）→ 牺牲 A（可用性） → 允许部分请求失败，确保所有副本数据一致。
* 选择 A（高可用）→ 牺牲 C（一致性） → 允许返回旧数据或稍后同步，以保证服务可用。

## 3. CAP 取舍示例（为什么只能三选二）

### 1.CP（强一致性 + 分区容忍） → 牺牲可用性

| 特性         | 保证                 | 缺点                 |
| ---------- | ------------------ | ------------------ |
| ✅ 一致性（C）   | 任何读请求都返回最新数据。      | 部分节点可能无法提供服务（不可用）。 |
| ❌ 可用性（A）   | 网络故障时，一部分请求被拒绝或超时。 |                    |
| ✅ 分区容忍性（P） | 允许网络分区时数据保持一致。     |                    |

#### 示例：

* Zookeeper（一致性高于可用性）
* HBase（事务数据库，必须等待数据同步完成）

⚠️ 问题：当网络分区发生，部分节点不能提供服务，牺牲可用性。

### 2.AP（高可用 + 分区容忍） → 牺牲一致性

| 特性         | 保证             | 缺点            |
| ---------- | -------------- | ------------- |
| ❌ 一致性（C）   | 允许短暂的数据不一致。    | 可能返回旧数据或数据冲突。 |
| ✅ 可用性（A）   | 任何时候都能返回响应。    |               |
| ✅ 分区容忍性（P） | 允许网络分区仍然能继续运行。 |               |

示例：

* DynamoDB、Cassandra（NoSQL 数据库，最终一致性）
* 缓存系统（如 Redis 读写分离）

问题：不同节点可能返回不同版本的数据，数据最终收敛一致（最终一致性）。

### 3.CA（强一致性 + 高可用） → 牺牲分区容忍

| 特性         | 保证                   | 缺点               |
| ---------- | -------------------- | ---------------- |
| ✅ 一致性（C）   | 所有请求返回最新数据。          | 发生网络分区时，部分节点不可用。 |
| ✅ 可用性（A）   | 系统始终能提供服务。           |                  |
| ❌ 分区容忍性（P） | 无法处理网络分区，要求所有节点通信正常。 |                  |

📌 示例：

• MySQL 单机模式

• 传统单机数据库\


⚠️ 问题：一旦发生网络分区，系统会直接不可用，不适用于分布式系统。

## 4. 为什么 P（分区容忍）是必选的？

在现实世界的分布式系统中：

* 机器之间的网络通信不可能 100% 可靠（机房故障、跨地域集群等）。
* 任何分布式架构都会遇到网络分区（如节点掉线、数据同步失败）。
* 因此，P （分区容忍）是必选项，只能在 C（一致性） 和 A（可用性） 之间做权衡。

## &#x20;5. CAP 定理的工程实践

### 1. 选择 CAP 方案

* 强一致性（CP） → 适用于 银行转账、支付、库存管理。
* 高可用（AP） → 适用于 社交网络、消息队列、缓存。
* 单机数据库（CA） → 适用于 传统企业系统。

### 2. BASE 模型：牺牲一致性，换取高可用

由于 CAP 限制，许多高并发分布式系统选择 BASE（Basically Available, Soft state, Eventually Consistent） 作为折中方案：

BASE 适用于高并发系统，如电商、社交网络、微服务架构等。

## 6. 现实世界中的 CAP 应用

| 方案         | 一致性   | 事务隔离 | 性能 | 适用场景      |
| ---------- | ----- | ---- | -- | --------- |
| 2PC（两阶段提交） | 强一致性  | 阻塞事务 | 低  | 金融支付、银行系统 |
| TCC（事务补偿）  | 最终一致性 | 业务补偿 | 高  | 电商、订单系统   |
| 可靠消息最终一致性  | 最终一致性 | 事务消息 | 高  | 订单、库存、支付  |

结论：分布式系统不会严格遵循 CAP，而是通过 Raft、TCC、MQ 等机制来优化事务管理，实现高可用、高一致性、高吞吐的平衡。🚀
