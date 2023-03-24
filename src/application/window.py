from tkinter import Tk
from asyncio import AbstractEventLoop

class Window:
    def __init__(self, loop, dir) -> None:
        self.loop: AbstractEventLoop = loop
        self.dir = dir
        self.window = Tk()
        self.window.resizable(False, False)

    def destroy(self):
        self.window.destroy()

    def update(self):
        self.window.update()

