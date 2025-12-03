/**
 * 第四章：树结构 - 二叉树、搜索树与平衡树
 * 示例代码
 */
import java.util.*;

// 二叉树节点定义
class TreeNode {
    int val;
    TreeNode left;
    TreeNode right;
    
    TreeNode() {}
    TreeNode(int val) { this.val = val; }
    TreeNode(int val, TreeNode left, TreeNode right) {
        this.val = val;
        this.left = left;
        this.right = right;
    }
}

// 二叉树基本操作
class BinaryTree {
    private TreeNode root;
    
    public BinaryTree() {
        this.root = null;
    }
    
    // 插入节点
    public void insert(int val) {
        root = insertRec(root, val);
        System.out.println("插入节点: " + val);
    }
    
    private TreeNode insertRec(TreeNode root, int val) {
        if (root == null) {
            return new TreeNode(val);
        }
        
        if (val < root.val) {
            root.left = insertRec(root.left, val);
        } else if (val > root.val) {
            root.right = insertRec(root.right, val);
        }
        
        return root;
    }
    
    // 查找节点
    public boolean search(int val) {
        boolean result = searchRec(root, val);
        System.out.println("查找节点 " + val + ": " + (result ? "找到" : "未找到"));
        return result;
    }
    
    private boolean searchRec(TreeNode root, int val) {
        if (root == null) {
            return false;
        }
        
        if (val == root.val) {
            return true;
        }
        
        if (val < root.val) {
            return searchRec(root.left, val);
        } else {
            return searchRec(root.right, val);
        }
    }
    
    // 删除节点
    public void delete(int val) {
        root = deleteRec(root, val);
        System.out.println("删除节点: " + val);
    }
    
    private TreeNode deleteRec(TreeNode root, int val) {
        if (root == null) {
            return root;
        }
        
        if (val < root.val) {
            root.left = deleteRec(root.left, val);
        } else if (val > root.val) {
            root.right = deleteRec(root.right, val);
        } else {
            // 找到要删除的节点
            if (root.left == null) {
                return root.right;
            } else if (root.right == null) {
                return root.left;
            }
            
            // 节点有两个子节点，找到右子树的最小值
            root.val = minValue(root.right);
            
            // 删除右子树的最小值节点
            root.right = deleteRec(root.right, root.val);
        }
        
        return root;
    }
    
    private int minValue(TreeNode root) {
        int minValue = root.val;
        while (root.left != null) {
            minValue = root.left.val;
            root = root.left;
        }
        return minValue;
    }
    
    // 前序遍历（根-左-右）
    public void preorderTraversal() {
        System.out.print("前序遍历: ");
        preorderRec(root);
        System.out.println();
    }
    
    private void preorderRec(TreeNode root) {
        if (root != null) {
            System.out.print(root.val + " ");
            preorderRec(root.left);
            preorderRec(root.right);
        }
    }
    
    // 中序遍历（左-根-右）
    public void inorderTraversal() {
        System.out.print("中序遍历: ");
        inorderRec(root);
        System.out.println();
    }
    
    private void inorderRec(TreeNode root) {
        if (root != null) {
            inorderRec(root.left);
            System.out.print(root.val + " ");
            inorderRec(root.right);
        }
    }
    
    // 后序遍历（左-右-根）
    public void postorderTraversal() {
        System.out.print("后序遍历: ");
        postorderRec(root);
        System.out.println();
    }
    
    private void postorderRec(TreeNode root) {
        if (root != null) {
            postorderRec(root.left);
            postorderRec(root.right);
            System.out.print(root.val + " ");
        }
    }
    
    // 层序遍历（广度优先遍历）
    public void levelOrderTraversal() {
        if (root == null) {
            System.out.println("层序遍历: 树为空");
            return;
        }
        
        Queue<TreeNode> queue = new LinkedList<>();
        queue.offer(root);
        System.out.print("层序遍历: ");
        
        while (!queue.isEmpty()) {
            TreeNode current = queue.poll();
            System.out.print(current.val + " ");
            
            if (current.left != null) {
                queue.offer(current.left);
            }
            
            if (current.right != null) {
                queue.offer(current.right);
            }
        }
        System.out.println();
    }
}

// 使用二叉搜索树实现有序集合
class BSTSet {
    private TreeNode root;
    private int size;
    
    public BSTSet() {
        this.root = null;
        this.size = 0;
    }
    
    // 添加元素
    public void add(int val) {
        if (!contains(val)) {
            root = insertRec(root, val);
            size++;
            System.out.println("添加元素: " + val);
        } else {
            System.out.println("元素已存在: " + val);
        }
    }
    
    private TreeNode insertRec(TreeNode root, int val) {
        if (root == null) {
            return new TreeNode(val);
        }
        
        if (val < root.val) {
            root.left = insertRec(root.left, val);
        } else if (val > root.val) {
            root.right = insertRec(root.right, val);
        }
        
        return root;
    }
    
    // 检查是否包含元素
    public boolean contains(int val) {
        return searchRec(root, val);
    }
    
    private boolean searchRec(TreeNode root, int val) {
        if (root == null) {
            return false;
        }
        
        if (val == root.val) {
            return true;
        }
        
        if (val < root.val) {
            return searchRec(root.left, val);
        } else {
            return searchRec(root.right, val);
        }
    }
    
    // 删除元素
    public void remove(int val) {
        if (contains(val)) {
            root = deleteRec(root, val);
            size--;
            System.out.println("删除元素: " + val);
        } else {
            System.out.println("元素不存在: " + val);
        }
    }
    
    private TreeNode deleteRec(TreeNode root, int val) {
        if (root == null) {
            return root;
        }
        
        if (val < root.val) {
            root.left = deleteRec(root.left, val);
        } else if (val > root.val) {
            root.right = deleteRec(root.right, val);
        } else {
            // 找到要删除的节点
            if (root.left == null) {
                return root.right;
            } else if (root.right == null) {
                return root.left;
            }
            
            // 节点有两个子节点，找到右子树的最小值
            root.val = minValue(root.right);
            
            // 删除右子树的最小值节点
            root.right = deleteRec(root.right, root.val);
        }
        
        return root;
    }
    
    private int minValue(TreeNode root) {
        int minValue = root.val;
        while (root.left != null) {
            minValue = root.left.val;
            root = root.left;
        }
        return minValue;
    }
    
    // 获取集合大小
    public int size() {
        return size;
    }
    
    // 中序遍历打印所有元素
    public void printElements() {
        System.out.print("集合元素: ");
        inorderRec(root);
        System.out.println();
    }
    
    private void inorderRec(TreeNode root) {
        if (root != null) {
            inorderRec(root.left);
            System.out.print(root.val + " ");
            inorderRec(root.right);
        }
    }
}

// AVL树节点定义
class AVLNode {
    int val;
    AVLNode left;
    AVLNode right;
    int height;
    
    AVLNode(int val) {
        this.val = val;
        this.height = 1;
    }
}

// AVL树实现
class AVLTree {
    private AVLNode root;
    
    // 获取节点高度
    private int getHeight(AVLNode node) {
        if (node == null) {
            return 0;
        }
        return node.height;
    }
    
    // 获取平衡因子
    private int getBalance(AVLNode node) {
        if (node == null) {
            return 0;
        }
        return getHeight(node.left) - getHeight(node.right);
    }
    
    // 右旋
    private AVLNode rightRotate(AVLNode y) {
        AVLNode x = y.left;
        AVLNode T2 = x.right;
        
        // 执行旋转
        x.right = y;
        y.left = T2;
        
        // 更新高度
        y.height = Math.max(getHeight(y.left), getHeight(y.right)) + 1;
        x.height = Math.max(getHeight(x.left), getHeight(x.right)) + 1;
        
        // 返回新的根节点
        return x;
    }
    
    // 左旋
    private AVLNode leftRotate(AVLNode x) {
        AVLNode y = x.right;
        AVLNode T2 = y.left;
        
        // 执行旋转
        y.left = x;
        x.right = T2;
        
        // 更新高度
        x.height = Math.max(getHeight(x.left), getHeight(x.right)) + 1;
        y.height = Math.max(getHeight(y.left), getHeight(y.right)) + 1;
        
        // 返回新的根节点
        return y;
    }
    
    // 插入节点
    public void insert(int val) {
        root = insertRec(root, val);
        System.out.println("AVL树插入节点: " + val);
    }
    
    private AVLNode insertRec(AVLNode node, int val) {
        // 1. 执行正常的BST插入
        if (node == null) {
            return new AVLNode(val);
        }
        
        if (val < node.val) {
            node.left = insertRec(node.left, val);
        } else if (val > node.val) {
            node.right = insertRec(node.right, val);
        } else {
            // 相等的值不插入
            return node;
        }
        
        // 2. 更新当前节点的高度
        node.height = 1 + Math.max(getHeight(node.left), getHeight(node.right));
        
        // 3. 获取平衡因子
        int balance = getBalance(node);
        
        // 4. 如果节点不平衡，进行相应的旋转
        
        // Left Left Case
        if (balance > 1 && val < node.left.val) {
            return rightRotate(node);
        }
        
        // Right Right Case
        if (balance < -1 && val > node.right.val) {
            return leftRotate(node);
        }
        
        // Left Right Case
        if (balance > 1 && val > node.left.val) {
            node.left = leftRotate(node.left);
            return rightRotate(node);
        }
        
        // Right Left Case
        if (balance < -1 && val < node.right.val) {
            node.right = rightRotate(node.right);
            return leftRotate(node);
        }
        
        // 返回未修改的节点指针
        return node;
    }
    
    // 中序遍历
    public void inorderTraversal() {
        System.out.print("AVL树中序遍历: ");
        inorderRec(root);
        System.out.println();
    }
    
    private void inorderRec(AVLNode root) {
        if (root != null) {
            inorderRec(root.left);
            System.out.print(root.val + " ");
            inorderRec(root.right);
        }
    }
}

// 简化的文件系统节点
class FileSystemNode {
    String name;
    boolean isDirectory;
    List<FileSystemNode> children;
    String content;  // 仅对文件有效
    
    public FileSystemNode(String name, boolean isDirectory) {
        this.name = name;
        this.isDirectory = isDirectory;
        if (isDirectory) {
            this.children = new ArrayList<>();
        }
    }
    
    // 添加子节点
    public void addChild(FileSystemNode child) {
        if (isDirectory && children != null) {
            children.add(child);
        }
    }
    
    // 查找子节点
    public FileSystemNode findChild(String name) {
        if (!isDirectory || children == null) {
            return null;
        }
        
        for (FileSystemNode child : children) {
            if (child.name.equals(name)) {
                return child;
            }
        }
        return null;
    }
}

// 表达式树节点
class ExpressionNode {
    char value;
    ExpressionNode left, right;
    
    public ExpressionNode(char value) {
        this.value = value;
        this.left = this.right = null;
    }
}

// 表达式树构建和计算
class ExpressionTree {
    // 根据后缀表达式构建表达式树
    public ExpressionNode buildExpressionTree(String postfix) {
        Stack<ExpressionNode> stack = new Stack<>();
        
        for (char ch : postfix.toCharArray()) {
            if (isOperand(ch)) {
                stack.push(new ExpressionNode(ch));
            } else {
                ExpressionNode node = new ExpressionNode(ch);
                node.right = stack.pop();
                node.left = stack.pop();
                stack.push(node);
            }
        }
        
        return stack.pop();
    }
    
    // 计算表达式树的值
    public int evaluate(ExpressionNode root) {
        if (root == null) {
            return 0;
        }
        
        // 如果是叶子节点（操作数）
        if (root.left == null && root.right == null) {
            return root.value - '0';  // 简化处理，假设是单数字
        }
        
        // 递归计算左右子树
        int leftVal = evaluate(root.left);
        int rightVal = evaluate(root.right);
        
        // 根据操作符计算结果
        switch (root.value) {
            case '+': return leftVal + rightVal;
            case '-': return leftVal - rightVal;
            case '*': return leftVal * rightVal;
            case '/': return leftVal / rightVal;
        }
        
        return 0;
    }
    
    private boolean isOperand(char ch) {
        return Character.isDigit(ch);
    }
}

public class Chapter4Example {
    public static void main(String[] args) {
        System.out.println("=== 第四章：树结构示例 ===\n");
        
        // 1. 二叉树操作演示
        System.out.println("1. 二叉树操作演示:");
        BinaryTree tree = new BinaryTree();
        int[] values = {50, 30, 70, 20, 40, 60, 80};
        
        // 插入节点
        for (int val : values) {
            tree.insert(val);
        }
        
        // 遍历
        tree.inorderTraversal();    // 应该输出有序序列
        tree.preorderTraversal();
        tree.postorderTraversal();
        tree.levelOrderTraversal();
        
        // 查找
        tree.search(40);
        tree.search(90);
        
        // 删除
        tree.delete(20);  // 删除叶子节点
        tree.inorderTraversal();
        tree.delete(30);  // 删除有两个子节点的节点
        tree.inorderTraversal();
        System.out.println();
        
        // 2. 二叉搜索树集合演示
        System.out.println("2. 二叉搜索树集合演示:");
        BSTSet bstSet = new BSTSet();
        int[] setValues = {5, 3, 7, 2, 4, 6, 8};
        
        // 添加元素
        for (int val : setValues) {
            bstSet.add(val);
        }
        bstSet.add(5);  // 重复元素
        
        // 显示元素
        bstSet.printElements();
        System.out.println("集合大小: " + bstSet.size());
        
        // 查找元素
        System.out.println("是否包含3: " + bstSet.contains(3));
        System.out.println("是否包含9: " + bstSet.contains(9));
        
        // 删除元素
        bstSet.remove(3);
        bstSet.remove(9);  // 不存在的元素
        bstSet.printElements();
        System.out.println("集合大小: " + bstSet.size());
        System.out.println();
        
        // 3. AVL树演示
        System.out.println("3. AVL树演示:");
        AVLTree avlTree = new AVLTree();
        int[] avlValues = {10, 20, 30, 40, 50, 25};  // 这些值会触发旋转操作
        
        for (int val : avlValues) {
            avlTree.insert(val);
        }
        avlTree.inorderTraversal();
        System.out.println();
        
        // 4. 表达式树演示
        System.out.println("4. 表达式树演示:");
        ExpressionTree exprTree = new ExpressionTree();
        // 表达式: (3 + 2) * (4 - 1) 对应的后缀表达式: 32+41-*
        String postfixExpr = "32+41-*";
        ExpressionNode root = exprTree.buildExpressionTree(postfixExpr);
        System.out.println("后缀表达式: " + postfixExpr);
        System.out.println("计算结果: " + exprTree.evaluate(root));
        System.out.println();
        
        // 5. 文件系统节点演示
        System.out.println("5. 文件系统节点演示:");
        FileSystemNode rootDir = new FileSystemNode("root", true);
        FileSystemNode homeDir = new FileSystemNode("home", true);
        FileSystemNode userDir = new FileSystemNode("user", true);
        FileSystemNode file1 = new FileSystemNode("document.txt", false);
        FileSystemNode file2 = new FileSystemNode("image.jpg", false);
        
        rootDir.addChild(homeDir);
        homeDir.addChild(userDir);
        userDir.addChild(file1);
        userDir.addChild(file2);
        
        System.out.println("创建了文件系统结构:");
        System.out.println("root/");
        System.out.println("  home/");
        System.out.println("    user/");
        System.out.println("      document.txt");
        System.out.println("      image.jpg");
        System.out.println();
        
        // 查找演示
        FileSystemNode found = rootDir.findChild("home");
        System.out.println("查找 'home': " + (found != null ? "找到" : "未找到"));
        found = homeDir.findChild("nonexistent");
        System.out.println("查找 'nonexistent': " + (found != null ? "找到" : "未找到"));
    }
}