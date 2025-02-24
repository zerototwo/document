---
cover: >-
  https://images.unsplash.com/photo-1737270019710-62b36a249aca?crop=entropy&cs=srgb&fm=jpg&ixid=M3wxOTcwMjR8MHwxfHJhbmRvbXx8fHx8fHx8fDE3Mzk1MjUxNTJ8&ixlib=rb-4.0.3&q=85
coverY: 0
---

# Distributed transaction

## 强一致性 vs. 最终一致性

| 对比项  | 强一致性 (2PC, 3PC, XA) | 最终一致性 (TCC, SAGA, MQ) |
| ---- | ------------------- | --------------------- |
| 一致性  | 严格一致性               | 最终一致性                 |
| 性能   | 较差（锁资源，影响性能）        | 高（低延迟，容忍短暂不一致）        |
| 适用场景 | 金融、银行、支付            | 电商、跨服务操作、微服务          |
| 故障恢复 | 事务失败时回滚             | 通过补偿操作恢复一致性           |
