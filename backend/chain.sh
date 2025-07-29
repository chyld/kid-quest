#!/bin/bash

# USAGE: chain.sh ON | OFF
# Master control script for IPv4 and IPv6 internet blocking

IS_ON="$1"

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Call both IPv4 and IPv6 scripts
echo "Managing IPv4 rules:"
"$SCRIPT_DIR/chain-v4.sh" "$IS_ON"

echo "Managing IPv6 rules:"
"$SCRIPT_DIR/chain-v6.sh" "$IS_ON"
