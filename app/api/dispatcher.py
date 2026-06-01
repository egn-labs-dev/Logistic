from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from app.db.database import get_db_session_with_rls
from app.db.models import CargoOrder
from sqlalchemy import select, update

router = APIRouter(prefix="/api/v1/dispatcher", tags=["Dispatcher Console (HITL)"])

class InterceptPayload(BaseModel):
    organization_id: str
    session_id: str

@router.get("/alerts", status_code=status.HTTP_200_OK)
async def get_alerts_for_human(organization_id: str):
    """Повертає список замовлень, які потребують термінового втручання людини"""
    async with get_db_session_with_rls(organization_id) as session:
        query = select(CargoOrder).where(
            CargoOrder.status == "human_required"
        )
        result = await session.execute(query)
        orders = result.scalars().all()
        return [{"id": str(o.id), "session_id": o.session_id, "status": o.status} for o in orders]

@router.post("/intercept", status_code=status.HTTP_200_OK)
async def intercept_chat(payload: InterceptPayload):
    """Оператор примусово перехоплює чат, вимикаючи ШІ для цієї сесії"""
    async with get_db_session_with_rls(payload.organization_id) as session:
        query = (
            update(CargoOrder)
            .where(CargoOrder.session_id == payload.session_id)
            .values(status="human_controlled")
        )
        await session.execute(query)
        return {"status": "success", "message": f"Chat {payload.session_id} transferred to human."}
