#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
LOGDIR=${HOME}/log
echo "Starting..."
sleep 3
nohup $DIR/zmqShutterDaemon.py >/dev/null 2>&1 &
nohup $DIR/zmqGPSDaemon.py >/dev/null 2>&1 &
nohup $DIR/zmqShutterSocketServer.py >/dev/null 2>&1 &
nohup $DIR/zmqHttpServer.py >/dev/null 2>&1 &
nohup $DIR/zmqTriggerDaemon.py >/dev/null 2>&1 &
nohup $DIR/zmqTriggerSocketServer.py >/dev/null 2>&1 &
nohup $DIR/pingTime.py >/dev/null 2>&1 &
