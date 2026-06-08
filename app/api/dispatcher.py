from datetime import datetime, timedelta
from collections import defaultdict
from fastapi import APIRouter, HTTPException, status, Depends, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy import select, update, func, cast, Integer
from app.db.database import get_db_session_with_rls
from app.db.models import CargoOrder, ImmutableAuditLog
from app.security.auth import TokenData, get_current_user_token_data, require_dispatcher_role
from app.security.scrubber import DataScrubber
from app.services.billing import report_successful_lead_to_stripe

router = APIRouter(prefix="/api/v1/dispatcher", tags=["Dispatcher Console (HITL)"])

# --- UPDATED SECURE ENDPOINTS ---

class InterceptPayload(BaseModel):
    session_id: str
    # organization_id is no longer passed in the request body! It is securely extracted from the token.

@router.get("/alerts", status_code=status.HTTP_200_OK)
async def get_alerts_for_human(current_user: TokenData = Depends(require_dispatcher_role)):
    """Returns a list of orders for the dispatcher. Data is isolated by the organization from the token."""
    async with get_db_session_with_rls(current_user.organization_id) as session:
        query = select(CargoOrder).where(CargoOrder.status.in_(["human_required", "human_controlled"]))
        result = await session.execute(query)
        orders = result.scalars().all()
        return [{"id": str(o.id), "session_id": o.session_id, "status": o.status} for o in orders]

@router.post("/intercept", status_code=status.HTTP_200_OK)
async def intercept_chat(payload: InterceptPayload, current_user: TokenData = Depends(require_dispatcher_role)):
    """The operator intercepts the chat. RLS ensures they cannot intercept a chat from another organization."""
    async with get_db_session_with_rls(current_user.organization_id) as session:
        query = (
            update(CargoOrder)
            .where(CargoOrder.session_id == payload.session_id)
            .values(status="human_controlled")
        )
        await session.execute(query)
        return {"status": "success", "message": f"Chat {payload.session_id} securely transferred to human."}

@router.get("/history/{session_id}", status_code=status.HTTP_200_OK)
async def get_chat_history(session_id: str, current_user: TokenData = Depends(require_dispatcher_role)):
    """
    Returns the chat history for a specific session with on-the-fly de-anonymization.
    """
    async with get_db_session_with_rls(current_user.organization_id) as session:
        query = select(ImmutableAuditLog).where(
            ImmutableAuditLog.session_id == session_id
        ).order_by(ImmutableAuditLog.timestamp.asc())
        
        result = await session.execute(query)
        logs = result.scalars().all()
        
        history = []
        for log in logs:
            if log.clean_prompt == "[MANUAL_OPERATOR]":
                clean_response = DataScrubber.deanonymize(log.clean_response, log.vault_snapshot)
                history.append({"role": "assistant", "text": f"[MANUAL_OPERATOR]{clean_response}", "timestamp": log.timestamp})
            else:
                clean_prompt = DataScrubber.deanonymize(log.clean_prompt, log.vault_snapshot)
                clean_response = DataScrubber.deanonymize(log.clean_response, log.vault_snapshot)
                history.append({"role": "user", "text": clean_prompt, "timestamp": log.timestamp})
                history.append({"role": "assistant", "text": clean_response, "timestamp": log.timestamp})
            
        return history

class ManualMessage(BaseModel):
    session_id: str
    message: str

@router.post("/send", status_code=status.HTTP_200_OK)
async def send_manual_message(msg: ManualMessage, current_user: TokenData = Depends(require_dispatcher_role)):
    async with get_db_session_with_rls(current_user.organization_id) as session:
        # 1. Check if the chat is actually intercepted
        query = select(CargoOrder).where(CargoOrder.session_id == msg.session_id).limit(1)
        order = (await session.execute(query)).scalar_one_or_none()
        
        if order and order.status != "human_controlled":
             raise HTTPException(status_code=400, detail="Chat is not in human-controlled mode")
        
        # 2. Log the dispatcher's message in the Audit Log (as a response)
        audit_entry = ImmutableAuditLog(
            organization_id=current_user.organization_id,
            session_id=msg.session_id,
            clean_prompt="[MANUAL_OPERATOR]",
            clean_response=msg.message,
            vault_snapshot={} # No masking required for operator messages
        )
        session.add(audit_entry)
        
        return {"status": "sent"}

@router.get("/stats", status_code=status.HTTP_200_OK)
async def get_analytics_stats(current_user: TokenData = Depends(require_dispatcher_role)):
    async with get_db_session_with_rls(current_user.organization_id) as session:
        # SQL Aggregation for efficiency
        query = select(
            func.count(CargoOrder.id).label("total"),
            func.sum(cast(CargoOrder.status == "human_required", Integer)).label("active"),
            func.sum(cast(CargoOrder.status == "human_controlled", Integer)).label("controlled")
        )
        result = await session.execute(query)
        stats_row = result.fetchone()
        
        total_sessions = stats_row.total or 0
        active_incidents = stats_row.active or 0
        controlled_incidents = stats_row.controlled or 0
        autonomous_sessions = total_sessions - active_incidents - controlled_incidents
        
        autonomy_rate = (autonomous_sessions / total_sessions * 100) if total_sessions > 0 else 100
        cost_savings_hours = autonomous_sessions * 0.25
        
        # Fetch logs for the chart (last 7 days)
        # Using Python aggregation to be safe across SQL dialects (SQLite vs Postgres)
        logs_query = select(ImmutableAuditLog)
        logs_result = await session.execute(logs_query)
        logs = logs_result.scalars().all()
        
        chart_data_map = defaultdict(lambda: {"autonomous": 0, "manual": 0})
        
        hitl_response_times = []
        incident_start_times = {}

        for log in logs:
            if not log.timestamp:
                continue
            day_str = log.timestamp.strftime("%m-%d")
            if "[MANUAL_OPERATOR]" in log.clean_prompt:
                chart_data_map[day_str]["manual"] += 1
                if log.session_id in incident_start_times:
                    start_time = incident_start_times.pop(log.session_id)
                    diff = (log.timestamp - start_time).total_seconds()
                    hitl_response_times.append(diff)
            else:
                chart_data_map[day_str]["autonomous"] += 1
                if log.session_id not in incident_start_times:
                    incident_start_times[log.session_id] = log.timestamp
                    
        avg_response_str = "N/A"
        if hitl_response_times:
            avg_secs = sum(hitl_response_times) / len(hitl_response_times)
            avg_mins = int(avg_secs // 60)
            avg_rem_secs = int(avg_secs % 60)
            avg_response_str = f"{avg_mins}m {avg_rem_secs}s"
                
        # Format for Recharts
        chart_data = []
        for day, counts in sorted(chart_data_map.items()):
            chart_data.append({
                "day": day,
                "autonomous": counts["autonomous"],
                "manual": counts["manual"]
            })
            
        return {
            "autonomy_rate": round(autonomy_rate, 1),
            "hitl_response_time": avg_response_str,
            "active_incidents": active_incidents,
            "cost_savings_hours": round(cost_savings_hours, 1),
            "chart_data": chart_data
        }

class ResolveRequest(BaseModel):
    session_id: str
    resolution_status: str

@router.post("/resolve", status_code=status.HTTP_200_OK)
async def resolve_incident(
    payload: ResolveRequest,
    background_tasks: BackgroundTasks,
    current_user: TokenData = Depends(require_dispatcher_role)
):
    """Закриття чату диспетчером (Deal Won / Deal Lost)"""
    tenant_id = current_user.organization_id
    
    async with get_db_session_with_rls(tenant_id) as session:
        query = (
            update(CargoOrder)
            .where(CargoOrder.session_id == payload.session_id)
            .values(status=payload.resolution_status)
        )
        await session.execute(query)
    
    # Реєстрація платіжної події (Тільки для успішних угод!)
    if payload.resolution_status == "resolved_won":
        background_tasks.add_task(report_successful_lead_to_stripe, tenant_id, payload.session_id)
    
    return {"detail": f"Session resolved as {payload.resolution_status}"}
