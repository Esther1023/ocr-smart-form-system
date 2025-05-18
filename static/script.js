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
        'btn-hetiao': 'https://bi.jdydevelop.com/webroot/decision#/?activeTab=6ed7a7e6-70b0-4814-9424-35d784d8e686',  // 业绩链接
        'btn-sa': 'https://dc.jdydevelop.com/sa?redirect_uri=%2Finfo_search%2Fuser_search',      // SA链接
        'btn-huikuan': 'https://crm.finereporthelp.com/WebReport/decision/view/report?viewlet=finance/jdy_confirm/bank_income_list_cofirm.cpt&op=write',  // 回款链接
        'btn-xiadan': 'https://open.work.weixin.qq.com/wwopen/developer#/sass/license/service/order/detail?orderid=OI00000FEA3AC66805CA325DABD6AN',   // 接口链接
        'btn-qiwei': 'https://crm.finereporthelp.com/WebReport/decision?#?activeTab=bf50447e-5ce2-4c7f-834e-3e1495df033a',                                           // 快去学习链接
        'btn-daike': 'https://bi.finereporthelp.com/webroot/decision?ticket=ST-1661930-gnOi6zSJldUmv-6b6jEx2sT-JPI-passport-cas-5f446496d7-hvvfc#/directory?activeTab=a5a2cd0c-e564-437b-87c4-https://bi.finereporthelp.com/webroot/decision?#/directory?activeTab=12d9701c-b4b7-4ae7-b37f-ff3d418f4b8a'    // 看板链接
    };
    
    // 内联快捷按钮的链接配置（与顶部快捷按钮使用相同的链接）
    const inlineShortcutLinks = {
        'btn-hetiao-inline': 'https://bi.jdydevelop.com/webroot/decision#/?activeTab=6ed7a7e6-70b0-4814-9424-35d784d8e686',  // 业绩链接
        'btn-sa-inline': 'https://dc.jdydevelop.com/sa?redirect_uri=%2Finfo_search%2Fuser_search',      // SA链接
        'btn-huikuan-inline': 'https://crm.finereporthelp.com/WebReport/decision/view/report?viewlet=finance/jdy_confirm/bank_income_list_cofirm.cpt&op=write',  // 回款链接
        'btn-xiadan-inline': 'https://open.work.weixin.qq.com/wwopen/developer#/sass/license/service/order/detail?orderid=OI00000FEA3AC66805CA325DABD6AN',   // 接口链接
        'btn-qiwei-inline': 'https://crm.finereporthelp.com/WebReport/decision?#?activeTab=bf50447e-5ce2-4c7f-834e-3e1495df033a',      // 快去学习链接
        'btn-daike-inline': 'https://bi.finereporthelp.com/webroot/decision?ticket=ST-1661930-gnOi6zSJldUmv-6b6jEx2sT-JPI-passport-cas-5f446496d7-hvvfc#/directory?activeTab=a5a2cd0c-e564-437b-87c4-75d1ae01b79ehttps://bi.finereporthelp.com/webroot/decision?#/directory?activeTab=12d9701c-b4b7-4ae7-b37f-ff3d418f4b8a'    // 看板链接
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
    });
});

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
        customerItem.style.padding = '2px 0 2px 0';
        
        const dateElement = document.createElement('div');
        dateElement.className = 'expiring-customer-date';
        dateElement.textContent = `${customer.expiry_date}`;
        dateElement.style.marginTop = '0';
        dateElement.style.marginBottom = '2px';
        
        const accountElement = document.createElement('div');
        accountElement.textContent = `${customer.jdy_account}`;
        accountElement.style.marginBottom = '1px';
        
        const companyElement = document.createElement('div');
        companyElement.textContent = `${customer.company_name}`;
        companyElement.style.marginBottom = '1px';
        
        const salesElement = document.createElement('div');
        salesElement.className = 'expiring-customer-sales';
        salesElement.textContent = `${customer.sales_person || '未指定'}`;
        if (customer.sales_person === 'Esther-朱晓琳') {
            salesElement.classList.add('esther-sales');
        } else if (customer.sales_person === 'public-公共账号') {
            salesElement.classList.add('public-sales');
        }
        salesElement.style.marginTop = '2px';
        salesElement.style.marginBottom = '0';
        
        customerItem.appendChild(dateElement);
        customerItem.appendChild(accountElement);
        customerItem.appendChild(companyElement);
        customerItem.appendChild(salesElement);
        
        alertBody.appendChild(customerItem);
    });
    
    // 组装提示框
    // 不添加标题部分，直接添加内容
    alertContainer.appendChild(alertBody);
    
    // 添加到页面
    document.body.appendChild(alertContainer);
}

// 获取未来23-30天内到期的客户信息
function fetchFutureExpiringCustomers() {
    fetch('/get_future_expiring_customers')
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error('获取未来即将过期客户失败:', data.error);
                return;
            }
            
            if ((data.esther_customers && data.esther_customers.length > 0) || 
                (data.other_customers && data.other_customers.length > 0)) {
                showFutureExpiringCustomersDashboard(data.esther_customers, data.other_customers);
            }
        })
        .catch(error => {
            console.error('获取未来即将过期客户错误:', error);
        });
}

// 创建并显示未来23-30天内到期客户看板
function showFutureExpiringCustomersDashboard(estherCustomers, otherCustomers) {
    // 检查是否已存在看板，如果存在则移除
    const existingDashboard = document.querySelector('.future-expiring-dashboard');
    if (existingDashboard) {
        existingDashboard.remove();
    }
    
    // 创建看板容器
    const dashboardContainer = document.createElement('div');
    dashboardContainer.className = 'future-expiring-dashboard';
    
    // 创建看板标题 - 只保留关闭按钮，不显示标题
    const dashboardHeader = document.createElement('div');
    dashboardHeader.className = 'dashboard-header';
    
    const closeButton = document.createElement('button');
    closeButton.className = 'close-btn';
    closeButton.textContent = '×';
    closeButton.onclick = function() {
        dashboardContainer.remove();
    };
    
    dashboardHeader.appendChild(closeButton);
    
    // 创建看板内容
    const dashboardBody = document.createElement('div');
    dashboardBody.className = 'dashboard-body';
    
    // Esther负责的客户部分
    if (estherCustomers && estherCustomers.length > 0) {
        const estherSection = document.createElement('div');
        estherSection.className = 'customer-section';
        
        // 不显示标题
        // const estherTitle = document.createElement('h4');
        // estherTitle.textContent = 'Esther朱晓琳负责的客户';
        // estherSection.appendChild(estherTitle);
        
        const estherTable = createCustomerTable(estherCustomers);
        estherSection.appendChild(estherTable);
        
        dashboardBody.appendChild(estherSection);
    }
    
    // 其他销售负责的客户部分
    if (otherCustomers && otherCustomers.length > 0) {
        const otherSection = document.createElement('div');
        otherSection.className = 'customer-section';
        
        // 不显示标题
        // const otherTitle = document.createElement('h4');
        // otherTitle.textContent = '其他销售负责的客户';
        // otherSection.appendChild(otherTitle);
        
        const otherTable = createCustomerTable(otherCustomers);
        otherSection.appendChild(otherTable);
        
        dashboardBody.appendChild(otherSection);
    }
    
    // 组装看板
    dashboardContainer.appendChild(dashboardHeader);
    dashboardContainer.appendChild(dashboardBody);
    
    // 添加到页面
    document.body.appendChild(dashboardContainer);
}

// 创建客户表格
function createCustomerTable(customers) {
    // 创建一个容器而不是表格，采用卡片式分行展示
    const container = document.createElement('div');
    container.className = 'customer-card-list';
    customers.forEach(customer => {
        const card = document.createElement('div');
        card.className = 'customer-card-item';
        // 到期日期（高亮加粗）
        const dateDiv = document.createElement('div');
        dateDiv.className = 'customer-card-date';
        dateDiv.textContent = customer.expiry_date;
        card.appendChild(dateDiv);
        // 简道云账号
        const accountDiv = document.createElement('div');
        accountDiv.className = 'customer-card-account';
        accountDiv.textContent = customer.jdy_account;
        card.appendChild(accountDiv);
        // 公司名称
        const companyDiv = document.createElement('div');
        companyDiv.className = 'customer-card-company';
        companyDiv.textContent = customer.company_name;
        card.appendChild(companyDiv);
        // 销售人员
        const salesDiv = document.createElement('div');
        salesDiv.className = 'customer-card-sales';
        salesDiv.textContent = customer.sales_person || '未指定';
        if (customer.sales_person === 'Esther-朱晓琳') {
            salesDiv.classList.add('esther-sales');
        } else if (customer.sales_person === 'public-公共账号') {
            salesDiv.classList.add('public-sales');
        }
        card.appendChild(salesDiv);
        container.appendChild(card);
    });
    return container;
}

// 页面加载完成后获取即将过期的客户
document.addEventListener('DOMContentLoaded', function() {
    // 检查用户是否已登录（通过检查页面上的元素判断）
    if (document.getElementById('contractForm')) {
        fetchExpiringCustomers();
        fetchFutureExpiringCustomers();
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