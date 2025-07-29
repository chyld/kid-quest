#!/bin/bash

# IPv6 chain management
# USAGE: chain-v6.sh ON | OFF

DOES_CHAIN_EXIST=$(sudo ip6tables -S INTERNET_OFF 2>/dev/null | wc -l)

if [ $DOES_CHAIN_EXIST -gt 1 ]; then
  echo "IPv6 chain exists"
else
  echo "creating IPv6 chain"
  sudo ip6tables -N INTERNET_OFF
  sudo ip6tables -A INTERNET_OFF -j REJECT
fi

IS_ON="$1"
IS_CHAIN_ACTIVE=$(sudo ip6tables -L OUTPUT | grep INTERNET_OFF | wc -l)

if [ "$IS_ON" = "ON" ]; then
  echo "IPv6 internet on"
  sudo ip6tables -D OUTPUT -j INTERNET_OFF 2>/dev/null
else
  if [ $IS_CHAIN_ACTIVE -eq 0 ]; then
    echo "IPv6 internet off"
    sudo ip6tables -I OUTPUT 1 -j INTERNET_OFF
  else
    echo "IPv6 internet off already"
  fi
fi