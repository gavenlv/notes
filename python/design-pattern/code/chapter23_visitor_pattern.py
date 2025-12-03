"""
第23章：访问者模式 (Visitor Pattern)

访问者模式是一种行为设计模式，它允许你将算法与对象结构分离，
使得可以在不修改现有对象结构的情况下定义新的操作。
"""

from abc import ABC, abstractmethod
from typing import List


class Element(ABC):
    """元素接口"""
    
    @abstractmethod
    def accept(self, visitor) -> None:
        """接受访问者"""
        pass


class Visitor(ABC):
    """访问者接口"""
    
    @abstractmethod
    def visit_concrete_element_a(self, element) -> None:
        """访问具体元素A"""
        pass
    
    @abstractmethod
    def visit_concrete_element_b(self, element) -> None:
        """访问具体元素B"""
        pass


class ConcreteElementA(Element):
    """具体元素A"""
    
    def __init__(self, name: str, value: int):
        self.name = name
        self.value = value
    
    def accept(self, visitor: Visitor) -> None:
        visitor.visit_concrete_element_a(self)
    
    def operation_a(self) -> str:
        return f"元素A操作: {self.name} - {self.value}"


class ConcreteElementB(Element):
    """具体元素B"""
    
    def __init__(self, title: str, data: List[str]):
        self.title = title
        self.data = data
    
    def accept(self, visitor: Visitor) -> None:
        visitor.visit_concrete_element_b(self)
    
    def operation_b(self) -> str:
        return f"元素B操作: {self.title} - {len(self.data)} 项数据"


# 示例1：文档元素访问
class DocumentElement(ABC):
    """文档元素接口"""
    
    @abstractmethod
    def accept(self, visitor) -> None:
        pass


class DocumentVisitor(ABC):
    """文档访问者接口"""
    
    @abstractmethod
    def visit_paragraph(self, paragraph) -> None:
        pass
    
    @abstractmethod
    def visit_heading(self, heading) -> None:
        pass
    
    @abstractmethod
    def visit_image(self, image) -> None:
        pass
    
    @abstractmethod
    def visit_table(self, table) -> None:
        pass


class Paragraph(DocumentElement):
    """段落元素"""
    
    def __init__(self, text: str):
        self.text = text
    
    def accept(self, visitor: DocumentVisitor) -> None:
        visitor.visit_paragraph(self)


class Heading(DocumentElement):
    """标题元素"""
    
    def __init__(self, level: int, text: str):
        self.level = level
        self.text = text
    
    def accept(self, visitor: DocumentVisitor) -> None:
        visitor.visit_heading(self)


class Image(DocumentElement):
    """图片元素"""
    
    def __init__(self, src: str, alt: str, width: int, height: int):
        self.src = src
        self.alt = alt
        self.width = width
        self.height = height
    
    def accept(self, visitor: DocumentVisitor) -> None:
        visitor.visit_image(self)


class Table(DocumentElement):
    """表格元素"""
    
    def __init__(self, rows: int, cols: int, data: List[List[str]]):
        self.rows = rows
        self.cols = cols
        self.data = data
    
    def accept(self, visitor: DocumentVisitor) -> None:
        visitor.visit_table(self)


class HTMLExportVisitor(DocumentVisitor):
    """HTML导出访问者"""
    
    def __init__(self):
        self.html_content = []
    
    def visit_paragraph(self, paragraph: Paragraph) -> None:
        self.html_content.append(f"<p>{paragraph.text}</p>")
    
    def visit_heading(self, heading: Heading) -> None:
        self.html_content.append(f"<h{heading.level}>{heading.text}</h{heading.level}>")
    
    def visit_image(self, image: Image) -> None:
        self.html_content.append(
            f'<img src="{image.src}" alt="{image.alt}" width="{image.width}" height="{image.height}">'
        )
    
    def visit_table(self, table: Table) -> None:
        html_table = ["<table border='1'>"]
        for row in table.data:
            html_table.append("<tr>")
            for cell in row:
                html_table.append(f"<td>{cell}</td>")
            html_table.append("</tr>")
        html_table.append("</table>")
        self.html_content.append('\n'.join(html_table))
    
    def get_html(self) -> str:
        return '\n'.join(self.html_content)


class PlainTextExportVisitor(DocumentVisitor):
    """纯文本导出访问者"""
    
    def __init__(self):
        self.text_content = []
    
    def visit_paragraph(self, paragraph: Paragraph) -> None:
        self.text_content.append(paragraph.text)
    
    def visit_heading(self, heading: Heading) -> None:
        self.text_content.append(f"{'#' * heading.level} {heading.text}")
    
    def visit_image(self, image: Image) -> None:
        self.text_content.append(f"[图片: {image.alt}]")
    
    def visit_table(self, table: Table) -> None:
        self.text_content.append("[表格数据]")
        for i, row in enumerate(table.data):
            self.text_content.append(f"行{i+1}: {' | '.join(row)}")
    
    def get_text(self) -> str:
        return '\n'.join(self.text_content)


class WordCountVisitor(DocumentVisitor):
    """字数统计访问者"""
    
    def __init__(self):
        self.word_count = 0
        self.element_count = 0
    
    def visit_paragraph(self, paragraph: Paragraph) -> None:
        self.element_count += 1
        self.word_count += len(paragraph.text.split())
    
    def visit_heading(self, heading: Heading) -> None:
        self.element_count += 1
        self.word_count += len(heading.text.split())
    
    def visit_image(self, image: Image) -> None:
        self.element_count += 1
        # 图片不计入字数
    
    def visit_table(self, table: Table) -> None:
        self.element_count += 1
        for row in table.data:
            for cell in row:
                self.word_count += len(cell.split())
    
    def get_stats(self) -> dict:
        return {
            'element_count': self.element_count,
            'word_count': self.word_count
        }


class Document:
    """文档类"""
    
    def __init__(self):
        self.elements: List[DocumentElement] = []
    
    def add_element(self, element: DocumentElement) -> None:
        self.elements.append(element)
    
    def accept(self, visitor: DocumentVisitor) -> None:
        for element in self.elements:
            element.accept(visitor)


# 示例2：购物车访问
class ShoppingItem(ABC):
    """购物项接口"""
    
    @abstractmethod
    def accept(self, visitor) -> None:
        pass


class ShoppingCartVisitor(ABC):
    """购物车访问者接口"""
    
    @abstractmethod
    def visit_book(self, book) -> None:
        pass
    
    @abstractmethod
    def visit_electronics(self, electronics) -> None:
        pass
    
    @abstractmethod
    def visit_clothing(self, clothing) -> None:
        pass


class Book(ShoppingItem):
    """书籍类"""
    
    def __init__(self, title: str, author: str, price: float, isbn: str):
        self.title = title
        self.author = author
        self.price = price
        self.isbn = isbn
    
    def accept(self, visitor: ShoppingCartVisitor) -> None:
        visitor.visit_book(self)


class Electronics(ShoppingItem):
    """电子产品类"""
    
    def __init__(self, name: str, brand: str, price: float, warranty_months: int):
        self.name = name
        self.brand = brand
        self.price = price
        self.warranty_months = warranty_months
    
    def accept(self, visitor: ShoppingCartVisitor) -> None:
        visitor.visit_electronics(self)


class Clothing(ShoppingItem):
    """服装类"""
    
    def __init__(self, name: str, size: str, color: str, price: float):
        self.name = name
        self.size = size
        self.color = color
        self.price = price
    
    def accept(self, visitor: ShoppingCartVisitor) -> None:
        visitor.visit_clothing(self)


class PriceCalculatorVisitor(ShoppingCartVisitor):
    """价格计算访问者"""
    
    def __init__(self):
        self.total_price = 0.0
        self.item_count = 0
    
    def visit_book(self, book: Book) -> None:
        self.item_count += 1
        self.total_price += book.price
        print(f"书籍: {book.title} - 价格: {book.price:.2f}")
    
    def visit_electronics(self, electronics: Electronics) -> None:
        self.item_count += 1
        self.total_price += electronics.price
        print(f"电子产品: {electronics.name} - 价格: {electronics.price:.2f}")
    
    def visit_clothing(self, clothing: Clothing) -> None:
        self.item_count += 1
        self.total_price += clothing.price
        print(f"服装: {clothing.name} - 价格: {clothing.price:.2f}")
    
    def get_total(self) -> dict:
        return {
            'item_count': self.item_count,
            'total_price': self.total_price
        }


class TaxCalculatorVisitor(ShoppingCartVisitor):
    """税费计算访问者"""
    
    def __init__(self):
        self.total_tax = 0.0
    
    def visit_book(self, book: Book) -> None:
        # 书籍免税
        tax = 0.0
        self.total_tax += tax
        print(f"书籍: {book.title} - 税费: {tax:.2f}")
    
    def visit_electronics(self, electronics: Electronics) -> None:
        # 电子产品10%税
        tax = electronics.price * 0.1
        self.total_tax += tax
        print(f"电子产品: {electronics.name} - 税费: {tax:.2f}")
    
    def visit_clothing(self, clothing: Clothing) -> None:
        # 服装5%税
        tax = clothing.price * 0.05
        self.total_tax += tax
        print(f"服装: {clothing.name} - 税费: {tax:.2f}")
    
    def get_total_tax(self) -> float:
        return self.total_tax


class ShoppingCart:
    """购物车类"""
    
    def __init__(self):
        self.items: List[ShoppingItem] = []
    
    def add_item(self, item: ShoppingItem) -> None:
        self.items.append(item)
    
    def accept(self, visitor: ShoppingCartVisitor) -> None:
        for item in self.items:
            item.accept(visitor)


# 示例3：文件系统访问
class FileSystemElement(ABC):
    """文件系统元素接口"""
    
    @abstractmethod
    def accept(self, visitor) -> None:
        pass


class FileSystemVisitor(ABC):
    """文件系统访问者接口"""
    
    @abstractmethod
    def visit_file(self, file) -> None:
        pass
    
    @abstractmethod
    def visit_directory(self, directory) -> None:
        pass


class File(FileSystemElement):
    """文件类"""
    
    def __init__(self, name: str, size: int, extension: str):
        self.name = name
        self.size = size
        self.extension = extension
    
    def accept(self, visitor: FileSystemVisitor) -> None:
        visitor.visit_file(self)


class Directory(FileSystemElement):
    """目录类"""
    
    def __init__(self, name: str):
        self.name = name
        self.children: List[FileSystemElement] = []
    
    def add_child(self, child: FileSystemElement) -> None:
        self.children.append(child)
    
    def accept(self, visitor: FileSystemVisitor) -> None:
        visitor.visit_directory(self)
        for child in self.children:
            child.accept(visitor)


class SizeCalculatorVisitor(FileSystemVisitor):
    """大小计算访问者"""
    
    def __init__(self):
        self.total_size = 0
        self.file_count = 0
        self.directory_count = 0
    
    def visit_file(self, file: File) -> None:
        self.file_count += 1
        self.total_size += file.size
        print(f"文件: {file.name} - 大小: {file.size} bytes")
    
    def visit_directory(self, directory: Directory) -> None:
        self.directory_count += 1
        print(f"目录: {directory.name}")
    
    def get_stats(self) -> dict:
        return {
            'file_count': self.file_count,
            'directory_count': self.directory_count,
            'total_size': self.total_size
        }


class SearchVisitor(FileSystemVisitor):
    """搜索访问者"""
    
    def __init__(self, search_term: str):
        self.search_term = search_term.lower()
        self.results = []
    
    def visit_file(self, file: File) -> None:
        if self.search_term in file.name.lower():
            self.results.append(f"文件: {file.name}")
    
    def visit_directory(self, directory: Directory) -> None:
        if self.search_term in directory.name.lower():
            self.results.append(f"目录: {directory.name}")
    
    def get_results(self) -> List[str]:
        return self.results


def test_document_visitors():
    """测试文档访问者"""
    print("=== 测试文档访问者 ===")
    
    # 创建文档
    document = Document()
    document.add_element(Heading(1, "设计模式教程"))
    document.add_element(Paragraph("这是一篇关于设计模式的教程。"))
    document.add_element(Image("pattern.jpg", "设计模式", 800, 600))
    document.add_element(Table(2, 3, [["模式", "类型", "描述"], ["单例", "创建型", "确保一个类只有一个实例"]]))
    document.add_element(Heading(2, "访问者模式"))
    document.add_element(Paragraph("访问者模式是一种行为设计模式。"))
    
    # 测试HTML导出
    print("\n1. HTML导出:")
    html_visitor = HTMLExportVisitor()
    document.accept(html_visitor)
    print(html_visitor.get_html())
    
    # 测试纯文本导出
    print("\n2. 纯文本导出:")
    text_visitor = PlainTextExportVisitor()
    document.accept(text_visitor)
    print(text_visitor.get_text())
    
    # 测试字数统计
    print("\n3. 字数统计:")
    word_visitor = WordCountVisitor()
    document.accept(word_visitor)
    stats = word_visitor.get_stats()
    print(f"元素数量: {stats['element_count']}, 字数: {stats['word_count']}")


def test_shopping_cart_visitors():
    """测试购物车访问者"""
    print("\n=== 测试购物车访问者 ===")
    
    # 创建购物车
    cart = ShoppingCart()
    cart.add_item(Book("设计模式", "四人组", 59.99, "978-7-111-12345-6"))
    cart.add_item(Electronics("笔记本电脑", "Dell", 5999.99, 24))
    cart.add_item(Clothing("T恤", "L", "蓝色", 99.99))
    cart.add_item(Book("Python编程", "Guido", 39.99, "978-7-111-67890-1"))
    
    # 测试价格计算
    print("\n1. 价格计算:")
    price_visitor = PriceCalculatorVisitor()
    cart.accept(price_visitor)
    total = price_visitor.get_total()
    print(f"总商品数: {total['item_count']}, 总价格: {total['total_price']:.2f}")
    
    # 测试税费计算
    print("\n2. 税费计算:")
    tax_visitor = TaxCalculatorVisitor()
    cart.accept(tax_visitor)
    total_tax = tax_visitor.get_total_tax()
    print(f"总税费: {total_tax:.2f}")


def test_file_system_visitors():
    """测试文件系统访问者"""
    print("\n=== 测试文件系统访问者 ===")
    
    # 创建文件系统结构
    root = Directory("root")
    
    docs = Directory("documents")
    docs.add_child(File("report.pdf", 1024000, "pdf"))
    docs.add_child(File("notes.txt", 2048, "txt"))
    
    images = Directory("images")
    images.add_child(File("photo1.jpg", 2048000, "jpg"))
    images.add_child(File("photo2.png", 1024000, "png"))
    
    code = Directory("code")
    code.add_child(File("main.py", 4096, "py"))
    code.add_child(File("utils.py", 2048, "py"))
    
    root.add_child(docs)
    root.add_child(images)
    root.add_child(code)
    
    # 测试大小计算
    print("\n1. 大小计算:")
    size_visitor = SizeCalculatorVisitor()
    root.accept(size_visitor)
    stats = size_visitor.get_stats()
    print(f"文件数: {stats['file_count']}, 目录数: {stats['directory_count']}, 总大小: {stats['total_size']} bytes")
    
    # 测试搜索
    print("\n2. 搜索文件:")
    search_visitor = SearchVisitor("py")
    root.accept(search_visitor)
    results = search_visitor.get_results()
    print("搜索结果:", results)


if __name__ == "main":
    # 运行所有测试
    test_document_visitors()
    test_shopping_cart_visitors()
    test_file_system_visitors()
    
    print("\n=== 访问者模式测试完成 ===")
    print("\n访问者模式总结：")
    print("1. 将算法与对象结构分离")
    print("2. 易于添加新的操作")
    print("3. 访问者可以累积状态")
    print("4. 违反开闭原则（添加新元素困难）")
    print("5. 适用于对象结构稳定但操作频繁变化的场景")