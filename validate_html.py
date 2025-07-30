#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTML标签验证脚本
"""

import re
from html.parser import HTMLParser

class LabelValidator(HTMLParser):
    def __init__(self):
        super().__init__()
        self.labels = []
        self.ids = []
        self.current_tag = None
        self.current_attrs = {}
        
    def handle_starttag(self, tag, attrs):
        self.current_tag = tag
        self.current_attrs = dict(attrs)
        
        if tag == 'label':
            for_attr = self.current_attrs.get('for', '')
            if for_attr:
                self.labels.append({
                    'for': for_attr,
                    'line': self.getpos()[0]
                })
        
        if 'id' in self.current_attrs:
            self.ids.append({
                'id': self.current_attrs['id'],
                'tag': tag,
                'line': self.getpos()[0]
            })
    
    def validate(self):
        print('🔍 HTML标签验证结果:')
        print('=' * 50)
        
        # 检查for属性
        for_values = [label['for'] for label in self.labels]
        id_values = [id_item['id'] for id_item in self.ids]
        
        print(f'找到 {len(self.labels)} 个label标签with for属性:')
        for label in self.labels:
            print(f"  行 {label['line']:3d}: for=\"{label['for']}\"")
        
        print(f'\n找到 {len(self.ids)} 个元素with id属性:')
        for id_item in self.ids:
            print(f"  行 {id_item['line']:3d}: <{id_item['tag']}> id=\"{id_item['id']}\"")
        
        # 检查不匹配的for属性
        unmatched_labels = []
        for label in self.labels:
            if label['for'] not in id_values:
                unmatched_labels.append(label)
        
        if unmatched_labels:
            print('\n❌ 不匹配的label for属性:')
            for label in unmatched_labels:
                print(f"  行 {label['line']}: for=\"{label['for']}\" (没有对应的id)")
        else:
            print('\n✅ 所有label for属性都有对应的id')
        
        # 检查重复的id
        id_counts = {}
        for id_item in self.ids:
            id_val = id_item['id']
            if id_val in id_counts:
                id_counts[id_val].append(id_item)
            else:
                id_counts[id_val] = [id_item]
        
        duplicates = {k: v for k, v in id_counts.items() if len(v) > 1}
        if duplicates:
            print('\n❌ 重复的id:')
            for id_val, items in duplicates.items():
                print(f"  id=\"{id_val}\" 出现在:")
                for item in items:
                    print(f"    行 {item['line']}: <{item['tag']}>")
        else:
            print('\n✅ 没有重复的id')
        
        # 检查空的for属性
        empty_for = [label for label in self.labels if not label['for'].strip()]
        if empty_for:
            print('\n❌ 空的for属性:')
            for label in empty_for:
                print(f"  行 {label['line']}: for=\"{label['for']}\"")
        else:
            print('\n✅ 没有空的for属性')

def validate_html_file(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        validator = LabelValidator()
        validator.feed(content)
        validator.validate()
        
    except Exception as e:
        print(f'❌ 验证失败: {str(e)}')

if __name__ == '__main__':
    validate_html_file('templates/index.html')
