#!/bin/bash
# Запускати від імені root (sudo)
set -e

echo "🚀 Починаємо налаштування сервера для Zero Trust Dispatch..."

# Оновлення системи
apt-get update && apt-get upgrade -y
apt-get install -y ca-certificates curl gnupg git ufw

# Налаштування Firewall (UFW) - Залишаємо тільки необхідні порти!
ufw allow ssh
ufw allow http
ufw allow https
ufw --force enable

# Встановлення сучасного Docker та Docker Compose
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

echo "✅ Сервер успішно підготовлено! Docker встановлено."
