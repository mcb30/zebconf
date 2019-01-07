"""Zebra printer device"""

import logging
import pathlib
import re
import selectors
from .config import ZebraConfigRoot

logger = logging.getLogger(__name__)


class UnknownVariableError(LookupError):
    """Unknown configuration variable"""
    pass


class ZebraDevice(object):
    """A Zebra printer device"""

    DEFAULT_PATH = '/dev/usb/lp0'
    """Default path to Zebra device"""

    MAX_RESPONSE_LEN = 16384
    """Maximum expected response length for any command"""

    DEFAULT_TIMEOUT = 0.5
    """Timeout used when reading from device"""

    config = ZebraConfigRoot()

    def __init__(self, path=DEFAULT_PATH):
        self.path = pathlib.Path(path)
        self.sel = selectors.DefaultSelector()
        self.fh = None

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, str(self.path))

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def __getitem__(self, key):
        return self.getvar(key)

    def __setitem__(self, key, value):
        self.setvar(key, value)

    def open(self):
        """Open device"""
        self.fh = self.path.open('r+b', buffering=0)
        self.sel.register(self.fh, selectors.EVENT_READ)

    def close(self):
        """Close device"""
        self.sel.unregister(self.fh)
        self.fh.close()

    def write(self, data, printable=True):
        """Write data to device"""
        logger.debug('tx: %s',
                     data.decode().strip() if printable else data.hex())
        self.fh.write(data)

    def read(self, expect=None, timeout=None, printable=True):
        """Read data from device

        There is no consistent structure or delimiter for data read
        from the device.  The only viable approach is to read until an
        expected pattern match is seen, or a timeout occurs.
        """
        if timeout is None:
            timeout = self.DEFAULT_TIMEOUT
        data = b''
        while self.sel.select(timeout):
            data += self.fh.read(self.MAX_RESPONSE_LEN)
            if expect is not None and re.fullmatch(expect, data):
                break
        if not data:
            raise TimeoutError
        logger.debug('rx: %s', data.decode() if printable else data.hex())
        return data

    def do(self, action, param=''):
        """Execute command"""
        self.write(b'! U1 do "%s" "%s"\r\n' %
                   (action.encode(), param.encode()))

    def setvar(self, name, value):
        """Set variable value"""
        self.write(b'! U1 setvar "%s" "%s"\r\n' %
                   (name.encode(), value.encode()))

    def getvar(self, name):
        """Get variable value"""
        self.write(b'! U1 getvar "%s"\r\n' % name.encode())
        value = self.read(rb'".+?"').decode()
        if value == '"?"':
            raise UnknownVariableError(name)
        return value.strip('"')

    def reset(self):
        """Reset device"""
        self.do('device.reset')

    def restore_defaults(self, category):
        """Restore configuration defaults"""
        self.do('device.restore_defaults', category)
