"""Zebra configuration command line interface"""

import argparse
from collections import namedtuple
import logging
import re
import colorlog
from .device import ZebraDevice

LOG_FMT = '%(log_color)s%(levelname)s:%(name)s:%(message)s'
LOG_COLS = {**colorlog.default_log_colors, 'DEBUG': 'cyan'}


class NameValuePair(namedtuple('NameValuePair', ('name', 'value'))):
    """A name=value pair argument"""

    @classmethod
    def parse(cls, text):
        """Parse name=value pair from a string"""
        m = re.fullmatch(r'([\w\.]+)=(.+)', text)
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
        handler = colorlog.StreamHandler()
        handler.setFormatter(colorlog.ColoredFormatter(LOG_FMT,
                                                       log_colors=LOG_COLS))
        logging.basicConfig(level=self.loglevel, handlers=[handler])
        self.device = ZebraDevice(self.args.device)

    @classmethod
    def parser(cls, **kwargs):
        """Construct argument parser"""
        # pylint: disable=unused-variable
        parser = argparse.ArgumentParser(description=cls.__doc__, **kwargs)
        common = argparse.ArgumentParser(add_help=False)
        common.add_argument('--verbose', '-v', action='count', default=0)
        common.add_argument('--quiet', '-q', action='count', default=0)
        common.add_argument('--device', '-d', default=ZebraDevice.DEFAULT_PATH)
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
