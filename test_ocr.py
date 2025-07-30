#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCR服务测试脚本
"""

import sys
import os
from PIL import Image, ImageDraw, ImageFont
import io

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from ocr_service import OCRService
    print("✓ OCR服务模块导入成功")
except ImportError as e:
    print(f"✗ OCR服务模块导入失败: {e}")
    print("请确保已安装所需依赖：pip install pytesseract pillow opencv-python")
    sys.exit(1)

def create_test_image():
    """创建一个测试图片"""
    # 创建一个白色背景的图片
    img = Image.new('RGB', (600, 400), color='white')
    draw = ImageDraw.Draw(img)
    
    # 尝试使用系统字体
    try:
        # 在macOS上尝试使用中文字体
        font_paths = [
            '/System/Library/Fonts/PingFang.ttc',
            '/System/Library/Fonts/Helvetica.ttc',
            '/Library/Fonts/Arial.ttf'
        ]
        
        font = None
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    font = ImageFont.truetype(font_path, 20)
                    break
                except:
                    continue
        
        if font is None:
            font = ImageFont.load_default()
            
    except:
        font = ImageFont.load_default()
    
    # 添加测试文本
    test_text = [
        "公司名称：测试科技有限公司",
        "税号：91330000123456789X", 
        "注册地址：浙江省杭州市西湖区测试路88号",
        "注册电话：0571-88888888",
        "开户行：中国测试银行杭州分行",
        "银行账号：1234567890123456789",
        "联系人：张测试",
        "联系电话：13800138000",
        "邮寄地址：浙江省杭州市西湖区测试路88号",
        "简道云账号：12345678abcdefghijklmnop"
    ]
    
    y_position = 30
    for line in test_text:
        draw.text((30, y_position), line, fill='black', font=font)
        y_position += 35
    
    # 保存为字节数据
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    
    return img_byte_arr

def test_ocr_service():
    """测试OCR服务"""
    print("\n开始测试OCR服务...")
    
    # 创建OCR服务实例
    ocr_service = OCRService()
    print("✓ OCR服务实例创建成功")
    
    # 创建测试图片
    print("创建测试图片...")
    test_image_data = create_test_image()
    print(f"✓ 测试图片创建成功，大小: {len(test_image_data)} bytes")
    
    # 处理图片
    print("开始OCR识别...")
    result = ocr_service.process_image(test_image_data)
    
    # 显示结果
    print("\n=== OCR识别结果 ===")
    print(f"识别状态: {'成功' if result['success'] else '失败'}")
    
    if result['success']:
        print(f"识别字段数量: {result['field_count']}")
        print(f"原始文本长度: {len(result['extracted_text'])}")
        
        print("\n识别的字段:")
        for field_name, value in result['parsed_fields'].items():
            print(f"  {field_name}: {value}")
        
        print(f"\n原始识别文本:")
        print(result['extracted_text'])
        
    else:
        print(f"识别失败: {result.get('error', '未知错误')}")
    
    return result['success']

if __name__ == '__main__':
    print("OCR服务测试程序")
    print("=" * 50)
    
    try:
        success = test_ocr_service()
        if success:
            print("\n✓ OCR服务测试通过")
        else:
            print("\n✗ OCR服务测试失败")
            
    except Exception as e:
        print(f"\n✗ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
