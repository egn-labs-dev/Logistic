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
