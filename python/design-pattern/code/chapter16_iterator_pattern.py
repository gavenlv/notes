"""
迭代器模式 (Iterator Pattern) 示例代码

迭代器模式提供一种方法顺序访问一个聚合对象中的各个元素，而又不暴露该对象的内部表示。
"""

from abc import ABC, abstractmethod
from typing import Any, List


class Iterator(ABC):
    """迭代器抽象类"""
    
    @abstractmethod
    def has_next(self) -> bool:
        """判断是否还有下一个元素"""
        pass
    
    @abstractmethod
    def next(self) -> Any:
        """获取下一个元素"""
        pass
    
    @abstractmethod
    def current(self) -> Any:
        """获取当前元素"""
        pass


class Aggregate(ABC):
    """聚合对象抽象类"""
    
    @abstractmethod
    def create_iterator(self) -> Iterator:
        """创建迭代器"""
        pass


class ConcreteIterator(Iterator):
    """具体迭代器"""
    
    def __init__(self, collection: List[Any]):
        self._collection = collection
        self._index = 0
    
    def has_next(self) -> bool:
        return self._index < len(self._collection)
    
    def next(self) -> Any:
        if self.has_next():
            item = self._collection[self._index]
            self._index += 1
            return item
        else:
            raise StopIteration("没有更多元素")
    
    def current(self) -> Any:
        if 0 <= self._index < len(self._collection):
            return self._collection[self._index]
        else:
            raise IndexError("索引超出范围")
    
    def reset(self):
        """重置迭代器"""
        self._index = 0


class ConcreteAggregate(Aggregate):
    """具体聚合对象"""
    
    def __init__(self):
        self._items: List[Any] = []
    
    def add_item(self, item: Any):
        """添加元素"""
        self._items.append(item)
    
    def remove_item(self, item: Any):
        """移除元素"""
        if item in self._items:
            self._items.remove(item)
    
    def get_item(self, index: int) -> Any:
        """获取指定位置的元素"""
        if 0 <= index < len(self._items):
            return self._items[index]
        else:
            raise IndexError("索引超出范围")
    
    def size(self) -> int:
        """获取元素数量"""
        return len(self._items)
    
    def create_iterator(self) -> Iterator:
        return ConcreteIterator(self._items)


# 测试基础迭代器模式
def test_basic_iterator():
    """测试基础迭代器模式"""
    print("=== 迭代器模式测试 - 基础示例 ===\n")
    
    # 创建聚合对象
    aggregate = ConcreteAggregate()
    aggregate.add_item("苹果")
    aggregate.add_item("香蕉")
    aggregate.add_item("橙子")
    aggregate.add_item("葡萄")
    
    # 创建迭代器
    iterator = aggregate.create_iterator()
    
    print("正向遍历:")
    while iterator.has_next():
        item = iterator.next()
        print(f"  {item}")
    
    print("\n重置迭代器并再次遍历:")
    iterator.reset()
    while iterator.has_next():
        item = iterator.next()
        print(f"  {item}")


# 实际应用示例：图书目录迭代器
def test_book_catalog():
    """测试图书目录迭代器"""
    print("\n=== 迭代器模式应用 - 图书目录示例 ===\n")
    
    class Book:
        """图书类"""
        
        def __init__(self, title: str, author: str, isbn: str):
            self.title = title
            self.author = author
            self.isbn = isbn
        
        def __str__(self):
            return f"《{self.title}》 - {self.author} (ISBN: {self.isbn})"
    
    class BookCatalog(Aggregate):
        """图书目录聚合类"""
        
        def __init__(self):
            self._books: List[Book] = []
        
        def add_book(self, book: Book):
            self._books.append(book)
        
        def remove_book(self, isbn: str):
            self._books = [book for book in self._books if book.isbn != isbn]
        
        def get_book_by_isbn(self, isbn: str) -> Book:
            for book in self._books:
                if book.isbn == isbn:
                    return book
            raise ValueError(f"未找到ISBN为 {isbn} 的图书")
        
        def create_iterator(self) -> Iterator:
            return BookIterator(self._books)
    
    class BookIterator(Iterator):
        """图书迭代器"""
        
        def __init__(self, books: List[Book]):
            self._books = books
            self._index = 0
        
        def has_next(self) -> bool:
            return self._index < len(self._books)
        
        def next(self) -> Book:
            if self.has_next():
                book = self._books[self._index]
                self._index += 1
                return book
            else:
                raise StopIteration("没有更多图书")
        
        def current(self) -> Book:
            if 0 <= self._index < len(self._books):
                return self._books[self._index]
            else:
                raise IndexError("索引超出范围")
        
        def reset(self):
            self._index = 0
    
    # 测试图书目录
    catalog = BookCatalog()
    catalog.add_book(Book("Python编程", "张三", "978-7-111-12345-6"))
    catalog.add_book(Book("设计模式", "李四", "978-7-111-12346-3"))
    catalog.add_book(Book("算法导论", "王五", "978-7-111-12347-0"))
    catalog.add_book(Book("数据库系统", "赵六", "978-7-111-12348-7"))
    
    iterator = catalog.create_iterator()
    
    print("图书目录:")
    while iterator.has_next():
        book = iterator.next()
        print(f"  {book}")


# 实际应用示例：二叉树迭代器
def test_binary_tree_iterator():
    """测试二叉树迭代器"""
    print("\n=== 迭代器模式应用 - 二叉树迭代器示例 ===\n")
    
    class TreeNode:
        """树节点"""
        
        def __init__(self, value):
            self.value = value
            self.left = None
            self.right = None
        
        def __str__(self):
            return str(self.value)
    
    class BinaryTree(Aggregate):
        """二叉树聚合类"""
        
        def __init__(self):
            self.root = None
        
        def insert(self, value):
            """插入节点"""
            if self.root is None:
                self.root = TreeNode(value)
            else:
                self._insert_recursive(self.root, value)
        
        def _insert_recursive(self, node, value):
            if value < node.value:
                if node.left is None:
                    node.left = TreeNode(value)
                else:
                    self._insert_recursive(node.left, value)
            else:
                if node.right is None:
                    node.right = TreeNode(value)
                else:
                    self._insert_recursive(node.right, value)
        
        def create_iterator(self, traversal_type="inorder") -> Iterator:
            """创建迭代器，支持不同遍历方式"""
            if traversal_type == "inorder":
                return InOrderIterator(self.root)
            elif traversal_type == "preorder":
                return PreOrderIterator(self.root)
            elif traversal_type == "postorder":
                return PostOrderIterator(self.root)
            else:
                raise ValueError("不支持的遍历方式")
    
    class InOrderIterator(Iterator):
        """中序遍历迭代器"""
        
        def __init__(self, root):
            self._stack = []
            self._current = root
            self._traverse_left()
        
        def _traverse_left(self):
            while self._current:
                self._stack.append(self._current)
                self._current = self._current.left
        
        def has_next(self) -> bool:
            return len(self._stack) > 0
        
        def next(self) -> TreeNode:
            if not self.has_next():
                raise StopIteration("没有更多节点")
            
            node = self._stack.pop()
            self._current = node.right
            self._traverse_left()
            return node
        
        def current(self) -> TreeNode:
            if self._stack:
                return self._stack[-1]
            else:
                raise IndexError("没有当前节点")
    
    class PreOrderIterator(Iterator):
        """前序遍历迭代器"""
        
        def __init__(self, root):
            self._stack = []
            if root:
                self._stack.append(root)
        
        def has_next(self) -> bool:
            return len(self._stack) > 0
        
        def next(self) -> TreeNode:
            if not self.has_next():
                raise StopIteration("没有更多节点")
            
            node = self._stack.pop()
            if node.right:
                self._stack.append(node.right)
            if node.left:
                self._stack.append(node.left)
            return node
        
        def current(self) -> TreeNode:
            if self._stack:
                return self._stack[-1]
            else:
                raise IndexError("没有当前节点")
    
    class PostOrderIterator(Iterator):
        """后序遍历迭代器"""
        
        def __init__(self, root):
            self._stack = []
            self._last_visited = None
            self._current = root
            self._traverse_left()
        
        def _traverse_left(self):
            while self._current:
                self._stack.append(self._current)
                self._current = self._current.left
        
        def has_next(self) -> bool:
            return len(self._stack) > 0
        
        def next(self) -> TreeNode:
            if not self.has_next():
                raise StopIteration("没有更多节点")
            
            node = self._stack[-1]
            
            # 如果右子树存在且未被访问过
            if node.right and node.right != self._last_visited:
                self._current = node.right
                self._traverse_left()
                return self.next()
            
            # 访问当前节点
            self._stack.pop()
            self._last_visited = node
            return node
        
        def current(self) -> TreeNode:
            if self._stack:
                return self._stack[-1]
            else:
                raise IndexError("没有当前节点")
    
    # 测试二叉树迭代器
    tree = BinaryTree()
    values = [5, 3, 7, 2, 4, 6, 8]
    
    for value in values:
        tree.insert(value)
    
    print("中序遍历:")
    iterator = tree.create_iterator("inorder")
    while iterator.has_next():
        node = iterator.next()
        print(f"  {node}")
    
    print("\n前序遍历:")
    iterator = tree.create_iterator("preorder")
    while iterator.has_next():
        node = iterator.next()
        print(f"  {node}")
    
    print("\n后序遍历:")
    iterator = tree.create_iterator("postorder")
    while iterator.has_next():
        node = iterator.next()
        print(f"  {node}")


# 实际应用示例：文件系统迭代器
def test_file_system_iterator():
    """测试文件系统迭代器"""
    print("\n=== 迭代器模式应用 - 文件系统迭代器示例 ===\n")
    
    class FileSystemItem:
        """文件系统项抽象类"""
        
        def __init__(self, name):
            self.name = name
        
        @abstractmethod
        def is_file(self) -> bool:
            pass
        
        @abstractmethod
        def is_directory(self) -> bool:
            pass
        
        def __str__(self):
            return self.name
    
    class File(FileSystemItem):
        """文件类"""
        
        def __init__(self, name, size):
            super().__init__(name)
            self.size = size
        
        def is_file(self) -> bool:
            return True
        
        def is_directory(self) -> bool:
            return False
        
        def __str__(self):
            return f"{self.name} ({self.size} bytes)"
    
    class Directory(FileSystemItem):
        """目录类"""
        
        def __init__(self, name):
            super().__init__(name)
            self._children: List[FileSystemItem] = []
        
        def add_item(self, item: FileSystemItem):
            self._children.append(item)
        
        def remove_item(self, item: FileSystemItem):
            if item in self._children:
                self._children.remove(item)
        
        def get_children(self) -> List[FileSystemItem]:
            return self._children.copy()
        
        def is_file(self) -> bool:
            return False
        
        def is_directory(self) -> bool:
            return True
        
        def create_iterator(self, recursive=False) -> Iterator:
            """创建迭代器"""
            if recursive:
                return RecursiveFileSystemIterator(self)
            else:
                return FileSystemIterator(self)
    
    class FileSystemIterator(Iterator):
        """文件系统迭代器（非递归）"""
        
        def __init__(self, directory: Directory):
            self._items = directory.get_children()
            self._index = 0
        
        def has_next(self) -> bool:
            return self._index < len(self._items)
        
        def next(self) -> FileSystemItem:
            if self.has_next():
                item = self._items[self._index]
                self._index += 1
                return item
            else:
                raise StopIteration("没有更多文件系统项")
        
        def current(self) -> FileSystemItem:
            if 0 <= self._index < len(self._items):
                return self._items[self._index]
            else:
                raise IndexError("索引超出范围")
    
    class RecursiveFileSystemIterator(Iterator):
        """递归文件系统迭代器"""
        
        def __init__(self, directory: Directory):
            self._stack = [directory]
            self._current_items = []
            self._current_index = 0
            self._prepare_next_items()
        
        def _prepare_next_items(self):
            """准备下一个要遍历的项目"""
            while self._stack:
                current_dir = self._stack.pop()
                items = current_dir.get_children()
                
                # 将子目录压入栈中（逆序，因为栈是后进先出）
                for item in reversed(items):
                    if item.is_directory():
                        self._stack.append(item)
                
                # 将当前目录的文件和目录添加到当前项目列表
                self._current_items.extend(items)
                
                if self._current_items:
                    break
        
        def has_next(self) -> bool:
            return len(self._current_items) > 0 or len(self._stack) > 0
        
        def next(self) -> FileSystemItem:
            if not self.has_next():
                raise StopIteration("没有更多文件系统项")
            
            if self._current_index >= len(self._current_items):
                self._current_items = []
                self._current_index = 0
                self._prepare_next_items()
            
            if self._current_index < len(self._current_items):
                item = self._current_items[self._current_index]
                self._current_index += 1
                return item
            else:
                raise StopIteration("没有更多文件系统项")
        
        def current(self) -> FileSystemItem:
            if 0 <= self._current_index < len(self._current_items):
                return self._current_items[self._current_index]
            else:
                raise IndexError("没有当前文件系统项")
    
    # 测试文件系统迭代器
    root = Directory("根目录")
    
    docs = Directory("文档")
    docs.add_item(File("报告.pdf", 1024))
    docs.add_item(File("简历.docx", 512))
    
    pictures = Directory("图片")
    pictures.add_item(File("照片1.jpg", 2048))
    pictures.add_item(File("照片2.jpg", 3072))
    
    vacation = Directory("假期")
    vacation.add_item(File("海滩.jpg", 4096))
    pictures.add_item(vacation)
    
    root.add_item(docs)
    root.add_item(pictures)
    root.add_item(File("readme.txt", 256))
    
    print("非递归遍历:")
    iterator = root.create_iterator(recursive=False)
    while iterator.has_next():
        item = iterator.next()
        print(f"  {item}")
    
    print("\n递归遍历:")
    iterator = root.create_iterator(recursive=True)
    while iterator.has_next():
        item = iterator.next()
        print(f"  {item}")


# Python内置迭代器协议示例
def test_python_iterator_protocol():
    """测试Python内置迭代器协议"""
    print("\n=== Python内置迭代器协议示例 ===\n")
    
    class FibonacciSequence:
        """斐波那契数列（实现迭代器协议）"""
        
        def __init__(self, max_count=10):
            self.max_count = max_count
            self.count = 0
            self.a, self.b = 0, 1
        
        def __iter__(self):
            """返回迭代器对象自身"""
            return self
        
        def __next__(self):
            """返回下一个斐波那契数"""
            if self.count >= self.max_count:
                raise StopIteration
            
            if self.count == 0:
                result = self.a
            elif self.count == 1:
                result = self.b
            else:
                result = self.a + self.b
                self.a, self.b = self.b, result
            
            self.count += 1
            return result
    
    class Range:
        """自定义范围类（实现迭代器协议）"""
        
        def __init__(self, start, stop, step=1):
            self.start = start
            self.stop = stop
            self.step = step
            self.current = start
        
        def __iter__(self):
            return self
        
        def __next__(self):
            if (self.step > 0 and self.current >= self.stop) or \
               (self.step < 0 and self.current <= self.stop):
                raise StopIteration
            
            result = self.current
            self.current += self.step
            return result
    
    # 测试斐波那契数列
    print("斐波那契数列（前10个）:")
    fib = FibonacciSequence(10)
    for num in fib:
        print(f"  {num}")
    
    print("\n自定义范围类:")
    custom_range = Range(1, 10, 2)
    for num in custom_range:
        print(f"  {num}")


if __name__ == "__main__":
    test_basic_iterator()
    test_book_catalog()
    test_binary_tree_iterator()
    test_file_system_iterator()
    test_python_iterator_protocol()
    
    print("\n=== 迭代器模式总结 ===")
    print("优点：")
    print("- 它支持以不同的方式遍历一个聚合对象")
    print("- 迭代器简化了聚合类")
    print("- 在同一个聚合上可以有多个遍历")
    print("- 在迭代器模式中，增加新的聚合类和迭代器类都很方便，无须修改原有代码")
    print("\n缺点：")
    print("- 由于迭代器模式将存储数据和遍历数据的职责分离，增加新的聚合类需要对应增加新的迭代器类")
    print("- 抽象迭代器的设计难度较大，需要充分考虑到系统将来的扩展")
    print("\n适用场景：")
    print("- 访问一个聚合对象的内容而无须暴露它的内部表示")
    print("- 需要为聚合对象提供多种遍历方式")
    print("- 为遍历不同的聚合结构提供一个统一的接口")
