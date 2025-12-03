"""
第22章：模板方法模式 (Template Method Pattern)

模板方法模式是一种行为设计模式，它在父类中定义了一个算法的框架，
允许子类在不改变算法结构的情况下重定义算法的某些特定步骤。
"""

from abc import ABC, abstractmethod
from datetime import datetime


class DataProcessor(ABC):
    """数据处理器抽象类（模板类）"""
    
    def process_data(self, data: list) -> list:
        """模板方法：定义数据处理流程"""
        print("=== 开始数据处理流程 ===")
        
        # 步骤1：验证数据
        validated_data = self._validate_data(data)
        
        # 步骤2：清理数据
        cleaned_data = self._clean_data(validated_data)
        
        # 步骤3：转换数据
        transformed_data = self._transform_data(cleaned_data)
        
        # 步骤4：保存数据
        saved_data = self._save_data(transformed_data)
        
        # 步骤5：生成报告
        self._generate_report(saved_data)
        
        print("=== 数据处理完成 ===")
        return saved_data
    
    def _validate_data(self, data: list) -> list:
        """验证数据（具体步骤，子类可重写）"""
        print("验证数据中...")
        return [item for item in data if item is not None]
    
    @abstractmethod
    def _clean_data(self, data: list) -> list:
        """清理数据（抽象方法，子类必须实现）"""
        pass
    
    @abstractmethod
    def _transform_data(self, data: list) -> list:
        """转换数据（抽象方法，子类必须实现）"""
        pass
    
    def _save_data(self, data: list) -> list:
        """保存数据（具体步骤，子类可重写）"""
        print(f"保存 {len(data)} 条数据")
        return data
    
    def _generate_report(self, data: list) -> None:
        """生成报告（钩子方法，子类可选择重写）"""
        print(f"生成报告：处理了 {len(data)} 条数据")


class CSVDataProcessor(DataProcessor):
    """CSV数据处理器"""
    
    def _clean_data(self, data: list) -> list:
        """清理CSV数据"""
        print("清理CSV数据：去除空行和无效字符")
        cleaned = []
        for item in data:
            if isinstance(item, str) and item.strip():
                cleaned.append(item.strip())
        return cleaned
    
    def _transform_data(self, data: list) -> list:
        """转换CSV数据"""
        print("转换CSV数据：解析字段和格式化")
        transformed = []
        for item in data:
            if isinstance(item, str):
                # 简单的CSV解析
                fields = item.split(',')
                transformed.append({
                    'raw': item,
                    'fields': fields,
                    'field_count': len(fields)
                })
        return transformed
    
    def _save_data(self, data: list) -> list:
        """保存CSV数据"""
        print("保存CSV数据到文件")
        return data


class JSONDataProcessor(DataProcessor):
    """JSON数据处理器"""
    
    def _clean_data(self, data: list) -> list:
        """清理JSON数据"""
        print("清理JSON数据：验证JSON格式")
        import json
        cleaned = []
        for item in data:
            try:
                if isinstance(item, str):
                    json.loads(item)  # 验证JSON格式
                    cleaned.append(item)
            except json.JSONDecodeError:
                continue
        return cleaned
    
    def _transform_data(self, data: list) -> list:
        """转换JSON数据"""
        print("转换JSON数据：解析为Python对象")
        import json
        transformed = []
        for item in data:
            try:
                parsed = json.loads(item)
                transformed.append({
                    'original': item,
                    'parsed': parsed,
                    'type': type(parsed).__name__
                })
            except json.JSONDecodeError:
                continue
        return transformed
    
    def _generate_report(self, data: list) -> None:
        """生成JSON处理报告"""
        super()._generate_report(data)
        if data:
            types = [item['type'] for item in data]
            type_counts = {}
            for t in types:
                type_counts[t] = type_counts.get(t, 0) + 1
            print("数据类型统计:", type_counts)


class XMLDataProcessor(DataProcessor):
    """XML数据处理器"""
    
    def _validate_data(self, data: list) -> list:
        """验证XML数据"""
        print("验证XML数据：检查XML声明和标签")
        validated = []
        for item in data:
            if isinstance(item, str) and item.strip().startswith('<?xml'):
                validated.append(item)
        return validated
    
    def _clean_data(self, data: list) -> list:
        """清理XML数据"""
        print("清理XML数据：去除无效标签和属性")
        import re
        cleaned = []
        for item in data:
            # 简单的XML清理
            cleaned_item = re.sub(r'<\w+\s+[^>]*>', lambda m: m.group().split()[0] + '>', item)
            cleaned.append(cleaned_item)
        return cleaned
    
    def _transform_data(self, data: list) -> list:
        """转换XML数据"""
        print("转换XML数据：解析为结构化数据")
        transformed = []
        for item in data:
            # 简单的XML解析
            import re
            tags = re.findall(r'<(\w+)>([^<]*)</\1>', item)
            transformed.append({
                'xml': item,
                'tags': dict(tags),
                'tag_count': len(tags)
            })
        return transformed


# 示例2：饮料制作模板
class BeverageMaker(ABC):
    """饮料制作器抽象类"""
    
    def make_beverage(self) -> None:
        """模板方法：饮料制作流程"""
        print("=== 开始制作饮料 ===")
        
        self._boil_water()
        self._brew()
        self._pour_in_cup()
        
        if self._customer_wants_condiments():
            self._add_condiments()
        
        self._serve()
        print("=== 饮料制作完成 ===")
    
    def _boil_water(self) -> None:
        """烧水（具体步骤）"""
        print("烧开水中...")
    
    @abstractmethod
    def _brew(self) -> None:
        """冲泡（抽象方法）"""
        pass
    
    def _pour_in_cup(self) -> None:
        """倒入杯子（具体步骤）"""
        print("倒入杯中...")
    
    @abstractmethod
    def _add_condiments(self) -> None:
        """添加调料（抽象方法）"""
        pass
    
    def _customer_wants_condiments(self) -> bool:
        """顾客是否需要调料（钩子方法）"""
        return True
    
    def _serve(self) -> None:
        """上饮料（具体步骤）"""
        print("上饮料...")


class CoffeeMaker(BeverageMaker):
    """咖啡制作器"""
    
    def _brew(self) -> None:
        """冲泡咖啡"""
        print("冲泡咖啡粉...")
    
    def _add_condiments(self) -> None:
        """添加咖啡调料"""
        print("加入糖和牛奶...")
    
    def _customer_wants_condiments(self) -> bool:
        """询问顾客是否需要调料"""
        # 在实际应用中，这里可以询问顾客
        answer = input("是否需要糖和牛奶？(y/n): ").lower()
        return answer == 'y' or answer == 'yes'


class TeaMaker(BeverageMaker):
    """茶制作器"""
    
    def _brew(self) -> None:
        """泡茶"""
        print("浸泡茶叶...")
    
    def _add_condiments(self) -> None:
        """添加茶调料"""
        print("加入柠檬...")


class HotChocolateMaker(BeverageMaker):
    """热巧克力制作器"""
    
    def _brew(self) -> None:
        """冲泡热巧克力"""
        print("融化巧克力粉...")
    
    def _add_condiments(self) -> None:
        """添加热巧克力调料"""
        print("加入棉花糖...")


# 示例3：游戏角色创建模板
class CharacterCreator(ABC):
    """角色创建器抽象类"""
    
    def create_character(self, name: str) -> dict:
        """模板方法：角色创建流程"""
        print(f"=== 开始创建角色: {name} ===")
        
        character = {}
        character['name'] = name
        character['created_at'] = datetime.now()
        
        # 创建流程
        self._select_race(character)
        self._select_class(character)
        self._assign_attributes(character)
        self._select_skills(character)
        self._equip_starting_gear(character)
        
        if self._needs_background_story():
            self._write_background_story(character)
        
        self._finalize_character(character)
        
        print(f"=== 角色创建完成 ===")
        return character
    
    @abstractmethod
    def _select_race(self, character: dict) -> None:
        """选择种族（抽象方法）"""
        pass
    
    @abstractmethod
    def _select_class(self, character: dict) -> None:
        """选择职业（抽象方法）"""
        pass
    
    def _assign_attributes(self, character: dict) -> None:
        """分配属性（具体步骤）"""
        print("分配基础属性...")
        character['attributes'] = {
            'strength': 10,
            'dexterity': 10,
            'intelligence': 10,
            'wisdom': 10,
            'charisma': 10
        }
    
    @abstractmethod
    def _select_skills(self, character: dict) -> None:
        """选择技能（抽象方法）"""
        pass
    
    def _equip_starting_gear(self, character: dict) -> None:
        """装备起始装备（具体步骤）"""
        print("装备起始装备...")
        character['equipment'] = ['背包', '火把', '口粮']
    
    def _needs_background_story(self) -> bool:
        """是否需要背景故事（钩子方法）"""
        return True
    
    def _write_background_story(self, character: dict) -> None:
        """编写背景故事（具体步骤）"""
        print("编写背景故事...")
        character['background'] = f"{character['name']}的冒险故事从这里开始..."
    
    def _finalize_character(self, character: dict) -> None:
        """最终确认角色（具体步骤）"""
        print("最终确认角色...")
        character['status'] = 'active'


class WarriorCreator(CharacterCreator):
    """战士角色创建器"""
    
    def _select_race(self, character: dict) -> None:
        """选择战士种族"""
        print("选择人类种族（适合战士）")
        character['race'] = '人类'
    
    def _select_class(self, character: dict) -> None:
        """选择战士职业"""
        print("选择战士职业")
        character['class'] = '战士'
    
    def _select_skills(self, character: dict) -> None:
        """选择战士技能"""
        print("选择战士技能：剑术、盾牌、重甲")
        character['skills'] = ['剑术', '盾牌', '重甲']
    
    def _equip_starting_gear(self, character: dict) -> None:
        """装备战士起始装备"""
        super()._equip_starting_gear(character)
        character['equipment'].extend(['长剑', '盾牌', '锁甲'])


class MageCreator(CharacterCreator):
    """法师角色创建器"""
    
    def _select_race(self, character: dict) -> None:
        """选择法师种族"""
        print("选择精灵种族（适合法师）")
        character['race'] = '精灵'
    
    def _select_class(self, character: dict) -> None:
        """选择法师职业"""
        print("选择法师职业")
        character['class'] = '法师'
    
    def _select_skills(self, character: dict) -> None:
        """选择法师技能"""
        print("选择法师技能：火球术、冰冻术、传送")
        character['skills'] = ['火球术', '冰冻术', '传送']
    
    def _equip_starting_gear(self, character: dict) -> None:
        """装备法师起始装备"""
        super()._equip_starting_gear(character)
        character['equipment'].extend(['法杖', '魔法书', '长袍'])


class RogueCreator(CharacterCreator):
    """盗贼角色创建器"""
    
    def _select_race(self, character: dict) -> None:
        """选择盗贼种族"""
        print("选择矮人种族（适合盗贼）")
        character['race'] = '矮人'
    
    def _select_class(self, character: dict) -> None:
        """选择盗贼职业"""
        print("选择盗贼职业")
        character['class'] = '盗贼'
    
    def _select_skills(self, character: dict) -> None:
        """选择盗贼技能"""
        print("选择盗贼技能：潜行、开锁、偷窃")
        character['skills'] = ['潜行', '开锁', '偷窃']
    
    def _needs_background_story(self) -> bool:
        """盗贼不需要背景故事"""
        return False


def test_data_processors():
    """测试数据处理器"""
    print("=== 测试数据处理器 ===")
    
    # 测试CSV数据处理器
    csv_data = [
        "name,age,city",
        "Alice,25,Beijing",
        "Bob,30,Shanghai",
        "  Charlie,35,Guangzhou  ",
        None,
        ""
    ]
    
    csv_processor = CSVDataProcessor()
    result = csv_processor.process_data(csv_data)
    print(f"CSV处理结果: {len(result)} 条记录")
    
    print("\n" + "="*50 + "\n")
    
    # 测试JSON数据处理器
    json_data = [
        '{"name": "Alice", "age": 25}',
        '{"name": "Bob", "age": 30}',
        'invalid json',
        '{"city": "Beijing"}'
    ]
    
    json_processor = JSONDataProcessor()
    result = json_processor.process_data(json_data)
    print(f"JSON处理结果: {len(result)} 条记录")


def test_beverage_makers():
    """测试饮料制作器"""
    print("\n=== 测试饮料制作器 ===")
    
    # 测试咖啡制作
    print("\n1. 制作咖啡:")
    coffee_maker = CoffeeMaker()
    coffee_maker.make_beverage()
    
    print("\n2. 制作茶:")
    tea_maker = TeaMaker()
    tea_maker.make_beverage()
    
    print("\n3. 制作热巧克力:")
    chocolate_maker = HotChocolateMaker()
    chocolate_maker.make_beverage()


def test_character_creators():
    """测试角色创建器"""
    print("\n=== 测试角色创建器 ===")
    
    # 测试战士创建
    print("\n1. 创建战士角色:")
    warrior_creator = WarriorCreator()
    warrior = warrior_creator.create_character("阿瑞斯")
    print(f"战士角色: {warrior}")
    
    print("\n2. 创建法师角色:")
    mage_creator = MageCreator()
    mage = mage_creator.create_character("梅林")
    print(f"法师角色: {mage}")
    
    print("\n3. 创建盗贼角色:")
    rogue_creator = RogueCreator()
    rogue = rogue_creator.create_character("影子")
    print(f"盗贼角色: {rogue}")


if __name__ == "__main__":
    # 运行所有测试
    test_data_processors()
    test_beverage_makers()
    test_character_creators()
    
    print("\n=== 模板方法模式测试完成 ===")
    print("\n模板方法模式总结：")
    print("1. 定义算法框架，子类实现具体步骤")
    print("2. 避免代码重复，提高复用性")
    print("3. 通过钩子方法提供灵活性")
    print("4. 符合开闭原则")
    print("5. 适用于具有固定流程的场景")