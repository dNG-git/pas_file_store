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

from os import path

try: from urllib.parse import urlsplit
except ImportError: from urlparse import urlsplit

from dNG.pas.data.mime_type import MimeType
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

		self.supported_features['flush'] = self._supports_flush
		self.supported_features['implementing_instance'] = self._supports_implementing_instance
	#

	def get_implementing_instance(self):
	#
		"""
Returns the implementing instance.

:return: (mixed) Implementing instance
:since:  v0.2.00
		"""

		if (self._wrapped_resource is None): raise IOException("VFS object not opened")
		return self._wrapped_resource
	#

	def get_implementing_scheme(self):
	#
		"""
Returns the implementing scheme name.

:return: (str) Implementing scheme name
:since:  v0.2.00
		"""

		return "x-file-store"
	#

	def get_mimetype(self):
	#
		"""
Returns the mime type of this VFS object.

:return: (str) VFS object mime type
:since:  v0.2.00
		"""

		if (self._wrapped_resource is None): raise IOException("VFS object not opened")

		resource_data = path.splitext(urlsplit(self._wrapped_resource.get_resource()).path)
		mimetype_definition = MimeType.get_instance().get(resource_data[1][1:])

		return ("application/octet-stream" if (mimetype_definition is None) else mimetype_definition['type'])
	#

	def get_name(self):
	#
		"""
Returns the name of this VFS object.

:return: (str) VFS object name
:since:  v0.1.00
		"""

		if (self._wrapped_resource is None): raise IOException("VFS object not opened")
		return self._wrapped_resource.get_id()
	#

	def get_time_created(self):
	#
		"""
Returns the UNIX timestamp this object was created.

:return: (int) UNIX timestamp this object was created
:since:  v0.2.00
		"""

		return self.get_time_updated()
	#

	def get_time_updated(self):
	#
		"""
Returns the UNIX timestamp this object was updated.

:return: (int) UNIX timestamp this object was updated
:since:  v0.2.00
		"""

		if (self._wrapped_resource is None): raise IOException("VFS object not opened")
		return self._wrapped_resource.get_data_attributes("time_stored")['time_stored']
	#

	def get_type(self):
	#
		"""
Returns the type of this object.

:return: (int) Object type
:since:  v0.2.00
		"""

		if (self._wrapped_resource is None): raise IOException("VFS object not opened")
		return Object.TYPE_FILE
	#

	def get_url(self):
	#
		"""
Returns the URL of this VFS object.

:return: (str) VFS URL
:since:  v0.1.00
		"""

		if (self._wrapped_resource is None): raise IOException("VFS object not opened")
		return "x-file-store:///{0}".format(self._wrapped_resource.get_id())
	#

	def new(self, _type, vfs_url):
	#
		"""
Creates a new VFS object.

:param _type: VFS object type
:param vfs_url: VFS URL

:since: v0.1.00
		"""

		if (_type != Object.TYPE_FILE): raise OperationNotSupportedException()
		if (self._wrapped_resource is not None): raise IOException("Can't create new VFS object on already opened instance")

		stored_file_data = { }
		vfs_file_id = Abstract._get_id_from_vfs_url(vfs_url)

		stored_file = StoredFile()

		stored_file_data['resource'] = "x-file-store:///{0}".format(stored_file.get_id()
		                                                           if (len(vfs_file_id) < 1) else
		                                                           vfs_file_id
		                                                          )

		if (len(stored_file_data) > 0): stored_file.set_data_attributes(**stored_file_data)

		self._set_wrapped_resource(stored_file)
	#

	def open(self, vfs_url, readonly = False):
	#
		"""
Opens a VFS object.

:param vfs_url: VFS URL
:param readonly: Open object in readonly mode

:since: v0.1.00
		"""

		if (self._wrapped_resource is not None): raise IOException("Can't create new VFS object on already opened instance")

		vfs_file_id = Abstract._get_id_from_vfs_url(vfs_url)

		try: stored_file = StoredFile.load_id(vfs_file_id)
		except NothingMatchedException as handled_exception: raise IOException("VFS URL '{0}' is invalid".format(vfs_url), handled_exception)

		self._set_wrapped_resource(stored_file)
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

	def _supports_flush(self):
	#
		"""
Returns false if flushing buffers is not supported.

:return: (bool) True if flushing buffers is supported
:since:  v0.1.04
		"""

		return (self._wrapped_resource is not None)
	#

	def _supports_implementing_instance(self):
	#
		"""
Returns false if no underlying, implementing instance can be returned.

:return: (bool) True if an implementing instance can be returned.
:since:  v0.2.00
		"""

		return (self._wrapped_resource is not None)
	#
#

##j## EOF