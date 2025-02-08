---
cover: >-
  https://images.unsplash.com/photo-1737625775035-31acd1e4e18b?crop=entropy&cs=srgb&fm=jpg&ixid=M3wxOTcwMjR8MHwxfHJhbmRvbXx8fHx8fHx8fDE3MzkwMzI0NTB8&ixlib=rb-4.0.3&q=85
coverY: 0
---

# Mysql

| **知识点**             | **重点内容**                             | **高频面试问题**                     |
| ------------------- | ------------------------------------ | ------------------------------ |
| **MySQL 体系架构**      | MySQL 逻辑架构、SQL 执行流程、查询优化器            | 一条 SQL 如何执行？查询优化器的作用？          |
| **存储引擎**            | InnoDB vs. MyISAM，存储结构、适用场景          | 为什么选择 InnoDB？MyISAM 适用于哪些场景？   |
| **索引优化**            | B+ 树索引、哈希索引、最左匹配、覆盖索引、索引下推           | 什么是回表查询？什么情况下索引失效？             |
| **事务（Transaction）** | ACID 事务特性，事务隔离级别，MVCC                | MySQL 默认的事务隔离级别是什么？如何避免幻读？     |
| **锁机制**             | 表锁 vs. 行锁，间隙锁，死锁检测与解决                | 如何分析死锁？间隙锁是如何工作的？              |
| **SQL 优化**          | EXPLAIN 分析，慢查询日志，索引优化                | 如何优化 ORDER BY？如何减少回表？          |
| **主从复制**            | binlog 复制机制，主备切换，GTID                | MySQL 如何实现主从同步？GTID 的作用是什么？    |
| **高并发优化**           | 读写分离，分库分表，连接池优化                      | MySQL 如何支撑高并发？如何设计分库分表策略？      |
| **分区表**             | Range、List、Hash、Key 分区的区别            | 分区表的优缺点？分区键如何选择？               |
| **大表优化**            | 数据分片，冷热数据分离，索引优化                     | MySQL 百万级数据如何优化查询性能？           |
| **存储与查询优化**         | 覆盖索引、索引合并、索引优化                       | 覆盖索引 vs. 普通索引的区别？如何减少回表？       |
| **连接查询优化**          | JOIN 语句优化，临时表、索引优化                   | INNER JOIN 和 LEFT JOIN 哪个性能更优？ |
| **MySQL 配置优化**      | InnoDB Buffer Pool，redo log，undo log | redo log 和 binlog 的区别？         |
| **MySQL 备份恢复**      | 逻辑备份（mysqldump）、物理备份（xtrabackup）     | 误删数据如何恢复？binlog 作用是什么？         |
| **MySQL 安全**        | 用户权限管理，SQL 注入防护                      | 如何防止 SQL 注入？如何查看当前用户权限？        |
