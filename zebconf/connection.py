"""Zebra printer device connection"""

from abc import ABC, abstractmethod
import selectors
import socket
from urllib.parse import urlparse


class ZebraConnection(ABC):
    """A Zebra device connection"""

    def __init__(self, path):
        self.path = path

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.path)

    @abstractmethod
    def open(self):
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


class ZebraFileHandleConnection(ZebraConnection):
    """A Zebra file-handle device connection"""
    # pylint: disable=abstract-method

    def __init__(self, path):
        super().__init__(path)
        self.fh = None
        self.sel = selectors.DefaultSelector()

    def register(self, fh):
        """Register file handle"""
        self.fh = fh
        self.sel.register(self.fh, selectors.EVENT_READ)

    def close(self):
        self.sel.unregister(self.fh)
        self.fh.close()
        self.fh = None

    def write(self, data):
        return self.fh.write(data)

    def read(self, size, timeout=None):
        if not self.sel.select(timeout):
            return None
        return self.fh.read(size)


class ZebraFileConnection(ZebraFileHandleConnection):
    """A Zebra file device connection"""

    def open(self):
        super().open()
        self.register(open(self.path, 'r+b', buffering=0))


class ZebraNetworkConnection(ZebraFileHandleConnection):
    """A Zebra network device connection"""

    DEFAULT_PORT = 9100
    """Default port number for Zebra device"""

    def open(self):
        super().open()
        url = urlparse('//%s' % self.path)
        address = (url.hostname, url.port or self.DEFAULT_PORT)
        sock = socket.create_connection(address)
        self.register(sock.makefile('rwb', buffering=0))
        sock.close()
