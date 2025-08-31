import asyncio
import json

class Server:
    """Handles the server-side networking for the VTT."""

    def __init__(self, host, port, engine):
        self.host = host
        self.port = port
        self.engine = engine
        self._clients = {}  # Maps writer to user_id
        self._server = None

    async def start(self):
        """Starts the server."""
        self._server = await asyncio.start_server(
            self.handle_client, self.host, self.port
        )
        addr = self._server.sockets[0].getsockname()
        print(f"Server started, listening on {addr}")

    async def stop(self):
        """Stops the server."""
        if self._server:
            self._server.close()
            await self._server.wait_closed()
            print("Server stopped.")

    async def handle_client(self, reader, writer):
        """Callback for when a new client connects."""
        addr = writer.get_extra_info('peername')
        print(f"New connection from {addr}")
        # For now, we don't have user authentication, so we just add the writer.
        # In a real app, we'd have a login process.
        self._clients[writer] = None # No user_id yet

        # This needs to be more robust, handling user login, etc.
        # For now, we'll create a temporary user for the connection.
        from .user import User
        temp_user = User(f"Player-{addr[1]}")
        self.engine.get_user_manager().add_user(temp_user)
        self._clients[writer] = temp_user.id

        # Send the current game state to the new client
        game_state = self.engine.get_persistence_manager().gather_game_state(self.engine)
        await self._send(writer, "full_state", game_state)

        try:
            while True:
                data = await reader.readline()
                if not data:
                    break

                message_str = data.decode().strip()
                print(f"Received from {temp_user.username}: {message_str}")

                # The server is the source of truth. It executes the command first.

                # Set the current user for the duration of this command
                original_user = self.engine.current_user
                self.engine.current_user = self.engine.get_user_manager().get_user(self._clients[writer])

                # In a real app, we'd validate the command and user permissions here.
                self.engine.get_command_handler().parse_and_handle(message_str)

                # Revert to the original user (the GM)
                self.engine.current_user = original_user

                # If successful, broadcast the command to all clients so they can sync.
                await self.broadcast(message_str)

        except asyncio.CancelledError:
            pass # Connection closed
        finally:
            print(f"Connection from {addr} closed.")
            del self._clients[writer]
            writer.close()
            await writer.wait_closed()

    async def _send(self, writer, msg_type, payload):
        """Sends a JSON message to a specific client."""
        message = json.dumps({"type": msg_type, "payload": payload})
        writer.write((message + '\n').encode())
        await writer.drain()

    async def broadcast(self, command_string, exclude_writer=None):
        """Broadcasts a command to all connected clients."""
        print(f"Broadcasting command: {command_string}")
        for writer in self._clients:
            if writer is not exclude_writer:
                await self._send(writer, "command", command_string)

from .cli.parser import CommandParser

class Client:
    """Handles the client-side networking for the VTT."""

    def __init__(self, host, port, engine):
        self.host = host
        self.port = port
        self.engine = engine
        self._reader = None
        self._writer = None

    async def connect(self):
        """Connects to the server."""
        try:
            self._reader, self._writer = await asyncio.open_connection(
                self.host, self.port
            )
            print(f"Successfully connected to {self.host}:{self.port}")
            return True
        except ConnectionRefusedError:
            print(f"Error: Connection refused. Is the server running at {self.host}:{self.port}?")
            return False

    async def disconnect(self):
        """Disconnects from the server."""
        if self._writer:
            self._writer.close()
            await self._writer.wait_closed()
            print("Disconnected from server.")

    async def send_message(self, message):
        """Sends a message to the server."""
        if self._writer:
            encoded_message = (message + '\n').encode()
            self._writer.write(encoded_message)
            await self._writer.drain()

    async def listen(self):
        """Listens for incoming messages from the server."""
        handler = self.engine.get_command_handler()
        try:
            while True:
                data = await self._reader.readline()
                if not data:
                    print("Connection to server lost.")
                    break

                try:
                    message = json.loads(data.decode().strip())
                    msg_type = message.get("type")
                    payload = message.get("payload")

                    if msg_type == "full_state":
                        print("\n<-- Received full game state. Loading...")
                        self.engine.load_game_from_dict(payload)
                        print("> ", end="")

                    elif msg_type == "command":
                        print(f"\n<-- Received command: {payload}")
                        handler.parse_and_handle(payload)
                        print("> ", end="")

                except json.JSONDecodeError:
                    print(f"\n<-- Received malformed message: {data.decode().strip()}")

        except asyncio.CancelledError:
            pass # Listener stopped
        finally:
            print("Stopped listening to server.")
