DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
LOGDIR=${HOME}/log
mkdir -p $LOGDIR
echo "Starting..."
sleep 3
nohup $DIR/zmqShutterDaemon.py >$LOGDIR/zmqShutterDaemon.log 2>&1 &
nohup $DIR/zmqGPSDaemon.py >$LOGDIR/zmqGPSDaemon.log 2>&1 &
nohup $DIR/zmqShutterSocketServer.py >$LOGDIR/zmqShutterSocketServer.log 2>&1 &
nohup $DIR/zmqHttpServer.py >$LOGDIR/zmqHttpServer.log 2>&1 &
nohup $DIR/zmqTriggerDaemon.py >$LOGDIR/zmqTriggerDaemon.log 2>&1 &
nohup $DIR/zmqTriggerSocketServer.py >$LOGDIR/zmqTriggerSocketServer.log 2>&1 &
nohup $DIR/pingTime.py >$LOGDIR/pingTime.log 2>&1 &
