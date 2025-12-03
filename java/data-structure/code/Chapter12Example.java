import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReentrantLock;

/**
 * 第十二章：分布式系统中的数据结构 - Java代码示例
 */
public class Chapter12Example {
    
    // 1. 简化的DHT节点实现
    public static class DHTNode {
        private String nodeId;
        private Map<String, String> localData;
        private DHTNode successor;
        private DHTNode predecessor;
        
        public DHTNode(String nodeId) {
            this.nodeId = nodeId;
            this.localData = new HashMap<>();
        }
        
        // 存储键值对
        public void put(String key, String value) {
            String targetNode = findNode(key);
            if (targetNode.equals(this.nodeId)) {
                localData.put(key, value);
            } else {
                // 转发到目标节点
                forwardPut(targetNode, key, value);
            }
        }
        
        // 获取值
        public String get(String key) {
            String targetNode = findNode(key);
            if (targetNode.equals(this.nodeId)) {
                return localData.get(key);
            } else {
                // 转发到目标节点
                return forwardGet(targetNode, key);
            }
        }
        
        // 查找负责该键的节点
        private String findNode(String key) {
            // 简化实现：使用哈希函数确定节点
            return hashKey(key);
        }
        
        // 哈希函数
        private String hashKey(String key) {
            // 简化实现
            return String.valueOf(Math.abs(key.hashCode()) % 1000);
        }
        
        // 转发PUT请求
        private void forwardPut(String targetNodeId, String key, String value) {
            // 在实际实现中，这里会将请求转发到目标节点
            System.out.println("Forwarding PUT request to node " + targetNodeId);
        }
        
        // 转发GET请求
        private String forwardGet(String targetNodeId, String key) {
            // 在实际实现中，这里会将请求转发到目标节点
            System.out.println("Forwarding GET request to node " + targetNodeId);
            return null;
        }
        
        // Getters and setters
        public String getNodeId() { return nodeId; }
        public void setSuccessor(DHTNode successor) { this.successor = successor; }
        public void setPredecessor(DHTNode predecessor) { this.predecessor = predecessor; }
    }
    
    // 2. 一致性哈希实现
    public static class ConsistentHashing {
        private TreeMap<Integer, String> circle = new TreeMap<>();
        private List<String> nodes;
        private int numberOfReplicas; // 虚拟节点数量
        
        public ConsistentHashing(List<String> nodes, int numberOfReplicas) {
            this.nodes = nodes;
            this.numberOfReplicas = numberOfReplicas;
            
            // 初始化哈希环
            for (String node : nodes) {
                addNode(node);
            }
        }
        
        // 添加节点
        public void addNode(String node) {
            for (int i = 0; i < numberOfReplicas; i++) {
                // 为每个节点创建虚拟节点
                circle.put((node + i).hashCode(), node);
            }
        }
        
        // 删除节点
        public void removeNode(String node) {
            for (int i = 0; i < numberOfReplicas; i++) {
                circle.remove((node + i).hashCode());
            }
        }
        
        // 获取负责该键的节点
        public String getNode(String key) {
            if (circle.isEmpty()) {
                return null;
            }
            
            int hash = key.hashCode();
            // 顺时针找到第一个节点
            SortedMap<Integer, String> tailMap = circle.tailMap(hash);
            int nodeHash = tailMap.isEmpty() ? circle.firstKey() : tailMap.firstKey();
            return circle.get(nodeHash);
        }
        
        // 测试一致性哈希
        public static void testConsistentHashing() {
            System.out.println("=== 一致性哈希测试 ===");
            List<String> nodes = Arrays.asList("node1", "node2", "node3");
            ConsistentHashing consistentHashing = new ConsistentHashing(nodes, 3);
            
            // 测试数据分布
            Map<String, Integer> distribution = new HashMap<>();
            for (int i = 0; i < 100; i++) {
                String key = "key" + i;
                String node = consistentHashing.getNode(key);
                distribution.put(node, distribution.getOrDefault(node, 0) + 1);
            }
            
            System.out.println("初始数据分布情况:");
            for (Map.Entry<String, Integer> entry : distribution.entrySet()) {
                System.out.println(entry.getKey() + ": " + entry.getValue() + " keys");
            }
            
            // 添加新节点
            System.out.println("\n添加新节点后:");
            consistentHashing.addNode("node4");
            Map<String, Integer> newDistribution = new HashMap<>();
            for (int i = 0; i < 100; i++) {
                String key = "key" + i;
                String node = consistentHashing.getNode(key);
                newDistribution.put(node, newDistribution.getOrDefault(node, 0) + 1);
            }
            
            for (Map.Entry<String, Integer> entry : newDistribution.entrySet()) {
                System.out.println(entry.getKey() + ": " + entry.getValue() + " keys");
            }
        }
    }
    
    // 3. 简化的Raft节点实现
    public static class RaftNode {
        // 节点状态枚举
        enum State {
            FOLLOWER, CANDIDATE, LEADER
        }
        
        private State state;
        private int currentTerm;
        private String votedFor;
        private List<LogEntry> log;
        private int commitIndex;
        private int lastApplied;
        private Map<String, Integer> nextIndex;
        private Map<String, Integer> matchIndex;
        private String nodeId;
        private List<String> peers;
        private long lastHeartbeat;
        private long electionTimeout;
        
        public RaftNode(String nodeId, List<String> peers) {
            this.nodeId = nodeId;
            this.peers = peers;
            this.state = State.FOLLOWER;
            this.currentTerm = 0;
            this.log = new ArrayList<>();
            this.commitIndex = 0;
            this.lastApplied = 0;
            this.nextIndex = new HashMap<>();
            this.matchIndex = new HashMap<>();
            this.lastHeartbeat = System.currentTimeMillis();
            this.electionTimeout = 150 + new Random().nextInt(150); // 150-300ms
            
            // 初始化跟随者索引
            for (String peer : peers) {
                if (!peer.equals(nodeId)) {
                    nextIndex.put(peer, 1);
                    matchIndex.put(peer, 0);
                }
            }
        }
        
        // 服务器规则
        public void run() {
            while (true) {
                switch (state) {
                    case FOLLOWER:
                        followerLogic();
                        break;
                    case CANDIDATE:
                        candidateLogic();
                        break;
                    case LEADER:
                        leaderLogic();
                        break;
                }
                
                try {
                    Thread.sleep(10);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                    return;
                }
            }
        }
        
        // 跟随者逻辑
        private void followerLogic() {
            long now = System.currentTimeMillis();
            if (now - lastHeartbeat > electionTimeout) {
                // 超时，转换为候选人
                becomeCandidate();
            }
        }
        
        // 候选人逻辑
        private void candidateLogic() {
            // 开始选举
            currentTerm++;
            votedFor = nodeId;
            int votesReceived = 1; // 自己的一票
            
            // 向其他节点发送投票请求
            for (String peer : peers) {
                if (!peer.equals(nodeId)) {
                    if (requestVote(peer)) {
                        votesReceived++;
                    }
                }
            }
            
            // 检查是否获得多数票
            if (votesReceived > peers.size() / 2) {
                becomeLeader();
            } else {
                // 选举失败，重新开始
                state = State.FOLLOWER;
            }
        }
        
        // 领导人逻辑
        private void leaderLogic() {
            // 发送心跳
            sendHeartbeat();
        }
        
        // 转换为候选人
        private void becomeCandidate() {
            state = State.CANDIDATE;
            System.out.println(nodeId + " became candidate");
        }
        
        // 转换为领导人
        private void becomeLeader() {
            state = State.LEADER;
            System.out.println(nodeId + " became leader");
        }
        
        // 请求投票
        private boolean requestVote(String peer) {
            // 简化实现：随机返回投票结果
            return new Random().nextBoolean();
        }
        
        // 发送心跳
        private void sendHeartbeat() {
            lastHeartbeat = System.currentTimeMillis();
            // 在实际实现中，这里会向所有跟随者发送心跳消息
            System.out.println(nodeId + " sending heartbeat");
        }
        
        // 处理投票请求
        public VoteResponse handleRequestVote(VoteRequest request) {
            if (request.getTerm() < currentTerm) {
                return new VoteResponse(currentTerm, false);
            }
            
            if ((votedFor == null || votedFor.equals(request.getCandidateId())) && 
                request.getLastLogIndex() >= getLastLogIndex()) {
                votedFor = request.getCandidateId();
                lastHeartbeat = System.currentTimeMillis();
                return new VoteResponse(currentTerm, true);
            }
            
            return new VoteResponse(currentTerm, false);
        }
        
        // 处理追加条目请求
        public AppendEntriesResponse handleAppendEntries(AppendEntriesRequest request) {
            if (request.getTerm() < currentTerm) {
                return new AppendEntriesResponse(currentTerm, false);
            }
            
            lastHeartbeat = System.currentTimeMillis();
            state = State.FOLLOWER;
            currentTerm = request.getTerm();
            
            // 在实际实现中，这里会处理日志条目
            return new AppendEntriesResponse(currentTerm, true);
        }
        
        // 获取最后日志索引
        private int getLastLogIndex() {
            return log.size() > 0 ? log.size() - 1 : -1;
        }
        
        // 内部类：日志条目
        static class LogEntry {
            private int term;
            private String command;
            
            public LogEntry(int term, String command) {
                this.term = term;
                this.command = command;
            }
            
            // Getters
            public int getTerm() { return term; }
            public String getCommand() { return command; }
        }
        
        // 内部类：投票请求
        static class VoteRequest {
            private int term;
            private String candidateId;
            private int lastLogIndex;
            private int lastLogTerm;
            
            public VoteRequest(int term, String candidateId, int lastLogIndex, int lastLogTerm) {
                this.term = term;
                this.candidateId = candidateId;
                this.lastLogIndex = lastLogIndex;
                this.lastLogTerm = lastLogTerm;
            }
            
            // Getters
            public int getTerm() { return term; }
            public String getCandidateId() { return candidateId; }
            public int getLastLogIndex() { return lastLogIndex; }
            public int getLastLogTerm() { return lastLogTerm; }
        }
        
        // 内部类：投票响应
        static class VoteResponse {
            private int term;
            private boolean voteGranted;
            
            public VoteResponse(int term, boolean voteGranted) {
                this.term = term;
                this.voteGranted = voteGranted;
            }
            
            // Getters
            public int getTerm() { return term; }
            public boolean isVoteGranted() { return voteGranted; }
        }
        
        // 内部类：追加条目请求
        static class AppendEntriesRequest {
            private int term;
            private String leaderId;
            private int prevLogIndex;
            private int prevLogTerm;
            private List<LogEntry> entries;
            private int leaderCommit;
            
            public AppendEntriesRequest(int term, String leaderId, int prevLogIndex, 
                                      int prevLogTerm, List<LogEntry> entries, int leaderCommit) {
                this.term = term;
                this.leaderId = leaderId;
                this.prevLogIndex = prevLogIndex;
                this.prevLogTerm = prevLogTerm;
                this.entries = entries;
                this.leaderCommit = leaderCommit;
            }
            
            // Getters
            public int getTerm() { return term; }
            public String getLeaderId() { return leaderId; }
            public int getPrevLogIndex() { return prevLogIndex; }
            public int getPrevLogTerm() { return prevLogTerm; }
            public List<LogEntry> getEntries() { return entries; }
            public int getLeaderCommit() { return leaderCommit; }
        }
        
        // 内部类：追加条目响应
        static class AppendEntriesResponse {
            private int term;
            private boolean success;
            
            public AppendEntriesResponse(int term, boolean success) {
                this.term = term;
                this.success = success;
            }
            
            // Getters
            public int getTerm() { return term; }
            public boolean isSuccess() { return success; }
        }
    }
    
    // 4. 基于内存的分布式锁实现
    public static class MemoryDistributedLock implements Lock {
        private static final Map<String, String> locks = new ConcurrentHashMap<>();
        private static final Map<String, Long> expireTimes = new ConcurrentHashMap<>();
        
        private String lockKey;
        private String lockValue;
        private long expireTime;
        
        public MemoryDistributedLock(String lockKey, long expireTime) {
            this.lockKey = lockKey;
            this.expireTime = expireTime;
            this.lockValue = UUID.randomUUID().toString();
        }
        
        @Override
        public void lock() {
            while (true) {
                if (tryLock()) {
                    return;
                }
                // 等待一段时间后重试
                try {
                    Thread.sleep(100);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                    return;
                }
            }
        }
        
        @Override
        public void lockInterruptibly() throws InterruptedException {
            while (true) {
                if (tryLock()) {
                    return;
                }
                if (Thread.currentThread().isInterrupted()) {
                    throw new InterruptedException();
                }
                Thread.sleep(100);
            }
        }
        
        @Override
        public boolean tryLock() {
            synchronized (locks) {
                // 清除过期锁
                Long expireTime = expireTimes.get(lockKey);
                if (expireTime != null && System.currentTimeMillis() > expireTime) {
                    locks.remove(lockKey);
                    expireTimes.remove(lockKey);
                }
                
                // 尝试获取锁
                if (!locks.containsKey(lockKey)) {
                    locks.put(lockKey, lockValue);
                    expireTimes.put(lockKey, System.currentTimeMillis() + this.expireTime * 1000);
                    return true;
                }
                return false;
            }
        }
        
        @Override
        public boolean tryLock(long time, TimeUnit unit) throws InterruptedException {
            long timeout = unit.toMillis(time);
            long start = System.currentTimeMillis();
            
            while (true) {
                if (tryLock()) {
                    return true;
                }
                if (System.currentTimeMillis() - start > timeout) {
                    return false;
                }
                if (Thread.currentThread().isInterrupted()) {
                    throw new InterruptedException();
                }
                Thread.sleep(100);
            }
        }
        
        @Override
        public void unlock() {
            synchronized (locks) {
                if (lockValue.equals(locks.get(lockKey))) {
                    locks.remove(lockKey);
                    expireTimes.remove(lockKey);
                }
            }
        }
        
        @Override
        public Condition newCondition() {
            throw new UnsupportedOperationException("MemoryDistributedLock does not support conditions");
        }
        
        // 测试分布式锁
        public static void testDistributedLock() throws InterruptedException {
            System.out.println("=== 分布式锁测试 ===");
            
            // 模拟多个线程竞争锁
            ExecutorService executor = Executors.newFixedThreadPool(3);
            CountDownLatch latch = new CountDownLatch(3);
            
            for (int i = 0; i < 3; i++) {
                final int threadId = i;
                executor.submit(() -> {
                    MemoryDistributedLock lock = new MemoryDistributedLock("test_lock", 10);
                    try {
                        lock.lock();
                        System.out.println("Thread " + threadId + " acquired lock");
                        Thread.sleep(2000); // 模拟业务处理
                        System.out.println("Thread " + threadId + " released lock");
                    } catch (InterruptedException e) {
                        Thread.currentThread().interrupt();
                    } finally {
                        lock.unlock();
                        latch.countDown();
                    }
                });
            }
            
            latch.await(); // 等待所有线程执行完毕
            executor.shutdown();
        }
    }
    
    // 5. 简化的分布式缓存实现
    public static class DistributedCache {
        private Map<String, CacheNode> nodes;
        private ConsistentHashing consistentHashing;
        
        public DistributedCache(List<String> nodeIds) {
            this.nodes = new ConcurrentHashMap<>();
            for (String nodeId : nodeIds) {
                nodes.put(nodeId, new CacheNode(nodeId));
            }
            this.consistentHashing = new ConsistentHashing(nodeIds, 3);
        }
        
        // 设置缓存
        public void put(String key, String value) {
            String nodeId = consistentHashing.getNode(key);
            CacheNode node = nodes.get(nodeId);
            if (node != null) {
                node.put(key, value);
                System.out.println("PUT " + key + " -> " + value + " on node " + nodeId);
            }
        }
        
        // 获取缓存
        public String get(String key) {
            String nodeId = consistentHashing.getNode(key);
            CacheNode node = nodes.get(nodeId);
            if (node != null) {
                String value = node.get(key);
                System.out.println("GET " + key + " from node " + nodeId + ": " + value);
                return value;
            }
            return null;
        }
        
        // 删除缓存
        public void remove(String key) {
            String nodeId = consistentHashing.getNode(key);
            CacheNode node = nodes.get(nodeId);
            if (node != null) {
                node.remove(key);
                System.out.println("REMOVE " + key + " from node " + nodeId);
            }
        }
        
        // 缓存节点实现
        static class CacheNode {
            private String nodeId;
            private Map<String, String> data;
            
            public CacheNode(String nodeId) {
                this.nodeId = nodeId;
                this.data = new ConcurrentHashMap<>();
            }
            
            public void put(String key, String value) {
                data.put(key, value);
            }
            
            public String get(String key) {
                return data.get(key);
            }
            
            public void remove(String key) {
                data.remove(key);
            }
            
            public String getNodeId() {
                return nodeId;
            }
        }
        
        // 测试分布式缓存
        public static void testDistributedCache() {
            System.out.println("=== 分布式缓存测试 ===");
            List<String> nodeIds = Arrays.asList("node1", "node2", "node3");
            DistributedCache cache = new DistributedCache(nodeIds);
            
            // 存储数据
            cache.put("key1", "value1");
            cache.put("key2", "value2");
            cache.put("key3", "value3");
            
            // 获取数据
            System.out.println("\nRetrieving data:");
            System.out.println(cache.get("key1"));
            System.out.println(cache.get("key2"));
            System.out.println(cache.get("key3"));
            
            // 删除数据
            System.out.println("\nRemoving key2:");
            cache.remove("key2");
            System.out.println("key2 after removal: " + cache.get("key2"));
        }
    }
    
    // 6. 简化的分布式队列实现
    public static class DistributedQueue {
        private String queueName;
        private Map<String, QueueNode> nodes;
        private ConsistentHashing consistentHashing;
        
        public DistributedQueue(String queueName, List<String> nodeIds) {
            this.queueName = queueName;
            this.nodes = new ConcurrentHashMap<>();
            for (String nodeId : nodeIds) {
                nodes.put(nodeId, new QueueNode(nodeId));
            }
            this.consistentHashing = new ConsistentHashing(nodeIds, 3);
        }
        
        // 入队
        public void enqueue(String message) {
            String nodeId = consistentHashing.getNode(message);
            QueueNode node = nodes.get(nodeId);
            if (node != null) {
                node.enqueue(message);
                System.out.println("ENQUEUE '" + message + "' to node " + nodeId);
            }
        }
        
        // 出队
        public String dequeue() {
            // 简化实现：随机选择一个节点出队
            for (QueueNode node : nodes.values()) {
                String message = node.dequeue();
                if (message != null) {
                    System.out.println("DEQUEUE '" + message + "' from node " + node.getNodeId());
                    return message;
                }
            }
            return null;
        }
        
        // 队列节点实现
        static class QueueNode {
            private String nodeId;
            private BlockingQueue<String> queue;
            
            public QueueNode(String nodeId) {
                this.nodeId = nodeId;
                this.queue = new LinkedBlockingQueue<>();
            }
            
            public void enqueue(String message) {
                try {
                    queue.put(message);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
            }
            
            public String dequeue() {
                try {
                    return queue.poll();
                } catch (Exception e) {
                    return null;
                }
            }
            
            public String getNodeId() {
                return nodeId;
            }
        }
        
        // 测试分布式队列
        public static void testDistributedQueue() throws InterruptedException {
            System.out.println("=== 分布式队列测试 ===");
            List<String> nodeIds = Arrays.asList("node1", "node2", "node3");
            DistributedQueue queue = new DistributedQueue("test_queue", nodeIds);
            
            // 入队
            System.out.println("Enqueuing messages:");
            queue.enqueue("message1");
            queue.enqueue("message2");
            queue.enqueue("message3");
            queue.enqueue("message4");
            queue.enqueue("message5");
            
            // 出队
            System.out.println("\nDequeuing messages:");
            for (int i = 0; i < 5; i++) {
                String message = queue.dequeue();
                if (message != null) {
                    System.out.println("Dequeued: " + message);
                }
                Thread.sleep(100); // 模拟处理时间
            }
        }
    }
    
    // 7. 简化的两阶段提交实现
    public static class TwoPhaseCommit {
        // 事务协调者
        static class Coordinator {
            private List<Participant> participants;
            private String transactionId;
            
            public Coordinator(String transactionId, List<Participant> participants) {
                this.transactionId = transactionId;
                this.participants = participants;
            }
            
            // 两阶段提交
            public boolean commit() {
                // 第一阶段：准备阶段
                boolean canCommit = true;
                for (Participant participant : participants) {
                    if (!participant.prepare(transactionId)) {
                        canCommit = false;
                        break;
                    }
                }
                
                // 第二阶段：提交或回滚
                if (canCommit) {
                    // 提交
                    for (Participant participant : participants) {
                        participant.commit(transactionId);
                    }
                    System.out.println("Transaction " + transactionId + " committed");
                    return true;
                } else {
                    // 回滚
                    for (Participant participant : participants) {
                        participant.rollback(transactionId);
                    }
                    System.out.println("Transaction " + transactionId + " rolled back");
                    return false;
                }
            }
        }
        
        // 事务参与者
        static class Participant {
            private String participantId;
            private Map<String, List<String>> preparedTransactions;
            
            public Participant(String participantId) {
                this.participantId = participantId;
                this.preparedTransactions = new ConcurrentHashMap<>();
            }
            
            // 准备阶段
            public boolean prepare(String transactionId) {
                // 模拟准备操作
                System.out.println("Participant " + participantId + " preparing transaction " + transactionId);
                
                // 模拟准备成功或失败
                boolean success = new Random().nextBoolean();
                if (success) {
                    // 记录准备好的事务
                    preparedTransactions.computeIfAbsent(transactionId, k -> new ArrayList<>());
                    System.out.println("Participant " + participantId + " ready for transaction " + transactionId);
                } else {
                    System.out.println("Participant " + participantId + " failed to prepare transaction " + transactionId);
                }
                return success;
            }
            
            // 提交阶段
            public void commit(String transactionId) {
                // 执行提交操作
                System.out.println("Participant " + participantId + " committing transaction " + transactionId);
                preparedTransactions.remove(transactionId);
            }
            
            // 回滚阶段
            public void rollback(String transactionId) {
                // 执行回滚操作
                System.out.println("Participant " + participantId + " rolling back transaction " + transactionId);
                preparedTransactions.remove(transactionId);
            }
        }
        
        // 测试两阶段提交
        public static void testTwoPhaseCommit() {
            System.out.println("=== 两阶段提交测试 ===");
            // 创建参与者
            List<Participant> participants = Arrays.asList(
                new Participant("participant1"),
                new Participant("participant2"),
                new Participant("participant3")
            );
            
            // 创建协调者
            Coordinator coordinator = new Coordinator("tx-001", participants);
            
            // 执行两阶段提交
            System.out.println("Starting two-phase commit for transaction tx-001");
            boolean result = coordinator.commit();
            System.out.println("Transaction result: " + (result ? "SUCCESS" : "FAILURE"));
        }
    }
    
    // 主方法：演示所有示例
    public static void main(String[] args) throws InterruptedException {
        System.out.println("第十二章：分布式系统中的数据结构 - Java代码示例");
        System.out.println("========================================");
        
        // 1. 测试一致性哈希
        ConsistentHashing.testConsistentHashing();
        System.out.println();
        
        // 2. 测试分布式锁
        MemoryDistributedLock.testDistributedLock();
        System.out.println();
        
        // 3. 测试分布式缓存
        DistributedCache.testDistributedCache();
        System.out.println();
        
        // 4. 测试分布式队列
        DistributedQueue.testDistributedQueue();
        System.out.println();
        
        // 5. 测试两阶段提交
        TwoPhaseCommit.testTwoPhaseCommit();
        System.out.println();
        
        System.out.println("所有示例演示完毕！");
    }
}