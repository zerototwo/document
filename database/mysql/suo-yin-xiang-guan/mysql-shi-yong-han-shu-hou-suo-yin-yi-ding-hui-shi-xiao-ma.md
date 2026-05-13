---
description: 虽然在 大多数情况下，如果 WHERE 或 JOIN 语句中的列使用了函数，MySQL 无法使用索引，但 部分情况可以优化避免索引失效。
cover: >-
  https://images.unsplash.com/photo-1723652057541-60b1069f6542?crop=entropy&cs=srgb&fm=jpg&ixid=M3wxOTcwMjR8MHwxfHNlYXJjaHw1fHxtfGVufDB8fHx8MTc0MDkwOTY2Mnww&ixlib=rb-4.0.3&q=85
coverY: 0
---

# MySQL 使用函数后索引一定会失效吗？

## 1.索引失效的情况

当 WHERE 子句中的索引列被函数包裹时，MySQL 可能会无法利用索引，导致 全表扫描（Full Table Scan）。

### 示例

```sql
SELECT * FROM users WHERE LOWER(email) = 'test@example.com';
```

### 为什么索引失效？

* 如果 email 列上有索引 idx\_email (email)，MySQL 无法直接利用索引，因为 LOWER(email) 会导致索引列的值被计算，而索引存储的是原始值。
* 这会导致 索引失效，使 MySQL 进行全表扫描（Using where + Using filesort）。

### 查看索引使用情况

```sql
EXPLAIN SELECT * FROM users WHERE LOWER(email) = 'test@example.com';
```

如果 possible\_keys 为空，说明索引未被使用。

## 2.避免索引失效的方法

✅ 方法 1：改写查询逻辑

<br>

避免在索引列上使用函数，而是将计算逻辑移到查询之外。

<br>

🔹 错误示例

```
SELECT * FROM users WHERE YEAR(created_at) = 2024;
```

📌 索引失效原因：

• YEAR(created\_at) 会对 每一行 进行计算，导致 索引无法使用。

<br>

🔹 正确写法

```
SELECT * FROM users WHERE created_at >= '2024-01-01' AND created_at < '2025-01-01';
```

📌 这样可以正常使用索引！

✅ 方法 2：使用 函数索引（Functional Index）（MySQL 8.0+）

<br>

MySQL 8.0+ 支持 函数索引（Generated Index），可以让函数计算后的值也存储在索引中，从而 避免索引失效。

<br>

🔹 创建函数索引

```
ALTER TABLE users ADD INDEX idx_lower_email ((LOWER(email)));
```

🔹 优化查询

```
SELECT * FROM users WHERE LOWER(email) = 'test@example.com';
```

📌 这样 LOWER(email) 仍然可以使用索引！

✅ 方法 3：使用存储列（Generated Column）

<br>

MySQL 5.7+ 允许创建虚拟列，存储计算后的值，并对其建立索引。

<br>

🔹 创建存储列并建立索引

```
ALTER TABLE users ADD COLUMN email_lower VARCHAR(255) GENERATED ALWAYS AS (LOWER(email)) STORED;
ALTER TABLE users ADD INDEX idx_email_lower (email_lower);
```

🔹 查询时使用存储列

```
SELECT * FROM users WHERE email_lower = 'test@example.com';
```

📌 这样 MySQL 能够正常使用索引！

## 3.哪些函数不会导致索引失效？

某些优化过的函数 不会影响索引，例如：

| 函数              | 索引是否有效 | 示例                                      |
| --------------- | ------ | --------------------------------------- |
| ABS()           | ❌ 失效   | WHERE ABS(id) = 10                      |
| UPPER()/LOWER() | ❌ 失效   | WHERE LOWER(email) = 'test@example.com' |
| YEAR()          | ❌ 失效   | WHERE YEAR(created\_at) = 2024          |
| BETWEEN         | ✅ 有效   | WHERE id BETWEEN 10 AND 20              |
| LIKE 'prefix%'  | ✅ 有效   | WHERE name LIKE 'Jo%'                   |
| LIKE '%suffix'  | ❌ 失效   | WHERE name LIKE '%son'                  |
| IN()            | ✅ 有效   | WHERE id IN (1, 2, 3)                   |
| IS NULL         | ✅ 有效   | WHERE email IS NULL                     |

## 4.结论

❌ 索引会失效的情况

• WHERE 语句中索引列使用函数（LOWER()、YEAR()、ABS()）。

• LIKE '%xxx' 这种前导通配符匹配。

• 隐式类型转换（如 WHERE id = '123'，id 是 INT）。

<br>

✅ 避免索引失效的方法

1\. 改写查询（避免在索引列上使用函数）。

2\. MySQL 8.0+ 使用函数索引（CREATE INDEX idx ON table ((LOWER(column)))）。

3\. 使用存储列（Generated Column）+ 索引（MySQL 5.7+）。

4\. 优化 WHERE 条件，让 MySQL 直接使用索引值 进行查询。

<br>

💡 索引优化是数据库性能优化的关键，避免索引失效可以大幅提高查询效率！ 🚀
