from flask import Flask, render_template, request, send_file, jsonify, redirect, url_for, session
from template_handler import TemplateHandler
import os
import tempfile
import pandas as pd
from datetime import datetime
import logging

# 设置日志记录
log_dir = 'logs'
log_file = os.path.join(log_dir, 'app.log')
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # 用于会话加密

# 存储最后导入时间
last_import_time = None

# 添加安全头
@app.after_request
def add_security_headers(response):
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'"
    return response

# 登录页面
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == 'admin' and password == 'password':  # 简单的用户名密码验证
            session['logged_in'] = True
            return redirect(url_for('index'))
        return render_template('login.html', error='用户名或密码错误')
    return render_template('login.html')

# 登出功能
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

# 登录保护装饰器
def login_required(func):
    def wrapper(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

# 加载Excel数据
def load_customer_data():
    global last_import_time
    excel_path = '十大战区公有云客户续费清单_20250307014553.xlsx'
    try:
        if not os.path.exists(excel_path):
            logger.error(f"文件不存在: {excel_path}")
            return None
        df = pd.read_excel(excel_path)
        return df
    except Exception as e:
        logger.error(f"Excel加载错误: {str(e)}")
        return None

@app.route('/')
@login_required
def index():
    return render_template('index.html', last_import_time=last_import_time)

@app.route('/test', methods=['GET'])
def test():
    return 'Hello, World!'
@app.route('/upload_excel', methods=['POST'])
@login_required
def upload_excel():
    global last_import_time
    try:
        if 'file' not in request.files:
            return jsonify({'error': '没有上传文件'}), 400
            
        file = request.files['file']
        if not file or not file.filename:
            return jsonify({'error': '没有选择文件'}), 400
            
        if not file.filename.endswith('.xlsx'):
            return jsonify({'error': '请上传Excel文件(.xlsx)'}), 400

        # 保存文件
        file.save('十大战区公有云客户续费清单_20250307014553.xlsx')
        
        # 更新导入时间
        last_import_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        return jsonify({
            'message': '文件上传成功',
            'last_import_time': last_import_time
        })
        
    except Exception as e:
        logger.error(f"文件上传失败: {str(e)}")
        return jsonify({'error': f'文件上传失败: {str(e)}'}), 500

@app.route('/get_last_import_time')
def get_last_import_time():
    return jsonify({'last_import_time': last_import_time})

@app.route('/query_customer', methods=['POST'])
@login_required
def query_customer():
    try:
        if not request.json or 'jdy_id' not in request.json:
            return jsonify({'error': '请提供简道云账号'}), 400
            
        jdy_id = request.json['jdy_id']
        if not jdy_id:
            return jsonify({'error': '请提供简道云账号'}), 400

        df = load_customer_data()
        if df is None:
            return jsonify({'error': '数据加载失败'}), 500

        # 查找匹配的客户
        matching_rows = df[df['简道云账号'] == jdy_id]
        if matching_rows.empty:
            return jsonify({'error': '未找到客户信息'}), 404

        customer_data = matching_rows.iloc[0]
        
        # 打印客户数据以便调试
        logger.info(f"客户数据: {customer_data}")
        logger.info(f"列名: {df.columns.tolist()}")
        
        # 处理日期
        expiry_date = ''
        if '版本到期时间' in customer_data and pd.notna(customer_data['版本到期时间']):
            expiry_date = pd.to_datetime(customer_data['版本到期时间']).strftime('%Y年%m月%d日')
        
        # 构建响应
        response = {
            'company_name': str(customer_data.get('公司名称', '')),
            'customer_type': str(customer_data.get('客户类型', '')),
            'version': str(customer_data.get('版本', '')),
            'expiry_date': expiry_date,
            'uid_arr': f"{str(customer_data.get('UID-ARR', '0'))}元",
        }

        # 根据条件判断续费责任销售
        arr_str = str(customer_data.get('UID-ARR', '0')).replace(',', '')
        arr = float(arr_str) if arr_str.replace('.', '').isdigit() else 0
        sales = str(customer_data.get('续费责任销售', ''))
        response['sales'] = sales or 'Esther.Zhu'

        return jsonify(response)

    except Exception as e:
        logger.error(f"查询出错: {str(e)}")
        return jsonify({'error': f'查询出错: {str(e)}'}), 500

@app.route('/docx_templates/<template_name>')
def get_template(template_name):
    if not template_name.endswith('.docx'):
        return '不支持的文件类型', 400

    try:
        # 从docx_templates目录加载模板文件
        template_path = os.path.join(os.getcwd(), 'templates', 'docx_templates', template_name)
        if not os.path.exists(template_path):
            logger.error(f"模板文件不存在: {template_path}")
            return '模板文件不存在', 404

        logger.info(f"正在加载模板文件: {template_path}")
        return send_file(
            template_path,
            as_attachment=False,  # 不作为附件发送，这样浏览器不会下载而是直接传给前端
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
    except Exception as e:
        logger.error(f"模板文件访问错误: {str(e)}")
        return '模板文件访问错误', 500

@app.route('/generate', methods=['POST'])
@login_required
def generate():
    temp_template = None
    temp_output = None
    
    try:
        logger.info("开始处理文件上传请求")
        
        # 检查是否有文件上传
        if 'template' not in request.files:
            logger.error("请求中没有找到文件")
            return '请选择合同模板文件', 400
            
        template_file = request.files['template']
        if not template_file or not template_file.filename:
            logger.error("没有选择文件")
            return '请选择合同模板文件', 400
            
        if not template_file.filename.endswith('.docx'):
            logger.error("文件格式不正确")
            return '请选择.docx格式的文件', 400

        logger.info(f"接收到文件: {template_file.filename}")

        # 创建临时文件保存上传的模板
        temp_template = tempfile.NamedTemporaryFile(suffix='.docx', delete=False)
        template_file.save(temp_template.name)
        logger.info(f"模板文件已保存到临时文件: {temp_template.name}")
        
        # 获取表单数据
        form_data = request.form.to_dict()
        
        # 处理多选值
        contract_types = request.form.getlist('contract_type')
        if contract_types:
            form_data['contract_types'] = ', '.join(contract_types)
        
        logger.info(f"接收到的表单数据: {form_data}")
        
        # 创建临时文件用于保存生成的合同
        temp_output = tempfile.NamedTemporaryFile(suffix='.docx', delete=False)
        logger.info(f"创建输出临时文件: {temp_output.name}")

        # 处理模板
        handler = TemplateHandler(temp_template.name)
        output_path = handler.process_template(form_data, temp_output.name)
        logger.info(f"合同生成完成，输出文件: {output_path}")

        # 返回生成的文件
        return send_file(
            output_path,
            as_attachment=True,
            download_name=f"{form_data['start_year']}-{form_data['end_year']}+{form_data['company_name']}+帆软简道云续费合同+{datetime.now().strftime('%Y%m%d')}.docx",
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )

    except Exception as e:
        logger.error(f"发生错误: {str(e)}")
        return f'生成合同时发生错误: {str(e)}', 500

    finally:
        # 清理临时文件
        try:
            if temp_template:
                os.unlink(temp_template.name)
                logger.info(f"清理临时模板文件: {temp_template.name}")
            if temp_output:
                os.unlink(temp_output.name)
                logger.info(f"清理临时输出文件: {temp_output.name}")
        except Exception as e:
            logger.error(f"清理临时文件时发生错误: {str(e)}")

if __name__ == '__main__':
    app.run(debug=True, port=5001,host='0.0.0.0')
