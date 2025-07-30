#!/usr/bin/env python3
"""
部署验证测试脚本
用于验证OCR图片识别系统的各项功能是否正常工作
"""

import requests
import json
import time
import sys
from urllib.parse import urljoin

class DeploymentTester:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'OCR-System-Deployment-Tester/1.0'
        })
    
    def test_health_check(self):
        """测试健康检查端点"""
        print("🔍 测试健康检查端点...")
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 健康检查通过: {data.get('status')}")
                return True
            else:
                print(f"❌ 健康检查失败: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 健康检查异常: {str(e)}")
            return False
    
    def test_homepage(self):
        """测试首页加载"""
        print("🏠 测试首页加载...")
        try:
            response = self.session.get(self.base_url, timeout=10)
            if response.status_code == 200 and ('智能表单' in response.text or 'OCR' in response.text or 'form' in response.text.lower()):
                print("✅ 首页加载成功")
                return True
            else:
                print(f"❌ 首页加载失败: HTTP {response.status_code}")
                print(f"响应内容预览: {response.text[:200]}...")
                return False
        except Exception as e:
            print(f"❌ 首页加载异常: {str(e)}")
            return False
    
    def test_static_files(self):
        """测试静态文件加载"""
        print("📁 测试静态文件...")
        static_files = ['/static/style.css', '/static/script.js']
        
        for file_path in static_files:
            try:
                response = self.session.get(f"{self.base_url}{file_path}", timeout=5)
                if response.status_code == 200:
                    print(f"✅ {file_path} 加载成功")
                else:
                    print(f"❌ {file_path} 加载失败: HTTP {response.status_code}")
                    return False
            except Exception as e:
                print(f"❌ {file_path} 加载异常: {str(e)}")
                return False
        
        return True
    
    def test_api_endpoints(self):
        """测试API端点"""
        print("🔌 测试API端点...")
        
        # 测试获取最后导入时间
        try:
            response = self.session.get(f"{self.base_url}/get_last_import_time", timeout=5)
            if response.status_code == 200:
                print("✅ 导入时间API正常")
            else:
                print(f"❌ 导入时间API失败: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 导入时间API异常: {str(e)}")
            return False
        
        # 测试获取即将过期客户
        try:
            response = self.session.get(f"{self.base_url}/get_expiring_customers", timeout=10)
            if response.status_code == 200:
                print("✅ 过期客户API正常")
            else:
                print(f"❌ 过期客户API失败: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 过期客户API异常: {str(e)}")
            return False
        
        return True
    
    def test_performance(self):
        """测试性能"""
        print("⚡ 测试响应性能...")
        
        start_time = time.time()
        try:
            response = self.session.get(self.base_url, timeout=10)
            end_time = time.time()
            
            response_time = end_time - start_time
            if response_time < 5.0:  # 5秒内响应
                print(f"✅ 响应时间正常: {response_time:.2f}秒")
                return True
            else:
                print(f"⚠️ 响应时间较慢: {response_time:.2f}秒")
                return True  # 不算失败，只是警告
        except Exception as e:
            print(f"❌ 性能测试异常: {str(e)}")
            return False
    
    def run_all_tests(self):
        """运行所有测试"""
        print(f"🚀 开始测试部署: {self.base_url}")
        print("=" * 50)
        
        tests = [
            ("健康检查", self.test_health_check),
            ("首页加载", self.test_homepage),
            ("静态文件", self.test_static_files),
            ("API端点", self.test_api_endpoints),
            ("性能测试", self.test_performance),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n📋 {test_name}测试:")
            if test_func():
                passed += 1
            time.sleep(1)  # 避免请求过于频繁
        
        print("\n" + "=" * 50)
        print(f"📊 测试结果: {passed}/{total} 通过")
        
        if passed == total:
            print("🎉 所有测试通过！部署成功！")
            return True
        else:
            print("❌ 部分测试失败，请检查部署配置")
            return False

def main():
    if len(sys.argv) != 2:
        print("使用方法: python test_deployment.py <URL>")
        print("例如: python test_deployment.py https://your-app.railway.app")
        sys.exit(1)
    
    url = sys.argv[1]
    tester = DeploymentTester(url)
    
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
