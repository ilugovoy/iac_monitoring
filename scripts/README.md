# parse_ssh_config.py  
Скрипт для проверки конфигурации ssh в файле `/etc/ssh/sshd_config` на соответствие security best practices.  
Принимает на вход путь к файлу `sshd_config` и JSON-файл с эталонными значениями, возвращает JSON аналогичный роли `ssh_audit`  


## Структура    
```
└── scripts
    ├── parse_ssh_config.py
    └── defaults.json
```

## Требования  
* Python 3.8+  


## Параметры для проверки  
- `PermitRootLogin`
- `PasswordAuthentication`
- `MaxAuthTries`
- `ChallengeResponseAuthentication` (в новых версиях заменён на `KbdInteractiveAuthentication`)
- `X11Forwarding`


## Эталонные значения  
Определены в `defaults.json`:
```json
{
    "PermitRootLogin": "no",
    "PasswordAuthentication": "no", 
    "MaxAuthTries": "5",
    "ChallengeResponseAuthentication": "no",
    "X11Forwarding": "no"
}
```

> **ВАЖНО!** `ChallengeResponseAuthentication` в новых версиях была заменена на `KbdInteractiveAuthentication`, поэтому если не найден первый параметр, применяется значение из второго. 



## Результаты проверки   
Пример `non-compliant` лога:  
```json
{"timestamp": "2025-08-29T20:32:16Z", "host": "ubt24-test-01", "ansible_version": "2.16.3", "ansible_user": "ubuntu", "message": {"status": "non-compliant", "PermitRootLogin": "no", "PasswordAuthentication": "no", "MaxAuthTries": "6", "ChallengeResponseAuthentication": "no", "X11Forwarding": "no"}}
```

Пример `compliant` лога:  
```json
"message": {"status": "compliant"}
```

## 🛠️ Использование  
Делаем скрипт исполняемым: `chmod +x parse_ssh_config.py`  
Запуск: `./parse_ssh_config.py /etc/ssh/sshd_config defaults.json --hostname localhost`


## Разработка  
Для изменения эталонных значений отредактируйте: `defaults.json`  