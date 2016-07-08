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

from sqlalchemy.schema import Column
from sqlalchemy.types import BIGINT, TEXT, VARCHAR
from uuid import uuid4 as uuid

from dNG.database.types.date_time import DateTime

from .abstract import Abstract

class StoredFile(Abstract):
#
	"""
SQLAlchemy database instance for StoredFile.

:author:     direct Netware Group et al.
:copyright:  (C) direct Netware Group - All rights reserved
:package:    pas
:subpackage: file_store
:since:      v0.2.00
:license:    https://www.direct-netware.de/redirect?licenses;mpl2
             Mozilla Public License, v. 2.0
	"""

	# pylint: disable=invalid-name

	__tablename__ = "{0}_stored_file".format(Abstract.get_table_prefix())
	"""
SQLAlchemy table name
	"""
	db_instance_class = "dNG.data.StoredFile"
	"""
Encapsulating SQLAlchemy database instance class name
	"""
	db_schema_version = 1
	"""
Database schema version
	"""

	id = Column(VARCHAR(32), primary_key = True)
	"""
stored_file.id
	"""
	time_stored = Column(DateTime, index = True, nullable = False)
	"""
stored_file.time_stored
	"""
	time_last_accessed = Column(DateTime, index = True, nullable = False)
	"""
stored_file.time_last_accessed
	"""
	timeout = Column(DateTime, index = True)
	"""
stored_file.timeout
	"""
	store_id = Column(VARCHAR(100), index = True, nullable = False)
	"""
stored_file.store_id
	"""
	resource = Column(TEXT, index = True, nullable = False)
	"""
stored_file.resource
	"""
	size = Column(BIGINT, index = True)
	"""
stored_file.size
	"""
	file_location = Column(VARCHAR(255), nullable = False)
	"""
stored_file.file_location
	"""

	def __init__(self, *args, **kwargs):
	#
		"""
Constructor __init__(StoredFile)

:since: v0.2.00
		"""

		Abstract.__init__(self, *args, **kwargs)
		if (self.id is None): self.id = uuid().hex
	#
#

##j## EOF