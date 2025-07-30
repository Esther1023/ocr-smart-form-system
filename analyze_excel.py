#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel数据源分析脚本
"""

import pandas as pd
import sys

def analyze_excel():
    try:
        # 读取Excel文件
        df = pd.read_excel('战区续费_副本.xlsx')
        
        print('📊 Excel文件分析报告')
        print('=' * 60)
        print(f'总行数: {len(df)}')
        print(f'总列数: {len(df.columns)}')
        print()
        
        print('📋 所有列名:')
        for i, col in enumerate(df.columns, 1):
            print(f'{i:2d}. {col}')
        print()
        
        # 检查关键字段
        key_fields = {
            '账号-企业名称': '查询结果显示用',
            '公司名称': '表单填充用',
            '税号': '表单填充用',
            '简道云销售': '用户ID字段',
            '客户分类': '看板过滤用',
            '到期日期': '看板筛选用',
            '应续ARR': '看板显示用'
        }
        
        print('🔍 关键字段检查:')
        for field, desc in key_fields.items():
            if field in df.columns:
                non_null_count = df[field].notna().sum()
                print(f'✅ {field} ({desc}): 存在，有效数据 {non_null_count} 条')
                # 显示前3个非空值作为示例
                sample_values = df[field].dropna().head(3).tolist()
                print(f'   示例值: {sample_values}')
            else:
                print(f'❌ {field} ({desc}): 不存在')
        print()
        
        # 检查可能的替代字段
        possible_company_fields = [col for col in df.columns if '公司' in col or '企业' in col or '名称' in col]
        possible_tax_fields = [col for col in df.columns if '税' in col or '统一' in col or '信用' in col]
        
        print('🔍 可能的公司名称字段:')
        for field in possible_company_fields:
            non_null_count = df[field].notna().sum()
            print(f'  - {field}: {non_null_count} 条有效数据')
        
        print('🔍 可能的税号字段:')
        for field in possible_tax_fields:
            non_null_count = df[field].notna().sum()
            print(f'  - {field}: {non_null_count} 条有效数据')
        print()
        
        # 检查包含name的客户分类
        if '客户分类' in df.columns:
            name_customers = df[df['客户分类'].astype(str).str.contains('name', case=False, na=False)]
            print(f'🚫 包含"name"的客户分类: {len(name_customers)} 个')
            if len(name_customers) > 0:
                print('示例:')
                for idx, row in name_customers.head(5).iterrows():
                    print(f'  - {row.get("账号-企业名称", "N/A")}: {row.get("客户分类", "N/A")}')
        
        # 检查一周内到期的客户
        if '到期日期' in df.columns:
            now = pd.Timestamp.now()
            one_week_later = now + pd.Timedelta(days=7)
            
            expiring_customers = []
            name_filtered_customers = []
            
            for _, row in df.iterrows():
                if pd.notna(row['到期日期']):
                    try:
                        expiry_date = pd.to_datetime(row['到期日期'])
                        if now <= expiry_date <= one_week_later:
                            customer_classification = str(row.get('客户分类', ''))
                            customer_info = {
                                'company': row.get('账号-企业名称', ''),
                                'classification': customer_classification,
                                'arr': row.get('应续ARR', 0),
                                'expiry': expiry_date.strftime('%Y-%m-%d')
                            }
                            
                            if 'name' in customer_classification.lower():
                                name_filtered_customers.append(customer_info)
                            else:
                                expiring_customers.append(customer_info)
                    except:
                        pass
            
            print(f'📅 一周内到期客户分析:')
            print(f'  - 符合条件的客户: {len(expiring_customers)} 个')
            print(f'  - 被过滤的name客户: {len(name_filtered_customers)} 个')
            
            if expiring_customers:
                print('符合条件的客户示例:')
                for customer in expiring_customers[:3]:
                    print(f'  - {customer["company"]} | {customer["classification"]} | {customer["arr"]} | {customer["expiry"]}')
            
            if name_filtered_customers:
                print('被过滤的客户示例:')
                for customer in name_filtered_customers[:3]:
                    print(f'  - {customer["company"]} | {customer["classification"]} | {customer["arr"]} | {customer["expiry"]}')
        
    except Exception as e:
        print(f'❌ 分析失败: {str(e)}')
        return False
    
    return True

if __name__ == '__main__':
    analyze_excel()
