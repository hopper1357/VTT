from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import List
import json

# This is a simplified approach for a CLI application.
# In a larger app, you might use dependency injection.
engine = None

class SessionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {} # client_id to websocket
        self.gm_client_id: str = None

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        if not self.gm_client_id:
            self.gm_client_id = client_id

    def disconnect(self, client_id: str):
        self.active_connections.pop(client_id, None)
        if self.gm_client_id == client_id:
            # In a real app, you'd handle GM disconnect more gracefully.
            # For now, we'll just clear it.
            self.gm_client_id = None

    def is_gm(self, client_id: str) -> bool:
        return self.gm_client_id == client_id

    async def send_personal_message(self, message: dict, client_id: str):
        websocket = self.active_connections.get(client_id)
        if websocket:
            await websocket.send_json(message)

    async def broadcast(self, message: dict, exclude_client_id: str = None):
        for client_id, connection in self.active_connections.items():
            if client_id != exclude_client_id:
                await connection.send_json(message)

def create_app(vtt_engine):
    """Creates the FastAPI app and sets up routes."""
    global engine
    engine = vtt_engine

    app = FastAPI()
    manager = SessionManager()

    @app.websocket("/ws/{client_id}")
    async def websocket_endpoint(websocket: WebSocket, client_id: str):
        await manager.connect(websocket, client_id)

        from .user import User, UserRole

        is_gm = manager.is_gm(client_id)
        role = UserRole.GM if is_gm else UserRole.PLAYER
        user = User(f"Player-{client_id}", role)
        engine.get_user_manager().add_user(user)

        # Send full state to the new client
        game_state = engine.get_persistence_manager().gather_game_state(engine)
        await manager.send_personal_message({"type": "full_state", "payload": game_state}, client_id)
        await manager.broadcast({"type": "chat", "payload": f"{user.username} ({role.name}) has joined."})

        try:
            while True:
                data = await websocket.receive_text()

                original_user = engine.current_user
                engine.current_user = user

                engine.get_command_handler().parse_and_handle(data)

                engine.current_user = original_user

                await manager.broadcast({"type": "command", "payload": data})

        except WebSocketDisconnect:
            manager.disconnect(client_id)
            engine.get_user_manager().remove_user(user.id)
            await manager.broadcast({"type": "chat", "payload": f"{user.username} has left."})

    return app
