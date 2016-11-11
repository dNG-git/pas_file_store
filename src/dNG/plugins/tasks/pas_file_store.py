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

# pylint: disable=unused-argument

from dNG.plugins.hook import Hook
from dNG.runtime.value_exception import ValueException
from dNG.vfs.cached_implementation import CachedImplementation

def store_vfs_url(params, last_return = None):
    """
Called for "dNG.pas.vfs.CachedObject.storeVfsUrl"

:param params: Parameter specified
:param last_return: The return value from the last hook called.

:since: v0.2.00
    """

    if (last_return is not None): _return = last_return
    elif ("vfs_url" not in params): raise ValueException("Missing required argument")
    else:
        CachedImplementation.store_cached_vfs_url(params['vfs_url'], params.get("cached_data", { }))
        _return = True
    #

    return _return
#

def register_plugin():
    """
Register plugin hooks.

:since: v0.2.00
    """

    Hook.register("dNG.pas.vfs.CachedObject.storeVfsUrl", store_vfs_url)
#

def unregister_plugin():
    """
Unregister plugin hooks.

:since: v0.2.00
    """

    Hook.unregister("dNG.pas.vfs.CachedObject.storeVfsUrl", store_vfs_url)
#
