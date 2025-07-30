from flask import Flask, render_template, request, send_file, jsonify, redirect, url_for, session
from template_handler import TemplateHandler
from ocr_service import OCRService
from config import config
import os
import tempfile
import pandas as pd
from datetime import datetime
import logging

# 获取环境配置
env = os.environ.get('FLASK_ENV', 'development')
app_config = config.get(env, config['default'])

# 创建Flask应用
app = Flask(__name__)
app.config.from_object(app_config)

# 设置日志记录
log_dir = 'logs'
if not os.path.exists(log_dir):
    os.makedirs(log_dir, exist_ok=True)

# 生产环境使用不同的日志配置
if env == 'production':
    logging.basicConfig(
        level=getattr(logging, app.config['LOG_LEVEL']),
        format='%(asctime)s %(levelname)s: %(message)s'
    )
else:
    log_file = os.path.join(log_dir, 'app.log')
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format='%(asctime)s %(levelname)s: %(message)s'
    )

logger = logging.getLogger(__name__)

# 初始化OCR服务（容错处理）
try:
    ocr_service = OCRService()
    logger.info("OCR服务初始化成功")
except Exception as e:
    logger.warning(f"OCR服务初始化失败: {str(e)}")
    ocr_service = None

# 存储最后导入时间
last_import_time = None

# 健康检查端点
@app.route('/health')
def health_check():
    """健康检查端点，用于监控服务状态"""
    try:
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0',
            'environment': os.environ.get('FLASK_ENV', 'development'),
            'services': {
                'flask': 'available',
                'template_handler': 'available'
            }
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# 添加安全头
@app.after_request
def add_security_headers(response):
    if app.config.get('DEBUG'):
        # 开发环境使用宽松的CSP
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'"
    else:
        # 生产环境使用更严格的安全头
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
    return response

# 登录页面
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if (username == 'Esther' and password == '967420') or (username == 'Mia' and password == '123456'):  # 简单的用户名密码验证
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
    excel_path = '六大战区简道云客户.xlsx'
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
        file.save('六大战区简道云客户.xlsx')
        
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

@app.route('/get_future_expiring_customers')
@login_required
def get_future_expiring_customers():
    try:
        # 检查文件是否存在
        excel_path = os.path.join(os.path.dirname(__file__), '六大战区简道云客户.xlsx')
        logger.info(f"尝试读取文件: {excel_path}")
        if not os.path.exists(excel_path):
            logger.error(f"文件不存在: {excel_path}")
            return jsonify({'error': '数据文件不存在'}), 500

        try:
            df = pd.read_excel(excel_path)
            logger.info(f"成功读取Excel文件，共{len(df)}行数据")
        except Exception as e:
            logger.error(f"Excel读取错误: {str(e)}")
            return jsonify({'error': '数据文件读取失败'}), 500

        if '版本到期时间' not in df.columns or '简道云账号' not in df.columns or '公司名称' not in df.columns or '续费责任销售' not in df.columns:
            logger.error("Excel文件中缺少必要列")
            return jsonify({'error': '数据格式错误：缺少必要列'}), 500
        
        # 获取当前日期
        now = datetime.now()
        
        # 计算23天后和30天后的日期
        days_23_later = now + pd.Timedelta(days=23)
        days_30_later = now + pd.Timedelta(days=30)
        
        # 筛选出23-30天内将要过期的客户
        esther_customers = []
        other_customers = []
        
        for _, row in df.iterrows():
            if pd.notna(row['版本到期时间']):
                try:
                    expiry_date = pd.to_datetime(row['版本到期时间'])
                    # 如果过期时间在23天后和30天后之间
                    if days_23_later <= expiry_date <= days_30_later:
                        customer_info = {
                            'id': str(row.get('ID', '')),
                            'expiry_date': expiry_date.strftime('%Y年%m月%d日'),
                            'jdy_account': str(row.get('简道云账号', '')),
                            'company_name': str(row.get('公司名称', '')),
                            'sales_person': str(row.get('续费责任销售', ''))
                        }
                        
                        # 根据续费责任销售分类
                        if '朱晓琳' in str(row.get('续费责任销售', '')) or 'Esther' in str(row.get('续费责任销售', '')):
                            esther_customers.append(customer_info)
                        else:
                            other_customers.append(customer_info)
                            
                except Exception as e:
                    logger.warning(f"日期转换错误: {str(e)}")
                    continue
        
        # 按过期日期排序
        esther_customers.sort(key=lambda x: x['expiry_date'])
        other_customers.sort(key=lambda x: x['expiry_date'])
        
        logger.info(f"找到{len(esther_customers)}个Esther负责的即将过期客户和{len(other_customers)}个其他销售负责的即将过期客户")
        return jsonify({
            'esther_customers': esther_customers,
            'other_customers': other_customers
        })

    except Exception as e:
        logger.error(f"获取未来即将过期客户失败: {str(e)}")
        return jsonify({'error': f'获取未来即将过期客户失败: {str(e)}'}), 500

@app.route('/get_expiring_customers')
@login_required
def get_expiring_customers():
    try:
        # 检查文件是否存在
        excel_path = os.path.join(os.path.dirname(__file__), '六大战区简道云客户.xlsx')
        logger.info(f"尝试读取文件: {excel_path}")
        if not os.path.exists(excel_path):
            logger.error(f"文件不存在: {excel_path}")
            return jsonify({'error': '数据文件不存在'}), 500

        try:
            df = pd.read_excel(excel_path)
            logger.info(f"成功读取Excel文件，共{len(df)}行数据")
        except Exception as e:
            logger.error(f"Excel读取错误: {str(e)}")
            return jsonify({'error': '数据文件读取失败'}), 500

        if '版本到期时间' not in df.columns or '简道云账号' not in df.columns or '公司名称' not in df.columns:
            logger.error("Excel文件中缺少必要列")
            return jsonify({'error': '数据格式错误：缺少必要列'}), 500
        
        # 获取当前日期
        now = datetime.now()
        
        # 计算一周后的日期
        one_week_later = now + pd.Timedelta(days=7)
        
        # 筛选出一周内将要过期的客户
        expiring_customers = []
        for _, row in df.iterrows():
            if pd.notna(row['版本到期时间']):
                try:
                    expiry_date = pd.to_datetime(row['版本到期时间'])
                    # 如果过期时间在当前日期和一周后之间
                    if now <= expiry_date <= one_week_later:
                        expiring_customers.append({
                            'expiry_date': expiry_date.strftime('%Y年%m月%d日'),
                            'jdy_account': str(row.get('简道云账号', '')),
                            'company_name': str(row.get('公司名称', '')),
                            'sales_person': str(row.get('续费责任销售', ''))
                        })
                except Exception as e:
                    logger.warning(f"日期转换错误: {str(e)}")
                    continue
        
        # 按过期日期排序
        expiring_customers.sort(key=lambda x: x['expiry_date'])
        
        logger.info(f"找到{len(expiring_customers)}个即将过期的客户")
        return jsonify({'expiring_customers': expiring_customers})

    except Exception as e:
        logger.error(f"获取即将过期客户失败: {str(e)}")
        return jsonify({'error': f'获取即将过期客户失败: {str(e)}'}), 500

@app.route('/query_customer', methods=['POST'])
@login_required
def query_customer():
    try:
        if not request.json or ('jdy_id' not in request.json and 'company_name' not in request.json):
            logger.warning("请求中缺少查询参数")
            return jsonify({'error': '请提供简道云账号或公司名称'}), 400
            
        # 获取查询参数
        jdy_id = request.json.get('jdy_id', '')
        company_name = request.json.get('company_name', '')
        
        # 记录查询参数
        if jdy_id:
            logger.info(f"开始通过简道云账号查询: {jdy_id}")
        if company_name:
            logger.info(f"开始通过公司名称查询: {company_name}")
        
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

        # 检查必要的列是否存在
        required_columns = ['简道云账号', '公司名称']
        for col in required_columns:
            if col not in df.columns:
                logger.error(f"Excel文件中缺少'{col}'列")
                return jsonify({'error': f'数据格式错误：缺少{col}列'}), 500
        
        # 根据查询条件进行模糊匹配
        if jdy_id:
            matching_rows = df[df['简道云账号'].astype(str).str.contains(str(jdy_id), case=False, na=False)]
        else:
            matching_rows = df[df['公司名称'].astype(str).str.contains(str(company_name), case=False, na=False)]
            
        if matching_rows.empty:
            query_type = "简道云账号" if jdy_id else "公司名称"
            query_value = jdy_id if jdy_id else company_name
            logger.info(f"未找到匹配的客户信息，查询{query_type}: {query_value}")
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

@app.route('/ocr_process', methods=['POST'])
def ocr_process():
    """处理OCR图片识别请求"""
    try:
        # 检查OCR服务是否可用
        if ocr_service is None:
            return jsonify({
                'success': False,
                'error': 'OCR服务暂时不可用，请稍后再试'
            }), 503

        # 检查是否有文件上传
        if 'image' not in request.files:
            return jsonify({'success': False, 'error': '没有上传图片文件'}), 400

        file = request.files['image']
        if file.filename == '':
            return jsonify({'success': False, 'error': '没有选择文件'}), 400

        # 检查文件类型
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'webp'}
        file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''

        if file_ext not in allowed_extensions:
            return jsonify({'success': False, 'error': '不支持的文件格式'}), 400

        # 读取图片数据
        image_data = file.read()

        # 检查文件大小（限制为10MB）
        if len(image_data) > 10 * 1024 * 1024:
            return jsonify({'success': False, 'error': '文件大小超过限制（10MB）'}), 400

        logger.info(f"开始处理OCR请求，文件大小: {len(image_data)} bytes")

        # 使用OCR服务处理图片
        result = ocr_service.process_image(image_data)

        if result['success']:
            logger.info(f"OCR处理成功，识别到 {result['field_count']} 个字段")
            return jsonify(result)
        else:
            logger.error(f"OCR处理失败: {result.get('error', '未知错误')}")
            # 对于OCR不可用的情况，返回200状态码但success=False
            # 这样前端可以正确处理错误信息
            return jsonify(result), 200

    except Exception as e:
        logger.error(f"OCR处理异常: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'服务器处理错误: {str(e)}',
            'extracted_text': '',
            'parsed_fields': {},
            'field_count': 0
        }), 500

if __name__ == '__main__':
    # 环境配置
    port = int(os.environ.get('PORT', 5001))
    # 生产环境使用0.0.0.0，开发环境使用localhost
    if os.environ.get('FLASK_ENV') == 'production':
        host = '0.0.0.0'
    else:
        host = os.environ.get('HOST', 'localhost')
    debug = os.environ.get('FLASK_ENV') != 'production'

    app.run(debug=debug, port=port, host=host)
