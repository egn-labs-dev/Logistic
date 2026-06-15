import json
import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select

from app.db.database import get_db_session_with_rls
from app.db.models import CargoOrder, ImmutableAuditLog, OrganizationSetting
from app.schemas.chat import ChatResponse, IncomingMessage
from app.security.auth import get_organization_from_api_key
from app.security.rate_limiter import limiter
from app.security.injection_shield import validate_against_injection
from app.security.scrubber import DataScrubber
from app.services.gemini_service import GeminiDispatcherService
from app.api.websockets import ws_manager

router = APIRouter(prefix="/api/v1", tags=["Secure Chat Engine"])
gemini_service = GeminiDispatcherService()

@router.post("/chat", response_model=ChatResponse, status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
async def process_secure_message(
    request: Request,
    payload: IncomingMessage,
    organization_id: str = Depends(get_organization_from_api_key)
):
    try:
        # Check for human interception before any other actions
        async with get_db_session_with_rls(organization_id) as session:
            query = select(CargoOrder).where(CargoOrder.session_id == payload.session_id).order_by(CargoOrder.created_at.desc()).limit(1)
            result = await session.execute(query)
            existing_order = result.scalar_one_or_none()
            
            # IF HUMAN INTERCEPTED - completely block AI
            if existing_order and existing_order.status == "human_controlled":
                return ChatResponse(
                    session_id=payload.session_id,
                    response_text="[SYSTEM: AI disabled. Your dialogue has been transferred to a live operator. Please wait for a response...]"
                )
            
            # Fetch custom system prompt if it exists
            prompt_query = select(OrganizationSetting).where(OrganizationSetting.organization_id == organization_id)
            prompt_res = await session.execute(prompt_query)
            org_setting = prompt_res.scalar_one_or_none()
            custom_prompt = org_setting.system_prompt if org_setting else None

        # Security and LLM Processing Block
        is_security_violation = False
        final_response_text = ""
        order_status = "active_chat"
        extracted_data_dump = "{}"
        clean_text_for_audit = payload.text
        vault_snapshot_for_audit = {}

        try:
            # Step 0: Prompt Injection Shield
            validate_against_injection(payload.text)

            # Step 1: Local Data Scrubbing
            scrubbed = DataScrubber.anonymize(payload.text)
            clean_text_for_audit = scrubbed.clean_text
            vault_snapshot_for_audit = scrubbed.vault
            
            # Step 2: Pass scrubbed text to Gemini
            llm_output = await gemini_service.analyze_dispatched_text(scrubbed.clean_text, custom_prompt)
            
            if llm_output.requires_human_intervention:
                order_status = "human_required"
            else:
                order_status = "qualified_lead" if llm_output.is_qualified_lead else "active_chat"
                
            extracted_data_dump = llm_output.extracted_data.model_dump_json()
            final_response_text = DataScrubber.deanonymize(llm_output.response_to_user, scrubbed.vault)
            
        except HTTPException as he:
            if he.status_code == 400:
                is_security_violation = True
                order_status = "human_required"
                final_response_text = "🚨 [Security System] Спроба маніпуляції заблокована. Запит відхилено."
                extracted_data_dump = json.dumps({"error": "Prompt Injection Detected", "raw_input": payload.text})
            else:
                raise he

        # Step 3: Asynchronous database writing protected by RLS
        async with get_db_session_with_rls(organization_id) as session:
            # Save structured data to CargoOrder
            new_order = CargoOrder(
                organization_id=organization_id,
                session_id=payload.session_id,
                cargo_details=json.loads(extracted_data_dump),
                status=order_status
            )
            session.add(new_order)
            
            # Record Immutable Audit Trail
            audit_entry = ImmutableAuditLog(
                organization_id=organization_id,
                session_id=payload.session_id,
                clean_prompt=clean_text_for_audit if not is_security_violation else "BLOCKED: Prompt Injection",
                clean_response=final_response_text,
                vault_snapshot=vault_snapshot_for_audit
            )
            session.add(audit_entry)

        # [НОВИЙ КОД] Відправляємо Push-сповіщення диспетчерам
        if order_status == "human_required":
            await ws_manager.broadcast_to_org(
                organization_id,
                {
                    "type": "NEW_ALERT",
                    "payload": {
                        "session_id": payload.session_id,
                        "status": order_status,
                        "driver_id": payload.session_id,
                        "message_preview": payload.text[:50] + "..."
                    }
                }
            )

        return ChatResponse(
            session_id=payload.session_id,
            response_text=final_response_text
        )
        
    except Exception as e:
        logging.getLogger(__name__).error(f"Secure pipeline failure: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal error occurred while processing your request. Please try again later."
        )
