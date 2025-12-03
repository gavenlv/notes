import java.util.*;

/**
 * 第十章：高级数据结构与算法
 * 完整可运行的代码示例
 */
public class Chapter10Example {
    
    /**
     * 跳表实现
     */
    static class SkipList<T extends Comparable<T>> {
        // 最大层数
        private static final int MAX_LEVEL = 16;
        
        // 当前跳表的实际层数
        private int levelCount = 1;
        
        // 带头链表节点
        private Node<T> head = new Node<>(MAX_LEVEL, null);
        
        // 随机数生成器
        private Random random = new Random();
        
        // 节点内部类
        public class Node<T> {
            private T data;
            private Node<T>[] forwards; // 存储每层的后继节点
            
            public Node(int level, T data) {
                this.forwards = new Node[level];
                this.data = data;
            }
        }
        
        // 查找操作
        public Node<T> find(T value) {
            Node<T> p = head;
            
            // 从最高层开始查找
            for (int i = levelCount - 1; i >= 0; --i) {
                while (p.forwards[i] != null && p.forwards[i].data.compareTo(value) < 0) {
                    p = p.forwards[i];
                }
            }
            
            // 此时p是小于value的最大节点
            if (p.forwards[0] != null && p.forwards[0].data.compareTo(value) == 0) {
                return p.forwards[0];
            } else {
                return null;
            }
        }
        
        // 插入操作
        public void insert(T value) {
            // 记录每层中小于value的最大节点
            Node<T>[] update = new Node[MAX_LEVEL];
            
            Node<T> p = head;
            for (int i = levelCount - 1; i >= 0; --i) {
                while (p.forwards[i] != null && p.forwards[i].data.compareTo(value) < 0) {
                    p = p.forwards[i];
                }
                update[i] = p;
            }
            
            // 如果value已经存在，则直接返回
            if (p.forwards[0] != null && p.forwards[0].data.compareTo(value) == 0) {
                return;
            }
            
            // 随机生成新节点的层数
            int level = randomLevel();
            
            // 更新跳表的层数
            if (level > levelCount) {
                for (int i = levelCount; i < level; ++i) {
                    update[i] = head;
                }
                levelCount = level;
            }
            
            // 创建新节点
            Node<T> newNode = new Node<>(level, value);
            
            // 更新每层的指针
            for (int i = 0; i < level; ++i) {
                newNode.forwards[i] = update[i].forwards[i];
                update[i].forwards[i] = newNode;
            }
        }
        
        // 删除操作
        public void delete(T value) {
            Node<T>[] update = new Node[MAX_LEVEL];
            Node<T> p = head;
            
            // 找到每一层要删除节点的前驱
            for (int i = levelCount - 1; i >= 0; --i) {
                while (p.forwards[i] != null && p.forwards[i].data.compareTo(value) < 0) {
                    p = p.forwards[i];
                }
                update[i] = p;
            }
            
            // 检查是否找到要删除的节点
            if (p.forwards[0] != null && p.forwards[0].data.compareTo(value) == 0) {
                // 更新每层指针
                for (int i = levelCount - 1; i >= 0; --i) {
                    if (update[i].forwards[i] != null && update[i].forwards[i].data.compareTo(value) == 0) {
                        update[i].forwards[i] = update[i].forwards[i].forwards[i];
                    }
                }
                
                // 更新levelCount
                while (levelCount > 1 && head.forwards[levelCount - 1] == null) {
                    levelCount--;
                }
            }
        }
        
        // 随机生成节点层数
        private int randomLevel() {
            int level = 1;
            // 每次有50%的概率增加一层
            while (random.nextInt() % 2 == 1 && level < MAX_LEVEL) {
                level++;
            }
            return level;
        }
        
        // 打印跳表
        public void printAll() {
            Node<T> p = head;
            while (p.forwards[0] != null) {
                System.out.print(p.forwards[0].data + " ");
                p = p.forwards[0];
            }
            System.out.println();
        }
    }
    
    /**
     * 布隆过滤器实现
     */
    static class BloomFilter<T> {
        // 位数组大小
        private int bitSize;
        
        // 位数组
        private BitSet bits;
        
        // 哈希函数个数
        private int hashFunctionsNum;
        
        // 已插入元素个数
        private int insertedElements;
        
        public BloomFilter(int bitSize, int hashFunctionsNum) {
            this.bitSize = bitSize;
            this.hashFunctionsNum = hashFunctionsNum;
            this.bits = new BitSet(bitSize);
            this.insertedElements = 0;
        }
        
        // 添加元素
        public void add(T value) {
            int[] hashes = createHashes(value.toString().getBytes(), hashFunctionsNum);
            for (int hash : hashes) {
                bits.set(Math.abs(hash % bitSize), true);
            }
            insertedElements++;
        }
        
        // 判断元素是否存在
        public boolean contains(T value) {
            int[] hashes = createHashes(value.toString().getBytes(), hashFunctionsNum);
            for (int hash : hashes) {
                if (!bits.get(Math.abs(hash % bitSize))) {
                    return false;
                }
            }
            return true;
        }
        
        // 计算哈希值
        private int[] createHashes(byte[] data, int num) {
            int[] result = new int[num];
            for (int i = 0; i < num; i++) {
                result[i] = MurmurHash.hash(data, i);
            }
            return result;
        }
        
        // MurmurHash实现
        static class MurmurHash {
            public static int hash(byte[] data, int seed) {
                int m = 0x5bd1e995;
                int r = 24;
                int h = seed ^ data.length;
                int len = data.length;
                int offset = 0;
                
                while (len >= 4) {
                    int k = data[offset] & 0xFF;
                    k |= (data[offset + 1] & 0xFF) << 8;
                    k |= (data[offset + 2] & 0xFF) << 16;
                    k |= (data[offset + 3] & 0xFF) << 24;
                    
                    k *= m;
                    k ^= k >>> r;
                    k *= m;
                    
                    h *= m;
                    h ^= k;
                    
                    offset += 4;
                    len -= 4;
                }
                
                switch (len) {
                    case 3:
                        h ^= (data[offset + 2] & 0xFF) << 16;
                    case 2:
                        h ^= (data[offset + 1] & 0xFF) << 8;
                    case 1:
                        h ^= (data[offset] & 0xFF);
                        h *= m;
                }
                
                h ^= h >>> 13;
                h *= m;
                h ^= h >>> 15;
                
                return h;
            }
        }
    }
    
    /**
     * LRU缓存实现
     */
    static class LRUCache<K, V> {
        // 双向链表节点
        class Node<K, V> {
            K key;
            V value;
            Node<K, V> prev;
            Node<K, V> next;
            
            public Node() {}
            
            public Node(K key, V value) {
                this.key = key;
                this.value = value;
            }
        }
        
        // 缓存容量
        private int capacity;
        
        // 当前缓存大小
        private int size;
        
        // 哈希表
        private Map<K, Node<K, V>> cache;
        
        // 双向链表的虚拟头尾节点
        private Node<K, V> head;
        private Node<K, V> tail;
        
        public LRUCache(int capacity) {
            this.capacity = capacity;
            this.size = 0;
            this.cache = new HashMap<>();
            
            // 初始化虚拟头尾节点
            this.head = new Node<>();
            this.tail = new Node<>();
            head.next = tail;
            tail.prev = head;
        }
        
        // 获取数据
        public V get(K key) {
            Node<K, V> node = cache.get(key);
            if (node == null) {
                return null;
            }
            
            // 移动到头部
            moveToHead(node);
            return node.value;
        }
        
        // 插入数据
        public void put(K key, V value) {
            Node<K, V> node = cache.get(key);
            if (node == null) {
                // 如果key不存在，创建新节点
                Node<K, V> newNode = new Node<>(key, value);
                
                // 添加到哈希表
                cache.put(key, newNode);
                
                // 添加到双向链表头部
                addToHead(newNode);
                
                size++;
                if (size > capacity) {
                    // 如果超出容量，删除尾部节点
                    Node<K, V> tail = removeTail();
                    cache.remove(tail.key);
                    size--;
                }
            } else {
                // 如果key存在，更新值并移动到头部
                node.value = value;
                moveToHead(node);
            }
        }
        
        // 添加节点到头部
        private void addToHead(Node<K, V> node) {
            node.prev = head;
            node.next = head.next;
            head.next.prev = node;
            head.next = node;
        }
        
        // 删除节点
        private void removeNode(Node<K, V> node) {
            node.prev.next = node.next;
            node.next.prev = node.prev;
        }
        
        // 移动节点到头部
        private void moveToHead(Node<K, V> node) {
            removeNode(node);
            addToHead(node);
        }
        
        // 删除尾部节点
        private Node<K, V> removeTail() {
            Node<K, V> res = tail.prev;
            removeNode(res);
            return res;
        }
    }
    
    /**
     * 并查集实现
     */
    static class UnionFind {
        private int[] parent;  // 父节点数组
        private int[] rank;    // 秩数组，用于优化
        private int count;     // 连通分量数量
        
        // 构造函数
        public UnionFind(int n) {
            count = n;
            parent = new int[n];
            rank = new int[n];
            
            // 初始化，每个节点的父节点是自己
            for (int i = 0; i < n; i++) {
                parent[i] = i;
                rank[i] = 1;
            }
        }
        
        // 查找根节点（带路径压缩优化）
        public int find(int x) {
            if (parent[x] != x) {
                parent[x] = find(parent[x]); // 路径压缩
            }
            return parent[x];
        }
        
        // 合并两个集合（按秩合并优化）
        public void union(int x, int y) {
            int rootX = find(x);
            int rootY = find(y);
            
            if (rootX != rootY) {
                // 按秩合并
                if (rank[rootX] > rank[rootY]) {
                    parent[rootY] = rootX;
                } else if (rank[rootX] < rank[rootY]) {
                    parent[rootX] = rootY;
                } else {
                    parent[rootY] = rootX;
                    rank[rootX]++;
                }
                count--;
            }
        }
        
        // 判断两个元素是否连通
        public boolean connected(int x, int y) {
            return find(x) == find(y);
        }
        
        // 返回连通分量数量
        public int getCount() {
            return count;
        }
    }
    
    /**
     * 线段树实现
     */
    static class SegmentTree {
        private int[] tree;  // 线段树数组
        private int[] data;  // 原始数据
        private int n;       // 数据长度
        
        public SegmentTree(int[] arr) {
            if (arr.length > 0) {
                n = arr.length;
                data = new int[n];
                System.arraycopy(arr, 0, data, 0, n);
                tree = new int[4 * n]; // 线段树数组大小为4*n
                buildTree(0, 0, n - 1);
            }
        }
        
        // 构建线段树
        private void buildTree(int treeIndex, int l, int r) {
            if (l == r) {
                tree[treeIndex] = data[l];
                return;
            }
            
            int mid = l + (r - l) / 2;
            int leftTreeIndex = 2 * treeIndex + 1;
            int rightTreeIndex = 2 * treeIndex + 2;
            
            // 递归构建左右子树
            buildTree(leftTreeIndex, l, mid);
            buildTree(rightTreeIndex, mid + 1, r);
            
            // 合并左右子树的结果
            tree[treeIndex] = tree[leftTreeIndex] + tree[rightTreeIndex];
        }
        
        // 查询区间和
        public int query(int queryL, int queryR) {
            if (queryL < 0 || queryL >= n || queryR < 0 || queryR >= n || queryL > queryR) {
                throw new IllegalArgumentException("Query range is invalid");
            }
            return query(0, 0, n - 1, queryL, queryR);
        }
        
        private int query(int treeIndex, int l, int r, int queryL, int queryR) {
            if (l == queryL && r == queryR) {
                return tree[treeIndex];
            }
            
            int mid = l + (r - l) / 2;
            int leftTreeIndex = 2 * treeIndex + 1;
            int rightTreeIndex = 2 * treeIndex + 2;
            
            if (queryR <= mid) {
                // 查询区间完全在左子树
                return query(leftTreeIndex, l, mid, queryL, queryR);
            } else if (queryL > mid) {
                // 查询区间完全在右子树
                return query(rightTreeIndex, mid + 1, r, queryL, queryR);
            } else {
                // 查询区间跨越左右子树
                int leftResult = query(leftTreeIndex, l, mid, queryL, mid);
                int rightResult = query(rightTreeIndex, mid + 1, r, mid + 1, queryR);
                return leftResult + rightResult;
            }
        }
        
        // 更新指定位置的值
        public void update(int index, int value) {
            if (index < 0 || index >= n) {
                throw new IllegalArgumentException("Index is illegal");
            }
            data[index] = value;
            update(0, 0, n - 1, index, value);
        }
        
        private void update(int treeIndex, int l, int r, int index, int value) {
            if (l == r) {
                tree[treeIndex] = value;
                return;
            }
            
            int mid = l + (r - l) / 2;
            int leftTreeIndex = 2 * treeIndex + 1;
            int rightTreeIndex = 2 * treeIndex + 2;
            
            if (index <= mid) {
                update(leftTreeIndex, l, mid, index, value);
            } else {
                update(rightTreeIndex, mid + 1, r, index, value);
            }
            
            tree[treeIndex] = tree[leftTreeIndex] + tree[rightTreeIndex];
        }
    }
    
    /**
     * 字典树实现
     */
    static class Trie {
        // Trie节点
        class TrieNode {
            private boolean isEnd;           // 标记是否为单词结尾
            private TrieNode[] children;     // 子节点数组
            
            public TrieNode() {
                isEnd = false;
                children = new TrieNode[26]; // 假设只包含小写字母
            }
        }
        
        private TrieNode root;
        
        public Trie() {
            root = new TrieNode();
        }
        
        // 插入单词
        public void insert(String word) {
            TrieNode node = root;
            for (int i = 0; i < word.length(); i++) {
                char ch = word.charAt(i);
                int index = ch - 'a';
                
                if (node.children[index] == null) {
                    node.children[index] = new TrieNode();
                }
                node = node.children[index];
            }
            node.isEnd = true; // 标记单词结尾
        }
        
        // 搜索单词
        public boolean search(String word) {
            TrieNode node = searchPrefix(word);
            return node != null && node.isEnd;
        }
        
        // 判断是否有以给定前缀开头的单词
        public boolean startsWith(String prefix) {
            return searchPrefix(prefix) != null;
        }
        
        // 搜索前缀
        private TrieNode searchPrefix(String prefix) {
            TrieNode node = root;
            for (int i = 0; i < prefix.length(); i++) {
                char ch = prefix.charAt(i);
                int index = ch - 'a';
                
                if (node.children[index] == null) {
                    return null;
                }
                node = node.children[index];
            }
            return node;
        }
        
        // 删除单词
        public boolean delete(String word) {
            return delete(root, word, 0);
        }
        
        private boolean delete(TrieNode node, String word, int index) {
            if (index == word.length()) {
                // 到达单词末尾
                if (!node.isEnd) {
                    return false; // 单词不存在
                }
                node.isEnd = false;
                // 如果当前节点没有子节点，则可以删除
                return isEmpty(node);
            }
            
            char ch = word.charAt(index);
            int idx = ch - 'a';
            if (node.children[idx] == null) {
                return false; // 单词不存在
            }
            
            boolean shouldDeleteChild = delete(node.children[idx], word, index + 1);
            
            if (shouldDeleteChild) {
                node.children[idx] = null;
                // 如果当前节点不是单词结尾且没有其他子节点，则可以删除
                return !node.isEnd && isEmpty(node);
            }
            
            return false;
        }
        
        // 判断节点是否为空（没有子节点）
        private boolean isEmpty(TrieNode node) {
            for (int i = 0; i < 26; i++) {
                if (node.children[i] != null) {
                    return false;
                }
            }
            return true;
        }
    }
    
    /**
     * 后缀数组实现（简化版）
     */
    static class SuffixArray {
        private String text;
        private Integer[] suffixes;
        
        public SuffixArray(String text) {
            this.text = text;
            this.suffixes = new Integer[text.length()];
            buildSuffixArray();
        }
        
        private void buildSuffixArray() {
            // 初始化后缀数组
            for (int i = 0; i < text.length(); i++) {
                suffixes[i] = i;
            }
            
            // 按后缀字典序排序
            Arrays.sort(suffixes, (a, b) -> text.substring(a).compareTo(text.substring(b)));
        }
        
        // 模式匹配
        public int[] search(String pattern) {
            int lo = 0, hi = suffixes.length - 1;
            
            // 查找下界
            while (lo <= hi) {
                int mid = lo + (hi - lo) / 2;
                int cmp = compare(pattern, suffixes[mid]);
                if (cmp < 0) hi = mid - 1;
                else if (cmp > 0) lo = mid + 1;
                else {
                    // 找到匹配，向左查找第一个匹配项
                    while (mid > 0 && compare(pattern, suffixes[mid - 1]) == 0) {
                        mid--;
                    }
                    // 收集所有匹配项
                    int count = 0;
                    int temp = mid;
                    while (temp < suffixes.length && compare(pattern, suffixes[temp]) == 0) {
                        count++;
                        temp++;
                    }
                    int[] result = new int[count];
                    for (int i = 0; i < count; i++) {
                        result[i] = suffixes[mid + i];
                    }
                    return result;
                }
            }
            return new int[0]; // 未找到
        }
        
        private int compare(String pattern, int suffixIndex) {
            int n = Math.min(pattern.length(), text.length() - suffixIndex);
            for (int i = 0; i < n; i++) {
                char c1 = pattern.charAt(i);
                char c2 = text.charAt(suffixIndex + i);
                if (c1 < c2) return -1;
                if (c1 > c2) return 1;
            }
            return pattern.length() - (text.length() - suffixIndex);
        }
        
        // 获取后缀数组
        public Integer[] getSuffixes() {
            return suffixes;
        }
        
        // 获取原始文本
        public String getText() {
            return text;
        }
    }
    
    /**
     * 性能测试工具类
     */
    static class AdvancedDataStructurePerformanceTest {
        /**
         * 测试跳表性能
         */
        public static void testSkipList() {
            System.out.println("=== 跳表性能测试 ===");
            SkipList<Integer> skipList = new SkipList<>();
            
            // 插入数据
            long startTime = System.nanoTime();
            for (int i = 0; i < 10000; i++) {
                skipList.insert(i);
            }
            long endTime = System.nanoTime();
            System.out.printf("插入10000个元素耗时: %.2f ms%n", (endTime - startTime) / 1_000_000.0);
            
            // 查找数据
            startTime = System.nanoTime();
            SkipList.Node<Integer> result = skipList.find(5000);
            endTime = System.nanoTime();
            System.out.printf("查找元素5000耗时: %.2f ms, 结果: %s%n", 
                (endTime - startTime) / 1_000_000.0, result != null ? "找到" : "未找到");
        }
        
        /**
         * 测试布隆过滤器性能
         */
        public static void testBloomFilter() {
            System.out.println("\n=== 布隆过滤器性能测试 ===");
            BloomFilter<String> bloomFilter = new BloomFilter<>(100000, 3);
            
            // 插入数据
            long startTime = System.nanoTime();
            for (int i = 0; i < 10000; i++) {
                bloomFilter.add("item" + i);
            }
            long endTime = System.nanoTime();
            System.out.printf("插入10000个元素耗时: %.2f ms%n", (endTime - startTime) / 1_000_000.0);
            
            // 查找存在的数据
            startTime = System.nanoTime();
            boolean result1 = bloomFilter.contains("item5000");
            endTime = System.nanoTime();
            System.out.printf("查找存在的元素'item5000'耗时: %.2f ms, 结果: %b%n", 
                (endTime - startTime) / 1_000_000.0, result1);
            
            // 查找不存在的数据
            startTime = System.nanoTime();
            boolean result2 = bloomFilter.contains("nonexistent");
            endTime = System.nanoTime();
            System.out.printf("查找不存在的元素'nonexistent'耗时: %.2f ms, 结果: %b%n", 
                (endTime - startTime) / 1_000_000.0, result2);
        }
        
        /**
         * 测试LRU缓存性能
         */
        public static void testLRUCache() {
            System.out.println("\n=== LRU缓存性能测试 ===");
            LRUCache<Integer, String> lruCache = new LRUCache<>(1000);
            
            // 插入数据
            long startTime = System.nanoTime();
            for (int i = 0; i < 10000; i++) {
                lruCache.put(i, "value" + i);
            }
            long endTime = System.nanoTime();
            System.out.printf("插入10000个元素耗时: %.2f ms%n", (endTime - startTime) / 1_000_000.0);
            
            // 查找数据
            startTime = System.nanoTime();
            String result = lruCache.get(9500);
            endTime = System.nanoTime();
            System.out.printf("查找元素9500耗时: %.2f ms, 结果: %s%n", 
                (endTime - startTime) / 1_000_000.0, result != null ? result : "未找到");
        }
    }
    
    /**
     * 主方法 - 演示各种高级数据结构的使用
     */
    public static void main(String[] args) {
        System.out.println("第十章：高级数据结构与算法");
        System.out.println("=========================\n");
        
        // 1. 跳表演示
        System.out.println("1. 跳表演示:");
        SkipList<Integer> skipList = new SkipList<>();
        int[] skipListData = {1, 3, 5, 7, 9, 11, 13, 15, 17, 19};
        for (int value : skipListData) {
            skipList.insert(value);
        }
        System.out.print("跳表内容: ");
        skipList.printAll();
        
        int searchValue = 11;
        SkipList.Node<Integer> result = skipList.find(searchValue);
        System.out.printf("查找%d的结果: %s%n", searchValue, result != null ? "找到" : "未找到");
        
        // 2. 布隆过滤器演示
        System.out.println("\n2. 布隆过滤器演示:");
        BloomFilter<String> bloomFilter = new BloomFilter<>(1000, 3);
        String[] bloomData = {"apple", "banana", "orange", "grape", "watermelon"};
        for (String value : bloomData) {
            bloomFilter.add(value);
        }
        
        String searchItem1 = "apple";
        String searchItem2 = "pineapple";
        System.out.printf("'%s' 是否可能存在: %b%n", searchItem1, bloomFilter.contains(searchItem1));
        System.out.printf("'%s' 是否可能存在: %b%n", searchItem2, bloomFilter.contains(searchItem2));
        
        // 3. LRU缓存演示
        System.out.println("\n3. LRU缓存演示:");
        LRUCache<Integer, String> lruCache = new LRUCache<>(3);
        lruCache.put(1, "one");
        lruCache.put(2, "two");
        lruCache.put(3, "three");
        System.out.println("缓存内容: 1->one, 2->two, 3->three");
        
        lruCache.get(1); // 访问1，使其变为最近使用
        lruCache.put(4, "four"); // 插入4，应该淘汰2
        System.out.println("访问1后插入4，缓存内容:");
        System.out.println("  1->" + lruCache.get(1)); // 应该存在
        System.out.println("  2->" + lruCache.get(2)); // 应该被淘汰
        System.out.println("  3->" + lruCache.get(3)); // 应该存在
        System.out.println("  4->" + lruCache.get(4)); // 应该存在
        
        // 4. 并查集演示
        System.out.println("\n4. 并查集演示:");
        UnionFind uf = new UnionFind(10);
        uf.union(0, 1);
        uf.union(1, 2);
        uf.union(3, 4);
        uf.union(5, 6);
        
        System.out.printf("0和2是否连通: %b%n", uf.connected(0, 2));
        System.out.printf("0和3是否连通: %b%n", uf.connected(0, 3));
        System.out.printf("连通分量数量: %d%n", uf.getCount());
        
        // 5. 线段树演示
        System.out.println("\n5. 线段树演示:");
        int[] segmentData = {1, 3, 5, 7, 9, 11};
        SegmentTree segmentTree = new SegmentTree(segmentData);
        System.out.printf("数组: %s%n", Arrays.toString(segmentData));
        System.out.printf("区间[1, 3]的和: %d%n", segmentTree.query(1, 3));
        
        segmentTree.update(1, 10);
        System.out.println("将索引1的值更新为10后:");
        System.out.printf("区间[1, 3]的和: %d%n", segmentTree.query(1, 3));
        
        // 6. 字典树演示
        System.out.println("\n6. 字典树演示:");
        Trie trie = new Trie();
        String[] words = {"apple", "app", "application", "apply", "banana"};
        for (String word : words) {
            trie.insert(word);
        }
        
        System.out.printf("'app' 是否存在: %b%n", trie.search("app"));
        System.out.printf("'appl' 是否存在: %b%n", trie.search("appl"));
        System.out.printf("是否存在以'app'开头的单词: %b%n", trie.startsWith("app"));
        System.out.printf("是否存在以'ban'开头的单词: %b%n", trie.startsWith("ban"));
        
        // 7. 后缀数组演示
        System.out.println("\n7. 后缀数组演示:");
        String text = "banana";
        SuffixArray suffixArray = new SuffixArray(text);
        System.out.printf("文本: %s%n", text);
        System.out.printf("后缀数组: %s%n", Arrays.toString(suffixArray.getSuffixes()));
        
        int[] matches = suffixArray.search("ana");
        System.out.printf("模式'ana'的匹配位置: %s%n", Arrays.toString(matches));
        
        // 8. 性能测试
        System.out.println("\n8. 高级数据结构性能测试:");
        AdvancedDataStructurePerformanceTest.testSkipList();
        AdvancedDataStructurePerformanceTest.testBloomFilter();
        AdvancedDataStructurePerformanceTest.testLRUCache();
    }
}