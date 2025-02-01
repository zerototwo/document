# Difference between String, StringBuilder and StringBuffer?

\# Difference between String, StringBuilder and StringBuffer

\

In Java, \`String\`, \`StringBuilder\` and \`StringBuffer\` are all used to process strings, but they differ in \*\*mutability\*\*, \*\*thread safety\*\* and \*\*performance\*\*.

\

\---

\

\## 1. \`String\` (immutable string)

\

\### \*\*Features\*\*

\- \`String\` is \*\*immutable\*\*, and the string cannot be modified once it is created.

\- Every time a \`String\` is modified (such as concatenation or replacement), a new \`String\` object will be generated. The original object still exists, which may increase \*\*memory consumption\*\* and \*\*performance overhead\*\*.

\

\### \*\*Example\*\*

\`\`\`java

String str = "Hello";

str = str + " World"; // Generate a new string object

System.out.println(str); // Output: Hello World

\

Applicable scenarios

• Need to store immutable data, such as constant strings.

• Thread-safe, no additional synchronization required.

\

2\. StringBuilder (mutable string, non-thread-safe)

\

Features

• StringBuilder is mutable. Each modification does not create a new object, but modifies the original object to improve performance.

• Not thread-safe, but fast, suitable for single-threaded environments.

\

Example

\

StringBuilder sb = new StringBuilder("Hello");

sb.append(" World"); // Modify directly on the original object

System.out.println(sb.toString()); // Output: Hello World

\

Applicable scenarios

• Need to perform a large number of string concatenation or modification, such as loop concatenation (avoid creating too many temporary objects).

• Single-threaded environment, no need to consider concurrency issues.

\

3\. StringBuffer (mutable string, thread-safe)

\

Features

• StringBuffer is also mutable, similar to StringBuilder, but its methods are thread-safe because synchronized is used internally for synchronization.

• Due to the existence of the synchronization mechanism, the performance of StringBuffer is slightly worse than StringBuilder, but it is suitable for multi-threaded environments.

\

Example

\

StringBuffer sb = new StringBuffer("Hello");

sb.append(" World"); // Thread-safe operation

System.out.println(sb.toString()); // Output: Hello World

\

Applicable scenarios

• Multithreaded environment requires safe string modification operations.

• When sharing mutable strings between threads, data consistency needs to be guaranteed.

\

4\. Comparison summary

\

Features String StringBuilder StringBuffer

Mutability ❌ Immutable ✅ Mutable ✅ Mutable

Thread safety ✅ Thread safe ❌ Non-thread safe ✅ Thread safe

Performance ⬇️ Slow (due to creating new objects) ⬆️ Fast (no synchronization overhead) ⬇️ Slower than StringBuilder (synchronization overhead)

Applicable scenarios Applicable to a small number of string operations, immutable data Applicable to single thread, large number of string modifications Applicable to multi-thread, large number of string modifications

\

5\. Best use recommendations

• If the string will not be modified → Use String (such as a constant string).

• If the string will be frequently modified and it is single-threaded → Use StringBuilder.

• If the string will be frequently modified and it is multi-threaded → Use StringBuffer.

\

6\. Example: Performance comparison of concatenating a large number of strings

\

public class StringTest {

&#x20; public static void main(String\[] args) {

&#x20; long startTime, endTime;

&#x20; &#x20;

&#x20; // String test

&#x20; startTime = System.nanoTime();

&#x20; String str = "";

&#x20; for (int i = 0; i < 10000; i++) {

&#x20; str += i; // Generate a large number of temporary objects

&#x20; }

&#x20; endTime = System.nanoTime();

&#x20; System.out.println("String time: " + (endTime - startTime) + " ns");

&#x20; &#x20; &#x20; // StringBuilder test &#x20; startTime = System.nanoTime(); &#x20; StringBuilder sb = new StringBuilder(); &#x20; for (int i = 0; i < 10000; i++) { &#x20; sb.append(i); &#x20; } &#x20; endTime = System.nanoTime(); &#x20; System.out.println("StringBuilder takes time: " + (endTime - startTime) + " ns"); \ &#x20; // StringBuffer test &#x20; startTime = System.nanoTime(); &#x20; StringBuffer sbf = new StringBuffer(); &#x20; for (int i = 0; i < 10000; i++) {

&#x20; sbf.append(i);

&#x20; }

&#x20; endTime = System.nanoTime();

&#x20; System.out.println("StringBuffer time: " + (endTime - startTime) + " ns");

&#x20; }

}

\

Running results (example):

\

String time: 123456789 ns

StringBuilder time: 9876543 ns

StringBuffer time: 13579246 ns

\

From the results, we can see:

• String is the slowest because it constantly creates new objects.

• StringBuilder is the fastest because there is no synchronization mechanism.

• StringBuffer is slower than StringBuilder, but thread-safe.

\

7\. Summary

1\. Need immutable string → String

2\. Need high-performance string concatenation (single-threaded) → StringBuilder

3\. Need thread-safe string operations → StringBuffer

\

The Markdown content formatted in this way is suitable for GitBook, just copy and paste it.