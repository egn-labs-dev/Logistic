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
    cargo_details = Column(JSON, nullable=False)  # JSON-представлення витягнутих даних
    status = Column(String, nullable=False, default="new")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ImmutableAuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(String, primary_key=True, default=lambda: os.urandom(16).hex())
    organization_id = Column(String, index=True, nullable=False)
    session_id = Column(String, index=True, nullable=False)
    clean_prompt = Column(Text, nullable=False)  # Анонімізований текст
    clean_response = Column(Text, nullable=False) # Відповідь моделі з токенами
    vault_snapshot = Column(JSON, nullable=False) # Сховище для підстановки
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
