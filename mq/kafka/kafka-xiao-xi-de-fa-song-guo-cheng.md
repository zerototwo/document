# Kafka 消息的发送过程



<figure><img src="../../.gitbook/assets/image (12).png" alt=""><figcaption></figcaption></figure>

## 1. 生产者（Producer）处理消息

生产者负责 构造消息 并决定发送到哪个分区（Partition）。

* Producer（生产者）：调用 sendProducerRecord() 方法，创建 Kafka 消息。
* Interceptor（拦截器）：可以在消息发送前修改消息（如打日志、流量控制等）。
* Serializer（序列化器）：将消息 Key/Value 转换成二进制格式，以便 Kafka 传输和存储。
* **Partitioner（分区器）：决定消息应该 存储在哪个分区，分区策略包括：**

&#x20;          • 指定分区

&#x20;          • Key 哈希取模

&#x20;          • 轮询（RoundRobin）

\
完成这部分后，Kafka 生产者会将消息封装为 ProducerRecord，准备发送。

## 2.生产者累积消息（RecordAccumulator）

* RecordAccumulator 是一个缓冲区，用于批量发送消息，提高吞吐量。
* 生产者会 暂存消息 在 多个 Queue（队列） 中，并等待批量发送。&#x20;

📌 Kafka 采用”批量提交 + 异步 IO” 机制，提升吞吐量。

## 3.发送线程（Sender 线程）

• 生产者的 Sender 线程 负责将消息 真正发送 到 Kafka Broker：

1\. Sender 线程 从 RecordAccumulator 获取批量消息。

2\. 创建 Request 请求。

3\. NetworkClient 负责网络通信。

4\. Selector 组件 负责管理 多个 TCP 连接 并发送数据。



📌 Kafka 采用 NIO（Netty）+ Selector 进行高效网络 IO 处理。

## 4.Kafka Broker 处理消息

* Kafka Broker 接收 Producer 发送的消息，并存储到对应 分区（Partition）。
* 分区的 Leader 负责写入数据，Follower 负责 复制数据（Replication），保证数据可靠性。
* 数据存储 采用 PageCache + Zero-Copy 零拷贝，提升吞吐量。

📌 Kafka 采用顺序写 + PageCache + 零拷贝 提高吞吐量。

## 5.生产者接收 ACK 确认

Kafka Broker 写入数据后，会根据 acks 机制返回确认：

* acks=0：不等待确认（高吞吐，可能丢数据）
* acks=1：Leader 存储成功即返回（可能丢数据）
* acks=all：所有副本存储成功才返回（最高可靠性）

📌 Kafka 生产者可以设置 acks=all 确保数据不丢失。

## 6.总结

* Kafka 生产者采用拦截器、序列化器、分区器 进行消息处理。
* RecordAccumulator 负责 批量存储，提高吞吐量。
* Sender 线程异步发送，通过 Netty + Selector 进行网络通信。
* Kafka Broker Leader 负责数据写入，Follower 负责复制，保证可靠性。
* 最终 Kafka Broker 返回 ACK，生产者确认消息是否成功。

🚀 Kafka 生产者采用”批量发送 + 零拷贝 + 顺序写”，保证了 高吞吐、低延迟 的消息发送能力！
