import unittest
from unittest.mock import patch
import guest_inventory as g
class InventoryTests(unittest.TestCase):
    def test_wrong_host_before_commands(self):
        with patch.object(g.socket,'gethostname',return_value='production'),patch.object(g,'command') as command:
            with self.assertRaises(RuntimeError):g.main()
            command.assert_not_called()
    def test_wrong_ip_before_php(self):
        with patch.object(g.socket,'gethostname',return_value='kaltura-php74-baseline'),patch.object(g,'command',return_value='[{"addr_info":[{"local":"192.168.56.20"}]}]') as command:
            with self.assertRaises(RuntimeError):g.main()
            self.assertEqual(command.call_count,1)
    def test_wrong_runtime_stops(self):
        replies=['[{"addr_info":[{"local":"192.168.56.74"}]}]','8.3.6']
        with patch.object(g.socket,'gethostname',return_value='kaltura-php74-baseline'),patch.object(g,'command',side_effect=replies):
            with self.assertRaises(RuntimeError):g.main()
    def test_partial_inventory_never_web_attestation(self):
        replies=['[{"addr_info":[{"local":"192.168.56.74"}]}]','7.4.33','[PHP Modules]\njson\nPDO\n','ii \tphp7.4\t7.4.33-1\tamd64\n']
        with patch.object(g.socket,'gethostname',return_value='kaltura-php74-baseline'),patch.object(g,'command',side_effect=replies),patch.object(g,'digest',return_value='a'*64):
            result=g.main()
        self.assertFalse(result['web_runtime_proven']);self.assertFalse(result['baseline_acceptance']);self.assertEqual(result['http_requests'],0)
    def test_uninstalled_wildcard_matches_are_retained_not_runtime_packages(self):
        installed,other=g.packages('ii \tphp7.4\t7.4.33-1\tamd64\nun \tphp7.4-ctype\t\t\n')
        self.assertEqual(installed,[['php7.4','7.4.33-1','amd64']])
        self.assertEqual(other,[{'package':'php7.4-ctype','dpkg_status':'un '}])
    def test_installed_empty_version_rejected(self):
        with self.assertRaises(RuntimeError):g.packages('ii \tphp7.4\t\tamd64\n')
    def test_unknown_package_record_rejected(self):
        with self.assertRaises(RuntimeError):g.packages('not-public\n')
if __name__=='__main__':unittest.main()
