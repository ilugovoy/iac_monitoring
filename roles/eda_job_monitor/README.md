# Ansible-роль eda_job_monitor для мониторинга регулярного исполнения ролей (EDA Job Monitor)  
Event-Driven Architecture (EDA) это архитектурный паттерн, где система реагирует на события (events) в реальном времени.  
Контейнеризированные Ansible-роли это когда вместо запуска Ansible напрямую, каждая роль упаковывается в Docker-контейнер.  
Роль проверяет запускался ли такой контейнер за последние N часов.    

## Структура роли  
```
├── inventory
│   ├── group_vars
│   │   └── local_test.yaml
│   └── hosts.ini
├── playbooks
│   └── eda_job_monitor.yml
└── roles
    └── roles/eda_job_monitor/
        ├── README.md
        ├── defaults
        │   └── main.yaml
        └── tasks
            └── main.yaml
```


## Параметры для проверки  
Для тестирования с Podman создал тестовые контейнеры:  
* `podman run -d --name ansible-job-ssh-audit alpine:latest sleep 3600`
Создание "старого" контейнера для тестирования времени:  
* `podman run -d --name ansible-job-old-job alpine:latest sleep 3600`
* `podman stop ansible-job-old-job`

Проверка формата вывода Podman: `podman ps -a --format "table {{.Names}}\t{{.CreatedAt}}\t{{.Status}}\t{{.State}}"`


## Эталонные значения  
Определены в `defaults/main.yml`:
```yaml
eda_job_monitor:
  container_prefix: "ansible-job-"          # Префикс контейнеров для мониторинга
  check_interval_minutes: 60                # Интервал проверки
```


## Результаты проверки   
Если контейнер в состоянии `exited` и запускался более `check_interval_minutes` назад, то получим статус `unhealthy`  
```json
{
    "msg": {
        "ansible_user": "ubuntu",
        "ansible_version": "2.16.3",
        "host": "ubt24-test-01",
        "message": {
            "jobs": {
                "ansible-job-old-job": "last_seen: 2025-08-29T22:40:58Z"
            },
            "status": "unhealthy"
        },
        "timestamp": "2025-08-30T00:49:31Z"
    }
}
```

Если контейнер в состоянии `running` или запускался менее `check_interval_minutes` назад, то получим статус `healthy`  
```json
{
    "msg": {
        "ansible_user": "ubuntu",
        "ansible_version": "2.16.3",
        "host": "ubt24-test-01",
        "message": {
            "jobs": {
                "ansible-job-ssh-audit": "executed_at: 2025-08-30T00:50:16Z"
            },
            "status": "healthy"
        },
        "timestamp": "2025-08-30T00:51:12Z"
    }
}
```

Для каждого контейнера формируется отдельная запись:  
```
$ cat /var/log/ansible-eda-monitor.log
{"timestamp": "2025-08-31T21:39:54Z", "host": "ubt24-test-01", "ansible_version": "2.16.3", "ansible_user": "ubuntu", "message": {"status": "healthy", "jobs": {"ansible-job-ssh-audit": "executed_at: 2025-08-31T20:52:57Z"}}}
{"timestamp": "2025-08-31T21:39:54Z", "host": "ubt24-test-01", "ansible_version": "2.16.3", "ansible_user": "ubuntu", "message": {"status": "unhealthy", "jobs": {"ansible-job-old-job": "last_seen: 2025-08-31T21:38:03Z"}}}
```


## 🛠️ Использование  
Запуск с ограничением по группе: `ansible-playbook playbooks/eda_job_monitor.yml -l localhost`  
Запуск с указанием конкретного хоста: `ansible-playbook playbooks/eda_job_monitor.yml -l localhost`  


## Разработка  
Для изменения эталонных значений отредактируйте: `roles/eda_job_monitor/defaults/main.yml`  