"""Basic functionality"""

import unittest
from zebconf import ZebraDevice
from zebconf.cli import ZebraCommand


class InitTests(unittest.TestCase):

    def test_device(self):
        dev = ZebraDevice()

    def test_command(self):
        cli = ZebraCommand(['get', 'device.friendly_name'])
