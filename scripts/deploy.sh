#!/bin/bash
set -e

echo "🚢 Починаємо деплой нової версії Zero Trust Dispatch..."

# 1. Забираємо найновіший код
git pull origin main

# 2. Перезбираємо і перезапускаємо контейнери (без downtime)
docker compose -f docker-compose.prod.yml up --build -d

# 3. Очищаємо старі "завислі" образи, щоб не забивати диск
docker image prune -f

echo "🎉 Деплой успішно завершено! Всі сервіси оновлено."
