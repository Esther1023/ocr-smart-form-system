#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试KA看板API和数据显示（带登录认证）
"""

import requests
import json
import pandas as pd
from datetime import datetime, timedelta

def test_api_with_login():
    """测试带登录认证的API"""
    print('🧪 测试KA看板API响应（带登录认证）:')
    print('=' * 60)
    
    try:
        # 创建会话以保持登录状态
        session = requests.Session()
        
        # 先登录
        login_url = 'http://localhost:8080/login'
        login_data = {
            'username': 'Esther',
            'password': '967420'
        }
        
        print('正在登录...')
        login_response = session.post(login_url, data=login_data, timeout=10)
        print(f'登录响应状态码: {login_response.status_code}')
        
        if login_response.status_code != 200 and login_response.status_code != 302:
            print(f'❌ 登录失败: HTTP {login_response.status_code}')
            print(f'响应内容: {login_response.text[:200]}...')
            return
        
        print('✅ 登录成功')
        
        # 测试API端点
        url = 'http://localhost:8080/get_expiring_customers'
        
        print(f'请求URL: {url}')
        
        # 发送请求（使用已登录的会话）
        response = session.get(url, timeout=10)
        
        print(f'响应状态码: {response.status_code}')
        print(f'响应头: {dict(response.headers)}')
        
        if response.status_code == 200:
            try:
                data = response.json()
                
                print('\n✅ API响应成功!')
                print(f'响应数据结构:')
                print(f'  - title: {data.get("title", "未找到")}')
                print(f'  - count: {data.get("count", "未找到")}')
                print(f'  - date_range: {data.get("date_range", "未找到")}')
                print(f'  - message: {data.get("message", "未找到")}')
                print(f'  - expiring_customers: {len(data.get("expiring_customers", []))} 个客户')
                
                # 显示客户数据示例
                customers = data.get('expiring_customers', [])
                if customers:
                    print('\n📋 客户数据示例:')
                    for i, customer in enumerate(customers[:3], 1):
                        print(f'  客户 {i}:')
                        print(f'    到期时间: {customer.get("expiry_date", "未找到")}')
                        print(f'    用户ID: {customer.get("user_id", "未找到")}')
                        print(f'    责任销售: {customer.get("renewal_sales", "未找到")}')
                else:
                    print('\n📋 无客户数据')
                    
                return data
                    
            except json.JSONDecodeError as e:
                print(f'❌ JSON解析失败: {str(e)}')
                print(f'响应内容: {response.text[:500]}...')
        else:
            print(f'❌ API请求失败: HTTP {response.status_code}')
            print(f'响应内容: {response.text[:200]}...')
            
    except requests.exceptions.ConnectionError:
        print('❌ 连接失败: 应用可能未启动')
    except Exception as e:
        print(f'❌ 测试异常: {str(e)}')
        
    return None

def test_backend_logic_direct():
    """直接测试后端逻辑"""
    print('\n🔧 直接测试后端逻辑:')
    print('=' * 60)
    
    try:
        # 读取Excel文件
        excel_path = '战区续费_副本.xlsx'
        df = pd.read_excel(excel_path)
        print(f'✅ 成功读取Excel文件，共{len(df)}行数据')
        
        # 检查关键字段
        key_fields = ['到期日期', '用户ID', '续费责任销售', '责任销售中英文', '简道云销售']
        
        print('字段检查:')
        for field in key_fields:
            if field in df.columns:
                non_null_count = df[field].notna().sum()
                print(f'  ✅ {field}: {non_null_count} 条有效数据')
            else:
                print(f'  ❌ {field}: 字段不存在')
        
        # 模拟后端的日期计算逻辑
        now = pd.Timestamp.now()
        weekday = now.weekday()  # 0=周一, 1=周二, ..., 6=周日
        
        print(f'\n当前时间: {now.strftime("%Y年%m月%d日 %H:%M")}')
        print(f'星期几: {["周一","周二","周三","周四","周五","周六","周日"][weekday]}')
        
        if weekday < 4:  # 周一至周四 (0-3)
            # 显示明天到期的客户
            start_date = now + pd.Timedelta(days=1)
            end_date = start_date
            title = f"{start_date.strftime('%m月%d日')}到期客户"
        elif weekday == 4:  # 周五
            # 显示整个周末期间（周六和周日）到期的客户
            start_date = now + pd.Timedelta(days=1)  # 周六
            end_date = now + pd.Timedelta(days=2)    # 周日
            title = "周末到期客户"
        else:  # 周末 (weekday == 5 or 6)
            # 周末不用提醒，返回空范围
            print("周末期间，不显示提醒")
            return
        
        print(f'查询日期范围: {start_date.strftime("%Y-%m-%d")} 至 {end_date.strftime("%Y-%m-%d")}')
        print(f'看板标题: {title}')
        
        # 筛选出目标日期范围内将要过期的客户
        expiring_customers = []
        for _, row in df.iterrows():
            if pd.notna(row['到期日期']):
                try:
                    expiry_date = pd.to_datetime(row['到期日期'])
                    # 检查过期时间是否在目标日期范围内
                    expiry_date_only = expiry_date.date()
                    start_date_only = start_date.date()
                    end_date_only = end_date.date()
                    
                    if start_date_only <= expiry_date_only <= end_date_only:
                        customer_info = {
                            'user_id': str(row.get('用户ID', '')),
                            'expiry_date': expiry_date.strftime('%Y年%m月%d日'),
                            'renewal_sales': str(row.get('续费责任销售', ''))
                        }
                        expiring_customers.append(customer_info)
                        
                except Exception as e:
                    continue
        
        print(f'\n找到 {len(expiring_customers)} 个匹配客户:')
        for i, customer in enumerate(expiring_customers[:5], 1):
            print(f'  客户 {i}:')
            print(f'    到期时间: {customer["expiry_date"]}')
            print(f'    用户ID: {customer["user_id"]}')
            print(f'    责任销售: {customer["renewal_sales"]}')
        
        if len(expiring_customers) > 5:
            print(f'  ... 还有 {len(expiring_customers) - 5} 个客户')
            
        return {
            'title': title,
            'count': len(expiring_customers),
            'expiring_customers': expiring_customers
        }
        
    except Exception as e:
        print(f'❌ 后端逻辑测试失败: {str(e)}')
        return None

if __name__ == '__main__':
    # 测试API
    api_result = test_api_with_login()
    
    # 测试后端逻辑
    backend_result = test_backend_logic_direct()
    
    # 比较结果
    if api_result and backend_result:
        print('\n🔍 结果比较:')
        print('=' * 60)
        print(f'API结果客户数量: {len(api_result.get("expiring_customers", []))}')
        print(f'后端逻辑客户数量: {len(backend_result.get("expiring_customers", []))}')
        print(f'API标题: {api_result.get("title", "未找到")}')
        print(f'后端标题: {backend_result.get("title", "未找到")}')
        
        if len(api_result.get("expiring_customers", [])) == len(backend_result.get("expiring_customers", [])):
            print('✅ 数据一致性检查通过')
        else:
            print('❌ 数据不一致，需要进一步检查')
