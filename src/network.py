import asyncio
import json
import websockets
import uuid
class Client:
    """Handles the client-side networking for the VTT."""

    def __init__(self, host, port, engine):
        self.host = host
        self.port = port
        self.engine = engine
        self.client_id = str(uuid.uuid4())
        self.uri = f"ws://{self.host}:{self.port}/ws/{self.client_id}"
        self._websocket = None

    async def connect(self):
        """Connects to the server."""
        try:
            self._websocket = await websockets.connect(self.uri)
            print(f"Successfully connected to {self.uri}")
            return True
        except ConnectionRefusedError:
            print(f"Error: Connection refused. Is the server running at {self.host}:{self.port}?")
            return False
        except Exception as e:
            print(f"An error occurred: {e}")
            return False

    async def disconnect(self):
        """Disconnects from the server."""
        if self._websocket:
            await self._websocket.close()
            print("Disconnected from server.")

    async def send_message(self, message):
        """Sends a message to the server."""
        if self._websocket:
            await self._websocket.send(message)

    async def listen(self):
        """Listens for incoming messages from the server."""
        handler = self.engine.get_command_handler()
        try:
            async for message in self._websocket:
                try:
                    data = json.loads(message)
                    msg_type = data.get("type")
                    payload = data.get("payload")

                    if msg_type == "full_state":
                        print("\n<-- Received full game state. Loading...")
                        self.engine.load_game_from_dict(payload)
                        print("> ", end="")

                    elif msg_type == "command":
                        print(f"\n<-- Received command: {payload}")
                        handler.parse_and_handle(payload)
                        print("> ", end="")

                    elif msg_type == "chat":
                        print(f"\n<-- Server: {payload}\n> ", end="")

                except json.JSONDecodeError:
                    print(f"\n<-- Received malformed message: {message}")
        except websockets.exceptions.ConnectionClosed:
            print("Connection to server lost.")
        except asyncio.CancelledError:
            pass # Listener stopped
        finally:
            print("Stopped listening to server.")
