import os
import json
from sqlalchemy import Column, String, Text, DateTime, JSON, func
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class CargoOrder(Base):
    __tablename__ = "cargo_orders"

    id = Column(String, primary_key=True, default=lambda: os.urandom(16).hex())
    organization_id = Column(String, index=True, nullable=False)
    session_id = Column(String, index=True, nullable=False)
    cargo_details = Column(JSON, nullable=False)  # JSON representation of extracted data
    status = Column(String, nullable=False, default="new")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ImmutableAuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(String, primary_key=True, default=lambda: os.urandom(16).hex())
    organization_id = Column(String, index=True, nullable=False)
    session_id = Column(String, index=True, nullable=False)
    clean_prompt = Column(Text, nullable=False)  # Anonymized text
    clean_response = Column(Text, nullable=False) # Model response with tokens
    vault_snapshot = Column(JSON, nullable=False) # Vault storage for de-anonymization
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

import uuid
from datetime import datetime
from sqlalchemy import Boolean, UUID
from sqlalchemy.orm import Mapped, mapped_column

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
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
