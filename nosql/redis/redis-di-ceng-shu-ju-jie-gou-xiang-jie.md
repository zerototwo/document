---
description: Redis 采用多种数据结构来优化不同数据类型的存储和查询效率。
cover: >-
  https://images.unsplash.com/photo-1722449304165-5ae436a656d8?crop=entropy&cs=srgb&fm=jpg&ixid=M3wxOTcwMjR8MHwxfHJhbmRvbXx8fHx8fHx8fDE3Mzk2MjI1NTV8&ixlib=rb-4.0.3&q=85
coverY: 0
---

# Redis 底层数据结构详解

* SDS（简单动态字符串）
* LinkedList（双向链表）
* Hashtable（哈希表）
* SkipList（跳表）
* IntSet（整数集合）
* QuickList（压缩列表 + 链表）
* StreamList（时间序列数据结构）

## 1. SDS（Simple Dynamic String，简单动态字符串）

🔹 用于： String 类型

🔹 作用： 代替 C 语言 char\*，提供自动扩展、避免缓冲区溢出等功能。

📌 SDS 结构

```
struct sdshdr {
    int len;    // 已使用字节数
    int free;   // 预分配空间
    char buf[]; // 存储实际字符串数据
};
```

✅ 特点

• 动态扩展：len + free 小于 1MB 时，扩展为 2 倍；否则，每次扩展 1MB。

• 二进制安全：SDS 可以存储 任意二进制数据，包括 \0。

• 减少内存碎片：避免 C 语言 strlen() 计算字符串长度的问题。

## 2. LinkedList（双向链表）

🔹 用于： List 类型（早期 Redis 版本）

🔹 作用： 适用于插入和删除操作频繁的场景。

📌 链表结构

```
struct listNode {
    void *value;
    struct listNode *prev;
    struct listNode *next;
};
```

✅ 特点

• 双向结构，可以从头部和尾部快速操作元素。

• 高效插入/删除，O(1) 复杂度。

• 适用于 早期 list 数据类型，后期被 quicklist 取代。

## 3. Hashtable（哈希表）

🔹 用于： Hash 类型、Redis 全局键值存储（dict）

🔹 作用： 快速存储 键值对，支持 O(1) 级别查询。

📌 哈希表结构

```
typedef struct dictht {
    dictEntry **table; // 哈希桶数组
    unsigned long size; // 哈希表大小
    unsigned long used; // 已用桶数
} dictht;
```

✅ 特点

• 使用 MurmurHash2 算法 计算 key 的哈希值，减少冲突。

• 渐进式 rehash：

• 新数据存入新哈希表

• 旧数据逐步迁移，避免 resize 带来的阻塞。



📌 适用场景

• 小型对象存储（< 64 字节，键值对数量 < 512）。

• 键值对存储（key-value）。

## 4. SkipList（跳表）

🔹 用于： Sorted Set（有序集合）

🔹 作用： 有序数据存储，支持范围查询。

📌 跳表结构

```
typedef struct zskiplistNode {
    struct zskiplistNode *backward;
    struct zskiplistLevel {
        struct zskiplistNode *forward;
        unsigned int span;
    } level[];
} zskiplistNode;
```

✅ 特点

• 平均查询复杂度 O(log N)，比 平衡二叉树 结构简单。

• 多层级索引，比链表查询更快。

• 适用于 ZSET 类型，支持排序、排名、范围查询。

\


📌 适用场景

• 排行榜、排名查询（如 TOP N 需求）。

• 金融 K 线数据存储。

## 5. IntSet（整数集合）

🔹 用于： Set 类型（所有元素是整数时）

🔹 作用： 存储小规模整型集合，比哈希表节省内存。

📌 结构

```
struct intset {
    uint32_t encoding; // 编码方式
    uint32_t length;   // 集合元素个数
    int8_t contents[]; // 实际存储数据
};
```

✅ 特点

• 节省内存：小数据量时比 hashtable 低。

• 自动升级：

• 16-bit → 32-bit → 64-bit，避免存储溢出。

• 查询 O(log N)，支持二分查找。

📌 适用场景

• 存储用户 ID、好友列表（整数集合）。

## 6. QuickList（压缩列表 + 链表）

🔹 用于： List 类型（新版本）

🔹 作用： 替代 LinkedList，节省内存，同时支持快速插入/删除。

📌 QuickList 结构

```
struct quicklist {
    quicklistNode *head;
    quicklistNode *tail;
    unsigned long count;
};
```

✅ 特点

• 综合 ziplist（紧凑存储）+ linkedlist（双向操作）。

• 减少指针开销，避免碎片化。

• 适用于 List 存储场景，如消息队列、聊天记录。

📌 适用场景

• 消息队列、日志存储。

## 7. StreamList（时间序列数据结构）

🔹 用于： Stream 类型（消息队列）

🔹 作用： 存储时间序列数据，类似 Kafka 结构。

📌 结构

```
struct stream {
    rax *rax_tree;
    streamID last_id;
    streamNACK *nacks;
};
```

✅ 特点

• 高效存储时间序列数据。

• 支持消费组（类似 Kafka），提供消息可靠性。

• 适用于 log 数据、实时消息推送。

📌 适用场景

• 消息队列、实时日志存储（如 Kafka 替代品）。

## 8. Redis 底层数据结构选型

| 数据结构       | 适用数据类型     | 作用      | 适用场景       |
| ---------- | ---------- | ------- | ---------- |
| SDS        | String     | 高效字符串存储 | 计数器、缓存     |
| LinkedList | List（旧）    | 双向链表    | 早期版本 Redis |
| QuickList  | List（新）    | 快速列表    | 消息队列、日志    |
| Hashtable  | Hash       | 哈希存储    | 购物车、用户信息   |
| SkipList   | Sorted Set | 有序存储    | 排行榜、股票 K 线 |
| IntSet     | Set（整数）    | 小整数集合   | 用户 ID 存储   |
| StreamList | Stream     | 消息存储    | 日志、消息队列    |

## 9. 结论

✅ 高效存储：Redis 根据不同数据类型，选择合适的数据结构。

✅ 节省内存：采用 QuickList / ZipList / IntSet 等优化存储。

✅ 适用于高并发：Epoll + 非阻塞 IO 支持高吞吐量。

