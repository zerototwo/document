# Kafka消费者消费堆积且频繁rebalance

```sh
告警名称：Kafka-topic consume exception
识别号：xxxxx
状态：firing 
开始时间：2023-08-09 19:28:05
当前时间：2023-08-09 19:28:05
Summary：Kafka Cluster: common-xxxx-xx Topic: { xxxxxxx-prod } Group:xxxxxxx-prod Status: STALL
Description： 诊断报告

```

## Kafka 消费分区的报警状态枚举

| **状态**          | **描述**                               | **可能原因**                                                           | **应对方案**                                                                                    |
| --------------- | ------------------------------------ | ------------------------------------------------------------------ | ------------------------------------------------------------------------------------------- |
| **1. NotFound** | `consumer group` 不存在                 | <p>- Consumer Group 没有注册到 Kafka<br>- 可能是新建 Group 但还没消费过数据</p>      | <p>- 确保 Consumer Group 正确启动<br>- 运行 <code>kafka-consumer-groups.sh --list</code> 检查</p>     |
| **2. OK**       | 正常消费                                 | - 消费者正常消费，Lag 处于合理范围内                                              | - 维持现有状态，定期监控                                                                               |
| **3. Warning**  | 分区消费延迟，Lag 持续增加                      | <p>- 消费者处理速度赶不上生产者<br>- 业务处理过慢，数据库或外部 API 阻塞</p>                   | <p>- 增加 <code>max.poll.records</code><br>- 添加消费者实例，提高消费吞吐</p>                               |
| **4. Error**    | 一个或多个分区进入 `STOP`、`STALL`、`Rewind` 状态 | - 可能是消费者超时导致 Rebalance 频繁发生                                        | <p>- 调整 <code>max.poll.interval.ms</code><br>- 避免高频 Rebalance</p>                           |
| **5. Stop**     | 长时间未提交 Offset，消费滞后                   | <p>- 业务逻辑阻塞，处理能力不足<br>- <code>auto.commit=false</code> 且未手动提交</p>  | <p>- <strong>优化消费逻辑</strong>，减少单条处理时间<br>- 适当 <strong>手动提交 Offset</strong></p>              |
| **6. Stall**    | Offset 提交失败，Lag 不减少                  | <p>- Offset 频繁提交但消费停滞<br>- 可能是 <code>batch commit</code> 处理不完整</p> | <p>- 增加 <code>max.poll.interval.ms</code> 避免误判<br>- 通过调整 <strong>批处理大小</strong> 避免长时间阻塞</p> |
| **7. Rewind**   | 提交了比之前更早的 Offset                     | - 消费者重置了 Offset（可能是 `auto.offset.reset=earliest`）                  | - 检查 Offset 重置策略，避免重复消费                                                                     |

***



## 原因

配置举例： max.poll.records = 500，而 max.poll.interval.ms = 1000，也就是说consumer一次最多拉取 20 条消息，两次拉取的最长时间间隔为 1 秒。也就是说消费者拉取的20条消息必须在1秒内处理完成，紧接着拉取下一批消息。否则，超过1秒后，kafka broker会认为该消费者处理太缓慢而将他踢出消费组，从而导致消费组rebalance。根据kafka机制，消费组rebalance过程中是不会消费消息的。所以看到三台机器轮流拉取消息，又轮流被踢出消费组，消费组循环进行rebalance，消费就堆积了&#x20;



### 问题解决



