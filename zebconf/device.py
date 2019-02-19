"""Zebra printer device"""

from __future__ import absolute_import

import binascii
import errno
import logging
import re
from passlib.utils import pbkdf2
from .connection import (ZebraFileConnection, ZebraNetworkConnection,
                         ZebraUsbConnection)

logger = logging.getLogger(__name__)


class UnknownVariableError(LookupError):
    """Unknown configuration variable"""
    pass


class ZebraDevice(object):
    """A Zebra printer device"""

    MAX_RESPONSE_LEN = 16384
    """Maximum expected response length for any command"""

    DEFAULT_TIMEOUT = 2.0
    """Timeout used when reading from device"""

    def __init__(self, path=None, timeout=None):
        if path is None:
            self.conn = ZebraUsbConnection()
        elif '/' in path:
            self.conn = ZebraFileConnection(path)
        else:
            self.conn = ZebraNetworkConnection(path)
        self.timeout = timeout if timeout is not None else self.DEFAULT_TIMEOUT

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.conn.path)

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
        self.conn.open(self.timeout)

    def close(self):
        """Close device"""
        self.conn.close()

    def write(self, data, printable=True):
        """Write data to device"""
        logger.debug('tx: %s',
                     data.decode().strip() if printable else
                     ''.join('%02x' % x for x in bytearray(data)))
        self.conn.write(data)

    def read(self, expect=None, printable=True):
        """Read data from device

        There is no consistent structure or delimiter for data read
        from the device.  The only viable approach is to read until an
        expected pattern match is seen, or a timeout occurs.
        """
        data = b''
        while True:
            frag = self.conn.read(self.MAX_RESPONSE_LEN, self.timeout)
            if not frag:
                break
            logger.debug('rx: %s',
                         frag.decode() if printable else
                         ''.join('%02x' % x for x in bytearray(frag)))
            data += frag
            if expect is not None and re.match(expect, data):
                break
        if not data:
            raise OSError(errno.ETIMEDOUT, "Timed out waiting for response")
        return data

    def do(self, action, param=''):
        """Execute command"""
        self.write(b'! U1 do "%s" "%s"\r\n' %
                   (action.encode(), param.encode()))

    def setvar(self, name, value):
        """Set variable value"""
        self.write(b'! U1 setvar "%s" "%s"\r\n' %
                   (name.encode(), value.encode()))

    def setint(self, name, value):
        """Set integer variable value"""
        self.setvar(name, str(value))

    def setbool(self, name, value):
        """Set boolean variable value"""
        self.setvar(name, 'on' if value else 'off')

    def getvar(self, name):
        """Get variable value"""
        self.write(b'! U1 getvar "%s"\r\n' % name.encode())
        value = self.read(br'".+?"$').decode()
        if value == '"?"':
            raise UnknownVariableError(name)
        return value.strip('"')

    def getint(self, name):
        """Get integer variable value"""
        return int(self.getvar(name))

    def getbool(self, name):
        """Get boolean variable value"""
        value = self.getvar(name)
        if value == 'on':
            return True
        elif value == 'off':
            return False
        raise ValueError("%s: invalid value '%s'" % (name, value))

    def reset(self):
        """Reset device"""
        self.do('device.reset')

    def restore_defaults(self, category):
        """Restore configuration defaults"""
        self.do('device.restore_defaults', category)

    def list(self):
        """List files"""
        self.do('file.dir')
        return self.read().decode().strip('"')

    def delete(self, filename):
        """Remove file"""
        self.do('file.delete', filename)

    def rename(self, oldname, newname):
        """Rename file"""
        self.do('file.rename', '%s %s' % (oldname, newname))

    def download(self, filename):
        """Download file"""
        self.do('file.type', filename)
        return self.read(printable=False)

    def upload(self, filename, content):
        """Upload file"""
        self.write(b'! CISDFCRC16\r\n0000\r\n%s\r\n%08x\r\n0000\r\n%s' %
                   (filename.encode(), len(content), content), printable=False)

    def upgrade(self, firmware):
        """Upgrade firmware"""
        self.write(bytes(firmware))

    def wifi(self, essid, password, auth='wpa_psk', country=None):
        """Configure WiFi ESSID and password"""
        self.restore_defaults('wlan')
        self.setvar('wlan.essid', essid)
        if country is not None:
            self.setvar('wlan.country_code', country)
        getattr(self, 'wifi_%s' % auth)(essid, password)

    def wifi_wpa_psk(self, essid, password):
        """Configure WiFi ESSID and WPA-PSK password"""
        raw = pbkdf2.pbkdf2(password.encode(), essid.encode(), 4096, 32)
        psk = binascii.b2a_hex(raw).decode().upper()
        self.setbool('wlan.wpa.enable', True)
        self.setvar('wlan.wpa.authentication', 'psk')
        self.setvar('wlan.wpa.psk', psk)
