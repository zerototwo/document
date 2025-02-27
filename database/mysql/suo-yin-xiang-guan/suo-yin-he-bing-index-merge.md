---
cover: >-
  https://images.unsplash.com/photo-1683512611593-59aa784f5f16?crop=entropy&cs=srgb&fm=jpg&ixid=M3wxOTcwMjR8MHwxfHJhbmRvbXx8fHx8fHx8fDE3NDA2NjA2MzB8&ixlib=rb-4.0.3&q=85
coverY: 0
---

# 索引合并（Index Merge）

## 1.什么是索引合并（Index Merge）？

索引合并（Index Merge） 是 MySQL 优化器的一种执行策略，用于 同时使用多个索引提高查询性能。当查询条件涉及多个列时，MySQL 可能会选择多个索引并合并结果。

## 2.索引合并的执行方式

索引合并主要有 3 种模式：

### 1. UNION（并集索引合并）

* 多个索引的结果取“并集”，然后进行去重。
* 适用于 多个 OR 条件，每个字段都有独立索引。

```java
SELECT * FROM users WHERE age = 25 OR gender = 'M';
```

#### 执行流程

1. 使用 age 索引查找 age = 25 的数据
2. 使用 gender 索引查找 gender = 'M' 的数据
3. 合并（UNION）两个索引的结果集
4. 去重后返回最终数据

### 2. INTERSECTION（交集索引合并）

* 多个索引的结果取“交集”，只保留同时匹配的记录。
* 适用于 多个 AND 条件，每个字段都有独立索引。

```sql
SELECT * FROM users WHERE age = 25 AND gender = 'M';
```

#### 执行流程

1. 使用 age 索引查找 age = 25 的数据
2. 使用 gender 索引查找 gender = 'M' 的数据
3. 取交集（INTERSECT），只保留同时满足的记录
4. 返回最终数据

### 3. SORT-UNION（排序合并）

* 多个索引分别扫描，再排序合并
* 适用于 索引条件为 OR，但 UNION 无法高效执行

```sql
SELECT * FROM users WHERE age = 25 OR city = 'New York';
```

#### 执行流程

1. 使用 age 索引获取 age = 25 的数据
2. 使用 city 索引获取 city = 'New York' 的数据
3. 排序合并结果
4. 返回最终数据

## 3.如何查看索引合并是否生效？

### 1. 使用 EXPLAIN 语句

```sql
EXPLAIN SELECT * FROM users WHERE age = 25 OR gender = 'M';
```

#### 可能的 Extra 信息

| type                  | 含义                   |
| --------------------- | -------------------- |
| index\_merge          | MySQL 选择索引合并         |
| Using union(...)      | 使用 UNION 合并索引        |
| Using intersect(...)  | 使用 INTERSECTION 合并索引 |
| Using sort-union(...) | 使用 SORT-UNION 进行排序合并 |

## 4.索引合并 vs. 复合索引

### 什么时候用索引合并？

1. 多个索引都能提高查询效率
2. 无法创建合适的联合索引
3. 查询条件涉及多个 OR，但不能使用单个索引\


### 什么时候用复合索引（联合索引）

1. 查询条件固定，适合索引顺序
2. AND 连接的多个列，且查询效率高
3. 避免索引合并的额外开销

### 示例

```sql
CREATE INDEX idx_age_gender ON users (age, gender);
```

✅ 对于 AND 查询，复合索引通常比索引合并更快！

## 5.索引合并优化建议

| 优化策略                    | 建议                      |
| ----------------------- | ----------------------- |
| 尽量使用复合索引                | 避免 index\_merge 额外的合并开销 |
| 减少 OR 条件查询              | 改为 UNION ALL 或 IN 查询    |
| 索引选择性要高                 | 避免低选择性索引合并，影响性能         |
| 调整 optimizer\_switch 选项 | 可手动开启/关闭 index\_merge   |

✅ 关闭索引合并（避免性能问题）

```sql
SET optimizer_switch = 'index_merge=off';
```

## 6.总结

| 方案                | 适用场景                 | 性能        |
| ----------------- | -------------------- | --------- |
| 索引合并（Index Merge） | 多个独立索引，查询涉及 OR 或 AND | 适用于部分场景   |
| 复合索引（联合索引）        | 查询涉及多个字段的 AND 条件     | 通常比索引合并更快 |

一般情况下， 复合索引优于索引合并，但当无法创建合适的联合索引时，索引合并是备选方案！&#x20;
