---
cover: >-
  https://images.unsplash.com/photo-1554734973-210811bdcabd?crop=entropy&cs=srgb&fm=jpg&ixid=M3wxOTcwMjR8MHwxfHNlYXJjaHw3fHxmfGVufDB8fHx8MTc0MDkyNzIzNXww&ixlib=rb-4.0.3&q=85
coverY: 0
---

# 数据库连接池满排查过程

## 1.数据库连接池满排查过程

在某些情况下，线上系统可能会因数据库连接池资源耗尽导致请求阻塞，具体的报错信息如下：

```sh
Caused by: ERR-CODE: [IDBX-4103] [ERR_ATON_CONNECTION_POOL_FULL]
Pool of 'xxxx' is full.
Message from pool: wait millis: 5000, active 10, maxActive 10.
```

## 2.查询数据库连接情况

```sql
SELECT * FROM information_schema.processlist 
WHERE COMMAND != 'Sleep' 
ORDER BY TIME DESC;
```

同时查看阿里云服务，发现有大量的同一个记录的耗时SQL。发现是一个乐观锁更新sql.

## 3.SQL示例

```sql
UPDATE user_balance 
SET balance = balance - 100, 
    version = version + 1 
WHERE user_id = 123 
AND version = 3;
```

为什么乐观锁还会导致大量的锁耗时呢？

虽然乐观锁是不需要加锁的，通过CAS的方式进行无锁并发控制进行更新的。但是InnoDB的update语句是要加锁的。当并发冲突比较大，发生热点更新的时候，多个update语句就会排队获取锁。

而这个排队的过程就会占用数据库连接，一旦排队的事务比较多的时候，就会导致数据库连接被耗尽。

## 4.解决方法

这类问题的解决思路有以下几个：

1、基于缓存进行热点数据更新，如 Redis。

2、通过异步更新的方式，将高并发的更新削峰填谷掉。

3、将热点数据进行拆分，分散到不同的库、不同的表中，减少并发冲突。

4、合并更新请求，通过批量执行的方式来降低冲突。（比如你有 10 条增加积分的操作要执行，那么你就可以算出这十条一共要加多少积分，一次性加上去）

其中，第 2 个和第 4 个方案，存在一定的延迟性，会把实时更新变异步更新，存在一定的数据实时性问题\


第 1 个和第 3 个方案，实现起来成本比较高，但是相对来说更加完整一点。

根据我们的实际业务场景，我们选择了第 4 个方案，将更新操作进行合并，批量执行。



比如本来需要 100 个交易金额累计，那么改成 10 分钟更新一次，一次就把 10 分钟中的所有需要增加的积分汇总之后一次更新用户交易金额累计表即可。
