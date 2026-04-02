class SocketManager:
    def __init__(self) -> None:
        self.active_connections: list[object] = []


socket_manager = SocketManager()
