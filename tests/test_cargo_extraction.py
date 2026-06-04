import pytest
import json
from unittest.mock import patch
from fastapi.testclient import TestClient
from httpx import AsyncClient

from app.main import app
from app.schemas.dispatcher import DispatcherLLMOutput, ExtractedCargoDetails, BodyType, TemperatureRegime, CargoDimensions, ADRDetails

# Приклад того, що мала б повернути Gemini (Мок для тестів без API-ключа)
MOCK_GEMINI_RESPONSE_TEXT = json.dumps({
    "is_qualified_lead": True,
    "requires_human_intervention": False,
    "extracted_data": {
        "departure_city": "Люблін",
        "destination_city": "Одеса",
        "cargo_type": "заморожена курка",
        "weight_tons": 3.0,
        "dimensions": {
            "length_m": 0.0,
            "width_m": 0.0,
            "height_m": 0.0,
            "volume_m3": 0.0
        },
        "body_type_required": "refrigerator",
        "temperature_control": {
            "is_required": True,
            "min_celsius": -18.0,
            "max_celsius": -18.0
        },
        "adr_specification": {
            "is_dangerous": False,
            "adr_class": ""
        },
        "detected_placeholders": ["[PHONE_0]"]
    },
    "response_to_user": "Дякую. Ми зафіксували ваш запит на рефрижератор (3 тонни, заморожена курка) за маршрутом Люблін - Одеса, температурний режим -18°C. Ми зателефонуємо на ваш номер [PHONE_0]."
})


@pytest.mark.asyncio
@patch('app.api.chat.gemini_service.analyze_dispatched_text')
async def test_complex_logistics_extraction(mock_analyze):
    """
    Симуляція того, як Gemini розбирає складний логістичний запит.
    Перевіряємо, що Pydantic схема ідеально валідує відповідь.
    """
    # Налаштовуємо мок методу
    mock_analyze.return_value = DispatcherLLMOutput(**json.loads(MOCK_GEMINI_RESPONSE_TEXT))

    import uuid
    from app.security.auth import get_organization_from_api_key
    
    app.dependency_overrides[get_organization_from_api_key] = lambda: "org_logistics_test"

    random_session = f"session_test_{uuid.uuid4().hex[:8]}"
    payload = {
        "organization_id": "org_logistics_test",
        "session_id": random_session,
        "text": "Потрібно завезти 3 тонни замороженої курки з Любліна до Одеси. Температура потрібна строго -18 градусів. Мій тел +380671112233"
    }
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/v1/chat", json=payload)
        
    app.dependency_overrides.clear()
        
    assert response.status_code == 200
    data = response.json()
    
    # Перевіряємо, що скруббер відновив номер телефону
    assert "+380671112233" in data["response_text"]
    assert "Люблін" in data["response_text"]
    assert "-18" in data["response_text"]

    # Звіримо чи дані потрапили в базу (через мок ми перевірили правильність виводу)
    # Якщо потрібно, можна додати перевірку в БД через сесію.
