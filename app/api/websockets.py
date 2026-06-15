import json
import logging
from typing import Dict, List
import os
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from jose import jwt, JWTError

logger = logging.getLogger(__name__)
router = APIRouter()

# Отримуємо секрети для валідації токенів
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"

class ConnectionManager:
    def __init__(self):
        # Словник для зберігання активних підключень: { "org_id": [websocket1, websocket2] }
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, org_id: str):
        await websocket.accept()
        if org_id not in self.active_connections:
            self.active_connections[org_id] = []
        self.active_connections[org_id].append(websocket)
        logger.info(f"WebSocket підключено для організації {org_id}. Всього клієнтів: {len(self.active_connections[org_id])}")

    def disconnect(self, websocket: WebSocket, org_id: str):
        if org_id in self.active_connections and websocket in self.active_connections[org_id]:
            self.active_connections[org_id].remove(websocket)
            if not self.active_connections[org_id]:
                del self.active_connections[org_id]
            logger.info(f"WebSocket відключено для організації {org_id}.")

    async def broadcast_to_org(self, org_id: str, message: dict):
        """Відправляє повідомлення всім активним диспетчерам конкретної компанії"""
        if org_id in self.active_connections:
            dead_connections = []
            for connection in self.active_connections[org_id]:
                try:
                    await connection.send_text(json.dumps(message))
                except Exception as e:
                    logger.error(f"Помилка відправки WS повідомлення: {str(e)}")
                    dead_connections.append(connection)
            
            # Очищення мертвих підключень
            for dead in dead_connections:
                self.disconnect(dead, org_id)

# Глобальний екземпляр менеджера
ws_manager = ConnectionManager()

@router.websocket("/")
async def websocket_endpoint(websocket: WebSocket, token: str = Query(...)):
    """Ендпоінт для підключення диспетчерів з фронтенду"""
    try:
        # Валідація JWT токена з URL параметра
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        org_id = payload.get("organization_id")
        
        if not org_id:
            await websocket.close(code=1008, reason="Відсутній organization_id у токені")
            return
            
    except JWTError:
        await websocket.close(code=1008, reason="Недійсний токен авторизації")
        return

    # Підключаємо клієнта до кімнати його організації
    await ws_manager.connect(websocket, org_id)
    
    try:
        while True:
            # Утримуємо з'єднання відкритим (тут можна приймати ping/pong, якщо треба)
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, org_id)
