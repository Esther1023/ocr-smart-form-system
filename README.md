# Word合同模板处理工具
 test

一个用于处理Word合同模板的Python工具，可以根据输入的变量替换模板中的指定文本，并生成新的合同文档。

## 安装

1. 确保已安装Python 3.6+
2. 安装依赖包：
```bash
pip install -r requirements.txt
```

## 使用方法

### 1. 准备模板文件

在Word模板中手动标记需要替换的变量，使用双大括号格式，例如：
```
甲方：{{ company_name }}
税号：{{ tax_number }}
```

注意：只需要在需要替换的地方添加变量标记，其他内容保持不变。

### 2. 生成新合同

使用以下命令替换变量并生成新合同：
```bash
python main.py --template 合同模板.docx --output 新合同.docx --vars "company_name=测试科技有限公司" "tax_number=91330000123456789X" ...
```

## 支持的变量

### 甲方基本信息
- company_name: 公司名称（甲方）
- tax_number: 税号
- reg_address: 注册地址
- reg_phone: 注册电话
- bank_name: 开户行
- bank_account: 账号
- contact_name: 联系人
- contact_phone: 联系电话
- mail_address: 邮寄地址
- jdy_account: 简道云账号

### 服务期限
- service_years: 服务年限
- start_year: 开始年份
- start_month: 开始月份
- start_day: 开始日期
- end_year: 结束年份
- end_month: 结束月份
- end_day: 结束日期

### 费用信息
- total_amount: 服务费用总额（数字）
- total_amount_cn: 服务费用总额（大写）
- payment_amount: 支付金额（数字）
- payment_amount_cn: 支付金额（大写）
- tax_rate: 税率

### 用户信息
- user_count: 用户数量

### 付款信息
- payment_year: 付款年份
- payment_month: 付款月份
- payment_day: 付款日期
- payment_days: 付款工作日天数

### 发票信息
- invoice_type: 发票类型（普通/专用）

## 示例

生成新合同：
```bash
python main.py --template 合同模板.docx --output 新合同.docx --vars \
"company_name=测试科技有限公司" \
"tax_number=91330000123456789X" \
"reg_address=浙江省杭州市西湖区xxx路100号" \
"reg_phone=0571-88888888" \
"bank_name=中国银行杭州分行" \
"bank_account=123456789012345678" \
"contact_name=张三" \
"contact_phone=13800138000" \
"mail_address=浙江省杭州市西湖区xxx路100号" \
"jdy_account=test@company.com" \
"service_years=1" \
"start_year=2024" \
"start_month=3" \
"start_day=5" \
"end_year=2025" \
"end_month=3" \
"end_day=4" \
"total_amount=36500" \
"total_amount_cn=叁万陆仟伍佰" \
"payment_amount=36500" \
"payment_amount_cn=叁万陆仟伍佰" \
"tax_rate=6" \
"user_count=100" \
"payment_year=2024" \
"payment_month=3" \
"payment_day=12" \
"payment_days=7" \
"invoice_type=专用"
```

注意：
1. 变量名称必须与模板中的标记完全匹配
2. 生成的新合同文件会保存在当前目录下
3. 除了变量标记外的其他内容将保持不变
