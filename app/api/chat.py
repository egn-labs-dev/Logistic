import json
from fastapi import APIRouter, HTTPException, status, Request, Depends
from app.schemas.chat import IncomingMessage, ChatResponse
from app.security.scrubber import DataScrubber
from app.services.gemini_service import GeminiDispatcherService
from app.db.database import get_db_session_with_rls
from app.db.models import CargoOrder, ImmutableAuditLog
from app.security.rate_limiter import limiter
from app.security.auth import get_current_user_token_data, TokenData

from sqlalchemy import select

router = APIRouter(prefix="/api/v1", tags=["Secure Chat Engine"])
gemini_service = GeminiDispatcherService()

@router.post("/chat", response_model=ChatResponse, status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
async def process_secure_message(
    request: Request,
    payload: IncomingMessage,
    current_user: TokenData = Depends(get_current_user_token_data)
):
    try:
        # Check for human interception before any other actions
        async with get_db_session_with_rls(current_user.organization_id) as session:
            query = select(CargoOrder).where(CargoOrder.session_id == payload.session_id).order_by(CargoOrder.created_at.desc()).limit(1)
            result = await session.execute(query)
            existing_order = result.scalar_one_or_none()
            
            # IF HUMAN INTERCEPTED - completely block AI
            if existing_order and existing_order.status == "human_controlled":
                return ChatResponse(
                    session_id=payload.session_id,
                    response_text="[SYSTEM: AI disabled. Your dialogue has been transferred to a live operator. Please wait for a response...]"
                )

        # Step 1: Local Data Scrubbing (Security barrier entry)
        scrubbed = DataScrubber.anonymize(payload.text)
        
        # Step 2: Pass scrubbed text to Gemini
        llm_output = await gemini_service.analyze_dispatched_text(scrubbed.clean_text)
        
        # Step 3: Asynchronous database writing protected by RLS
        async with get_db_session_with_rls(current_user.organization_id) as session:
            
            # Determine final status based on Gemini's verdict
            if llm_output.requires_human_intervention:
                order_status = "human_required"
            else:
                order_status = "qualified_lead" if llm_output.is_qualified_lead else "active_chat"
            
            # Save structured data to CargoOrder
            new_order = CargoOrder(
                organization_id=current_user.organization_id,
                session_id=payload.session_id,
                cargo_details=json.loads(llm_output.extracted_data.model_dump_json()),
                status=order_status
            )
            session.add(new_order)
            
            # Record Immutable Audit Trail
            audit_entry = ImmutableAuditLog(
                organization_id=current_user.organization_id,
                session_id=payload.session_id,
                clean_prompt=scrubbed.clean_text,
                clean_response=llm_output.response_to_user,
                vault_snapshot=scrubbed.vault
            )
            session.add(audit_entry)

        # Step 4: Deanonymize generated response before sending it to the client
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
