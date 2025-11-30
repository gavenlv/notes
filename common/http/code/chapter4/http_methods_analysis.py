#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
HTTP请求方法分析工具
用于分析HTTP请求方法的特性和使用场景
"""

import requests
from typing import Dict, List, Tuple
from dataclasses import dataclass
from collections import defaultdict
import json


@dataclass
class MethodCharacteristics:
    """HTTP方法特性数据类"""
    method: str
    safe: bool  # 安全性：不会改变服务器状态
    idempotent: bool  # 幂等性：多次执行效果相同
    cacheable: bool  # 可缓存性：响应可以被缓存
    description: str  # 描述
    common_use_cases: List[str]  # 常见使用场景


class HTTPMethodsAnalyzer:
    """HTTP请求方法分析器"""
    
    def __init__(self):
        """初始化分析器"""
        self.methods_data = self._initialize_methods_data()
    
    def _initialize_methods_data(self) -> Dict[str, MethodCharacteristics]:
        """初始化HTTP方法特性数据"""
        return {
            "GET": MethodCharacteristics(
                method="GET",
                safe=True,
                idempotent=True,
                cacheable=True,
                description="请求指定的资源，不应产生任何副作用",
                common_use_cases=[
                    "获取网页内容",
                    "检索API数据",
                    "图片、CSS、JS等静态资源加载",
                    "搜索引擎爬虫抓取内容"
                ]
            ),
            "POST": MethodCharacteristics(
                method="POST",
                safe=False,
                idempotent=False,
                cacheable=False,
                description="向指定资源提交数据进行处理请求（例如提交表单或者上传文件）",
                common_use_cases=[
                    "提交表单数据",
                    "创建新资源",
                    "文件上传",
                    "API中的复杂操作"
                ]
            ),
            "PUT": MethodCharacteristics(
                method="PUT",
                safe=False,
                idempotent=True,
                cacheable=False,
                description="向指定资源位置上传其最新状态，通常用于更新整个资源",
                common_use_cases=[
                    "更新完整资源",
                    "创建或替换资源（指定ID）",
                    "API中的资源更新操作"
                ]
            ),
            "DELETE": MethodCharacteristics(
                method="DELETE",
                safe=False,
                idempotent=True,
                cacheable=False,
                description="请求服务器删除指定的资源",
                common_use_cases=[
                    "删除用户账户",
                    "移除资源",
                    "清理临时数据"
                ]
            ),
            "PATCH": MethodCharacteristics(
                method="PATCH",
                safe=False,
                idempotent=False,  # 通常不是幂等的，但可以设计成幂等的
                cacheable=False,
                description="对资源进行部分修改",
                common_use_cases=[
                    "更新资源的部分属性",
                    "增量更新",
                    "API中的局部修改操作"
                ]
            ),
            "HEAD": MethodCharacteristics(
                method="HEAD",
                safe=True,
                idempotent=True,
                cacheable=True,
                description="类似于GET请求，但服务器只返回状态行和头部，不返回响应体",
                common_use_cases=[
                    "检查资源是否存在",
                    "获取资源元信息",
                    "验证缓存有效性",
                    "检查文件大小而不下载"
                ]
            ),
            "OPTIONS": MethodCharacteristics(
                method="OPTIONS",
                safe=True,
                idempotent=True,
                cacheable=False,
                description="返回服务器针对特定资源所支持的通信选项",
                common_use_cases=[
                    "CORS预检请求",
                    "发现API支持的方法",
                    "调试和测试"
                ]
            ),
            "TRACE": MethodCharacteristics(
                method="TRACE",
                safe=True,
                idempotent=True,
                cacheable=False,
                description="回显服务器收到的请求，主要用于测试或诊断",
                common_use_cases=[
                    "调试HTTP连接",
                    "检测代理行为",
                    "网络问题排查"
                ]
            ),
            "CONNECT": MethodCharacteristics(
                method="CONNECT",
                safe=False,
                idempotent=False,
                cacheable=False,
                description="建立到目标资源的隧道，通常用于SSL/TLS加密的HTTPS连接",
                common_use_cases=[
                    "HTTPS代理连接",
                    "建立TCP隧道"
                ]
            )
        }
    
    def get_method_characteristics(self, method: str) -> MethodCharacteristics:
        """
        获取指定HTTP方法的特性
        
        Args:
            method: HTTP方法名
            
        Returns:
            MethodCharacteristics: 方法特性对象
        """
        return self.methods_data.get(method.upper(), None)
    
    def compare_methods(self, methods: List[str]) -> Dict[str, Dict[str, str]]:
        """
        比较多个HTTP方法的特性
        
        Args:
            methods: HTTP方法列表
            
        Returns:
            包含各方法特性的字典
        """
        comparison = {}
        for method in methods:
            char = self.get_method_characteristics(method)
            if char:
                comparison[method] = {
                    "安全性": "✓" if char.safe else "✗",
                    "幂等性": "✓" if char.idempotent else "✗",
                    "可缓存": "✓" if char.cacheable else "✗",
                    "描述": char.description
                }
        return comparison
    
    def get_restful_recommendations(self) -> Dict[str, str]:
        """
        获取RESTful API设计推荐
        
        Returns:
            RESTful设计推荐字典
        """
        return {
            "资源获取": "使用GET方法获取资源表示",
            "资源创建": "使用POST方法创建新资源",
            "资源更新": "使用PUT更新整个资源，PATCH更新部分资源",
            "资源删除": "使用DELETE方法删除资源",
            "资源查询": "使用GET方法配合查询参数进行过滤、排序、分页",
            "安全性考虑": "敏感操作避免使用GET方法，防止数据泄露在URL中",
            "幂等性保证": "确保PUT和DELETE操作的幂等性",
            "状态码使用": "正确使用HTTP状态码表示操作结果"
        }
    
    def analyze_method_usage_patterns(self) -> Dict[str, List[str]]:
        """
        分析HTTP方法使用模式
        
        Returns:
            使用模式分析结果
        """
        patterns = {
            "读取操作": ["GET", "HEAD"],
            "写入操作": ["POST", "PUT", "PATCH", "DELETE"],
            "元信息操作": ["HEAD", "OPTIONS"],
            "调试诊断": ["TRACE"],
            "连接建立": ["CONNECT"]
        }
        return patterns
    
    def generate_best_practices(self) -> List[str]:
        """
        生成HTTP方法使用最佳实践
        
        Returns:
            最佳实践列表
        """
        return [
            "1. 遵循HTTP方法的语义，不要滥用",
            "2. GET请求不应改变服务器状态",
            "3. POST用于创建资源或执行非幂等操作",
            "4. PUT用于更新完整资源，具有幂等性",
            "5. PATCH用于部分更新资源",
            "6. DELETE用于删除资源，具有幂等性",
            "7. HEAD用于获取资源元信息，不传输响应体",
            "8. OPTIONS用于发现资源支持的操作",
            "9. 正确使用HTTP状态码表示操作结果",
            "10. 在RESTful API设计中遵循统一接口约束"
        ]


class HTTPMethodsTester:
    """HTTP方法测试器"""
    
    def __init__(self, base_url: str = "https://httpbin.org"):
        """
        初始化测试器
        
        Args:
            base_url: 测试服务器URL
        """
        self.base_url = base_url.rstrip('/')
    
    def test_get_method(self) -> Dict[str, any]:
        """测试GET方法"""
        try:
            response = requests.get(f"{self.base_url}/get", params={"key": "value"})
            return {
                "success": True,
                "method": "GET",
                "status_code": response.status_code,
                "response_time": response.elapsed.total_seconds(),
                "safe": True,
                "idempotent": True
            }
        except Exception as e:
            return {
                "success": False,
                "method": "GET",
                "error": str(e)
            }
    
    def test_post_method(self) -> Dict[str, any]:
        """测试POST方法"""
        try:
            data = {"name": "test", "value": 123}
            response = requests.post(f"{self.base_url}/post", json=data)
            return {
                "success": True,
                "method": "POST",
                "status_code": response.status_code,
                "response_time": response.elapsed.total_seconds(),
                "safe": False,
                "idempotent": False
            }
        except Exception as e:
            return {
                "success": False,
                "method": "POST",
                "error": str(e)
            }
    
    def test_put_method(self) -> Dict[str, any]:
        """测试PUT方法"""
        try:
            data = {"name": "updated", "value": 456}
            response = requests.put(f"{self.base_url}/put", json=data)
            return {
                "success": True,
                "method": "PUT",
                "status_code": response.status_code,
                "response_time": response.elapsed.total_seconds(),
                "safe": False,
                "idempotent": True
            }
        except Exception as e:
            return {
                "success": False,
                "method": "PUT",
                "error": str(e)
            }
    
    def test_delete_method(self) -> Dict[str, any]:
        """测试DELETE方法"""
        try:
            response = requests.delete(f"{self.base_url}/delete")
            return {
                "success": True,
                "method": "DELETE",
                "status_code": response.status_code,
                "response_time": response.elapsed.total_seconds(),
                "safe": False,
                "idempotent": True
            }
        except Exception as e:
            return {
                "success": False,
                "method": "DELETE",
                "error": str(e)
            }
    
    def run_all_tests(self) -> List[Dict[str, any]]:
        """
        运行所有HTTP方法测试
        
        Returns:
            测试结果列表
        """
        tests = [
            self.test_get_method,
            self.test_post_method,
            self.test_put_method,
            self.test_delete_method
        ]
        
        results = []
        for test in tests:
            result = test()
            results.append(result)
            print(f"测试 {result['method']} 方法: {'成功' if result['success'] else '失败'}")
            if not result['success']:
                print(f"  错误: {result.get('error', '未知错误')}")
        
        return results


def demonstrate_analyzer():
    """演示HTTP方法分析器的使用"""
    print("HTTP请求方法分析工具演示")
    print("=" * 50)
    
    # 创建分析器实例
    analyzer = HTTPMethodsAnalyzer()
    
    # 1. 显示单个方法特性
    print("\n1. GET方法特性分析")
    print("-" * 30)
    get_char = analyzer.get_method_characteristics("GET")
    if get_char:
        print(f"方法: {get_char.method}")
        print(f"安全性: {'是' if get_char.safe else '否'}")
        print(f"幂等性: {'是' if get_char.idempotent else '否'}")
        print(f"可缓存: {'是' if get_char.cacheable else '否'}")
        print(f"描述: {get_char.description}")
        print("常见使用场景:")
        for i, use_case in enumerate(get_char.common_use_cases, 1):
            print(f"  {i}. {use_case}")
    
    # 2. 比较多个方法特性
    print("\n2. HTTP方法特性对比")
    print("-" * 30)
    methods_to_compare = ["GET", "POST", "PUT", "DELETE"]
    comparison = analyzer.compare_methods(methods_to_compare)
    
    # 打印表格形式的对比结果
    print(f"{'方法':<8} {'安全性':<6} {'幂等性':<6} {'可缓存':<6} {'描述'}")
    print("-" * 80)
    for method, chars in comparison.items():
        print(f"{method:<8} {chars['安全性']:<6} {chars['幂等性']:<6} {chars['可缓存']:<6} {chars['描述']}")
    
    # 3. RESTful设计推荐
    print("\n3. RESTful API设计推荐")
    print("-" * 30)
    recommendations = analyzer.get_restful_recommendations()
    for title, recommendation in recommendations.items():
        print(f"{title}: {recommendation}")
    
    # 4. 使用模式分析
    print("\n4. HTTP方法使用模式分析")
    print("-" * 30)
    patterns = analyzer.analyze_method_usage_patterns()
    for category, methods in patterns.items():
        print(f"{category}: {', '.join(methods)}")
    
    # 5. 最佳实践
    print("\n5. HTTP方法使用最佳实践")
    print("-" * 30)
    best_practices = analyzer.generate_best_practices()
    for practice in best_practices:
        print(practice)


def demonstrate_tester():
    """演示HTTP方法测试器的使用"""
    print("\n\nHTTP方法测试器演示")
    print("=" * 50)
    
    # 创建测试器实例
    tester = HTTPMethodsTester()
    
    # 运行所有测试
    print("运行HTTP方法测试...")
    results = tester.run_all_tests()
    
    # 显示测试结果汇总
    print("\n测试结果汇总:")
    print("-" * 50)
    successful_tests = [r for r in results if r['success']]
    failed_tests = [r for r in results if not r['success']]
    
    print(f"成功测试: {len(successful_tests)} 个")
    print(f"失败测试: {len(failed_tests)} 个")
    
    if successful_tests:
        print("\n详细结果:")
        for result in successful_tests:
            print(f"  {result['method']}: "
                  f"状态码 {result['status_code']}, "
                  f"耗时 {result['response_time']:.3f}s, "
                  f"安全性: {'是' if result['safe'] else '否'}, "
                  f"幂等性: {'是' if result['idempotent'] else '否'}")


def main():
    """主函数"""
    demonstrate_analyzer()
    demonstrate_tester()


if __name__ == '__main__':
    main()