DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
LOGDIR=${HOME}/log
echo "Starting..."
sleep 3
nohup $DIR/zmqShutterDaemon.py >$LOGDIR/zmqShutterDaemon.log 2>&1 &
nohup $DIR/zmqGPSDaemon.py >$LOGDIR/zmqGPSDaemon.log 2>&1 &
nohup $DIR/zmqSocketServer.py >$LOGDIR/zmqSocketServer.log 2>&1 &
nohup $DIR/zmqHttpServer.py >$LOGDIR/zmqHttpServer.log 2>&1 &
nohup $DIR/zmqTripDaemon.py >$LOGDIR/zmqTripDaemon.log 2>&1 &
nohup $DIR/zmqTripSocketServer.py >$LOGDIR/zmqTripSocketServer.log 2>&1 &
nohup $DIR/pingTime.py >$LOGDIR/pingTime.log 2>&1 &
