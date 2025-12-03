"""
第20章：状态模式 (State Pattern)

状态模式是一种行为设计模式，它允许一个对象在其内部状态改变时改变它的行为，
使对象看起来似乎修改了它的类。
"""

from abc import ABC, abstractmethod
from typing import Optional


class State(ABC):
    """状态接口"""
    
    @abstractmethod
    def handle(self, context) -> None:
        """处理方法"""
        pass


class Context:
    """上下文类"""
    
    def __init__(self, state: State):
        self._state = state
    
    def set_state(self, state: State) -> None:
        """设置状态"""
        print(f"状态变化: {self._state.__class__.__name__} -> {state.__class__.__name__}")
        self._state = state
    
    def request(self) -> None:
        """请求处理"""
        self._state.handle(self)


# 示例1：电梯状态系统
class ElevatorState(State):
    """电梯状态基类"""
    
    def handle(self, elevator) -> None:
        pass


class StoppedState(ElevatorState):
    """停止状态"""
    
    def handle(self, elevator) -> None:
        print("电梯已停止，可以开门")
        elevator.open_doors()


class MovingUpState(ElevatorState):
    """上升状态"""
    
    def handle(self, elevator) -> None:
        print("电梯正在上升，无法开门")
        elevator.move_to_floor()


class MovingDownState(ElevatorState):
    """下降状态"""
    
    def handle(self, elevator) -> None:
        print("电梯正在下降，无法开门")
        elevator.move_to_floor()


class DoorOpenState(ElevatorState):
    """门开状态"""
    
    def handle(self, elevator) -> None:
        print("电梯门已打开，可以上下乘客")
        elevator.close_doors()


class DoorClosedState(ElevatorState):
    """门关状态"""
    
    def handle(self, elevator) -> None:
        print("电梯门已关闭，可以移动")


class Elevator:
    """电梯类"""
    
    def __init__(self):
        self._current_floor = 1
        self._target_floor = 1
        self._state: ElevatorState = StoppedState()
    
    def set_state(self, state: ElevatorState) -> None:
        """设置状态"""
        self._state = state
    
    def call_elevator(self, floor: int) -> None:
        """呼叫电梯"""
        print(f"呼叫电梯到 {floor} 层")
        self._target_floor = floor
        
        if self._current_floor < floor:
            self.set_state(MovingUpState())
        elif self._current_floor > floor:
            self.set_state(MovingDownState())
        else:
            self.set_state(StoppedState())
        
        self._state.handle(self)
    
    def open_doors(self) -> None:
        """开门"""
        self.set_state(DoorOpenState())
        print("电梯门已打开")
    
    def close_doors(self) -> None:
        """关门"""
        self.set_state(DoorClosedState())
        print("电梯门已关闭")
    
    def move_to_floor(self) -> None:
        """移动到目标楼层"""
        if isinstance(self._state, MovingUpState):
            self._current_floor += 1
            print(f"电梯上升到 {self._current_floor} 层")
        elif isinstance(self._state, MovingDownState):
            self._current_floor -= 1
            print(f"电梯下降到 {self._current_floor} 层")
        
        if self._current_floor == self._target_floor:
            self.set_state(StoppedState())
            print(f"电梯已到达 {self._current_floor} 层")


# 示例2：TCP连接状态
class TCPState(State):
    """TCP状态基类"""
    
    def handle(self, connection) -> None:
        pass


class TCPClosedState(TCPState):
    """关闭状态"""
    
    def handle(self, connection) -> None:
        print("TCP连接已关闭")


class TCPListenState(TCPState):
    """监听状态"""
    
    def handle(self, connection) -> None:
        print("TCP正在监听连接")


class TCPSynSentState(TCPState):
    """SYN发送状态"""
    
    def handle(self, connection) -> None:
        print("TCP已发送SYN包，等待SYN-ACK")


class TCPSynReceivedState(TCPState):
    """SYN接收状态"""
    
    def handle(self, connection) -> None:
        print("TCP已收到SYN包，发送SYN-ACK")


class TCPEstablishedState(TCPState):
    """已建立状态"""
    
    def handle(self, connection) -> None:
        print("TCP连接已建立，可以传输数据")


class TCPConnection:
    """TCP连接类"""
    
    def __init__(self):
        self._state: TCPState = TCPClosedState()
    
    def set_state(self, state: TCPState) -> None:
        """设置状态"""
        self._state = state
    
    def active_open(self) -> None:
        """主动打开连接"""
        print("主动打开TCP连接")
        self.set_state(TCPSynSentState())
        self._state.handle(self)
    
    def passive_open(self) -> None:
        """被动打开连接"""
        print("被动打开TCP连接")
        self.set_state(TCPListenState())
        self._state.handle(self)
    
    def send_syn(self) -> None:
        """发送SYN包"""
        print("发送SYN包")
        self.set_state(TCPSynSentState())
        self._state.handle(self)
    
    def receive_syn(self) -> None:
        """接收SYN包"""
        print("接收SYN包")
        self.set_state(TCPSynReceivedState())
        self._state.handle(self)
    
    def receive_syn_ack(self) -> None:
        """接收SYN-ACK包"""
        print("接收SYN-ACK包")
        self.set_state(TCPEstablishedState())
        self._state.handle(self)
    
    def send_ack(self) -> None:
        """发送ACK包"""
        print("发送ACK包")
        self.set_state(TCPEstablishedState())
        self._state.handle(self)
    
    def close(self) -> None:
        """关闭连接"""
        print("关闭TCP连接")
        self.set_state(TCPClosedState())
        self._state.handle(self)


# 示例3：工作流状态管理
class WorkflowState(State):
    """工作流状态基类"""
    
    def handle(self, workflow) -> None:
        pass


class DraftState(WorkflowState):
    """草稿状态"""
    
    def handle(self, workflow) -> None:
        print("文档处于草稿状态，可以编辑")


class ReviewState(WorkflowState):
    """审核状态"""
    
    def handle(self, workflow) -> None:
        print("文档处于审核状态，等待审核意见")


class ApprovedState(WorkflowState):
    """已批准状态"""
    
    def handle(self, workflow) -> None:
        print("文档已批准，可以发布")


class PublishedState(WorkflowState):
    """已发布状态"""
    
    def handle(self, workflow) -> None:
        print("文档已发布，不可修改")


class ArchivedState(WorkflowState):
    """已归档状态"""
    
    def handle(self, workflow) -> None:
        print("文档已归档，只读")


class DocumentWorkflow:
    """文档工作流类"""
    
    def __init__(self, title: str):
        self.title = title
        self._state: WorkflowState = DraftState()
        self._content = ""
    
    def set_state(self, state: WorkflowState) -> None:
        """设置状态"""
        self._state = state
    
    def edit_content(self, content: str) -> None:
        """编辑内容"""
        if isinstance(self._state, DraftState):
            self._content = content
            print(f"文档内容已更新: {content[:50]}...")
        else:
            print("当前状态不允许编辑")
    
    def submit_for_review(self) -> None:
        """提交审核"""
        if isinstance(self._state, DraftState):
            self.set_state(ReviewState())
            print("文档已提交审核")
        else:
            print("当前状态不允许提交审核")
    
    def approve(self) -> None:
        """批准文档"""
        if isinstance(self._state, ReviewState):
            self.set_state(ApprovedState())
            print("文档已批准")
        else:
            print("当前状态不允许批准")
    
    def publish(self) -> None:
        """发布文档"""
        if isinstance(self._state, ApprovedState):
            self.set_state(PublishedState())
            print("文档已发布")
        else:
            print("当前状态不允许发布")
    
    def archive(self) -> None:
        """归档文档"""
        if isinstance(self._state, PublishedState):
            self.set_state(ArchivedState())
            print("文档已归档")
        else:
            print("当前状态不允许归档")
    
    def get_status(self) -> None:
        """获取状态"""
        self._state.handle(self)


# 示例4：游戏角色状态
class CharacterState(State):
    """角色状态基类"""
    
    def handle(self, character) -> None:
        pass


class NormalState(CharacterState):
    """正常状态"""
    
    def handle(self, character) -> None:
        print(f"{character.name} 处于正常状态")


class PoisonedState(CharacterState):
    """中毒状态"""
    
    def handle(self, character) -> None:
        character.health -= 5
        print(f"{character.name} 中毒了，生命值-5，当前生命值: {character.health}")


class ParalyzedState(CharacterState):
    """麻痹状态"""
    
    def handle(self, character) -> None:
        print(f"{character.name} 被麻痹了，无法行动")


class BerserkState(CharacterState):
    """狂暴状态"""
    
    def handle(self, character) -> None:
        character.attack_power *= 1.5
        print(f"{character.name} 进入狂暴状态，攻击力提升50%")


class GameCharacter:
    """游戏角色类"""
    
    def __init__(self, name: str):
        self.name = name
        self.health = 100
        self.attack_power = 10
        self._state: CharacterState = NormalState()
    
    def set_state(self, state: CharacterState) -> None:
        """设置状态"""
        self._state = state
    
    def attack(self) -> None:
        """攻击"""
        if not isinstance(self._state, ParalyzedState):
            print(f"{self.name} 发动攻击，伤害: {self.attack_power}")
        else:
            print(f"{self.name} 被麻痹，无法攻击")
    
    def take_damage(self, damage: int) -> None:
        """受到伤害"""
        self.health = max(0, self.health - damage)
        print(f"{self.name} 受到 {damage} 点伤害，剩余生命值: {self.health}")
    
    def apply_status(self, status: str) -> None:
        """应用状态效果"""
        if status == "poison":
            self.set_state(PoisonedState())
        elif status == "paralyze":
            self.set_state(ParalyzedState())
        elif status == "berserk":
            self.set_state(BerserkState())
        elif status == "normal":
            self.set_state(NormalState())
    
    def update(self) -> None:
        """更新状态效果"""
        self._state.handle(self)


def test_elevator():
    """测试电梯状态系统"""
    print("=== 测试电梯状态系统 ===")
    
    elevator = Elevator()
    
    # 呼叫电梯到3层
    elevator.call_elevator(3)
    
    # 模拟移动过程
    for _ in range(2):
        elevator.move_to_floor()
    
    # 开门
    elevator.open_doors()
    
    # 关门
    elevator.close_doors()
    
    # 呼叫到1层
    elevator.call_elevator(1)
    
    # 模拟移动过程
    for _ in range(2):
        elevator.move_to_floor()


def test_tcp_connection():
    """测试TCP连接状态"""
    print("\n=== 测试TCP连接状态 ===")
    
    # 客户端连接过程
    client = TCPConnection()
    client.active_open()
    client.receive_syn_ack()
    client.send_ack()
    client.close()
    
    print()
    
    # 服务器端连接过程
    server = TCPConnection()
    server.passive_open()
    server.receive_syn()
    server.send_ack()
    server.close()


def test_workflow():
    """测试工作流状态"""
    print("\n=== 测试工作流状态 ===")
    
    document = DocumentWorkflow("项目计划书")
    
    # 正常流程
    document.edit_content("这是项目计划书的内容...")
    document.get_status()
    
    document.submit_for_review()
    document.get_status()
    
    document.approve()
    document.get_status()
    
    document.publish()
    document.get_status()
    
    document.archive()
    document.get_status()
    
    # 尝试在错误状态下操作
    print("\n尝试在归档状态下编辑:")
    document.edit_content("新内容")


def test_game_character():
    """测试游戏角色状态"""
    print("\n=== 测试游戏角色状态 ===")
    
    character = GameCharacter("勇士")
    
    # 正常状态
    character.update()
    character.attack()
    
    # 中毒状态
    character.apply_status("poison")
    for _ in range(3):
        character.update()
    
    # 麻痹状态
    character.apply_status("paralyze")
    character.attack()
    character.update()
    
    # 狂暴状态
    character.apply_status("berserk")
    character.update()
    character.attack()
    
    # 恢复正常
    character.apply_status("normal")
    character.update()
    character.attack()


if __name__ == "__main__":
    # 运行所有测试
    test_elevator()
    test_tcp_connection()
    test_workflow()
    test_game_character()
    
    print("\n=== 状态模式测试完成 ===")
    print("\n状态模式总结：")
    print("1. 对象行为随状态改变而改变")
    print("2. 消除大量的条件判断语句")
    print("3. 状态转换逻辑清晰")
    print("4. 符合开闭原则")
    print("5. 适用于状态驱动的系统")