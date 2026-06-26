from collections.abc import Iterable

from fastapi import WebSocket


class ConnectionManager:

    def __init__(self) -> None:
        self.rooms: dict[str, set[WebSocket]] = {}
        self.socket_rooms: dict[WebSocket, set[str]] = {}

    async def connect(self, websocket: WebSocket, roles: Iterable[str]) -> None:
        await websocket.accept()
        for role in roles:
            self._join_room(websocket, f"role:{role}")

    def disconnect(self, websocket: WebSocket) -> None:
        for room_name in list(self.socket_rooms.get(websocket, set())):
            self._leave_room(websocket, room_name)
        self.socket_rooms.pop(websocket, None)

    def join_order_room(self, websocket: WebSocket, order_id: int) -> None:
        self._join_room(websocket, f"order:{order_id}")

    def leave_order_room(self, websocket: WebSocket, order_id: int) -> None:
        self._leave_room(websocket, f"order:{order_id}")

    async def send_json(self, websocket: WebSocket, event: str, data: dict) -> None:
        await websocket.send_json({"event": event, "data": data})

    async def broadcast_to_order(self, order_id: int, event: str, data: dict) -> None:
        await self._broadcast_rooms([f"order:{order_id}"], event, data)

    async def broadcast_to_roles(self, roles: Iterable[str], event: str, data: dict) -> None:
        await self._broadcast_rooms([f"role:{role}" for role in roles], event, data)

    async def broadcast_all(self, event: str, data: dict) -> None:
        delivered: set[WebSocket] = set()
        for sockets in self.rooms.values():
            for websocket in list(sockets):
                if websocket not in delivered:
                    await self.send_json(websocket, event, data)
                    delivered.add(websocket)

    def _join_room(self, websocket: WebSocket, room_name: str) -> None:
        self.rooms.setdefault(room_name, set()).add(websocket)
        self.socket_rooms.setdefault(websocket, set()).add(room_name)

    def _leave_room(self, websocket: WebSocket, room_name: str) -> None:
        sockets = self.rooms.get(room_name)
        if sockets is not None:
            sockets.discard(websocket)
            if not sockets:
                self.rooms.pop(room_name, None)

        joined_rooms = self.socket_rooms.get(websocket)
        if joined_rooms is not None:
            joined_rooms.discard(room_name)
            if not joined_rooms:
                self.socket_rooms.pop(websocket, None)

    async def _broadcast_rooms(self, room_names: Iterable[str], event: str, data: dict) -> None:
        delivered: set[WebSocket] = set()
        for room_name in room_names:
            for websocket in list(self.rooms.get(room_name, set())):
                if websocket in delivered:
                    continue
                await self.send_json(websocket, event, data)
                delivered.add(websocket)


manager = ConnectionManager()
