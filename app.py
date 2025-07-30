from flask import Flask, render_template, request, send_file, jsonify, redirect, url_for, session
import os
import tempfile
import pandas as pd
from datetime import datetime
import logging

# 延迟导入OCR相关模块，避免启动时失败
template_handler = None
ocr_service = None

# 创建Flask应用
app = Flask(__name__)

# 简化配置
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

# 设置日志记录
log_dir = 'logs'
if not os.path.exists(log_dir):
    os.makedirs(log_dir, exist_ok=True)

# 生产环境使用不同的日志配置
env = os.environ.get('FLASK_ENV', 'development')
if env == 'production':
    logging.basicConfig(
        level=logging.INFO,
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
def init_ocr_service():
    """延迟初始化OCR服务"""
    global ocr_service
    try:
        from ocr_service import OCRService
        ocr_service = OCRService()
        logger.info("OCR服务初始化成功")
        return True
    except Exception as e:
        logger.warning(f"OCR服务初始化失败: {str(e)}")
        ocr_service = None
        return False

# 尝试初始化OCR服务，但不阻塞应用启动
init_ocr_service()

# 存储最后导入时间
last_import_time = None

# 简单测试端点
@app.route('/ping')
def ping():
    """最简单的测试端点"""
    return "pong - Railway deployment test"

# 健康检查端点
@app.route('/health')
def health_check():
    """健康检查端点，用于监控服务状态"""
    return "OK", 200

@app.route('/health-json')
def health_check_json():
    """详细健康检查端点"""
    try:
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0',
            'environment': os.environ.get('FLASK_ENV', 'development'),
            'port': os.environ.get('PORT', 'not-set'),
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
    excel_path = '战区续费_副本.xlsx'
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

        if '到期日期' not in df.columns or '简道云销售' not in df.columns or '账号-企业名称' not in df.columns or '续费责任销售' not in df.columns:
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
            if pd.notna(row['到期日期']):
                try:
                    expiry_date = pd.to_datetime(row['到期日期'])
                    # 如果过期时间在23天后和30天后之间
                    if days_23_later <= expiry_date <= days_30_later:
                        customer_info = {
                            'id': str(row.get('用户ID', '')),
                            'expiry_date': expiry_date.strftime('%Y年%m月%d日'),
                            'jdy_account': str(row.get('简道云销售', '')),
                            'company_name': str(row.get('账号-企业名称', '')),
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
        excel_path = os.path.join(os.path.dirname(__file__), '战区续费_副本.xlsx')
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

        if '到期日期' not in df.columns or '简道云销售' not in df.columns or '账号-企业名称' not in df.columns:
            logger.error("Excel文件中缺少必要列")
            return jsonify({'error': '数据格式错误：缺少必要列'}), 500
        
        # 获取当前日期
        now = datetime.now()
        
        # 计算一周后的日期
        one_week_later = now + pd.Timedelta(days=7)
        
        # 筛选出一周内将要过期的客户
        expiring_customers = []
        for _, row in df.iterrows():
            if pd.notna(row['到期日期']):
                try:
                    expiry_date = pd.to_datetime(row['到期日期'])
                    # 如果过期时间在当前日期和一周后之间
                    if now <= expiry_date <= one_week_later:
                        # 获取客户分类，过滤掉包含"name"的客户
                        customer_classification = str(row.get('客户分类', ''))
                        if 'name' in customer_classification.lower():
                            logger.info(f"过滤掉包含'name'的客户: {row.get('账号-企业名称', '')} - {customer_classification}")
                            continue

                        # 处理应续ARR
                        arr_value = row.get('应续ARR', 0)
                        try:
                            if pd.isna(arr_value) or arr_value == '' or float(str(arr_value).replace(',', '')) == 0:
                                arr_display = '0元'
                            else:
                                arr_display = f"{float(str(arr_value).replace(',', ''))}元"
                        except:
                            arr_display = '0元'

                        expiring_customers.append({
                            'company_name': str(row.get('账号-企业名称', '')),  # 显示账号-企业名称，但标签为公司名称
                            'customer_type': customer_classification,  # 客户分类作为客户类型
                            'uid_arr': arr_display,  # 应续ARR
                            'expiry_date': expiry_date.strftime('%Y年%m月%d日')  # 保留用于排序
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
        excel_path = '战区续费_副本.xlsx'
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
        required_columns = ['账号-企业名称']
        for col in required_columns:
            if col not in df.columns:
                logger.error(f"Excel文件中缺少'{col}'列")
                return jsonify({'error': f'数据格式错误：缺少{col}列'}), 500

        # 确定用户ID字段 - 检查可能的字段名
        user_id_field = None
        possible_id_fields = ['用户ID', 'ID', '简道云账号', '简道云销售', '账号ID']
        for field in possible_id_fields:
            if field in df.columns:
                user_id_field = field
                logger.info(f"使用字段 '{field}' 作为用户ID字段")
                break

        # 根据查询条件进行模糊匹配
        if jdy_id:
            if user_id_field:
                matching_rows = df[df[user_id_field].astype(str).str.contains(str(jdy_id), case=False, na=False)]
            else:
                # 如果没有找到用户ID字段，尝试在多个字段中搜索
                logger.warning("未找到明确的用户ID字段，在多个字段中搜索")
                mask = False
                search_fields = ['简道云销售', '账号-企业名称']
                for field in search_fields:
                    if field in df.columns:
                        mask = mask | df[field].astype(str).str.contains(str(jdy_id), case=False, na=False)
                matching_rows = df[mask]
        else:
            matching_rows = df[df['账号-企业名称'].astype(str).str.contains(str(company_name), case=False, na=False)]
            
        if matching_rows.empty:
            query_type = "简道云账号" if jdy_id else "公司名称"
            query_value = jdy_id if jdy_id else company_name
            logger.info(f"未找到匹配的客户信息，查询{query_type}: {query_value}")
            return jsonify({'error': '未找到客户信息'}), 404

        # 处理多条匹配记录
        results = []
        for _, customer_data in matching_rows.iterrows():
            # 处理新字段映射
            account_company_name = str(customer_data.get('账号-企业名称', ''))
            integration_mode = str(customer_data.get('集成模式', ''))
            customer_classification = str(customer_data.get('客户分类', ''))
            renewal_sales = str(customer_data.get('续费责任销售', ''))
            sales_chinese_english = str(customer_data.get('责任销售中英文', ''))
            jiandaoyun_sales = str(customer_data.get('简道云销售', ''))

            logger.info(f"处理客户数据: {jiandaoyun_sales}, 账号-企业名称: {account_company_name}, 客户分类: {customer_classification}, "
                      f"续费责任销售: {renewal_sales}, 集成模式: {integration_mode}, "
                      f"责任销售中英文: {sales_chinese_english}, 简道云销售: {jiandaoyun_sales}")
            
            # 处理到期日期
            expiry_date = ''
            if '到期日期' in customer_data and pd.notna(customer_data['到期日期']):
                try:
                    expiry_date = pd.to_datetime(customer_data['到期日期']).strftime('%Y年%m月%d日')
                    logger.info(f"到期日期: {expiry_date}")
                except Exception as e:
                    logger.warning(f"日期转换错误: {str(e)}")
                    expiry_date = ''

            # 处理应续ARR
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
                'account_company_name': account_company_name,  # 账号-企业名称
                'integration_mode': integration_mode,          # 集成模式
                'expiry_date': expiry_date,                   # 到期日期
                'uid_arr': arr_display,                       # 应续ARR
                'customer_classification': customer_classification,  # 客户分类
                'renewal_sales': renewal_sales,               # 续费责任销售
                'sales_chinese_english': sales_chinese_english,  # 责任销售中英文
                'jiandaoyun_sales': jiandaoyun_sales         # 简道云销售
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
        try:
            from template_handler import TemplateHandler
            handler = TemplateHandler(temp_template.name)
            output_path = handler.process_template(form_data, temp_output.name)
            logger.info(f"合同生成完成，输出文件: {output_path}")
        except ImportError as e:
            logger.error(f"模板处理器导入失败: {str(e)}")
            return jsonify({'success': False, 'error': '模板处理功能暂时不可用'}), 503

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
    port = int(os.environ.get('PORT', 8080))

    # 根据环境设置主机
    if os.environ.get('FLASK_ENV') == 'production':
        host = '0.0.0.0'  # 生产环境绑定所有接口
    else:
        host = 'localhost'  # 开发环境使用localhost

    debug = os.environ.get('FLASK_ENV') != 'production'

    print(f"🚀 启动Flask应用...")
    print(f"📍 端口: {port}")
    print(f"🌐 主机: {host}")
    print(f"🔧 环境: {os.environ.get('FLASK_ENV', 'development')}")
    print(f"🐛 调试模式: {debug}")

    app.run(debug=debug, port=port, host=host)
