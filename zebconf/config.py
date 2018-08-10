"""Zebra printer device configuration"""

# pylint: disable=too-few-public-methods

import binascii
import ipaddress
from passlib.utils import pbkdf2


class ZebraConfigBlock(object):
    """A Zebra configuration variable namespace"""

    __slots__ = ['_key', '_prefix', '_parent']

    def __init__(self, key=None, parent=None):
        self._key = key
        self._prefix = '' if key is None else key + '.'
        self._parent = parent

    def __repr__(self):
        if self._parent is None:
            return '%s(%r)' % (self.__class__.__name__, self._key)
        return '%r.%s' % (self._parent,
                          'config' if self._key is None else self._key)

    def __getitem__(self, key):
        return self._parent[self._prefix + key]

    def __setitem__(self, key, value):
        self._parent[self._prefix + key] = value

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return type(self)(self._key, parent=instance)


class ZebraConfig(object):
    """A Zebra configuration variable"""

    def __init__(self, name, readonly=False):
        self.name = name
        self.readonly = readonly

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.name)

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return self.from_string(instance[self.name])

    def __set__(self, instance, value):
        if self.readonly:
            raise AttributeError("%s: read-only variable" % self.name)
        instance[self.name] = self.to_string(value)

    @staticmethod
    def from_string(value):
        """Convert from raw string value"""
        return value

    @staticmethod
    def to_string(value):
        """Convert to raw string value"""
        return value


class ZebraConfigInteger(ZebraConfig):
    """A Zebra configuration variable using integer values"""

    @staticmethod
    def from_string(value):
        return int(value)

    @staticmethod
    def to_string(value):
        return str(value)


class ZebraConfigOnOff(ZebraConfig):
    """A Zebra configuration variable using values 'on' or 'off'"""

    def from_string(self, value):
        if value == 'on':
            return True
        elif value == 'off':
            return False
        raise ValueError("%s: invalid value '%s'" % (self.name, value))

    @staticmethod
    def to_string(value):
        return 'on' if value else 'off'


class ZebraConfigIpv4(ZebraConfig):
    """A Zebra configuration variable using IPv4 address values"""

    @staticmethod
    def from_string(value):
        return ipaddress.IPv4Address(value)

    @staticmethod
    def to_string(value):
        return str(value)


class ZebraConfigDevice(ZebraConfigBlock):
    """Zebra configuration variable namespace 'device'"""

    __slots__ = []

    friendly_name = ZebraConfig('friendly_name')


class ZebraConfigIpDhcp(ZebraConfigBlock):
    """Zebra configuration variable namespace 'ip.dhcp'"""

    __slots__ = []

    enable = ZebraConfigOnOff('enable')
    cid_type = ZebraConfigInteger('cid_type')


class ZebraConfigIp(ZebraConfigBlock):
    """Zebra configuration variable namespace 'ip'"""

    __slots__ = []

    dhcp = ZebraConfigIpDhcp('dhcp')


class ZebraConfigWlanIp(ZebraConfigBlock):
    """Zebra configuration variable namespace 'wlan.ip'"""

    __slots__ = []

    addr = ZebraConfigIpv4('addr')
    protocol = ZebraConfig('protocol')


class ZebraConfigWlanWpa(ZebraConfigBlock):
    """Zebra configuration variable namespace 'wlan.wpa'"""

    __slots__ = []

    authentication = ZebraConfig('authentication')
    enable = ZebraConfigOnOff('enable')
    psk = ZebraConfig('psk')

    def set_psk(self, essid, password):
        """Set WPA pre-shared key"""
        raw = pbkdf2.pbkdf2(password.encode(), essid.encode(), 4096, 32)
        self.psk = binascii.b2a_hex(raw).decode().upper()


class ZebraConfigWlan(ZebraConfigBlock):
    """Zebra configuration variable namespace 'wlan'"""

    __slots__ = []

    ip = ZebraConfigWlanIp('ip')
    wpa = ZebraConfigWlanWpa('wpa')

    allowed_band = ZebraConfig('allowed_band')
    country_code = ZebraConfig('country_code')
    encryption_mode = ZebraConfigOnOff('encryption_mode')
    essid = ZebraConfig('essid')
    international_mode = ZebraConfigOnOff('international_mode')
    operating_mode = ZebraConfig('operating_mode')
    power_save = ZebraConfigOnOff('power_save')

    def set_wpa_psk(self, password):
        """Set WPA pre-shared key"""
        self.wpa.set_psk(self.essid, password)


class ZebraConfigRoot(ZebraConfigBlock):
    """Zebra configuration variable root namespace"""

    __slots__ = []

    device = ZebraConfigDevice('device')
    ip = ZebraConfigIp('ip')
    wlan = ZebraConfigWlan('wlan')
