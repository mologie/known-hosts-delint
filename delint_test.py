import unittest
import textwrap
from io import StringIO
from delint import merge_known_hosts

def normstr(s):
    return textwrap.dedent(s).strip() + "\n"

def cmp(test, input_data, expected_output, **kwargs):
    with StringIO(normstr(input_data)) as infile, StringIO() as outfile:
        merge_known_hosts(infile, outfile, **kwargs)
        test.assertEqual(outfile.getvalue(), normstr(expected_output))

class TestMergeKnownHosts(unittest.TestCase):
    def test_sorting(self):
        cmp(self, """
                  1111:2222::3335,host3,1111:2222::3334,1111:2222::3333 ecdsa-sha2-nistp256 BAZ
                  10.0.0.1,host1 ssh-rsa FOO
                  host2 ecdsa-sha2-nistp256 BAR
                  host2 ssh-rsa BAR
                  host2 ssh-ed25519 BAR
                  """,
                  """
                  host1,10.0.0.1 ssh-rsa FOO
                  host2 ssh-ed25519 BAR
                  host2 ssh-rsa BAR
                  host2 ecdsa-sha2-nistp256 BAR
                  host3,1111:2222::3333,1111:2222::3334,1111:2222::3335 ecdsa-sha2-nistp256 BAZ
                  """)

    def test_hosts_with_same_key(self):
        cmp(self, """
                  host1 ssh-ed25519 FOO
                  host2 ssh-ed25519 FOO
                  host3 ssh-rsa FOO
                  host3,ip2 ssh-rsa BAR
                  """,
                  """
                  host1,host2 ssh-ed25519 FOO
                  host3 ssh-rsa FOO
                  host3,ip2 ssh-rsa BAR
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
        
    def test_hosts_transitive_union(self):
        cmp(self, """
                  host1,ip1 ssh-ed25519 FOO
                  host1 ssh-rsa BAR
                  ip2 ssh-rsa BAR
                  ip2,ip3 ssh-baz BAZ
                  host2 ssh-ed25519 BAR
                  """,
                  """
                  host1,ip1,ip2,ip3 ssh-ed25519 FOO
                  host1,ip1,ip2,ip3 ssh-rsa BAR
                  host1,ip1,ip2,ip3 ssh-baz BAZ
                  host2 ssh-ed25519 BAR
                  """,
                  transitive=True)

if __name__ == "__main__":
    unittest.main()
