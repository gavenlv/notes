/**
 * 第二十二章示例代码：模板方法模式
 */

// 1. 基本模板方法模式实现
abstract class Game {
    // 模板方法，定义游戏的流程
    public final void play() {
        // 初始化游戏
        initialize();
        
        // 开始游戏
        startPlay();
        
        // 结束游戏
        endPlay();
    }
    
    // 基本方法 - 初始化游戏
    abstract void initialize();
    
    // 基本方法 - 开始游戏
    abstract void startPlay();
    
    // 基本方法 - 结束游戏
    abstract void endPlay();
}

// 具体游戏类 - 板球游戏
class Cricket extends Game {
    @Override
    void initialize() {
        System.out.println("Cricket Game Initialized! Start playing.");
    }
    
    @Override
    void startPlay() {
        System.out.println("Cricket Game Started. Enjoy the game!");
    }
    
    @Override
    void endPlay() {
        System.out.println("Cricket Game Finished!");
    }
}

// 具体游戏类 - 足球游戏
class Football extends Game {
    @Override
    void initialize() {
        System.out.println("Football Game Initialized! Start playing.");
    }
    
    @Override
    void startPlay() {
        System.out.println("Football Game Started. Enjoy the game!");
    }
    
    @Override
    void endPlay() {
        System.out.println("Football Game Finished!");
    }
}

// 2. 制作饮料示例
// 抽象模板类 - 饮料制作
abstract class BeverageMaker {
    // 模板方法 - 定义制作饮料的流程
    public final void prepareRecipe() {
        boilWater();
        brew();
        pourInCup();
        addCondiments();
    }
    
    // 基本方法 - 煮水（通用步骤）
    void boilWater() {
        System.out.println("Boiling water");
    }
    
    // 抽象方法 - 冲泡（由子类实现）
    abstract void brew();
    
    // 基本方法 - 倒入杯中（通用步骤）
    void pourInCup() {
        System.out.println("Pouring into cup");
    }
    
    // 抽象方法 - 添加调料（由子类实现）
    abstract void addCondiments();
}

// 具体类 - 制作咖啡
class CoffeeMaker extends BeverageMaker {
    @Override
    void brew() {
        System.out.println("Dripping Coffee through filter");
    }
    
    @Override
    void addCondiments() {
        System.out.println("Adding Sugar and Milk");
    }
}

// 具体类 - 制作茶
class Tea extends BeverageMaker {
    @Override
    void brew() {
        System.out.println("Steeping the tea");
    }
    
    @Override
    void addCondiments() {
        System.out.println("Adding Lemon");
    }
}

// 3. 数据处理流程示例
// 抽象模板类 - 数据处理器
abstract class DataProcessor {
    // 模板方法 - 定义数据处理流程
    public final void processData() {
        readData();
        processDataSteps();
        saveData();
        if (isPostProcessingNeeded()) {
            postProcess();
        }
    }
    
    // 基本方法 - 读取数据
    abstract void readData();
    
    // 基本方法 - 处理数据步骤
    private void processDataSteps() {
        validateData();
        transformData();
        aggregateData();
    }
    
    // 基本方法 - 验证数据
    void validateData() {
        System.out.println("Validating data");
    }
    
    // 基本方法 - 转换数据
    void transformData() {
        System.out.println("Transforming data");
    }
    
    // 基本方法 - 聚合数据
    void aggregateData() {
        System.out.println("Aggregating data");
    }
    
    // 基本方法 - 保存数据
    abstract void saveData();
    
    // 钩子方法 - 是否需要后处理
    boolean isPostProcessingNeeded() {
        return false; // 默认不需要后处理
    }
    
    // 钩子方法 - 后处理
    void postProcess() {
        System.out.println("Performing post-processing");
    }
}

// 具体类 - XML数据处理器
class XMLDataProcessor extends DataProcessor {
    @Override
    void readData() {
        System.out.println("Reading data from XML file");
    }
    
    @Override
    void saveData() {
        System.out.println("Saving data to XML file");
    }
    
    @Override
    boolean isPostProcessingNeeded() {
        return true; // XML数据需要后处理
    }
    
    @Override
    void postProcess() {
        System.out.println("Performing XML-specific post-processing");
    }
}

// 具体类 - JSON数据处理器
class JSONDataProcessor extends DataProcessor {
    @Override
    void readData() {
        System.out.println("Reading data from JSON file");
    }
    
    @Override
    void saveData() {
        System.out.println("Saving data to JSON file");
    }
}

// 主类
public class Chapter22Example {
    public static void main(String[] args) {
        System.out.println("=== 模板方法模式示例 ===\n");
        
        // 1. 游戏示例
        System.out.println("1. 游戏示例:");
        System.out.println("玩板球游戏:");
        Game cricket = new Cricket();
        cricket.play();
        
        System.out.println("\n玩足球游戏:");
        Game football = new Football();
        football.play();
        
        // 2. 制作饮料示例
        System.out.println("\n2. 制作饮料示例:");
        System.out.println("制作咖啡:");
        BeverageMaker coffee = new CoffeeMaker();
        coffee.prepareRecipe();
        
        System.out.println("\n制作茶:");
        BeverageMaker tea = new Tea();
        tea.prepareRecipe();
        
        // 3. 数据处理示例
        System.out.println("\n3. 数据处理示例:");
        System.out.println("处理XML数据:");
        DataProcessor xmlProcessor = new XMLDataProcessor();
        xmlProcessor.processData();
        
        System.out.println("\n处理JSON数据:");
        DataProcessor jsonProcessor = new JSONDataProcessor();
        jsonProcessor.processData();
    }
}