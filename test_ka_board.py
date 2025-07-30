#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试KA看板API和数据显示
"""

import requests
import json
import pandas as pd
from datetime import datetime, timedelta

def test_api_response():
    """测试API返回的数据结构"""
    print('🧪 测试KA看板API响应:')
    print('=' * 60)
    
    try:
        # 测试API端点
        url = 'http://localhost:8080/get_expiring_customers'
        
        print(f'请求URL: {url}')
        
        # 发送请求
        response = requests.get(url, timeout=10)
        
        print(f'响应状态码: {response.status_code}')
        print(f'响应头: {dict(response.headers)}')
        
        if response.status_code == 200:
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
                
        elif response.status_code == 302:
            print('\n🔄 需要登录认证')
            print(f'重定向到: {response.headers.get("Location", "未知")}')
            
        else:
            print(f'\n❌ API请求失败')
            print(f'错误信息: {response.text}')
            
    except requests.exceptions.ConnectionError:
        print('❌ 连接失败: 应用可能未启动')
    except requests.exceptions.Timeout:
        print('❌ 请求超时')
    except Exception as e:
        print(f'❌ 测试失败: {str(e)}')

def test_date_logic():
    """测试日期计算逻辑"""
    print('\n🗓️ 测试日期计算逻辑:')
    print('=' * 60)
    
    # 模拟当前时间
    now = pd.Timestamp.now()
    weekday = now.weekday()
    
    print(f'当前时间: {now.strftime("%Y年%m月%d日 %H:%M")}')
    print(f'星期几: {["周一","周二","周三","周四","周五","周六","周日"][weekday]}')
    
    # 计算目标日期
    if weekday < 4:  # 周一至周四
        start_date = now + pd.Timedelta(days=1)
        end_date = start_date
        title = '明天到期的客户'
        expected_display = start_date.strftime('%m月%d日')
    elif weekday == 4:  # 周五
        start_date = now + pd.Timedelta(days=1)
        end_date = now + pd.Timedelta(days=2)
        title = '周末到期的客户'
        expected_display = f"{start_date.strftime('%m月%d日')}至{end_date.strftime('%m月%d日')}"
    else:  # 周末
        print('周末期间，应该不显示提醒')
        return
    
    print(f'\n预期结果:')
    print(f'  查询日期: {expected_display}')
    print(f'  标题格式: "{expected_display}到期客户 (X个)"')
    print(f'  日期范围: {start_date.strftime("%Y-%m-%d")} 至 {end_date.strftime("%Y-%m-%d")}')

def test_data_processing():
    """测试数据处理逻辑"""
    print('\n📊 测试数据处理逻辑:')
    print('=' * 60)
    
    try:
        # 读取Excel文件
        df = pd.read_excel('战区续费_副本.xlsx')
        
        # 检查关键字段
        key_fields = ['到期日期', '用户ID', '续费责任销售', '责任销售中英文', '简道云销售']
        
        print('字段检查:')
        for field in key_fields:
            if field in df.columns:
                non_null_count = df[field].notna().sum()
                print(f'  ✅ {field}: {non_null_count} 条有效数据')
            else:
                print(f'  ❌ {field}: 字段不存在')
        
        # 模拟数据处理
        now = pd.Timestamp.now()
        start_date = now + pd.Timedelta(days=1)
        end_date = start_date
        
        print(f'\n模拟查询范围: {start_date.strftime("%Y-%m-%d")}')
        
        matching_customers = []
        for _, row in df.iterrows():
            if pd.notna(row['到期日期']):
                try:
                    expiry_date = pd.to_datetime(row['到期日期'])
                    if start_date.date() <= expiry_date.date() <= end_date.date():
                        # 模拟数据处理逻辑
                        user_id_raw = row.get('用户ID', '')
                        user_id = str(user_id_raw) if pd.notna(user_id_raw) else ''
                        
                        renewal_sales = ''
                        for sales_field in ['续费责任销售', '责任销售中英文', '简道云销售']:
                            if sales_field in row and pd.notna(row[sales_field]):
                                renewal_sales = str(row[sales_field])
                                break
                        
                        # 处理空值
                        final_user_id = user_id if user_id and user_id != '未指定' else '暂无信息'
                        final_renewal_sales = renewal_sales if renewal_sales and renewal_sales != '未指定' else '暂无信息'
                        
                        matching_customers.append({
                            'company': row.get('账号-企业名称', ''),
                            'expiry_date': expiry_date.strftime('%m月%d日'),
                            'user_id': final_user_id,
                            'renewal_sales': final_renewal_sales
                        })
                        
                        if len(matching_customers) >= 3:
                            break
                except:
                    pass
        
        print(f'\n找到 {len(matching_customers)} 个匹配客户:')
        for i, customer in enumerate(matching_customers, 1):
            print(f'  客户 {i}:')
            print(f'    公司: {customer["company"]}')
            print(f'    到期时间: {customer["expiry_date"]}')
            print(f'    用户ID: {customer["user_id"]}')
            print(f'    责任销售: {customer["renewal_sales"]}')
            
    except Exception as e:
        print(f'❌ 数据处理测试失败: {str(e)}')

if __name__ == '__main__':
    test_date_logic()
    test_data_processing()
    test_api_response()
