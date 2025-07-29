#!/bin/bash

# IPv4 chain management
# USAGE: chain-v4.sh ON | OFF

DOES_CHAIN_EXIST=$(sudo iptables -S INTERNET_OFF 2>/dev/null | wc -l)

if [ $DOES_CHAIN_EXIST -gt 1 ]; then
  echo "IPv4 chain exists"
else
  echo "creating IPv4 chain"
  sudo iptables -N INTERNET_OFF
  sudo iptables -A INTERNET_OFF -d 127.0.0.0/8 -j RETURN
  sudo iptables -A INTERNET_OFF -d 192.168.0.0/16 -j RETURN
  sudo iptables -A INTERNET_OFF -j REJECT
fi

IS_ON="$1"
IS_CHAIN_ACTIVE=$(sudo iptables -L OUTPUT | grep INTERNET_OFF | wc -l)

if [ "$IS_ON" = "ON" ]; then
  echo "IPv4 internet on"
  sudo iptables -D OUTPUT -j INTERNET_OFF 2>/dev/null
else
  if [ $IS_CHAIN_ACTIVE -eq 0 ]; then
    echo "IPv4 internet off"
    sudo iptables -I OUTPUT 1 -j INTERNET_OFF
  else
    echo "IPv4 internet off already"
  fi
fi