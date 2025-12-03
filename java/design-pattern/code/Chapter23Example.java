import java.util.*;

// 访问者接口
interface Visitor {
    void visit(ConcreteElementA element);
    void visit(ConcreteElementB element);
}

// 具体访问者 - 显示访问者
class ConcreteVisitor1 implements Visitor {
    @Override
    public void visit(ConcreteElementA element) {
        System.out.println("ConcreteVisitor1 访问 " + element.operationA());
    }
    
    @Override
    public void visit(ConcreteElementB element) {
        System.out.println("ConcreteVisitor1 访问 " + element.operationB());
    }
}

// 具体访问者 - 执行访问者
class ConcreteVisitor2 implements Visitor {
    @Override
    public void visit(ConcreteElementA element) {
        System.out.println("ConcreteVisitor2 访问 " + element.operationA());
    }
    
    @Override
    public void visit(ConcreteElementB element) {
        System.out.println("ConcreteVisitor2 访问 " + element.operationB());
    }
}

// 元素接口
interface Element {
    void accept(Visitor visitor);
}

// 具体元素A
class ConcreteElementA implements Element {
    @Override
    public void accept(Visitor visitor) {
        visitor.visit(this);
    }
    
    public String operationA() {
        return "ConcreteElementA 的操作";
    }
}

// 具体元素B
class ConcreteElementB implements Element {
    @Override
    public void accept(Visitor visitor) {
        visitor.visit(this);
    }
    
    public String operationB() {
        return "ConcreteElementB 的操作";
    }
}

// 访问者接口
interface DocumentVisitor {
    void visit(TextElement text);
    void visit(ImageElement image);
    void visit(TableElement table);
}

// 具体访问者 - 导出为HTML
class HtmlExportVisitor implements DocumentVisitor {
    @Override
    public void visit(TextElement text) {
        System.out.println("<p>" + text.getContent() + "</p>");
    }
    
    @Override
    public void visit(ImageElement image) {
        System.out.println("<img src=\"" + image.getSource() + "\" alt=\"" + image.getCaption() + "\">");
    }
    
    @Override
    public void visit(TableElement table) {
        System.out.println("<table>");
        for (String row : table.getRows()) {
            System.out.println("  <tr><td>" + row + "</td></tr>");
        }
        System.out.println("</table>");
    }
}

// 具体访问者 - 导出为纯文本
class PlainTextExportVisitor implements DocumentVisitor {
    @Override
    public void visit(TextElement text) {
        System.out.println(text.getContent());
    }
    
    @Override
    public void visit(ImageElement image) {
        System.out.println("[图片: " + image.getCaption() + "]");
    }
    
    @Override
    public void visit(TableElement table) {
        System.out.println("表格:");
        for (String row : table.getRows()) {
            System.out.println("  " + row);
        }
    }
}

// 具体访问者 - 统计字数
class WordCountVisitor implements DocumentVisitor {
    private int wordCount = 0;
    
    @Override
    public void visit(TextElement text) {
        wordCount += text.getContent().split("\\s+").length;
    }
    
    @Override
    public void visit(ImageElement image) {
        // 图片不计算字数
    }
    
    @Override
    public void visit(TableElement table) {
        for (String row : table.getRows()) {
            wordCount += row.split("\\s+").length;
        }
    }
    
    public int getWordCount() {
        return wordCount;
    }
}

// 文档元素接口
interface DocumentElement {
    void accept(DocumentVisitor visitor);
}

// 文本元素
class TextElement implements DocumentElement {
    private String content;
    
    public TextElement(String content) {
        this.content = content;
    }
    
    @Override
    public void accept(DocumentVisitor visitor) {
        visitor.visit(this);
    }
    
    public String getContent() {
        return content;
    }
}

// 图片元素
class ImageElement implements DocumentElement {
    private String source;
    private String caption;
    
    public ImageElement(String source, String caption) {
        this.source = source;
        this.caption = caption;
    }
    
    @Override
    public void accept(DocumentVisitor visitor) {
        visitor.visit(this);
    }
    
    public String getSource() {
        return source;
    }
    
    public String getCaption() {
        return caption;
    }
}

// 表格元素
class TableElement implements DocumentElement {
    private List<String> rows;
    
    public TableElement(List<String> rows) {
        this.rows = new ArrayList<>(rows);
    }
    
    @Override
    public void accept(DocumentVisitor visitor) {
        visitor.visit(this);
    }
    
    public List<String> getRows() {
        return new ArrayList<>(rows);
    }
}

// 文档类 - 对象结构
class Document {
    private List<DocumentElement> elements = new ArrayList<>();
    
    public void addElement(DocumentElement element) {
        elements.add(element);
    }
    
    public void removeElement(DocumentElement element) {
        elements.remove(element);
    }
    
    public void accept(DocumentVisitor visitor) {
        for (DocumentElement element : elements) {
            element.accept(visitor);
        }
    }
}

// 访问者接口
interface ShoppingCartVisitor {
    double visit(Book book);
    double visit(Fruit fruit);
    double visit(Electronics electronics);
}

// 具体访问者 - 普通客户价格计算
class RegularCustomerVisitor implements ShoppingCartVisitor {
    @Override
    public double visit(Book book) {
        double cost = book.getPrice();
        // 普通客户书籍打9折
        if (book.getPrice() > 50) {
            cost *= 0.9;
        }
        System.out.println("书籍: " + book.getName() + ", 原价: " + book.getPrice() + ", 折扣价: " + cost);
        return cost;
    }
    
    @Override
    public double visit(Fruit fruit) {
        double cost = fruit.getPricePerKg() * fruit.getWeight();
        System.out.println("水果: " + fruit.getName() + ", 重量: " + fruit.getWeight() + "kg, 总价: " + cost);
        return cost;
    }
    
    @Override
    public double visit(Electronics electronics) {
        double cost = electronics.getPrice();
        // 普通客户电子产品打9.5折
        cost *= 0.95;
        System.out.println("电子产品: " + electronics.getName() + ", 原价: " + electronics.getPrice() + ", 折扣价: " + cost);
        return cost;
    }
}

// 具体访问者 - VIP客户价格计算
class VIPCustomerVisitor implements ShoppingCartVisitor {
    @Override
    public double visit(Book book) {
        double cost = book.getPrice();
        // VIP客户书籍打8折
        cost *= 0.8;
        System.out.println("书籍: " + book.getName() + ", 原价: " + book.getPrice() + ", VIP价: " + cost);
        return cost;
    }
    
    @Override
    public double visit(Fruit fruit) {
        double cost = fruit.getPricePerKg() * fruit.getWeight();
        // VIP客户水果打9折
        cost *= 0.9;
        System.out.println("水果: " + fruit.getName() + ", 重量: " + fruit.getWeight() + "kg, VIP价: " + cost);
        return cost;
    }
    
    @Override
    public double visit(Electronics electronics) {
        double cost = electronics.getPrice();
        // VIP客户电子产品打8.5折
        cost *= 0.85;
        System.out.println("电子产品: " + electronics.getName() + ", 原价: " + electronics.getPrice() + ", VIP价: " + cost);
        return cost;
    }
}

// 商品接口
interface ItemElement {
    double accept(ShoppingCartVisitor visitor);
}

// 书籍类
class Book implements ItemElement {
    private double price;
    private String name;
    
    public Book(double price, String name) {
        this.price = price;
        this.name = name;
    }
    
    @Override
    public double accept(ShoppingCartVisitor visitor) {
        return visitor.visit(this);
    }
    
    public double getPrice() {
        return price;
    }
    
    public String getName() {
        return name;
    }
}

// 水果类
class Fruit implements ItemElement {
    private double pricePerKg;
    private double weight;
    private String name;
    
    public Fruit(double pricePerKg, double weight, String name) {
        this.pricePerKg = pricePerKg;
        this.weight = weight;
        this.name = name;
    }
    
    @Override
    public double accept(ShoppingCartVisitor visitor) {
        return visitor.visit(this);
    }
    
    public double getPricePerKg() {
        return pricePerKg;
    }
    
    public double getWeight() {
        return weight;
    }
    
    public String getName() {
        return name;
    }
}

// 电子产品类
class Electronics implements ItemElement {
    private double price;
    private String name;
    
    public Electronics(double price, String name) {
        this.price = price;
        this.name = name;
    }
    
    @Override
    public double accept(ShoppingCartVisitor visitor) {
        return visitor.visit(this);
    }
    
    public double getPrice() {
        return price;
    }
    
    public String getName() {
        return name;
    }
}

// 购物车类
class ShoppingCart {
    private List<ItemElement> items = new ArrayList<>();
    
    public void addItem(ItemElement item) {
        items.add(item);
    }
    
    public void removeItem(ItemElement item) {
        items.remove(item);
    }
    
    public double calculateTotal(ShoppingCartVisitor visitor) {
        double sum = 0;
        for (ItemElement item : items) {
            sum += item.accept(visitor);
        }
        return sum;
    }
}

public class Chapter23Example {
    public static void main(String[] args) {
        System.out.println("=== 访问者模式示例 ===\n");
        
        // 1. 基本访问者模式示例
        System.out.println("1. 基本访问者模式示例:");
        List<Element> elements = new ArrayList<>();
        elements.add(new ConcreteElementA());
        elements.add(new ConcreteElementB());
        
        Visitor visitor1 = new ConcreteVisitor1();
        Visitor visitor2 = new ConcreteVisitor2();
        
        for (Element element : elements) {
            element.accept(visitor1);
        }
        
        System.out.println();
        
        for (Element element : elements) {
            element.accept(visitor2);
        }
        
        System.out.println("\n----------------------\n");
        
        // 2. 文档编辑器示例
        System.out.println("2. 文档编辑器示例:");
        Document document = new Document();
        document.addElement(new TextElement("这是一个访问者模式的示例文档"));
        document.addElement(new ImageElement("image.jpg", "访问者模式图示"));
        document.addElement(new TableElement(Arrays.asList("姓名:张三", "年龄:25", "职业:工程师")));
        
        System.out.println("导出为HTML格式:");
        document.accept(new HtmlExportVisitor());
        
        System.out.println("\n导出为纯文本格式:");
        document.accept(new PlainTextExportVisitor());
        
        System.out.println("\n统计字数:");
        WordCountVisitor wordCountVisitor = new WordCountVisitor();
        document.accept(wordCountVisitor);
        System.out.println("文档总字数: " + wordCountVisitor.getWordCount());
        
        System.out.println("\n----------------------\n");
        
        // 3. 电商购物车示例
        System.out.println("3. 电商购物车示例:");
        ShoppingCart cart = new ShoppingCart();
        cart.addItem(new Book(60, "设计模式"));
        cart.addItem(new Fruit(15, 2, "苹果"));
        cart.addItem(new Electronics(1000, "手机"));
        
        System.out.println("普通客户购买商品:");
        double regularTotal = cart.calculateTotal(new RegularCustomerVisitor());
        System.out.println("普通客户总价: " + regularTotal);
        
        System.out.println("\nVIP客户购买商品:");
        double vipTotal = cart.calculateTotal(new VIPCustomerVisitor());
        System.out.println("VIP客户总价: " + vipTotal);
    }
}