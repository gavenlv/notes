"""
第19章：观察者模式 (Observer Pattern)

观察者模式是一种行为设计模式，它定义了一种一对多的依赖关系，让多个观察者对象
同时监听某一个主题对象。当主题对象状态发生变化时，它会通知所有观察者对象，
使它们能够自动更新。
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any


class Observer(ABC):
    """观察者接口"""
    
    @abstractmethod
    def update(self, subject) -> None:
        """更新方法"""
        pass


class Subject(ABC):
    """主题接口"""
    
    @abstractmethod
    def attach(self, observer: Observer) -> None:
        """附加观察者"""
        pass
    
    @abstractmethod
    def detach(self, observer: Observer) -> None:
        """分离观察者"""
        pass
    
    @abstractmethod
    def notify(self) -> None:
        """通知观察者"""
        pass


class ConcreteSubject(Subject):
    """具体主题类"""
    
    def __init__(self):
        self._observers: List[Observer] = []
        self._state: Dict[str, Any] = {}
    
    def attach(self, observer: Observer) -> None:
        """附加观察者"""
        if observer not in self._observers:
            self._observers.append(observer)
    
    def detach(self, observer: Observer) -> None:
        """分离观察者"""
        if observer in self._observers:
            self._observers.remove(observer)
    
    def notify(self) -> None:
        """通知所有观察者"""
        for observer in self._observers:
            observer.update(self)
    
    def set_state(self, key: str, value: Any) -> None:
        """设置状态"""
        self._state[key] = value
        self.notify()
    
    def get_state(self) -> Dict[str, Any]:
        """获取状态"""
        return self._state.copy()


# 示例1：股票价格监控系统
class StockMarket(Subject):
    """股票市场（主题）"""
    
    def __init__(self):
        super().__init__()
        self._stock_prices: Dict[str, float] = {}
        self._observers: List[Observer] = []
    
    def attach(self, observer: Observer) -> None:
        """附加观察者"""
        if observer not in self._observers:
            self._observers.append(observer)
    
    def detach(self, observer: Observer) -> None:
        """分离观察者"""
        if observer in self._observers:
            self._observers.remove(observer)
    
    def notify(self) -> None:
        """通知观察者"""
        for observer in self._observers:
            observer.update(self)
    
    def update_stock_price(self, symbol: str, price: float) -> None:
        """更新股票价格"""
        old_price = self._stock_prices.get(symbol)
        self._stock_prices[symbol] = price
        
        if old_price is not None:
            change = price - old_price
            change_percent = (change / old_price) * 100
            print(f"{symbol}: {old_price:.2f} -> {price:.2f} ({change:+.2f}, {change_percent:+.2f}%)")
        else:
            print(f"{symbol}: 新上市 {price:.2f}")
        
        self.notify()
    
    def get_stock_price(self, symbol: str) -> float:
        """获取股票价格"""
        return self._stock_prices.get(symbol, 0.0)
    
    def get_all_prices(self) -> Dict[str, float]:
        """获取所有股票价格"""
        return self._stock_prices.copy()


class StockInvestor(Observer):
    """股票投资者（观察者）"""
    
    def __init__(self, name: str, interests: List[str]):
        self.name = name
        self.interests = interests
        self._alert_threshold = 5.0  # 价格变化超过5%时提醒
    
    def update(self, subject: StockMarket) -> None:
        """更新方法"""
        prices = subject.get_all_prices()
        
        for symbol in self.interests:
            if symbol in prices:
                price = prices[symbol]
                print(f"{self.name} 收到 {symbol} 价格更新: {price:.2f}")
    
    def set_alert_threshold(self, threshold: float) -> None:
        """设置提醒阈值"""
        self._alert_threshold = threshold


class StockAnalyst(Observer):
    """股票分析师（观察者）"""
    
    def __init__(self, name: str):
        self.name = name
        self._price_history: Dict[str, List[float]] = {}
    
    def update(self, subject: StockMarket) -> None:
        """更新方法"""
        prices = subject.get_all_prices()
        
        for symbol, price in prices.items():
            if symbol not in self._price_history:
                self._price_history[symbol] = []
            
            self._price_history[symbol].append(price)
            
            # 分析价格趋势
            if len(self._price_history[symbol]) >= 3:
                recent_prices = self._price_history[symbol][-3:]
                trend = self._analyze_trend(recent_prices)
                print(f"{self.name} 分析: {symbol} {trend}")
    
    def _analyze_trend(self, prices: List[float]) -> str:
        """分析价格趋势"""
        if len(prices) < 2:
            return "数据不足"
        
        changes = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        avg_change = sum(changes) / len(changes)
        
        if avg_change > 0:
            return "上涨趋势"
        elif avg_change < 0:
            return "下跌趋势"
        else:
            return "平稳"


# 示例2：天气监测系统
class WeatherStation(Subject):
    """气象站（主题）"""
    
    def __init__(self):
        super().__init__()
        self._observers: List[Observer] = []
        self._temperature = 20.0
        self._humidity = 50.0
        self._pressure = 1013.25
    
    def attach(self, observer: Observer) -> None:
        """附加观察者"""
        if observer not in self._observers:
            self._observers.append(observer)
    
    def detach(self, observer: Observer) -> None:
        """分离观察者"""
        if observer in self._observers:
            self._observers.remove(observer)
    
    def notify(self) -> None:
        """通知观察者"""
        for observer in self._observers:
            observer.update(self)
    
    def set_measurements(self, temperature: float, humidity: float, pressure: float) -> None:
        """设置测量数据"""
        self._temperature = temperature
        self._humidity = humidity
        self._pressure = pressure
        self.notify()
    
    def get_temperature(self) -> float:
        return self._temperature
    
    def get_humidity(self) -> float:
        return self._humidity
    
    def get_pressure(self) -> float:
        return self._pressure


class CurrentConditionsDisplay(Observer):
    """当前状况显示（观察者）"""
    
    def __init__(self, name: str):
        self.name = name
    
    def update(self, subject: WeatherStation) -> None:
        """更新方法"""
        temp = subject.get_temperature()
        humidity = subject.get_humidity()
        pressure = subject.get_pressure()
        
        print(f"{self.name} - 当前状况: ")
        print(f"  温度: {temp:.1f}°C")
        print(f"  湿度: {humidity:.1f}%")
        print(f"  气压: {pressure:.1f} hPa")


class StatisticsDisplay(Observer):
    """统计显示（观察者）"""
    
    def __init__(self, name: str):
        self.name = name
        self._temperature_readings: List[float] = []
        self._humidity_readings: List[float] = []
    
    def update(self, subject: WeatherStation) -> None:
        """更新方法"""
        temp = subject.get_temperature()
        humidity = subject.get_humidity()
        
        self._temperature_readings.append(temp)
        self._humidity_readings.append(humidity)
        
        avg_temp = sum(self._temperature_readings) / len(self._temperature_readings)
        max_temp = max(self._temperature_readings)
        min_temp = min(self._temperature_readings)
        
        avg_humidity = sum(self._humidity_readings) / len(self._humidity_readings)
        
        print(f"{self.name} - 统计信息:")
        print(f"  平均温度: {avg_temp:.1f}°C")
        print(f"  最高温度: {max_temp:.1f}°C")
        print(f"  最低温度: {min_temp:.1f}°C")
        print(f"  平均湿度: {avg_humidity:.1f}%")


class ForecastDisplay(Observer):
    """天气预报显示（观察者）"""
    
    def __init__(self, name: str):
        self.name = name
        self._last_pressure = 0.0
    
    def update(self, subject: WeatherStation) -> None:
        """更新方法"""
        current_pressure = subject.get_pressure()
        
        if self._last_pressure == 0:
            forecast = "无法预测"
        elif current_pressure > self._last_pressure:
            forecast = "天气转好"
        elif current_pressure < self._last_pressure:
            forecast = "天气转坏"
        else:
            forecast = "天气稳定"
        
        print(f"{self.name} - 天气预报: {forecast}")
        self._last_pressure = current_pressure


# 示例3：新闻发布系统
class NewsAgency(Subject):
    """新闻机构（主题）"""
    
    def __init__(self):
        super().__init__()
        self._observers: List[Observer] = []
        self._latest_news: Dict[str, str] = {}
    
    def attach(self, observer: Observer) -> None:
        """附加观察者"""
        if observer not in self._observers:
            self._observers.append(observer)
    
    def detach(self, observer: Observer) -> None:
        """分离观察者"""
        if observer in self._observers:
            self._observers.remove(observer)
    
    def notify(self) -> None:
        """通知观察者"""
        for observer in self._observers:
            observer.update(self)
    
    def publish_news(self, category: str, headline: str) -> None:
        """发布新闻"""
        self._latest_news[category] = headline
        print(f"新闻发布 - {category}: {headline}")
        self.notify()
    
    def get_latest_news(self) -> Dict[str, str]:
        """获取最新新闻"""
        return self._latest_news.copy()


class NewsSubscriber(Observer):
    """新闻订阅者（观察者）"""
    
    def __init__(self, name: str, interests: List[str]):
        self.name = name
        self.interests = interests
    
    def update(self, subject: NewsAgency) -> None:
        """更新方法"""
        latest_news = subject.get_latest_news()
        
        for category, headline in latest_news.items():
            if category in self.interests:
                print(f"{self.name} 收到 {category} 新闻: {headline}")


# 示例4：事件驱动系统
class EventManager(Subject):
    """事件管理器"""
    
    def __init__(self):
        super().__init__()
        self._observers: List[Observer] = []
        self._events: List[Dict[str, Any]] = []
    
    def attach(self, observer: Observer) -> None:
        """附加观察者"""
        if observer not in self._observers:
            self._observers.append(observer)
    
    def detach(self, observer: Observer) -> None:
        """分离观察者"""
        if observer in self._observers:
            self._observers.remove(observer)
    
    def notify(self) -> None:
        """通知观察者"""
        for observer in self._observers:
            observer.update(self)
    
    def trigger_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """触发事件"""
        event = {
            'type': event_type,
            'data': data,
            'timestamp': '2024-01-01 12:00:00'
        }
        self._events.append(event)
        print(f"事件触发: {event_type}")
        self.notify()
    
    def get_recent_events(self) -> List[Dict[str, Any]]:
        """获取最近事件"""
        return self._events[-5:] if self._events else []


class EventListener(Observer):
    """事件监听器"""
    
    def __init__(self, name: str, event_types: List[str]):
        self.name = name
        self.event_types = event_types
    
    def update(self, subject: EventManager) -> None:
        """更新方法"""
        recent_events = subject.get_recent_events()
        
        for event in recent_events:
            if event['type'] in self.event_types:
                print(f"{self.name} 处理事件: {event['type']} - {event['data']}")


def test_stock_market():
    """测试股票市场系统"""
    print("=== 测试股票市场系统 ===")
    
    market = StockMarket()
    
    # 创建投资者和分析师
    investor1 = StockInvestor("张三", ["AAPL", "GOOGL"])
    investor2 = StockInvestor("李四", ["TSLA", "MSFT"])
    analyst = StockAnalyst("王分析师")
    
    # 注册观察者
    market.attach(investor1)
    market.attach(investor2)
    market.attach(analyst)
    
    # 更新股票价格
    market.update_stock_price("AAPL", 150.25)
    market.update_stock_price("GOOGL", 2750.80)
    market.update_stock_price("TSLA", 850.60)
    market.update_stock_price("MSFT", 305.45)
    
    # 再次更新价格
    market.update_stock_price("AAPL", 152.30)
    market.update_stock_price("TSLA", 845.20)


def test_weather_station():
    """测试气象站系统"""
    print("\n=== 测试气象站系统 ===")
    
    weather_station = WeatherStation()
    
    # 创建显示设备
    current_display = CurrentConditionsDisplay("当前状况显示器")
    stats_display = StatisticsDisplay("统计显示器")
    forecast_display = ForecastDisplay("天气预报显示器")
    
    # 注册观察者
    weather_station.attach(current_display)
    weather_station.attach(stats_display)
    weather_station.attach(forecast_display)
    
    # 更新气象数据
    weather_station.set_measurements(25.5, 65.0, 1015.0)
    weather_station.set_measurements(26.0, 70.0, 1012.0)
    weather_station.set_measurements(24.0, 90.0, 1008.0)


def test_news_agency():
    """测试新闻发布系统"""
    print("\n=== 测试新闻发布系统 ===")
    
    news_agency = NewsAgency()
    
    # 创建订阅者
    subscriber1 = NewsSubscriber("体育迷", ["体育", "娱乐"])
    subscriber2 = NewsSubscriber("财经达人", ["财经", "科技"])
    subscriber3 = NewsSubscriber("全能读者", ["体育", "财经", "科技", "娱乐"])
    
    # 注册观察者
    news_agency.attach(subscriber1)
    news_agency.attach(subscriber2)
    news_agency.attach(subscriber3)
    
    # 发布新闻
    news_agency.publish_news("体育", "中国男篮获得亚运会冠军")
    news_agency.publish_news("财经", "央行宣布降准0.5个百分点")
    news_agency.publish_news("科技", "人工智能技术取得重大突破")
    news_agency.publish_news("娱乐", "新电影票房突破10亿元")


def test_event_system():
    """测试事件驱动系统"""
    print("\n=== 测试事件驱动系统 ===")
    
    event_manager = EventManager()
    
    # 创建事件监听器
    ui_listener = EventListener("UI监听器", ["user_click", "window_resize"])
    data_listener = EventListener("数据监听器", ["data_update", "cache_clear"])
    system_listener = EventListener("系统监听器", ["system_start", "system_shutdown"])
    
    # 注册观察者
    event_manager.attach(ui_listener)
    event_manager.attach(data_listener)
    event_manager.attach(system_listener)
    
    # 触发事件
    event_manager.trigger_event("user_click", {"button": "submit", "x": 100, "y": 200})
    event_manager.trigger_event("data_update", {"table": "users", "rows": 150})
    event_manager.trigger_event("system_start", {"version": "1.0.0", "time": "12:00"})
    event_manager.trigger_event("window_resize", {"width": 1920, "height": 1080})


if __name__ == "__main__":
    # 运行所有测试
    test_stock_market()
    test_weather_station()
    test_news_agency()
    test_event_system()
    
    print("\n=== 观察者模式测试完成 ===")
    print("\n观察者模式总结：")
    print("1. 实现松耦合的对象间通信")
    print("2. 支持一对多的依赖关系")
    print("3. 主题变化时自动通知观察者")
    print("4. 适用于事件驱动系统")
    print("5. 注意避免循环通知和内存泄漏")