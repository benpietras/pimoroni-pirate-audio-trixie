#!/bin/bash
while true; do
    sleep 60
    STATUS=$(mpc -h 127.0.0.1 status 2>/dev/null | grep -c "\[playing\]")
    if [ "$STATUS" -eq 0 ]; then
        echo "$(date): Stream not playing, restarting..."
        mpc -h 127.0.0.1 clear
        mpc -h 127.0.0.1 add https://radiostreaming.ert.gr/ert-kosmos
        mpc -h 127.0.0.1 play
    fi
done
