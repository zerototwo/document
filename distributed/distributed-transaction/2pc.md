---
description: 两阶段提交协议（2PC）是一种 分布式事务协议，用于确保多个 数据库或服务 在 分布式环境下 一致提交或回滚事务。
cover: >-
  https://images.unsplash.com/photo-1738557555727-7116a7d5ce83?crop=entropy&cs=srgb&fm=jpg&ixid=M3wxOTcwMjR8MHwxfHJhbmRvbXx8fHx8fHx8fDE3Mzk0NjYwODl8&ixlib=rb-4.0.3&q=85
coverY: 0
---

# 2PC

<figure><img src="../../.gitbook/assets/image (1) (1) (1) (1).png" alt=""><figcaption></figcaption></figure>

## 1.两阶段提交的角色

* 协调者（Coordinator）：负责管理事务的提交或回滚
* 参与者（Participants，即数据库节点）：执行事务的数据库或服务

## 2.两阶段提交的流程

### 第一阶段：准备阶段（Prepare Phase）

1. 客户端 向 协调者 发送事务请求
2. 协调者 依次向所有 参与者 发送 “准备提交” 请求
3. 参与者 执行事务 但不提交，并记录 Undo Log 和 Redo Log
4. 参与者 返回

成功（Yes，准备成功）

失败（No，准备失败）



### 第二阶段：提交/回滚阶段（Commit/Rollback Phase）

* 情况①：所有参与者都返回 “Yes”

1. 协调者 发送 “提交” 请求
2. 参与者 执行 正式提交
3. 事务完成

* 情况②：任意参与者返回 “No” 或超时

1. 协调者 发送 “回滚” 请求
2. 所有参与者 执行 回滚
3. 事务失败

## 3.2PC 的缺点

### ❌ 同步阻塞问题：

* 所有参与者必须 等待协调者 指令，可能长时间占用资源

### ❌ 单点故障：

* 协调者崩溃，整个事务可能陷入 不确定状态（等待提交 or 回滚）

### ❌ 超时问题：

* 参与者 等待超时 可能导致事务长时间锁定资源

## 4.2PC 的改进方案

### 三阶段提交（3PC，Three-Phase Commit）

* 在 2PC 基础上 增加 “Can Commit” 阶段，防止协调者崩溃导致事务悬挂。

### Paxos/Raft 分布式共识协议

* 解决 2PC 同步阻塞 和 单点故障 问题，适用于 高可用分布式系统。

### TCC（Try-Confirm-Cancel）事务

更适用于业务层面，分成：

* Try（预留资源）
* Confirm（正式提交）
* Cancel（取消回滚）

## 5.适用场景

* 跨数据库事务：涉及 MySQL + Redis 或 多个数据库实例
* 分布式微服务事务：例如 电商、支付系统
* 多数据中心事务：涉及 远程数据同步

