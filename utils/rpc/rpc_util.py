from pypresence import Presence
import time

from utils.console.logger_util import logger

class DiscordRPC:
    def __init__(self, client_id: str):
        self.client_id = client_id
        self.rpc = Presence(client_id)
        self.start_time = int(time.time())

    def connect(self):
        try:
            self.rpc.connect()
        except Exception as e:
            print(f"[RPC] Failed to connect: {e}")
            return

    def update(self):
        try:
            self.rpc.update(
                details="Excellent Omni",
                state="Разработчик » rare.creation",
                start=self.start_time,
                large_image="icon_rpc.gif",
                large_text="Excellent Omni",
            )
        except Exception as e:
            logger(f"[RPC] Failed to update presence: {e}")

    def start(self):
        self.connect()
        self.update()
