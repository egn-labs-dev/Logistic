import pytest
import uuid
from fastapi.testclient import TestClient
from httpx import AsyncClient
import json

from app.main import app
from app.security.scrubber import DataScrubber
from app.security.auth import create_access_token

# Створюємо базовий синхронний клієнт для швидких перевірок
client = TestClient(app)

# --- БЛОК 1: ТЕСТУВАННЯ DATA SCRUBBING (ЮНІТ-ТЕСТ) ---
def test_data_scrubber_anonymization():
    """Перевірка, що локальний скруббер коректно маскує телефони та email"""
    raw_text = "Привіт, я Дмитро, мій тел +380991234567, пошта test@cargo.com. Треба фура."
    
    scrubbed = DataScrubber.anonymize(raw_text)
    
    # Перевіряємо, що реальних даних немає в очищеному тексті
    assert "+380991234567" not in scrubbed.clean_text
    assert "test@cargo.com" not in scrubbed.clean_text
    # Перевіряємо наявність правильних масок
    assert "[PHONE_0]" in scrubbed.clean_text
    assert "[EMAIL_0]" in scrubbed.clean_text
    # Перевіряємо, що дані збереглися у сейфі (vault)
    assert scrubbed.vault["[PHONE_0]"] == "+380991234567"
    assert scrubbed.vault["[EMAIL_0]"] == "test@cargo.com"

def test_data_scrubber_deanonymization():
    """Перевірка, що скруббер коректно відновлює дані у відповіді для клієнта"""
    llm_response = "Ми зафіксували ваш контактний телефон [PHONE_0]. Чекайте дзвінка."
    vault = {"[PHONE_0]": "+380991234567"}
    
    restored = DataScrubber.deanonymize(llm_response, vault)
    
    assert restored == "Ми зафіксували ваш контактний телефон +380991234567. Чекайте дзвінка."


# --- БЛОК 2: ІНТЕГРАЦІЙНИЙ ТЕСТ API ТА FAIL-SAFE ---
@pytest.mark.asyncio
async def test_chat_endpoint_fail_safe_and_restoration():
    """
    Інтеграційний тест контуру /chat.
    Перевіряє, що при відсутності ключа (заглушці) спрацьовує Fail-safe,
    але скруббінг та повернення структури працюють коректно.
    """
    payload = {
        "organization_id": "org_test_metrics",
        "session_id": "session_pytest_999",
        "text": "Вантаж з Києва. Мій тел +380670000000"
    }
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/v1/chat", json=payload)
        
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert data["session_id"] == "session_pytest_999"
    # Оскільки ключ Gemini пустий, має повернутися наш безпечний дефолтний текст
    assert "Вибачте, виникла технічна затримка при аналізі специфікації вантажу" in data["response_text"]


# --- БЛОК 3: ТЕСТУВАННЯ HUMAN-IN-THE-LOOP (HITL) ---
@pytest.mark.asyncio
async def test_dispatcher_intercept_flow():
    """
    Тест перевіряє логіку перехоплення чату АВТОРИЗОВАНИМ диспетчером.
    1. Генерується валідний JWT токен диспетчера.
    2. Оператор викликає /intercept з Bearer токеном.
    3. Наступний запит від користувача в /chat має миттєво заблокувати ШІ.
    """
    org_id = "org_intercept_test"
    sess_id = "session_hitl_888"
    mock_user_id = str(uuid.uuid4())
    
    # Створюємо валідний JWT токен для тестування (імітація успішного логіну)
    valid_token = create_access_token(
        data={"sub": mock_user_id, "role": "dispatcher", "org_id": org_id}
    )
    auth_headers = {"Authorization": f"Bearer {valid_token}"}
    
    # В payload для перехоплення більше не передаємо organization_id (береться з токена)
    intercept_payload = {
        "session_id": sess_id
    }
    
    user_payload = {
        "organization_id": org_id,
        "session_id": sess_id,
        "text": "Ей, тут є хтось? Мені потрібна машина!"
    }
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Крок 0: Симулюємо перший запит, щоб створити сесію в БД
        await ac.post("/api/v1/chat", json=user_payload)
        
        # Крок 1: Симулюємо примусове перехоплення чату АВТОРИЗОВАНИМ оператором
        intercept_res = await ac.post(
            "/api/v1/dispatcher/intercept", 
            json=intercept_payload, 
            headers=auth_headers
        )
        assert intercept_res.status_code == 200
        assert intercept_res.json()["status"] == "success"
        
        # Крок 2: Надсилаємо повідомлення від користувача в цей же чат (публічний ендпоінт)
        chat_res = await ac.post("/api/v1/chat", json=user_payload)
        
    assert chat_res.status_code == 200
    chat_data = chat_res.json()
    # Система повинна віддати системний HITL-варнінг замість звернення до ШІ
    assert "[SYSTEM: ШІ вимкнено" in chat_data["response_text"]

    # Крок 3: Перевірка захисту (спроба перехоплення БЕЗ токена)
    async with AsyncClient(app=app, base_url="http://test") as ac:
        unauth_res = await ac.post("/api/v1/dispatcher/intercept", json=intercept_payload)
        assert unauth_res.status_code == 401
