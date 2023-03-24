import asyncio
import platform
from application.login import LoginWindow
from application.ultimate import UltimateWindow

class Entry:
    def __init__(self) -> None:
        self.os = platform.platform().lower()
    
    async def exec(self, dir):
        self.login = LoginWindow(asyncio.get_event_loop(), dir)
        username = await self.login.show()
        self.login.destroy()
        self.ultimate = UltimateWindow(asyncio.get_event_loop(), dir, self.os, username)
        await self.ultimate.show()
        self.ultimate.destroy()
        exit()