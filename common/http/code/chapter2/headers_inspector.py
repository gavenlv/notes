#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
HTTP头部字段检查器
分析HTTP头部字段的使用情况和最佳实践
"""

import requests
import re
from typing import Dict, List, Tuple
from collections import defaultdict


class HeadersInspector:
    """HTTP头部字段检查器"""
    
    def __init__(self):
        """初始化检查器"""
        # 常见的安全头部字段
        self.security_headers = {
            'Content-Security-Policy': '内容安全策略，防止XSS攻击',
            'X-Content-Type-Options': '防止MIME类型嗅探',
            'X-Frame-Options': '防止点击劫持',
            'X-XSS-Protection': '启用浏览器XSS过滤器',
            'Strict-Transport-Security': '强制HTTPS连接',
            'Referrer-Policy': '控制Referer头部',
            'Permissions-Policy': '控制浏览器权限'
        }
        
        # 常见的缓存头部字段
        self.cache_headers = {
            'Cache-Control': '缓存控制指令',
            'Expires': '过期时间',
            'ETag': '实体标签',
            'Last-Modified': '最后修改时间',
            'If-Modified-Since': '条件请求头部',
            'If-None-Match': '条件请求头部'
        }
        
        # 常见的性能相关头部字段
        self.performance_headers = {
            'Content-Encoding': '内容编码方式',
            'Transfer-Encoding': '传输编码方式',
            'Accept-Encoding': '可接受的编码方式',
            'Vary': '缓存变化依据',
            'Link': '资源链接关系'
        }
    
    def inspect_website_headers(self, url: str) -> Dict:
        """
        检查网站的HTTP头部字段
        
        Args:
            url: 网站URL
            
        Returns:
            包含检查结果的字典
        """
        print(f"=== 检查网站头部字段: {url} ===")
        
        try:
            # 发送HEAD请求获取头部信息
            response = requests.head(url, timeout=10)
            headers = response.headers
            
            # 分析结果
            analysis_result = {
                'url': url,
                'status_code': response.status_code,
                'security_headers_found': {},
                'missing_security_headers': [],
                'cache_headers_found': {},
                'performance_headers_found': {},
                'other_headers': {},
                'recommendations': []
            }
            
            # 检查安全头部
            for header, description in self.security_headers.items():
                if header in headers:
                    analysis_result['security_headers_found'][header] = {
                        'value': headers[header],
                        'description': description
                    }
                else:
                    analysis_result['missing_security_headers'].append({
                        'header': header,
                        'description': description
                    })
            
            # 检查缓存头部
            for header, description in self.cache_headers.items():
                if header in headers:
                    analysis_result['cache_headers_found'][header] = {
                        'value': headers[header],
                        'description': description
                    }
            
            # 检查性能相关头部
            for header, description in self.performance_headers.items():
                if header in headers:
                    analysis_result['performance_headers_found'][header] = {
                        'value': headers[header],
                        'description': description
                    }
            
            # 收集其他头部
            known_headers = set()
            known_headers.update(self.security_headers.keys())
            known_headers.update(self.cache_headers.keys())
            known_headers.update(self.performance_headers.keys())
            
            for header, value in headers.items():
                if header not in known_headers:
                    analysis_result['other_headers'][header] = value
            
            # 生成建议
            analysis_result['recommendations'] = self._generate_recommendations(analysis_result)
            
            # 显示结果
            self._display_analysis_result(analysis_result)
            
            return analysis_result
            
        except Exception as e:
            print(f"检查失败: {e}")
            return {}
    
    def _generate_recommendations(self, analysis_result: Dict) -> List[str]:
        """
        根据分析结果生成建议
        
        Args:
            analysis_result: 分析结果
            
        Returns:
            建议列表
        """
        recommendations = []
        
        # 安全建议
        if analysis_result['missing_security_headers']:
            recommendations.append("建议添加以下安全头部字段:")
            for missing in analysis_result['missing_security_headers']:
                recommendations.append(f"  - {missing['header']}: {missing['description']}")
        
        # 缓存建议
        if not analysis_result['cache_headers_found']:
            recommendations.append("建议添加缓存相关头部字段以提高性能")
        
        # 内容编码建议
        if 'Content-Encoding' not in analysis_result['performance_headers_found']:
            recommendations.append("建议启用内容压缩 (gzip/br) 以减少传输大小")
        
        return recommendations
    
    def _display_analysis_result(self, analysis_result: Dict):
        """
        显示分析结果
        
        Args:
            analysis_result: 分析结果
        """
        print(f"状态码: {analysis_result['status_code']}")
        
        # 显示安全头部
        if analysis_result['security_headers_found']:
            print("\n🔒 安全头部字段:")
            for header, info in analysis_result['security_headers_found'].items():
                print(f"  {header}: {info['value']}")
                print(f"    描述: {info['description']}")
        
        # 显示缺失的安全头部
        if analysis_result['missing_security_headers']:
            print("\n⚠️  缺失的安全头部字段:")
            for missing in analysis_result['missing_security_headers']:
                print(f"  {missing['header']}: {missing['description']}")
        
        # 显示缓存头部
        if analysis_result['cache_headers_found']:
            print("\nキャッシング 缓存头部字段:")
            for header, info in analysis_result['cache_headers_found'].items():
                print(f"  {header}: {info['value']}")
                print(f"    描述: {info['description']}")
        
        # 显示性能相关头部
        if analysis_result['performance_headers_found']:
            print("\n⚡ 性能相关头部字段:")
            for header, info in analysis_result['performance_headers_found'].items():
                print(f"  {header}: {info['value']}")
                print(f"    描述: {info['description']}")
        
        # 显示其他头部
        if analysis_result['other_headers']:
            print("\n📄 其他头部字段:")
            for header, value in analysis_result['other_headers'].items():
                print(f"  {header}: {value}")
        
        # 显示建议
        if analysis_result['recommendations']:
            print("\n💡 优化建议:")
            for recommendation in analysis_result['recommendations']:
                print(f"  {recommendation}")
        
        print("=" * 60 + "\n")
    
    def validate_header_format(self, header_name: str, header_value: str) -> Tuple[bool, str]:
        """
        验证HTTP头部字段格式
        
        Args:
            header_name: 头部字段名称
            header_value: 头部字段值
            
        Returns:
            (是否有效, 错误信息)
        """
        # 验证头部名称
        if not re.match(r'^[a-zA-Z0-9\-]+$', header_name):
            return False, f"无效的头部字段名称: {header_name}"
        
        # 验证常见头部字段的值格式
        validation_rules = {
            'Content-Type': r'^[a-zA-Z0-9\-]+/[a-zA-Z0-9\-]+(?:; .*)?$',
            'Content-Length': r'^\d+$',
            'Cache-Control': r'^[a-zA-Z0-9\-,\s=]+$',  # 简化验证
            'Date': r'^[A-Za-z]{3}, \d{2} [A-Za-z]{3} \d{4} \d{2}:\d{2}:\d{2} GMT$'
        }
        
        if header_name in validation_rules:
            pattern = validation_rules[header_name]
            if not re.match(pattern, header_value):
                return False, f"头部字段 {header_name} 的值格式不正确: {header_value}"
        
        return True, ""
    
    def analyze_header_usage(self, urls: List[str]):
        """
        分析多个网站的头部字段使用情况
        
        Args:
            urls: 网站URL列表
        """
        print("=== 头部字段使用情况分析 ===")
        
        # 统计头部字段使用频率
        header_counts = defaultdict(int)
        total_sites = 0
        
        for url in urls:
            try:
                response = requests.head(url, timeout=5)
                for header in response.headers:
                    header_counts[header] += 1
                total_sites += 1
            except:
                print(f"无法访问 {url}")
                continue
        
        # 显示统计结果
        print(f"分析了 {total_sites} 个网站的头部字段使用情况:")
        sorted_headers = sorted(header_counts.items(), key=lambda x: x[1], reverse=True)
        
        for header, count in sorted_headers:
            percentage = (count / total_sites) * 100
            print(f"  {header}: {count}/{total_sites} ({percentage:.1f}%)")
        
        print("=" * 60 + "\n")


def demonstrate_header_inspection():
    """演示头部字段检查"""
    inspector = HeadersInspector()
    
    # 检查几个知名网站
    websites = [
        "https://www.github.com",
        "https://httpbin.org/get",
        "https://www.baidu.com"
    ]
    
    for website in websites:
        inspector.inspect_website_headers(website)


def demonstrate_header_validation():
    """演示头部字段格式验证"""
    inspector = HeadersInspector()
    
    print("=== 头部字段格式验证演示 ===")
    
    # 测试一些头部字段
    test_headers = [
        ('Content-Type', 'application/json'),
        ('Content-Type', 'invalid-type'),  # 无效格式
        ('Content-Length', '1234'),
        ('Content-Length', 'abc'),  # 无效格式
        ('Cache-Control', 'max-age=3600, public'),
        ('Date', 'Mon, 01 Jan 2023 12:00:00 GMT'),
        ('Invalid-Header@Name', 'value')  # 无效名称
    ]
    
    for header_name, header_value in test_headers:
        is_valid, error_msg = inspector.validate_header_format(header_name, header_value)
        status = "✅ 有效" if is_valid else "❌ 无效"
        print(f"{status} {header_name}: {header_value}")
        if error_msg:
            print(f"  错误: {error_msg}")
        print()


def demonstrate_usage_analysis():
    """演示头部字段使用情况分析"""
    inspector = HeadersInspector()
    
    # 分析多个网站的头部使用情况
    test_urls = [
        "https://www.github.com",
        "https://httpbin.org/get",
        "https://www.stackoverflow.com",
        "https://www.python.org",
        "https://httpbin.org/response-headers?Content-Type=text/plain"
    ]
    
    inspector.analyze_header_usage(test_urls)


def main():
    """主函数"""
    print("HTTP头部字段检查器示例")
    print("=" * 60)
    print()
    
    # 演示头部字段检查
    demonstrate_header_inspection()
    
    # 演示头部字段验证
    demonstrate_header_validation()
    
    # 演示使用情况分析
    demonstrate_usage_analysis()
    
    print("所有演示完成!")


if __name__ == "__main__":
    main()