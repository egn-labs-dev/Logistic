import uuid
import json
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, JSON, func, UUID, Boolean
from sqlalchemy.orm import declarative_base, Mapped, mapped_column

Base = declarative_base()

class CargoOrder(Base):
    __tablename__ = "cargo_orders"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    session_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    cargo_details: Mapped[dict] = mapped_column(JSON, nullable=False)  # JSON representation of extracted data
    status: Mapped[str] = mapped_column(String, nullable=False, default="new")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

class ImmutableAuditLog(Base):
    __tablename__ = "audit_logs"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    session_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    clean_prompt: Mapped[str] = mapped_column(Text, nullable=False)  # Anonymized text
    clean_response: Mapped[str] = mapped_column(Text, nullable=False) # Model response with tokens
    vault_snapshot: Mapped[dict] = mapped_column(JSON, nullable=False) # Vault storage for de-anonymization
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

class User(Base):
    """
    Model for logistics company employee (Dispatcher, Admin).
    """
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), default="dispatcher", nullable=False)
    organization_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class ApiKey(Base):
    """
    Model for storing organization API Keys for external widgets.
    """
    __tablename__ = "api_keys"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    key: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class OrganizationSetting(Base):
    """
    Model for storing organization-specific AI settings like custom System Prompts.
    """
    __tablename__ = "organization_settings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    system_prompt: Mapped[str] = mapped_column(Text, nullable=True)
    stripe_item_id: Mapped[str] = mapped_column(String, nullable=True, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

