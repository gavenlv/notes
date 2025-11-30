#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
缓存验证演示
展示缓存验证机制的工作原理和实现方式
"""

import requests
import time
import hashlib
from datetime import datetime, timedelta
import threading
from flask import Flask, request, make_response, jsonify
import json


# Flask应用用于模拟服务器端
server_app = Flask(__name__)

# 模拟资源数据
resources = {
    'news': {
        'title': '最新新闻',
        'content': '这里是今天的最新新闻内容...',
        'updated_at': datetime.now().isoformat()
    },
    'weather': {
        'location': '北京',
        'temperature': 25,
        'condition': '晴朗',
        'updated_at': datetime.now().isoformat()
    }
}

# 存储ETags
etags = {}


@server_app.route('/')
def server_home():
    """服务器首页"""
    html = '''
    <h1>缓存验证服务器</h1>
    <p>可用端点:</p>
    <ul>
        <li><a href="/api/news">/api/news</a> - 新闻API</li>
        <li><a href="/api/weather">/api/weather</a> - 天气API</li>
        <li>/api/resource/&lt;resource_id&gt; - 通用资源API</li>
    </ul>
    '''
    return html


@server_app.route('/api/<resource_id>')
def get_resource(resource_id):
    """获取资源"""
    if resource_id not in resources:
        return jsonify({'error': 'Resource not found'}), 404
    
    resource = resources[resource_id]
    
    # 生成ETag
    content_str = json.dumps(resource, sort_keys=True)
    etag = hashlib.md5(content_str.encode()).hexdigest()
    etags[resource_id] = etag
    
    # 设置Last-Modified
    last_modified = datetime.now()
    
    # 检查条件请求头部
    if_none_match = request.headers.get('If-None-Match')
    if_modified_since = request.headers.get('If-Modified-Since')
    
    # 处理If-None-Match
    if if_none_match and if_none_match == f'"{etag}"':
        response = make_response('', 304)
        response.headers['ETag'] = f'"{etag}"'
        response.headers['Last-Modified'] = last_modified.strftime('%a, %d %b %Y %H:%M:%S GMT')
        response.headers['Cache-Control'] = 'max-age=60'
        return response
    
    # 处理If-Modified-Since
    if if_modified_since:
        try:
            if_modified_dt = datetime.strptime(if_modified_since, '%a, %d %b %Y %H:%M:%S GMT')
            if last_modified <= if_modified_dt:
                response = make_response('', 304)
                response.headers['ETag'] = f'"{etag}"'
                response.headers['Last-Modified'] = last_modified.strftime('%a, %d %b %Y %H:%M:%S GMT')
                response.headers['Cache-Control'] = 'max-age=60'
                return response
        except ValueError:
            pass
    
    # 返回完整响应
    response = jsonify(resource)
    response.headers['ETag'] = f'"{etag}"'
    response.headers['Last-Modified'] = last_modified.strftime('%a, %d %b %Y %H:%M:%S GMT')
    response.headers['Cache-Control'] = 'max-age=60'
    
    return response


@server_app.route('/api/update/<resource_id>', methods=['POST'])
def update_resource(resource_id):
    """更新资源"""
    if resource_id in resources:
        resources[resource_id]['updated_at'] = datetime.now().isoformat()
        # 清除旧的ETag
        if resource_id in etags:
            del etags[resource_id]
        return jsonify({'message': f'Resource {resource_id} updated'})
    return jsonify({'error': 'Resource not found'}), 404


class CacheValidator:
    """缓存验证器"""
    
    def __init__(self, base_url='http://localhost:5001'):
        self.base_url = base_url
        self.cache = {}  # 简单内存缓存
        self.etags = {}  # 存储ETags
    
    def fetch_resource(self, resource_id, use_cache=True):
        """
        获取资源，支持缓存验证
        
        Args:
            resource_id (str): 资源ID
            use_cache (bool): 是否使用缓存
            
        Returns:
            dict: 资源数据或错误信息
        """
        url = f'{self.base_url}/api/{resource_id}'
        
        # 如果使用缓存且缓存中有数据
        if use_cache and resource_id in self.cache:
            cached_data = self.cache[resource_id]
            
            # 准备条件请求头部
            headers = {}
            if resource_id in self.etags:
                headers['If-None-Match'] = f'"{self.etags[resource_id]}"'
            if 'last_modified' in cached_data:
                headers['If-Modified-Since'] = cached_data['last_modified']
            
            print(f"发送条件请求到 {url}")
            response = requests.get(url, headers=headers)
            
            if response.status_code == 304:
                print("缓存有效，使用本地缓存数据")
                return cached_data['data']
            elif response.status_code == 200:
                print("缓存已过期，获取新数据")
                data = response.json()
                # 更新缓存
                self._update_cache(resource_id, data, response)
                return data
            else:
                print(f"请求失败，状态码: {response.status_code}")
                return {'error': f'HTTP {response.status_code}'}
        else:
            # 首次请求或不使用缓存
            print(f"首次请求 {url}")
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                # 更新缓存
                self._update_cache(resource_id, data, response)
                return data
            else:
                print(f"请求失败，状态码: {response.status_code}")
                return {'error': f'HTTP {response.status_code}'}
    
    def _update_cache(self, resource_id, data, response):
        """
        更新缓存
        
        Args:
            resource_id (str): 资源ID
            data (dict): 资源数据
            response (requests.Response): HTTP响应对象
        """
        # 存储ETag
        etag = response.headers.get('ETag')
        if etag:
            # 移除引号
            self.etags[resource_id] = etag.strip('"')
        
        # 存储Last-Modified
        last_modified = response.headers.get('Last-Modified')
        
        # 更新缓存
        self.cache[resource_id] = {
            'data': data,
            'etag': etag,
            'last_modified': last_modified,
            'timestamp': time.time()
        }
    
    def get_cache_info(self, resource_id):
        """
        获取缓存信息
        
        Args:
            resource_id (str): 资源ID
            
        Returns:
            dict: 缓存信息
        """
        if resource_id in self.cache:
            cache_entry = self.cache[resource_id]
            age = time.time() - cache_entry['timestamp']
            return {
                'cached': True,
                'age_seconds': int(age),
                'etag': cache_entry.get('etag'),
                'last_modified': cache_entry.get('last_modified')
            }
        return {'cached': False}
    
    def clear_cache(self, resource_id=None):
        """
        清除缓存
        
        Args:
            resource_id (str, optional): 特定资源ID，如果为None则清除所有缓存
        """
        if resource_id:
            if resource_id in self.cache:
                del self.cache[resource_id]
            if resource_id in self.etags:
                del self.etags[resource_id]
            print(f"已清除资源 {resource_id} 的缓存")
        else:
            self.cache.clear()
            self.etags.clear()
            print("已清除所有缓存")


def demonstrate_cache_validation():
    """演示缓存验证过程"""
    print("缓存验证演示")
    print("=" * 30)
    
    # 创建缓存验证器
    validator = CacheValidator()
    
    print("1. 首次请求资源 (应该返回完整数据)")
    news_data = validator.fetch_resource('news')
    print(f"新闻数据: {json.dumps(news_data, indent=2, ensure_ascii=False)}")
    print(f"缓存信息: {validator.get_cache_info('news')}")
    
    print("\n2. 第二次请求相同资源 (应该使用缓存)")
    news_data_cached = validator.fetch_resource('news')
    print(f"新闻数据: {json.dumps(news_data_cached, indent=2, ensure_ascii=False)}")
    print(f"缓存信息: {validator.get_cache_info('news')}")
    
    print("\n3. 等待一段时间后再次请求 (模拟缓存过期)")
    time.sleep(2)
    news_data_refresh = validator.fetch_resource('news')
    print(f"新闻数据: {json.dumps(news_data_refresh, indent=2, ensure_ascii=False)}")
    
    print("\n4. 模拟服务器端资源更新")
    # 这里我们手动触发服务器端资源更新
    resources['news']['updated_at'] = datetime.now().isoformat()
    print("服务器端新闻资源已更新")
    
    print("\n5. 再次请求资源 (应该获取新数据)")
    news_data_updated = validator.fetch_resource('news')
    print(f"新闻数据: {json.dumps(news_data_updated, indent=2, ensure_ascii=False)}")
    print(f"缓存信息: {validator.get_cache_info('news')}")
    
    print("\n6. 测试天气资源")
    weather_data = validator.fetch_resource('weather')
    print(f"天气数据: {json.dumps(weather_data, indent=2, ensure_ascii=False)}")
    print(f"缓存信息: {validator.get_cache_info('weather')}")
    
    print("\n缓存验证优势:")
    print("- 减少网络传输量")
    print("- 降低服务器负载")
    print("- 提高响应速度")
    print("- 保持数据新鲜度")


def start_server():
    """启动服务器"""
    print("启动缓存验证演示服务器...")
    print("服务器地址: http://localhost:5001")
    server_app.run(host='localhost', port=5001, debug=False, use_reloader=False)


def run_demo():
    """运行完整演示"""
    # 启动服务器线程
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # 等待服务器启动
    time.sleep(2)
    
    # 运行演示
    demonstrate_cache_validation()


if __name__ == '__main__':
    run_demo()