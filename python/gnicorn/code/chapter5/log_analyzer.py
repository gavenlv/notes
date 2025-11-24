# log_analyzer.py
# 用于分析Gunicorn日志的工具

import re
import json
from collections import defaultdict, deque
import datetime
import argparse

class GunicornLogAnalyzer:
    def __init__(self, log_file_path):
        self.log_file_path = log_file_path
        
        # 访问日志解析模式
        self.access_pattern = re.compile(
            r'(?P<ip>[\d\.]+) - (?P<user>\S+) \[(?P<timestamp>[^\]]+)\] '
            r'"(?P<method>\w+) (?P<path>[^\s]+) HTTP/[\d\.]+" '
            r'(?P<status>\d+) (?P<size>\d+) "(?P<referer>[^"]*)" '
            r'"(?P<user_agent>[^"]*)" (?P<response_time>[\d\.]+)'
        )
        
        # 错误日志解析模式
        self.error_pattern = re.compile(
            r'\[(?P<timestamp>[^\]]+)\] \[(?P<log_level>\w+)\] '
            r'(?P<process_info>\[PID:\d+\]) (?P<message>.*)'
        )
    
    def parse_access_log(self, max_lines=None):
        """解析访问日志"""
        entries = []
        
        with open(self.log_file_path, 'r') as f:
            for i, line in enumerate(f):
                if max_lines and i >= max_lines:
                    break
                
                match = self.access_pattern.match(line)
                if match:
                    entry = {
                        'ip': match.group('ip'),
                        'timestamp': match.group('timestamp'),
                        'method': match.group('method'),
                        'path': match.group('path'),
                        'status': int(match.group('status')),
                        'size': int(match.group('size')),
                        'referer': match.group('referer'),
                        'user_agent': match.group('user_agent'),
                        'response_time': float(match.group('response_time'))
                    }
                    entries.append(entry)
        
        return entries
    
    def analyze_status_codes(self, entries):
        """分析HTTP状态码分布"""
        status_counts = defaultdict(int)
        
        for entry in entries:
            status = entry['status']
            status_counts[status] += 1
            status_counts[f"{status // 100}xx"] += 1
        
        return dict(status_counts)
    
    def analyze_response_times(self, entries):
        """分析响应时间"""
        response_times = [entry['response_time'] for entry in entries]
        
        if not response_times:
            return {}
        
        sorted_times = sorted(response_times)
        total_requests = len(response_times)
        
        return {
            'min': min(response_times),
            'max': max(response_times),
            'avg': sum(response_times) / total_requests,
            'p50': sorted_times[int(total_requests * 0.5)],
            'p75': sorted_times[int(total_requests * 0.75)],
            'p90': sorted_times[int(total_requests * 0.9)],
            'p95': sorted_times[int(total_requests * 0.95)],
            'p99': sorted_times[int(total_requests * 0.99)]
        }
    
    def analyze_top_paths(self, entries, limit=10):
        """分析最受欢迎的路径"""
        path_counts = defaultdict(int)
        
        for entry in entries:
            path_counts[entry['path']] += 1
        
        return sorted(path_counts.items(), key=lambda x: x[1], reverse=True)[:limit]
    
    def analyze_top_ips(self, entries, limit=10):
        """分析访问最频繁的IP"""
        ip_counts = defaultdict(int)
        
        for entry in entries:
            ip_counts[entry['ip']] += 1
        
        return sorted(ip_counts.items(), key=lambda x: x[1], reverse=True)[:limit]
    
    def analyze_hourly_requests(self, entries):
        """分析每小时的请求数"""
        hourly_counts = defaultdict(int)
        
        for entry in entries:
            try:
                # 尝试解析时间戳
                timestamp = datetime.datetime.strptime(entry['timestamp'], '%d/%b/%Y:%H:%M:%S %z')
                hour = timestamp.hour
                hourly_counts[hour] += 1
            except ValueError:
                # 如果解析失败，尝试其他格式
                try:
                    timestamp = datetime.datetime.strptime(entry['timestamp'], '%d/%b/%Y:%H:%M:%S')
                    hour = timestamp.hour
                    hourly_counts[hour] += 1
                except ValueError:
                    continue
        
        return dict(hourly_counts)
    
    def analyze_user_agents(self, entries, limit=10):
        """分析User-Agent分布"""
        ua_counts = defaultdict(int)
        
        for entry in entries:
            ua = entry['user_agent']
            if ua:
                ua_counts[ua] += 1
        
        return sorted(ua_counts.items(), key=lambda x: x[1], reverse=True)[:limit]
    
    def analyze_slow_requests(self, entries, threshold=1.0, limit=10):
        """分析慢请求"""
        slow_requests = [
            entry for entry in entries 
            if entry['response_time'] > threshold
        ]
        
        # 按响应时间排序
        slow_requests.sort(key=lambda x: x['response_time'], reverse=True)
        
        return slow_requests[:limit]
    
    def generate_report(self, max_lines=None):
        """生成完整分析报告"""
        entries = self.parse_access_log(max_lines)
        
        if not entries:
            return {"error": "No valid log entries found"}
        
        report = {
            "timestamp": datetime.datetime.now().isoformat(),
            "total_entries": len(entries),
            "date_range": {
                "start": min(entry['timestamp'] for entry in entries),
                "end": max(entry['timestamp'] for entry in entries)
            },
            "status_codes": self.analyze_status_codes(entries),
            "response_times": self.analyze_response_times(entries),
            "top_paths": self.analyze_top_paths(entries),
            "top_ips": self.analyze_top_ips(entries),
            "hourly_requests": self.analyze_hourly_requests(entries),
            "user_agents": self.analyze_user_agents(entries),
            "slow_requests": self.analyze_slow_requests(entries)
        }
        
        return report
    
    def save_report(self, report, output_file):
        """保存报告到文件"""
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"Report saved to {output_file}")

def main():
    parser = argparse.ArgumentParser(description='Analyze Gunicorn access logs')
    parser.add_argument('log_file', help='Path to the log file')
    parser.add_argument('--max-lines', type=int, help='Maximum number of lines to analyze')
    parser.add_argument('--output', help='Output file for the report (default: stdout)')
    
    args = parser.parse_args()
    
    analyzer = GunicornLogAnalyzer(args.log_file)
    report = analyzer.generate_report(args.max_lines)
    
    if args.output:
        analyzer.save_report(report, args.output)
    else:
        print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()