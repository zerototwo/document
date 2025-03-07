---
description: >-
  TCC（Try-Confirm-Cancel）是一种分布式事务解决方案，相较于 2PC 和 3PC，它更加灵活，不依赖数据库锁，适用于
  高并发、微服务、分布式系统。
cover: >-
  https://images.unsplash.com/photo-1737798388229-2524c7777c60?crop=entropy&cs=srgb&fm=jpg&ixid=M3wxOTcwMjR8MHwxfHJhbmRvbXx8fHx8fHx8fDE3Mzk1NDc3NDF8&ixlib=rb-4.0.3&q=85
coverY: 0
---

# TCC (Try-Confirm-Cancel)

## 1.TCC 事务的基本流程

TCC 事务模型由 三个阶段 组成：

### 1.1Try（尝试阶段）：

* 预留资源，进行事务的初步检查。
* 例如，在资金转账中，Try 阶段会先锁定金额但不真正扣款。

### 2.Confirm（确认阶段）：

* 业务操作正式提交。
* 例如，扣款操作真正生效，资金从账户 A 转入账户 B。

### 3.Cancel（取消阶段）：

* 发生异常时，回滚预留的资源，恢复到 Try 之前的状态。

## 2.TCC 事务的执行示例

以 银行转账 为例：

* 用户 A 向用户 B 转账 100 元

### 2.1Try 阶段

* 用户 A 账户 冻结 100 元（但未真正扣款）
* 用户 B 账户真正增加 100 元

### 2.2Confirm 阶段

* 用户 A 账户真正扣除 100 元
* 用户 B 账户真正增加 100 元

### 2.3Cancel 阶段（异常回滚）

* 用户 A 账户解冻 100 元
* 用户 B 账户不变

## 3.TCC 事务的优势

✅ 降低数据库锁竞争：

* TCC 采用应用层控制事务，不会长期占用数据库锁，提高并发能力。

✅ 灵活适配业务逻辑：

* Try 阶段可以自定义业务校验逻辑，例如库存检查、权限校验等。

✅ 事务可恢复：

* 失败时可以 手动重试 或 定期扫描补偿，提升可用性。

## 4.TCC 事务的挑战

❌ 业务侵入性高：

* 需要应用开发者实现 Try / Confirm / Cancel 三个操作，开发成本较高。

❌ 回滚复杂：

* 由于 TCC 事务是分布式的，Cancel 阶段需要设计幂等性和事务补偿机制，否则可能导致数据不一致。

❌ 并发控制难度大：

* 例如，两个并发事务可能导致相同资源被 Try 预留，但最后只有一个事务能成功。



## 5.空回滚、幂等、悬挂问题

### 5.1空回滚

空回滚 在没有调用TCC资源Try方法得情况下，调用了二阶段得Cancel方法，Cancel方法需要识别出这是一个空回滚，然后直接返回成功。

#### 原因

当一个分支事务所在服务宕机或者网络异常，分支事务调用记录为失败，这个时候其实还没有执行Try阶段的，当故障恢复后，分支事务进行回滚则会调用二阶段得Cancel方法，从而形成空回滚。

#### 解决思路

&#x20;解决的关键就是要识别出这个空回滚。方法很简单就是需要知道一阶段是否执行，如果执行了，那就是正常回滚；如果没执行，那就是空回滚。TM在发起全局事务时会生成全局事务记录，全局事务ID贯穿整个分布式事务调用链条。可以再额外增加一张分支事务记录表，其中有全局事务 ID 和分支事务 ID，第一阶段 Try 方法里会插入一条记录，表示一阶段执行了。Cancel 接口里读取该记录，如果该记录存在，则正常回滚；如果该记录不存在，则是空回滚。

### 5.2幂等

幂等 TCC模式在Try阶段执行成功后必须保证二阶段也成功执行，所以二阶段需要有重试机制。

幂等出现原因 为了保证TCC二阶段提交重试机制不会引发数据不一致，要求 TCC 的二阶段 Try、Confirm 和 Cancel 接口保证幂等，这样不会重复使用或者释放资源。如果幂等控制没有做好，很有可能导致数据不一致等严重问题。

#### 解决思路

在上述“分支事务记录”中增加执行状态，每次执行前都查询该状态，如果是未执行的状态则执行否则不执行。

### 5.3悬挂&#x20;

悬挂就是对于一个分布式事务，其二阶段 Cancel 接口比 Try 接口先执行。

出现原因 在 RPC(远程访问) 调用分支事务try时，先注册分支事务，再执行RPC调用，如果此时 RPC 调用的网络发生拥堵，通常 RPC 调用是有超时时间的，RPC 超时以后，TM就会通知RM回滚该分布式事务，可能回滚完成后，RPC 请求才到达参与者并且真正执行成功，而此时Try 方法才执行完成并且将所需的业务资源预留，但是此时二阶段已经完成无法对预留的资源做出处理。对于这种情况，我们就称为悬挂，即业务资源预留后没法继续处理。

#### 解决思路

如果二阶段执行完成，那一阶段就不能再继续执行。在执行一阶段事务时判断在该全局事务下，“分支事务记录”表中是否已经有二阶段事务记录，如果有则不执行Try。&#x20;

## 5.适用场景

✅ 微服务架构

* 适用于电商、支付、库存管理等分布式业务。

✅ 高并发系统

* 适用于 大规模并发交易，如 秒杀、订单处理。

✅ 无数据库锁的业务

* 例如 Redis 缓存事务、消息队列事务。

## 总结

* TCC 事务是一种轻量级分布式事务解决方案，适用于高并发、分布式环境。
* 相比 2PC/3PC，它避免了数据库锁竞争，但需要业务端实现事务控制。
* 适合微服务架构，如支付、库存、订单等场景。







