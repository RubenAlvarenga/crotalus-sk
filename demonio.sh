#!/bin/bash
# Copyright (c) 2016 Mercado 4
case "$1" in
  start)
    echo "Starting server"
    # Start the daemon
    python /usr/local/django-apps/copperhead/socketBepsa.py start >> /usr/local/django-apps/copperhead/log/socketlog.log 2>&1
    ;;
  stop)
    echo "Stopping server"
    # Stop the daemon
    python /usr/local/django-apps/copperhead/socketBepsa.py stop
    ;;
  restart)
    echo "Restarting server"
    python /usr/local/django-apps/copperhead/socketBepsa.py restart  >> /usr/local/django-apps/copperhead/log/socketlog.log 2>&1
    ;;
  *)
    # Refuse to do other stuff
    echo "Usage: /etc/init.d/demonioBepsa {start|stop|restart}"
    exit 1
    ;;
esac
exit 0
