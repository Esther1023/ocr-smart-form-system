#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCR服务模块
提供图片文本识别和智能字段匹配功能
"""

import os
import re
import logging
from typing import Dict, List, Tuple, Optional
import tempfile
import base64
import requests
import json

# 尝试导入OCR相关库，如果失败则使用简化版本
try:
    import cv2
    import numpy as np
    from PIL import Image
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    # 导入简化版本
    try:
        from simple_ocr import SimpleOCR
        SIMPLE_OCR_AVAILABLE = True
    except ImportError:
        SIMPLE_OCR_AVAILABLE = False

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OCRService:
    """OCR服务类"""
    
    def __init__(self):
        """初始化OCR服务"""
        # 如果没有完整的OCR库，使用简化版本
        if not OCR_AVAILABLE and SIMPLE_OCR_AVAILABLE:
            self.simple_ocr = SimpleOCR()
            logger.info("使用简化OCR服务")
        else:
            self.simple_ocr = None

        # 字段映射配置 - 支持多种表达方式
        self.field_mapping = {
            'company_name': [
                '公司名称', '甲方', '甲方名称', '企业名称', '单位名称', 
                '公司', '企业', '单位', '名称', '机构名称'
            ],
            'tax_number': [
                '税号', '纳税人识别号', '统一社会信用代码', '税务登记号',
                '纳税识别号', '信用代码', '社会信用代码'
            ],
            'reg_address': [
                '注册地址', '地址', '注册地', '企业地址', '公司地址',
                '营业地址', '办公地址', '联系地址'
            ],
            'reg_phone': [
                '注册电话', '电话', '联系电话', '固定电话', '办公电话',
                '公司电话', '座机', '固话'
            ],
            'bank_name': [
                '开户行', '开户银行', '银行', '开户行名称', '银行名称',
                '基本户开户行', '基本账户开户行'
            ],
            'bank_account': [
                '账号', '银行账号', '账户', '银行账户', '基本户账号',
                '对公账号', '基本账户', '开户账号', '银行卡号', '卡号',
                '账户号码', '银行账户号', '账户号'
            ],
            'contact_name': [
                '联系人', '联系人姓名', '负责人', '经办人', '联系人名称',
                '法人', '法定代表人', '代表人'
            ],
            'contact_phone': [
                '联系人电话', '手机', '手机号', '移动电话', '联系方式',
                '联系人手机', '手机号码', '电话号码', '联系电话', '电话',
                '手机号：', '联系人手机号', '移动号码', '手机：'
            ],
            'mail_address': [
                '邮寄地址', '收件地址', '快递地址', '邮件地址', '寄送地址',
                '收货地址', '通讯地址'
            ],
            'jdy_account': [
                '简道云账号', '简道云ID', 'JDY账号', 'JDY_ID', '账号ID',
                '用户ID', '客户ID', '系统账号', '简道云', 'JDY',
                '简道云用户', '简道云客户', '云账号', '平台账号'
            ]
        }
        
        # 常见分隔符
        self.separators = ['：', ':', '=', '：', '＝', '｜', '|', '\t']
        
    def preprocess_image(self, image_data: bytes):
        """
        预处理图片以提高OCR识别率

        Args:
            image_data: 图片二进制数据

        Returns:
            处理后的图片数组或原始数据
        """
        if not OCR_AVAILABLE:
            return image_data

        try:
            # 将字节数据转换为numpy数组
            nparr = np.frombuffer(image_data, np.uint8)
            # 解码图片
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if img is None:
                raise ValueError("无法解码图片")

            # 转换为灰度图
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # 应用高斯模糊减少噪声
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)

            # 自适应阈值处理
            thresh = cv2.adaptiveThreshold(
                blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY, 11, 2
            )

            # 形态学操作去除噪声
            kernel = np.ones((1, 1), np.uint8)
            processed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

            return processed

        except Exception as e:
            logger.error(f"图片预处理失败: {str(e)}")
            # 如果预处理失败，返回原始数据
            return image_data
    
    def extract_text_from_image(self, image_data: bytes) -> str:
        """
        从图片中提取文本

        Args:
            image_data: 图片二进制数据

        Returns:
            提取的文本内容
        """
        if not OCR_AVAILABLE:
            logger.warning("OCR库未安装，使用演示模式。请安装 pytesseract, pillow, opencv-python 以启用真实OCR功能")
            # 返回空字符串，让用户知道OCR不可用
            return ""

        # 检查Tesseract是否可用
        try:
            # 测试Tesseract是否安装
            pytesseract.get_tesseract_version()
        except Exception as e:
            logger.error(f"Tesseract OCR引擎不可用: {str(e)}")
            # 尝试使用在线OCR服务
            logger.info("尝试使用在线OCR服务...")
            return self._try_online_ocr(image_data)

        try:
            # 预处理图片
            processed_img = self.preprocess_image(image_data)

            if processed_img is None:
                raise ValueError("图片处理失败")

            # 配置Tesseract参数
            custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz一二三四五六七八九十百千万亿零壹贰叁肆伍陆柒捌玖拾佰仟萬億〇（）()【】[]{}《》<>""''：:；;，,。.？?！!、\|/\\-_=+*&%$#@^~`'

            # 使用Tesseract进行OCR识别
            # 尝试中英文混合识别
            text = pytesseract.image_to_string(
                processed_img,
                lang='chi_sim+eng',  # 中文简体+英文
                config=custom_config
            )

            # 清理文本
            text = self._clean_text(text)

            logger.info(f"OCR识别完成，提取文本长度: {len(text)}")
            return text

        except Exception as e:
            logger.error(f"OCR文本提取失败: {str(e)}")
            return ""

    def _try_online_ocr(self, image_data: bytes) -> str:
        """
        尝试使用在线OCR服务

        Args:
            image_data: 图片二进制数据

        Returns:
            提取的文本内容
        """
        try:
            # 使用免费的OCR.space API
            # 注意：这是一个演示用的免费服务，有使用限制

            # 将图片转换为base64
            import base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')

            # 准备API请求
            url = 'https://api.ocr.space/parse/image'
            payload = {
                'base64Image': f'data:image/png;base64,{image_base64}',
                'language': 'chs',  # 中文简体
                'isOverlayRequired': False,
                'apikey': 'helloworld',  # 免费API密钥
                'OCREngine': 2
            }

            # 发送请求
            response = requests.post(url, data=payload, timeout=30)

            if response.status_code == 200:
                result = response.json()

                if result.get('IsErroredOnProcessing', True):
                    logger.error(f"在线OCR处理失败: {result.get('ErrorMessage', '未知错误')}")
                    return ""

                # 提取文本
                text_results = result.get('ParsedResults', [])
                if text_results:
                    extracted_text = text_results[0].get('ParsedText', '')
                    logger.info(f"在线OCR识别成功，提取文本长度: {len(extracted_text)}")
                    return extracted_text.strip()
                else:
                    logger.warning("在线OCR未识别到任何文本")
                    return ""
            else:
                logger.error(f"在线OCR API请求失败: {response.status_code}")
                return ""

        except requests.exceptions.RequestException as e:
            logger.error(f"在线OCR网络请求失败: {str(e)}")
            return ""
        except Exception as e:
            logger.error(f"在线OCR处理异常: {str(e)}")
            return ""

    def _get_demo_text(self) -> str:
        """
        获取演示用的文本（当OCR库不可用时）
        """
        return """公司名称：演示科技有限公司
税号：91330000123456789X
注册地址：浙江省杭州市西湖区演示路88号
注册电话：0571-88888888
开户行：中国演示银行杭州分行
银行账号：1234567890123456789
联系人：张演示
联系电话：13800138000
邮寄地址：浙江省杭州市西湖区演示路88号
简道云账号：demo12345678abcdefghijklmnop"""
    
    def _clean_text(self, text: str) -> str:
        """
        清理OCR识别的文本
        
        Args:
            text: 原始文本
            
        Returns:
            清理后的文本
        """
        if not text:
            return ""
        
        # 移除多余的空白字符
        text = re.sub(r'\s+', ' ', text)
        
        # 移除特殊字符但保留中文标点
        text = re.sub(r'[^\w\s\u4e00-\u9fff：:=（）()【】\[\]{}《》<>""''；;，,。.？?！!\|/\\-_+*&%$#@^~`]', '', text)
        
        # 修复常见OCR错误
        replacements = {
            '0': 'O',  # 数字0可能被识别为字母O
            'l': '1',  # 字母l可能被识别为数字1
            'S': '5',  # 字母S可能被识别为数字5
        }
        
        # 只在特定上下文中进行替换
        for old, new in replacements.items():
            # 在数字上下文中进行替换
            text = re.sub(f'(?<=\d){old}(?=\d)', new, text)
        
        return text.strip()
    
    def parse_text_to_fields(self, text: str) -> Dict[str, str]:
        """
        解析文本并映射到表单字段

        Args:
            text: OCR识别的文本

        Returns:
            字段映射字典
        """
        result = {}

        if not text:
            return result

        # 按行分割文本
        lines = text.split('\n')

        # 处理每一行
        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 尝试不同的分隔符
            for separator in self.separators:
                if separator in line:
                    parts = line.split(separator, 1)  # 只分割第一个分隔符
                    if len(parts) == 2:
                        key = parts[0].strip()
                        value = parts[1].strip()

                        if key and value:
                            # 查找匹配的字段
                            field_name = self._find_matching_field(key)
                            if field_name:
                                # 对特定字段进行值的清理和验证
                                cleaned_value = self._clean_field_value(field_name, value)
                                if cleaned_value:
                                    result[field_name] = cleaned_value
                                    logger.info(f"字段匹配成功: {key} -> {field_name} = {cleaned_value}")
                    break

        # 如果没有找到某些关键字段，尝试使用正则表达式进行模式匹配
        result = self._pattern_match_fields(text, result)

        return result
    
    def _find_matching_field(self, key: str) -> Optional[str]:
        """
        查找匹配的字段名
        
        Args:
            key: 待匹配的键名
            
        Returns:
            匹配的字段名，如果没有匹配则返回None
        """
        key = key.strip()
        
        # 精确匹配
        for field_name, patterns in self.field_mapping.items():
            if key in patterns:
                return field_name
        
        # 模糊匹配
        for field_name, patterns in self.field_mapping.items():
            for pattern in patterns:
                if pattern in key or key in pattern:
                    return field_name
        
        return None

    def _clean_field_value(self, field_name: str, value: str) -> str:
        """
        清理和验证字段值

        Args:
            field_name: 字段名
            value: 原始值

        Returns:
            清理后的值
        """
        value = value.strip()

        # 移除常见的无用字符
        value = re.sub(r'^[：:=\s]+|[：:=\s]+$', '', value)

        if field_name == 'contact_phone':
            # 电话号码清理：保留数字、+、-、空格、()
            value = re.sub(r'[^\d+\-\s()]', '', value)
            # 移除多余的空格
            value = re.sub(r'\s+', ' ', value).strip()
            # 验证电话号码格式（至少7位数字）
            if not re.search(r'\d{7,}', value):
                return ""

        elif field_name == 'bank_account':
            # 银行账号清理：只保留数字和空格
            value = re.sub(r'[^\d\s]', '', value)
            # 移除空格
            value = re.sub(r'\s+', '', value)
            # 验证账号长度（至少10位数字）
            if not re.match(r'^\d{10,}$', value):
                return ""

        elif field_name == 'jdy_account':
            # 简道云账号清理：保留字母、数字、下划线
            value = re.sub(r'[^\w]', '', value)
            # 验证账号格式（至少3位字符）
            if len(value) < 3:
                return ""

        return value

    def _pattern_match_fields(self, text: str, existing_result: Dict[str, str]) -> Dict[str, str]:
        """
        使用正则表达式模式匹配字段

        Args:
            text: 完整文本
            existing_result: 已有的解析结果

        Returns:
            更新后的结果字典
        """
        result = existing_result.copy()

        # 如果还没有找到联系电话，尝试模式匹配
        if 'contact_phone' not in result:
            # 匹配手机号模式：1开头的11位数字
            phone_pattern = r'1[3-9]\d{9}'
            phone_match = re.search(phone_pattern, text)
            if phone_match:
                result['contact_phone'] = phone_match.group()
                logger.info(f"模式匹配手机号: {phone_match.group()}")

        # 如果还没有找到银行账号，尝试模式匹配
        if 'bank_account' not in result:
            # 匹配银行账号模式：10-25位数字
            account_pattern = r'\b\d{10,25}\b'
            account_matches = re.findall(account_pattern, text)
            if account_matches:
                # 选择最长的数字串作为账号
                longest_account = max(account_matches, key=len)
                result['bank_account'] = longest_account
                logger.info(f"模式匹配银行账号: {longest_account}")

        # 如果还没有找到简道云账号，尝试模式匹配
        if 'jdy_account' not in result:
            # 匹配简道云账号模式：字母数字组合，长度3-50
            jdy_pattern = r'\b[a-zA-Z0-9]{3,50}\b'
            jdy_matches = re.findall(jdy_pattern, text)
            if jdy_matches:
                # 过滤掉纯数字（可能是其他字段）
                for match in jdy_matches:
                    if not match.isdigit() and len(match) >= 5:
                        result['jdy_account'] = match
                        logger.info(f"模式匹配简道云账号: {match}")
                        break

        return result
    
    def process_image(self, image_data: bytes) -> Dict[str, any]:
        """
        处理图片的主要方法

        Args:
            image_data: 图片二进制数据

        Returns:
            处理结果字典
        """
        try:
            # 检查OCR是否可用
            if not OCR_AVAILABLE:
                # 尝试使用简化版本
                if self.simple_ocr:
                    return self.simple_ocr.process_image(image_data)
                else:
                    return {
                        'success': False,
                        'error': 'OCR功能不可用。请安装必要的依赖包：\n\npip install pytesseract pillow opencv-python\nbrew install tesseract tesseract-lang\n\n然后重启应用。',
                        'extracted_text': '',
                        'parsed_fields': {},
                        'field_count': 0,
                        'ocr_available': False
                    }

            # 检查Tesseract引擎是否可用
            try:
                pytesseract.get_tesseract_version()
                # Tesseract可用，使用本地OCR
                extracted_text = self.extract_text_from_image(image_data)
            except Exception as e:
                logger.error(f"Tesseract OCR引擎不可用: {str(e)}")
                logger.info("尝试使用在线OCR服务...")
                # 尝试使用在线OCR服务
                extracted_text = self._try_online_ocr(image_data)

                if not extracted_text:
                    return {
                        'success': False,
                        'error': f'OCR识别失败。Tesseract不可用且在线OCR服务也失败。\n\n请安装Tesseract OCR引擎：\n\n方案1（推荐）：\nbrew install tesseract tesseract-lang\n\n方案2：\nconda install -c conda-forge tesseract\n\n安装完成后重启应用。',
                        'extracted_text': '',
                        'parsed_fields': {},
                        'field_count': 0,
                        'ocr_available': True,
                        'tesseract_available': False
                    }

            # 解析字段
            parsed_fields = self.parse_text_to_fields(extracted_text)

            return {
                'success': True,
                'extracted_text': extracted_text,
                'parsed_fields': parsed_fields,
                'field_count': len(parsed_fields),
                'ocr_available': True
            }

        except Exception as e:
            logger.error(f"图片处理失败: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'extracted_text': '',
                'parsed_fields': {},
                'field_count': 0,
                'ocr_available': OCR_AVAILABLE
            }
