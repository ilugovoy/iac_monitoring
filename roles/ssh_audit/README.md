# Ansible роль: ssh_audit  
Роль для проверки конфигурации ssh в файле `/etc/ssh/sshd_config` на соответствие security best practices.  

## Структура роли  
```
├── inventory
│   ├── group_vars
│   │   └── local_test.yaml
│   └── hosts.ini
├── playbooks
│   └── ssh_audit.yml
└── roles
    └── ssh_audit
        ├── README.md
        ├── defaults
        │   └── main.yaml
        ├── tasks
        │   └── main.yaml
        └── templates
            └── ssh_config_parser.j2
```


## Параметры для проверки  
- `PermitRootLogin`
- `PasswordAuthentication`
- `MaxAuthTries`
- `ChallengeResponseAuthentication` (в новых версиях заменён на `KbdInteractiveAuthentication`)
- `X11Forwarding`

## Эталонные значения  
Определены в `defaults/main.yml`:
```yaml
ssh_audit_config:
  PermitRootLogin: "no"
  PasswordAuthentication: "no"
  MaxAuthTries: "5"
  ChallengeResponseAuthentication: "no"
  X11Forwarding: "no"
```

> **ВАЖНО!** `ChallengeResponseAuthentication` в новых версиях была заменена на `KbdInteractiveAuthentication`, поэтому если не найден первый параметр, применяется значение из второго. 

В файле `roles\ssh_audit\templates\ssh_config_parser.j2` указан шаблон для проверки, в котором определены значения по умолчанию для OpenSSH:  
```json
{% set result = {
    'PermitRootLogin': 'yes',
    'PasswordAuthentication': 'yes', 
    'MaxAuthTries': '6',
    'ChallengeResponseAuthentication': 'yes',
    'X11Forwarding': 'no'
} %}
``` 

## Результаты проверки  
Результаты записываются в `/var/log/ansible-ssh-audit.log` в формате JSON.  

Пример `non-compliant` лога:  
```json
{"timestamp": "2025-08-29T20:32:16Z", "host": "ubt24-test-01", "ansible_version": "2.16.3", "ansible_user": "ubuntu", "message": {"status": "non-compliant", "PermitRootLogin": "no", "PasswordAuthentication": "no", "MaxAuthTries": "6", "ChallengeResponseAuthentication": "no", "X11Forwarding": "no"}}
```

Пример `compliant` лога:  
```json
"message": {"status": "compliant"}
```

## 🛠️ Использование  
Запуск с ограничением по группе: `ansible-playbook playbooks/ssh_audit.yml -l local_test`  
Запуск с указанием конкретного хоста: `ansible-playbook playbooks/ssh_audit.yml -l localhost`  

При выполнении мы увидим такое

## Разработка  
Для изменения эталонных значений отредактируйте: `roles/ssh_audit/defaults/main.yml`  