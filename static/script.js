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
        'btn-qiwei': 'https://crm.finereporthelp.com/WebReport/decision?#?activeTab=bf50447e-5ce2-4c7f-834e-3e1495df033a',                                           // kms链接
        'btn-daike': 'https://bi.finereporthelp.com/webroot/decision?#/directory?activeTab=4a3d1d52-2e58-4e0c-bb82-722b1a8bc6bf'    // 看板链接
    };
    
    // 内联快捷按钮的链接配置（与顶部快捷按钮使用相同的链接）
    const inlineShortcutLinks = {
        'btn-hetiao-inline': 'https://bi.jdydevelop.com/webroot/decision#/?activeTab=6ed7a7e6-70b0-4814-9424-35d784d8e686',  // 业绩链接
        'btn-sa-inline': 'https://dc.jdydevelop.com/sa?redirect_uri=%2Finfo_search%2Fuser_search',      // SA链接
        'btn-huikuan-inline': 'https://crm.finereporthelp.com/WebReport/decision/view/report?viewlet=finance/jdy_confirm/bank_income_list_cofirm.cpt&op=write',  // 回款链接
        'btn-xiadan-inline': 'https://open.work.weixin.qq.com/wwopen/developer#/sass/license/service/order/detail?orderid=OI00000FEA3AC66805CA325DABD6AN',   // 接口链接
        'btn-qiwei-inline': 'https://crm.finereporthelp.com/WebReport/decision?#?activeTab=bf50447e-5ce2-4c7f-834e-3e1495df033a',      // kms链接
        'btn-daike-inline': 'https://bi.finereporthelp.com/webroot/decision?#/directory?activeTab=4a3d1d52-2e58-4e0c-bb82-722b1a8bc6bf'    // 看板链接
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

// 创建备忘录白板（替代原来的25-30天到期客户看板）
function showFutureExpiringCustomersDashboard(estherCustomers, otherCustomers) {
    // 检查是否已存在看板，如果存在则移除
    const existingDashboard = document.querySelector('.future-expiring-dashboard');
    if (existingDashboard) {
        existingDashboard.remove();
    }

    // 创建看板容器（保持原来的类名以维持样式）
    const dashboardContainer = document.createElement('div');
    dashboardContainer.className = 'future-expiring-dashboard';

    // 创建看板标题
    const dashboardHeader = document.createElement('div');
    dashboardHeader.className = 'dashboard-header';

    const memoTitle = document.createElement('h4');
    memoTitle.textContent = '备忘录';
    memoTitle.style.color = 'var(--text-color)';
    memoTitle.style.margin = '0';
    memoTitle.style.fontSize = '16px';

    const closeButton = document.createElement('button');
    closeButton.className = 'close-btn';
    closeButton.textContent = '×';
    closeButton.onclick = function() {
        dashboardContainer.remove();
    };

    dashboardHeader.appendChild(memoTitle);
    dashboardHeader.appendChild(closeButton);

    // 创建备忘录内容区域（使用原来的dashboard-body类名）
    const dashboardBody = document.createElement('div');
    dashboardBody.className = 'dashboard-body';

    const memoTextarea = document.createElement('textarea');
    memoTextarea.className = 'memo-textarea';
    memoTextarea.placeholder = '在这里记录您的备忘事项...\n\n• 待办事项\n• 重要提醒\n• 工作笔记\n• 客户跟进';
    memoTextarea.style.width = '100%';
    memoTextarea.style.height = '100%';
    memoTextarea.style.border = 'none';
    memoTextarea.style.outline = 'none';
    memoTextarea.style.resize = 'none';
    memoTextarea.style.padding = '15px';
    memoTextarea.style.fontSize = '14px';
    memoTextarea.style.lineHeight = '1.5';
    memoTextarea.style.backgroundColor = 'transparent';
    memoTextarea.style.color = 'var(--text-color)';
    memoTextarea.style.fontFamily = 'inherit';

    // 从本地存储加载备忘录内容
    const savedMemo = localStorage.getItem('memo-content');
    if (savedMemo) {
        memoTextarea.value = savedMemo;
    }

    // 自动保存备忘录内容
    memoTextarea.addEventListener('input', function() {
        localStorage.setItem('memo-content', this.value);
    });

    dashboardBody.appendChild(memoTextarea);

    // 组装看板
    dashboardContainer.appendChild(dashboardHeader);
    dashboardContainer.appendChild(dashboardBody);

    // 添加到页面
    document.body.appendChild(dashboardContainer);
}





// 页面加载完成后获取即将过期的客户并显示备忘录
document.addEventListener('DOMContentLoaded', function() {
    // 检查用户是否已登录（通过检查页面上的元素判断）
    if (document.getElementById('contractForm')) {
        fetchExpiringCustomers();
        // 显示备忘录白板（替代原来的25-30天到期客户看板）
        showFutureExpiringCustomersDashboard([], []);
    }
});




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