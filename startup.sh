#!/bin/bash

echo "begin" >/tmp/lolz.txt

# Get the absolute path of the script's directory
working_dir="$(cd "$(dirname "$0")" && pwd)"
echo "wd: $working_dir" >>/tmp/lolz.txt

# Start backend
cd "$working_dir/backend"
echo "pwd1: $(pwd)" >>/tmp/lolz.txt
./start.sh &

# Start frontend
cd "$working_dir/frontend"
echo "pwd2: $(pwd)" >>/tmp/lolz.txt
npm run dev &
