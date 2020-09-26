#!/bin/bash
kill  -9 `ps -ef | grep zmqShutterDaemon.py | grep -v grep | awk '{print $2}'`
kill  -9 `ps -ef | grep zmqGPSDaemon.py | grep -v grep | awk '{print $2}'`
kill  -9 `ps -ef | grep zmqHttpServer.py | grep -v grep | awk '{print $2}'`
kill  -9 `ps -ef | grep zmqSocketServer.py | grep -v grep | awk '{print $2}'`
kill  -9 `ps -ef | grep zmqTripDaemon.py | grep -v grep | awk '{print $2}'`
kill  -9 `ps -ef | grep zmqTripSocketServer.py | grep -v grep | awk '{print $2}'`
kill  -9 `ps -ef | grep pingTime.py | grep -v grep | awk '{print $2}'`

