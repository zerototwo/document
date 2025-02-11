---
description: >-
  页分裂是 InnoDB 维护 B+ 树索引 时，为了保证索引结构平衡而进行的数据页拆分操作。当一个页（Leaf
  Page）填满后，需要新建一个页，并迁移部分数据，导致写入放大和性能下降。
---

# 如何避免 InnoDB 页分裂？

## 避免页分裂的方法

### 1.选择合适的主键 (Primary Key)

避免使用过长的主键（如 UUID、随机字符串），推荐使用 自增 ID (AUTO\_INCREMENT) 作为主键。

✅ 推荐

```sql
CREATE TABLE users (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    age INT
) ENGINE=InnoDB;
```

**原因：**

* 自增 ID 使数据按顺序插入，避免频繁的页分裂。
* 避免随机键（如 UUID），否则数据会插入到 B+ 树的不同位置，导致频繁分裂。

❌ 不推荐

```sql
CREATE TABLE users (
    uuid CHAR(36) PRIMARY KEY,
    name VARCHAR(255),
    age INT
) ENGINE=InnoDB;
```

**问题：**

* UUID 是随机的，每次插入数据会在 B+ 树的不同位置，造成大量页分裂和写入放大。

### 2.适当调整 fill\_factor（页填充因子）

* 默认情况下，InnoDB 在页填充满 100% 时才会触发分裂。
* 通过 降低填充因子（控制页的填充程度），可以减少数据插入时的页分裂。

**方法：**

* 使用 innodb\_fill\_factor 控制填充比率，使页在分裂前预留空间。

```sql
SET GLOBAL innodb_fill_factor = 80;
```

默认值 100%，可以调整到 80-90%，避免后续插入数据时频繁触发页分裂。

### 3.批量插入数据，而非单条插入

减少随机插入，使用 批量插入 避免多次触发页分裂。

✅ 推荐

```sql
INSERT INTO users (name, age) VALUES 
('Alice', 25),
('Bob', 30),
('Charlie', 28);
```

❌ 不推荐

```sql
INSERT INTO users (name, age) VALUES ('Alice', 25);
INSERT INTO users (name, age) VALUES ('Bob', 30);
INSERT INTO users (name, age) VALUES ('Charlie', 28);
```

**原因：**

* 单条插入会触发多次索引更新，影响性能。
* 批量插入可减少 B+ 树结构调整，避免频繁的页分裂。

### 4.控制索引数量，避免冗余索引

**索引过多会增加页分裂的概率**，因为每次插入数据时，所有索引页都会受到影响。

**建议：**

* 只创建 必要的索引，避免创建 冗余索引。

✅ 推荐

```sql
CREATE INDEX idx_name ON users(name);
```

❌ 不推荐

```sql
CREATE INDEX idx_name ON users(name);
CREATE INDEX idx_name_age ON users(name, age);
```

**问题：**

* 冗余索引会导致数据页频繁分裂，增加存储空间和维护成本。

## 5.监控和优化 innodb\_page\_size

默认 innodb\_page\_size 为 16KB，但如果数据行较小，可以适当调整。

```
SHOW VARIABLES LIKE 'innodb_page_size';
```

* 如果 单行数据较大（如 JSON、BLOB、TEXT），建议使用 大页大小（16KB）。
* 如果 单行数据较小（如 INT、VARCHAR），可以考虑 使用 8KB 或 4KB 的页，减少分裂带来的额外存储开销。

### 6.总结

| **方法**                    | **原理**            | **适用场景**        |
| ------------------------- | ----------------- | --------------- |
| **使用自增 ID 作为主键**          | 让数据顺序插入，减少 B+ 树分裂 | 适用于大部分 InnoDB 表 |
| **降低填充因子 (fill\_factor)** | 预留部分空间，减少插入时的页分裂  | 适用于频繁插入更新的表     |
| **批量插入数据**                | 避免多次索引更新，提高写入性能   | 适用于大批量数据插入场景    |
| **优化索引数量**                | 避免冗余索引，减少 B+ 树调整  | 适用于索引较多的表       |
| **调整 innodb\_page\_size** | 选择合适的页大小，减少存储浪费   | 适用于大字段存储        |



