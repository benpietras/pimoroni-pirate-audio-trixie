#!/bin/bash
# Wait for mopidy MPD to be ready
for i in $(seq 1 30); do
    mpc -h 127.0.0.1 status > /dev/null 2>&1 && break
    sleep 2
done

# Add and play the stream
mpc -h 127.0.0.1 clear
mpc -h 127.0.0.1 add https://radiostreaming.ert.gr/ert-kosmos
mpc -h 127.0.0.1 play
