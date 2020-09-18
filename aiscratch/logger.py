import os
import logging
import logging.handlers

BASE_DIR = "aiscratch/"

logger = logging.getLogger("aiscratch")

hdlr = logging.handlers.TimedRotatingFileHandler(filename=os.path.join(BASE_DIR, "logs", "aiscratch.log"),  when='midnight', backupCount=7)

formatter = logging.Formatter('[%(asctime)s] {%(filename)-10s:%(lineno)-4d} %(levelname)-5s - %(message)s','%m-%d %H:%M:%S')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)