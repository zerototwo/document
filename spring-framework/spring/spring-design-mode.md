# Spring Design mode

Spring 框架中的设计模式及应用

| 设计模式                                   | Spring 中的应用                                  | 源码示例                                                                             |
| -------------------------------------- | -------------------------------------------- | -------------------------------------------------------------------------------- |
| 工厂模式（Factory Pattern）                  | BeanFactory、ApplicationContext               | context.getBean("beanName")                                                      |
| 单例模式（Singleton Pattern）                | Spring Bean 默认是单例                            | DefaultSingletonBeanRegistry                                                     |
| 代理模式（Proxy Pattern）                    | AOP（JdkDynamicAopProxy、CglibAopProxy）        | @Aspect、@Transactional                                                           |
| 模板方法模式（Template Method Pattern）        | JdbcTemplate、RestTemplate                    | execute(ConnectionCallback\<T> action)                                           |
| 观察者模式（Observer Pattern）                | 事件驱动模型（ApplicationEvent、ApplicationListener） | eventPublisher.publishEvent(event)                                               |
| 装饰器模式（Decorator Pattern）               | BeanPostProcessor、TransactionInterceptor     | invoke(MethodInvocation invocation)                                              |
| 策略模式（Strategy Pattern）                 | TransactionManager、Resource                  | strategy.execute()                                                               |
| 责任链模式（Chain of Responsibility Pattern） | FilterChain、Spring Security                  | doFilter(request, response)                                                      |
| 适配器模式（Adapter Pattern）                 | HandlerAdapter、ViewResolver                  | handle(HttpServletRequest request, HttpServletResponse response, Object handler) |
| 建造者模式（Builder Pattern）                 | BeanDefinitionBuilder                        | BeanDefinitionBuilder.rootBeanDefinition(MyBean.class)                           |
| 原型模式（Prototype Pattern）                | @Scope("prototype")                          | context.getBean("beanName")（非单例）                                                 |
| MVC 模式（MVC Pattern）                    | Spring MVC                                   | @Controller、@RequestMapping                                                      |
| 依赖注入（Dependency Injection, DI）         | @Autowired、@Bean                             | @Autowired private UserService userService;                                      |

