from server.server import Server as s
from utilities.proxy import goto

async def login(username, password):
    body = {'username': username, 'password': password, 'version': s.version}
    try:
        res = await goto(url=s.auth, method='post', json=body)
        if res.status_code == 200:
            return True, 'ultimate'
        elif res.status_code == 401:
            return False, '帳號密碼錯誤'
        else:
            return False, '請重新操作'
    except Exception as e:
        return False, '請重新操作'

async def report(username, time, searches, connections):
    res = await goto(url=s.report, method='post', json=s.genReport(username, time, searches, connections))
    if res.status_code == 200:
        return True
    else:
        return False

async def bindAccount():
    body = {}
    res = await goto(url=s.account, method='post')