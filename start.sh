echo "Killing..."
./stop.sh
echo "Starting..."
sleep 1
nohup ./zmqShutterDaemon.py >/dev/null &
nohup ./zmqGPSDaemon.py >/dev/null &
nohup ./zmqSocketServer.py >/dev/null &
nohup ./zmqHttpServer.py >/dev/null &
