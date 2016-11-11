# -*- coding: utf-8 -*-

"""
direct PAS
Python Application Services
----------------------------------------------------------------------------
(C) direct Netware Group - All rights reserved
https://www.direct-netware.de/redirect?pas;file_store

This Source Code Form is subject to the terms of the Mozilla Public License,
v. 2.0. If a copy of the MPL was not distributed with this file, You can
obtain one at http://mozilla.org/MPL/2.0/.
----------------------------------------------------------------------------
https://www.direct-netware.de/redirect?licenses;mpl2
----------------------------------------------------------------------------
#echo(pasFileStoreVersion)#
#echo(__FILEPATH__)#
"""

from dNG.data.stored_file import StoredFile

class File(StoredFile):
    """
"File" represents a cached (mostly generated) file in the store.

:author:     direct Netware Group et al.
:copyright:  direct Netware Group - All rights reserved
:package:    pas
:subpackage: file_store
:since:      v0.2.00
:license:    https://www.direct-netware.de/redirect?licenses;mpl2
             Mozilla Public License, v. 2.0
    """

    STORE_ID = "cache"
    """
Default store ID for instances of this class
    """
    STORE_SIZE_MB_MAX = 2048
    """
Default maximum size for instances of this class
    """
    STORE_SUBDIRECTORY_LENGTH = 4
    """
Default number of characters used to create the subdirectory structure.
    """
#
