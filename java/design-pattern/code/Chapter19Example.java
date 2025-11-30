import java.util.*;

// 抽象观察者
interface Observer {
    void update(String message);
}

// 抽象主题
abstract class Subject {
    protected List<Observer> observers = new ArrayList<>();
    
    // 添加观察者
    public void addObserver(Observer observer) {
        observers.add(observer);
    }
    
    // 删除观察者
    public void removeObserver(Observer observer) {
        observers.remove(observer);
    }
    
    // 通知所有观察者
    protected void notifyObservers(String message) {
        for (Observer observer : observers) {
            observer.update(message);
        }
    }
}

// 具体主题
class ConcreteSubject extends Subject {
    private String state;
    
    public String getState() {
        return state;
    }
    
    public void setState(String state) {
        this.state = state;
        // 状态改变时通知所有观察者
        notifyObservers("状态已更新为: " + state);
    }
}

// 具体观察者
class ConcreteObserver implements Observer {
    private String name;
    
    public ConcreteObserver(String name) {
        this.name = name;
    }
    
    @Override
    public void update(String message) {
        System.out.println(name + " 收到通知: " + message);
    }
}

// 新闻观察者接口
interface NewsObserver {
    void updateNews(String category, String news);
}

// 抽象新闻主题
abstract class NewsSubject {
    protected List<NewsObserver> observers = new ArrayList<>();
    
    // 订阅
    public void subscribe(NewsObserver observer) {
        observers.add(observer);
    }
    
    // 取消订阅
    public void unsubscribe(NewsObserver observer) {
        observers.remove(observer);
    }
    
    // 通知观察者
    protected void notifyObservers(String category, String news) {
        for (NewsObserver observer : observers) {
            observer.updateNews(category, news);
        }
    }
}

// 新闻发布者
class NewsPublisher extends NewsSubject {
    private Map<String, List<String>> newsCategories;
    
    public NewsPublisher() {
        this.newsCategories = new HashMap<>();
    }
    
    // 发布新闻
    public void publishNews(String category, String news) {
        newsCategories.computeIfAbsent(category, k -> new ArrayList<>()).add(news);
        System.out.println("发布[" + category + "]新闻: " + news);
        // 通知所有订阅者
        notifyObservers(category, news);
    }
    
    // 获取某类别的所有新闻
    public List<String> getNewsByCategory(String category) {
        return newsCategories.getOrDefault(category, new ArrayList<>());
    }
}

// 新闻订阅者 - 用户
class User implements NewsObserver {
    private String name;
    private Set<String> subscribedCategories;
    
    public User(String name) {
        this.name = name;
        this.subscribedCategories = new HashSet<>();
    }
    
    // 订阅类别
    public void subscribeCategory(String category) {
        subscribedCategories.add(category);
        System.out.println(name + " 订阅了 [" + category + "] 类别");
    }
    
    // 取消订阅类别
    public void unsubscribeCategory(String category) {
        subscribedCategories.remove(category);
        System.out.println(name + " 取消订阅了 [" + category + "] 类别");
    }
    
    @Override
    public void updateNews(String category, String news) {
        // 只接收订阅类别的新闻
        if (subscribedCategories.contains(category)) {
            System.out.println(name + " 收到 [" + category + "] 新闻: " + news);
        }
    }
}

// 股票观察者接口
interface StockObserver {
    void update(String stockSymbol, double price);
}

// 股票主题抽象类
abstract class StockSubject {
    protected List<StockObserver> observers = new ArrayList<>();
    
    public void addObserver(StockObserver observer) {
        observers.add(observer);
    }
    
    public void removeObserver(StockObserver observer) {
        observers.remove(observer);
    }
    
    protected void notifyObservers(String stockSymbol, double price) {
        for (StockObserver observer : observers) {
            observer.update(stockSymbol, price);
        }
    }
}

// 股票价格监控系统
class StockPriceMonitor extends StockSubject {
    private Map<String, Double> stockPrices;
    
    public StockPriceMonitor() {
        this.stockPrices = new HashMap<>();
    }
    
    // 更新股票价格
    public void updateStockPrice(String stockSymbol, double price) {
        Double oldPrice = stockPrices.get(stockSymbol);
        stockPrices.put(stockSymbol, price);
        
        if (oldPrice == null || oldPrice != price) {
            System.out.println("股票 " + stockSymbol + " 价格更新为: " + price);
            notifyObservers(stockSymbol, price);
        }
    }
    
    // 获取股票当前价格
    public Double getStockPrice(String stockSymbol) {
        return stockPrices.get(stockSymbol);
    }
}

// 股票投资者
class Investor implements StockObserver {
    private String name;
    private Map<String, Double> watchedStocks; // 关注的股票及阈值
    
    public Investor(String name) {
        this.name = name;
        this.watchedStocks = new HashMap<>();
    }
    
    // 添加关注的股票及预警价格
    public void watchStock(String stockSymbol, double alertPrice) {
        watchedStocks.put(stockSymbol, alertPrice);
        System.out.println(name + " 开始关注股票: " + stockSymbol + ", 预警价格: " + alertPrice);
    }
    
    @Override
    public void update(String stockSymbol, double price) {
        Double alertPrice = watchedStocks.get(stockSymbol);
        if (alertPrice != null) {
            if (price >= alertPrice) {
                System.out.println("【警告】" + name + ": 股票 " + stockSymbol + " 当前价格 " + price + 
                                 " 已达到或超过预警价格 " + alertPrice + "，建议卖出！");
            } else if (price <= alertPrice * 0.9) { // 价格下跌超过10%
                System.out.println("【提醒】" + name + ": 股票 " + stockSymbol + " 当前价格 " + price + 
                                 " 较预警价格 " + alertPrice + " 下跌超过10%，可考虑买入！");
            }
        }
    }
}

public class Chapter19Example {
    public static void main(String[] args) {
        System.out.println("=== 观察者模式示例 ===\n");
        
        // 1. 基本观察者模式示例
        System.out.println("1. 基本观察者模式示例:");
        basicObserverExample();
        
        // 2. 新闻发布系统示例
        System.out.println("\n2. 新闻发布系统示例:");
        newsPublisherExample();
        
        // 3. 股票价格监控系统示例
        System.out.println("\n3. 股票价格监控系统示例:");
        stockPriceMonitorExample();
    }
    
    // 基本观察者模式示例
    public static void basicObserverExample() {
        // 创建主题
        ConcreteSubject subject = new ConcreteSubject();
        
        // 创建观察者
        ConcreteObserver observer1 = new ConcreteObserver("观察者1");
        ConcreteObserver observer2 = new ConcreteObserver("观察者2");
        ConcreteObserver observer3 = new ConcreteObserver("观察者3");
        
        // 注册观察者
        subject.addObserver(observer1);
        subject.addObserver(observer2);
        subject.addObserver(observer3);
        
        // 改变主题状态
        subject.setState("新状态");
        
        System.out.println();
        
        // 移除一个观察者
        subject.removeObserver(observer2);
        
        // 再次改变主题状态
        subject.setState("另一个状态");
    }
    
    // 新闻发布系统示例
    public static void newsPublisherExample() {
        // 创建新闻发布者
        NewsPublisher publisher = new NewsPublisher();
        
        // 创建用户
        User user1 = new User("张三");
        User user2 = new User("李四");
        User user3 = new User("王五");
        
        // 用户订阅新闻类别
        user1.subscribeCategory("科技");
        user1.subscribeCategory("体育");
        
        user2.subscribeCategory("科技");
        user2.subscribeCategory("娱乐");
        
        user3.subscribeCategory("体育");
        user3.subscribeCategory("娱乐");
        
        // 注册用户到新闻发布者
        publisher.subscribe(user1);
        publisher.subscribe(user2);
        publisher.subscribe(user3);
        
        System.out.println();
        
        // 发布新闻
        publisher.publishNews("科技", "Java 17正式发布，带来众多新特性");
        publisher.publishNews("体育", "世界杯决赛今晚开战");
        publisher.publishNews("娱乐", "著名演员获得奥斯卡奖");
        
        System.out.println();
        
        // 用户取消订阅
        user1.unsubscribeCategory("体育");
        
        // 再次发布体育新闻
        publisher.publishNews("体育", "篮球巨星宣布退役");
    }
    
    // 股票价格监控系统示例
    public static void stockPriceMonitorExample() {
        // 创建股票价格监控系统
        StockPriceMonitor monitor = new StockPriceMonitor();
        
        // 创建投资者
        Investor investor1 = new Investor("散户甲");
        Investor investor2 = new Investor("散户乙");
        Investor investor3 = new Investor("机构投资者");
        
        // 投资者关注股票及设置预警价格
        investor1.watchStock("AAPL", 150.0);
        investor1.watchStock("GOOGL", 2800.0);
        
        investor2.watchStock("AAPL", 140.0);
        investor2.watchStock("TSLA", 800.0);
        
        investor3.watchStock("GOOGL", 2700.0);
        investor3.watchStock("MSFT", 300.0);
        
        // 注册投资者到监控系统
        monitor.addObserver(investor1);
        monitor.addObserver(investor2);
        monitor.addObserver(investor3);
        
        System.out.println();
        
        // 更新股票价格
        monitor.updateStockPrice("AAPL", 155.0);  // 触发警告
        monitor.updateStockPrice("GOOGL", 2750.0); // 触发提醒
        monitor.updateStockPrice("TSLA", 750.0);   // 触发提醒
        monitor.updateStockPrice("MSFT", 310.0);   // 无特殊提醒
        
        System.out.println();
        
        // 进一步更新价格
        monitor.updateStockPrice("AAPL", 135.0);   // 触发提醒
        monitor.updateStockPrice("GOOGL", 2600.0); // 触发警告
    }
}