#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建OCR测试图片
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_test_image():
    """创建包含中英文文字的测试图片"""
    
    # 创建白色背景图片
    width, height = 800, 600
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)
    
    # 尝试使用系统字体
    try:
        # Mac系统字体
        font_large = ImageFont.truetype('/System/Library/Fonts/PingFang.ttc', 40)
        font_medium = ImageFont.truetype('/System/Library/Fonts/PingFang.ttc', 30)
        font_small = ImageFont.truetype('/System/Library/Fonts/PingFang.ttc', 24)
    except:
        try:
            # 备用字体
            font_large = ImageFont.truetype('/System/Library/Fonts/Arial.ttf', 40)
            font_medium = ImageFont.truetype('/System/Library/Fonts/Arial.ttf', 30)
            font_small = ImageFont.truetype('/System/Library/Fonts/Arial.ttf', 24)
        except:
            # 使用默认字体
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
            font_small = ImageFont.load_default()
    
    # 绘制标题
    draw.text((50, 50), "测试公司信息", font=font_large, fill='black')
    draw.text((50, 100), "Test Company Information", font=font_medium, fill='black')
    
    # 绘制分割线
    draw.line([(50, 150), (750, 150)], fill='gray', width=2)
    
    # 绘制公司信息
    y_pos = 180
    company_info = [
        "公司名称：北京科技创新有限公司",
        "Company Name: Beijing Tech Innovation Co., Ltd.",
        "",
        "统一社会信用代码：91110000123456789X",
        "Tax ID: 91110000123456789X",
        "",
        "地址：北京市海淀区中关村大街1号",
        "Address: No.1 Zhongguancun Street, Haidian District, Beijing",
        "",
        "联系电话：010-12345678",
        "Phone: 010-12345678",
        "",
        "法定代表人：张三",
        "Legal Representative: Zhang San",
        "",
        "注册资本：1000万元人民币",
        "Registered Capital: 10 Million RMB"
    ]
    
    for line in company_info:
        if line.strip():  # 非空行
            draw.text((80, y_pos), line, font=font_small, fill='black')
        y_pos += 35
    
    # 保存图片
    image_path = 'test_ocr_image.png'
    image.save(image_path)
    print(f"✅ 测试图片已创建: {image_path}")
    return image_path

if __name__ == "__main__":
    create_test_image()
