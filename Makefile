.PHONY: lint build test log-check clean

# Переменные
IMAGE_NAME = ssh-audit
IMAGE_TAG = latest

# Проверка синтаксиса
lint:
	@echo "Запуск ansible-lint для роли ssh_audit..."
	ansible-lint roles/ssh_audit/
	@echo "Запуск yamllint для роли ssh_audit..."
	yamllint roles/ssh_audit/

# Сборка Docker образа
build:
	@echo "Сборка оптимизированного контейнера..."
	sudo podman build --no-cache -t $(IMAGE_NAME):$(IMAGE_TAG) .

# Запуск тестов в контейнере
test:
	@echo "Запуск SSH аудита в контейнере..."
	sudo podman run --rm \
		-v /etc/ssh/sshd_config:/etc/ssh/sshd_config:ro \
		$(IMAGE_NAME):$(IMAGE_TAG)

# Проверка валидности лог-файла
log-check:
	@echo "Проверка валидности лог-файла..."
	@if [ -f "/var/log/ansible-ssh-audit.log" ]; then \
		sudo jq empty /var/log/ansible-ssh-audit.log && \
		echo "✓ Лог-файл содержит валидный JSON"; \
	else \
		echo "✗ Лог-файл не найден: /var/log/ansible-ssh-audit.log"; \
		exit 1; \
	fi

# Очистка
clean:
	@echo "Очистка..."
	sudo podman rmi $(IMAGE_NAME):$(IMAGE_TAG) 2>/dev/null || true
	-sudo podman image prune -f
	-sudo rm -f /var/log/ansible-ssh-audit.log

# Запуск всех проверок
all: lint build test log-check

help:
	@echo "Доступные команды:"
	@echo "  make lint      - Проверка синтаксиса Ansible и YAML"
	@echo "  make build     - Сборка Docker образа"
	@echo "  make test      - Запуск тестов в контейнере"
	@echo "  make log-check - Проверка валидности лог-файла"
	@echo "  make clean     - Очистка (удаление образа и логов)"
	@echo "  make all       - Все этапы сразу"