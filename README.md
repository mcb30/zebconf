Zebra printer configuration tool
================================

[![Build Status](https://travis-ci.org/unipartdigital/zebconf.svg?branch=master)](https://travis-ci.org/unipartdigital/zebconf)

This package provides a command-line configuration tool for Zebra
[printers](https://www.zebra.com/gb/en/products/printers.html).  For
example:

* Get product name: `zebconf get device.product_name`
* Set hostname: `zebconf set device.friendy_name myzq520`
* Configure WiFi: `zebconf wifi myessid -p mypassword`
* Upgrade firmware: `zebconf upgrade V76.20.15Z.zip`
