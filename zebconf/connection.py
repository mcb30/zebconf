"""Zebra printer device connection"""

from abc import ABC, abstractmethod
import errno
import selectors
import socket
from urllib.parse import urlparse
import usb


class ZebraConnection(ABC):
    """A Zebra device connection"""

    def __init__(self, path=None):
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

    def __init__(self, path=None):
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


class ZebraUsbConnection(ZebraConnection):
    """A Zebra USB device connection"""

    DEFAULT_VENDOR = 0x0a5f
    """Default vendor ID for Zebra device"""

    def __init__(self, path=None):
        super().__init__(path)
        self.dev = None
        self.intf = None
        self.ep_in = None
        self.ep_out = None

    def open(self):
        intfs = lambda dev: (usb.util.find_descriptor(
            cfg, bInterfaceClass=usb.CLASS_PRINTER
        ) for cfg in dev)
        self.dev = usb.core.find(idVendor=self.DEFAULT_VENDOR,
                                 custom_match=lambda dev: any(intfs(dev)))
        if self.dev is None:
            raise FileNotFoundError("No Zebra printers found")
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
        return bytes(raw)
