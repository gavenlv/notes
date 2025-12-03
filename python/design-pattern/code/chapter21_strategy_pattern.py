"""
第21章：策略模式 (Strategy Pattern)

策略模式是一种行为设计模式，它定义了一系列算法，并将每个算法封装起来，
使它们可以相互替换。策略模式让算法的变化独立于使用算法的客户。
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any


class PaymentStrategy(ABC):
    """支付策略接口"""
    
    @abstractmethod
    def pay(self, amount: float) -> None:
        """支付方法"""
        pass


class CreditCardPayment(PaymentStrategy):
    """信用卡支付策略"""
    
    def __init__(self, card_number: str, expiry_date: str, cvv: str):
        self.card_number = card_number
        self.expiry_date = expiry_date
        self.cvv = cvv
    
    def pay(self, amount: float) -> None:
        print(f"使用信用卡支付 {amount:.2f} 元")
        print(f"卡号: {self.card_number[-4:]}")
        print("支付成功！")


class PayPalPayment(PaymentStrategy):
    """PayPal支付策略"""
    
    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password
    
    def pay(self, amount: float) -> None:
        print(f"使用PayPal支付 {amount:.2f} 元")
        print(f"账户: {self.email}")
        print("支付成功！")


class WeChatPayment(PaymentStrategy):
    """微信支付策略"""
    
    def __init__(self, openid: str):
        self.openid = openid
    
    def pay(self, amount: float) -> None:
        print(f"使用微信支付 {amount:.2f} 元")
        print(f"用户ID: {self.openid}")
        print("支付成功！")


class AliPayPayment(PaymentStrategy):
    """支付宝支付策略"""
    
    def __init__(self, account: str):
        self.account = account
    
    def pay(self, amount: float) -> None:
        print(f"使用支付宝支付 {amount:.2f} 元")
        print(f"账户: {self.account}")
        print("支付成功！")


class PaymentContext:
    """支付上下文类"""
    
    def __init__(self, strategy: PaymentStrategy = None):
        self._strategy = strategy
    
    def set_strategy(self, strategy: PaymentStrategy) -> None:
        """设置支付策略"""
        self._strategy = strategy
    
    def execute_payment(self, amount: float) -> None:
        """执行支付"""
        if self._strategy:
            self._strategy.pay(amount)
        else:
            print("请先设置支付策略")


# 示例2：排序算法策略
class SortStrategy(ABC):
    """排序策略接口"""
    
    @abstractmethod
    def sort(self, data: List[int]) -> List[int]:
        """排序方法"""
        pass


class BubbleSortStrategy(SortStrategy):
    """冒泡排序策略"""
    
    def sort(self, data: List[int]) -> List[int]:
        print("使用冒泡排序算法")
        n = len(data)
        for i in range(n):
            for j in range(0, n - i - 1):
                if data[j] > data[j + 1]:
                    data[j], data[j + 1] = data[j + 1], data[j]
        return data


class QuickSortStrategy(SortStrategy):
    """快速排序策略"""
    
    def _quick_sort(self, data: List[int]) -> List[int]:
        if len(data) <= 1:
            return data
        pivot = data[len(data) // 2]
        left = [x for x in data if x < pivot]
        middle = [x for x in data if x == pivot]
        right = [x for x in data if x > pivot]
        return self._quick_sort(left) + middle + self._quick_sort(right)
    
    def sort(self, data: List[int]) -> List[int]:
        print("使用快速排序算法")
        return self._quick_sort(data.copy())


class MergeSortStrategy(SortStrategy):
    """归并排序策略"""
    
    def _merge_sort(self, data: List[int]) -> List[int]:
        if len(data) <= 1:
            return data
        mid = len(data) // 2
        left = self._merge_sort(data[:mid])
        right = self._merge_sort(data[mid:])
        return self._merge(left, right)
    
    def _merge(self, left: List[int], right: List[int]) -> List[int]:
        result = []
        i = j = 0
        while i < len(left) and j < len(right):
            if left[i] <= right[j]:
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1
        result.extend(left[i:])
        result.extend(right[j:])
        return result
    
    def sort(self, data: List[int]) -> List[int]:
        print("使用归并排序算法")
        return self._merge_sort(data.copy())


class SortContext:
    """排序上下文类"""
    
    def __init__(self, strategy: SortStrategy = None):
        self._strategy = strategy
    
    def set_strategy(self, strategy: SortStrategy) -> None:
        """设置排序策略"""
        self._strategy = strategy
    
    def execute_sort(self, data: List[int]) -> List[int]:
        """执行排序"""
        if self._strategy:
            return self._strategy.sort(data)
        else:
            print("请先设置排序策略")
            return data


# 示例3：压缩算法策略
class CompressionStrategy(ABC):
    """压缩策略接口"""
    
    @abstractmethod
    def compress(self, data: str) -> str:
        """压缩方法"""
        pass
    
    @abstractmethod
    def decompress(self, data: str) -> str:
        """解压方法"""
        pass


class ZipCompression(CompressionStrategy):
    """ZIP压缩策略"""
    
    def compress(self, data: str) -> str:
        print("使用ZIP压缩算法")
        # 简化的压缩实现
        compressed = f"ZIP[{data}]"
        return compressed
    
    def decompress(self, data: str) -> str:
        print("使用ZIP解压算法")
        if data.startswith("ZIP[") and data.endswith("]"):
            return data[4:-1]
        return data


class RarCompression(CompressionStrategy):
    """RAR压缩策略"""
    
    def compress(self, data: str) -> str:
        print("使用RAR压缩算法")
        # 简化的压缩实现
        compressed = f"RAR[{data}]"
        return compressed
    
    def decompress(self, data: str) -> str:
        print("使用RAR解压算法")
        if data.startswith("RAR[") and data.endswith("]"):
            return data[4:-1]
        return data


class SevenZipCompression(CompressionStrategy):
    """7-Zip压缩策略"""
    
    def compress(self, data: str) -> str:
        print("使用7-Zip压缩算法")
        # 简化的压缩实现
        compressed = f"7Z[{data}]"
        return compressed
    
    def decompress(self, data: str) -> str:
        print("使用7-Zip解压算法")
        if data.startswith("7Z[") and data.endswith("]"):
            return data[3:-1]
        return data


class CompressionContext:
    """压缩上下文类"""
    
    def __init__(self, strategy: CompressionStrategy = None):
        self._strategy = strategy
    
    def set_strategy(self, strategy: CompressionStrategy) -> None:
        """设置压缩策略"""
        self._strategy = strategy
    
    def compress(self, data: str) -> str:
        """执行压缩"""
        if self._strategy:
            return self._strategy.compress(data)
        else:
            print("请先设置压缩策略")
            return data
    
    def decompress(self, data: str) -> str:
        """执行解压"""
        if self._strategy:
            return self._strategy.decompress(data)
        else:
            print("请先设置压缩策略")
            return data


# 示例4：导航策略
class NavigationStrategy(ABC):
    """导航策略接口"""
    
    @abstractmethod
    def calculate_route(self, start: str, destination: str) -> str:
        """计算路线"""
        pass


class DrivingNavigation(NavigationStrategy):
    """驾车导航策略"""
    
    def calculate_route(self, start: str, destination: str) -> str:
        print(f"计算驾车路线: {start} -> {destination}")
        return f"驾车路线: {start} -> 高速公路 -> {destination}"


class WalkingNavigation(NavigationStrategy):
    """步行导航策略"""
    
    def calculate_route(self, start: str, destination: str) -> str:
        print(f"计算步行路线: {start} -> {destination}")
        return f"步行路线: {start} -> 人行道 -> {destination}"


class PublicTransportNavigation(NavigationStrategy):
    """公共交通导航策略"""
    
    def calculate_route(self, start: str, destination: str) -> str:
        print(f"计算公共交通路线: {start} -> {destination}")
        return f"公共交通路线: {start} -> 地铁 -> 公交 -> {destination}"


class BikingNavigation(NavigationStrategy):
    """骑行导航策略"""
    
    def calculate_route(self, start: str, destination: str) -> str:
        print(f"计算骑行路线: {start} -> {destination}")
        return f"骑行路线: {start} -> 自行车道 -> {destination}"


class NavigationContext:
    """导航上下文类"""
    
    def __init__(self, strategy: NavigationStrategy = None):
        self._strategy = strategy
    
    def set_strategy(self, strategy: NavigationStrategy) -> None:
        """设置导航策略"""
        self._strategy = strategy
    
    def get_route(self, start: str, destination: str) -> str:
        """获取路线"""
        if self._strategy:
            return self._strategy.calculate_route(start, destination)
        else:
            return "请先设置导航策略"


# 示例5：折扣策略
class DiscountStrategy(ABC):
    """折扣策略接口"""
    
    @abstractmethod
    def calculate_discount(self, amount: float) -> float:
        """计算折扣"""
        pass


class NoDiscount(DiscountStrategy):
    """无折扣策略"""
    
    def calculate_discount(self, amount: float) -> float:
        return 0.0


class PercentageDiscount(DiscountStrategy):
    """百分比折扣策略"""
    
    def __init__(self, percentage: float):
        self.percentage = percentage
    
    def calculate_discount(self, amount: float) -> float:
        return amount * (self.percentage / 100)


class FixedAmountDiscount(DiscountStrategy):
    """固定金额折扣策略"""
    
    def __init__(self, amount: float):
        self.amount = amount
    
    def calculate_discount(self, total_amount: float) -> float:
        return min(self.amount, total_amount)


class SeasonalDiscount(DiscountStrategy):
    """季节性折扣策略"""
    
    def __init__(self, season: str):
        self.season = season
        self.discounts = {
            "spring": 0.1,  # 春季10%折扣
            "summer": 0.2,  # 夏季20%折扣
            "autumn": 0.15, # 秋季15%折扣
            "winter": 0.25  # 冬季25%折扣
        }
    
    def calculate_discount(self, amount: float) -> float:
        discount_rate = self.discounts.get(self.season.lower(), 0.0)
        return amount * discount_rate


class ShoppingCart:
    """购物车类"""
    
    def __init__(self):
        self.items: List[Dict[str, Any]] = []
        self._discount_strategy: DiscountStrategy = NoDiscount()
    
    def add_item(self, name: str, price: float, quantity: int = 1) -> None:
        """添加商品"""
        self.items.append({
            'name': name,
            'price': price,
            'quantity': quantity
        })
    
    def set_discount_strategy(self, strategy: DiscountStrategy) -> None:
        """设置折扣策略"""
        self._discount_strategy = strategy
    
    def calculate_total(self) -> float:
        """计算总价"""
        total = sum(item['price'] * item['quantity'] for item in self.items)
        discount = self._discount_strategy.calculate_discount(total)
        final_total = total - discount
        
        print(f"商品总价: {total:.2f} 元")
        print(f"折扣金额: {discount:.2f} 元")
        print(f"最终价格: {final_total:.2f} 元")
        
        return final_total


def test_payment_strategies():
    """测试支付策略"""
    print("=== 测试支付策略 ===")
    
    payment_context = PaymentContext()
    
    # 测试信用卡支付
    credit_card = CreditCardPayment("1234-5678-9012-3456", "12/25", "123")
    payment_context.set_strategy(credit_card)
    payment_context.execute_payment(100.50)
    
    print()
    
    # 测试微信支付
    wechat_pay = WeChatPayment("wx123456789")
    payment_context.set_strategy(wechat_pay)
    payment_context.execute_payment(200.75)


def test_sort_strategies():
    """测试排序策略"""
    print("\n=== 测试排序策略 ===")
    
    data = [64, 34, 25, 12, 22, 11, 90]
    print(f"原始数据: {data}")
    
    sort_context = SortContext()
    
    # 测试冒泡排序
    bubble_sort = BubbleSortStrategy()
    sort_context.set_strategy(bubble_sort)
    result = sort_context.execute_sort(data.copy())
    print(f"冒泡排序结果: {result}")
    
    # 测试快速排序
    quick_sort = QuickSortStrategy()
    sort_context.set_strategy(quick_sort)
    result = sort_context.execute_sort(data.copy())
    print(f"快速排序结果: {result}")
    
    # 测试归并排序
    merge_sort = MergeSortStrategy()
    sort_context.set_strategy(merge_sort)
    result = sort_context.execute_sort(data.copy())
    print(f"归并排序结果: {result}")


def test_compression_strategies():
    """测试压缩策略"""
    print("\n=== 测试压缩策略 ===")
    
    original_data = "Hello World! This is a test string for compression."
    print(f"原始数据: {original_data}")
    
    compression_context = CompressionContext()
    
    # 测试ZIP压缩
    zip_compression = ZipCompression()
    compression_context.set_strategy(zip_compression)
    compressed = compression_context.compress(original_data)
    print(f"压缩后: {compressed}")
    decompressed = compression_context.decompress(compressed)
    print(f"解压后: {decompressed}")
    
    print()
    
    # 测试RAR压缩
    rar_compression = RarCompression()
    compression_context.set_strategy(rar_compression)
    compressed = compression_context.compress(original_data)
    print(f"压缩后: {compressed}")
    decompressed = compression_context.decompress(compressed)
    print(f"解压后: {decompressed}")


def test_navigation_strategies():
    """测试导航策略"""
    print("\n=== 测试导航策略 ===")
    
    navigation_context = NavigationContext()
    
    # 测试驾车导航
    driving_nav = DrivingNavigation()
    navigation_context.set_strategy(driving_nav)
    route = navigation_context.get_route("北京天安门", "上海外滩")
    print(route)
    
    # 测试步行导航
    walking_nav = WalkingNavigation()
    navigation_context.set_strategy(walking_nav)
    route = navigation_context.get_route("公司", "地铁站")
    print(route)
    
    # 测试公共交通导航
    public_nav = PublicTransportNavigation()
    navigation_context.set_strategy(public_nav)
    route = navigation_context.get_route("家", "商场")
    print(route)


def test_discount_strategies():
    """测试折扣策略"""
    print("\n=== 测试折扣策略 ===")
    
    cart = ShoppingCart()
    cart.add_item("笔记本电脑", 5999.00, 1)
    cart.add_item("鼠标", 99.00, 2)
    cart.add_item("键盘", 299.00, 1)
    
    # 无折扣
    print("1. 无折扣:")
    cart.set_discount_strategy(NoDiscount())
    cart.calculate_total()
    
    print("\n2. 百分比折扣(10%):")
    cart.set_discount_strategy(PercentageDiscount(10))
    cart.calculate_total()
    
    print("\n3. 固定金额折扣(500元):")
    cart.set_discount_strategy(FixedAmountDiscount(500))
    cart.calculate_total()
    
    print("\n4. 季节性折扣(冬季):")
    cart.set_discount_strategy(SeasonalDiscount("winter"))
    cart.calculate_total()


if __name__ == "__main__":
    # 运行所有测试
    test_payment_strategies()
    test_sort_strategies()
    test_compression_strategies()
    test_navigation_strategies()
    test_discount_strategies()
    
    print("\n=== 策略模式测试完成 ===")
    print("\n策略模式总结：")
    print("1. 定义一系列可互换的算法")
    print("2. 算法可以独立于客户端变化")
    print("3. 避免使用多重条件判断")
    print("4. 符合开闭原则")
    print("5. 适用于需要多种算法的场景")