#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
${DIR}/stop.sh
sleep 2
${DIR}/start.sh
