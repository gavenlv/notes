#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第5章：测试驱动开发(TDD) - 示例代码
本文件包含测试驱动开发(TDD)的示例代码，涵盖TDD开发周期、实践技巧、
测试替身、重构等内容。
"""

import unittest
import sys
import os
import time
import uuid
import hashlib
import datetime
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

# ============================================================================
# 实验1：TDD开发周期 - 红绿重构
# ============================================================================

def demo_tdd_cycle():
    """演示TDD开发周期"""
    print("=== 实验1：TDD开发周期 - 红绿重构 ===")
    
    # 步骤1：编写失败的测试 (Red)
    print("\n步骤1：编写失败的测试 (Red)")
    
    # 我们想要实现一个简单的计算器类
    # 首先编写一个测试，这个测试会失败，因为Calculator类还不存在
    
    # 模拟运行测试失败的情况
    try:
        calculator = Calculator()
        result = calculator.add(2, 3)
        assert result == 5
        print("测试通过（不应该发生）")
    except NameError:
        print("测试失败：Calculator类不存在")
    except AttributeError:
        print("测试失败：Calculator类没有add方法")
    
    # 步骤2：编写最少的代码使测试通过 (Green)
    print("\n步骤2：编写最少的代码使测试通过 (Green)")
    
    # 创建最简单的Calculator类，只包含add方法
    class Calculator:
        def add(self, a, b):
            return a + b
    
    # 再次运行测试，现在应该通过
    calculator = Calculator()
    result = calculator.add(2, 3)
    assert result == 5
    print("测试通过：Calculator.add方法正常工作")
    
    # 步骤3：重构代码，保持测试通过 (Refactor)
    print("\n步骤3：重构代码，保持测试通过 (Refactor)")
    
    # 扩展Calculator类，添加更多功能，同时保持原有测试通过
    class Calculator:
        def __init__(self):
            self.history = []
        
        def add(self, a, b):
            result = a + b
            self._record_operation("add", a, b, result)
            return result
        
        def subtract(self, a, b):
            result = a - b
            self._record_operation("subtract", a, b, result)
            return result
        
        def multiply(self, a, b):
            result = a * b
            self._record_operation("multiply", a, b, result)
            return result
        
        def divide(self, a, b):
            if b == 0:
                raise ValueError("除数不能为零")
            result = a / b
            self._record_operation("divide", a, b, result)
            return result
        
        def _record_operation(self, operation, a, b, result):
            self.history.append({
                "operation": operation,
                "operands": (a, b),
                "result": result,
                "timestamp": datetime.datetime.now()
            })
        
        def get_history(self):
            return self.history
    
    # 验证原有测试仍然通过
    calculator = Calculator()
    result = calculator.add(2, 3)
    assert result == 5
    print("重构后测试仍然通过：Calculator.add方法正常工作")
    
    # 验证新功能
    assert calculator.subtract(5, 3) == 2
    assert calculator.multiply(4, 3) == 12
    assert calculator.divide(10, 2) == 5
    print("新功能测试通过：subtract, multiply, divide方法正常工作")
    
    # 验证历史记录功能
    assert len(calculator.get_history()) == 4
    print("历史记录功能正常工作")
    
    return Calculator


# ============================================================================
# 实验2：TDD实践技巧 - 测试命名与结构
# ============================================================================

def demo_test_naming_and_structure():
    """演示测试命名与结构"""
    print("\n=== 实验2：TDD实践技巧 - 测试命名与结构 ===")
    
    # 好的测试命名示例
    print("\n好的测试命名示例:")
    print("1. test_should_return_sum_when_adding_two_positive_numbers")
    print("2. test_should_throw_exception_when_dividing_by_zero")
    print("3. test_user_should_be_able_to_login_with_valid_credentials")
    
    # 不好的测试命名示例
    print("\n不好的测试命名示例:")
    print("1. test_add")
    print("2. test_divide")
    print("3. test_login")
    
    # AAA模式示例
    print("\nAAA模式示例 (Arrange-Act-Assert):")
    
    # Arrange
    calculator = Calculator()
    num1 = 5
    num2 = 7
    expected_result = 12
    
    # Act
    actual_result = calculator.add(num1, num2)
    
    # Assert
    assert actual_result == expected_result
    print(f"测试通过：{num1} + {num2} = {actual_result} (期望: {expected_result})")
    
    return Calculator


# ============================================================================
# 实验3：测试替身 - Mock, Stub, Fake
# ============================================================================

# 定义一些接口和类用于演示测试替身
class EmailService:
    """邮件服务接口"""
    def send_email(self, to, subject, body):
        pass

class UserRepository:
    """用户仓储接口"""
    def find_by_id(self, user_id):
        pass
    
    def save(self, user):
        pass

class User:
    """用户类"""
    def __init__(self, user_id, name, email):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.is_active = False
    
    def activate(self):
        self.is_active = True
    
    def deactivate(self):
        self.is_active = False

class UserService:
    """用户服务类"""
    def __init__(self, user_repository, email_service):
        self.user_repository = user_repository
        self.email_service = email_service
    
    def activate_user(self, user_id):
        user = self.user_repository.find_by_id(user_id)
        if user:
            user.activate()
            self.user_repository.save(user)
            self.email_service.send_email(
                user.email, 
                "账户激活", 
                "您的账户已成功激活"
            )
            return True
        return False

# 测试替身实现
class MockEmailService:
    """模拟邮件服务"""
    def __init__(self):
        self.sent_emails = []
    
    def send_email(self, to, subject, body):
        self.sent_emails.append({
            "to": to,
            "subject": subject,
            "body": body
        })

class StubUserRepository:
    """存根用户仓储"""
    def __init__(self):
        self.users = {
            "user123": User("user123", "John Doe", "john@example.com")
        }
    
    def find_by_id(self, user_id):
        return self.users.get(user_id)
    
    def save(self, user):
        self.users[user.user_id] = user

class FakeUserRepository:
    """假用户仓储"""
    def __init__(self):
        self.users = {}
    
    def find_by_id(self, user_id):
        return self.users.get(user_id)
    
    def save(self, user):
        self.users[user.user_id] = user
    
    def count(self):
        return len(self.users)

def demo_test_doubles():
    """演示测试替身"""
    print("\n=== 实验3：测试替身 - Mock, Stub, Fake ===")
    
    # 使用Mock对象测试UserService
    print("\n使用Mock对象测试UserService:")
    mock_email_service = MockEmailService()
    stub_user_repository = StubUserRepository()
    
    user_service = UserService(stub_user_repository, mock_email_service)
    
    # 激活用户
    result = user_service.activate_user("user123")
    
    # 验证结果
    assert result == True
    assert len(mock_email_service.sent_emails) == 1
    assert mock_email_service.sent_emails[0]["to"] == "john@example.com"
    assert mock_email_service.sent_emails[0]["subject"] == "账户激活"
    
    print("测试通过：用户激活成功，邮件已发送")
    
    # 使用Fake对象测试
    print("\n使用Fake对象测试:")
    fake_user_repository = FakeUserRepository()
    fake_email_service = MockEmailService()
    
    user_service = UserService(fake_user_repository, fake_email_service)
    
    # 添加用户
    user = User("user456", "Jane Smith", "jane@example.com")
    fake_user_repository.save(user)
    
    # 激活用户
    result = user_service.activate_user("user456")
    
    # 验证结果
    assert result == True
    assert fake_user_repository.count() == 1
    assert len(fake_email_service.sent_emails) == 1
    
    print("测试通过：用户激活成功，仓储中用户数量正确")
    
    return user_service


# ============================================================================
# 实验4：TDD实战案例 - 任务管理系统
# ============================================================================

# 任务状态枚举
class TaskStatus(Enum):
    TODO = "待办"
    IN_PROGRESS = "进行中"
    DONE = "已完成"

# 任务优先级枚举
class TaskPriority(Enum):
    LOW = "低"
    MEDIUM = "中"
    HIGH = "高"

# 任务类
class Task:
    def __init__(self, title, description="", priority=TaskPriority.MEDIUM):
        self.id = str(uuid.uuid4())
        self.title = title
        self.description = description
        self.priority = priority
        self.status = TaskStatus.TODO
        self.created_at = datetime.datetime.now()
        self.updated_at = datetime.datetime.now()
        self.due_date = None
    
    def update_title(self, title):
        self.title = title
        self.updated_at = datetime.datetime.now()
    
    def update_description(self, description):
        self.description = description
        self.updated_at = datetime.datetime.now()
    
    def set_priority(self, priority):
        self.priority = priority
        self.updated_at = datetime.datetime.now()
    
    def set_status(self, status):
        self.status = status
        self.updated_at = datetime.datetime.now()
    
    def set_due_date(self, due_date):
        self.due_date = due_date
        self.updated_at = datetime.datetime.now()
    
    def is_overdue(self):
        if self.due_date is None:
            return False
        return datetime.datetime.now() > self.due_date and self.status != TaskStatus.DONE

# 任务仓储接口
class TaskRepository(ABC):
    @abstractmethod
    def save(self, task):
        pass
    
    @abstractmethod
    def find_by_id(self, task_id):
        pass
    
    @abstractmethod
    def find_all(self):
        pass
    
    @abstractmethod
    def delete(self, task_id):
        pass
    
    @abstractmethod
    def find_by_status(self, status):
        pass
    
    @abstractmethod
    def find_by_priority(self, priority):
        pass

# 内存任务仓储实现
class InMemoryTaskRepository(TaskRepository):
    def __init__(self):
        self.tasks = {}
    
    def save(self, task):
        self.tasks[task.id] = task
        return task
    
    def find_by_id(self, task_id):
        return self.tasks.get(task_id)
    
    def find_all(self):
        return list(self.tasks.values())
    
    def delete(self, task_id):
        if task_id in self.tasks:
            del self.tasks[task_id]
            return True
        return False
    
    def find_by_status(self, status):
        return [task for task in self.tasks.values() if task.status == status]
    
    def find_by_priority(self, priority):
        return [task for task in self.tasks.values() if task.priority == priority]

# 任务服务类
class TaskService:
    def __init__(self, task_repository):
        self.task_repository = task_repository
    
    def create_task(self, title, description="", priority=TaskPriority.MEDIUM):
        task = Task(title, description, priority)
        return self.task_repository.save(task)
    
    def get_task(self, task_id):
        return self.task_repository.find_by_id(task_id)
    
    def update_task(self, task_id, title=None, description=None, priority=None, status=None, due_date=None):
        task = self.task_repository.find_by_id(task_id)
        if not task:
            return None
        
        if title is not None:
            task.update_title(title)
        if description is not None:
            task.update_description(description)
        if priority is not None:
            task.set_priority(priority)
        if status is not None:
            task.set_status(status)
        if due_date is not None:
            task.set_due_date(due_date)
        
        return self.task_repository.save(task)
    
    def delete_task(self, task_id):
        return self.task_repository.delete(task_id)
    
    def get_all_tasks(self):
        return self.task_repository.find_all()
    
    def get_tasks_by_status(self, status):
        return self.task_repository.find_by_status(status)
    
    def get_tasks_by_priority(self, priority):
        return self.task_repository.find_by_priority(priority)
    
    def get_overdue_tasks(self):
        return [task for task in self.task_repository.find_all() if task.is_overdue()]

# TDD测试用例
class TaskServiceTest(unittest.TestCase):
    def setUp(self):
        self.task_repository = InMemoryTaskRepository()
        self.task_service = TaskService(self.task_repository)
    
    def test_create_task_should_return_task_with_id(self):
        # Arrange
        title = "学习TDD"
        description = "完成TDD章节的学习"
        priority = TaskPriority.HIGH
        
        # Act
        task = self.task_service.create_task(title, description, priority)
        
        # Assert
        self.assertIsNotNone(task.id)
        self.assertEqual(task.title, title)
        self.assertEqual(task.description, description)
        self.assertEqual(task.priority, priority)
        self.assertEqual(task.status, TaskStatus.TODO)
    
    def test_get_task_should_return_task_with_correct_id(self):
        # Arrange
        task = self.task_service.create_task("测试任务")
        
        # Act
        retrieved_task = self.task_service.get_task(task.id)
        
        # Assert
        self.assertEqual(retrieved_task.id, task.id)
        self.assertEqual(retrieved_task.title, "测试任务")
    
    def test_update_task_should_modify_task_properties(self):
        # Arrange
        task = self.task_service.create_task("原始标题", "原始描述")
        new_title = "更新标题"
        new_description = "更新描述"
        new_status = TaskStatus.IN_PROGRESS
        
        # Act
        updated_task = self.task_service.update_task(
            task.id, 
            title=new_title, 
            description=new_description, 
            status=new_status
        )
        
        # Assert
        self.assertEqual(updated_task.title, new_title)
        self.assertEqual(updated_task.description, new_description)
        self.assertEqual(updated_task.status, new_status)
    
    def test_delete_task_should_remove_task_from_repository(self):
        # Arrange
        task = self.task_service.create_task("待删除任务")
        
        # Act
        result = self.task_service.delete_task(task.id)
        
        # Assert
        self.assertTrue(result)
        self.assertIsNone(self.task_service.get_task(task.id))
    
    def test_get_tasks_by_status_should_return_only_tasks_with_specified_status(self):
        # Arrange
        task1 = self.task_service.create_task("任务1")
        task2 = self.task_service.create_task("任务2")
        task3 = self.task_service.create_task("任务3")
        
        self.task_service.update_task(task1.id, status=TaskStatus.DONE)
        self.task_service.update_task(task2.id, status=TaskStatus.IN_PROGRESS)
        
        # Act
        done_tasks = self.task_service.get_tasks_by_status(TaskStatus.DONE)
        in_progress_tasks = self.task_service.get_tasks_by_status(TaskStatus.IN_PROGRESS)
        todo_tasks = self.task_service.get_tasks_by_status(TaskStatus.TODO)
        
        # Assert
        self.assertEqual(len(done_tasks), 1)
        self.assertEqual(done_tasks[0].id, task1.id)
        
        self.assertEqual(len(in_progress_tasks), 1)
        self.assertEqual(in_progress_tasks[0].id, task2.id)
        
        self.assertEqual(len(todo_tasks), 1)
        self.assertEqual(todo_tasks[0].id, task3.id)
    
    def test_get_overdue_tasks_should_return_only_overdue_tasks(self):
        # Arrange
        task1 = self.task_service.create_task("过期任务")
        task2 = self.task_service.create_task("未过期任务")
        task3 = self.task_service.create_task("已完成过期任务")
        
        # 设置过期时间（昨天）
        yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
        self.task_service.update_task(task1.id, due_date=yesterday)
        self.task_service.update_task(task3.id, due_date=yesterday, status=TaskStatus.DONE)
        
        # 设置未过期时间（明天）
        tomorrow = datetime.datetime.now() + datetime.timedelta(days=1)
        self.task_service.update_task(task2.id, due_date=tomorrow)
        
        # Act
        overdue_tasks = self.task_service.get_overdue_tasks()
        
        # Assert
        self.assertEqual(len(overdue_tasks), 1)
        self.assertEqual(overdue_tasks[0].id, task1.id)

def demo_task_management_system():
    """演示任务管理系统"""
    print("\n=== 实验4：TDD实战案例 - 任务管理系统 ===")
    
    # 创建任务服务
    task_repository = InMemoryTaskRepository()
    task_service = TaskService(task_repository)
    
    # 创建任务
    print("\n创建任务:")
    task1 = task_service.create_task("学习TDD", "完成TDD章节的学习", TaskPriority.HIGH)
    task2 = task_service.create_task("编写测试用例", "为任务管理系统编写测试用例", TaskPriority.MEDIUM)
    task3 = task_service.create_task("代码重构", "重构任务管理系统代码", TaskPriority.LOW)
    
    print(f"已创建任务: {task1.title} (优先级: {task1.priority.value})")
    print(f"已创建任务: {task2.title} (优先级: {task2.priority.value})")
    print(f"已创建任务: {task3.title} (优先级: {task3.priority.value})")
    
    # 更新任务状态
    print("\n更新任务状态:")
    task_service.update_task(task1.id, status=TaskStatus.IN_PROGRESS)
    task_service.update_task(task2.id, status=TaskStatus.DONE)
    
    updated_task1 = task_service.get_task(task1.id)
    updated_task2 = task_service.get_task(task2.id)
    
    print(f"任务 '{updated_task1.title}' 状态更新为: {updated_task1.status.value}")
    print(f"任务 '{updated_task2.title}' 状态更新为: {updated_task2.status.value}")
    
    # 按状态查询任务
    print("\n按状态查询任务:")
    todo_tasks = task_service.get_tasks_by_status(TaskStatus.TODO)
    in_progress_tasks = task_service.get_tasks_by_status(TaskStatus.IN_PROGRESS)
    done_tasks = task_service.get_tasks_by_status(TaskStatus.DONE)
    
    print(f"待办任务数量: {len(todo_tasks)}")
    print(f"进行中任务数量: {len(in_progress_tasks)}")
    print(f"已完成任务数量: {len(done_tasks)}")
    
    # 设置过期任务
    print("\n设置过期任务:")
    yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
    task_service.update_task(task3.id, due_date=yesterday)
    
    # 查询过期任务
    overdue_tasks = task_service.get_overdue_tasks()
    print(f"过期任务数量: {len(overdue_tasks)}")
    if overdue_tasks:
        for task in overdue_tasks:
            print(f"过期任务: {task.title}")
    
    return task_service


# ============================================================================
# 实验5：TDD与BDD对比
# ============================================================================

# BDD风格的行为定义
class UserBehavior:
    def given_a_user_with_email_and_password(self, email, password):
        self.user = User("user123", "John Doe", email)
        self.user.password = password  # 简化实现，实际应该哈希
        return self.user
    
    def when_the_user_attempts_to_login_with(self, email, password):
        self.login_result = self.authenticate(email, password)
        return self.login_result
    
    def then_the_login_should_be_successful(self):
        return self.login_result is True
    
    def then_the_login_should_fail(self):
        return self.login_result is False
    
    def authenticate(self, email, password):
        # 简化的认证逻辑
        if hasattr(self, 'user') and self.user.email == email and self.user.password == password:
            return True
        return False

def demo_tdd_vs_bdd():
    """演示TDD与BDD的区别"""
    print("\n=== 实验5：TDD与BDD对比 ===")
    
    # TDD风格测试
    print("\nTDD风格测试:")
    print("def test_user_authentication_with_valid_credentials():")
    print("    # Arrange")
    print("    user = User('user123', 'John Doe', 'john@example.com')")
    print("    user.set_password('password123')")
    print("    auth_service = AuthService()")
    print("    ")
    print("    # Act")
    print("    result = auth_service.authenticate('john@example.com', 'password123')")
    print("    ")
    print("    # Assert")
    print("    assert result is True")
    
    # BDD风格测试
    print("\nBDD风格测试:")
    print("Feature: User Authentication")
    print("  As a user")
    print("  I want to authenticate with my email and password")
    print("  So that I can access my account")
    print("  ")
    print("  Scenario: Successful login with valid credentials")
    print("    Given a user with email 'john@example.com' and password 'password123'")
    print("    When the user attempts to login with 'john@example.com' and 'password123'")
    print("    Then the login should be successful")
    
    # 实际运行BDD风格测试
    print("\n运行BDD风格测试:")
    behavior = UserBehavior()
    
    # Given
    behavior.given_a_user_with_email_and_password("john@example.com", "password123")
    
    # When
    behavior.when_the_user_attempts_to_login_with("john@example.com", "password123")
    
    # Then
    result = behavior.then_the_login_should_be_successful()
    print(f"测试结果: {'通过' if result else '失败'}")
    
    # 运行失败场景
    print("\n运行失败场景:")
    behavior.when_the_user_attempts_to_login_with("john@example.com", "wrongpassword")
    result = behavior.then_the_login_should_fail()
    print(f"测试结果: {'通过' if result else '失败'}")
    
    return behavior


# ============================================================================
# 主函数：运行所有实验
# ============================================================================

def main():
    """运行所有实验"""
    print("测试驱动开发(TDD) - 示例代码")
    print("=" * 50)
    
    # 运行所有实验
    demo_tdd_cycle()
    demo_test_naming_and_structure()
    demo_test_doubles()
    demo_task_management_system()
    demo_tdd_vs_bdd()
    
    print("\n所有实验已完成！")
    print("\nTDD核心要点:")
    print("1. 先写失败的测试 (Red)")
    print("2. 编写最少的代码使测试通过 (Green)")
    print("3. 重构代码，保持测试通过 (Refactor)")
    print("4. 使用描述性的测试名称")
    print("5. 遵循AAA模式 (Arrange-Act-Assert)")
    print("6. 使用测试替身隔离依赖")
    print("7. 保持测试简单和专注")
    print("8. 定期运行测试")


if __name__ == "__main__":
    main()