"""Zebra printer device connection"""

from __future__ import absolute_import
from future.utils import with_metaclass
from future.standard_library import install_aliases
install_aliases()

from abc import ABCMeta, abstractmethod
import errno
import select
import socket
from urllib.parse import urlparse
import usb


class ZebraConnection(with_metaclass(ABCMeta)):
    """A Zebra device connection"""

    def __init__(self, path=None):
        self.path = path

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.path)

    @abstractmethod
    def open(self, timeout=None):
        """Open connection"""
        pass

    @abstractmethod
    def close(self):
        """Close connection"""
        pass

    @abstractmethod
    def write(self, data):
        """Write data to connection"""
        pass

    @abstractmethod
    def read(self, size, timeout=None):
        """Read data from connection"""
        pass


class ZebraFileConnection(ZebraConnection):
    """A Zebra file device connection"""
    # pylint: disable=abstract-method

    def __init__(self, path=None):
        super(ZebraFileConnection, self).__init__(path)
        self.fh = None

    def open(self, timeout=None):
        self.fh = open(self.path, 'r+b', buffering=0)

    def close(self):
        self.fh.close()
        self.fh = None

    def write(self, data):
        self.fh.write(data)

    def read(self, size, timeout=None):
        if not select.select([self.fh], [], [], timeout)[0]:
            return None
        return self.fh.read(size)


class ZebraNetworkConnection(ZebraConnection):
    """A Zebra network device connection"""

    DEFAULT_PORT = 9100
    """Default port number for Zebra device"""

    def __init__(self, path=None):
        super(ZebraNetworkConnection, self).__init__(path)
        self.sock = None

    def open(self, timeout=None):
        super(ZebraNetworkConnection, self).open()
        url = urlparse('//%s' % self.path)
        address = (url.hostname, url.port or self.DEFAULT_PORT)
        self.sock = socket.create_connection(address, timeout)

    def close(self):
        self.sock.close()
        self.sock = None

    def write(self, data):
        self.sock.sendall(data)

    def read(self, size, timeout=None):
        if not select.select([self.sock.fileno()], [], [], timeout)[0]:
            return None
        return self.sock.recv(size)


class ZebraUsbConnection(ZebraConnection):
    """A Zebra USB device connection"""

    DEFAULT_VENDOR = 0x0a5f
    """Default vendor ID for Zebra device"""

    def __init__(self, path=None):
        super(ZebraUsbConnection, self).__init__(path)
        self.dev = None
        self.intf = None
        self.ep_in = None
        self.ep_out = None

    def open(self, timeout=None):
        intfs = lambda dev: (usb.util.find_descriptor(
            cfg, bInterfaceClass=usb.CLASS_PRINTER
        ) for cfg in dev)
        self.dev = usb.core.find(idVendor=self.DEFAULT_VENDOR,
                                 custom_match=lambda dev: any(intfs(dev)))
        if self.dev is None:
            raise OSError(errno.ENOENT, "No Zebra printers found")
        self.intf = next(intfs(self.dev))
        ep_dir = lambda ep: usb.util.endpoint_direction(ep.bEndpointAddress)
        self.ep_in = next(x for x in self.intf
                          if ep_dir(x) == usb.ENDPOINT_IN)
        self.ep_out = next(x for x in self.intf
                           if ep_dir(x) == usb.ENDPOINT_OUT)
        try:
            self.dev.detach_kernel_driver(self.intf.bInterfaceNumber)
        except (NotImplementedError, usb.USBError):
            pass
        usb.util.claim_interface(self.dev, self.intf)
        self.dev.reset()

    def close(self):
        usb.util.release_interface(self.dev, self.intf)
        try:
            self.dev.attach_kernel_driver(self.intf.bInterfaceNumber)
        except (NotImplementedError, usb.USBError):
            pass
        usb.util.dispose_resources(self.dev)

    def write(self, data):
        return self.ep_out.write(data)

    def read(self, size, timeout=None):
        timeout_ms = None if timeout is None else int(timeout * 1000)
        try:
            raw = self.ep_in.read(size, timeout_ms)
        except usb.USBError as e:
            if e.errno == errno.ETIMEDOUT:
                return b''
            raise
        return raw.tostring()
