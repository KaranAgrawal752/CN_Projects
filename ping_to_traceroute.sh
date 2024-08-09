

#!/bin/bash

if [ $# -ne 1 ]; then
	echo "Usage: $0 <hostname or IP>"
	exit 1
fi

host=$1
ttl=1

echo "Traceroute to $host"

while true; do
	output=$(ping -4 -c 1 -t $ttl $host 2>&1)
	ip=$(echo "$output" | grep -oE '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+' | head -n 2 | tail -n 1)
    tm=$(ping  -c 1 $ip | awk 'NR==2' | grep -oE "time=[0-9]+\.[0-9]* ms" )
	echo "TTL=$ttl IP=$ip Time=$tm"
	if echo "$output" | grep -q " 0% packet loss"; then
        break
    fi
    if [ $ttl = 30 ]; then
		break
	fi
	ttl=$((ttl+1))
done