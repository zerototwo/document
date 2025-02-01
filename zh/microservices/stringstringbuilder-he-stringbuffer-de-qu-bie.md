# String、StringBuilder 和 StringBuffer 的区别？

\# String、StringBuilder 和 StringBuffer 的区别

\


在 Java 中，\`String\`、\`StringBuilder\` 和 \`StringBuffer\` 都用于处理字符串，但它们在 \*\*可变性\*\*、\*\*线程安全性\*\* 和 \*\*性能\*\* 方面有所不同。

\


\---

\


\## 1. \`String\`（不可变字符串）

\


\### \*\*特点\*\*

\- \`String\` 是 \*\*不可变\*\*（immutable）的，字符串一旦创建就不能修改。

\- 每次对 \`String\` 进行修改（如拼接、替换）都会生成新的 \`String\` 对象，原对象仍然存在，可能会增加 \*\*内存消耗\*\* 和 \*\*性能开销\*\*。

\


\### \*\*示例\*\*

\`\`\`java

String str = "Hello";

str = str + " World"; // 产生新的字符串对象

System.out.println(str); // 输出: Hello World

\


适用场景

• 需要存储 不可变 数据，如 常量字符串。

• 线程安全，不需要额外同步处理。

\


2\. StringBuilder（可变字符串，非线程安全）

\


特点

• StringBuilder 是 可变（mutable）的，每次修改时不会创建新的对象，而是在原对象上修改，提高性能。

• 非线程安全，但速度快，适用于 单线程环境。

\


示例

\


StringBuilder sb = new StringBuilder("Hello");

sb.append(" World"); // 直接在原对象上修改

System.out.println(sb.toString()); // 输出: Hello World

\


适用场景

• 需要进行 大量字符串拼接或修改，如 循环拼接（避免创建过多临时对象）。

• 单线程环境，不需要考虑并发问题。

\


3\. StringBuffer（可变字符串，线程安全）

\


特点

• StringBuffer 也是 可变 的，与 StringBuilder 类似，但它的方法是 线程安全的，因为 内部使用了 synchronized 进行同步。

• 由于同步机制的存在，StringBuffer 的性能比 StringBuilder 稍差，但适用于 多线程环境。

\


示例

\


StringBuffer sb = new StringBuffer("Hello");

sb.append(" World"); // 线程安全的操作

System.out.println(sb.toString()); // 输出: Hello World

\


适用场景

• 多线程环境 需要安全的字符串修改操作。

• 线程间共享 可变字符串 时，需要保证数据一致性。

\


4\. 对比总结

\


特性 String StringBuilder StringBuffer

可变性 ❌ 不可变 ✅ 可变 ✅ 可变

线程安全性 ✅ 线程安全 ❌ 非线程安全 ✅ 线程安全

性能 ⬇️ 慢（因创建新对象） ⬆️ 快（无同步开销） ⬇️ 比 StringBuilder 慢（同步开销）

适用场景 适用于少量字符串操作、不可变数据 适用于单线程、大量字符串修改 适用于多线程、大量字符串修改

\


5\. 最佳使用建议

• 如果字符串不会被修改 → 使用 String（如常量字符串）。

• 如果字符串会被频繁修改，并且是单线程 → 使用 StringBuilder。

• 如果字符串会被频繁修改，并且是多线程 → 使用 StringBuffer。

\


6\. 示例：大量字符串拼接的性能对比

\


public class StringTest {

&#x20;   public static void main(String\[] args) {

&#x20;       long startTime, endTime;

&#x20;      &#x20;

&#x20;       // String 测试

&#x20;       startTime = System.nanoTime();

&#x20;       String str = "";

&#x20;       for (int i = 0; i < 10000; i++) {

&#x20;           str += i;  // 产生大量临时对象

&#x20;       }

&#x20;       endTime = System.nanoTime();

&#x20;       System.out.println("String 耗时: " + (endTime - startTime) + " ns");

&#x20;      &#x20;

&#x20;       // StringBuilder 测试

&#x20;       startTime = System.nanoTime();

&#x20;       StringBuilder sb = new StringBuilder();

&#x20;       for (int i = 0; i < 10000; i++) {

&#x20;           sb.append(i);

&#x20;       }

&#x20;       endTime = System.nanoTime();

&#x20;       System.out.println("StringBuilder 耗时: " + (endTime - startTime) + " ns");

\


&#x20;       // StringBuffer 测试

&#x20;       startTime = System.nanoTime();

&#x20;       StringBuffer sbf = new StringBuffer();

&#x20;       for (int i = 0; i < 10000; i++) {

&#x20;           sbf.append(i);

&#x20;       }

&#x20;       endTime = System.nanoTime();

&#x20;       System.out.println("StringBuffer 耗时: " + (endTime - startTime) + " ns");

&#x20;   }

}

\


运行结果（示例）：

\


String 耗时: 123456789 ns

StringBuilder 耗时: 9876543 ns

StringBuffer 耗时: 13579246 ns

\


从结果可以看出：

• String 最慢，因为不断创建新对象。

• StringBuilder 最快，因为无同步机制。

• StringBuffer 比 StringBuilder 慢，但线程安全。

\


7\. 总结

1\. 需要不可变字符串 → String

2\. 需要高性能字符串拼接（单线程） → StringBuilder

3\. 需要线程安全的字符串操作 → StringBuffer

\


这样格式化的 Markdown 内容适用于 GitBook，直接复制粘贴即可。
