"""Zebra configuration command line interface"""

from __future__ import absolute_import, print_function

import argparse
from collections import namedtuple
import logging
import os.path
import re
from .device import ZebraDevice
from .firmware import ZebraFirmware
from .logging import ZebraFormatter


class NameValuePair(namedtuple('NameValuePair', ('name', 'value'))):
    """A name=value pair argument"""

    @classmethod
    def parse(cls, text):
        """Parse name=value pair from a string"""
        m = re.match(r'([\w\.]+)=(.+)$', text)
        if not m:
            raise ValueError(text)
        return cls(*m.groups())


class ZebraCommand(object):
    """Configure Zebra printer"""

    loglevels = [logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG]

    def __init__(self, argv=None):
        self.args = self.parser().parse_args(argv)
        self.verbosity = (self.loglevels.index(logging.INFO) +
                          self.args.verbose - self.args.quiet)
        handler = logging.StreamHandler()
        formatter = ZebraFormatter('%(levelname)s:%(name)s:%(message)s')
        handler.setFormatter(formatter)
        logging.basicConfig(level=self.loglevel, handlers=[handler])
        self.device = ZebraDevice(self.args.device, timeout=self.args.timeout)

    @classmethod
    def parser(cls, **kwargs):
        """Construct argument parser"""
        # pylint: disable=too-many-locals, unused-variable
        parser = argparse.ArgumentParser(description=cls.__doc__, **kwargs)
        common = argparse.ArgumentParser(add_help=False)
        common.add_argument('--verbose', '-v', action='count', default=0)
        common.add_argument('--quiet', '-q', action='count', default=0)
        common.add_argument('--device', '-d')
        common.add_argument('--timeout', '-t', type=float,
                            default=ZebraDevice.DEFAULT_TIMEOUT)
        cmds = parser.add_subparsers(title="subcommands", dest='subcommand')
        cmds.required = True

        getvar = cmds.add_parser('get', parents=[common])
        getvar.add_argument('variables', metavar='name', nargs='+')

        setvar = cmds.add_parser('set', parents=[common])
        setvar.add_argument('variables', metavar='name=value', nargs='+',
                            type=NameValuePair.parse)

        reset = cmds.add_parser('reset', parents=[common])

        restore = cmds.add_parser('restore', parents=[common])
        restore.add_argument('category')

        ls = cmds.add_parser('ls', parents=[common])

        rm = cmds.add_parser('rm', parents=[common])
        rm.add_argument('filename')

        mv = cmds.add_parser('mv', parents=[common])
        mv.add_argument('oldname')
        mv.add_argument('newname')

        cat = cmds.add_parser('cat', parents=[common])
        cat.add_argument('filename')

        pull = cmds.add_parser('pull', parents=[common])
        pull.add_argument('filename')
        pull.add_argument('--output', '-o')

        push = cmds.add_parser('push', parents=[common])
        push.add_argument('filename')
        push.add_argument('--input', '-i')

        upgrade = cmds.add_parser('upgrade', parents=[common])
        upgrade.add_argument('firmware')
        upgrade.add_argument('--check', action='store_true')

        wifi = cmds.add_parser('wifi', parents=[common])
        wifi.add_argument('essid')
        wifi.add_argument('--password', '-p')
        auth = wifi.add_mutually_exclusive_group()
        auth.add_argument('--wpa-psk', dest='auth', action='store_const',
                          const='wpa_psk')
        wifi.add_argument('--country')
        wifi.add_argument('--no-reset', dest='reset', action='store_false',
                          default=True)

        return parser

    @property
    def loglevel(self):
        """Log level"""
        return (self.loglevels[self.verbosity]
                if self.verbosity < len(self.loglevels) else logging.NOTSET)

    @classmethod
    def main(cls):
        """Execute command (as main entry point)"""
        cls().execute()

    def execute(self):
        """Execute command"""
        with self.device:
            getattr(self, self.args.subcommand)()

    def get(self):
        """Get variable(s)"""
        for name in self.args.variables:
            print(self.device.getvar(name))

    def set(self):
        """Set variable(s)"""
        for name, value in self.args.variables:
            self.device.setvar(name, value)

    def reset(self):
        """Reset device"""
        self.device.reset()

    def restore(self):
        """Restore configuration defaults"""
        self.device.restore_defaults(self.args.category)

    def ls(self):
        """List files"""
        print(self.device.list())

    def rm(self):
        """Remove file"""
        self.device.delete(self.args.filename)

    def mv(self):
        """Rename file"""
        self.device.rename(self.args.oldname, self.args.newname)

    def cat(self):
        """Get file contents"""
        print(self.device.download(self.args.filename).decode(), end='')

    def pull(self):
        """Download file"""
        outfile = self.args.output or self.args.filename
        name = os.path.basename(self.args.filename)
        with open(outfile, 'wb') as f:
            f.write(self.device.download(name))

    def push(self):
        """Upload file"""
        infile = self.args.input or self.args.filename
        name = os.path.basename(self.args.filename)
        with open(infile, 'rb') as f:
            self.device.upload(name, f.read())

    def upgrade(self):
        """Upgrade firmware"""
        firmware = ZebraFirmware(self.args.firmware)
        if not self.args.check:
            self.device.upgrade(firmware)

    def wifi(self):
        """Configure WiFi"""
        kwargs = {x: getattr(self.args, x)
                  for x in ('auth', 'country')
                  if getattr(self.args, x) is not None}
        self.device.wifi(self.args.essid, self.args.password, **kwargs)
        if self.args.reset:
            self.device.reset()
