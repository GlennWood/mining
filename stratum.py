#!/usr/bin/python

"""
Usage: stratum.py OPERATION [-hvX] [COIN] ...

Arguments:
  OPERATION  start | stop | shutdown | status | list | logs
               (a comma-separated list of OPERATIONs)
  COIN       Apply OPERATION to this coin/pool's stratum proxy

Options:
  -X  dryrun, print configured behavior, then exit
  -h  print help, then exit
  -v  verbose mode
"""

from __future__ import print_function
import os
import sys
import daemon
import signal
import lockfile
import logging
import subprocess
import time

sys.path.insert(0,'/opt/mining/mining')
sys.path.insert(0,'/opt/mining/monitor')
import config
import importlib

global logger

### Ref: http://docopt.org/
### Ref: https://github.com/docopt/docopt
from docopt import docopt
config = config.Config(docopt(__doc__, argv=None, help=True, version=None, options_first=False))
arguments = config.arguments
OPERATION = arguments.get('OPERATION')

config.PIDFILE = '/var/local/ramdisk/stratum.pid'


POOL_WALLET_HASH=$(echo $POOL_WALLET | md5sum | cut -f1 -d" ")

export POOL_PORT=$(echo $POOL_URL_PORT | sed 's/^.*:\([0-9]\{4,5\}\)/\1/')
export POOL_URL=$(echo $POOL_URL_PORT | sed 's/^\(.*\):[0-9]\{4,5\}/\1/')

export LOCAL_URL=$(ifconfig -a|grep 'inet addr:'|grep -v 'inet addr:127'|sed 's/^.*inet addr:\([0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}\).*$/\1/')

LOG_FILE=stratum-$LOCAL_PORT

NAME=stratum
DAEMON_PATH="/usr/bin"
DAEMON="python"
DAEMON_OPTS="/opt/eth-proxy/eth-proxy.py"


get_status() {
	### Ref: https://www.thegeekstuff.com/2010/03/netstat-command-examples/
  local PORT_IN_USE=$(netstat -ltnp|grep tcp)
  PORT_IN_USE=$(echo $PORT_IN_USE|grep ":$LOCAL_PORT")
  if [ -n "$PORT_IN_USE" ]; then
  	PID=$(echo $PORT_IN_USE|awk '{print $NF}'|cut -f1 -d/)
  	LOG=$(cat /var/log/mining/stratum.log|grep "localPort=$LOCAL_PORT"|grep "START"|tail -1)
  fi
}
usage() {
	echo "Usage: $0 $OP LOCAL_PORT POOL_URL_PORT POOL_WALLET"
}
check_opts() {
	[ -z "$LOCAL_PORT" ]    && usage LOCAL_PORT    && exit 1
	[ -z "$POOL_URL_PORT" ] && usage POOL_URL_PORT && exit 1
	[ -z "$POOL_WALLET" ]   && usage POOL_WALLET   && exit 1
}

case "$OP" in

CONFIRM)
	check_opts 3
  get_status
  if [ -z "$PID" ]; then
    printf "There was no stratum proxy running on port %s, so one will be started.\n" $LOCAL_PORT
    $0 START $LOCAL_PORT $POOL_URL_PORT $POOL_WALLET
    exit $?
  fi
  
  ORIG_LOCAL_PORT=$(echo $LOG | sed 's/.*localPort=\([0-9]\{4,5\}\).*/\1/')
  ORIG_POOL_URL_PORT=$(echo $LOG | sed 's/.*remoteUrl=\(\S*\).*/\1/')
  ORIG_POOL_WALLET_HASH=$(echo $LOG | sed 's/.*wallet=\(\S*\).*/\1/')
  if [ "$ORIG_LOCAL_PORT" != "$LOCAL_PORT" ]; then
  	printf "%s\n" "Original LOCAL_PORT, $ORIG_LOCAL_PORT, is not $LOCAL_PORT"
  	exit 1
  fi
  if [ "$ORIG_POOL_URL_PORT" != "$POOL_URL_PORT" ]; then
  	printf "%s\n" "Original POOL_URL_PORT, $ORIG_POOL_URL_PORT, is not $POOL_URL_PORT"
  	exit 1
  fi
  if [ "$ORIG_POOL_WALLET_HASH" != "$POOL_WALLET_HASH" ]; then
  	printf "%s\n" "Original POOL_WALLET_HASH, $ORIG_POOL_WALLET_HASH, is not $POOL_WALLET_HASH"
  	exit 1
  fi

  printf "%s\n" "$LOG"
;;


START)
	check_opts 3
	get_status
	if [ -n "$PID" ]; then
	  printf "There is already a stratum proxy running on port %i\n%s\nFailed.\n" $LOCAL_PORT "$LOG"
	  exit 1
	fi

  pushd /opt/eth-proxy >/dev/null
  POOL_PORT=$POOL_PORT POOL_URL=$POOL_URL POOL_URL_PORT=$POOL_URL_PORT LOCAL_PORT=$LOCAL_PORT LOCAL_URL=$LOCAL_URL POOL_WALLET=$POOL_WALLET \
	  cat eth-proxy.conf.tmpl | envsubst > eth-proxy.conf
	nohup $DAEMON_PATH/$DAEMON $DAEMON_OPTS >$LOG_DIR/$LOG_FILE.log 2>$LOG_DIR/$LOG_FILE.err &
  popd >/dev/null

  RC=$?
  PID=$!
  if [ -z "$PID" ]; then
    printf "%s %i\n" "Fail" $RC
  else
    printf "%s\n" "Ok"
  fi

	cat >> $LOG_DIR/stratum.log << EOL
`date +%Y-%m-%dT%H:%M:%S` $OP Stratum pid=$PID localPort=$LOCAL_PORT remoteUrl=$POOL_URL_PORT wallet=$POOL_WALLET_HASH
EOL

;;


STOP)
  get_status
  if [ -z "$PID" ]; then
    printf "There is no stratum proxy running on port %s\n" $PORT
    exit 1
  fi

  printf "Stopping pid=%i %9s %s" $PID $PORT
  kill -KILL $PID

	# Update the logs
  echo $LOG|sed 's/.*START //'
  MSG=$(echo $X|sed 's/.*START *//')
  DATE=$(date +%Y-%m-%dT%H:%M:%S)
	echo $DATE $OP $MSG >> $LOG_DIR/stratum-$LOCAL_PORT.log
	echo $DATE $OP $MSG >> $LOG_DIR/stratum.log

  printf "%s\n" "Ok"
;;


STATUS)
  get_status
  if [ -z "$PID" ]; then
    printf "There is no stratum proxy running on port %s\n" $LOCAL_PORT
    exit 1
  fi
  printf "%s\n" "$LOG"
;;


RESTART)
  get_status
  if [ -z "$PID" ]; then
    printf "There is no stratum proxy running on port %s\n" $PORT
  else
    $0 stop $LOCAL_PORT $POOL_URL_PORT
  fi
  $0 start $LOCAL_PORT $POOL_URL_PORT
;;


ERR)
  tail -f $LOG_DIR/$LOG_FILE.err
;;


LOG)
  tail -f $LOG_DIR/$LOG_FILE.log
;;


LOGS)
  tail -f $LOG_DIR/$LOG_FILE.log $LOG_DIR/$LOG_FILE.err
;;


*)
  echo "Usage: $0 {confirm|err|log|logs|status|start|stop|restart}"
  exit 1
esac

