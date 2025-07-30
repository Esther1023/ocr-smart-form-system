#!/usr/bin/env python3
"""
部署准备检查脚本
检查项目是否已准备好部署到生产环境
"""

import os
import sys
import json
from pathlib import Path

class DeploymentChecker:
    def __init__(self):
        self.project_root = Path.cwd()
        self.issues = []
        self.warnings = []
    
    def check_required_files(self):
        """检查必需的文件"""
        print("📋 检查必需文件...")
        
        required_files = [
            'app.py',
            'requirements.txt',
            'Procfile',
            'config.py',
            'runtime.txt',
            'aptfile'
        ]
        
        for file_name in required_files:
            file_path = self.project_root / file_name
            if file_path.exists():
                print(f"✅ {file_name}")
            else:
                self.issues.append(f"缺少必需文件: {file_name}")
                print(f"❌ {file_name}")
    
    def check_requirements(self):
        """检查requirements.txt"""
        print("\n📦 检查依赖配置...")
        
        req_file = self.project_root / 'requirements.txt'
        if not req_file.exists():
            self.issues.append("缺少requirements.txt文件")
            return
        
        with open(req_file, 'r') as f:
            content = f.read()
        
        # 检查关键依赖
        required_packages = [
            'Flask',
            'gunicorn',
            'pytesseract',
            'Pillow',
            'opencv-python-headless'
        ]
        
        for package in required_packages:
            if package.lower() in content.lower():
                print(f"✅ {package}")
            else:
                self.issues.append(f"缺少关键依赖: {package}")
                print(f"❌ {package}")
        
        # 检查是否使用了headless版本的opencv
        if 'opencv-python-headless' in content:
            print("✅ 使用opencv-python-headless（适合服务器环境）")
        elif 'opencv-python' in content:
            self.warnings.append("建议使用opencv-python-headless替代opencv-python")
    
    def check_app_config(self):
        """检查应用配置"""
        print("\n⚙️ 检查应用配置...")
        
        app_file = self.project_root / 'app.py'
        if not app_file.exists():
            self.issues.append("缺少app.py文件")
            return
        
        with open(app_file, 'r') as f:
            content = f.read()
        
        # 检查生产环境配置
        if 'config' in content and 'from config import' in content:
            print("✅ 使用配置文件")
        else:
            self.warnings.append("建议使用配置文件管理环境设置")
        
        # 检查是否有硬编码的debug=True
        if 'debug=True' in content and 'os.environ.get' not in content:
            self.warnings.append("发现硬编码的debug=True，建议使用环境变量控制")
        
        # 检查密钥配置
        if 'your_secret_key' in content or 'your-secret-key' in content:
            self.warnings.append("发现默认密钥，部署时必须更改SECRET_KEY")
    
    def check_procfile(self):
        """检查Procfile配置"""
        print("\n🚀 检查Procfile...")
        
        procfile = self.project_root / 'Procfile'
        if not procfile.exists():
            self.issues.append("缺少Procfile文件")
            return
        
        with open(procfile, 'r') as f:
            content = f.read().strip()
        
        if 'gunicorn' in content and 'app:app' in content:
            print("✅ Procfile配置正确")
        else:
            self.issues.append("Procfile配置可能有误")
            print(f"当前内容: {content}")
    
    def check_docker_config(self):
        """检查Docker配置"""
        print("\n🐳 检查Docker配置...")
        
        dockerfile = self.project_root / 'Dockerfile'
        if dockerfile.exists():
            with open(dockerfile, 'r') as f:
                content = f.read()
            
            if 'tesseract-ocr' in content:
                print("✅ Dockerfile包含OCR依赖")
            else:
                self.warnings.append("Dockerfile可能缺少OCR系统依赖")
            
            if 'gunicorn' in content:
                print("✅ Dockerfile使用gunicorn")
            else:
                self.warnings.append("Dockerfile建议使用gunicorn作为WSGI服务器")
        else:
            print("ℹ️ 未找到Dockerfile（可选）")
    
    def check_security(self):
        """检查安全配置"""
        print("\n🔒 检查安全配置...")
        
        # 检查.env文件是否被忽略
        gitignore = self.project_root / '.gitignore'
        if gitignore.exists():
            with open(gitignore, 'r') as f:
                content = f.read()
            
            if '.env' in content:
                print("✅ .env文件已被git忽略")
            else:
                self.warnings.append("建议在.gitignore中添加.env文件")
        
        # 检查是否有.env文件在仓库中
        env_file = self.project_root / '.env'
        if env_file.exists():
            self.warnings.append("发现.env文件，确保不要提交到git仓库")
    
    def check_file_structure(self):
        """检查文件结构"""
        print("\n📁 检查项目结构...")
        
        expected_dirs = ['static', 'templates']
        for dir_name in expected_dirs:
            dir_path = self.project_root / dir_name
            if dir_path.exists() and dir_path.is_dir():
                print(f"✅ {dir_name}/")
            else:
                self.issues.append(f"缺少目录: {dir_name}/")
        
        # 检查关键文件
        key_files = [
            'static/style.css',
            'static/script.js',
            'templates/index.html'
        ]
        
        for file_path in key_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                print(f"✅ {file_path}")
            else:
                self.issues.append(f"缺少文件: {file_path}")
    
    def generate_report(self):
        """生成检查报告"""
        print("\n" + "="*60)
        print("📊 部署准备检查报告")
        print("="*60)
        
        if not self.issues and not self.warnings:
            print("🎉 恭喜！项目已准备好部署到生产环境！")
            print("\n📝 下一步:")
            print("1. 将代码推送到Git仓库")
            print("2. 在部署平台创建新项目")
            print("3. 设置环境变量（特别是SECRET_KEY）")
            print("4. 部署并测试")
            return True
        
        if self.issues:
            print(f"\n❌ 发现 {len(self.issues)} 个问题需要修复:")
            for i, issue in enumerate(self.issues, 1):
                print(f"   {i}. {issue}")
        
        if self.warnings:
            print(f"\n⚠️ 发现 {len(self.warnings)} 个警告:")
            for i, warning in enumerate(self.warnings, 1):
                print(f"   {i}. {warning}")
        
        print(f"\n📋 总结:")
        print(f"   - 问题: {len(self.issues)} 个")
        print(f"   - 警告: {len(self.warnings)} 个")
        
        if self.issues:
            print("\n🔧 请修复所有问题后再次运行检查")
            return False
        else:
            print("\n✅ 没有严重问题，可以尝试部署（注意警告项）")
            return True
    
    def run_all_checks(self):
        """运行所有检查"""
        print("🔍 OCR系统部署准备检查")
        print("="*60)
        
        self.check_required_files()
        self.check_requirements()
        self.check_app_config()
        self.check_procfile()
        self.check_docker_config()
        self.check_security()
        self.check_file_structure()
        
        return self.generate_report()

def main():
    checker = DeploymentChecker()
    success = checker.run_all_checks()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
