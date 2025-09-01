#!/bin/sh
set -e

echo "Starting SSH audit container..."

# Проверяем доступность Ansible
if ! command -v ansible &> /dev/null; then
    echo "Error: Ansible not found!"
    exit 1
fi

# Проверяем наличие необходимых файлов
if [ ! -f "/etc/ssh/sshd_config" ]; then
    echo "Error: sshd_config not found at /etc/ssh/sshd_config"
    exit 1
fi

# Запускаем плейбук
echo "Running SSH audit playbook..."
ansible-playbook -i inventory/hosts.ini playbooks/ssh_audit.yml

# Проверяем наличие лог-файла
if [ -f "/var/log/ansible-ssh-audit.log" ]; then
    echo "Log file generated successfully"
    echo "=== LOG CONTENT ==="
    cat /var/log/ansible-ssh-audit.log
    echo "==================="
    
    # Проверяем валидность JSON
    if jq empty /var/log/ansible-ssh-audit.log 2>/dev/null; then
        echo "✓ Log file contains valid JSON"
        exit 0
    else
        echo "✗ Log file contains invalid JSON"
        exit 1
    fi
else
    echo "Error: Log file not found at /var/log/ansible-ssh-audit.log"
    exit 1
fi