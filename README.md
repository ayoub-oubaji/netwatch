# Cisco Config Backup

Automated backup of Cisco IOS running configurations over SSH.
A practical network-automation tool for technicians managing
switches and routers.

## Features

- Connects to multiple Cisco IOS devices over SSH (via Netmiko)
- Saves `show running-config` with hostname + timestamp
- JSON device inventory (template included)
- Clear per-device success/failure reporting
- Credentials prompted interactively — never stored in files

## Usage

```bash
pip install -r requirements.txt

# 1. Create your inventory from the template
cp devices.example.json devices.json
# 2. Edit devices.json with your real device IPs/names
# 3. Run the backup
python3 backup.py
```

Backups land in `backups/<hostname>/<timestamp>.cfg`.

Options:

```bash
python3 backup.py --inventory lab.json --out ./lab_backups --username admin
```

## Inventory format

```json
{
  "devices": [
    {"device_type": "cisco_ios", "host": "192.168.1.1", "name": "edge-router-01"},
    {"device_type": "cisco_ios", "host": "192.168.1.2", "name": "core-switch-01"}
  ]
}
```

## Security notes

- `devices.json` (real credentials/IPs) is git-ignored — only the
  `.example.json` template is committed.
- Passwords are read with `getpass` and never written to disk.

## Requirements

- Python 3.8+
- netmiko (`pip install -r requirements.txt`)
- SSH access to the target Cisco devices

## License

MIT
