// 获取即将过期的客户信息并显示提示框
function fetchExpiringCustomers() {
    fetch('/get_expiring_customers')
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error('获取即将过期客户失败:', data.error);
                return;
            }
            
            if (data.expiring_customers && data.expiring_customers.length > 0) {
                showExpiringCustomersAlert(data.expiring_customers);
            }
        })
        .catch(error => {
            console.error('获取即将过期客户错误:', error);
        });
}

// 创建并显示即将过期客户提示框
// 快捷按钮链接配置
document.addEventListener('DOMContentLoaded', function() {
    // 配置快捷按钮的链接
    const shortcutLinks = {
        'btn-hetiao': 'https://www.jiandaoyun.com/dashboard#/app/5a015dd12d85443cacd1b893/form/5a0186552d85443cacd4ef18',  // 合票链接
        'btn-sa': 'https://dc.jdydevelop.com/sa?redirect_uri=%2Finfo_search%2Fuser_search',      // SA链接
        'btn-huikuan': 'https://crm.finereporthelp.com/WebReport/decision/view/report?viewlet=finance/jdy_confirm/bank_income_list_cofirm.cpt&op=write',  // 回款链接
        'btn-xiadan': 'https://www.jiandaoyun.com/dashboard#/app/5a015dd12d85443cacd1b893/form/5a0186552d85443cacd4ef18',   // 下单链接
        'btn-qiwei': 'https://open.work.weixin.qq.com/wwopen/login?etype=noTtl#/payment/cashier',                                           // 企微链接
        'btn-daike': 'https://www.jiandaoyun.com/dashboard#/app/5a015dd12d85443cacd1b893/form/6462df15ad96a800087b1f8f'    // 代客链接
    };
    
    // 内联快捷按钮的链接配置（与顶部快捷按钮使用相同的链接）
    const inlineShortcutLinks = {
        'btn-hetiao-inline': 'https://www.jiandaoyun.com/dashboard#/app/5a015dd12d85443cacd1b893/form/5a0186552d85443cacd4ef18',  // 合票链接
        'btn-sa-inline': 'https://dc.jdydevelop.com/sa?redirect_uri=%2Finfo_search%2Fuser_search',      // SA链接
        'btn-huikuan-inline': 'https://crm.finereporthelp.com/WebReport/decision/view/report?viewlet=finance/jdy_confirm/bank_income_list_cofirm.cpt&op=write',  // 回款链接
        'btn-xiadan-inline': 'https://www.jiandaoyun.com/dashboard#/app/5a015dd12d85443cacd1b893/form/5a0186552d85443cacd4ef18',   // 下单链接
        'btn-qiwei-inline': 'https://open.work.weixin.qq.com/wwopen/login?etype=noTtl#/payment/cashier',                                           // 企微链接
        'btn-daike-inline': 'https://www.jiandaoyun.com/dashboard#/app/5a015dd12d85443cacd1b893/form/6462df15ad96a800087b1f8f'    // 代客链接
    };
    
    // 为顶部快捷按钮添加点击事件
    Object.keys(shortcutLinks).forEach(btnId => {
        const btn = document.getElementById(btnId);
        if (btn) {
            btn.addEventListener('click', function() {
                window.open(shortcutLinks[btnId], '_blank');
            });
        }
    });
    
    // 为内联快捷按钮添加点击事件
    Object.keys(inlineShortcutLinks).forEach(btnId => {
        const btn = document.getElementById(btnId);
        if (btn) {
            btn.addEventListener('click', function() {
                window.open(inlineShortcutLinks[btnId], '_blank');
            });
        }
    });}
);

function showExpiringCustomersAlert(customers) {
    // 检查是否已存在提示框，如果存在则移除
    const existingAlert = document.querySelector('.expiring-customers-alert');
    if (existingAlert) {
        existingAlert.remove();
    }
    
    // 创建提示框容器
    const alertContainer = document.createElement('div');
    alertContainer.className = 'expiring-customers-alert';
    
    // 创建提示框头部
    const alertHeader = document.createElement('div');
    alertHeader.className = 'expiring-customers-header';
    
    const alertTitle = document.createElement('h4');
    alertTitle.textContent = '即将过期客户提醒';
    
    const closeButton = document.createElement('button');
    closeButton.className = 'close-btn';
    closeButton.textContent = '×';
    closeButton.onclick = function() {
        alertContainer.remove();
    };
    
    alertHeader.appendChild(alertTitle);
    alertHeader.appendChild(closeButton);
    
    // 创建提示框内容
    const alertBody = document.createElement('div');
    alertBody.className = 'expiring-customers-body';
    
    // 添加客户信息
    customers.forEach(customer => {
        const customerItem = document.createElement('div');
        customerItem.className = 'expiring-customer-item';
        
        const dateElement = document.createElement('div');
        dateElement.className = 'expiring-customer-date';
        dateElement.textContent = `过期日期: ${customer.expiry_date}`;
        
        const accountElement = document.createElement('div');
        accountElement.textContent = `简道云账号: ${customer.jdy_account}`;
        
        const companyElement = document.createElement('div');
        companyElement.textContent = `公司名称: ${customer.company_name}`;
        
        customerItem.appendChild(dateElement);
        customerItem.appendChild(accountElement);
        customerItem.appendChild(companyElement);
        
        alertBody.appendChild(customerItem);
    });
    
    // 组装提示框
    // 不添加标题部分，直接添加内容
    alertContainer.appendChild(alertBody);
    
    // 添加到页面
    document.body.appendChild(alertContainer);
}

// 页面加载完成后获取即将过期的客户
document.addEventListener('DOMContentLoaded', function() {
    // 检查用户是否已登录（通过检查页面上的元素判断）
    if (document.getElementById('contractForm')) {
        fetchExpiringCustomers();
    }
});

function generateInvoiceInfo() {
    const invoiceType = document.getElementById('invoiceType').value;
    const email = document.getElementById('invoiceEmail').value;
    const totalAmount = document.getElementById('totalAmount').value;
    const totalAmountCn = document.getElementById('totalAmountCn').value;
    
    let info = `简道云ID: ${jdyId}\n`;
    info += `发票类型: ${invoiceType}\n`;
    info += `服务费用金额: ${totalAmount}元（${totalAmountCn}）\n`;
    info += `公司名称: ${companyName}\n`;
    info += `税号: ${taxNumber}\n`;
    info += `地址: ${address}\n`;
    info += `电话: ${phone}\n`;
    info += `开户行: ${bankName}\n`;
    info += `账号: ${bankAccount}\n`;
    info += `邮箱: ${email}\n`;
    
    document.getElementById('invoiceInfo').value = info;

    // 添加历史记录
    const now = new Date();
    const timestamp = now.toLocaleString('zh-CN');
    let historyInfo = document.getElementById('invoiceHistory').value;
    historyInfo = `${timestamp}\n${info}\n\n${historyInfo}`;
    document.getElementById('invoiceHistory').value = historyInfo;
}


function queryCustomer() {
    const jdyId = document.querySelector('[name="jdy_account"]').value.trim();
    if (!jdyId) {
        alert('请输入简道云账号');
        return;
    }

    fetch('/query_customer', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ jdy_id: jdyId })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
            return;
        }
        
        // 更新显示内容
        document.getElementById('companyName').textContent = data.company_name || '暂无数据';
        document.getElementById('customerType').textContent = data.customer_type || '暂无数据';
        document.getElementById('customerRegion').textContent = data.customer_region || '暂无数据';
        document.getElementById('salesPerson').textContent = data.sales || '暂无数据';
        document.getElementById('jdyAccountInfo').textContent = data.jdy_account || '暂无数据';
        document.getElementById('expiryDate').textContent = data.expiry_date || '暂无数据';
        document.getElementById('version').textContent = data.version || '暂无数据';
        document.getElementById('accountCount').textContent = data.account_count || '0';
        document.getElementById('paidAccountCount').textContent = data.paid_account_count || '0';
        document.getElementById('uidArr').textContent = data.uid_arr || '0元';
        
        // 显示结果区域
        document.getElementById('customerInfo').style.display = 'block';
    })
    .catch(error => {
        console.error('Error:', error);
        alert('查询失败，请稍后重试');
    });
}