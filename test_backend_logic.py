#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接测试后端逻辑，不通过API
"""

import pandas as pd
import os
from datetime import datetime, timedelta

def get_target_date_range():
    """根据当前日期和工作日规则计算目标查询日期范围"""
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

def test_backend_logic():
    """测试修复后的后端逻辑"""
    print('🧪 测试修复后的后端逻辑:')
    print('=' * 60)
    
    try:
        # 检查文件是否存在
        excel_path = '战区续费_副本.xlsx'
        if not os.path.exists(excel_path):
            print(f'❌ 文件不存在: {excel_path}')
            return
        
        # 读取Excel文件
        df = pd.read_excel(excel_path)
        print(f'✅ 成功读取Excel文件，共{len(df)}行数据')
        
        # 获取当前时间和目标日期范围
        now = pd.Timestamp.now()
        print(f'当前时间: {now.strftime("%Y年%m月%d日 %H:%M")}')
        
        # 使用智能日期计算
        start_date, end_date, title = get_target_date_range()
        
        # 如果是周末，返回空结果
        if start_date is None:
            print("周末期间，不显示提醒")
            result = {
                'expiring_customers': [],
                'title': title,
                'message': '周末休息，无客户到期提醒'
            }
            print(f'周末结果: {result}')
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
                        # 获取客户分类，过滤掉真正的"name客户"
                        customer_classification = str(row.get('客户分类', ''))
                        if ('name客户' in customer_classification.lower() or 
                            ('name名单' in customer_classification.lower() and '非name' not in customer_classification.lower())):
                            print(f"过滤掉name客户: {row.get('账号-企业名称', '')} - {customer_classification}")
                            continue
                        
                        # 获取用户ID和责任销售信息
                        user_id_raw = row.get('用户ID', '')
                        user_id = str(user_id_raw) if pd.notna(user_id_raw) else ''
                        
                        # 尝试多个销售字段，优先级：续费责任销售 > 责任销售中英文 > 简道云销售
                        renewal_sales = ''
                        sales_field_used = None
                        for sales_field in ['续费责任销售', '责任销售中英文', '简道云销售']:
                            if sales_field in row and pd.notna(row[sales_field]):
                                renewal_sales = str(row[sales_field])
                                sales_field_used = sales_field
                                break
                        
                        # 处理空值情况
                        if not user_id or user_id == 'nan' or user_id == 'None':
                            user_id = '未指定'
                        if not renewal_sales or renewal_sales == 'nan' or renewal_sales == 'None':
                            renewal_sales = '未指定'
                        
                        # 格式化日期为用户友好格式
                        expiry_date_display = expiry_date.strftime('%m月%d日')
                        
                        # 确保数据完整性，避免显示技术错误信息
                        final_user_id = user_id if user_id and user_id != '未指定' else '暂无信息'
                        final_renewal_sales = renewal_sales if renewal_sales and renewal_sales != '未指定' else '暂无信息'
                        
                        company_name = row.get('账号-企业名称', '')
                        print(f"处理客户: {company_name}")
                        print(f"  原始用户ID: {repr(user_id_raw)} -> 处理后: {final_user_id}")
                        print(f"  使用销售字段: {sales_field_used} -> 值: {final_renewal_sales}")
                        print(f"  到期日期: {expiry_date_display}")
                        
                        expiring_customers.append({
                            'expiry_date': expiry_date_display,  # 用户友好的到期时间格式
                            'user_id': final_user_id,  # 用户ID
                            'renewal_sales': final_renewal_sales,  # 责任销售
                            'expiry_date_sort': expiry_date  # 用于排序的日期对象
                        })
                        
                except Exception as e:
                    print(f"日期转换错误: {str(e)}")
                    continue
        
        # 按过期日期排序
        expiring_customers.sort(key=lambda x: x['expiry_date_sort'])
        
        # 移除排序用的字段
        for customer in expiring_customers:
            customer.pop('expiry_date_sort', None)
        
        # 生成用户友好的标题和描述
        if len(expiring_customers) == 0:
            if start_date == end_date:
                user_friendly_title = f"{start_date.strftime('%m月%d日')}无客户到期"
                user_message = f"今日({start_date.strftime('%m月%d日')})无客户到期，可以安心工作"
            else:
                user_friendly_title = f"{start_date.strftime('%m月%d日')}至{end_date.strftime('%m月%d日')}无客户到期"
                user_message = f"周末({start_date.strftime('%m月%d日')}至{end_date.strftime('%m月%d日')})无客户到期"
        else:
            if start_date == end_date:
                user_friendly_title = f"{start_date.strftime('%m月%d日')}到期客户 ({len(expiring_customers)}个)"
                user_message = None
            else:
                user_friendly_title = f"{start_date.strftime('%m月%d日')}至{end_date.strftime('%m月%d日')}到期客户 ({len(expiring_customers)}个)"
                user_message = None
        
        print(f"\\n找到{len(expiring_customers)}个即将过期的客户")
        
        result = {
            'expiring_customers': expiring_customers,
            'title': user_friendly_title,
            'count': len(expiring_customers),
            'date_range': f"{start_date.strftime('%m月%d日')} 至 {end_date.strftime('%m月%d日')}",
            'message': user_message
        }
        
        print(f'\\n📊 最终结果:')
        print(f'  标题: {result["title"]}')
        print(f'  数量: {result["count"]}')
        print(f'  日期范围: {result["date_range"]}')
        print(f'  消息: {result["message"]}')
        
        if expiring_customers:
            print(f'\\n📋 客户列表:')
            for i, customer in enumerate(expiring_customers[:5], 1):
                print(f'  客户 {i}:')
                print(f'    到期时间: {customer["expiry_date"]}')
                print(f'    用户ID: {customer["user_id"]}')
                print(f'    责任销售: {customer["renewal_sales"]}')
        
        return result
        
    except Exception as e:
        print(f'❌ 测试失败: {str(e)}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_backend_logic()
