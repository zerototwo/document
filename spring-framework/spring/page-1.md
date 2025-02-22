---
description: >-
  以下是 Spring @Transactional 事务失效的所有场景，分为 代码级别、代理机制、异常处理、事务传播、事务隔离级别、事务管理器、Spring
  Bean 管理 7 类，并提供解决方案。
cover: >-
  https://images.unsplash.com/photo-1739469600176-b58ebd9b9404?crop=entropy&cs=srgb&fm=jpg&ixid=M3wxOTcwMjR8MHwxfHJhbmRvbXx8fHx8fHx8fDE3NDAyMjU4OTl8&ixlib=rb-4.0.3&q=85
coverY: 0
---

# Spring @Transactional 事务失效的所有场景

## 1. 代码级别（方法修饰符 & 可代理性问题）

| 失效场景                 | 原因                           | 解决方案                                     |
| -------------------- | ---------------------------- | ---------------------------------------- |
| private/protected 方法 | Spring 代理只能作用于 public 方法     | 改为 public 方法                             |
| final 方法             | Spring 代理不能代理 final 方法       | 移除 final 关键字                             |
| static 方法            | static 方法属于类级别，Spring 代理无法拦截 | 改为实例方法，不使用 static                        |
| final 类              | CGLIB 代理不能代理 final 类         | 去掉 final 关键字，或开启 proxyTargetClass = true |

2\. 代理机制（AOP 代理 & 代理方式导致事务失效）

| 失效场景                       | 原因                                        | 解决方案                                         |
| -------------------------- | ----------------------------------------- | -------------------------------------------- |
| 同类方法调用（this.method()）      | 绕过 AOP 代理，Spring 无法拦截事务                   | 使用 AopContext.currentProxy() 访问代理对象          |
| @Transactional 作用于 final 类 | JDK 代理模式需要接口，CGLIB 不能代理 final 类           | 去掉 final，或 proxyTargetClass = true           |
| 手动创建对象 new Class()         | Spring 事务管理的是 Spring Bean，手动创建的对象不在 IoC 中 | 使用 @Autowired 或 ApplicationContext#getBean() |

## 3. 异常处理（异常捕获 & 事务回滚问题）

| 失效场景                     | 原因                                               | 解决方案                                                                      |
| ------------------------ | ------------------------------------------------ | ------------------------------------------------------------------------- |
| try-catch 吃掉异常           | Spring 只回滚 RuntimeException，CheckedException 不回滚 | @Transactional(rollbackFor = Exception.class)                             |
| @Transactional 方法被 catch | 异常被外部 catch，Spring 认为方法正常结束，不会回滚                 | 使用 TransactionAspectSupport.currentTransactionStatus().setRollbackOnly(); |
| 异步方法 @Async              | @Async 使事务运行在不同线程，Spring 事务失效                    | 异步方法内部使用 @Transactional，或改用 TransactionTemplate                           |

## 4. 事务传播机制导致的失效

| 失效场景                        | 原因                | 解决方案                          |
| --------------------------- | ----------------- | ----------------------------- |
| PROPAGATION\_NOT\_SUPPORTED | 以非事务方式运行，导致事务不会生效 | 改用 PROPAGATION\_REQUIRED      |
| PROPAGATION\_NESTED         | 嵌套事务，父事务异常时不回滚子事务 | 改用 PROPAGATION\_REQUIRES\_NEW |

## 5. 事务隔离级别导致的失效

| 失效场景                | 原因                                  | 解决方案                                            |
| ------------------- | ----------------------------------- | ----------------------------------------------- |
| 数据库不支持 SERIALIZABLE | 部分数据库（如 MySQL）不支持 Serializable 隔离级别 | 改用 Isolation.READ\_COMMITTED 或 REPEATABLE\_READ |

## 6. 事务管理器问题

| 失效场景     | 原因                                                                | 解决方案                                          |
| -------- | ----------------------------------------------------------------- | --------------------------------------------- |
| 事务管理器不匹配 | JPA 需要 JpaTransactionManager，JDBC 需要 DataSourceTransactionManager | 确保 @Transactional(transactionManager = "xxx") |

## 7. 事务未被 Spring 管理

| 失效场景                           | 原因                             | 解决方案                                           |
| ------------------------------ | ------------------------------ | ---------------------------------------------- |
| @Transactional 用于非 Spring Bean | 方法未被 Spring 托管，无法启用事务          | 使用 @Service 或手动注册 ApplicationContext#getBean() |
| @Transactional 用于 main() 方法    | main() 由 JVM 直接调用，不受 Spring 代理 | 在 @Service 中调用 @Transactional 方法               |

✅ 事务生效的最佳实践

• 方法必须 public，确保 Spring 能代理事务。

• 异常必须是 RuntimeException 或 显式指定 rollbackFor = Exception.class。

• 避免 try-catch 吃掉异常，否则事务不会回滚。

• 使用 @Autowired 调用 @Transactional 方法，避免 this.method() 失效。

• 事务管理器必须匹配（如 JPA 使用 JpaTransactionManager）。

\
