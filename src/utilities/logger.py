import logging
import os

class Logger:
    def __init__(self, dir) -> None:
        stage = os.getenv('STAGE', 'development')
        print(stage)
        if stage == 'development':
            logging.basicConfig(level=logging.DEBUG, filename=f'{dir}/enterprise.log', filemode='a', format='%(asctime)s - %(levelname)s - %(message)s')
        elif stage == 'production':
            logging.basicConfig(level=logging.ERROR, filename=f'{dir}/enterprise.log', filemode='w', format='%(asctime)s - %(levelname)s - %(message)s')