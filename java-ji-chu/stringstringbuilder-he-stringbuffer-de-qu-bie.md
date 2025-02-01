---
cover: >-
  https://images.unsplash.com/photo-1736444387876-cd5949fc7347?crop=entropy&cs=srgb&fm=jpg&ixid=M3wxOTcwMjR8MHwxfHJhbmRvbXx8fHx8fHx8fDE3Mzg0MjA1MzR8&ixlib=rb-4.0.3&q=85
coverY: 0
---

# ⚽ String、StringBuilder和StringBuffer的区别？

在 Java 中，String、StringBuilder 和 StringBuffer 都是用来处理字符串的，但它们在 可变性、线程安全性 和 性能 方面有显著区别：

## **1. String(不可变)**

• **不可变对象**：String 是不可变的（immutable），一旦创建就无法修改，每次修改都会生成新的字符串对象。

• **存储位置**：String 对象存储在字符串常量池（如果是直接赋值），或者堆内存（如果用 new 创建）。

• **适用场景**：

* 适用于少量字符串拼接或修改的情况。
* 适用于字符串不会发生改变的情况，如常量、配置项等。



**示例：**

```java
String s1 = "Hello";
String s2 = s1 + " World";  // 生成新的字符串对象
System.out.println(s1);  // Hello
System.out.println(s2);  // Hello World// Some code
```

{% hint style="danger" %}
问题：由于 String 不可变，每次修改都会生成新的对象，占用额外的内存并降低效率。
{% endhint %}

## 2.StringBuilder(可变,非线程安全)

• **可变对象**：StringBuilder 是可变的，修改字符串不会创建新对象，而是在原对象上修改，提高了性能。

• **线程不安全**：不支持多线程安全，但性能更高。

• **适用场景**：

* 适用于**单线程环境**，需要频繁修改字符串（如字符串拼接、替换等）。
* 适用于**大批量字符串操作，如循环拼接**。



**示例：**

```java
StringBuilder sb = new StringBuilder("Hello");
sb.append(" World");
System.out.println(sb);  // Hello World
```

**✔ 性能比 String 更高，尤其是多个字符串拼接时不会生成多个对象。**



## 3.StringBuffer(可变，线程安全)



* 可变对象：和 StringBuilder 类似，StringBuffer 也是可变的，修改不会创建新对象。
* 线程安全：方法使用 synchronized 关键字进行同步，因此适用于多线程环境。
* 适用场景：
  * 适用于多线程环境，需要线程安全的字符串操作。
  * 适用于频繁修改字符串且涉及多线程的情况。



**示例：**

```java
StringBuffer sb = new StringBuffer("Hello");
sb.append(" World");
System.out.println(sb);  // Hello World
```

**✔ 线程安全，但比 StringBuilder 性能稍低。**



## 4.总结对比

• 用 String：如果字符串不会改变，或字符串修改次数较少（如常量、日志等）。

• 用 StringBuilder：在单线程环境下，执行大量字符串拼接或修改时（性能更高）。

• 用 StringBuffer：在多线程环境下，执行大量字符串修改时（保证线程安全）。



### **🚀** 最佳实践

在 循环拼接字符串 时，建议使用 StringBuilder，否则 String 会生成大量临时对象，浪费内存。

如果在多线程中操作字符串，使用 StringBuffer 确保线程安全。

```java
// 不推荐：使用 String 在循环拼接字符串
String str = "";
for (int i = 0; i < 10000; i++) {
    str += i; // 产生大量临时对象，性能差
}

// 推荐：使用 StringBuilder
StringBuilder sb = new StringBuilder();
for (int i = 0; i < 10000; i++) {
    sb.append(i);
}
String result = sb.toString();  // 性能高// Some code
```





















