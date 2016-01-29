DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo "Starting..."
sleep 3
nohup $DIR/zmqShutterDaemon.py >/dev/null &
nohup $DIR/zmqGPSDaemon.py >/dev/null &
nohup $DIR/zmqSocketServer.py >/dev/null &
nohup $DIR/zmqHttpServer.py >/dev/null &
