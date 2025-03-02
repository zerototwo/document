---
cover: >-
  https://images.unsplash.com/photo-1727466928916-9789f30de10b?crop=entropy&cs=srgb&fm=jpg&ixid=M3wxOTcwMjR8MHwxfHJhbmRvbXx8fHx8fHx8fDE3NDA5MzM4MTJ8&ixlib=rb-4.0.3&q=85
coverY: 0
---

# RedisMessageListenerContainer 没线程池导致CPU高

```java
public class RedisMessageListenerContainer implements InitializingBean, DisposableBean, BeanNameAware, SmartLifecycle {

	/** Logger available to subclasses */
	protected final Log logger = LogFactory.getLog(getClass());

	/**
	 * Default thread name prefix: "RedisListeningContainer-".
	 */
	public static final String DEFAULT_THREAD_NAME_PREFIX = ClassUtils.getShortName(RedisMessageListenerContainer.class)
			+ "-";

	/**
	 * The default recovery interval: 5000 ms = 5 seconds.
	 */
	public static final long DEFAULT_RECOVERY_INTERVAL = 5000;

	/**
	 * The default subscription wait time: 2000 ms = 2 seconds.
	 */
	public static final long DEFAULT_SUBSCRIPTION_REGISTRATION_WAIT_TIME = 2000L;

	private long initWait = TimeUnit.SECONDS.toMillis(5);

	private @Nullable Executor subscriptionExecutor;

	private @Nullable Executor taskExecutor;

	private @Nullable RedisConnectionFactory connectionFactory;

	private @Nullable String beanName;

	private @Nullable ErrorHandler errorHandler;

	private final Object monitor = new Object();
	// whether the container is running (or not)
	private volatile boolean running = false;
	// whether the container has been initialized
	private volatile boolean initialized = false;
	// whether the container uses a connection or not
	// (as the container might be running but w/o listeners, it won't use any resources)
	private volatile boolean listening = false;

	private volatile boolean manageExecutor = false;

	// lookup maps
	// to avoid creation of hashes for each message, the maps use raw byte arrays (wrapped to respect the equals/hashcode
	// contract)

	// lookup map between patterns and listeners
	private final Map<ByteArrayWrapper, Collection<MessageListener>> patternMapping = new ConcurrentHashMap<>();
	// lookup map between channels and listeners
	private final Map<ByteArrayWrapper, Collection<MessageListener>> channelMapping = new ConcurrentHashMap<>();
	// lookup map between listeners and channels
	private final Map<MessageListener, Set<Topic>> listenerTopics = new ConcurrentHashMap<>();

	private final SubscriptionTask subscriptionTask = new SubscriptionTask();

	private volatile RedisSerializer<String> serializer = RedisSerializer.string();

	private long recoveryInterval = DEFAULT_RECOVERY_INTERVAL;

	private long maxSubscriptionRegistrationWaitingTime = DEFAULT_SUBSCRIPTION_REGISTRATION_WAIT_TIME;

	public void afterPropertiesSet() {
		if (taskExecutor == null) {
			manageExecutor = true;
			taskExecutor = createDefaultTaskExecutor();
		}

		if (subscriptionExecutor == null) {
			subscriptionExecutor = taskExecutor;
		}

		initialized = true;
	}
	
		/**
	 * Creates a default TaskExecutor. Called if no explicit TaskExecutor has been specified.
	 * <p>
	 * The default implementation builds a {@link org.springframework.core.task.SimpleAsyncTaskExecutor} with the
	 * specified bean name (or the class name, if no bean name specified) as thread name prefix.
	 *
	 * @see org.springframework.core.task.SimpleAsyncTaskExecutor#SimpleAsyncTaskExecutor(String)
	 */
	protected TaskExecutor createDefaultTaskExecutor() {
		String threadNamePrefix = (beanName != null ? beanName + "-" : DEFAULT_THREAD_NAME_PREFIX);
		return new SimpleAsyncTaskExecutor(threadNamePrefix);
	}
}	
```

模式使用SimpleAsyncTaskExecutor来处理任务，
