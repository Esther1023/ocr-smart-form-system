#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最小化Flask应用 - 用于测试Railway部署
"""

import os
from datetime import datetime
from flask import Flask, jsonify, render_template

# 创建Flask应用
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key')

@app.route('/')
def index():
    """主页"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>OCR智能表单系统</title>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .container { max-width: 800px; margin: 0 auto; }
            .status { padding: 20px; background: #e8f5e8; border-radius: 8px; }
            .info { margin: 20px 0; padding: 15px; background: #f0f8ff; border-radius: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🖼️ OCR智能表单系统</h1>
            <div class="status">
                <h2>✅ 部署成功！</h2>
                <p>您的OCR智能表单系统已成功部署到Railway平台。</p>
            </div>
            
            <div class="info">
                <h3>📋 系统信息</h3>
                <ul>
                    <li><strong>状态</strong>: 运行中</li>
                    <li><strong>环境</strong>: """ + os.environ.get('FLASK_ENV', 'development') + """</li>
                    <li><strong>时间</strong>: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</li>
                    <li><strong>版本</strong>: 1.0.0</li>
                </ul>
            </div>
            
            <div class="info">
                <h3>🔗 API端点</h3>
                <ul>
                    <li><a href="/health">健康检查</a> - /health</li>
                    <li><a href="/test">测试端点</a> - /test</li>
                </ul>
            </div>
            
            <div class="info">
                <h3>🚀 下一步</h3>
                <p>基础部署已完成，OCR功能正在配置中...</p>
            </div>
        </div>
    </body>
    </html>
    """

@app.route('/health')
def health_check():
    """健康检查端点"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'environment': os.environ.get('FLASK_ENV', 'development'),
        'port': os.environ.get('PORT', 'not-set')
    })

@app.route('/test')
def test():
    """测试端点"""
    return jsonify({
        'message': 'Railway部署测试成功！',
        'timestamp': datetime.now().isoformat(),
        'environment_vars': {
            'FLASK_ENV': os.environ.get('FLASK_ENV'),
            'PORT': os.environ.get('PORT'),
            'SECRET_KEY': '***' if os.environ.get('SECRET_KEY') else 'not-set'
        }
    })

if __name__ == '__main__':
    # 环境配置
    port = int(os.environ.get('PORT', 8080))
    debug = os.environ.get('FLASK_ENV') != 'production'
    
    print(f"启动Flask应用...")
    print(f"端口: {port}")
    print(f"环境: {os.environ.get('FLASK_ENV', 'development')}")
    print(f"调试模式: {debug}")
    
    app.run(debug=debug, port=port, host='0.0.0.0')
