#!/bin/bash
kill  -9 `ps -ef | grep zmqShutterDaemon.py | grep -v grep | awk '{print $2}'`
kill  -9 `ps -ef | grep zmqGPSDaemon.py | grep -v grep | awk '{print $2}'`
kill  -9 `ps -ef | grep zmqHttpServer.py | grep -v grep | awk '{print $2}'`
kill  -9 `ps -ef | grep zmqShutterSocketServer.py | grep -v grep | awk '{print $2}'`
kill  -9 `ps -ef | grep zmqTriggerDaemon.py | grep -v grep | awk '{print $2}'`
kill  -9 `ps -ef | grep zmqTriggerSocketServer.py | grep -v grep | awk '{print $2}'`
kill  -9 `ps -ef | grep pingTime.py | grep -v grep | awk '{print $2}'`

