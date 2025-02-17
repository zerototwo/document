---
description: >-
  Kafka 能够实现高吞吐、低延迟，其中 “零拷贝（Zero Copy）” 技术起到了关键作用。Kafka 采用 Linux 的 sendfile()
  机制，让数据 在内核空间直接传输，避免用户空间和内核空间的数据拷贝，从而 大幅减少 CPU 开销 & 提高传输效率。
cover: >-
  https://images.unsplash.com/photo-1737366984875-fb81751f6655?crop=entropy&cs=srgb&fm=jpg&ixid=M3wxOTcwMjR8MHwxfHJhbmRvbXx8fHx8fHx8fDE3Mzk3ODU2Nzd8&ixlib=rb-4.0.3&q=85
coverY: 0
---

# Kafka 零拷贝（Zero Copy）

## 1.什么是零拷贝（Zero Copy）

**传统的 I/O 读写 需要 4 次数据拷贝 & 4 次用户态/内核态切换：**

* 磁盘数据 → 内核缓冲区（PageCache）
* 内核缓冲区 → 用户缓冲区（应用层）
* 用户缓冲区 → Socket 缓冲区
* Socket 缓冲区 → 网络传输



**问题**：

* 数据需要在用户态 & 内核态之间多次拷贝，导致 CPU 开销大，吞吐量受限。
* Kafka 需要高吞吐，如果每条消息都需要 多次数据拷贝，会严重影响性能。

## 2.Kafka 如何利用零拷贝？

Kafka 使用 sendfile() 代替传统的 read() & write()，减少数据拷贝次数。

### 传统方式（read + write）

```cpp
// 传统 I/O
int fd = open("file.txt", O_RDONLY);
char buf[4096];

while (read(fd, buf, sizeof(buf)) > 0) {
    write(socket_fd, buf, sizeof(buf));
}
```

• 数据先读入应用程序缓冲区，再写入 Socket，产生 4 次拷贝。

### 零拷贝（sendfile 方式）

```cpp
// 使用 sendfile() 实现零拷贝
int fd = open("file.txt", O_RDONLY);
sendfile(socket_fd, fd, NULL, file_size);
```

• sendfile() 直接让数据从 PageCache 进入 Socket，减少 CPU 拷贝。

## 3.Kafka 零拷贝的 4 大优化

| 优化点         | 传统方式（read + write）     | Kafka（sendfile）     |
| ----------- | ---------------------- | ------------------- |
| 数据拷贝次数      | 4 次（磁盘 → 内核 → 用户 → 网络） | 2 次（磁盘 → 内核 → 网络）   |
| 用户态 / 内核态切换 | 4 次（CPU 开销大）           | 2 次（CPU 负担小）        |
| CPU 占用      | 高（数据多次拷贝）              | 低（直接从 PageCache 发送） |
| 吞吐量         | 低（CPU 处理速度受限）          | 高（数据传输更快）           |

## 4.Kafka 零拷贝工作流程

### 4.1Producer 生产数据

• Producer 将数据发送到 Kafka Leader 副本。



### 4.2Kafka Broker 先写入 PageCache

• Kafka 不会直接写入磁盘，而是先写入 PageCache，等待 Consumer 读取。



### 4.3Consumer 读取数据

• Kafka 调用 sendfile() 直接从 PageCache 发送数据到网络。



### 4.4零拷贝传输

• 数据直接从 PageCache 进入 Socket 缓冲区，避免 CPU 额外拷贝。

## 5.为什么 Kafka 采用零拷贝？

* 减少 CPU 开销（少了 2 次拷贝 & 2 次用户态/内核态切换）。
* 提高吞吐量（避免数据多次拷贝 & 线程阻塞）。
* 减少延迟（直接从 PageCache 传输数据到 Socket）。
* 适合大数据流处理（Kafka 主要用于日志 & 流式数据，高吞吐是关键）。

## 6.结论

💡 Kafka 采用 Linux sendfile() 进行零拷贝，让数据 直接从 PageCache 进入 Socket 发送到网络，避免传统 I/O 的多次数据拷贝和 CPU 负担，极大提升了数据传输的吞吐量 & 处理效率。\


👉 零拷贝（Zero Copy）是 Kafka 高性能的关键技术之一，确保 Kafka 在海量数据流转时保持超高吞吐 & 低延迟！
