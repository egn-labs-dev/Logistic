# 1. Технічний контекст проекту
**Проект:** B2B логістичний ШІ-диспетчер.
**Стек:** Python, FastAPI, PostgreSQL (із суворим RLS), Alembic.
**Модель:** Gemini 3.1 Flash Lite (через офіційний SDK `google-genai` зі Structured Outputs).
**Ключові механізми:** Локальний Data Scrubbing (анонімізація перед відправкою в ШІ) та Human-in-the-Loop (HITL).

# 2. Актуальний код

**`app/schemas/dispatcher.py`**
```python
from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum

# 1. Енуми для суворої типізації логістичних параметрів
class BodyType(str, Enum):
    TENT = "tent"                  # Тент
    REFRIGERATOR = "refrigerator"  # Рефрижератор
    ISOTHERM = "isotherm"          # Ізотерм
    JUMBO = "jumbo"                # Юмбо (збільшена кубатура)
    OPEN_PLATFORM = "platform"     # Відкрита платформа
    NOT_SPECIFIED = "not_specified"

class TemperatureRegime(BaseModel):
    is_required: bool = Field(False, description="Чи потрібен температурний режим (для рефів)")
    min_celsius: Optional[float] = Field(None, description="Мінімальна температура в градусах Цельсія")
    max_celsius: Optional[float] = Field(None, description="Максимальна температура в градусах Цельсія")

class CargoDimensions(BaseModel):
    length_m: Optional[float] = Field(None, description="Довжина в метрах")
    width_m: Optional[float] = Field(None, description="Ширина в метрах")
    height_m: Optional[float] = Field(None, description="Висота в метрах")
    volume_m3: Optional[float] = Field(None, description="Загальний об'єм в кубічних метрах")

class ADRDetails(BaseModel):
    is_dangerous: bool = Field(False, description="Чи є вантаж небезпечним (ADR)")
    adr_class: Optional[str] = Field(None, description="Клас небезпеки ADR (наприклад, Клас 3 - легкозаймисті рідини)")

# 2. Розширена модель деталей вантажу
class ExtractedCargoDetails(BaseModel):
    departure_city: Optional[str] = Field(None, description="Місто/країна відправлення (наприклад, Варшава, Польща)")
    destination_city: Optional[str] = Field(None, description="Місто/країна доставки")
    cargo_type: Optional[str] = Field(None, description="Детальний опис товару (електроніка, заморожена риба, меблі)")
    weight_tons: Optional[float] = Field(None, description="Загальна вага вантажу в ТОННАХ (якщо вказано в кг — конвертуй у тонни)")
    
    dimensions: CargoDimensions = Field(default_factory=CargoDimensions)
    body_type_required: BodyType = Field(default=BodyType.NOT_SPECIFIED)
    temperature_control: TemperatureRegime = Field(default_factory=TemperatureRegime)
    adr_specification: ADRDetails = Field(default_factory=ADRDetails)
    
    detected_placeholders: List[str] = Field(default=[], description="Знайдені маски, наприклад [PHONE_0]")

# 3. Головний вихідний контейнер для Gemini
class DispatcherLLMOutput(BaseModel):
    is_qualified_lead: bool = Field(..., description="True, якщо є чіткий запит на перевезення вантажу і вказано хоча б маршрут")
    requires_human_intervention: bool = Field(..., description="True, якщо клієнт незадоволений, або запит занадто заплутаний")
    extracted_data: ExtractedCargoDetails
    response_to_user: str = Field(..., description="Ввічлива відповідь користувачу українською мовою з підтвердженням параметрів вантажу.")
```

**`app/services/gemini_service.py`**
```python
import os
import json
from google import genai
from google.genai import types
from app.schemas.dispatcher import DispatcherLLMOutput, ExtractedCargoDetails

class GeminiDispatcherService:
    def __init__(self):
        # Ініціалізація офіційного клієнта. API_KEY береться з системних змінних
        api_key = os.getenv("GEMINI_API_KEY", "YOUR_TEMPORARY_STUB_KEY_FOR_DEV")
        self.client = genai.Client(api_key=api_key)
        # Використовуємо модель згідно твоїх лімітів тарифної сітки
        self.model_name = "gemini-3.1-flash-lite"

    async def analyze_dispatched_text(self, clean_text: str) -> DispatcherLLMOutput:
        system_instruction = (
            "Ти — провідний логістичний ШІ-диспетчер міжнародної експедиторської компанії.\n"
            "Аналізуй вхідний текст та структуруй його згідно з наданою JSON-схемою.\n\n"
            "ПРАВИЛА ВИЗНАЧЕННЯ ПАРАМЕТРІВ:\n"
            "1. Конвертація ваги: Завжди записуй вагу в ТОННАХ у поле weight_tons. Якщо клієнт пише '500 кг', запиши 0.5. Якщо '20 тонн', запиши 20.0.\n"
            "2. Тип кузова (body_type_required): Якщо згадуються продукти, що псуються, або глибока заморозка — виставляй 'refrigerator'. Якщо звичайні коробки чи палети — 'tent'. Якщо вантаж негабаритний або труби — 'platform'.\n"
            "3. Температурний режим: Якщо потрібен рефрижератор, обов'язково заповнюй температурний режим. Якщо клієнт написав '+4', запиши min_celsius=4.0, max_celsius=4.0.\n"
            "4. ADR (Небезпека): Хімія, акумулятори, лаки, фарби, бензин — це небезпечний вантаж. Став embraces_adr=True та вказуй клас, якщо його можна зрозуміти з контексту.\n"
            "5. Безпека: Клієнтські дані анонімізовані масками на кшталт [PHONE_0]. У полі response_to_user відповідай ввічливо, підтверджуй маршрут та параметри вантажу, які ти зміг розпізнати. Якщо згадуєш його контакти, пиши їх суворо маскою [PHONE_0].\n"
            "6. Кваліфікація: Якщо клієнт просто каже 'Привіт' або пише спам — стави запис is_qualified_lead=False."
        )

        user_content = f"<user_input>\n{clean_text}\n</user_input>"

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=user_content,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    response_mime_type="application/json",
                    response_schema=DispatcherLLMOutput,
                    temperature=0.1,
                ),
            )
            data_dict = json.loads(response.text)
            return DispatcherLLMOutput(**data_dict)
        except Exception as e:
            # Наш надійний Fail-safe контур
            return DispatcherLLMOutput(
                is_qualified_lead=False,
                requires_human_intervention=True,
                extracted_data=ExtractedCargoDetails(detected_placeholders=[]),
                response_to_user="Вибачте, виникла технічна затримка при аналізі специфікації вантажу. Передаю діалог оператору."
            )
```

# 3. Поточна задача
Наступна задача: написати pytest-тести для нової бізнес-логіки розпізнавання параметрів вантажу.
