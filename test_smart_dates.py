#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试智能日期筛选逻辑
"""

import pandas as pd
from datetime import datetime, timedelta

def get_target_date_range(current_time=None):
    """根据当前日期和工作日规则计算目标查询日期范围"""
    if current_time:
        now = pd.Timestamp(current_time)
    else:
        now = pd.Timestamp.now()
    
    weekday = now.weekday()  # 0=周一, 1=周二, ..., 6=周日
    
    if weekday < 4:  # 周一至周四 (0-3)
        # 显示明天到期的客户
        start_date = now + pd.Timedelta(days=1)
        end_date = start_date
        title = "明天到期的客户"
    elif weekday == 4:  # 周五
        # 显示整个周末期间（周六和周日）到期的客户
        start_date = now + pd.Timedelta(days=1)  # 周六
        end_date = now + pd.Timedelta(days=2)    # 周日
        title = "周末到期的客户"
    else:  # 周末 (weekday == 5 or 6)
        # 周末不用提醒，返回空范围
        return None, None, "周末休息，无需提醒"
    
    return start_date, end_date, title

def test_smart_dates():
    print('🧪 测试智能日期筛选逻辑:')
    print('=' * 50)

    # 测试不同的星期几
    test_dates = [
        ('2025-07-28', '周一'),  # 周一
        ('2025-07-29', '周二'),  # 周二
        ('2025-07-30', '周三'),  # 周三
        ('2025-07-31', '周四'),  # 周四
        ('2025-08-01', '周五'),  # 周五
        ('2025-08-02', '周六'),  # 周六
        ('2025-08-03', '周日'),  # 周日
    ]

    for date_str, day_name in test_dates:
        print(f'\n📅 模拟日期: {date_str} ({day_name})')
        
        start_date, end_date, title = get_target_date_range(date_str)
        
        if start_date is None:
            print(f'   结果: {title}')
        else:
            if start_date == end_date:
                print(f'   结果: {title} - {start_date.strftime("%Y-%m-%d")}')
            else:
                print(f'   结果: {title} - {start_date.strftime("%Y-%m-%d")} 至 {end_date.strftime("%Y-%m-%d")}')

    print('\n✅ 测试完成！')

def test_with_real_data():
    """测试使用真实数据的情况"""
    print('\n🔍 测试真实数据筛选:')
    print('=' * 50)
    
    try:
        # 读取Excel文件
        df = pd.read_excel('战区续费_副本.xlsx')
        
        # 模拟周五的情况（显示周末到期的客户）
        friday_date = '2025-08-01'  # 假设这是周五
        start_date, end_date, title = get_target_date_range(friday_date)
        
        if start_date is None:
            print(f'周末无需提醒: {title}')
            return
        
        print(f'模拟日期: {friday_date} (周五)')
        print(f'查询范围: {start_date.strftime("%Y-%m-%d")} 至 {end_date.strftime("%Y-%m-%d")}')
        print(f'标题: {title}')
        
        # 筛选数据
        matching_customers = []
        for _, row in df.iterrows():
            if pd.notna(row['到期日期']):
                try:
                    expiry_date = pd.to_datetime(row['到期日期'])
                    expiry_date_only = expiry_date.date()
                    start_date_only = start_date.date()
                    end_date_only = end_date.date()
                    
                    if start_date_only <= expiry_date_only <= end_date_only:
                        customer_classification = str(row.get('客户分类', ''))
                        # 过滤逻辑
                        if ('name客户' in customer_classification.lower() or 
                            ('name名单' in customer_classification.lower() and '非name' not in customer_classification.lower())):
                            continue
                        
                        matching_customers.append({
                            'company': row.get('账号-企业名称', ''),
                            'expiry_date': expiry_date.strftime('%Y年%m月%d日'),
                            'user_id': str(row.get('用户ID', '')),
                            'classification': customer_classification
                        })
                except:
                    pass
        
        print(f'找到 {len(matching_customers)} 个符合条件的客户')
        
        if matching_customers:
            print('\n客户示例:')
            for i, customer in enumerate(matching_customers[:3], 1):
                print(f'{i}. {customer["company"]} - {customer["expiry_date"]} - {customer["user_id"][:20]}...')
    
    except Exception as e:
        print(f'测试真实数据时出错: {str(e)}')

if __name__ == '__main__':
    test_smart_dates()
    test_with_real_data()
