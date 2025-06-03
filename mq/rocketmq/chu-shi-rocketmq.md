---
cover: >-
  https://images.unsplash.com/photo-1735644274639-2cfbe17fd270?crop=entropy&cs=srgb&fm=jpg&ixid=M3wxOTcwMjR8MHwxfHJhbmRvbXx8fHx8fHx8fDE3NDAyNDMzNTB8&ixlib=rb-4.0.3&q=85
coverY: 0
---

# 初识RocketMQ

发布-订阅（Pub/Sub）是一种消息范式，消息的发送者（称为发布者、生产者、Producer）会将消息直接发送给特定的接收者（称为订阅者、消费者、Consumer）。而RocketMQ的基础消息模型就是一个简单的Pub/Sub模型。



## 1.RocketMQ的基础消息模型，一个简单的Pub/Sub模型 <a href="#rocketmq-de-ji-chu-xiao-xi-mo-xing-yi-ge-jian-dan-de-pubsub-mo-xing" id="rocketmq-de-ji-chu-xiao-xi-mo-xing-yi-ge-jian-dan-de-pubsub-mo-xing"></a>

<figure><img src="../../.gitbook/assets/image (1).png" alt=""><figcaption></figcaption></figure>

在**基于主题**的系统中，消息被发布到主题或命名通道上。消费者将收到其订阅主题上的所有消息，生产者负责定义订阅者所订阅的消息类别。这是一个基础的概念模型，而在实际的应用中，结构会更复杂。例如为了支持高并发和水平扩展，中间的消息主题需要进行分区，同一个Topic会有多个生产者，同一个信息会有多个消费者，消费者之间要进行负载均衡等。

## 2.RocketMQ 扩展后的消息模型 <a href="#rocketmq-kuo-zhan-hou-de-xiao-xi-mo-xing" id="rocketmq-kuo-zhan-hou-de-xiao-xi-mo-xing"></a>

<figure><img src="../../.gitbook/assets/image (1) (1).png" alt=""><figcaption></figcaption></figure>

## 3.RocketMQ的部署模型

\
Producer、Consumer又是如何找到Topic和Broker的地址呢？消息的具体发送和接收又是怎么进行的呢？

\


<figure><img src="../../.gitbook/assets/image (2).png" alt=""><figcaption></figcaption></figure>

### 3.1生产者 Producer

发布消息的角色。Producer通过 MQ 的负载均衡模块选择相应的 Broker 集群队列进行消息投递，投递的过程支持快速失败和重试。



### **3.2消费者 Consumer**

消息消费的角色

* 支持以推（push），拉（pull）两种模式对消息进行消费。
* 同时也支持**集群方式**和广播方式的消费。
* 提供实时消息订阅机制，可以满足大多数用户的需求。

### 3.3名字服务器 **NameServer**

NameServer是一个简单的 Topic 路由注册中心，支持 Topic、Broker 的动态注册与发现。

主要包括两个功能

* **Broker管理**，NameServer接受Broker集群的注册信息并且保存下来作为路由信息的基本数据。然后提供心跳检测机制，检查Broker是否还存活；
* **路由信息管理**，每个NameServer将保存关于 Broker 集群的整个路由信息和用于客户端查询的队列信息。Producer和Consumer通过NameServer就可以知道整个Broker集群的路由信息，从而进行消息的投递和消费。

NameServer通常会有多个实例部署，各实例间相互不进行信息通讯。Broker是向每一台NameServer注册自己的路由信息，所以每一个NameServer实例上面都保存一份完整的路由信息。当某个NameServer因某种原因下线了，客户端仍然可以向其它NameServer获取路由信息。

### 3.4代理服务器 Broker

Broker主要负责消息的存储、投递和查询以及服务高可用保证。

NameServer几乎无状态节点，因此可集群部署，节点之间无任何信息同步。Broker部署相对复杂。

在 Master-Slave 架构中，Broker 分为 Master 与 Slave。一个Master可以对应多个Slave，但是一个Slave只能对应一个Master。Master 与 Slave 的对应关系通过指定相同的BrokerName，不同的BrokerId 来定义，BrokerId为0表示Master，非0表示Slave。Master也可以部署多个





