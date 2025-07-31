#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试看板功能 - 包含模拟数据
"""

import requests
import json
from datetime import datetime, timedelta

def test_kanban_with_mock_data():
    """测试看板功能，使用模拟数据"""
    print('🧪 测试看板功能（包含模拟数据）:')
    print('=' * 60)
    
    try:
        # 创建会话并登录
        session = requests.Session()
        
        # 登录
        login_url = 'http://localhost:8080/login'
        login_data = {
            'username': 'Esther',
            'password': '967420'
        }
        
        print('正在登录...')
        login_response = session.post(login_url, data=login_data, timeout=10)
        
        if login_response.status_code not in [200, 302]:
            print(f'❌ 登录失败: HTTP {login_response.status_code}')
            return
        
        print('✅ 登录成功')
        
        # 测试API
        url = 'http://localhost:8080/get_expiring_customers'
        response = session.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f'📊 API返回数据: {json.dumps(data, ensure_ascii=False, indent=2)}')
            
            # 如果没有真实数据，创建模拟数据进行测试
            if not data.get('expiring_customers') or len(data.get('expiring_customers', [])) == 0:
                print('\n🎭 创建模拟数据进行测试...')
                
                # 创建模拟客户数据
                mock_data = {
                    'title': '明天到期客户 (3个)',
                    'count': 3,
                    'date_range': '08月01日 至 08月01日',
                    'expiring_customers': [
                        {
                            'user_id': 'JDY001234',
                            'expiry_date': '2025年08月01日',
                            'renewal_sales': '朱晓琳',
                            'company_name': '测试科技有限公司'
                        },
                        {
                            'user_id': 'JDY005678',
                            'expiry_date': '2025年08月01日',
                            'renewal_sales': '张三',
                            'company_name': '示例企业集团'
                        },
                        {
                            'user_id': 'JDY009999',
                            'expiry_date': '2025年08月01日',
                            'renewal_sales': '李四',
                            'company_name': '样本公司'
                        }
                    ]
                }
                
                print('📋 模拟数据创建完成:')
                print(f'  - 标题: {mock_data["title"]}')
                print(f'  - 客户数量: {mock_data["count"]}')
                print(f'  - 客户列表:')
                for i, customer in enumerate(mock_data['expiring_customers'], 1):
                    print(f'    {i}. {customer["user_id"]} - {customer["company_name"]} - {customer["renewal_sales"]}')
                
                # 测试前端显示逻辑
                test_frontend_display(mock_data)
            else:
                print('✅ 使用真实数据测试')
                test_frontend_display(data)
                
        else:
            print(f'❌ API请求失败: HTTP {response.status_code}')
            
    except Exception as e:
        print(f'❌ 测试异常: {str(e)}')

def test_frontend_display(data):
    """测试前端显示逻辑"""
    print('\n🎨 测试前端显示逻辑:')
    print('=' * 40)
    
    customers = data.get('expiring_customers', [])
    title = data.get('title', '')
    message = data.get('message', '')
    
    print(f'标题: {title}')
    
    if message:
        print(f'消息: {message}')
        print('📝 应显示: 友好消息界面')
        return
    
    if not customers or len(customers) == 0:
        print('📝 应显示: 无客户到期界面')
        return
    
    print(f'📝 应显示: {len(customers)} 个客户卡片')
    
    for i, customer in enumerate(customers, 1):
        print(f'  卡片 {i}:')
        
        # 模拟前端数据清理逻辑
        expiry_date = clean_value(customer.get('expiry_date'), '日期待确认')
        user_id = clean_value(customer.get('user_id'), '信息待完善')
        renewal_sales = clean_value(customer.get('renewal_sales'), '待分配')
        
        print(f'    🗓️ 到期时间: {expiry_date}')
        print(f'    👤 用户ID: {user_id}')
        print(f'    💼 责任销售: {renewal_sales}')

def clean_value(value, default_value):
    """数据清理函数（模拟前端逻辑）"""
    if not value or \
       value == 'undefined' or \
       value == 'null' or \
       value == '未指定' or \
       str(value).strip() == '':
        return default_value
    return str(value).strip()

def test_edge_cases():
    """测试边界情况"""
    print('\n🧪 测试边界情况:')
    print('=' * 40)
    
    # 测试空数据
    print('1. 测试空数据:')
    test_frontend_display({
        'title': '今日无客户到期',
        'expiring_customers': [],
        'message': ''
    })
    
    print('\n2. 测试消息数据:')
    test_frontend_display({
        'title': '周末休息',
        'expiring_customers': [],
        'message': '周末休息，无客户到期提醒'
    })
    
    print('\n3. 测试异常数据:')
    test_frontend_display({
        'title': '数据异常测试',
        'expiring_customers': [
            {
                'user_id': '',
                'expiry_date': 'undefined',
                'renewal_sales': 'null'
            },
            {
                'user_id': 'JDY123',
                'expiry_date': '2025年08月01日',
                'renewal_sales': '正常销售'
            }
        ]
    })

if __name__ == '__main__':
    test_kanban_with_mock_data()
    test_edge_cases()
