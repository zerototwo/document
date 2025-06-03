---
cover: >-
  https://images.unsplash.com/photo-1748283052403-72ffdbfea80b?crop=entropy&cs=srgb&fm=jpg&ixid=M3wxOTcwMjR8MHwxfHJhbmRvbXx8fHx8fHx8fDE3NDg5MzE0OTN8&ixlib=rb-4.1.0&q=85
coverY: 0
---

# Http2

HTTP/2 是 HTTP 协议的第二个主版本，是对 HTTP/1.1 的一次重要升级。它主要由 Google 的 SPDY 协议发展而来，于 2015 年作为 RFC 7540 标准正式发布。HTTP/2 设计目标是提高 web 性能、减少延迟，解决 HTTP/1.x 协议中的一些瓶颈问题。

\


下面是 HTTP/2 的核心内容及其与 HTTP/1.1 的主要区别：

***

### 1.&#x20;

### 二进制分帧（Binary Framing Layer）

* HTTP/2 使用二进制格式传输数据，而不是 HTTP/1.1 的纯文本。
* 所有通信都被分割成更小的帧（Frame），每个帧属于一个流（Stream）。

***

### 2.&#x20;

### 多路复用（Multiplexing）

* 在同一个 TCP 连接上，可以并发发送多个请求和响应，不再像 HTTP/1.1 那样“队头阻塞”（Head-of-Line Blocking）。
* 多个流的数据帧可以交错发送，接收端可以根据帧中的 stream id 组装数据。

***

### 3.&#x20;

### 首部压缩（Header Compression）

* HTTP/2 使用 HPACK 算法对头部进行高效压缩，大幅减少冗余信息，提升传输效率。
* 这对携带大量 Cookie 或重复头的请求尤其有帮助。

***

### 4.&#x20;

### 服务端推送（Server Push）

* 服务器可以主动推送资源（如 CSS、JS、图片）到客户端，无需等待客户端请求。
* 典型场景：HTML 页面响应时服务器就推送相关静态资源。

***

### 5.&#x20;

### 流量控制（Flow Control）

* 对每个流和整个连接都可以进行流量控制，防止某个流占用所有带宽。

***

### 6.&#x20;

### 优先级和依赖（Prioritization & Dependency）

* 客户端可以为每个流分配优先级，帮助服务器更智能地分配资源。

***

### 7.&#x20;

### 连接复用

* 理论上只需要一个 TCP 连接就能支持所有请求和响应，极大减少握手、延迟和端口资源消耗。

***

### 与 HTTP/1.1 对比

| 特性     | HTTP/1.1   | HTTP/2      |
| ------ | ---------- | ----------- |
| 数据格式   | 纯文本        | 二进制分帧       |
| 并发处理   | 单一请求阻塞后续请求 | 多路复用，不阻塞    |
| 首部压缩   | 无，头部冗余严重   | HPACK 高效压缩  |
| 连接复用   | 连接数有限/无复用  | 连接复用（理想单连接） |
| 服务端推送  | 不支持        | 支持          |
| 优先级与依赖 | 不支持        | 支持          |

***

### 场景图示（简单）

```
sequenceDiagram
Client->>Server: 请求 index.html
Server-->>Client: index.html
Server-->>Client: (Push) style.css
Server-->>Client: (Push) script.js
Client->>Server: 请求其他资源（与上面推送的可重叠）
```

***

### HTTP/2 在实际开发中的优势

* 网页加载速度更快（尤其资源多的页面）
* 移动端网络环境改善明显（弱网下减少连接数与重传）
* 降低服务器连接压力
* 改善长连接、大量数据传输的业务

***

### 常见问题

1. 需要更换 URL/协议吗？
   * 不需要，还是用 http(s)://，浏览器和服务端协商升级。
2. 所有主流浏览器和 Web 服务器都支持吗？
   * 现代浏览器（Chrome、Firefox、Safari、Edge 等）和主流服务器（nginx、Apache、Node.js 等）都支持。
3. 需要考虑安全性吗？
   * 浏览器一般只在 HTTPS 下启用 HTTP/2，提升了安全性。

***

