from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum

# 1. Enums for strict typing of logistics parameters
class BodyType(str, Enum):
    TENT = "tent"                  # Tent
    REFRIGERATOR = "refrigerator"  # Refrigerator
    ISOTHERM = "isotherm"          # Isotherm
    JUMBO = "jumbo"                # Jumbo (increased volume)
    OPEN_PLATFORM = "platform"     # Open platform
    NOT_SPECIFIED = "not_specified"

class TemperatureRegime(BaseModel):
    is_required: bool = Field(description="Is temperature control required (for reefers)")
    min_celsius: float = Field(description="Minimum temperature in degrees Celsius. Return 0.0 if not specified.")
    max_celsius: float = Field(description="Maximum temperature in degrees Celsius. Return 0.0 if not specified.")

class CargoDimensions(BaseModel):
    length_m: float = Field(description="Length in meters. Return 0.0 if not specified.")
    width_m: float = Field(description="Width in meters. Return 0.0 if not specified.")
    height_m: float = Field(description="Height in meters. Return 0.0 if not specified.")
    volume_m3: float = Field(description="Total volume in cubic meters. Return 0.0 if not specified.")

class ADRDetails(BaseModel):
    is_dangerous: bool = Field(description="Is the cargo dangerous (ADR)")
    adr_class: str = Field(description="ADR hazard class (e.g., Class 3 - flammable liquids). Return empty string if not specified.")

# 2. Extended model for cargo details
class ExtractedCargoDetails(BaseModel):
    departure_city: str = Field(description="City/country of departure (e.g., Warsaw, Poland). Return empty string if not specified.")
    destination_city: str = Field(description="City/country of delivery. Return empty string if not specified.")
    cargo_type: str = Field(description="Detailed description of goods (electronics, frozen fish, furniture). Return empty string if not specified.")
    weight_tons: float = Field(description="Total cargo weight in TONS (if specified in kg - convert to tons). Return 0.0 if not specified.")
    
    dimensions: CargoDimensions = Field(description="Cargo dimensions")
    body_type_required: BodyType = Field(description="Required body type")
    temperature_control: TemperatureRegime = Field(description="Temperature regime details")
    adr_specification: ADRDetails = Field(description="ADR details")
    
    detected_placeholders: list[str] = Field(description="Detected masks, e.g., [PHONE_0]. Return empty list if none.")

# 3. Main output container for Gemini
class DispatcherLLMOutput(BaseModel):
    is_qualified_lead: bool = Field(description="True if there is a clear request for cargo transportation and at least a route is specified")
    requires_human_intervention: bool = Field(description="True if the client is dissatisfied or the request is too confusing")
    extracted_data: ExtractedCargoDetails
    response_to_user: str = Field(description="Polite response to the user confirming cargo parameters.")
