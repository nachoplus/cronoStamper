#!/bin/bash
socat -d TCP:192.168.1.36:27644,reuseaddr  pty,link=/tmp/cronostamperCOM &
