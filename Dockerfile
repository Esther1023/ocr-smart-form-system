FROM gitea/runner-images:ubuntu-20.04-slim

# 更新包列表并安装 Python 3 和 pip
RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 修改 pip 源
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# 使用 pip 安装 Ansible
RUN pip3 install ansible

# 将 Ansible 添加到环境变量
ENV PATH="/usr/local/bin:$PATH"

# 设置工作目录

# 复制 Ansible 配置文件和剧本（如果有）
# COPY ansible.cfg /etc/ansible/ansible.cfg
# COPY playbooks/ /workspace/playbooks/

# 默认命令
CMD ["ansible", "--version"]
