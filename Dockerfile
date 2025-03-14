FROM gitea/runner-images:ubuntu-20.04-slim

# 更新包列表并安装 Ansible 及其依赖项
RUN apt-get update && \
    apt-get install -y ansible && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 设置工作目录

# 复制 Ansible 配置文件和剧本（如果有）
# COPY ansible.cfg /etc/ansible/ansible.cfg
# COPY playbooks/ /workspace/playbooks/

# 默认命令
CMD ["node"]
