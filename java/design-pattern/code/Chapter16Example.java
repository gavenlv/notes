import java.util.*;

// 抽象迭代器接口
interface Iterator<T> {
    boolean hasNext();
    T next();
    void remove();
}

// 抽象聚合接口
interface Aggregate<T> {
    Iterator<T> createIterator();
}

// 具体聚合类 - 字符串列表
class StringList implements Aggregate<String> {
    private String[] items;
    private int size;
    private int capacity;
    
    public StringList() {
        this.capacity = 10;
        this.items = new String[capacity];
        this.size = 0;
    }
    
    public StringList(int capacity) {
        this.capacity = capacity;
        this.items = new String[capacity];
        this.size = 0;
    }
    
    public void add(String item) {
        if (size >= capacity) {
            resize();
        }
        items[size++] = item;
    }
    
    public String get(int index) {
        if (index < 0 || index >= size) {
            throw new IndexOutOfBoundsException("Index: " + index + ", Size: " + size);
        }
        return items[index];
    }
    
    public int size() {
        return size;
    }
    
    private void resize() {
        capacity *= 2;
        String[] newItems = new String[capacity];
        System.arraycopy(items, 0, newItems, 0, size);
        items = newItems;
    }
    
    @Override
    public Iterator<String> createIterator() {
        return new StringListIterator();
    }
    
    // 具体内迭代器
    private class StringListIterator implements Iterator<String> {
        private int currentIndex = 0;
        
        @Override
        public boolean hasNext() {
            return currentIndex < size;
        }
        
        @Override
        public String next() {
            if (!hasNext()) {
                throw new NoSuchElementException();
            }
            return items[currentIndex++];
        }
        
        @Override
        public void remove() {
            if (currentIndex <= 0) {
                throw new IllegalStateException();
            }
            // 简单实现，实际应该更复杂
            for (int i = currentIndex - 1; i < size - 1; i++) {
                items[i] = items[i + 1];
            }
            items[--size] = null;
            currentIndex--;
        }
    }
}

// 双向迭代器接口
interface BidirectionalIterator<T> extends Iterator<T> {
    boolean hasPrevious();
    T previous();
    int nextIndex();
    int previousIndex();
}

// 双向列表实现
class BidirectionalList<T> {
    private Object[] elements;
    private int size;
    private int capacity;
    
    public BidirectionalList() {
        this.capacity = 10;
        this.elements = new Object[capacity];
        this.size = 0;
    }
    
    public void add(T element) {
        if (size >= capacity) {
            resize();
        }
        elements[size++] = element;
    }
    
    @SuppressWarnings("unchecked")
    public T get(int index) {
        if (index < 0 || index >= size) {
            throw new IndexOutOfBoundsException("Index: " + index + ", Size: " + size);
        }
        return (T) elements[index];
    }
    
    public int size() {
        return size;
    }
    
    private void resize() {
        capacity *= 2;
        Object[] newElements = new Object[capacity];
        System.arraycopy(elements, 0, newElements, 0, size);
        elements = newElements;
    }
    
    public BidirectionalIterator<T> bidirectionalIterator() {
        return new BidirectionalListIterator(0);
    }
    
    public BidirectionalIterator<T> bidirectionalIterator(int index) {
        return new BidirectionalListIterator(index);
    }
    
    // 双向迭代器实现
    private class BidirectionalListIterator implements BidirectionalIterator<T> {
        private int currentIndex;
        
        public BidirectionalListIterator(int index) {
            this.currentIndex = index;
        }
        
        @Override
        public boolean hasNext() {
            return currentIndex < size;
        }
        
        @Override
        @SuppressWarnings("unchecked")
        public T next() {
            if (!hasNext()) {
                throw new NoSuchElementException();
            }
            return (T) elements[currentIndex++];
        }
        
        @Override
        public boolean hasPrevious() {
            return currentIndex > 0;
        }
        
        @Override
        @SuppressWarnings("unchecked")
        public T previous() {
            if (!hasPrevious()) {
                throw new NoSuchElementException();
            }
            return (T) elements[--currentIndex];
        }
        
        @Override
        public int nextIndex() {
            return currentIndex;
        }
        
        @Override
        public int previousIndex() {
            return currentIndex - 1;
        }
        
        @Override
        public void remove() {
            if (currentIndex <= 0) {
                throw new IllegalStateException();
            }
            for (int i = currentIndex - 1; i < size - 1; i++) {
                elements[i] = elements[i + 1];
            }
            elements[--size] = null;
            currentIndex--;
        }
    }
}

// 树节点定义
class TreeNode<T> {
    T data;
    TreeNode<T> left;
    TreeNode<T> right;
    
    public TreeNode(T data) {
        this.data = data;
    }
}

// 树的迭代器接口
interface TreeIterator<T> extends Iterator<T> {
    // 前序遍历
    void setPreOrder();
    // 中序遍历
    void setInOrder();
    // 后序遍历
    void setPostOrder();
}

// 二叉树实现
class BinaryTree<T> {
    private TreeNode<T> root;
    
    public void setRoot(TreeNode<T> root) {
        this.root = root;
    }
    
    public TreeNode<T> getRoot() {
        return root;
    }
    
    public TreeIterator<T> createIterator() {
        return new BinaryTreeIterator();
    }
    
    // 二叉树迭代器实现
    private class BinaryTreeIterator implements TreeIterator<T> {
        private List<T> traversalResult;
        private int currentIndex;
        private int traversalType; // 0: pre-order, 1: in-order, 2: post-order
        
        public BinaryTreeIterator() {
            this.traversalResult = new ArrayList<>();
            this.currentIndex = 0;
            this.traversalType = 1; // 默认中序遍历
            performTraversal();
        }
        
        private void performTraversal() {
            traversalResult.clear();
            switch (traversalType) {
                case 0: // 前序遍历
                    preOrderTraversal(root);
                    break;
                case 1: // 中序遍历
                    inOrderTraversal(root);
                    break;
                case 2: // 后序遍历
                    postOrderTraversal(root);
                    break;
            }
        }
        
        private void preOrderTraversal(TreeNode<T> node) {
            if (node != null) {
                traversalResult.add(node.data);
                preOrderTraversal(node.left);
                preOrderTraversal(node.right);
            }
        }
        
        private void inOrderTraversal(TreeNode<T> node) {
            if (node != null) {
                inOrderTraversal(node.left);
                traversalResult.add(node.data);
                inOrderTraversal(node.right);
            }
        }
        
        private void postOrderTraversal(TreeNode<T> node) {
            if (node != null) {
                postOrderTraversal(node.left);
                postOrderTraversal(node.right);
                traversalResult.add(node.data);
            }
        }
        
        @Override
        public void setPreOrder() {
            this.traversalType = 0;
            currentIndex = 0;
            performTraversal();
        }
        
        @Override
        public void setInOrder() {
            this.traversalType = 1;
            currentIndex = 0;
            performTraversal();
        }
        
        @Override
        public void setPostOrder() {
            this.traversalType = 2;
            currentIndex = 0;
            performTraversal();
        }
        
        @Override
        public boolean hasNext() {
            return currentIndex < traversalResult.size();
        }
        
        @Override
        public T next() {
            if (!hasNext()) {
                throw new NoSuchElementException();
            }
            return traversalResult.get(currentIndex++);
        }
        
        @Override
        public void remove() {
            throw new UnsupportedOperationException("Remove operation is not supported");
        }
    }
}

// 过滤器接口
interface Filter<T> {
    boolean accept(T item);
}

// 过滤迭代器实现
class FilterIterator<T> implements java.util.Iterator<T> {
    private java.util.Iterator<T> iterator;
    private Filter<T> filter;
    private T nextItem;
    private boolean hasNextItem;
    
    public FilterIterator(java.util.Iterator<T> iterator, Filter<T> filter) {
        this.iterator = iterator;
        this.filter = filter;
        findNext();
    }
    
    private void findNext() {
        hasNextItem = false;
        while (iterator.hasNext()) {
            nextItem = iterator.next();
            if (filter.accept(nextItem)) {
                hasNextItem = true;
                break;
            }
        }
    }
    
    @Override
    public boolean hasNext() {
        return hasNextItem;
    }
    
    @Override
    public T next() {
        if (!hasNextItem) {
            throw new NoSuchElementException();
        }
        T result = nextItem;
        findNext();
        return result;
    }
    
    @Override
    public void remove() {
        iterator.remove();
    }
}

// 跳过迭代器
class SkipIterator<T> implements java.util.Iterator<T> {
    private java.util.Iterator<T> iterator;
    private int skipCount;
    private int currentSkip;
    
    public SkipIterator(java.util.Iterator<T> iterator, int skipCount) {
        this.iterator = iterator;
        this.skipCount = skipCount;
        this.currentSkip = 0;
    }
    
    @Override
    public boolean hasNext() {
        return iterator.hasNext();
    }
    
    @Override
    public T next() {
        while (iterator.hasNext() && currentSkip < skipCount) {
            iterator.next();
            currentSkip++;
        }
        
        if (!iterator.hasNext()) {
            throw new NoSuchElementException();
        }
        
        currentSkip = 0;
        return iterator.next();
    }
    
    @Override
    public void remove() {
        iterator.remove();
    }
}

public class Chapter16Example {
    public static void main(String[] args) {
        System.out.println("=== 迭代器模式示例 ===\n");
        
        // 1. 基本迭代器示例
        System.out.println("1. 基本迭代器示例:");
        basicIteratorExample();
        
        // 2. 双向迭代器示例
        System.out.println("\n2. 双向迭代器示例:");
        bidirectionalIteratorExample();
        
        // 3. 树结构迭代器示例
        System.out.println("\n3. 树结构迭代器示例:");
        treeIteratorExample();
        
        // 4. 过滤迭代器示例
        System.out.println("\n4. 过滤迭代器示例:");
        filterIteratorExample();
    }
    
    // 基本迭代器示例
    public static void basicIteratorExample() {
        StringList stringList = new StringList();
        stringList.add("Apple");
        stringList.add("Banana");
        stringList.add("Cherry");
        stringList.add("Date");
        stringList.add("Elderberry");
        
        Iterator<String> iterator = stringList.createIterator();
        System.out.println("正向遍历:");
        while (iterator.hasNext()) {
            System.out.println("  " + iterator.next());
        }
    }
    
    // 双向迭代器示例
    public static void bidirectionalIteratorExample() {
        BidirectionalList<String> list = new BidirectionalList<>();
        list.add("A");
        list.add("B");
        list.add("C");
        list.add("D");
        list.add("E");
        
        // 正向遍历
        System.out.println("正向遍历:");
        BidirectionalIterator<String> forwardIterator = list.bidirectionalIterator();
        while (forwardIterator.hasNext()) {
            System.out.println("  " + forwardIterator.next() + " (nextIndex: " + forwardIterator.nextIndex() + ")");
        }
        
        // 反向遍历
        System.out.println("反向遍历:");
        BidirectionalIterator<String> backwardIterator = list.bidirectionalIterator(list.size());
        while (backwardIterator.hasPrevious()) {
            System.out.println("  " + backwardIterator.previous() + " (previousIndex: " + backwardIterator.previousIndex() + ")");
        }
    }
    
    // 树结构迭代器示例
    public static void treeIteratorExample() {
        // 构建二叉树
        //       1
        //      / \
        //     2   3
        //    / \
        //   4   5
        BinaryTree<Integer> tree = new BinaryTree<>();
        TreeNode<Integer> root = new TreeNode<>(1);
        root.left = new TreeNode<>(2);
        root.right = new TreeNode<>(3);
        root.left.left = new TreeNode<>(4);
        root.left.right = new TreeNode<>(5);
        tree.setRoot(root);
        
        TreeIterator<Integer> iterator = tree.createIterator();
        
        // 中序遍历
        System.out.println("中序遍历:");
        iterator.setInOrder();
        while (iterator.hasNext()) {
            System.out.println("  " + iterator.next());
        }
        
        // 前序遍历
        System.out.println("前序遍历:");
        iterator.setPreOrder();
        while (iterator.hasNext()) {
            System.out.println("  " + iterator.next());
        }
        
        // 后序遍历
        System.out.println("后序遍历:");
        iterator.setPostOrder();
        while (iterator.hasNext()) {
            System.out.println("  " + iterator.next());
        }
    }
    
    // 过滤迭代器示例
    public static void filterIteratorExample() {
        List<Integer> numbers = Arrays.asList(1, 2, 3, 4, 5, 6, 7, 8, 9, 10);
        
        // 过滤出偶数
        Filter<Integer> evenFilter = new Filter<Integer>() {
            @Override
            public boolean accept(Integer item) {
                return item % 2 == 0;
            }
        };
        
        FilterIterator<Integer> evenIterator = new FilterIterator<>(numbers.iterator(), evenFilter);
        System.out.println("偶数过滤:");
        while (evenIterator.hasNext()) {
            System.out.println("  " + evenIterator.next());
        }
        
        // 过滤出大于5的数
        Filter<Integer> greaterThanFiveFilter = new Filter<Integer>() {
            @Override
            public boolean accept(Integer item) {
                return item > 5;
            }
        };
        
        FilterIterator<Integer> greaterIterator = new FilterIterator<>(numbers.iterator(), greaterThanFiveFilter);
        System.out.println("大于5的数过滤:");
        while (greaterIterator.hasNext()) {
            System.out.println("  " + greaterIterator.next());
        }
    }
}