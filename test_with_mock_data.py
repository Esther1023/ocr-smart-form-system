#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用模拟数据测试KA看板显示效果
"""

import pandas as pd
from datetime import datetime, timedelta

def test_with_mock_customers():
    """测试有客户数据的情况"""
    print('🧪 测试有客户数据的KA看板显示:')
    print('=' * 60)
    
    # 模拟明天的日期
    now = pd.Timestamp.now()
    tomorrow = now + pd.Timedelta(days=1)
    
    print(f'当前时间: {now.strftime("%Y年%m月%d日 %H:%M")}')
    print(f'明天日期: {tomorrow.strftime("%Y年%m月%d日")}')
    
    # 模拟客户数据
    mock_customers = [
        {
            'expiry_date': tomorrow.strftime('%m月%d日'),
            'user_id': '65baeb1c3ab7331e0b802314',
            'renewal_sales': 'Kyle.Zheng-郑秀锐'
        },
        {
            'expiry_date': tomorrow.strftime('%m月%d日'),
            'user_id': '暂无信息',
            'renewal_sales': 'Alice.Wang-王小丽'
        },
        {
            'expiry_date': tomorrow.strftime('%m月%d日'),
            'user_id': '507f1f77bcf86cd799439011',
            'renewal_sales': '暂无信息'
        }
    ]
    
    # 应用修复后的数据处理逻辑
    processed_customers = []
    for customer in mock_customers:
        # 确保数据完整性，避免显示技术错误信息
        final_user_id = customer['user_id'] if customer['user_id'] and customer['user_id'] != '未指定' else '暂无信息'
        final_renewal_sales = customer['renewal_sales'] if customer['renewal_sales'] and customer['renewal_sales'] != '未指定' else '暂无信息'
        
        processed_customers.append({
            'expiry_date': customer['expiry_date'],
            'user_id': final_user_id,
            'renewal_sales': final_renewal_sales
        })
    
    # 生成用户友好的标题
    user_friendly_title = f"{tomorrow.strftime('%m月%d日')}到期客户 ({len(processed_customers)}个)"
    
    print(f'\\n📊 修复后的显示效果:')
    print(f'看板标题: {user_friendly_title}')
    print(f'客户数量: {len(processed_customers)}')
    
    print(f'\\n📋 客户列表:')
    for i, customer in enumerate(processed_customers, 1):
        print(f'  客户 {i}:')
        print(f'    到期时间: {customer["expiry_date"]}')
        print(f'    用户ID: {customer["user_id"]}')
        print(f'    责任销售: {customer["renewal_sales"]}')
    
    # 模拟前端JavaScript处理
    print(f'\\n🖥️ 前端JavaScript处理结果:')
    for i, customer in enumerate(processed_customers, 1):
        # 前端双重防护
        expiry_date = customer['expiry_date'] or '日期待确认'
        user_id = customer['user_id'] or '信息待完善'
        renewal_sales = customer['renewal_sales'] or '待分配'
        
        print(f'  客户 {i} (前端处理后):')
        print(f'    到期时间: {expiry_date}')
        print(f'    用户ID: {user_id}')
        print(f'    责任销售: {renewal_sales}')

def test_empty_data():
    """测试无客户数据的情况"""
    print('\\n🧪 测试无客户数据的显示:')
    print('=' * 60)
    
    now = pd.Timestamp.now()
    tomorrow = now + pd.Timedelta(days=1)
    
    # 无客户情况
    user_friendly_title = f"{tomorrow.strftime('%m月%d日')}无客户到期"
    user_message = f"今日({tomorrow.strftime('%m月%d日')})无客户到期，可以安心工作"
    
    print(f'📊 无客户数据显示效果:')
    print(f'看板标题: {user_friendly_title}')
    print(f'友好提示: {user_message}')
    
    # 前端显示
    print(f'\\n🖥️ 前端显示:')
    print(f'HTML内容: <div class="friendly-message">{user_message}</div>')

def test_weekend_scenario():
    """测试周末情况"""
    print('\\n🧪 测试周末显示:')
    print('=' * 60)
    
    # 模拟周六
    saturday = pd.Timestamp('2025-08-02')  # 假设这是周六
    
    print(f'模拟时间: {saturday.strftime("%Y年%m月%d日")} (周六)')
    
    # 周末逻辑
    title = "周末休息，无需提醒"
    message = "周末休息，无客户到期提醒"
    
    print(f'📊 周末显示效果:')
    print(f'标题: {title}')
    print(f'消息: {message}')
    
    # 前端显示
    print(f'\\n🖥️ 前端显示:')
    print(f'HTML内容: <div class="weekend-message">{message}</div>')

def test_data_safety():
    """测试数据安全处理"""
    print('\\n🧪 测试数据安全处理:')
    print('=' * 60)
    
    # 模拟各种问题数据
    problematic_data = [
        {'user_id': None, 'renewal_sales': 'John.Doe'},
        {'user_id': '', 'renewal_sales': ''},
        {'user_id': 'nan', 'renewal_sales': 'nan'},
        {'user_id': 'undefined', 'renewal_sales': 'undefined'},
        {'user_id': '未指定', 'renewal_sales': '未指定'},
    ]
    
    print('原始问题数据 -> 修复后显示:')
    for i, data in enumerate(problematic_data, 1):
        # 后端处理
        user_id = str(data['user_id']) if data['user_id'] and data['user_id'] not in ['nan', 'None', '未指定'] else '暂无信息'
        renewal_sales = str(data['renewal_sales']) if data['renewal_sales'] and data['renewal_sales'] not in ['nan', 'None', '未指定'] else '暂无信息'
        
        # 前端处理
        final_user_id = user_id or '信息待完善'
        final_renewal_sales = renewal_sales or '待分配'
        
        print(f'  数据 {i}:')
        print(f'    原始用户ID: {repr(data["user_id"])} -> 显示: {final_user_id}')
        print(f'    原始销售: {repr(data["renewal_sales"])} -> 显示: {final_renewal_sales}')

if __name__ == '__main__':
    test_with_mock_customers()
    test_empty_data()
    test_weekend_scenario()
    test_data_safety()
