#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
HTTP头部案例研究
分析真实网站的HTTP头部设置并提供改进建议
"""

import requests
import json
from urllib.parse import urlparse
from typing import Dict, List, Optional
import argparse
import re


class HttpHeadersCaseStudy:
    """HTTP头部分析案例研究"""
    
    def __init__(self, url: str, timeout: int = 10):
        """
        初始化案例研究分析器
        
        Args:
            url: 要分析的URL
            timeout: 请求超时时间（秒）
        """
        self.url = url
        self.timeout = timeout
        self.response = None
        self.headers = {}
        self.analysis_results = {}
    
    def fetch_data(self) -> bool:
        """
        获取网站数据
        
        Returns:
            是否成功获取数据
        """
        try:
            # 尝试多种请求方法
            methods = ['HEAD', 'GET']
            for method in methods:
                try:
                    if method == 'HEAD':
                        self.response = requests.head(
                            self.url, 
                            timeout=self.timeout, 
                            allow_redirects=True,
                            headers={'User-Agent': 'HttpHeadersCaseStudy/1.0'}
                        )
                    else:
                        self.response = requests.get(
                            self.url, 
                            timeout=self.timeout, 
                            allow_redirects=True,
                            headers={'User-Agent': 'HttpHeadersCaseStudy/1.0'}
                        )
                    
                    self.headers = self.response.headers
                    return True
                except requests.exceptions.RequestException:
                    continue
            
            return False
        except Exception as e:
            print(f"获取数据失败: {e}")
            return False
    
    def analyze_security_headers(self) -> Dict[str, any]:
        """
        分析安全头部
        
        Returns:
            安全头部分析结果
        """
        if not self.headers:
            return {}
        
        findings = {
            'issues': [],
            'recommendations': [],
            'score': 0,
            'max_score': 10
        }
        
        # 检查关键安全头部
        security_headers = {
            'Strict-Transport-Security': {
                'required': True,
                'check_function': self._check_hsts,
                'weight': 2
            },
            'X-Content-Type-Options': {
                'required': True,
                'check_function': self._check_x_content_type_options,
                'weight': 1
            },
            'X-Frame-Options': {
                'required': True,
                'check_function': self._check_x_frame_options,
                'weight': 1
            },
            'Content-Security-Policy': {
                'required': True,
                'check_function': self._check_csp,
                'weight': 3
            },
            'X-XSS-Protection': {
                'required': False,
                'check_function': self._check_xss_protection,
                'weight': 1
            },
            'Referrer-Policy': {
                'required': True,
                'check_function': self._check_referrer_policy,
                'weight': 1
            },
            'Permissions-Policy': {
                'required': False,
                'check_function': self._check_permissions_policy,
                'weight': 1
            }
        }
        
        for header, config in security_headers.items():
            value = self.headers.get(header)
            check_result = config['check_function'](value)
            
            if check_result['valid']:
                findings['score'] += config['weight']
            else:
                if config['required'] or value is not None:
                    findings['issues'].append({
                        'header': header,
                        'value': value,
                        'issue': check_result['issue']
                    })
                    findings['recommendations'].append({
                        'header': header,
                        'recommendation': check_result['recommendation']
                    })
        
        return findings
    
    def _check_hsts(self, value: Optional[str]) -> Dict[str, any]:
        """检查HSTS头部"""
        if not value:
            return {
                'valid': False,
                'issue': '未设置HSTS头部',
                'recommendation': '对于HTTPS站点，应设置Strict-Transport-Security头部，建议值: max-age=31536000; includeSubDomains; preload'
            }
        
        # 检查HSTS值是否符合要求
        if 'max-age' not in value:
            return {
                'valid': False,
                'issue': 'HSTS缺少max-age指令',
                'recommendation': 'HSTS必须包含max-age指令，建议至少设置为31536000秒（1年）'
            }
        
        # 检查max-age值
        max_age_match = re.search(r'max-age=(\d+)', value)
        if max_age_match:
            max_age = int(max_age_match.group(1))
            if max_age < 31536000:  # 1年
                return {
                    'valid': False,
                    'issue': f'HSTS max-age值({max_age})小于推荐值(31536000)',
                    'recommendation': '建议将HSTS max-age设置为至少31536000秒（1年）'
                }
        
        return {'valid': True}
    
    def _check_x_content_type_options(self, value: Optional[str]) -> Dict[str, any]:
        """检查X-Content-Type-Options头部"""
        if not value:
            return {
                'valid': False,
                'issue': '未设置X-Content-Type-Options头部',
                'recommendation': '应设置X-Content-Type-Options: nosniff以防止MIME类型嗅探'
            }
        
        if value.lower() != 'nosniff':
            return {
                'valid': False,
                'issue': f'X-Content-Type-Options值({value})不正确',
                'recommendation': 'X-Content-Type-Options应设置为nosniff'
            }
        
        return {'valid': True}
    
    def _check_x_frame_options(self, value: Optional[str]) -> Dict[str, any]:
        """检查X-Frame-Options头部"""
        if not value:
            return {
                'valid': False,
                'issue': '未设置X-Frame-Options头部',
                'recommendation': '应设置X-Frame-Options以防止点击劫持，推荐值: SAMEORIGIN或DENY'
            }
        
        valid_values = ['DENY', 'SAMEORIGIN']
        if value.upper() not in valid_values:
            return {
                'valid': False,
                'issue': f'X-Frame-Options值({value})不在推荐范围内',
                'recommendation': f'X-Frame-Options应设置为{valid_values}之一'
            }
        
        return {'valid': True}
    
    def _check_csp(self, value: Optional[str]) -> Dict[str, any]:
        """检查Content-Security-Policy头部"""
        if not value:
            return {
                'valid': False,
                'issue': '未设置Content-Security-Policy头部',
                'recommendation': '应设置Content-Security-Policy以防止XSS等攻击'
            }
        
        # 基本检查：是否包含关键指令
        required_directives = ['default-src', 'script-src']
        missing_directives = []
        for directive in required_directives:
            if directive not in value:
                missing_directives.append(directive)
        
        if missing_directives:
            return {
                'valid': False,
                'issue': f'CSP缺少关键指令: {missing_directives}',
                'recommendation': f'CSP应包含{required_directives}等关键指令以限制资源加载'
            }
        
        return {'valid': True}
    
    def _check_xss_protection(self, value: Optional[str]) -> Dict[str, any]:
        """检查X-XSS-Protection头部"""
        # 注意：现代浏览器已逐渐弃用此头部，推荐使用CSP
        if value:
            if value != '1; mode=block':
                return {
                    'valid': False,
                    'issue': f'X-XSS-Protection值({value})不是推荐值',
                    'recommendation': '如果使用X-XSS-Protection，应设置为1; mode=block，但更推荐使用CSP'
                }
        
        return {'valid': True}
    
    def _check_referrer_policy(self, value: Optional[str]) -> Dict[str, any]:
        """检查Referrer-Policy头部"""
        if not value:
            return {
                'valid': False,
                'issue': '未设置Referrer-Policy头部',
                'recommendation': '应设置Referrer-Policy以控制Referer头部的发送，推荐值: no-referrer-when-downgrade'
            }
        
        recommended_values = [
            'no-referrer',
            'no-referrer-when-downgrade',
            'same-origin',
            'strict-origin',
            'strict-origin-when-cross-origin'
        ]
        
        if value not in recommended_values:
            return {
                'valid': False,
                'issue': f'Referrer-Policy值({value})不在推荐范围内',
                'recommendation': f'Referrer-Policy应设置为{recommended_values}之一'
            }
        
        return {'valid': True}
    
    def _check_permissions_policy(self, value: Optional[str]) -> Dict[str, any]:
        """检查Permissions-Policy头部"""
        # 这是一个较新的头部，不是必需的但推荐
        if not value:
            return {
                'valid': True  # 不是必需的
            }
        
        return {'valid': True}
    
    def analyze_cache_headers(self) -> Dict[str, any]:
        """
        分析缓存头部
        
        Returns:
            缓存头部分析结果
        """
        if not self.headers:
            return {}
        
        findings = {
            'issues': [],
            'recommendations': [],
            'score': 0,
            'max_score': 5
        }
        
        cache_control = self.headers.get('Cache-Control', '')
        expires = self.headers.get('Expires')
        etag = self.headers.get('ETag')
        last_modified = self.headers.get('Last-Modified')
        
        # 检查Cache-Control
        if cache_control:
            findings['score'] += 1
            
            # 检查是否有冲突的指令
            directives = [d.strip().lower() for d in cache_control.split(',')]
            if 'no-cache' in directives and 'public' in directives:
                findings['issues'].append({
                    'header': 'Cache-Control',
                    'value': cache_control,
                    'issue': '同时设置了no-cache和public，可能存在冲突'
                })
                findings['recommendations'].append({
                    'header': 'Cache-Control',
                    'recommendation': '避免同时使用冲突的缓存指令'
                })
            elif 'no-store' in directives and ('public' in directives or 'private' in directives):
                findings['issues'].append({
                    'header': 'Cache-Control',
                    'value': cache_control,
                    'issue': '同时设置了no-store和其他缓存可见性指令，存在冲突'
                })
                findings['recommendations'].append({
                    'header': 'Cache-Control',
                    'recommendation': 'no-store与其他缓存可见性指令不应同时使用'
                })
        else:
            findings['issues'].append({
                'header': 'Cache-Control',
                'value': None,
                'issue': '未设置Cache-Control头部'
            })
            findings['recommendations'].append({
                'header': 'Cache-Control',
                'recommendation': '应设置Cache-Control头部来控制缓存行为'
            })
        
        # 检查ETag或Last-Modified
        if etag or last_modified:
            findings['score'] += 2
        else:
            findings['issues'].append({
                'header': 'ETag/Last-Modified',
                'value': None,
                'issue': '未设置ETag或Last-Modified头部'
            })
            findings['recommendations'].append({
                'header': 'ETag/Last-Modified',
                'recommendation': '应设置ETag或Last-Modified以支持条件请求'
            })
        
        # 检查Expires（与Cache-Control配合使用）
        if expires:
            findings['score'] += 1
        else:
            # Expires不是必需的，如果有Cache-Control就不扣分
            if not cache_control:
                findings['issues'].append({
                    'header': 'Expires',
                    'value': None,
                    'issue': '未设置Expires头部且没有Cache-Control'
                })
                findings['recommendations'].append({
                    'header': 'Expires',
                    'recommendation': '应设置Expires头部或使用Cache-Control'
                })
        
        # 检查Pragma（主要用于向后兼容）
        pragma = self.headers.get('Pragma')
        if pragma:
            if pragma.lower() != 'no-cache':
                findings['issues'].append({
                    'header': 'Pragma',
                    'value': pragma,
                    'issue': 'Pragma值不是no-cache'
                })
                findings['recommendations'].append({
                    'header': 'Pragma',
                    'recommendation': 'Pragma主要用于HTTP/1.0向后兼容，应设置为no-cache'
                })
            else:
                findings['score'] += 1
        elif not cache_control:
            findings['issues'].append({
                'header': 'Pragma',
                'value': None,
                'issue': '未设置Pragma头部且没有Cache-Control'
            })
            findings['recommendations'].append({
                'header': 'Pragma',
                'recommendation': '对于HTTP/1.0兼容性，可考虑设置Pragma: no-cache'
            })
        
        return findings
    
    def analyze_content_headers(self) -> Dict[str, any]:
        """
        分析内容头部
        
        Returns:
            内容头部分析结果
        """
        if not self.headers:
            return {}
        
        findings = {
            'issues': [],
            'recommendations': [],
            'score': 0,
            'max_score': 3
        }
        
        content_type = self.headers.get('Content-Type')
        content_encoding = self.headers.get('Content-Encoding')
        content_length = self.headers.get('Content-Length')
        
        # 检查Content-Type
        if content_type:
            findings['score'] += 1
            
            # 检查是否包含字符集信息
            if 'charset' not in content_type.lower():
                findings['issues'].append({
                    'header': 'Content-Type',
                    'value': content_type,
                    'issue': 'Content-Type未指定字符集'
                })
                findings['recommendations'].append({
                    'header': 'Content-Type',
                    'recommendation': 'Content-Type应指定字符集，如text/html; charset=utf-8'
                })
        else:
            findings['issues'].append({
                'header': 'Content-Type',
                'value': None,
                'issue': '未设置Content-Type头部'
            })
            findings['recommendations'].append({
                'header': 'Content-Type',
                'recommendation': '必须设置Content-Type头部指定内容类型'
            })
        
        # 检查Content-Encoding（如果有压缩）
        if content_encoding:
            findings['score'] += 1
            valid_encodings = ['gzip', 'deflate', 'br']
            if content_encoding.lower() not in valid_encodings:
                findings['issues'].append({
                    'header': 'Content-Encoding',
                    'value': content_encoding,
                    'issue': f'Content-Encoding值({content_encoding})不在常见范围内'
                })
                findings['recommendations'].append({
                    'header': 'Content-Encoding',
                    'recommendation': f'Content-Encoding应为{valid_encodings}之一'
                })
        # Content-Encoding不是必需的，如果没有压缩就不扣分
        
        # 检查Content-Length
        if content_length:
            findings['score'] += 1
        # Content-Length不是必需的，特别是在使用分块传输编码时
        
        return findings
    
    def analyze_performance_headers(self) -> Dict[str, any]:
        """
        分析性能相关头部
        
        Returns:
            性能头部分析结果
        """
        if not self.headers:
            return {}
        
        findings = {
            'issues': [],
            'recommendations': [],
            'score': 0,
            'max_score': 3
        }
        
        # 检查是否启用了压缩
        content_encoding = self.headers.get('Content-Encoding')
        if content_encoding:
            findings['score'] += 1
        else:
            findings['recommendations'].append({
                'header': 'Content-Encoding',
                'recommendation': '考虑启用Gzip或Brotli压缩以减少传输大小'
            })
        
        # 检查Early Hints支持（通过Alt-Svc头部）
        alt_svc = self.headers.get('Alt-Svc')
        if alt_svc:
            findings['score'] += 1
        # 不是必需的
        
        # 检查是否使用了CDN相关头部
        cdn_headers = [
            'CF-Cache-Status',  # Cloudflare
            'X-Cache',  # 通用CDN
            'X-Via',  # 某些CDN
            'Via'  # 标准代理头部
        ]
        
        cdn_used = any(header in self.headers for header in cdn_headers)
        if cdn_used:
            findings['score'] += 1
        else:
            findings['recommendations'].append({
                'header': 'CDN',
                'recommendation': '考虑使用CDN加速静态资源分发'
            })
        
        return findings
    
    def generate_comprehensive_report(self) -> Dict[str, any]:
        """
        生成综合分析报告
        
        Returns:
            综合分析报告
        """
        if not self.fetch_data():
            return {"error": "无法获取网站数据"}
        
        # 执行各项分析
        security_analysis = self.analyze_security_headers()
        cache_analysis = self.analyze_cache_headers()
        content_analysis = self.analyze_content_headers()
        performance_analysis = self.analyze_performance_headers()
        
        # 计算总分
        total_score = (
            security_analysis['score'] +
            cache_analysis['score'] +
            content_analysis['score'] +
            performance_analysis['score']
        )
        
        max_score = (
            security_analysis['max_score'] +
            cache_analysis['max_score'] +
            content_analysis['max_score'] +
            performance_analysis['max_score']
        )
        
        overall_rating = (total_score / max_score * 100) if max_score > 0 else 0
        
        # 确定评级等级
        if overall_rating >= 90:
            rating_level = "优秀"
        elif overall_rating >= 75:
            rating_level = "良好"
        elif overall_rating >= 60:
            rating_level = "一般"
        else:
            rating_level = "需要改进"
        
        return {
            "url": self.url,
            "status_code": self.response.status_code if self.response else None,
            "overall_score": round(overall_rating, 1),
            "rating_level": rating_level,
            "max_score": max_score,
            "categories": {
                "security": security_analysis,
                "cache": cache_analysis,
                "content": content_analysis,
                "performance": performance_analysis
            },
            "summary": {
                "total_issues": sum(len(cat['issues']) for cat in [
                    security_analysis, cache_analysis, content_analysis, performance_analysis
                ]),
                "total_recommendations": sum(len(cat['recommendations']) for cat in [
                    security_analysis, cache_analysis, content_analysis, performance_analysis
                ])
            }
        }
    
    def print_detailed_report(self):
        """打印详细分析报告"""
        report = self.generate_comprehensive_report()
        
        if "error" in report:
            print(f"分析失败: {report['error']}")
            return
        
        print(f"HTTP头部分析报告 - {report['url']}")
        print("=" * 60)
        print(f"状态码: {report['status_code']}")
        print(f"总体评分: {report['overall_score']}/100 ({report['rating_level']})")
        print()
        
        # 安全性分析
        security = report['categories']['security']
        print("安全性分析:")
        print(f"  得分: {security['score']}/{security['max_score']}")
        if security['issues']:
            print("  发现的问题:")
            for issue in security['issues']:
                print(f"    • {issue['header']}: {issue['issue']}")
        if security['recommendations']:
            print("  改进建议:")
            for rec in security['recommendations']:
                print(f"    • {rec['header']}: {rec['recommendation']}")
        print()
        
        # 缓存分析
        cache = report['categories']['cache']
        print("缓存分析:")
        print(f"  得分: {cache['score']}/{cache['max_score']}")
        if cache['issues']:
            print("  发现的问题:")
            for issue in cache['issues']:
                print(f"    • {issue['header']}: {issue['issue']}")
        if cache['recommendations']:
            print("  改进建议:")
            for rec in cache['recommendations']:
                print(f"    • {rec['header']}: {rec['recommendation']}")
        print()
        
        # 内容分析
        content = report['categories']['content']
        print("内容分析:")
        print(f"  得分: {content['score']}/{content['max_score']}")
        if content['issues']:
            print("  发现的问题:")
            for issue in content['issues']:
                print(f"    • {issue['header']}: {issue['issue']}")
        if content['recommendations']:
            print("  改进建议:")
            for rec in content['recommendations']:
                print(f"    • {rec['header']}: {rec['recommendation']}")
        print()
        
        # 性能分析
        performance = report['categories']['performance']
        print("性能分析:")
        print(f"  得分: {performance['score']}/{performance['max_score']}")
        if performance['recommendations']:
            print("  改进建议:")
            for rec in performance['recommendations']:
                print(f"    • {rec['header']}: {rec['recommendation']}")
        print()
        
        # 总结
        summary = report['summary']
        print("总结:")
        print(f"  总共发现 {summary['total_issues']} 个问题")
        print(f"  提供 {summary['total_recommendations']} 个改进建议")


def compare_websites(urls: List[str]):
    """
    比较多个网站的HTTP头部
    
    Args:
        urls: 要比较的网站URL列表
    """
    print("网站HTTP头部对比分析")
    print("=" * 60)
    
    results = []
    for url in urls:
        print(f"\n分析网站: {url}")
        analyzer = HttpHeadersCaseStudy(url)
        report = analyzer.generate_comprehensive_report()
        if "error" not in report:
            results.append(report)
        else:
            print(f"  分析失败: {report['error']}")
    
    if not results:
        print("没有成功分析任何网站")
        return
    
    # 按评分排序
    results.sort(key=lambda x: x['overall_score'], reverse=True)
    
    print("\n网站排名:")
    print("-" * 40)
    for i, report in enumerate(results, 1):
        print(f"{i}. {report['url']}")
        print(f"   评分: {report['overall_score']}/100 ({report['rating_level']})")
        print(f"   状态码: {report['status_code']}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='HTTP头部分析案例研究')
    parser.add_argument('url', nargs='?', help='要分析的URL')
    parser.add_argument('--compare', nargs='+', help='比较多个网站的HTTP头部')
    parser.add_argument('--timeout', type=int, default=10, help='请求超时时间（秒）')
    
    args = parser.parse_args()
    
    if args.compare:
        # 比较多个网站
        compare_websites(args.compare)
    elif args.url:
        # 分析单个网站
        url = args.url
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        print(f"开始分析: {url}")
        analyzer = HttpHeadersCaseStudy(url, args.timeout)
        analyzer.print_detailed_report()
    else:
        # 默认示例
        print("HTTP头部分析案例研究")
        print("=" * 50)
        print("使用方法:")
        print("  python http_headers_case_study.py example.com")
        print("  python http_headers_case_study.py --compare site1.com site2.com site3.com")
        
        # 提供一些知名网站作为示例
        example_sites = [
            "https://www.google.com",
            "https://www.github.com",
            "https://stackoverflow.com"
        ]
        
        print(f"\n示例分析网站:")
        for site in example_sites:
            print(f"  {site}")


if __name__ == '__main__':
    main()