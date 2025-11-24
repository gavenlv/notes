package com.redis.tutorial;

import redis.clients.jedis.Jedis;
import redis.clients.jedis.StreamEntry;
import redis.clients.jedis.StreamEntryID;
import redis.clients.jedis.params.XAddParams;
import redis.clients.jedis.params.XReadParams;
import redis.clients.jedis.params.XReadGroupParams;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.*;
import java.util.concurrent.*;
import java.util.function.Consumer;

/**
 * Redis消息队列实现
 * 支持List队列、Pub/Sub、Stream等模式
 */
public class MessageQueue {
    
    private static final Logger logger = LoggerFactory.getLogger(MessageQueue.class);
    private static final ObjectMapper objectMapper = new ObjectMapper();
    
    private final Jedis jedis;
    
    public MessageQueue(Jedis jedis) {
        this.jedis = jedis;
    }
}

/**
 * List队列实现（简单的FIFO队列）
 */
class ListMessageQueue {
    
    private final Jedis jedis;
    private final String queueName;
    
    public ListMessageQueue(Jedis jedis, String queueName) {
        this.jedis = jedis;
        this.queueName = queueName;
    }
    
    /**
     * 发送消息
     */
    public <T> boolean sendMessage(T message) {
        try {
            String serializedMessage = objectMapper.writeValueAsString(message);
            jedis.rpush(queueName, serializedMessage);
            return true;
        } catch (JsonProcessingException e) {
            logger.error("消息序列化失败: {}", e.getMessage());
            return false;
        }
    }
    
    /**
     * 接收消息（阻塞）
     */
    public <T> T receiveMessage(Class<T> clazz, int timeoutSeconds) {
        List<String> messages = jedis.blpop(timeoutSeconds, queueName);
        
        if (messages != null && messages.size() >= 2) {
            String message = messages.get(1);
            try {
                return objectMapper.readValue(message, clazz);
            } catch (JsonProcessingException e) {
                logger.error("消息反序列化失败: {}", e.getMessage());
                return null;
            }
        }
        
        return null;
    }
    
    /**
     * 批量发送消息
     */
    public <T> boolean batchSendMessages(List<T> messages) {
        try {
            String[] serializedMessages = messages.stream()
                    .map(message -> {
                        try {
                            return objectMapper.writeValueAsString(message);
                        } catch (JsonProcessingException e) {
                            logger.error("消息序列化失败: {}", e.getMessage());
                            return null;
                        }
                    })
                    .filter(Objects::nonNull)
                    .toArray(String[]::new);
            
            if (serializedMessages.length > 0) {
                jedis.rpush(queueName, serializedMessages);
                return true;
            }
            return false;
        } catch (Exception e) {
            logger.error("批量发送消息失败: {}", e.getMessage());
            return false;
        }
    }
}

/**
 * Pub/Sub消息队列实现
 */
class PubSubMessageQueue {
    
    private final Jedis jedis;
    private final String channelName;
    private final ExecutorService executorService;
    
    public PubSubMessageQueue(Jedis jedis, String channelName) {
        this.jedis = jedis;
        this.channelName = channelName;
        this.executorService = Executors.newCachedThreadPool();
    }
    
    /**
     * 发布消息
     */
    public <T> boolean publishMessage(T message) {
        try {
            String serializedMessage = objectMapper.writeValueAsString(message);
            jedis.publish(channelName, serializedMessage);
            return true;
        } catch (JsonProcessingException e) {
            logger.error("消息序列化失败: {}", e.getMessage());
            return false;
        }
    }
    
    /**
     * 订阅消息
     */
    public <T> void subscribeMessage(Class<T> clazz, Consumer<T> messageHandler) {
        executorService.submit(() -> {
            jedis.subscribe(new redis.clients.jedis.JedisPubSub() {
                @Override
                public void onMessage(String channel, String message) {
                    if (channelName.equals(channel)) {
                        try {
                            T deserializedMessage = objectMapper.readValue(message, clazz);
                            messageHandler.accept(deserializedMessage);
                        } catch (JsonProcessingException e) {
                            logger.error("消息反序列化失败: {}", e.getMessage());
                        }
                    }
                }
            }, channelName);
        });
    }
    
    /**
     * 关闭订阅
     */
    public void shutdown() {
        executorService.shutdown();
    }
}

/**
 * Stream消息队列实现（Redis 5.0+）
 */
class StreamMessageQueue {
    
    private final Jedis jedis;
    private final String streamName;
    
    public StreamMessageQueue(Jedis jedis, String streamName) {
        this.jedis = jedis;
        this.streamName = streamName;
    }
    
    /**
     * 发送消息
     */
    public <T> StreamEntryID sendMessage(T message) {
        try {
            String serializedMessage = objectMapper.writeValueAsString(message);
            
            Map<String, String> messageMap = new HashMap<>();
            messageMap.put("data", serializedMessage);
            messageMap.put("timestamp", String.valueOf(System.currentTimeMillis()));
            
            XAddParams params = XAddParams.xAddParams();
            return jedis.xadd(streamName, params, messageMap);
        } catch (JsonProcessingException e) {
            logger.error("消息序列化失败: {}", e.getMessage());
            return null;
        }
    }
    
    /**
     * 读取消息
     */
    public <T> List<T> readMessages(Class<T> clazz, int count) {
        return readMessages(clazz, count, "0");
    }
    
    /**
     * 从指定位置读取消息
     */
    public <T> List<T> readMessages(Class<T> clazz, int count, String startId) {
        Map<String, StreamEntryID> streams = new HashMap<>();
        streams.put(streamName, new StreamEntryID(startId));
        
        XReadParams params = XReadParams.xReadParams().count(count);
        
        List<Map.Entry<String, List<StreamEntry>>> results = 
                jedis.xread(params, streams);
        
        List<T> messages = new ArrayList<>();
        
        for (Map.Entry<String, List<StreamEntry>> result : results) {
            for (StreamEntry entry : result.getValue()) {
                try {
                    String messageData = entry.getFields().get("data");
                    T message = objectMapper.readValue(messageData, clazz);
                    messages.add(message);
                } catch (JsonProcessingException e) {
                    logger.error("消息反序列化失败: {}", e.getMessage());
                }
            }
        }
        
        return messages;
    }
    
    /**
     * 创建消费者组
     */
    public boolean createConsumerGroup(String groupName, String startId) {
        try {
            jedis.xgroupCreate(streamName, groupName, new StreamEntryID(startId), true);
            return true;
        } catch (Exception e) {
            logger.error("创建消费者组失败: {}", e.getMessage());
            return false;
        }
    }
    
    /**
     * 消费者组读取消息
     */
    public <T> List<T> readMessagesByGroup(Class<T> clazz, String groupName, 
                                          String consumerName, int count) {
        Map<String, StreamEntryID> streams = new HashMap<>();
        streams.put(streamName, StreamEntryID.UNRECEIVED_ENTRY);
        
        XReadGroupParams params = XReadGroupParams.xReadGroupParams()
                .count(count)
                .block(5000); // 5秒阻塞
        
        List<Map.Entry<String, List<StreamEntry>>> results = 
                jedis.xreadGroup(groupName, consumerName, params, streams);
        
        List<T> messages = new ArrayList<>();
        
        for (Map.Entry<String, List<StreamEntry>> result : results) {
            for (StreamEntry entry : result.getValue()) {
                try {
                    String messageData = entry.getFields().get("data");
                    T message = objectMapper.readValue(messageData, clazz);
                    messages.add(message);
                    
                    // 确认消息处理
                    jedis.xack(streamName, groupName, entry.getID());
                } catch (JsonProcessingException e) {
                    logger.error("消息反序列化失败: {}", e.getMessage());
                }
            }
        }
        
        return messages;
    }
}

/**
 * 延迟消息队列实现
 */
class DelayedMessageQueue {
    
    private final Jedis jedis;
    private final String queueName;
    private final ScheduledExecutorService scheduler;
    
    public DelayedMessageQueue(Jedis jedis, String queueName) {
        this.jedis = jedis;
        this.queueName = queueName;
        this.scheduler = Executors.newScheduledThreadPool(1);
    }
    
    /**
     * 发送延迟消息
     */
    public <T> boolean sendDelayedMessage(T message, long delay, TimeUnit unit) {
        try {
            String serializedMessage = objectMapper.writeValueAsString(message);
            long delayMillis = unit.toMillis(delay);
            long deliverTime = System.currentTimeMillis() + delayMillis;
            
            // 使用有序集合存储延迟消息
            jedis.zadd(queueName + ":delayed", deliverTime, serializedMessage);
            
            // 调度检查任务
            scheduleDeliveryCheck();
            
            return true;
        } catch (JsonProcessingException e) {
            logger.error("消息序列化失败: {}", e.getMessage());
            return false;
        }
    }
    
    /**
     * 调度消息投递检查
     */
    private void scheduleDeliveryCheck() {
        scheduler.schedule(() -> {
            try {
                checkAndDeliverMessages();
            } catch (Exception e) {
                logger.error("延迟消息投递检查失败: {}", e.getMessage());
            }
        }, 1, TimeUnit.SECONDS);
    }
    
    /**
     * 检查并投递到期消息
     */
    private void checkAndDeliverMessages() {
        long currentTime = System.currentTimeMillis();
        
        // 获取所有到期的消息
        Set<String> expiredMessages = jedis.zrangeByScore(
                queueName + ":delayed", 0, currentTime);
        
        if (!expiredMessages.isEmpty()) {
            // 投递到实际队列
            String[] messagesArray = expiredMessages.toArray(new String[0]);
            jedis.rpush(queueName, messagesArray);
            
            // 从延迟队列中移除
            jedis.zremrangeByScore(queueName + ":delayed", 0, currentTime);
        }
        
        // 继续调度下一次检查
        scheduleDeliveryCheck();
    }
    
    /**
     * 接收消息
     */
    public <T> T receiveMessage(Class<T> clazz, int timeoutSeconds) {
        List<String> messages = jedis.blpop(timeoutSeconds, queueName);
        
        if (messages != null && messages.size() >= 2) {
            String message = messages.get(1);
            try {
                return objectMapper.readValue(message, clazz);
            } catch (JsonProcessingException e) {
                logger.error("消息反序列化失败: {}", e.getMessage());
                return null;
            }
        }
        
        return null;
    }
    
    /**
     * 关闭队列
     */
    public void shutdown() {
        scheduler.shutdown();
    }
}

/**
 * 消息队列测试类
 */
class MessageQueueTest {
    
    public static void main(String[] args) throws Exception {
        Jedis jedis = RedisConfig.getJedis();
        
        try {
            System.out.println("=== 测试List消息队列 ===");
            ListMessageQueue listQueue = new ListMessageQueue(jedis, "test:list:queue");
            
            // 发送测试消息
            Map<String, Object> testMessage = Map.of("type", "test", "content", "Hello List Queue");
            listQueue.sendMessage(testMessage);
            
            // 接收消息
            @SuppressWarnings("unchecked")
            Map<String, Object> receivedMessage = (Map<String, Object>) 
                    listQueue.receiveMessage(Object.class, 5);
            System.out.println("List队列接收消息: " + receivedMessage);
            
            System.out.println("\n=== 测试Pub/Sub消息队列 ===");
            PubSubMessageQueue pubSubQueue = new PubSubMessageQueue(jedis, "test:pubsub:channel");
            
            // 订阅消息
            CountDownLatch latch = new CountDownLatch(1);
            pubSubQueue.subscribeMessage(Object.class, message -> {
                System.out.println("Pub/Sub队列接收消息: " + message);
                latch.countDown();
            });
            
            // 发布消息
            Thread.sleep(100); // 等待订阅建立
            Map<String, Object> pubSubMessage = Map.of("type", "test", "content", "Hello Pub/Sub");
            pubSubQueue.publishMessage(pubSubMessage);
            
            // 等待消息接收
            latch.await(5, TimeUnit.SECONDS);
            pubSubQueue.shutdown();
            
            System.out.println("\n=== 测试Stream消息队列 ===");
            StreamMessageQueue streamQueue = new StreamMessageQueue(jedis, "test:stream:queue");
            
            // 发送消息
            Map<String, Object> streamMessage = Map.of("type", "test", "content", "Hello Stream");
            StreamEntryID messageId = streamQueue.sendMessage(streamMessage);
            System.out.println("Stream队列发送消息，ID: " + messageId);
            
            // 读取消息
            List<Object> streamMessages = streamQueue.readMessages(Object.class, 10);
            System.out.println("Stream队列读取消息: " + streamMessages);
            
            System.out.println("\n=== 测试延迟消息队列 ===");
            DelayedMessageQueue delayedQueue = new DelayedMessageQueue(jedis, "test:delayed:queue");
            
            // 发送延迟消息（2秒后投递）
            Map<String, Object> delayedMessage = Map.of("type", "test", "content", "Hello Delayed Queue");
            delayedQueue.sendDelayedMessage(delayedMessage, 2, TimeUnit.SECONDS);
            
            // 立即尝试接收（应该收不到）
            Object immediateMessage = delayedQueue.receiveMessage(Object.class, 1);
            System.out.println("立即接收延迟消息: " + immediateMessage);
            
            // 等待2秒后接收
            Thread.sleep(2500);
            Object delayedReceivedMessage = delayedQueue.receiveMessage(Object.class, 1);
            System.out.println("延迟后接收消息: " + delayedReceivedMessage);
            
            delayedQueue.shutdown();
            
            System.out.println("\n消息队列测试完成!");
            
        } finally {
            RedisConfig.closeJedis(jedis);
        }
    }
}