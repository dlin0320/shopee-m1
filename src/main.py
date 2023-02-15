from app.app import App
import asyncio
import sys, os
from utilities.logger import Logger
import logging
from dotenv import load_dotenv
import faulthandler
import shutil

def main():
    if getattr(sys, 'frozen', False):
        dir = sys._MEIPASS
    else:
        dir = os.path.dirname(os.path.abspath(__file__))
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
    # shutil.rmtree(f'{dir}/profiles', ignore_errors=True)
    load_dotenv()
    Logger(dir)
    app = App()
    asyncio.run(app.exec(dir))

if __name__ == '__main__':
    try:
        faulthandler.enable()
        sys.setrecursionlimit(10**8)
        main()
    except Exception as e:
        print(e)
        logging.debug('exited main')
        logging.debug(e.__class__)