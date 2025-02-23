# known-hosts-linter

**A tool to clean up your SSH `known_hosts` file**

By default, it will normalize your known hosts file by merging host lines that share the same key. If `--transitive` is set, then it will additionally propagate keys of different types to all hosts linked via either a key or an alias.

## Example

This tool will turn this hosts file:

```text
host2 ssh-ed25519 KEY
host1,ip1 ssh-ed25519 FOO
host1 ssh-rsa BAR
ip2 ssh-rsa BAR
ip2,ip3 ssh-baz BAZ
```

Into this:

```text
host1,ip1,ip2,ip3 ssh-ed25519 FOO
host1,ip1,ip2,ip3 ssh-rsa BAR
host1,ip1,ip2,ip3 ssh-baz BAZ
host2 ssh-ed25519 KEY
```

## Usage

1. Preview changes: `./lint.py --transitive --mode diff`
2. Apply: `./lint.py --transitive --mode apply`

There is not much more to it. You can optionally set the path to your known hosts file as first argument, or omit `--mode` to receive the output on stdout for further processing.

### About transitive key propagation

The `--transitive` flag, off by default, results key `FOO` in the example above being applied to `ip2`, because they are linked through key `bar` on `host1`. This is usually what you want to happen, but wildcard entries and custom setups where some hosts share some keys might be incompatible. Omit the flag if that's the case for you.

## Do I need this?

No, this exists purely to satisfy my OCD. I wanted an alphabetically sorted list of hosts that I connected to, and `sort` alone did not suffice. OpenSSH's maintenance of your known_hosts file is fine as-is. This tool does nothing for security (bugs in it might even decrease security).

## License

This project is licensed under the MIT License.
