import os, logging, settings
from logging.handlers import TimedRotatingFileHandler

timedLogger = None

def getTimedLogger():
    global timedLogger
    if not timedLogger:
        timedLogger = logging.getLogger("UPLOADER LOGS")
        
        handler = TimedRotatingFileHandler(os.path.join(settings.BASE_DIR, "logs/access_log.txt"), when = "midnight", interval = 1, backupCount = 30)
        handler.setFormatter(logging.Formatter('[%(asctime)-19.19s - %(name)-3.3s - %(threadName)-10.10s - %(levelname)-8s] - %(message)s'))
        
        timedLogger.addHandler(handler)
        
        if settings.DEBUG:
            timedLogger.setLevel(logging.DEBUG)
            
            consolehandler = logging.StreamHandler()
            consolehandler.setFormatter(logging.Formatter('[%(asctime)-19.19s - %(levelname)-8s] - %(message)s'))
            
            timedLogger.addHandler(consolehandler)
        else:
            timedLogger.setLevel(logging.INFO)
        
    return timedLogger