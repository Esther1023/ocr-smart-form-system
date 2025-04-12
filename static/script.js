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