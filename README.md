![poster](pics/poster_iac_mon.png)


## Структура проекта  
```
├── README.md                                   # Этот файл
├── TASK.md                                     # Описание заданий
├── ansible.cfg
├── inventory/
│   ├── group_vars
│   │   └── local_test.yaml
│   └── hosts.ini
├── pics/                                        # Скриншоты вывода
├── playbooks/                                   # Плейбуки для запуска ролей
│   ├── eda_job_monitor.yml
│   └── ssh_audit.yml
├── roles/
│   ├── eda_job_monitor/                         # Роль для аудита контейнерных джоб
│   │   ├── README.md
│   │   ├── defaults/
│   │   │   └── main.yaml
│   │   └── tasks/
│   │       └── main.yaml
│   └── ssh_audit/                               # Роль для аудита конфига SSH
│       ├── README.md
│       ├── defaults/
│       │   └── main.yaml
│       ├── tasks/
│       │   └── main.yaml
│       └── templates/
│           └── ssh_config_parser.j2
├── scripts/                                     # Скрипт для аудита конфига SSH
│   ├── parse_ssh_config.py
│   └── defaults.json
├── requirements.txt
├── .gitlab-ci.yml
├── entrypoint.sh
├── Dockerfile
└── Makefile
```


## Компоненты
* Роль `ssh_audit` для проверки конфигурации SSH
* Роль `eda_job_monitor` для аудита контейнерных джоб
* Скрипт `parse_ssh_config.py` для проверки конфигурации SSH


## Требования   
* Ansible 2.9+
* Python 3.8+
* Docker/Podman
* Make


## Ansible-роль ssh_audit  
Роль описана в [roles/ssh_audit/README.md](roles/ssh_audit/README.md)  
Запуск с указанием конкретного хоста: `ansible-playbook playbooks/ssh_audit.yml -l localhost`  


## Ansible-роль eda_job_monitor для мониторинга регулярного исполнения ролей  
Роль описана в [roles/eda_job_monitor/README.md](roles/eda_job_monitor/README.md)  
Запуск с указанием конкретного хоста: `ansible-playbook playbooks/eda_job_monitor -l localhost`  


## Python-скрипт parse_ssh_config.py     
Скрипт описан в [scripts/README.md](scripts/README.md)  
Запуск с указанием конкретного хоста: `./parse_ssh_config.py /etc/ssh/sshd_config defaults.json --hostname localhost`


## CI/CD и запуск сервиса в Docker контейнере 
Автоматизированная систему проверки соответствия конфигурации SSH серверов корпоративным стандартам безопасности.  

Решение включает:  
* **Ansible роль** для глубокого аудита настроек sshd_config
* **Docker/Podman контейнер** для изолированного выполнения
* **CI/CD пайплайн** для автоматической сборки и тестирования
* **JSON отчеты** с детализацией несоответствий

Основные функции:  
* Проверка критических параметров безопасности SSH
* Изолированное выполнение в контейнере
* Интеграция с GitLab CI/CD
* Валидация JSON логов
* Поддержка эталонных конфигураций

Use Cases:  
* Регулярный аудит безопасности SSH
* Проверка соответствия compliance требованиям
* Интеграция в pipeline развертывания инфраструктуры
* Автоматизированный мониторинг дрифта конфигураций

### CI/CD пайплайн  
* `lint`: Проверка синтаксиса Ansible и YAML
* `build`: Сборка Docker образа с Podman
* `test`: Запуск роли в контейнере с тестовой конфигурацией
* `log_check`: Проверка валидности сгенерированного лога

### Использование    
* Установить зависимости: `pip install -r requirements.txt`
* Запустить линтеры: `make lint`
* Собрать контейнер: `make build`
* Запустить тесты: `sudo make test`
* Проверить лог: `make log-check`
* Все этапы: `make all`

### Примечания  
* Для доступа к `/etc/ssh/sshd_config` требуются права root
* Контейнер использует минимальный образ Alpine Linux
* Лог сохраняется в `/var/log/ansible-ssh-audit.log`


## Лицензия
Этот проект лицензирован [MIT License](LICENSE)  
