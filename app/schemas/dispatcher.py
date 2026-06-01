from pydantic import BaseModel, Field
from typing import Optional, List

class ExtractedCargoDetails(BaseModel):
    departure_city: Optional[str] = Field(None, description="Місто відправлення (наприклад, Варшава)")
    destination_city: Optional[str] = Field(None, description="Місто доставки")
    cargo_type: Optional[str] = Field(None, description="Тип вантажу (коробки, палети, насипний тощо)")
    weight_kg: Optional[float] = Field(None, description="Вага вантажу в кілограмах, якщо вказана")
    volume_m3: Optional[float] = Field(None, description="Об'єм вантажу в кубічних метрах, якщо вказано")
    detected_placeholders: List[str] = Field(
        default=[], 
        description="Список виявлених масок анонімізації, наприклад [PHONE_0], [EMAIL_0]"
    )

class DispatcherLLMOutput(BaseModel):
    is_qualified_lead: bool = Field(
        ..., 
        description="True, якщо запит містить реальний намір відправити вантаж і достатньо даних для старту"
    )
    requires_human_intervention: bool = Field(
        ..., 
        description="True, якщо клієнт незадоволений, ставить занадто складні питання, або ШІ не впевнений у відповіді"
    )
    extracted_data: ExtractedCargoDetails
    response_to_user: str = Field(
        ..., 
        description="Ввічлива відповідь клієнту з підтвердженням параметрів вантажу. Використовуй маски анонімізації, якщо згадуєш контакти!"
    )
