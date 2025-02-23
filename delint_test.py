import unittest
import textwrap
from io import StringIO
from delint import merge_known_hosts

def normstr(s):
    return textwrap.dedent(s).strip() + "\n"

def cmp(test, input_data, expected_output):
    with StringIO(normstr(input_data)) as infile, StringIO() as outfile:
        merge_known_hosts(infile, outfile)
        test.assertEqual(outfile.getvalue(), normstr(expected_output))

class TestMergeKnownHosts(unittest.TestCase):
    def test_merge_hosts_with_same_key(self):
        cmp(self, """
                  host1 ssh-ed25519 FOO
                  host2 ssh-ed25519 FOO
                  host3 ssh-rsa FOO
                  """,
                  """
                  host1,host2 ssh-ed25519 FOO
                  host3 ssh-rsa FOO
                  """)

    def test_hosts_with_different_keys(self):
        cmp(self, """
                  host1 ssh-ed25519 FOO
                  host2 ssh-ed25519 BAR
                  """,
                  """
                  host1 ssh-ed25519 FOO
                  host2 ssh-ed25519 BAR
                  """)

if __name__ == "__main__":
    unittest.main()
