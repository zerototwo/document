---
cover: >-
  https://images.unsplash.com/photo-1748360434564-f425c0f2668d?crop=entropy&cs=srgb&fm=jpg&ixid=M3wxOTcwMjR8MHwxfHJhbmRvbXx8fHx8fHx8fDE3NDg5MzMzMzh8&ixlib=rb-4.1.0&q=85
coverY: 0
---

# Disruptor为什么那么快？

1、定长数组/预加载

2、CAS替代锁竞争，单线程无锁化

3、Cache Padding 解决多线程cache Line 命中率,通过空间来换时间

4、内存屏障，通过添加写屏障，避免多生产重复更新序号，多消费重复消费覆盖同一个entry.尽管没有锁，但是导致编译器和Cpu不能指令重排序，不能高效利用CPU，另外缓存刷新也有少许开销。但是可以通过批量出来降低序列号读写频率。
