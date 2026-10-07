#!/usr/bin/env python3
"""
NetWatch — simple network uptime monitor
========================================
Pings a list of hosts (or a whole subnet), reports up/down status,
and logs every check to a CSV file for later analysis.

Usage:
    python3 netwatch.py 192.168.1.1 192.168.1.254 8.8.8.8
    python3 netwatch.py --subnet 192.168.1.0/24
    python3 netwatch.py --subnet 192.168.1.0/24 --interval 60 --log uptime.csv

Only the Python standard library is required. Works on Linux/macOS.
"""

import argparse
import csv
import ipaddress
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime


def ping(host: str, timeout: int = 2) -> tuple:
    """Ping a host once. Returns (host, is_up, latency_ms)."""
    try:
        result = subprocess.run(
            ["ping", "-c", "1", "-W", str(timeout), host],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=timeout + 2,
        )
    except (subprocess.SubprocessError, OSError):
        return host, False, None

    if result.returncode != 0:
        return host, False, None

    latency = None
    for line in result.stdout.splitlines():
        if "time=" in line:
            try:
                latency = float(line.split("time=")[1].split()[0])
            except (IndexError, ValueError):
                pass
            break
    return host, True, latency


def check_hosts(hosts, workers: int = 32, timeout: int = 2):
    """Check all hosts concurrently. Returns a list of (host, is_up, latency)."""
    results = []
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(ping, h, timeout): h for h in hosts}
        for future in as_completed(futures):
            results.append(future.result())
    # Keep output ordered by IP/hostname for readability.
    results.sort(key=lambda r: r[0])
    return results


def log_csv(path: str, timestamp: str, results):
    """Append one check round to the CSV log file."""
    write_header = False
    try:
        with open(path, "r", encoding="utf-8"):
            pass
    except FileNotFoundError:
        write_header = True
    with open(path, "a", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        if write_header:
            writer.writerow(["timestamp", "host", "status", "latency_ms"])
        for host, is_up, latency in results:
            writer.writerow([
                timestamp,
                host,
                "UP" if is_up else "DOWN",
                f"{latency:.2f}" if latency is not None else "",
            ])


def run_once(hosts, log_path: str, timeout: int):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    results = check_hosts(hosts, timeout=timeout)
    up = sum(1 for _, ok, _ in results if ok)
    print(f"[{timestamp}] {up}/{len(results)} hosts up")
    for host, is_up, latency in results:
        status = "UP  " if is_up else "DOWN"
        extra = f" ({latency:.1f} ms)" if latency is not None else ""
        print(f"  {status}  {host}{extra}")
        if not is_up:
            print(f"  ⚠ ALERT: {host} is not responding!", file=sys.stderr)
    if log_path:
        log_csv(log_path, timestamp, results)
    return results


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Ping-monitor hosts or a subnet and log uptime to CSV."
    )
    parser.add_argument("hosts", nargs="*", help="Hosts/IPs to monitor")
    parser.add_argument("--subnet", help="CIDR subnet to sweep, e.g. 192.168.1.0/24")
    parser.add_argument("--interval", type=int, default=0,
                        help="Repeat every N seconds (0 = run once)")
    parser.add_argument("--log", default="",
                        help="CSV file to append results to")
    parser.add_argument("--timeout", type=int, default=2,
                        help="Ping timeout in seconds (default: 2)")
    args = parser.parse_args()

    hosts = list(args.hosts)
    if args.subnet:
        try:
            net = ipaddress.ip_network(args.subnet, strict=False)
        except ValueError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1
        hosts.extend(str(ip) for ip in net.hosts())

    if not hosts:
        print("Error: give at least one host or --subnet", file=sys.stderr)
        return 1

    # Deduplicate while preserving order.
    hosts = list(dict.fromkeys(hosts))
    print(f"Monitoring {len(hosts)} host(s)... (Ctrl+C to stop)")

    try:
        while True:
            run_once(hosts, args.log, args.timeout)
            if args.interval <= 0:
                break
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\nStopped.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
