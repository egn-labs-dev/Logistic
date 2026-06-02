import json
from fastapi import APIRouter, HTTPException, status, Request
from app.schemas.chat import IncomingMessage, ChatResponse
from app.security.scrubber import DataScrubber
from app.services.gemini_service import GeminiDispatcherService
from app.db.database import get_db_session_with_rls
from app.db.models import CargoOrder, ImmutableAuditLog
from app.security.rate_limiter import limiter

from sqlalchemy import select

router = APIRouter(prefix="/api/v1", tags=["Secure Chat Engine"])
gemini_service = GeminiDispatcherService()

@router.post("/chat", response_model=ChatResponse, status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
async def process_secure_message(request: Request, payload: IncomingMessage):
    try:
        # Перевірка на перехоплення людиною перед будь-якими іншими діями
        async with get_db_session_with_rls(payload.organization_id) as session:
            query = select(CargoOrder).where(CargoOrder.session_id == payload.session_id).order_by(CargoOrder.created_at.desc()).limit(1)
            result = await session.execute(query)
            existing_order = result.scalar_one_or_none()
            
            # ЯКЩО ЧАТ ПЕРЕХОПИЛА ЛЮДИНА — повністю блокуємо ШІ
            if existing_order and existing_order.status == "human_controlled":
                return ChatResponse(
                    session_id=payload.session_id,
                    response_text="[SYSTEM: ШІ вимкнено. Ваш діалог переведено на живого оператора. Очікуйте відповіді...]"
                )

        # Крок 1: Локальний Data Scrubbing (Вхідний бар'єр безпеки)
        scrubbed = DataScrubber.anonymize(payload.text)
        
        # Крок 2: Передача очищеного тексту в Gemini
        llm_output = await gemini_service.analyze_dispatched_text(scrubbed.clean_text)
        
        # Крок 3: Асинхронний запис у базу даних під захистом RLS
        async with get_db_session_with_rls(payload.organization_id) as session:
            
            # Визначаємо фінальний статус на основі вердикту Gemini
            if llm_output.requires_human_intervention:
                order_status = "human_required"
            else:
                order_status = "qualified_lead" if llm_output.is_qualified_lead else "active_chat"
            
            # Зберігаємо структуровані дані у CargoOrder
            new_order = CargoOrder(
                organization_id=payload.organization_id,
                session_id=payload.session_id,
                cargo_details=json.loads(llm_output.extracted_data.model_dump_json()),
                status=order_status
            )
            session.add(new_order)
            
            # Фіксуємо Immutable Audit Trail
            audit_entry = ImmutableAuditLog(
                organization_id=payload.organization_id,
                session_id=payload.session_id,
                clean_prompt=scrubbed.clean_text,
                clean_response=llm_output.response_to_user,
                vault_snapshot=scrubbed.vault
            )
            session.add(audit_entry)

        # Крок 4: Деанонімізація згенерованої відповіді перед відправкою клієнту
        final_response_text = DataScrubber.deanonymize(llm_output.response_to_user, scrubbed.vault)
        
        return ChatResponse(
            session_id=payload.session_id,
            response_text=final_response_text
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Secure Gemini pipeline failure: {str(e)}"
        )
