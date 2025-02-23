#!/usr/bin/env python3
import sys
import re

def sort_host(host):
    # IPs are sorted after hostnames.
    if re.match(r'^\d{1,3}(?:\.\d{1,3}){3}$', host) or (host.startswith('[') and host.endswith(']')):
        return (1, host)
    return (0, host)

def key_type_order(key):
    key_type, _, _ = key.partition(' ')
    order = {"ssh-ed25519": 0, "ssh-rsa": 1, "ecdsa-sha2-nistp256": 2}
    return order.get(key_type, 99)

def merge_known_hosts(infile, outfile):
    merged = {}
    for line in infile:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        hosts, _, key = line.partition(' ')
        merged.setdefault(key, set()).update(hosts.split(','))
    for key, hosts in sorted(merged.items(), key=lambda item: (item[0][1], key_type_order(item[0][0]), item[0][0])):
        sorted_hosts = sorted(hosts, key=sort_host)
        outfile.write(f"{','.join(sorted_hosts)} {key}\n")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: known-hosts-delinter <known_hosts_file>")
        sys.exit(1)
    with open(sys.argv[1]) as infile, sys.stdout as outfile:
        merge_known_hosts(infile, outfile)
