"""Zebra printer firmware"""

from __future__ import absolute_import

import logging
import os.path
import zipfile

logger = logging.getLogger(__name__)


class BadFirmwareError(Exception):
    """Invalid Zebra firmware image"""
    pass


class ZebraFirmware(object):
    """Zebra printer firmware"""
    # pylint: disable=too-few-public-methods

    def __init__(self, file):
        self.file = file
        with zipfile.ZipFile(file) as archive:
            zpls = [x for x in archive.namelist()
                    if os.path.splitext(x)[1].lower() == '.zpl']
            if not zpls:
                raise BadFirmwareError('No .zpl files in firmware')
            for zpl in zpls:
                logger.debug('found %s', zpl)
            if len(zpls) > 1:
                raise BadFirmwareError('Multiple .zpl files in firmware')
            self.zpl = zpls[0]
            with archive.open(self.zpl) as f:
                self.data = f.read()
            logger.debug('version %s', self.version)

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.file)

    def __bytes__(self):
        return self.data

    @property
    def version(self):
        """Firmware version"""
        return os.path.splitext(self.zpl)[0]
