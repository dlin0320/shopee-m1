from datetime import datetime
from application.window import Window
from server.scripts import report
from shopee.shopee import ChangePayload, SearchPayload
import logging
from time import time
from application.models import History, Shop
from shopee.scripts import changePrice, getDetails, search, shopeeLogin, getAdvertisements
from tkinter import StringVar, Frame, Button, BOTTOM, LEFT, RIGHT, simpledialog, ttk, Label, DISABLED, NORMAL, OptionMenu
import asyncio
import queue
import random
from PIL import Image, ImageTk
import shutil

class UltimateWindow(Window):
    def __init__(self, loop, dir, os, username) -> None:
        Shop(dir)
        History(dir)
        print('init dir', History.dir)
        super().__init__(loop, dir)
        self.window.geometry('1369x690')
        self.window.title('廣告幫手ultimate')
        self.os = os
        self.username = username
        self.initTime = time()
        self.searches = 0
        self.connections = 0
        self.shops = []
        self.profiles = {}
        self.autoTask = None
        self.rankingsTask = None
        self.detailsTask = None
        self.setupTask = None
        self.gotoTask = None 
        self.priorityRows = queue.Queue()
        self.backgroundRows = queue.Queue()

        self.msg = StringVar()
        self.cycle = StringVar()
        self.span = StringVar()
        self.actionFrame = Frame(self.window)
        self.actionFrame.pack()
        self.messageFrame = Frame(self.actionFrame)
        self.messageFrame.pack(side=BOTTOM)
        self.buttonFrame = Frame(self.actionFrame)
        self.buttonFrame.pack(side=LEFT)
        self.optionFrame = Frame(self.actionFrame)
        self.optionFrame.pack(side=RIGHT)
        self.tableFrame = Frame(self.window)
        self.tableFrame.pack(side=BOTTOM)

        self.profileButton = Button(self.buttonFrame, text='新增帳號', command=lambda: self.loop.create_task(self.newProfile()))
        self.profileButton.pack(side=LEFT)
        Button(self.buttonFrame, text='載入紀錄', command=lambda: self.loop.create_task(self.loadHistories())).pack(side=LEFT)
        self.spanOption = OptionMenu(self.optionFrame, self.span, '1', '7', '30', command=lambda _: self.loop.create_task(self.getDetails()))
        self.spanOption.config(state=DISABLED)
        self.spanOption.pack(side=RIGHT)
        Label(self.messageFrame, textvariable=self.msg).pack()

        self.table = ttk.Treeview(self.tableFrame, height=100) 
        self.columns = ['id', '關鍵字', '價格', '新價格', '最高價格[x]', '最低價格[n]', '目標排名[a]', '廣告排名', '自然排名', '花費', '銷售額', 'ROAS', '最低ROAS[o]', '修改時間']
        self.columnIndices = {'id':0, 'name':1, 'price':2, 'new_price':3, 'max_price':4, 'min_price':5, 'target_ad':6, 'ad':7, 'hype':8, 'cost':9, 'sales':10, 'roas':11, 'min_roas':12, 'time':13}

    # Task
    # def createTask(self, name, task, **kwargs):
    #     setattr(self, name, self.loop.create_task(task(**kwargs)))

    # def stopTask(self, name, callback=None, **kwargs):
    #     if name == None:
    #         return None
    #     for task in asyncio.all_tasks(self.loop):
    #         if task.get_name() == name:
    #             task.cancel()
    #             if callback != None:
    #                 callback(**kwargs)

    # Init
    async def show(self):
        self.currentTime = time()
        shops = Shop.select()
        for shop in shops:
            print(shop)
            id, cookie, agent = shop
            print(id, cookie, agent)
            self.shops.append(id)
            self.profiles[id] = (cookie, agent)
        print(self.shops, self.profiles)
        await self.makeTable()
        self.loop.create_task(self.searchRankings())
        self.loop.create_task(self.auto())
        while True:
            if time() - self.currentTime > 60 * 10:
                self.currentTime = time()
                totalTime = self.currentTime - self.initTime
                if not (await report(self.username, totalTime, self.searches, self.connections)):
                    self.msg.set('將於10秒後關閉')
                    print('服務連線已中斷')
                    await asyncio.sleep(10)
                    for task in asyncio.all_tasks(self.loop):
                        task.cancel()
                    return
            if len(self.table.get_children()) == 0:
                self.spanOption.config(state=DISABLED)
            else:
                self.spanOption.config(state=NORMAL)
            self.update()
            await asyncio.sleep(.1)

    async def loadHistories(self):
        # if len(self.shops) == 0:
        #     return
        for ad in History.select():
            # if ad[0] in self.shops:
            print('new ad', ad)
            self.insertRow(ad)
            print('inserted', ad)
        print('loaded')

    # Profile
    async def newProfile(self):
        try:
            self.profileButton.config(state=DISABLED)
            dir = f'{self.dir}/profiles/{len(self.shops)}'
            print(dir)
            ok, id, cookie, agent =  await shopeeLogin(self.os, dir)
            if ok:
                if self.shops.__contains__(id):
                    index = self.shops.index(id) 
                    self.shops[index] = '0'
                    dir = f'{self.dir}/profiles/{index}'
                    shutil.rmtree(dir, ignore_errors=True)
                    print('removed ', dir)
                # for ad in await getAdvertisements(cookie, agent):
                    # self.advertisements.insert((id, *ad))
                Shop.insert((id, cookie, agent))
                self.shops.append(id)
                self.profiles[id] = (cookie, agent)
        except Exception as e:
            logging.debug(e.__class__, exc_info=True)
        finally:
            self.profileButton.config(state=NORMAL)
            print(len(self.shops))
            print(Shop.select())

    async def checkSubscription(self):
        # TODO
        return True
    # async def refreshShopeeProfile(self):
    #     self.msg.set('抓取資料')
    #     self.connections += 1
    #     try:
    #         ok, advertisevents = await getAdvertisements(self.cookie, self.agent)
    #         if ok:
    #             for ad in advertisevents:
    #                 for keyword in ad.keywords:
    #                     row = self.items.get(f'{ad.id}{keyword.name}', None)
    #                     if row != None:
    #                         await self.updateRow(row, price=keyword.price)
    #     except Exception as e:
    #         logging.debug(e.__class__, exc_info=True)

    async def getDetails(self):
        try:
            shops = {}
            rows = self.table.get_children()
            for row in rows:
                shop = self.table.item(row, 'text')
                values = self.table.item(row, 'values')
                id = self.getValue(values, 'id')
                name = self.getValue(values, 'name')
                if shop in shops:
                    if id in shops[shop]:
                        shops[shop][id].append((name, row))
                    else:
                        shops[shop][id] = [(name, row)]
                else:
                    shops[shop] = {id: [(name, row)]}
            for i, s in shops.items():
                cookie, agent = self.profiles[i]
                for id, keywords in s.items():
                    details = await getDetails(cookie, agent, id, int(self.span.get()))
                    for name, row in keywords:
                        roas, cost, sales = details.get(name, ('','',''))
                        await self.updateRow(row, roas=roas, cost=cost, sales=sales)
        except Exception as e:
            logging.debug(e.__class__, exc_info=True)
    
    # Main
    async def searchRankings(self):
        try:
            while True:
                next = random.uniform(3, 6)
                if len(self.shops) == 0:
                    await asyncio.sleep(next)
                    continue 
                print(self.priorityRows.qsize(), self.backgroundRows.qsize())
                while not self.priorityRows.empty():
                    print('priority:', self.priorityRows.queue)
                    self.loop.create_task(self.searchAndUpdate(self.priorityRows.get()))
                    await asyncio.sleep(random.uniform(9,21))
                while not self.backgroundRows.empty():
                    print('background:', self.backgroundRows.queue)
                    if not self.priorityRows.empty():
                        break
                    self.loop.create_task(self.searchAndUpdate(self.backgroundRows.get()))
                    await asyncio.sleep(random.uniform(9,21))
                await asyncio.sleep(next)
        except Exception as e:
            print('search error')
            logging.debug(e.__class__, exc_info=True)
    
    async def searchAndUpdate(self, row):
        try:
            self.searches += 1
            values = self.table.item(row, 'values')
            id = self.getValue(values, 'id')
            name = self.getValue(values, 'name')
            print(name, id, row)
            result = await search(self.os, SearchPayload(name, id, row))
            print(result)
            if result != None:
                await self.updateRow(result.row, ad=result.ad, hype=result.hype)
        except Exception as e:
            logging.debug(e.__class__, exc_info=True)

    async def auto(self):
        try:
            cycle = 15
            hour = datetime.now().hour
            if hour >= 2 and hour <= 8:
                min = 50 * 60
                max = 70 * 60
            else:
                min = (int(cycle) * 0.69) * 60
                max = (int(cycle)) * 60
            # min = 50
            # max = 70
            while True:
                self.msg.set('運行中')
                # await self.refreshShopeeProfile()
                newPrices = await self.autoPrices()
                await self.changePrices()
                if newPrices == 0:
                    next = 5
                else:
                    next = int(random.uniform(min, max))
                    logging.error(next)
                await asyncio.sleep(next)
        except Exception as e:
            self.msg.set('已停止') 
            logging.debug(e.__class__, exc_info=True)

    async def autoPrices(self):
        newPrices = 0
        try:
            self.msg.set('計算新價格...')
            for row in self.table.tag_has('auto'):
                values = self.table.item(row, 'values')
                new_price = self.getValue(values, 'new_price')
                if new_price == '':
                    ad = self.getValue(values, 'ad')
                    if ad == '無':
                        ad = 10 + 3
                    elif ad == '':
                        continue
                    target_ad = self.getValue(values, 'target_ad')
                    price = self.getValue(values, 'price')
                    max_price = self.getValue(values, 'max_price')
                    diff = int(ad) - int(target_ad)
                    if diff > 0:
                        diff = min(diff, 3)
                        new_price = round(float(price) * (1 + 0.1 * diff), 2)
                        if max_price != '' :
                            new_price = min(new_price, float(max_price))
                    elif diff < 0:
                        diff = max(diff, -3)
                        new_price = round(float(price) * (1 + 0.1 * diff), 2) 
                        min_price = self.getValue(values, 'min_price')
                        if min_price == '':
                            min_price = 1.2
                        else:
                            min_price = float(min_price)
                        new_price = max(new_price, min_price)
                    #TODO better logic for small prices
                    elif diff == 0:
                        new_price = round(float(price) * (1 - 0.05), 2)
                        if abs(new_price - float(price)) <= 0.3:
                            continue
                    if float(new_price) == float(price):
                        continue
                await self.updateRow(row, new_price=new_price)
                newPrices += 1
        except Exception as e:
            logging.debug(e.__class__, exc_info=True)
        finally:
            self.msg.set('')
            return newPrices

    async def changePrices(self):
        pendingRows = self.table.tag_has('change')
        if len(pendingRows) == 0:
            return
        try:
            self.msg.set('更新價格...')
            shops = {}
            for row in pendingRows:
                shop = self.table.item(row, 'text')
                values = self.table.item(row, 'values')
                id = self.getValue(values, 'id')
                if shop in shops:
                    if id in shops[shop]:
                        shops[shop][id].append(ChangePayload(self.getValue(values, 'name'), self.getValue(values, 'new_price'), row))
                    else:
                        shops[shop][id] = [ChangePayload(self.getValue(values, 'name'), self.getValue(values, 'new_price'), row)]
                else:
                    shops[shop] = {id: [ChangePayload(self.getValue(values, 'name'), self.getValue(values, 'new_price'), row)]}
            for i, s in shops.items():
                dir = f'{self.dir}/profiles/{self.shops.index(i)}'
                for itemId, payloads in s.items():
                    self.connections += 1
                    rows, prices = await changePrice(self.os, dir, itemId, payloads)
                    for row, price in zip(rows, prices):
                        time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                        await self.updateRow(row, price=price, new_price='', time=time)
        except Exception as e:
            logging.debug(e.__class__, exc_info=True)
        finally:
            self.msg.set('')

    # Key
    async def handleKeyPress(self, key, _):
        kwargs = dict()
        if key == 'x':
            prompt = '最高價格'
            kwargs['max_price']= ''
        elif key == 'n':
            prompt = '最低價格'
            kwargs['min_price'] = ''
        elif key == 'a':
            prompt = '目標排名'
            kwargs['target_ad']= ''
        elif key == 'o':
            prompt = '最低ROAS'
            kwargs['min_roas']= ''
        elif key == 'd':
            for selected in self.table.selection():
                values = self.table.item(selected, 'values')
                id = self.getValue(values, 'id')
                name = self.getValue(values, 'name')
                self.table.delete(selected)
                History.delete(id, name)
            return
        elif key == 'r':
            for selected in self.table.selection():
                await self.updateRow(selected, ad='')
                self.priorityRows.put(selected)
        input = simpledialog.askstring(title='', prompt=prompt)
        if input == None:
            return
        selection = self.table.selection()
        for selected in selection:            
            for k in kwargs:
                kwargs[k] = input
            self.loop.create_task(self.updateRow(selected, **kwargs))

    # Table
    async def makeTable(self):
        try:
            self.table.destroy()
            self.table = ttk.Treeview(self.tableFrame, height=100, columns=self.columns) 
            self.table.heading('#0', text='賣場')
            self.table.column('#0', width=150)
            for i, column in enumerate(self.columns):
                self.table.heading(f'#{i+1}', text=column)
                self.table.column(f'#{i+1}', width=69)
            self.table.column('#1', width=150)
            self.table.column('#2', width=150)
            self.table.column('#14', width=150)
            self.table.bind('<x>', lambda event: asyncio.ensure_future(self.handleKeyPress('x', event)))
            self.table.bind('<n>', lambda event: asyncio.ensure_future(self.handleKeyPress('n', event)))
            self.table.bind('<a>', lambda event: asyncio.ensure_future(self.handleKeyPress('a', event)))
            self.table.bind('<r>', lambda event: asyncio.ensure_future(self.handleKeyPress('r', event)))
            self.table.bind('<d>', lambda event: asyncio.ensure_future(self.handleKeyPress('d', event)))
            self.table.tag_configure('auto')
            self.table.tag_configure('change')
            self.table.tag_configure('price_alert', background='yellow')
            self.table.tag_configure('roas_alert', background='orange')
            self.table.pack(side=BOTTOM)
        except Exception as e:
            print(e)
            logging.debug(e.__class__, exc_info=True) 

    def insertRow(self, advertisement):
        print('inserting ad', advertisement)
        try:
            values = [''] * len(self.columns)
            values[self.getIndex('id')] = advertisement[1]
            values[self.getIndex('name')] = advertisement[2]
            values[self.getIndex('price')] = advertisement[3]
            values[self.getIndex('target_ad')] = advertisement[4]
            row = self.table.insert('', index='end', text=advertisement[0], values=values, iid=f'{advertisement[1]} {advertisement[2]}')
            if advertisement[4] != '':
                self.priorityRows.put(row)
            else:
                self.backgroundRows.put(row)
            print('row', row)
        except Exception as e:
            print('exception', e)

    async def updateRow(self, row, **kwargs):
        values = self.table.item(row, 'values')
        tags = []
        newValues = list(values)
        for key, value in kwargs.items():
            newValues[self.getIndex(key)] = value
            if key == 'time' or key == 'target_ad':
                print('inserting priority:', row)
                self.priorityRows.put(row)
        id = self.getValue(newValues, 'id')
        name = self.getValue(newValues, 'name')
        price = self.getValue(newValues, 'price')
        new_price = self.getValue(newValues, 'new_price')
        max_price = self.getValue(newValues, 'max_price')
        target_ad = self.getValue(newValues, 'target_ad')
        min_roas = self.getValue(newValues, 'min_roas')
        roas = self.getValue(newValues, 'roas')
        if target_ad != '':
            tags.append('auto')
            History.update(target_ad, id, name)
        if new_price != '':
            tags.append('change')
        if max_price != '':
            if new_price != '' and float(new_price) >= float(max_price):
                tags.append('price_alert')
            elif price != '' and float(price) >= float(max_price):
                tags.append('price_alert')
        if min_roas != '' and roas != '' and float(roas) < float(min_roas):
                tags.append('roas_alert')
        self.table.item(row, values=newValues, tags=tags, image='')

    # def addKeyword(self, shop, id, name, price):
    #     print('adding keyword', shop, id, name, price)
    #     # History.insert(shop, id, name, price, '')
    #     try:
    #         self.insertRow((shop, id, name, price, ''))
    #     except Exception as e:
    #         print(e)
    #     print('done')
        # name = simpledialog.askstring(title='新增', prompt='關鍵字')
        # if name == None:
        #     return
        
        # for ad in self.advertisements.select(name):
            # History.insert((*ad, ''))
            # self.insertRow((*ad, ''))

    def getValue(self, values, colName):
        return values[self.getIndex(colName)]

    def getIndex(self, colName):
        return self.columnIndices[colName]

    # IO
    def exportFile(self):
        f = open(f'{self.dir}/test.txt', 'a')
        f.write('done')
        f.close()
        # rows = self.table.get_children()
        # f = open('./results.txt', 'w')
        # f.write('"關鍵字", \'價格\',[廣告排名], (自然排名)\n')
        # for r in rows:
        #     v = self.table.item(r, 'values')
        #     f.write(f'"{v[0]}", \'{v[1]}\' [{v[2]}], ({v[3]})\n')
        # f.close()
        # self.msg.set('輸出完成')