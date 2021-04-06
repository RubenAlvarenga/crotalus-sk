#!/bin/bash
# Copyright (c) 2021 develpy
case "$1" in
  start)
    echo "Starting server"
    # Start the daemon
    python /usr/local/djangov18/crotalus-sk/socketBepsa.py start >> /usr/local/djangov18/crotalus-sk/log/socketlog.log 2>&1
    ;;
  stop)
    echo "Stopping server"
    # Stop the daemon
    python /usr/local/djangov18/crotalus-sk/socketBepsa.py stop
    ;;
  restart)
    echo "Restarting server"
    python /usr/local/djangov18/crotalus-sk/socketBepsa.py restart  >> /usr/local/djangov18/crotalus-sk/log/socketlog.log 2>&1
    ;;
  *)
    # Refuse to do other stuff
    echo "Usage: /etc/init.d/demonioBepsa {start|stop|restart}"
    exit 1
    ;;
esac
exit 0
