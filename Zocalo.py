# -*- coding: utf-8 -*-
#!/usr/bin/env python
#import psycopg2
import socket
#import sys
#import time
from datetime import datetime
import logging
logger = logging.getLogger("testlog.procesar")

from constant import ALLOWED_IPS, COUCHDB_SERVER, IP_SERVIDOR, PORT, PATH

class Zocalo:
    """objeto Zocalo recibe la direcion ip desde donde va a operar y el puerto correspondiente"""
    def __init__(self, ipServidor=IP_SERVIDOR, puerto=PORT):
        self.ipServidor = ipServidor
        self.puerto = puerto
        self.servidor = self.iniciarSocket()
        self.conn = None
        self.addr = None

    def iniciarSocket(self):
        servidor = socket.socket() #socket.AF_INET, socket.SOCK_STREAM
        # servidor.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        # servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        servidor.bind((self.ipServidor, self.puerto))
        servidor.listen(1)
        return servidor


    def escucharUnaVez(self, funcionTren):
        """recibe como argumento una funcion en la que se debera definir la respuesta al tren de entrada
        mantiene la coneccion hasta el envio de la respuesta"""
        logger.debug('---------socket arriba------------')
        while True:
            self.conn, self.addr = self.servidor.accept()
            print ('listening & waiting')
            if not self.addr[0] in ALLOWED_IPS:
                logger.debug('Direccion de IP invalida %s', str(self.addr))
                self.conn.send('IP-FAIL')
                self.conn.close()
            else:
                recv = self.conn.recv(1024)
                print ('INT: {0}'.format(recv))
                if recv:
                    if len(recv.split('|')) > 22:
                        try:
                            resp = funcionTren(recv)
                        except Exception, e:
                            logger.critical("ERROR %s - %s " % (e.message, e.args))
                            respuesta = str('06|000000000000000|+|000000000000000|+|000000000000000|000000000000000|000|||')
                            self.conn.send(respuesta)
                            self.conn.close()
                            logger.debug(" Desconectado a: %s", str(self.addr))
                        else:
                            ##################
                            ####  MEOLLO  ####
                            ##################
                            respuesta = str(resp)
                            logger.debug(" Tren INP : %s", str(recv))
                            logger.debug(" Tren OUT : %s", str(respuesta))

                            self.conn.send(respuesta)
                            logger.debug(" Desconectado a: %s", str(self.addr))
                            self.conn.close()
                    else:
                        respuesta = str('30|000000000000000|+|000000000000000|+|000000000000000|000000000000000|000|||')
                        logger.debug(" Tren INP : %s", str(recv))
                        logger.debug(" Tren OUT : %s", str(respuesta))

                        self.conn.send(respuesta)
                        self.conn.close()

        logger.debug('---------socket abajo------------')


    def detenerSocket(self):
        self.conn.close()
        self.servidor.close()
