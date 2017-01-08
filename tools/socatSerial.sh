#!/bin/bash
#Just an example of how to redir serial port to the network
socat -d TCP:cronostamper:27644,reuseaddr  pty,link=/tmp/cronostamperCOM &
