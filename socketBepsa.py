# -*- coding: utf-8 -*-
#!/usr/bin/env python
import logging
import logging.handlers
from daemon import runner
from Zocalo import *
from procesar import *

from constant import IP_SERVIDOR, PORT, PATH



class App():
    def __init__(self):
        #Se define unos path estandar en linux.
        self.stdin_path = '/dev/null'
        self.stdout_path = '/dev/tty'
        self.stderr_path = '/dev/tty'
        #Se define la ruta del archivo pid del demonio.
        self.pidfile_path = PATH+'/run/demonioBepsa.pid'
        self.pidfile_timeout = 15

    def run(self):
        while True:
            Zoc = Zocalo(ipServidor=IP_SERVIDOR, puerto=PORT)
            logger.info("socket Bepsa conectado en "+str(Zoc.ipServidor)+" Puerto: "+str(Zoc.puerto))
            Zoc.escucharUnaVez(procesar)
            time.sleep(1)




if __name__ == '__main__':
    app = App()
    logger = logging.getLogger("testlog")
    logger.setLevel(logging.DEBUG)
    handler = logging.handlers.TimedRotatingFileHandler(filename=PATH+'/log/file.log', when="W6", interval=1, backupCount=0)
    formatter = logging.Formatter('%(levelname)-8s:%(asctime)14s %(module)14s : %(lineno)5s - %(message)s')
    
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    serv = runner.DaemonRunner(app)
    serv.daemon_context.files_preserve = [handler.stream]
    serv.do_action()



