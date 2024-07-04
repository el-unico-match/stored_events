from settings import settings
import logging

def getLogger(name):
    logger=logging.getLogger(name)
    streamHandler = logging.StreamHandler()
    streamHandler.setLevel(settings.logging_level)
    formatter = logging.Formatter('%(levelname)s %(asctime)s [%(filename)s] %(message)s')
    streamHandler.setFormatter(formatter)
    logger.addHandler(streamHandler)
    return logger
