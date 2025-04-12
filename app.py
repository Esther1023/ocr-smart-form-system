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
            logger.warning("请求中缺少jdy_id参数")
            return jsonify({'error': '请提供简道云账号'}), 400
            
        jdy_id = request.json['jdy_id']
        logger.info(f"开始查询简道云账号: {jdy_id}")
        
        # 检查文件是否存在
        excel_path = '六大战区简道云客户.xlsx'
        if not os.path.exists(excel_path):
            logger.error(f"文件不存在: {excel_path}")
            return jsonify({'error': '数据文件不存在'}), 500

        try:
            df = pd.read_excel(excel_path)
            logger.info(f"成功读取Excel文件，共{len(df)}行数据")
        except Exception as e:
            logger.error(f"Excel读取错误: {str(e)}")
            return jsonify({'error': '数据文件读取失败'}), 500

        if '简道云账号' not in df.columns:
            logger.error("Excel文件中缺少'简道云账号'列")
            return jsonify({'error': '数据格式错误：缺少简道云账号列'}), 500
        
        # 使用str.contains进行模糊匹配
        matching_rows = df[df['简道云账号'].astype(str).str.contains(str(jdy_id), case=False, na=False)]
        if matching_rows.empty:
            logger.info(f"未找到匹配的客户信息，查询ID: {jdy_id}")
            return jsonify({'error': '未找到客户信息'}), 404

        # 处理多条匹配记录
        results = []
        for _, customer_data in matching_rows.iterrows():
            # 处理版本和相关信息
            version = str(customer_data.get('版本', ''))
            company_name = str(customer_data.get('公司名称', ''))
            customer_type = str(customer_data.get('客户类型', ''))
            customer_region = str(customer_data.get('客户归属战区', ''))
            sales = str(customer_data.get('续费责任销售', ''))
            account_count = str(customer_data.get('账号数量', ''))
            paid_account_count = str(customer_data.get('付费中账号数量', ''))
            
            logger.info(f"处理客户数据: {customer_data['简道云账号']}, 公司名称: {company_name}, 客户类型: {customer_type}, "
                      f"客户归属战区: {customer_region}, 续费责任销售: {sales}, 版本: {version}, "
                      f"账号数量: {account_count}, 付费中账号数量: {paid_account_count}")
            
            # 如果是免费版，不显示到期时间和ARR
            if '免费' in version:
                expiry_date = ''
                arr_display = ''
            else:
                # 处理到期时间
                expiry_date = ''
                if '版本到期时间' in customer_data and pd.notna(customer_data['版本到期时间']):
                    try:
                        expiry_date = pd.to_datetime(customer_data['版本到期时间']).strftime('%Y年%m月%d日')
                        logger.info(f"版本到期时间: {expiry_date}")
                    except Exception as e:
                        logger.warning(f"日期转换错误: {str(e)}")
                        expiry_date = ''
                
                # 处理ARR
                try:
                    arr_value = customer_data.get('应续ARR', 0)
                    if pd.isna(arr_value) or arr_value == '' or float(str(arr_value).replace(',', '')) == 0:
                        arr_display = '0元'
                    else:
                        arr_display = f"{float(str(arr_value).replace(',', ''))}元"
                    logger.info(f"应续ARR: {arr_display}")
                except Exception as e:
                    logger.warning(f"ARR处理错误: {str(e)}")
                    arr_display = '0元'
            
            results.append({
                'company_name': str(customer_data.get('公司名称', '')),
                'customer_type': str(customer_data.get('客户类型', '')),
                'customer_region': str(customer_data.get('客户归属战区', '')),
                'sales': str(customer_data.get('续费责任销售', '')),
                'jdy_account': str(customer_data.get('简道云账号', '')),
                'expiry_date': expiry_date,
                'version': version,
                'account_count': str(customer_data.get('账号数量', '')),
                'paid_account_count': str(customer_data.get('付费中账号数量', '')),
                'uid_arr': arr_display
            })

        logger.info(f"查询成功，找到{len(results)}条匹配记录")
        return jsonify({'results': results})

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
