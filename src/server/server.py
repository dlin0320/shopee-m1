from dataclasses import dataclass
import json

class Server:
    version = 1.4

    home = 'https://shopee-helper.herokuapp.com/'

    auth = f'{home}auth'

    report = f'{home}report'

    account = f'{home}account'

    def genReport(username, time, searches, connections):
        session = json.dumps(Session(time, searches, connections).__dict__)
        return { username: session, 'version': Server.version}

@dataclass
class Session:
    time: str
    searches: int
    actions: int