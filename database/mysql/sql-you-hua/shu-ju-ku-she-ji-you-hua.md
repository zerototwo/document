---
description: 数据库设计优化对 SQL 性能至关重要。良好的数据库设计能够减少冗余、提高查询速度、优化存储效率，避免不必要的锁等待和性能瓶颈。
cover: >-
  https://images.unsplash.com/photo-1735627062325-c978986b1871?crop=entropy&cs=srgb&fm=jpg&ixid=M3wxOTcwMjR8MHwxfHJhbmRvbXx8fHx8fHx8fDE3Mzk0NTUzNDV8&ixlib=rb-4.0.3&q=85
coverY: 0
---

# 数据库设计优化

## 1.规范化 vs. 反规范化

### (1) 规范化

目标：减少数据冗余，避免数据不一致，提高更新效率。

* 第一范式 (1NF)：所有列必须是原子性的（不可再拆分）。
* 第二范式 (2NF)：消除部分依赖，每个非主键列都完全依赖主键。
* 第三范式 (3NF)：消除传递依赖，非主键列不能依赖其他非主键列。

✅ 示例（非规范化 → 规范化）

```sql
-- 非规范化表：存储冗余信息（课程名、教师名）
CREATE TABLE student_course (
    student_id INT,
    student_name VARCHAR(100),
    course_name VARCHAR(100),
    teacher_name VARCHAR(100),
    PRIMARY KEY (student_id, course_name)
);

-- 规范化后的表结构
CREATE TABLE students (
    student_id INT PRIMARY KEY,
    student_name VARCHAR(100)
);

CREATE TABLE courses (
    course_id INT PRIMARY KEY,
    course_name VARCHAR(100),
    teacher_id INT,
    FOREIGN KEY (teacher_id) REFERENCES teachers(teacher_id)
);

CREATE TABLE student_course (
    student_id INT,
    course_id INT,
    PRIMARY KEY (student_id, course_id),
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    FOREIGN KEY (course_id) REFERENCES courses(course_id)
);
```

### (2) 反规范化

目标：提高查询性能，减少表连接（JOIN）带来的开销，适用于 高并发读多写少 的业务场景。

✅ 示例

```sql
-- 反规范化：冗余存储学生和教师信息，避免 JOIN
CREATE TABLE student_course (
    student_id INT,
    student_name VARCHAR(100),
    course_id INT,
    course_name VARCHAR(100),
    teacher_name VARCHAR(100),
    PRIMARY KEY (student_id, course_id)
);
```

应用场景：

* 高并发查询场景，例如电商订单、日志存储等，减少 JOIN 操作带来的查询开销。
* 需要优化 读性能 而非存储占用。

