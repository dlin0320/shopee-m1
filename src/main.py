from application.entry import Entry
import asyncio
import sys, os
from utilities.logger import Logger
import logging
from dotenv import load_dotenv
import faulthandler
import shutil
from threading import Thread
from app import app

def main():
    # if getattr(sys, 'frozen', False):
    #     dir = sys._MEIPASS
    # else:
    # dir = os.path.dirname(os.path.abspath(__file__))
    dir = '.'
    if dir:
        try:
            os.mkdir(f'{dir}/temp')
        except Exception as e:
            pass
        dir += '/temp'
    else:
        dir = '.'
        try:
            os.mkdir(f'{dir}/temp') 
        except Exception as e:
            pass
    # try:
    #     os.mkdir('./shopee-extension/temp')
    # except Exception as e:
    #     print(e)
    # dir = './shopee-extension/temp'
    load_dotenv()
    Logger(dir)
    entry = Entry()
    app_thread = Thread(target=app.run)
    app_thread.start()
    asyncio.run(entry.exec(dir))

if __name__ == '__main__':
    try:
        faulthandler.enable()
        sys.setrecursionlimit(10**8)
        main()
    except Exception as e:
        print(e)
        logging.debug('exited main')
        logging.debug(e.__class__)