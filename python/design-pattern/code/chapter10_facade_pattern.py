"""
外观模式 (Facade Pattern) 示例代码

外观模式为子系统中的一组接口提供一个一致的界面，此模式定义了一个高层接口，这个接口使得这一子系统更加容易使用。
"""

class CPU:
    """CPU子系统"""
    
    def freeze(self):
        print("CPU: 冻结")
    
    def jump(self, position):
        print(f"CPU: 跳转到地址 {position}")
    
    def execute(self):
        print("CPU: 执行")


class Memory:
    """内存子系统"""
    
    def __init__(self):
        self._data = {}
    
    def load(self, position, data):
        self._data[position] = data
        print(f"内存: 在地址 {position} 加载数据")
    
    def read(self, position):
        data = self._data.get(position, "0x00")
        print(f"内存: 从地址 {position} 读取数据: {data}")
        return data


class HardDrive:
    """硬盘子系统"""
    
    def read(self, lba, size):
        print(f"硬盘: 从LBA {lba} 读取 {size} 字节数据")
        return f"数据块 {lba}"


class ComputerFacade:
    """计算机外观类"""
    
    def __init__(self):
        self._cpu = CPU()
        self._memory = Memory()
        self._hard_drive = HardDrive()
    
    def start(self):
        """启动计算机"""
        print("=== 计算机启动过程 ===")
        self._cpu.freeze()
        
        # 从硬盘读取引导程序
        boot_sector = self._hard_drive.read(0, 512)
        
        # 加载引导程序到内存
        self._memory.load(0, boot_sector)
        self._memory.load(512, "操作系统内核")
        
        # CPU执行引导程序
        self._cpu.jump(0)
        self._cpu.execute()
        
        print("计算机启动完成!")
    
    def shutdown(self):
        """关闭计算机"""
        print("=== 计算机关闭过程 ===")
        print("保存数据到硬盘...")
        print("清理内存...")
        print("CPU停止执行...")
        print("计算机关闭完成!")


# 测试外观模式
def test_computer_facade():
    """测试计算机外观模式"""
    print("=== 外观模式测试 - 计算机启动示例 ===\n")
    
    computer = ComputerFacade()
    
    # 用户只需要调用简单的接口
    computer.start()
    print("\n---")
    computer.shutdown()


# 实际应用示例：银行系统
def test_bank_facade():
    """测试银行系统外观模式"""
    print("\n=== 外观模式应用 - 银行系统示例 ===\n")
    
    class AccountService:
        """账户服务子系统"""
        
        def verify_account(self, account_number):
            print(f"账户服务: 验证账户 {account_number}")
            return True
        
        def get_balance(self, account_number):
            print(f"账户服务: 获取账户 {account_number} 余额")
            return 1000.0
        
        def update_balance(self, account_number, amount):
            print(f"账户服务: 更新账户 {account_number} 余额，变动金额: {amount}")


    class SecurityService:
        """安全服务子系统"""
        
        def verify_pin(self, account_number, pin):
            print(f"安全服务: 验证账户 {account_number} 的PIN码")
            return True
        
        def log_transaction(self, account_number, transaction_type, amount):
            print(f"安全服务: 记录交易 - 账户: {account_number}, 类型: {transaction_type}, 金额: {amount}")


    class NotificationService:
        """通知服务子系统"""
        
        def send_sms(self, phone_number, message):
            print(f"通知服务: 发送短信到 {phone_number}: {message}")
        
        def send_email(self, email, message):
            print(f"通知服务: 发送邮件到 {email}: {message}")


    class BankFacade:
        """银行外观类"""
        
        def __init__(self):
            self._account_service = AccountService()
            self._security_service = SecurityService()
            self._notification_service = NotificationService()
        
        def withdraw_cash(self, account_number, pin, amount):
            """取款操作"""
            print(f"\n=== 取款操作: 账户 {account_number}, 金额 {amount} ===")
            
            # 验证安全
            if not self._security_service.verify_pin(account_number, pin):
                print("安全验证失败!")
                return False
            
            # 验证账户
            if not self._account_service.verify_account(account_number):
                print("账户验证失败!")
                return False
            
            # 检查余额
            balance = self._account_service.get_balance(account_number)
            if balance < amount:
                print("余额不足!")
                return False
            
            # 执行取款
            self._account_service.update_balance(account_number, -amount)
            
            # 记录交易
            self._security_service.log_transaction(account_number, "取款", amount)
            
            # 发送通知
            self._notification_service.send_sms("13800138000", 
                                               f"您的账户{account_number}取款{amount}元，余额{balance-amount}元")
            
            print(f"取款成功! 当前余额: {balance - amount}")
            return True
        
        def deposit_cash(self, account_number, pin, amount):
            """存款操作"""
            print(f"\n=== 存款操作: 账户 {account_number}, 金额 {amount} ===")
            
            # 验证安全
            if not self._security_service.verify_pin(account_number, pin):
                print("安全验证失败!")
                return False
            
            # 验证账户
            if not self._account_service.verify_account(account_number):
                print("账户验证失败!")
                return False
            
            # 执行存款
            balance = self._account_service.get_balance(account_number)
            self._account_service.update_balance(account_number, amount)
            
            # 记录交易
            self._security_service.log_transaction(account_number, "存款", amount)
            
            # 发送通知
            self._notification_service.send_email("user@example.com",
                                                 f"您的账户{account_number}存款{amount}元，余额{balance+amount}元")
            
            print(f"存款成功! 当前余额: {balance + amount}")
            return True
        
        def check_balance(self, account_number, pin):
            """查询余额"""
            print(f"\n=== 查询余额: 账户 {account_number} ===")
            
            # 验证安全
            if not self._security_service.verify_pin(account_number, pin):
                print("安全验证失败!")
                return None
            
            # 验证账户
            if not self._account_service.verify_account(account_number):
                print("账户验证失败!")
                return None
            
            # 查询余额
            balance = self._account_service.get_balance(account_number)
            print(f"账户余额: {balance}")
            return balance


    # 测试银行系统
    bank = BankFacade()
    
    # 用户只需要调用简单的接口
    bank.check_balance("123456789", "1234")
    bank.withdraw_cash("123456789", "1234", 200)
    bank.deposit_cash("123456789", "1234", 500)


# 实际应用示例：家庭影院系统
def test_home_theater_facade():
    """测试家庭影院外观模式"""
    print("\n=== 外观模式应用 - 家庭影院系统示例 ===\n")
    
    class Amplifier:
        """功放子系统"""
        
        def on(self):
            print("功放: 开启")
        
        def set_volume(self, level):
            print(f"功放: 设置音量 {level}")
        
        def set_surround_sound(self):
            print("功放: 设置环绕声")
        
        def off(self):
            print("功放: 关闭")


    class DVDPlayer:
        """DVD播放器子系统"""
        
        def on(self):
            print("DVD播放器: 开启")
        
        def play(self, movie):
            print(f"DVD播放器: 播放电影《{movie}》")
        
        def stop(self):
            print("DVD播放器: 停止播放")
        
        def eject(self):
            print("DVD播放器: 弹出光盘")
        
        def off(self):
            print("DVD播放器: 关闭")


    class Projector:
        """投影仪子系统"""
        
        def on(self):
            print("投影仪: 开启")
        
        def wide_screen_mode(self):
            print("投影仪: 设置宽屏模式")
        
        def off(self):
            print("投影仪: 关闭")


    class Lights:
        """灯光子系统"""
        
        def dim(self, level):
            print(f"灯光: 调暗到 {level}%")
        
        def on(self):
            print("灯光: 开启")


    class Screen:
        """屏幕子系统"""
        
        def down(self):
            print("屏幕: 降下")
        
        def up(self):
            print("屏幕: 升起")


    class HomeTheaterFacade:
        """家庭影院外观类"""
        
        def __init__(self):
            self._amp = Amplifier()
            self._dvd = DVDPlayer()
            self._projector = Projector()
            self._lights = Lights()
            self._screen = Screen()
        
        def watch_movie(self, movie):
            """观看电影"""
            print("\n=== 准备观看电影 ===")
            
            self._lights.dim(10)
            self._screen.down()
            self._projector.on()
            self._projector.wide_screen_mode()
            self._amp.on()
            self._amp.set_surround_sound()
            self._amp.set_volume(5)
            self._dvd.on()
            self._dvd.play(movie)
            
            print("电影开始播放!")
        
        def end_movie(self):
            """结束电影"""
            print("\n=== 结束观看电影 ===")
            
            self._dvd.stop()
            self._dvd.eject()
            self._dvd.off()
            self._amp.off()
            self._projector.off()
            self._screen.up()
            self._lights.on()
            
            print("家庭影院系统关闭完成!")


    # 测试家庭影院系统
    home_theater = HomeTheaterFacade()
    
    # 用户只需要调用简单的接口
    home_theater.watch_movie("阿凡达")
    home_theater.end_movie()


if __name__ == "__main__":
    test_computer_facade()
    test_bank_facade()
    test_home_theater_facade()
    
    print("\n=== 外观模式总结 ===")
    print("优点：")
    print("- 对客户屏蔽子系统组件，减少了客户处理的对象数目")
    print("- 实现了子系统与客户之间的松耦合关系")
    print("- 降低了大型软件系统中的编译依赖性")
    print("- 简化了系统在不同平台之间的移植过程")
    print("\n缺点：")
    print("- 不能很好地限制客户使用子系统类")
    print("- 在不引入抽象外观类的情况下，增加新的子系统可能需要修改外观类")
    print("\n适用场景：")
    print("- 要为一个复杂子系统提供一个简单接口时")
    print("- 客户程序与多个子系统之间存在很大的依赖性时")
    print("- 在层次化结构中，可以使用外观模式定义系统中每一层的入口")
