// Chapter11Example.java - 享元模式示例代码

import java.awt.*;
import java.util.HashMap;
import java.util.Map;
import java.util.Random;

// 抽象享元类
interface Shape {
    void draw(int x, int y, String color);
}

// 具体享元类
class Circle implements Shape {
    private String color;
    
    public Circle(String color) {
        this.color = color;
        System.out.println("Creating circle of color : " + color);
    }
    
    @Override
    public void draw(int x, int y, String color) {
        System.out.println("Circle: Draw() [Color : " + color + ", x : " + x + ", y :" + y + "]");
    }
}

// 享元工厂类
class ShapeFactory {
    private static final Map<String, Shape> circleMap = new HashMap<>();
    
    public static Shape getCircle(String color) {
        Circle circle = (Circle)circleMap.get(color);
        
        if(circle == null) {
            circle = new Circle(color);
            circleMap.put(color, circle);
            System.out.println("Creating circle of color : " + color);
        }
        return circle;
    }
}

// 抽象享元类 - 树类型
class TreeType {
    private String name;
    private Color color;
    private String otherTreeData;
    
    public TreeType(String name, Color color, String otherTreeData) {
        this.name = name;
        this.color = color;
        this.otherTreeData = otherTreeData;
    }
    
    public void draw(Graphics g, int x, int y) {
        System.out.println("Drawing tree type: " + name + " at (" + x + ", " + y + ")");
    }
    
    public String getName() {
        return name;
    }
    
    public Color getColor() {
        return color;
    }
}

// 享元工厂类
class TreeFactory {
    static Map<String, TreeType> treeTypes = new HashMap<>();
    
    public static TreeType getTreeType(String name, Color color, String otherTreeData) {
        TreeType result = treeTypes.get(name);
        if (result == null) {
            result = new TreeType(name, color, otherTreeData);
            treeTypes.put(name, result);
            System.out.println("Created tree type: " + name);
        }
        return result;
    }
}

// 树类 - 包含外部状态
class Tree {
    private int x, y;
    private TreeType type;
    
    public Tree(int x, int y, TreeType type) {
        this.x = x;
        this.y = y;
        this.type = type;
    }
    
    public void draw(Graphics g) {
        type.draw(g, x, y);
    }
}

// 森林类
class Forest {
    private java.util.List<Tree> trees = new java.util.ArrayList<>();
    
    public void plantTree(int x, int y, String name, Color color, String otherTreeData) {
        TreeType type = TreeFactory.getTreeType(name, color, otherTreeData);
        Tree tree = new Tree(x, y, type);
        trees.add(tree);
    }
    
    public void draw(Graphics g) {
        for (Tree tree : trees) {
            tree.draw(g);
        }
    }
    
    public int getTreeCount() {
        return trees.size();
    }
    
    public int getTreeTypeCount() {
        return TreeFactory.treeTypes.size();
    }
}

// 字符格式类 - 享元对象
class CharacterFormat {
    private String fontName;
    private String color;
    private boolean bold;
    
    public CharacterFormat(String fontName, String color, boolean bold) {
        this.fontName = fontName;
        this.color = color;
        this.bold = bold;
    }
    
    public void format(char character, int x, int y) {
        // 应用格式到字符
        System.out.println("Formatting character '" + character + "' with font " + 
                          fontName + ", color " + color + 
                          ", bold: " + bold + " at (" + x + ", " + y + ")");
    }
    
    // Getters
    public String getFontName() { return fontName; }
    public String getColor() { return color; }
    public boolean isBold() { return bold; }
    
    @Override
    public boolean equals(Object obj) {
        if (this == obj) return true;
        if (obj == null || getClass() != obj.getClass()) return false;
        CharacterFormat that = (CharacterFormat) obj;
        return bold == that.bold &&
               java.util.Objects.equals(fontName, that.fontName) &&
               java.util.Objects.equals(color, that.color);
    }
    
    @Override
    public int hashCode() {
        return java.util.Objects.hash(fontName, color, bold);
    }
}

// 字符格式工厂
class FormatFactory {
    private static final Map<CharacterFormat, CharacterFormat> formats = new HashMap<>();
    
    public static CharacterFormat getFormat(String fontName, String color, boolean bold) {
        CharacterFormat key = new CharacterFormat(fontName, color, bold);
        CharacterFormat format = formats.get(key);
        
        if (format == null) {
            format = new CharacterFormat(fontName, color, bold);
            formats.put(format, format);
            System.out.println("Created new character format: " + fontName + 
                             ", " + color + ", bold=" + bold);
        }
        return format;
    }
    
    public static int getFormatCount() {
        return formats.size();
    }
}

// 文档字符类 - 包含外部状态
class DocumentCharacter {
    private char character;
    private int x, y;
    private CharacterFormat format;
    
    public DocumentCharacter(char character, int x, int y, CharacterFormat format) {
        this.character = character;
        this.x = x;
        this.y = y;
        this.format = format;
    }
    
    public void draw() {
        format.format(character, x, y);
    }
}

// 单位类型 - 享元对象
class UnitType {
    private String name;
    private int health;
    private int attackPower;
    private String texture;
    private String sound;
    
    public UnitType(String name, int health, int attackPower, String texture, String sound) {
        this.name = name;
        this.health = health;
        this.attackPower = attackPower;
        this.texture = texture;
        this.sound = sound;
    }
    
    public void render(int x, int y) {
        System.out.println("Rendering " + name + " at (" + x + ", " + y + ") with texture: " + texture);
    }
    
    public void playSound() {
        System.out.println("Playing sound: " + sound);
    }
    
    // Getters
    public String getName() { return name; }
    public int getHealth() { return health; }
    public int getAttackPower() { return attackPower; }
}

// 单位类型工厂
class UnitTypeFactory {
    private static Map<String, UnitType> unitTypes = new HashMap<>();
    
    public static UnitType getUnitType(String name, int health, int attackPower, 
                                      String texture, String sound) {
        UnitType type = unitTypes.get(name);
        if (type == null) {
            type = new UnitType(name, health, attackPower, texture, sound);
            unitTypes.put(name, type);
            System.out.println("Created unit type: " + name);
        }
        return type;
    }
    
    public static int getUnitTypeCount() {
        return unitTypes.size();
    }
}

// 游戏单位类 - 包含外部状态
class GameUnit {
    private int x, y;
    private UnitType type;
    private int currentHealth;
    
    public GameUnit(int x, int y, UnitType type) {
        this.x = x;
        this.y = y;
        this.type = type;
        this.currentHealth = type.getHealth();
    }
    
    public void move(int newX, int newY) {
        this.x = newX;
        this.y = newY;
        System.out.println(type.getName() + " moved to (" + x + ", " + y + ")");
    }
    
    public void render() {
        type.render(x, y);
    }
    
    public void attack(GameUnit target) {
        System.out.println(type.getName() + " attacks " + target.type.getName() + 
                          " with " + type.getAttackPower() + " damage");
        type.playSound();
    }
}

// 主类 - 演示享元模式
public class Chapter11Example {
    private static final String colors[] = { "Red", "Green", "Blue", "White", "Black" };
    
    public static void main(String[] args) {
        System.out.println("=== 第十一章 享元模式示例 ===\n");
        
        // 示例1: 基本圆形享元模式
        System.out.println("1. 基本圆形享元模式示例:");
        for(int i=0; i < 10; ++i) {
            Circle circle = (Circle)ShapeFactory.getCircle(getRandomColor());
            circle.draw(getRandomX(), getRandomY(), getRandomColor());
        }
        System.out.println();
        
        // 示例2: 森林绘制系统
        System.out.println("2. 森林绘制系统示例:");
        Forest forest = new Forest();
        
        // 种植多种类型的树
        for(int i=0; i < 5; i++) {
            forest.plantTree(
                getRandomX(), 
                getRandomY(), 
                "Oak", 
                Color.GREEN, 
                "Oak tree data"
            );
        }
        
        for(int i=0; i < 3; i++) {
            forest.plantTree(
                getRandomX(), 
                getRandomY(), 
                "Pine", 
                Color.DARK_GRAY, 
                "Pine tree data"
            );
        }
        
        for(int i=0; i < 2; i++) {
            forest.plantTree(
                getRandomX(), 
                getRandomY(), 
                "Birch", 
                Color.LIGHT_GRAY, 
                "Birch tree data"
            );
        }
        
        System.out.println("Total trees planted: " + forest.getTreeCount());
        System.out.println("Distinct tree types: " + forest.getTreeTypeCount());
        System.out.println();
        
        // 示例3: 文档编辑器字符格式化
        System.out.println("3. 文档编辑器字符格式化示例:");
        String text = "Hello Flyweight Pattern!";
        int xPos = 0;
        int yPos = 0;
        
        for(char c : text.toCharArray()) {
            CharacterFormat format = FormatFactory.getFormat("Arial", "Black", false);
            DocumentCharacter docChar = new DocumentCharacter(c, xPos, yPos, format);
            docChar.draw();
            xPos += 10; // 简单的字符间距
        }
        
        System.out.println("Distinct character formats: " + FormatFactory.getFormatCount());
        System.out.println();
        
        // 示例4: 游戏单位系统
        System.out.println("4. 游戏单位系统示例:");
        // 创建不同类型的单位
        UnitType warriorType = UnitTypeFactory.getUnitType(
            "Warrior", 100, 20, "warrior.png", "sword.wav");
        UnitType archerType = UnitTypeFactory.getUnitType(
            "Archer", 80, 15, "archer.png", "bow.wav");
        UnitType mageType = UnitTypeFactory.getUnitType(
            "Mage", 60, 25, "mage.png", "spell.wav");
        
        // 创建单位实例
        GameUnit warrior1 = new GameUnit(10, 10, warriorType);
        GameUnit warrior2 = new GameUnit(15, 15, warriorType);
        GameUnit archer1 = new GameUnit(20, 20, archerType);
        GameUnit mage1 = new GameUnit(25, 25, mageType);
        
        // 执行操作
        warrior1.render();
        warrior2.render();
        archer1.render();
        mage1.render();
        
        warrior1.move(12, 12);
        archer1.attack(mage1);
        
        System.out.println("Distinct unit types: " + UnitTypeFactory.getUnitTypeCount());
    }
    
    private static String getRandomColor() {
        return colors[(int)(Math.random() * colors.length)];
    }
    
    private static int getRandomX() {
        return (int)(Math.random() * 100);
    }
    
    private static int getRandomY() {
        return (int)(Math.random() * 100);
    }
}