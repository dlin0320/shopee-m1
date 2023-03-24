from tkinter import StringVar, Label, Entry, Button
import asyncio
from application.window import Window
from server.scripts import login

class LoginWindow(Window):
    def __init__(self, loop, dir) -> None:
        super().__init__(loop, dir)
        self.window.geometry("420x420")
        self.window.title('登入')
        self.loggedIn = False

        self.msg = StringVar()
        Label(self.window, textvariable=self.msg).pack()
        Label(self.window, text='帳號').pack()
        self.usernameEntry = Entry(self.window)
        self.usernameEntry.pack()
        Label(self.window, text='密碼').pack()
        self.passwordEntry = Entry(self.window, show='*')
        self.passwordEntry.pack()
        Button(text='登入', command=lambda: asyncio.create_task(self.login())).pack()

    async def show(self):
        while self.loggedIn == False:
            self.update()
            await asyncio.sleep(.1)
        return self.username

    async def login(self):
        self.username = self.usernameEntry.get()
        ok, msg = await login(self.username, self.passwordEntry.get())
        if ok:
            self.loggedIn = True
        else:
            self.msg.set(msg)