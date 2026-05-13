# redis 分布式锁式

好的，这里是Redis 实现分布式锁的完整整理版，涵盖 锁的原理、几种实现方式、比较分析、最佳实践与推荐，并配图帮助理解。

***

### 🧠 一、什么是分布式锁？

<br>

分布式锁用于协调多个进程或系统实例对共享资源的并发访问。

特点包括：

* 互斥性：同一时间只有一个客户端能获取锁。
* 避免死锁：锁不能永久占用，必须有超时机制。
* 可重入性（可选）：同一个客户端可以多次获得锁。
* 高可用性：系统崩溃后锁能自动释放。

***

### 🧰 二、Redis 实现分布式锁的常见方式

| 实现方式           | 原子性 | 自动过期   | 安全解锁   | 高可用性   | 推荐等级     |
| -------------- | --- | ------ | ------ | ------ | -------- |
| SETNX + EXPIRE | ❌   | ✅（非原子） | ❌      | ❌      | ⭐（不推荐）   |
| SET NX PX（推荐）  | ✅   | ✅      | ✅（Lua） | ❌（单实例） | ⭐⭐⭐⭐     |
| Redisson       | ✅   | ✅（可续期） | ✅      | ❌      | ⭐⭐⭐⭐⭐    |
| Redlock（官方算法）  | ✅   | ✅      | ✅      | ✅（多节点） | ⭐⭐⭐⭐（复杂） |

***

### 🔍 三、实现原理详解

<br>

#### 1️⃣ SETNX + EXPIRE（过时方案）

```
if (redis.setnx("lock:order123", uuid)) {
    redis.expire("lock:order123", 10); // 设置锁超时
}
```

**❌ 问题**

* setnx 和 expire 非原子：setnx 成功但程序 crash 会造成死锁。
* 无法安全解锁：可能误删他人锁。

***

#### 2️⃣ SET NX PX（推荐基础方案）

```
SET lock:order123 uuid NX PX 10000
```

* NX：只在 key 不存在时设置
* PX 10000：设置锁过期时间为 10 秒（ms）
* uuid：每个客户端唯一标识，用于解锁验证

<br>

**✅ 安全解锁（Lua 脚本）：**

```
if redis.call("get", KEYS[1]) == ARGV[1] then
    return redis.call("del", KEYS[1])
else
    return 0
end
```

**优点：**

* 原子加锁
* 自动过期
* 可防误删

***

#### 3️⃣ Redisson（Java 项目首选）

<br>

**支持特性：**

* 自动续期（WatchDog）
* 可重入锁、公平锁、读写锁、红锁
* 自动释放锁，避免死锁

<br>

**使用示例：**

```
RLock lock = redissonClient.getLock("lock:stock");
lock.lock(); // 默认 WatchDog 自动续期
try {
    // 执行逻辑
} finally {
    lock.unlock();
}
```

**WatchDog 工作机制（见下图）：**

* 初始 TTL = 30s（默认）
* 每 10s 自动续期 TTL
* 调用 unlock() 后 WatchDog 停止

***

#### 4️⃣ Redlock（Redis 官方分布式锁）

<br>

适用于多 Redis 实例环境（一般 5 个节点）。

<br>

**流程：**

1. 向多个 Redis 实例尝试 SET NX PX
2. 如果 N/2 + 1 成功，则认为加锁成功
3. 设置 TTL，确保在所有 Redis 节点中生效时间一致
4. 解锁时向所有节点执行 Lua 脚本

<br>

**优点：**

* 抵御单个 Redis 节点宕机
* 高可用保障

<br>

**缺点：**

* 实现复杂
* 存在对时钟和网络延迟依赖问题

***

### 🧭 四、时序图对比（简图）

<br>

#### SET NX PX 原理图

```
Client ——> Redis:
  SET lock_key uuid NX PX 10000  ✅

Client ——> Lua:
  if get(lock_key) == uuid:
     del(lock_key)
```

***

#### Redisson WatchDog 原理图

```
时间轴 →
|-- 加锁（TTL=30s） --|-- 10s 后 WatchDog 续期 --|-- ...直到 unlock() --|
```

***

### ✅ 五、最佳实践建议

| 使用场景               | 推荐方案                 |
| ------------------ | -------------------- |
| 单机 Redis + Java 项目 | Redisson             |
| 多服务节点，无需强一致        | SET NX PX + Lua      |
| 多 Redis 节点需高可用     | Redlock（或 ZooKeeper） |
| 精准控制锁释放时间          | lock(5, TimeUnit.S)  |
| 需要分布式公平锁/读写锁等      | Redisson             |

***

### 🔧 六、Redisson 快速配置

```
singleServerConfig:
  address: "redis://127.0.0.1:6379"
lockWatchdogTimeout: 30000 # 默认锁续期时间
```

Maven 依赖：

```
<dependency>
  <groupId>org.redisson</groupId>
  <artifactId>redisson</artifactId>
  <version>3.23.4</version>
</dependency>
```

***

### 📌 七、小结

| 优点  | Redis 实现        |
| --- | --------------- |
| 简单  | SET NX PX + Lua |
| 强大  | Redisson（自动续期）  |
| 高可用 | Redlock（多节点）    |

***

如果你需要 封装工具类、Spring Boot Starter、Redis Redlock 实现代码模板，我可以继续提供。

是否需要 Java 封装示例或 Redisson 使用模板？
