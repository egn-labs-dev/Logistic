import asyncio
import os
import secrets

import stripe
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import async_session_maker
from app.db.models import ApiKey, OrganizationSetting

# Налаштування Stripe
stripe.api_key = os.getenv("STRIPE_API_KEY")
STRIPE_PRICE_ID = os.getenv("STRIPE_METERED_PRICE_ID")

def generate_api_key() -> str:
    """Генерує безпечний M2M ключ для віджетів та ботів"""
    return f"sk_live_{secrets.token_urlsafe(32)}"

async def onboard_new_client(company_name: str, admin_email: str):
    """Повний цикл реєстрації нового B2B клієнта"""
    print(f"🚀 Починаємо онбординг для компанії: {company_name}")
    
    # 1. Генерація внутрішніх ідентифікаторів
    tenant_id = company_name.lower().replace(" ", "_")
    new_api_key = generate_api_key()
    
    # 2. Інтеграція зі Stripe (Створення клієнта та підписки)
    try:
        print("💳 Створення акаунту в Stripe...")
        customer = stripe.Customer.create(
            name=company_name,
            email=admin_email,
            metadata={"tenant_id": tenant_id}
        )
        
        print("📦 Оформлення Pay-per-Lead підписки...")
        subscription = stripe.Subscription.create(
            customer=customer.id,
            items=[{"price": STRIPE_PRICE_ID}],
            metadata={"tenant_id": tenant_id}
        )
        # Отримуємо ID конкретного item для запису використання
        stripe_item_id = subscription['items']['data'][0]['id']
    except Exception as e:
        print(f"❌ Помилка інтеграції Stripe: {e}")
        return

    # 3. Запис у нашу Zero Trust Базу Даних
    print("🔐 Налаштування ізольованої бази даних (RLS)...")
    async with async_session_maker() as db:
        # Зберігаємо API ключ
        db_key = ApiKey(
            organization_id=tenant_id,
            key=new_api_key
        )
        db.add(db_key)
        
        # Створюємо базові налаштування (System Prompt + Білінг)
        db_settings = OrganizationSetting(
            organization_id=tenant_id,
            system_prompt="Ви - ввічливий логістичний ШІ-диспетчер. Завжди запитуйте про вагу та маршрут.",
            stripe_item_id=stripe_item_id
        )
        db.add(db_settings)
        
        await db.commit()

    print("\n✅ Онбординг успішно завершено!")
    print("-" * 40)
    print(f"🏢 Тенант ID: {tenant_id}")
    print(f"🔑 API Ключ: {new_api_key}")
    print(f"💳 Stripe Item ID: {stripe_item_id}")
    print("-" * 40)
    print("⚠️ Передайте API Ключ клієнту в безпечний спосіб (наприклад, через 1Password).")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Zero Trust Dispatch - Client Onboarding")
    parser.add_argument("--company", required=True, help="Назва логістичної компанії")
    parser.add_argument("--email", required=True, help="Email адміністратора клієнта")
    args = parser.parse_args()

    if not stripe.api_key or not STRIPE_PRICE_ID:
        print("❌ Помилка: Додайте STRIPE_API_KEY та STRIPE_METERED_PRICE_ID у змінні середовища!")
        exit(1)

    asyncio.run(onboard_new_client(args.company, args.email))
