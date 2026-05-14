# 链路追踪原理

可以，面试时你可以把 Java Agent 一起放进链路追踪原理里讲，完整版本如下：

***

### 链路追踪原理 + Java Agent 版

链路追踪的核心原理是：一次请求进入系统时生成一个全局唯一的 TraceId，然后在请求经过的每个服务、每次远程调用、数据库访问、缓存访问、消息发送等操作上创建 Span。

每个 Span 会记录自己的 SpanId、ParentSpanId、TraceId、服务名、接口名、开始时间、结束时间、耗时、状态和异常信息。

最后追踪系统会根据 TraceId 和 ParentSpanId，把分散在不同服务里的 Span 聚合成一棵完整调用树，从而看到一次请求经过了哪些服务、每个服务耗时多少、哪里报错、哪里慢。

***

### Java Agent 在里面起什么作用？

在 Java 系统里，像 SkyWalking、Pinpoint、OpenTelemetry 这类链路追踪工具，通常会通过 Java Agent 实现自动埋点。

Java Agent 本质上是 JVM 提供的一种代理机制。应用启动时通过 `-javaagent` 参数加载 Agent，例如：

```bash
java -javaagent:/opt/skywalking/skywalking-agent.jar -jar app.jar
```

JVM 会在业务 `main` 方法执行之前，先加载 Agent，并执行 Agent 的 `premain` 方法。

Agent 会基于 `java.lang.instrument.Instrumentation` 注册 `ClassFileTransformer`，在 JVM 加载类的时候拦截 class 字节码，然后通过 ByteBuddy、ASM、Javassist 这类字节码增强工具，对目标框架类的方法进行增强。

***

### 字节码增强做了什么？

比如对于 Spring MVC、Feign、Dubbo、JDBC、Redis、Kafka 这些常见组件，Agent 会在它们的关键方法前后自动插入追踪逻辑。

方法执行前创建 Span，方法执行后关闭 Span，发生异常时记录异常信息。如果是远程调用，还会把 Trace 上下文注入到 HTTP Header 或 RPC Metadata 里。

逻辑上类似这样：

```java
public Object invoke() {
    Span span = tracer.createSpan("GET /api/order");
    try {
        return 原始业务方法();
    } catch (Throwable e) {
        span.recordException(e);
        throw e;
    } finally {
        span.end();
    }
}
```

但是它不是改 Java 源码，而是在 JVM 加载 class 的时候修改字节码，所以业务代码基本无侵入。

***

### Trace 上下文怎么传递？

在同一个服务内部，Trace 上下文一般通过 ThreadLocal 保存。

比如当前请求的 TraceId、当前 Span、父 Span 都会放在线程上下文里。这样后续调用 MySQL、Redis、Feign 时，埋点组件就能从 ThreadLocal 中拿到当前上下文，并创建子 Span。

跨服务时：

当 A 服务调用 B 服务时，Agent 会把 TraceId、SpanId 等上下文写入请求头，例如 SkyWalking 的 `sw8` Header，或者 OpenTelemetry 的 `traceparent` Header。

B 服务收到请求后，Agent 会从请求头里解析出 Trace 上下文，然后创建自己的 Span，并和上游 Span 建立父子关系。

跨线程时：

如果使用线程池、CompletableFuture 这类异步任务，由于普通 ThreadLocal 在线程切换后会丢失，所以链路追踪框架会做上下文快照。

提交任务前 capture 当前上下文，执行任务时 restore 上下文，执行结束后 clear 上下文。这样异步任务也能挂到同一条 Trace 上。

***

### 数据怎么上报？

Span 生成以后，一般不会在业务线程里同步上报，因为这样会影响接口性能。

通常是请求结束后生成一段 Trace 数据，放到本地队列里，由 Agent 后台线程异步批量上报到 Collector。

例如 SkyWalking 会把数据上报到 OAP Server，OAP 再负责拓扑分析、指标聚合、Trace 存储，最后由 UI 查询展示。

整体流程可以理解为：

```
用户请求
  ↓
Java Agent 自动创建 EntrySpan
  ↓
业务方法执行
  ↓
调用 Redis / MySQL / Feign / Kafka
  ↓
Agent 自动创建子 Span
  ↓
跨服务时注入 Trace Header
  ↓
下游服务解析 Header 并继续创建 Span
  ↓
请求结束后 Span 异步批量上报
  ↓
后端根据 TraceId + ParentSpanId 聚合成调用树
  ↓
UI 展示完整链路、耗时、异常、拓扑
```

***

### 面试口述版

你可以直接这样说：

链路追踪的核心原理是，一次请求进来时生成一个全局唯一的 TraceId，然后在请求经过的每个服务、每次远程调用、数据库访问、缓存访问、消息发送等操作上创建 Span。每个 Span 记录 SpanId、ParentSpanId、TraceId、开始时间、结束时间、耗时、状态、异常等信息。最后追踪系统根据 TraceId 和 ParentSpanId，把分散在各个服务里的 Span 聚合成一棵调用树。

在 Java 体系里，像 SkyWalking 这类工具一般通过 Java Agent 实现无侵入埋点。应用启动时加 `-javaagent` 参数，JVM 会在 main 方法之前加载 Agent。Agent 基于 Instrumentation 机制注册 ClassFileTransformer，在类加载时拦截字节码，然后通过 ByteBuddy 或 ASM 对 Spring MVC、Feign、Dubbo、JDBC、Redis、Kafka 等框架的关键方法做增强。

增强后的效果就是：入口请求创建 EntrySpan，内部方法或中间件调用创建 LocalSpan，远程调用创建 ExitSpan，方法结束关闭 Span，异常时记录异常。跨服务调用时，Agent 会把 Trace 上下文注入到请求头，比如 SkyWalking 的 sw8，下游服务再解析这个 Header，继续创建自己的 Span。

在服务内部，Trace 上下文一般通过 ThreadLocal 传递；如果涉及线程池或异步任务，会通过上下文快照 capture 和 restore 来解决跨线程 Trace 丢失的问题。

最后，Agent 会把生成的 Span 或 Segment 放到本地队列，由后台线程异步批量上报到后端，比如 SkyWalking OAP。OAP 再做调用关系聚合、服务拓扑分析、耗时和错误率统计，最终在 UI 上展示完整调用链。

所以总结来说，Java 链路追踪就是：Java Agent 字节码增强自动埋点，ThreadLocal 管理进程内上下文，Header 传递跨服务上下文，异步上报 Span 数据，后端根据 TraceId 和 ParentSpanId 聚合成完整调用树。

***

### 精简版

链路追踪就是通过 Java Agent 对框架关键方法做字节码增强，自动创建 Span；通过 ThreadLocal 在进程内传递 Trace 上下文，通过 Header 在服务间传递 TraceId；最后由 Agent 异步上报到后端，后端根据 TraceId 和 ParentSpanId 聚合成完整调用链。
