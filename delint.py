#!/usr/bin/env python3

import argparse, difflib, os, re, sys, tempfile
from collections import defaultdict
from io import StringIO
from pathlib import Path

def sort_host(host):
    # IPs are sorted after hostnames.
    if re.match(r'^\d{1,3}(?:\.\d{1,3}){3}$', host) or (host.startswith('[') and host.endswith(']')):
        return (1, host)
    return (0, host)

def key_type_order(key):
    key_type, _, _ = key.partition(' ')
    order = {"ssh-ed25519": 0, "ssh-rsa": 1, "ecdsa-sha2-nistp256": 2}
    return order.get(key_type, 99)

def merge_known_hosts(infile, outfile, transitive=False):
    key_to_hosts = defaultdict(set)
    host_to_keys = defaultdict(set)
    for line in infile:
        line = line.strip()
        if not line or line.startswith('#') or line.startswith('@'):
            # can't process this
            outfile.write(line + '\n')
            continue
        hosts, _, key = line.partition(' ')
        if key == '':
            # syntax error, OpenSSH would skip the line too
            outfile.write(line + '\n')
            continue
        for host in hosts.split(','):
            key_to_hosts[key].add(host)
            host_to_keys[host].add(key)
    if transitive:
        changed = True
        while changed:
            changed = False
            for key, hosts in list(key_to_hosts.items()):
                new_hosts = hosts | {h for host in hosts for k in host_to_keys[host] for h in key_to_hosts[k]}
                if new_hosts != hosts:
                    key_to_hosts[key] = new_hosts
                    changed = True
    sorted_keys = {k: sorted(v, key=sort_host) for k, v in key_to_hosts.items()}
    for key, hosts in sorted(sorted_keys.items(), key=lambda item: (item[1], key_type_order(item[0]), item[0])):
        outfile.write(f"{','.join(hosts)} {key}\n")

def main():
    parser = argparse.ArgumentParser(description="Delint known_hosts file")
    parser.add_argument('known_hosts_file', nargs='?', default=os.path.expanduser('~/.ssh/known_hosts'), help="Path to the known_hosts file")
    parser.add_argument('--mode', choices=['diff', 'apply', 'emit'], default='emit', help="Mode of operation: 'diff' to emit a diff, 'apply' to replace the input file, 'emit' to write to stdout (default)")
    parser.add_argument('--transitive', action='store_true', help="Enable transitive merging")
    args = parser.parse_args()
    input_path = Path(args.known_hosts_file)

    if args.mode == 'diff':
        input_text = input_path.read_text()
        output_io = StringIO()
        merge_known_hosts(StringIO(input_text), output_io, transitive=args.transitive)
        diff = difflib.unified_diff(
            input_text.splitlines(keepends=True),
            output_io.getvalue().splitlines(keepends=True),
            fromfile='old_known_hosts',
            tofile='new_known_hosts')
        exit_code = 0
        for line in diff:
            sys.stdout.write(line)
            exit_code = 1
        sys.exit(exit_code)
    elif args.mode == 'apply':
        try:
            with open(args.known_hosts_file) as input_io:
                with tempfile.NamedTemporaryFile('w', delete=False, dir=input_path.parent) as temp_file:
                    merge_known_hosts(input_io, temp_file, transitive=args.transitive)
                    temp_file.flush()
                    os.replace(temp_file.name, args.known_hosts_file)
        except Exception as e:
            os.remove(temp_file.name)
            raise e
    else:
        with open(args.known_hosts_file) as input_io:
            merge_known_hosts(input_io, sys.stdout, transitive=args.transitive)

if __name__ == '__main__':
    main()
