#!/bin/bash

cd /home/pi/flexy-reader-public

find . -type f -empty -delete -print

[ $(git rev-parse HEAD) = $(git ls-remote $(git rev-parse --abbrev-ref @{u} | \
sed 's/\// /g') | cut -f1) ] || (git reset --hard origin/master && git pull)

FILE=/home/pi/flexy-reader-public/dsmr.log
if [ ! -f "$FILE" ]; then
    echo "Log file[$FILE] does not exist, creating new file"
    touch /home/pi/flexy-reader-public/dsmr.log
fi

python3 /home/pi/flexy-reader-public/dsmr_reader_cron.py

