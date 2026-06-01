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
