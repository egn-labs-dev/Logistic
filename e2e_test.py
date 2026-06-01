import asyncio
import os
import httpx
from sqlalchemy import select
from app.db.database import AsyncSessionLocal
from app.db.models import User, CargoOrder, ImmutableAuditLog

BASE_URL = "http://127.0.0.1:8000/api/v1"

async def main():
    # 1. Fetch dispatcher credentials or create one if not exists
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.role == "dispatcher").limit(1))
        user = result.scalar_one_or_none()
        
        if not user:
            print("Creating default dispatcher...")
            from app.security.auth import get_password_hash
            user = User(
                email="dispatcher@cargo.com",
                hashed_password=get_password_hash("securepassword"),
                role="dispatcher",
                organization_id="org_logistic_pro_1"
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
            
        print(f"Using dispatcher: {user.email} (Org: {user.organization_id})")
        org_id = user.organization_id
        
        # 2. Login dispatcher
        async with httpx.AsyncClient() as client:
            # We don't know the plain password, but we know it from earlier sessions: "securepassword"
            login_data = {"username": user.email, "password": "securepassword"}
            res = await client.post(f"{BASE_URL}/auth/login", data=login_data)
            
            if res.status_code != 200:
                print("Failed to login as dispatcher:", res.text)
                return
                
            token = res.json()["access_token"]
            print(f"Logged in successfully. Token: {token[:15]}...")
            
            headers = {"Authorization": f"Bearer {token}"}
            
            # 3. Simulate Client Panic Message
            print("\n--- SIMULATING CLIENT PANIC (HITL TRIGGER) ---")
            payload = {
                "organization_id": org_id,
                "session_id": "test_e2e_session",
                "text": "Терміново! Важливий ADR-вантаж, температура має бути +5, але я боюся, що машина не приїде за моїм номером 099-123-45-67, мені потрібна гарантія!"
            }
            chat_res = await client.post(f"{BASE_URL}/chat", json=payload)
            print("Chat Response:", chat_res.json())
            
            # 4. Check Alerts via Dispatcher API
            print("\n--- FETCHING ALERTS ---")
            alerts_res = await client.get(f"{BASE_URL}/dispatcher/alerts", headers=headers)
            alerts = alerts_res.json()
            print("Alerts:", alerts)
            
            target_alert = next((a for a in alerts if a["session_id"] == "test_e2e_session"), None)
            if not target_alert:
                print("Alert not found! E2E failed.")
                return
                
            print(f"Alert found: {target_alert}")
            
            # 5. Dispatcher Intercepts
            print("\n--- INTERCEPTING SESSION ---")
            intercept_res = await client.post(f"{BASE_URL}/dispatcher/intercept", json={"session_id": "test_e2e_session"}, headers=headers)
            print("Intercept Response:", intercept_res.json())
            
            # 6. Dispatcher Reads History (De-anonymization)
            print("\n--- READING DEANONYMIZED HISTORY ---")
            history_res = await client.get(f"{BASE_URL}/dispatcher/history/test_e2e_session", headers=headers)
            print("History:")
            for msg in history_res.json():
                print(f"  [{msg['role'].upper()}] {msg['text']}")
                
            # 7. Dispatcher Sends Manual Message
            print("\n--- SENDING MANUAL MESSAGE ---")
            send_res = await client.post(f"{BASE_URL}/dispatcher/send", json={"session_id": "test_e2e_session", "message": "Доброго дня! Я ваш оператор. Щодо вашого ADR-вантажу, я особисто контролюю вибір рефрижератора з датчиком температури. Ви можете бути спокійні, ми гарантуємо подачу машини на номер 099-123-45-67."}, headers=headers)
            print("Send Response:", send_res.json())
            
            # 8. Check Database Audit Logs
            print("\n--- CHECKING IMMUTABLE AUDIT LOGS IN DATABASE ---")
            query = select(ImmutableAuditLog).where(ImmutableAuditLog.session_id == "test_e2e_session").order_by(ImmutableAuditLog.timestamp.asc())
            logs = (await session.execute(query)).scalars().all()
            for log in logs:
                print(f"Log ID: {log.id}")
                print(f"  Clean Prompt: {log.clean_prompt}")
                print(f"  Clean Response: {log.clean_response}")
                print(f"  Vault: {log.vault_snapshot}")

if __name__ == "__main__":
    asyncio.run(main())
