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