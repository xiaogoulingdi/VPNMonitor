import unittest

from vpn_monitor.adapters.xray_access_log import XrayAccessLogAdapter


class XrayAccessLogAdapterTest(unittest.TestCase):
    def test_parse_domain_event(self):
        raw = "2026/06/04 03:20:40 from 1.2.3.4:51234 accepted tcp:www.google.com:443 [VLESS TCP REALITY >> proxy] email: 1.puppy"
        event = XrayAccessLogAdapter().parse_line(raw)
        self.assertIsNotNone(event)
        self.assertEqual(event.domain, "www.google.com")
        self.assertEqual(event.dest_port, 443)
        self.assertEqual(event.email, "1.puppy")
        self.assertEqual(event.category, "overseas")

    def test_parse_cnki_as_domestic(self):
        raw = "2026/06/04 03:20:40 from 1.2.3.4:51234 accepted tcp:co2.cnki.net:443 [VLESS TCP REALITY >> proxy] email: 1.puppy"
        event = XrayAccessLogAdapter().parse_line(raw)
        self.assertIsNotNone(event)
        self.assertEqual(event.domain, "co2.cnki.net")
        self.assertEqual(event.category, "domestic")

    def test_ignores_unmatched_lines(self):
        self.assertIsNone(XrayAccessLogAdapter().parse_line("not an xray access log line"))


if __name__ == "__main__":
    unittest.main()
