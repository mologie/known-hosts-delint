#!/usr/bin/env python3
import sys
import re

def sort_host(host):
    # IPs are sorted after hostnames.
    if re.match(r'^\d{1,3}(?:\.\d{1,3}){3}$', host) or (host.startswith('[') and host.endswith(']')):
        return (1, host)
    return (0, host)

def key_type_order(key_type):
    order = {"ssh-ed25519": 0, "ssh-rsa": 1, "ecdsa-sha2-nistp256": 2}
    return order.get(key_type, 99)

def merge_known_hosts(filename):
    merged = {}
    with open(filename) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split()
            if len(parts) < 3:
                continue
            hosts, key_type, key = parts[0], parts[1], parts[2]
            merged.setdefault((key_type, key), set()).update(hosts.split(','))
    # Sort by custom key type order, then key type and key value.
    for (key_type, key), hosts in sorted(merged.items(), key=lambda item: (key_type_order(item[0][0]), item[0][0], item[0][1])):
        sorted_hosts = sorted(hosts, key=sort_host)
        print(f"{','.join(sorted_hosts)} {key_type} {key}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: known-hosts-delinter <known_hosts_file>")
        sys.exit(1)
    merge_known_hosts(sys.argv[1])
