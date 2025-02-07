---
description: transient 关键字是 Java 序列化机制中的修饰符，用于标记不需要序列化的字段。
cover: >-
  https://images.unsplash.com/photo-1736251513671-3175c0896fb0?crop=entropy&cs=srgb&fm=jpg&ixid=M3wxOTcwMjR8MHwxfHJhbmRvbXx8fHx8fHx8fDE3Mzg5MzMyMDB8&ixlib=rb-4.0.3&q=85
coverY: 0
---

# Java transient

## 1.transient 的作用

* 当对象被序列化（ObjectOutputStream.writeObject()）时，transient 修饰的字段不会被写入文件或网络传输。
* 反序列化（ObjectInputStream.readObject()）后，transient 字段的值会变成默认值（null、0 或 false）。

## 2.transient 代码示例

```java
import java.io.*;

class Person implements Serializable {
    private static final long serialVersionUID = 1L;

    String name;
    transient int age;  // 这个字段不会被序列化

    public Person(String name, int age) {
        this.name = name;
        this.age = age;
    }
}

public class TransientExample {
    public static void main(String[] args) throws Exception {
        Person person = new Person("Alice", 30);

        // 序列化
        ObjectOutputStream oos = new ObjectOutputStream(new FileOutputStream("person.ser"));
        oos.writeObject(person);
        oos.close();

        // 反序列化
        ObjectInputStream ois = new ObjectInputStream(new FileInputStream("person.ser"));
        Person deserializedPerson = (Person) ois.readObject();
        ois.close();

        System.out.println("Name: " + deserializedPerson.name); // Alice
        System.out.println("Age: " + deserializedPerson.age);  // 0（默认值）
    }
}
```

📌 输出

```sh
Name: Alice
Age: 0  // `transient` 使 `age` 不被序列化，反序列化后变为默认值
```

📌 总结：transient 关键字使 age 不会被写入文件，反序列化时 age 变成默认值 0。

## 3.transient 使用场景

### 📌 `transient` 关键字的使用场景

| **场景**      | **为什么用 `transient`？**                                     |
| ----------- | --------------------------------------------------------- |
| **密码/敏感数据** | 防止密码明文存储，如 `password`，避免序列化到磁盘。                           |
| **计算字段**    | 如 `hashCode` 或 `cache`，可以在 `transient` 字段中缓存，但不需要序列化。     |
| **数据库连接**   | `Connection`、`ThreadLocal`、`Socket` 不能被序列化，否则反序列化后无法恢复。   |
| **日志记录器**   | `Logger` 对象通常标记为 `transient`，因为它不需要序列化。                   |
| **线程相关字段**  | `ThreadLocal` 或 `ExecutorService` 不能被序列化，应标记 `transient`。 |

#### **`transient` 保护密码**

```java
class User implements Serializable {
    String username;
    transient String password;  // 保护密码不被序列化

    public User(String username, String password) {
        this.username = username;
        this.password = password;
    }
}
```

## 4. `transient` vs `static` 对比

| **关键字**     | **是否可序列化？**  | **作用范围** | **特点**                                          |
| ----------- | ------------ | -------- | ----------------------------------------------- |
| `transient` | ❌ **不会被序列化** | **对象级别** | **用于防止某个字段被序列化，反序列化后字段值变为默认值（`null/0/false`）**。 |
| `static`    | ❌ **不会被序列化** | **类级别**  | **`static` 变量属于类，而不属于对象，序列化和反序列化后仍然保留最新的静态值**。  |

#### **✅ 示例 1：`transient` vs `static`**

```java
import java.io.*;

class Example implements Serializable {
    static int staticVar = 100;
    transient int transientVar = 200;
}

public class TransientVsStatic {
    public static void main(String[] args) throws IOException, ClassNotFoundException {
        Example obj = new Example();

        // 序列化
        ObjectOutputStream oos = new ObjectOutputStream(new FileOutputStream("data.ser"));
        oos.writeObject(obj);
        oos.close();

        // 修改静态变量值（影响整个类）
        Example.staticVar = 300;

        // 反序列化
        ObjectInputStream ois = new ObjectInputStream(new FileInputStream("data.ser"));
        Example deserializedObj = (Example) ois.readObject();
        ois.close();

        System.out.println("StaticVar: " + Example.staticVar);       // 300 （不会受序列化影响）
        System.out.println("TransientVar: " + deserializedObj.transientVar); // 0 （transient 变量不会被保存）
    }
}
```

📌 静态变量不会被序列化，但因为属于类变量，反序列化后仍然保留最新的静态值。

## 5.总结

### 📌 `transient` 关键字总结

| **问题**                          | **结论**                            |
| ------------------------------- | --------------------------------- |
| **`transient` 用于什么？**           | **防止字段被序列化（敏感数据、缓存等）**            |
| **`transient` 的值会丢失吗？**         | ✅ **是的，反序列化后变为默认值（null/0/false）** |
| **`transient` 可用于 `static` 吗？** | ❌ **无意义，`static` 本来就不会被序列化**      |
| **什么时候用 `transient`？**          | ✅ **敏感信息（密码）、计算属性、数据库连接等**        |

📌 **`transient` 适用于** **防止敏感数据存入磁盘**，但反序列化后**字段值会丢失**，需要手动恢复！
