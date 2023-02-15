from app.login import LoginWindow
from app.ultimate import UltimateWindow
import asyncio
import platform

class App:
    def __init__(self) -> None:
        self.os = platform.platform().lower()
    
    async def exec(self, dir):
        login = LoginWindow(asyncio.get_event_loop(), dir)
        username = await login.show()
        login.destroy()
        ultimate = UltimateWindow(asyncio.get_event_loop(), dir, self.os, username)
        await ultimate.show()
        ultimate.destroy()
        exit()