# Тестовое задание на позицию "Специалист по автоматизации процессов мониторинга и реагирования"  

## Содержание  
Файл/папка | Назначение
-----------|-----------
`roles/ssh_audit/` | Ansible-роль
`eda_job_monitor/` | Мониторинг исполнения ролей
`docker/Dockerfile` | Контейнер с ролью
`entrypoint.sh` | Скрипт запуска роли
`.github/workflows/ansible.yml` или `.gitlab-ci.yml` | CI/CD
`scripts/parse_ssh_config.py` или `.ipynb` | Анализ sshd_config
`README.md` | Инструкция по сборке, запуску и тестированию
`example_logs/` | Примеры логов: `compliant / non-compliant / monitoring`

## Задачи  

### 1. Ansible-роль ssh_audit  
**Задача:** разработать Ansible-роль `ssh_audit`, которая проверяет конфигурационный файл `/etc/ssh/sshd_config` на соответствие заданным параметрам.  

**Проверяемые параметры:**
* `PermitRootLogin`
* `PasswordAuthentication`
* `MaxAuthTries`
* `ChallengeResponseAuthentication`
* `X11Forwarding`

**Требования**:  
* Эталонные значения параметров должны задаваться в переменных роли
* Вся информация о результате проверки должна записываться в однострочную JSON-запись в файл `/var/log/ansible-ssh-audit.log`

Формат лога:  
```json
{"timestamp": "2025-07-01T01:23:45Z",
  "host": "srv1.example.com",
  "ansible_version": "2.15.0",
  "ansible_user": "admin",
  "message": {
    "status": "non-compliant",
    "PermitRootLogin": "yes",
    "PasswordAuthentication": "yes",
    "MaxAuthTries": "6",
    "ChallengeResponseAuthentication": "no",
    "X11Forwarding": "yes"
  }
}
```

Если конфигурация соответствует:
```json
"message": {"status": "compliant"}
```


### 2. Мониторинг регулярного исполнения ролей (EDA Jobs Monitoring)  
В продакшене Ansible-работы исполняются как контейнеризированные сервисы (одна роль = один контейнер) в составе Event-Driven Architecture (EDA).  
Каждый такой контейнер должен исполняться не реже 1 раза в сутки.  

**Задача:** Реализовать мониторинг того, что такие контейнеры:
* действительно запускались за последние 24 часа
* завершились корректно

**Что нужно сделать**  
Написать Ansible-роль, которая:
•	Находит контейнеры с Ansible-ролями (например, по префиксу `ansible-job-*`)
•	Проверяет, запускался ли каждый из них за последние N часов
•	Выдает лог в формате:
```json
{
  "timestamp": "2025-07-01T12:34:56Z",
  "host": "eda-node-1",
  "ansible_version": "2.15.0",
  "ansible_user": "admin",
  "message": {
    "status": "healthy",
    "jobs": {"ansible-job-ssh-audit": "executed_at: 2025-07-01T01:01:00Z"}
  }
}
```

Если контейнер не запускался:  
```json
"message": {
  "status": "unhealthy",
  "jobs": {"ansible-job-ssh-audit": "last_seen: 2025-06-29T01:01:00Z"}
}
```

### 3. Python-скрипт или Jupyter Notebook   
**Задача:** Написать вспомогательный инструмент, который:  
* Принимает на вход: путь к файлу `sshd_config` и JSON-файл с эталонными значениями
* Возвращает JSON-сообщение, message (аналогичный роли `ssh_audit`)
* Название файла: `parse_ssh_config.py`  
 
 
### 4. CI/CD и запуск сервиса в Docker контейнере  
**Задача:** Обеспечить автоматизацию сборки, запуска и проверки роли `ssh_audit`  

**Требования**:  
* Dockerfile:
    * Сборка контейнера с установленным Ansible
    * Копирование роли, переменных, инвентари файла
    * Запуск роли при старте контейнера (`entrypoint.sh`)
* CI/CD пайплайн:
    * Написать yml-файл для CI/CD. GitLab CI (`.gitlab-ci.yml`) или иной.
    * Стадии:
        * `lint` — ansible-lint, yamllint
        * `build` — сборка Docker-образа
        * `test` — запуск роли в контейнере
        * `log_check` — проверка, что сгенерирован лог и он валиден (jq)
    * `Makefile` (опционально, если так удобней). Команды: `make lint`, `make build`, `make test`
