# NetWatch — Network Uptime Monitor

A simple ping-based uptime monitor for small networks and homelabs.
Checks hosts concurrently, prints up/down status with latency,
alerts on failures, and logs every round to CSV.

## Features

- Monitor individual hosts or sweep a whole subnet (`--subnet`)
- Concurrent checks (fast even on a /24)
- CSV logging for uptime history and reporting
- Repeat mode (`--interval`) for continuous monitoring
- Console alerts when a host goes down
- Only the Python standard library — no dependencies

## Usage

```bash
# Check a few hosts once
python3 netwatch.py 192.168.1.1 192.168.1.254 8.8.8.8

# Sweep a /24 subnet
python3 netwatch.py --subnet 192.168.1.0/24

# Monitor continuously every 60s and log to CSV
python3 netwatch.py --subnet 192.168.1.0/24 --interval 60 --log uptime.csv
```

## Example output

```
$ python3 netwatch.py 192.168.1.1 8.8.8.8
Monitoring 2 host(s)... (Ctrl+C to stop)
[2026-10-07 11:50:00] 2/2 hosts up
  UP    192.168.1.1 (0.8 ms)
  UP    8.8.8.8 (24.3 ms)
```

## CSV log format

`timestamp,host,status,latency_ms` — easy to open in Excel or feed into a dashboard.

## Requirements

- Python 3.8+
- Linux or macOS (uses the system `ping` command)

## License

MIT
