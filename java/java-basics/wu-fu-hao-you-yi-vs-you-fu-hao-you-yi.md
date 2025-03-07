# >>>（无符号右移） vs >>（有符号右移）

| 运算符   | 名称        | 作用                      | 负数填充                       | 适用场景              |
| ----- | --------- | ----------------------- | -------------------------- | ----------------- |
| `>>`  | **有符号右移** | **右移 `n` 位，保留符号**       | **填充符号位**（负数补 `1`，正数补 `0`） | 保持正负号，如二进制计算、算术运算 |
| `>>>` | **无符号右移** | **右移 `n` 位，左侧始终填充 `0`** | **始终填充 `0`**（不管正负）         | 处理无符号数据，如哈希运算、位运算 |

## 示例对比

### 例 1：正数右移

```java
int a = 8;  // 0000 0000 0000 0000 0000 0000 0000 1000
System.out.println(a >> 2);  // 0000 0000 0000 0000 0000 0000 0000 0010 = 2
System.out.println(a >>> 2); // 0000 0000 0000 0000 0000 0000 0000 0010 = 2
```

✅ 结论：正数 >> 和 >>> 结果相同，都用 0 填充高位。

### 例 2：负数右移

```java
int b = -8;  // 负数补码: 1111 1111 1111 1111 1111 1111 1111 1000
System.out.println(b >> 2);  
// 右移 2 位，保持符号位 1：
// 1111 1111 1111 1111 1111 1111 1111 1110 = -2

System.out.println(b >>> 2);
// 右移 2 位，无符号填充 0：
// 0011 1111 1111 1111 1111 1111 1111 1110 = 1073741822
```

✔ 负数 >> 填充 1，结果 -2

✔ 负数 >>> 填充 0，结果 1073741822（高位全 0，变成正数）
