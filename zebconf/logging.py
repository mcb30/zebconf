"""Zebra configuration logging"""

from __future__ import absolute_import

import logging

try:
    import colorlog
    Formatter = colorlog.ColoredFormatter
    colors = colorlog.default_log_colors.copy()
    colors.update({'DEBUG': 'cyan'})
except ImportError:
    Formatter = logging.Formatter
    colors = None


class ZebraFormatter(Formatter):
    """Zebra logging formatter"""

    def __init__(self, fmt, *args, **kwargs):
        if colors is not None:
            kwargs['log_colors'] = colors
            fmt = '%(log_color)s' + fmt
        super(ZebraFormatter, self).__init__(fmt, *args, **kwargs)
