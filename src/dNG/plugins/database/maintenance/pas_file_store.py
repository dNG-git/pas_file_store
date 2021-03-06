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

from dNG.module.named_loader import NamedLoader
from dNG.plugins.hook import Hook

def execute_auto_maintenance(params, last_return = None):
    """
Executes database auto-maintenance tasks.

:param params: Parameter specified
:param last_return: The return value from the last hook called.

:return: (mixed) Return value
:since:  v0.2.00
    """

    stored_file = NamedLoader.get_instance("dNG.data.StoredFile")
    stored_file.db_cleanup()

    _file = NamedLoader.get_instance("dNG.data.cache.File")
    _file.db_cleanup()

    return last_return
#

def register_plugin():
    """
Register plugin hooks.

:since: v0.2.00
    """

    Hook.register("dNG.pas.Database.executeAutoMaintenance", execute_auto_maintenance)
#

def unregister_plugin():
    """
Unregister plugin hooks.

:since: v0.2.00
    """

    Hook.unregister("dNG.pas.Database.executeAutoMaintenance", execute_auto_maintenance)
#
