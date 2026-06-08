import asyncio
import uuid

import httpx
from sqlalchemy import select

from app.db.database import AsyncSessionLocal
from app.db.models import ApiKey

BASE_URL = "http://localhost:8000/api/v1"
SESSION_ID = f"sim_{uuid.uuid4().hex[:8]}"

async def ensure_api_key():
    async with AsyncSessionLocal() as session:
        # Перевіряємо чи є хоча б один API ключ
        query = select(ApiKey).limit(1)
        res = await session.execute(query)
        api_key = res.scalar_one_or_none()
        
        if not api_key:
            print("[Система] Створюємо тестовий API ключ...")
            api_key = ApiKey(
                key="test-api-key-123",
                organization_id="org_logistic_pro_1",
                is_active=True
            )
            session.add(api_key)
            await session.commit()
            
        return api_key.key

async def main():
    print("==================================================")
    print("🤖 ZT Dispatch Client Simulator (Gemini AI)")
    print(f"Session ID: {SESSION_ID}")
    print("==================================================")
    
    # 1. Забезпечуємо наявність API ключа в БД
    api_key = await ensure_api_key()
    headers = {"X-API-Key": api_key}
    
    print("\n[Система] Ви симулюєте клієнта. Вводьте свої повідомлення нижче.")
    print("[Система] Введіть 'exit' або 'quit' для виходу.\n")
    
    # 2. Інтерактивний цикл чату
    async with httpx.AsyncClient(timeout=60.0) as client:
        while True:
            text = input("👤 Клієнт: ")
            if text.lower() in ['exit', 'quit']:
                break
            
            if not text.strip():
                continue
                
            payload = {
                "session_id": SESSION_ID,
                "text": text
            }
            
            try:
                res = await client.post(f"{BASE_URL}/chat", json=payload, headers=headers)
                if res.status_code == 200:
                    data = res.json()
                    print(f"🤖 Gemini: {data['response_text']}\n")
                else:
                    print(f"❌ Помилка [{res.status_code}]: {res.text}\n")
            except Exception as e:
                print(f"❌ Помилка з'єднання: {e}\n")

if __name__ == "__main__":
    asyncio.run(main())
