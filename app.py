from os import makedirs
from os.path import join, exists, abspath
from datetime import datetime
import logging
from backend import app, initial_load

file_name = datetime.now().strftime("%Y-%m-%d %H:%M:%S").replace(' ', '_')
if not exists(abspath('logs')):
    makedirs('logs')
log_name = join('logs', file_name)
logging.basicConfig(filename=log_name + '.log', filemode='w',
                    format='%(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

initial_load()

if __name__ == '__main__':
    try:
        app.run()
    except Exception as e:
        logging.exception("main crashed. Error: %s", e)
        print("main crashed. Error: %s", e)
