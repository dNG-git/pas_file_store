# -*- coding: utf-8 -*-
##j## BOF

"""
direct PAS
Python Application Services
----------------------------------------------------------------------------
(C) direct Netware Group - All rights reserved
https://www.direct-netware.de/redirect?pas;core

This Source Code Form is subject to the terms of the Mozilla Public License,
v. 2.0. If a copy of the MPL was not distributed with this file, You can
obtain one at http://mozilla.org/MPL/2.0/.
----------------------------------------------------------------------------
https://www.direct-netware.de/redirect?licenses;mpl2
----------------------------------------------------------------------------
#echo(pasCoreVersion)#
#echo(__FILEPATH__)#
"""

# pylint: disable=unused-argument

from dNG.pas.data.stored_file import StoredFile
from dNG.pas.database.nothing_matched_exception import NothingMatchedException
from dNG.pas.runtime.io_exception import IOException
from dNG.pas.runtime.operation_not_supported_exception import OperationNotSupportedException
from dNG.pas.vfs.abstract import Abstract
from dNG.pas.vfs.file_like_wrapper_mixin import FileLikeWrapperMixin

class Object(FileLikeWrapperMixin, Abstract):
#
	"""
Provides the VFS implementation for 'x-file-store' objects.

:author:     direct Netware Group
:copyright:  direct Netware Group - All rights reserved
:package:    pas
:subpackage: file_store
:since:      v0.1.00
:license:    https://www.direct-netware.de/redirect?licenses;mpl2
             Mozilla Public License, v. 2.0
	"""

	_FILE_WRAPPED_METHODS = ( "flush",
	                          "get_size",
	                          "is_eof",
	                          "is_valid",
	                          "read",
	                          "seek",
	                          "tell",
	                          "truncate",
	                          "write"
	                        )
	"""
File IO methods implemented by an wrapped resource.
	"""

	def __init__(self):
	#
		"""
Constructor __init__(Object)

:since: v0.1.00
		"""

		FileLikeWrapperMixin.__init__(self)

		self.stored_file = None
		"""
Underlying StoredFile instance
		"""
	#

	def get_name(self):
	#
		"""
Returns the name of this VFS object.

:return: (str) VFS object name
:since:  v0.1.03
		"""

		if (self.stored_file is None): raise IOException("VFS object not opened")
		return self.stored_file.get_id()
	#

	def get_uri(self):
	#
		"""
Returns the URI of this VFS object.

:return: (str) VFS URI
:since:  v0.1.03
		"""

		if (self.stored_file is None): raise IOException("VFS object not opened")
		return "x-file-store:///{0}".format(self.stored_file.get_id())
	#

	def new(self, _type, vfs_uri):
	#
		"""
Creates a new VFS object.

:param _type: VFS object type
:param vfs_uri: VFS URI

:since: v0.1.00
		"""

		if (_type != Object.TYPE_FILE): raise OperationNotSupportedException()
		if (self.stored_file is not None): raise IOException("Can't create new VFS object on already opened instance")

		stored_file_data = { }
		vfs_file_id = Abstract._get_id_from_vfs_uri(vfs_uri)

		self.stored_file = StoredFile()

		stored_file_data['resource'] = "x-file-store:///{0}".format(self.stored_file.get_id()
		                                                           if (len(vfs_file_id) < 1) else
		                                                           vfs_file_id
		                                                          )

		if (len(stored_file_data) > 0): self.stored_file.set_data_attributes(**stored_file_data)

		self._set_wrapped_resource(self.stored_file)
	#

	def open(self, vfs_uri, readonly = False):
	#
		"""
Opens a VFS object.

:param vfs_uri: VFS URI
:param readonly: Open object in readonly mode

:since: v0.1.00
		"""

		if (self.stored_file is not None): raise IOException("Can't create new VFS object on already opened instance")

		vfs_file_id = Abstract._get_id_from_vfs_uri(vfs_uri)

		try: self.stored_file = StoredFile.load_id(vfs_file_id)
		except NothingMatchedException as handled_exception: raise IOException("VFS URI '{0}' is invalid".format(vfs_uri), handled_exception)

		self._set_wrapped_resource(self.stored_file)
	#

	def scan(self):
	#
		"""
Scan over objects of a collection like a directory.

:return: (object) Child VFS object
:since:  v0.1.00
		"""

		raise OperationNotSupportedException()
	#
#

##j## EOF