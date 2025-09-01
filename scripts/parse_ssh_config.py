#!/usr/bin/env python3
"""
Парсер конфигурации SSH с проверкой соответствия эталонным значениям
"""

import json
import sys
import argparse
from datetime import datetime, timezone
from pathlib import Path


def load_defaults(defaults_file=None):
    """
    Загружает значения по умолчанию
    """
    if defaults_file and Path(defaults_file).exists():
        try:
            with open(defaults_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, Exception) as e:
            print(f"Warning: Cannot load defaults from {defaults_file}: {e}", file=sys.stderr)


def parse_ssh_config(config_path, defaults_file=None):
    """
    Парсит файл sshd_config и извлекает значения указанных параметров
    """
    result = load_defaults(defaults_file)
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Ошибка: Файл {config_path} не найден", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Ошибка чтения файла: {e}", file=sys.stderr)
        sys.exit(1)
    
    for line in lines:
        line = line.strip()
        
        # Пропускаем комментарии и пустые строки
        if not line or line.startswith('#'):
            continue
        
        # Обрабатываем PermitRootLogin
        if line.startswith('PermitRootLogin'):
            value = extract_value(line)
            if value is not None:
                result['PermitRootLogin'] = normalize_boolean(value)
        
        # Обрабатываем PasswordAuthentication
        elif line.startswith('PasswordAuthentication'):
            value = extract_value(line)
            if value is not None:
                result['PasswordAuthentication'] = normalize_boolean(value)
        
        # Обрабатываем MaxAuthTries
        elif line.startswith('MaxAuthTries'):
            value = extract_value(line)
            if value is not None:
                result['MaxAuthTries'] = value
        
        # Обрабатываем ChallengeResponseAuthentication
        elif line.startswith('ChallengeResponseAuthentication'):
            value = extract_value(line)
            if value is not None:
                result['ChallengeResponseAuthentication'] = normalize_boolean(value)
        
        # Обрабатываем KbdInteractiveAuthentication (синоним для ChallengeResponseAuthentication)
        elif line.startswith('KbdInteractiveAuthentication'):
            value = extract_value(line)
            if value is not None:
                result['ChallengeResponseAuthentication'] = normalize_boolean(value)
        
        # Обрабатываем X11Forwarding
        elif line.startswith('X11Forwarding'):
            value = extract_value(line)
            if value is not None:
                result['X11Forwarding'] = normalize_boolean(value)
    
    return result


def extract_value(line):
    """
    Извлекает значение из строки конфигурации
    """
    parts = line.split(None, 1)
    if len(parts) < 2:
        return None
    
    value = parts[1].strip()
    
    # Удаляем комментарии в конце строки
    if '#' in value:
        value = value.split('#')[0].strip()
    
    return value if value else None


def normalize_boolean(value):
    """
    Нормализует булевы значения
    """
    value_lower = value.lower()
    
    if value_lower in ('yes', 'true', '1', 'on'):
        return 'yes'
    elif value_lower in ('no', 'false', '0', 'off'):
        return 'no'
    else:
        return value


def check_compliance(current_config, reference_config):
    """
    Проверяет соответствие текущей конфигурации
    """
    is_compliant = True
    non_compliant_params = {}
    
    for param, expected_value in reference_config.items():
        if param in current_config:
            current_value = current_config[param]
            if current_value != expected_value:
                is_compliant = False
                non_compliant_params[param] = {
                    'expected': expected_value,
                    'actual': current_value
                }
    
    return is_compliant, non_compliant_params


def create_output_message(current_config, reference_config, hostname=None):
    """
    Создает выходное сообщение в формате, аналогичном роли ssh_audit
    """
    is_compliant, non_compliant_params = check_compliance(current_config, reference_config)
    
    if is_compliant:
        return {
            "message": {
                "status": "compliant"
            }
        }
    else:
        # Создаем сообщение с несоответствующими параметрами
        message = {
            "status": "non-compliant"
        }
        
        # Добавляем только те параметры, которые не соответствуют
        for param in non_compliant_params:
            message[param] = current_config[param]
        
        # Добавляем временную метку и информацию о хосте, если предоставлена
        output = {
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        }
        
        if hostname:
            output["host"] = hostname
        
        output["message"] = message
        
        return output


def main():
    parser = argparse.ArgumentParser(description='Парсер конфигурации SSH с проверкой соответствия эталону')
    parser.add_argument('config_file', help='Путь к файлу sshd_config')
    parser.add_argument('reference_file', help='Путь к JSON-файлу с эталонными значениями')
    parser.add_argument('--defaults', '-d', help='Путь к JSON-файлу со значениями по умолчанию', default='defaults.json')
    parser.add_argument('--hostname', '-H', help='Имя хоста для включения в вывод', default=None)
    
    args = parser.parse_args()
    
    # Проверяем существование файлов
    if not Path(args.config_file).exists():
        print(f"Ошибка: Файл конфигурации {args.config_file} не найден", file=sys.stderr)
        sys.exit(1)
    
    if not Path(args.reference_file).exists():
        print(f"Ошибка: Эталонный файл {args.reference_file} не найден", file=sys.stderr)
        sys.exit(1)
    
    # Загружаем эталонную конфигурацию
    try:
        with open(args.reference_file, 'r', encoding='utf-8') as f:
            reference_config = json.load(f)
    except json.JSONDecodeError:
        print("Ошибка: Неверный формат JSON в эталонном файле", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Ошибка чтения эталонного файла: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Парсим конфигурацию SSH
    current_config = parse_ssh_config(args.config_file, args.defaults)
    
    # Создаем выходное сообщение
    output_message = create_output_message(current_config, reference_config, args.hostname)
    
    # Выводим результат в формате JSON
    print(json.dumps(output_message, indent=2))


if __name__ == "__main__":
    main()