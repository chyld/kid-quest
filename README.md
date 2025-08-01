# Kid Quest

- clone repo

## Requirements

- uv
- node
- tmux
- need to use a static IP, so can be remotely managed

## Backend

- add reward.txt; set initial value
- `./start.sh`
- http://localhost:8000/docs

## Frontend

- `npm install`
- `npm run dev`
- http://localhost:5173/

## Permissions

- `sudo visudo`
- `%sudo   ALL=(ALL:ALL) ALL, (ALL) NOPASSWD: /sbin/iptables, /sbin/ip6tables`

## GUI

- `uv sync`
- `uv run main.py`
- the `kidquest.desktop` needs to move to `$HOME/.local/share/applications`; does not need to `chmod +x`
- the `Path` in the desktop file is the only thing that would need to change for other systems; it is the `cwd`
- either add `uv` absolute path; or just edit the `~/.profile` and update the `PATH`; it runs on gnome login, so all downstream processes will inherit the env
