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
    is_required: bool = Field(False, description="Is temperature control required (for reefers)")
    min_celsius: Optional[float] = Field(None, description="Minimum temperature in degrees Celsius")
    max_celsius: Optional[float] = Field(None, description="Maximum temperature in degrees Celsius")

class CargoDimensions(BaseModel):
    length_m: Optional[float] = Field(None, description="Length in meters")
    width_m: Optional[float] = Field(None, description="Width in meters")
    height_m: Optional[float] = Field(None, description="Height in meters")
    volume_m3: Optional[float] = Field(None, description="Total volume in cubic meters")

class ADRDetails(BaseModel):
    is_dangerous: bool = Field(False, description="Is the cargo dangerous (ADR)")
    adr_class: Optional[str] = Field(None, description="ADR hazard class (e.g., Class 3 - flammable liquids)")

# 2. Extended model for cargo details
class ExtractedCargoDetails(BaseModel):
    departure_city: Optional[str] = Field(None, description="City/country of departure (e.g., Warsaw, Poland)")
    destination_city: Optional[str] = Field(None, description="City/country of delivery")
    cargo_type: Optional[str] = Field(None, description="Detailed description of goods (electronics, frozen fish, furniture)")
    weight_tons: Optional[float] = Field(None, description="Total cargo weight in TONS (if specified in kg - convert to tons)")
    
    dimensions: CargoDimensions = Field(default_factory=CargoDimensions)
    body_type_required: BodyType = Field(default=BodyType.NOT_SPECIFIED)
    temperature_control: TemperatureRegime = Field(default_factory=TemperatureRegime)
    adr_specification: ADRDetails = Field(default_factory=ADRDetails)
    
    detected_placeholders: List[str] = Field(default=[], description="Detected masks, e.g., [PHONE_0]")

# 3. Main output container for Gemini
class DispatcherLLMOutput(BaseModel):
    is_qualified_lead: bool = Field(..., description="True if there is a clear request for cargo transportation and at least a route is specified")
    requires_human_intervention: bool = Field(..., description="True if the client is dissatisfied or the request is too confusing")
    extracted_data: ExtractedCargoDetails
    response_to_user: str = Field(..., description="Polite response to the user confirming cargo parameters.")
