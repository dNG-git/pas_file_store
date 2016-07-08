# -*- coding: utf-8 -*-
##j## BOF

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

from dNG.database.schema import Schema
from dNG.module.named_loader import NamedLoader
from dNG.plugins.hook import Hook

def after_apply_schema(params, last_return = None):
#
	"""
Called for "dNG.pas.Database.applySchema.after"

:param params: Parameter specified
:param last_return: The return value from the last hook called.

:return: (mixed) Return value
:since:  v0.2.00
	"""

	stored_file_class = NamedLoader.get_class("dNG.database.instances.StoredFile")
	Schema.apply_version(stored_file_class)

	return last_return
#

def load_all(params, last_return = None):
#
	"""
Load and register all SQLAlchemy objects to generate database tables.

:param params: Parameter specified
:param last_return: The return value from the last hook called.

:return: (mixed) Return value
:since:  v0.2.00
	"""

	NamedLoader.get_class("dNG.database.instances.StoredFile")
	return last_return
#

def register_plugin():
#
	"""
Register plugin hooks.

:since: v0.2.00
	"""

	Hook.register("dNG.pas.Database.applySchema.after", after_apply_schema)
	Hook.register("dNG.pas.Database.loadAll", load_all)
#

def unregister_plugin():
#
	"""
Unregister plugin hooks.

:since: v0.2.00
	"""

	Hook.unregister("dNG.pas.Database.applySchema.after", after_apply_schema)
	Hook.unregister("dNG.pas.Database.loadAll", load_all)
#

##j## EOF