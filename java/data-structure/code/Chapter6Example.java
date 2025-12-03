import java.util.*;

/**
 * 第六章：哈希表 - 快速查找的艺术
 * 完整可运行的代码示例
 */
public class Chapter6Example {
    
    // 1. 链地址法哈希表实现
    static class ChainedHashTable<K, V> {
        private int bucketSize;
        private List<HashNode<K, V>> bucketArray;
        
        static class HashNode<K, V> {
            K key;
            V value;
            HashNode<K, V> next;
            
            public HashNode(K key, V value) {
                this.key = key;
                this.value = value;
                this.next = null;
            }
        }
        
        public ChainedHashTable(int bucketSize) {
            this.bucketSize = bucketSize;
            this.bucketArray = new ArrayList<>(bucketSize);
            
            for (int i = 0; i < bucketSize; i++) {
                bucketArray.add(null);
            }
        }
        
        private int getBucketIndex(K key) {
            int hashCode = key.hashCode();
            return Math.abs(hashCode) % bucketSize;
        }
        
        public void put(K key, V value) {
            int bucketIndex = getBucketIndex(key);
            HashNode<K, V> head = bucketArray.get(bucketIndex);
            
            while (head != null) {
                if (head.key.equals(key)) {
                    head.value = value;
                    return;
                }
                head = head.next;
            }
            
            HashNode<K, V> newNode = new HashNode<>(key, value);
            head = bucketArray.get(bucketIndex);
            newNode.next = head;
            bucketArray.set(bucketIndex, newNode);
            System.out.println("链地址法 - 插入: (" + key + ", " + value + ")");
        }
        
        public V get(K key) {
            int bucketIndex = getBucketIndex(key);
            HashNode<K, V> head = bucketArray.get(bucketIndex);
            
            while (head != null) {
                if (head.key.equals(key)) {
                    return head.value;
                }
                head = head.next;
            }
            
            return null;
        }
        
        public V remove(K key) {
            int bucketIndex = getBucketIndex(key);
            HashNode<K, V> head = bucketArray.get(bucketIndex);
            
            if (head != null && head.key.equals(key)) {
                V value = head.value;
                bucketArray.set(bucketIndex, head.next);
                return value;
            }
            
            while (head != null && head.next != null) {
                if (head.next.key.equals(key)) {
                    V value = head.next.value;
                    head.next = head.next.next;
                    return value;
                }
                head = head.next;
            }
            
            return null;
        }
    }
    
    // 2. 开放地址法哈希表实现
    static class OpenAddressingHashTable<K, V> {
        private int capacity;
        private int size;
        private K[] keys;
        private V[] values;
        private boolean[] isOccupied;
        private boolean[] isDeleted;
        
        @SuppressWarnings("unchecked")
        public OpenAddressingHashTable(int capacity) {
            this.capacity = capacity;
            this.size = 0;
            this.keys = (K[]) new Object[capacity];
            this.values = (V[]) new Object[capacity];
            this.isOccupied = new boolean[capacity];
            this.isDeleted = new boolean[capacity];
        }
        
        private int hash(K key) {
            return Math.abs(key.hashCode()) % capacity;
        }
        
        private int findSlot(K key) {
            int index = hash(key);
            int startIndex = index;
            
            while (isOccupied[index] && !isDeleted[index] && !keys[index].equals(key)) {
                index = (index + 1) % capacity;
                if (index == startIndex) {
                    return -1;
                }
            }
            
            return index;
        }
        
        public void put(K key, V value) {
            if (size >= capacity) {
                System.out.println("开放地址法 - 哈希表已满");
                return;
            }
            
            int index = findSlot(key);
            if (index == -1) {
                System.out.println("开放地址法 - 哈希表已满");
                return;
            }
            
            if (!isOccupied[index] || isDeleted[index]) {
                size++;
            }
            
            keys[index] = key;
            values[index] = value;
            isOccupied[index] = true;
            isDeleted[index] = false;
            System.out.println("开放地址法 - 插入: (" + key + ", " + value + ")");
        }
        
        public V get(K key) {
            int index = findSlot(key);
            if (index != -1 && isOccupied[index] && !isDeleted[index] && keys[index].equals(key)) {
                return values[index];
            }
            
            return null;
        }
        
        public V remove(K key) {
            int index = findSlot(key);
            if (index != -1 && isOccupied[index] && !isDeleted[index] && keys[index].equals(key)) {
                V value = values[index];
                isDeleted[index] = true;
                size--;
                return value;
            }
            
            return null;
        }
    }
    
    // 3. 动态扩容哈希表
    static class DynamicHashTable<K, V> {
        private int capacity;
        private int size;
        private double loadFactorThreshold;
        private List<HashNode<K, V>>[] buckets;
        
        static class HashNode<K, V> {
            K key;
            V value;
            HashNode<K, V> next;
            
            HashNode(K key, V value) {
                this.key = key;
                this.value = value;
                this.next = null;
            }
        }
        
        @SuppressWarnings("unchecked")
        public DynamicHashTable() {
            this.capacity = 16;
            this.size = 0;
            this.loadFactorThreshold = 0.75;
            this.buckets = new List[capacity];
            
            for (int i = 0; i < capacity; i++) {
                buckets[i] = null;
            }
        }
        
        private int getBucketIndex(K key) {
            return Math.abs(key.hashCode()) % capacity;
        }
        
        private double getLoadFactor() {
            return (double) size / capacity;
        }
        
        @SuppressWarnings("unchecked")
        private void resize() {
            System.out.println("动态扩容 - 扩容: " + capacity + " -> " + (capacity * 2));
            
            int oldCapacity = capacity;
            List<HashNode<K, V>>[] oldBuckets = buckets;
            
            capacity *= 2;
            size = 0;
            buckets = new List[capacity];
            
            for (int i = 0; i < capacity; i++) {
                buckets[i] = null;
            }
            
            for (int i = 0; i < oldCapacity; i++) {
                List<HashNode<K, V>> bucket = oldBuckets[i];
                if (bucket != null) {
                    for (HashNode<K, V> node : bucket) {
                        put(node.key, node.value);
                    }
                }
            }
        }
        
        public void put(K key, V value) {
            if (getLoadFactor() >= loadFactorThreshold) {
                resize();
            }
            
            int bucketIndex = getBucketIndex(key);
            
            if (buckets[bucketIndex] == null) {
                buckets[bucketIndex] = new ArrayList<>();
            }
            
            List<HashNode<K, V>> bucket = buckets[bucketIndex];
            
            for (HashNode<K, V> node : bucket) {
                if (node.key.equals(key)) {
                    node.value = value;
                    return;
                }
            }
            
            bucket.add(new HashNode<>(key, value));
            size++;
            System.out.println("动态扩容 - 插入: (" + key + ", " + value + ")");
        }
        
        public V get(K key) {
            int bucketIndex = getBucketIndex(key);
            
            if (buckets[bucketIndex] == null) {
                return null;
            }
            
            List<HashNode<K, V>> bucket = buckets[bucketIndex];
            
            for (HashNode<K, V> node : bucket) {
                if (node.key.equals(key)) {
                    return node.value;
                }
            }
            
            return null;
        }
        
        public V remove(K key) {
            int bucketIndex = getBucketIndex(key);
            
            if (buckets[bucketIndex] == null) {
                return null;
            }
            
            List<HashNode<K, V>> bucket = buckets[bucketIndex];
            
            Iterator<HashNode<K, V>> iterator = bucket.iterator();
            while (iterator.hasNext()) {
                HashNode<K, V> node = iterator.next();
                if (node.key.equals(key)) {
                    V value = node.value;
                    iterator.remove();
                    size--;
                    return value;
                }
            }
            
            return null;
        }
        
        public void printStats() {
            System.out.println("动态扩容 - 状态: 容量=" + capacity + ", 元素数=" + size + 
                             ", 负载因子=" + String.format("%.2f", getLoadFactor()));
        }
    }
    
    // 4. LRU缓存实现
    static class LRUCache<K, V> {
        private final int capacity;
        private final Map<K, V> cache;
        private final LinkedList<K> accessOrder;
        
        public LRUCache(int capacity) {
            this.capacity = capacity;
            this.cache = new HashMap<>();
            this.accessOrder = new LinkedList<>();
        }
        
        public V get(K key) {
            if (!cache.containsKey(key)) {
                return null;
            }
            
            accessOrder.remove(key);
            accessOrder.addFirst(key);
            return cache.get(key);
        }
        
        public void put(K key, V value) {
            if (cache.containsKey(key)) {
                cache.put(key, value);
                accessOrder.remove(key);
                accessOrder.addFirst(key);
            } else {
                if (cache.size() >= capacity) {
                    K lruKey = accessOrder.removeLast();
                    cache.remove(lruKey);
                    System.out.println("LRU缓存 - 移除: " + lruKey);
                }
                cache.put(key, value);
                accessOrder.addFirst(key);
            }
            System.out.println("LRU缓存 - 存储: " + key + " = " + value);
        }
        
        public void printCache() {
            System.out.println("LRU缓存 - 内容:");
            for (K key : accessOrder) {
                System.out.println("  " + key + " = " + cache.get(key));
            }
        }
    }
    
    // 5. 数据库索引实现
    static class DatabaseIndex {
        private Map<String, List<Integer>> index;
        
        public DatabaseIndex() {
            this.index = new HashMap<>();
        }
        
        public void addIndex(String fieldValue, int recordId) {
            index.computeIfAbsent(fieldValue, k -> new ArrayList<>()).add(recordId);
            System.out.println("数据库索引 - 添加: " + fieldValue + " -> " + recordId);
        }
        
        public List<Integer> findRecords(String fieldValue) {
            return index.getOrDefault(fieldValue, new ArrayList<>());
        }
        
        public void removeIndex(String fieldValue, int recordId) {
            List<Integer> recordIds = index.get(fieldValue);
            if (recordIds != null) {
                recordIds.remove(Integer.valueOf(recordId));
                if (recordIds.isEmpty()) {
                    index.remove(fieldValue);
                }
                System.out.println("数据库索引 - 删除: " + fieldValue + " -> " + recordId);
            }
        }
    }
    
    // 6. Rabin-Karp字符串匹配算法
    static class RabinKarp {
        private static final int PRIME = 101;
        
        public static List<Integer> search(String pattern, String text) {
            List<Integer> result = new ArrayList<>();
            int patternLength = pattern.length();
            int textLength = text.length();
            
            if (patternLength > textLength) {
                return result;
            }
            
            int patternHash = calculateHash(pattern, patternLength);
            int textHash = calculateHash(text, patternLength);
            
            int h = 1;
            for (int i = 0; i < patternLength - 1; i++) {
                h = (h * 256) % PRIME;
            }
            
            for (int i = 0; i <= textLength - patternLength; i++) {
                if (patternHash == textHash) {
                    boolean match = true;
                    for (int j = 0; j < patternLength; j++) {
                        if (text.charAt(i + j) != pattern.charAt(j)) {
                            match = false;
                            break;
                        }
                    }
                    
                    if (match) {
                        result.add(i);
                    }
                }
                
                if (i < textLength - patternLength) {
                    textHash = (256 * (textHash - text.charAt(i) * h) + text.charAt(i + patternLength)) % PRIME;
                    
                    if (textHash < 0) {
                        textHash += PRIME;
                    }
                }
            }
            
            return result;
        }
        
        private static int calculateHash(String str, int length) {
            int hash = 0;
            for (int i = 0; i < length; i++) {
                hash = (256 * hash + str.charAt(i)) % PRIME;
            }
            return hash;
        }
    }
    
    // 测试方法
    public static void main(String[] args) {
        System.out.println("=== 第六章：哈希表 - 快速查找的艺术 ===\n");
        
        // 1. 测试链地址法哈希表
        System.out.println("1. 链地址法哈希表测试:");
        ChainedHashTable<String, Integer> chainedTable = new ChainedHashTable<>(5);
        chainedTable.put("apple", 5);
        chainedTable.put("banana", 3);
        chainedTable.put("orange", 8);
        System.out.println("查找apple: " + chainedTable.get("apple"));
        System.out.println("查找grape: " + chainedTable.get("grape"));
        System.out.println();
        
        // 2. 测试开放地址法哈希表
        System.out.println("2. 开放地址法哈希表测试:");
        OpenAddressingHashTable<String, Integer> openTable = new OpenAddressingHashTable<>(7);
        openTable.put("key1", 10);
        openTable.put("key2", 20);
        openTable.put("key3", 30);
        System.out.println("查找key2: " + openTable.get("key2"));
        System.out.println();
        
        // 3. 测试动态扩容哈希表
        System.out.println("3. 动态扩容哈希表测试:");
        DynamicHashTable<String, Integer> dynamicTable = new DynamicHashTable<>();
        for (int i = 0; i < 20; i++) {
            dynamicTable.put("key" + i, i * 10);
        }
        dynamicTable.printStats();
        System.out.println();
        
        // 4. 测试LRU缓存
        System.out.println("4. LRU缓存测试:");
        LRUCache<String, Integer> lruCache = new LRUCache<>(3);
        lruCache.put("a", 1);
        lruCache.put("b", 2);
        lruCache.put("c", 3);
        lruCache.printCache();
        lruCache.put("d", 4);  // 应该移除"a"
        lruCache.printCache();
        System.out.println();
        
        // 5. 测试数据库索引
        System.out.println("5. 数据库索引测试:");
        DatabaseIndex dbIndex = new DatabaseIndex();
        dbIndex.addIndex("apple", 101);
        dbIndex.addIndex("apple", 102);
        dbIndex.addIndex("banana", 201);
        System.out.println("查找apple的记录: " + dbIndex.findRecords("apple"));
        dbIndex.removeIndex("apple", 101);
        System.out.println("删除后查找apple的记录: " + dbIndex.findRecords("apple"));
        System.out.println();
        
        // 6. 测试Rabin-Karp字符串匹配
        System.out.println("6. Rabin-Karp字符串匹配测试:");
        String text = "ABABCABABA";
        String pattern = "ABAB";
        List<Integer> positions = RabinKarp.search(pattern, text);
        System.out.println("在\"" + text + "\"中查找\"" + pattern + "\"的位置: " + positions);
    }
}