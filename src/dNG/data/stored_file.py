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

from os import path
from random import randrange
from sqlalchemy.sql.expression import and_
from sqlalchemy.sql.functions import sum as sql_sum
from time import time
import os
import re

try: from urllib.parse import urlsplit
except ImportError: from urlparse import urlsplit

from dNG.data.binary import Binary
from dNG.data.file import File
from dNG.data.settings import Settings
from dNG.database.connection import Connection
from dNG.database.instance import Instance
from dNG.database.instances.stored_file import StoredFile as _DbStoredFile
from dNG.database.nothing_matched_exception import NothingMatchedException
from dNG.database.transaction_context import TransactionContext
from dNG.runtime.io_exception import IOException
from dNG.runtime.value_exception import ValueException

class StoredFile(Instance):
#
	"""
"StoredFile" represents a (mostly generated) file in a local storage.

:author:     direct Netware Group et al.
:copyright:  direct Netware Group - All rights reserved
:package:    pas
:subpackage: file_store
:since:      v0.2.00
:license:    https://www.direct-netware.de/redirect?licenses;mpl2
             Mozilla Public License, v. 2.0
	"""

	_DB_INSTANCE_CLASS = _DbStoredFile
	"""
SQLAlchemy database instance class to initialize for new instances.
	"""
	STORE_ID = "default"
	"""
Default store ID for instances of this class
	"""
	STORE_SIZE_MB_MAX = -1
	"""
Default maximum size for instances of this class
	"""
	STORE_SUBDIRECTORY_LENGTH = 0
	"""
Default number of characters used to create the subdirectory structure.
	"""

	def __init__(self, db_instance = None):
	#
		"""
Constructor __init__(StoredFile)

:param db_instance: Encapsulated SQLAlchemy database instance

:since: v0.2.00
		"""

		Instance.__init__(self, db_instance)

		self.chmod_dirs = 0o750
		"""
chmod to set when creating a new directory
		"""
		self.chmod_files = 0o640
		"""
chmod to set when creating a new file
		"""
		self.db_id = None
		"""
Database ID used for reloading
		"""
		self.store_path = None
		"""
Store directory path
		"""
		self.stored_file = None
		"""
Stored file instance
		"""
		self.stored_file_path_name = None
		"""
Path and name of the stored file
		"""
		self.subdirectory_length = 0
		"""
Number of characters used to create the subdirectory structure for a file
store.
		"""
		self.umask = None
		"""
umask to set before creating a new directory or file
		"""

		chmod_dirs = Settings.get("pas_file_store_chmod_dirs")
		if (chmod_dirs is not None): self.chmod_dirs = int(chmod_dirs, 8)

		chmod_files = Settings.get("pas_file_store_chmod_files")
		if (chmod_files is not None): self.chmod_files = int(chmod_files, 8)

		self.umask = Settings.get("pas_file_store_umask")

		if (isinstance(db_instance, _DbStoredFile)): self._load_data()
	#

	def __del__(self):
	#
		"""
Destructor __del__(StoredFile)

:since: v0.1.00
		"""

		self.close()
	#

	def close(self):
	#
		"""
python.org: Flush and close this stream.

:since: v0.2.00
		"""

		if (self.log_handler is not None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}.close()- (#echo(__LINE__)#)", self, context = "pas_tasks_store")

		if (self.stored_file is not None):
		#
			try:
			#
				self.save()
				self.stored_file.close()
			#
			finally: self.stored_file = None
		#
	#

	def _create_writable_directory(self, path):
	#
		"""
Creates the file store directory given.

:param path: File store directory to be created

:since: v0.2.00
		"""

		if (self.umask is not None): os.umask(int(self.umask, 8))
		is_writable = False

		try:
		#
			os.mkdir(path, self.chmod_dirs)
			is_writable = os.access(path, os.W_OK)
		#
		except IOError: pass

		if (not is_writable): raise IOException("Failed to create file store directory '{0}'".format(path))
	#

	def db_cleanup(self):
	#
		"""
Cleans up the file store directory.

:since: v0.2.00
		"""

		with Connection.get_instance() as connection:
		#
			store_id = self.get_store_id()

			delete_condition = and_(_DbStoredFile.store_id == store_id,
			                        _DbStoredFile.timeout > 0,
			                        _DbStoredFile.timeout < int(time())
			                       )

			entries_deleted = connection.query(_DbStoredFile).filter(delete_condition).delete()

			store_max_mb_size = int(Settings.get("pas_file_store_{0}_max_mb_size".format(store_id), self.__class__.STORE_SIZE_MB_MAX))
			store_max_size = ((store_max_mb_size * 1048576) if (store_max_mb_size > 0) else -1)

			if (store_max_size > 0):
			#
				size_used = connection.query(sql_sum(_DbStoredFile.size)).filter(_DbStoredFile.store_id == store_id).scalar()

				if (size_used is not None and size_used > store_max_size):
				#
					db_query = connection.query(_DbStoredFile).filter(_DbStoredFile.store_id == store_id)
					db_query = db_query.order_by(_DbStoredFile.time_last_accessed.asc())
					db_query = db_query.limit(100)

					size_to_be_deleted = (size_used - store_max_size)

					while (size_to_be_deleted > 0):
					#
						loop_entries_deleted = 0

						with TransactionContext():
						#
							for cached_file in StoredFile.iterator(_DbStoredFile, connection.execute(db_query)):
							#
								try:
								#
									size_to_be_deleted -= cached_file.get_size()
									if (cached_file.delete()): loop_entries_deleted += 1
								#
								except Exception as handled_exception:
								#
									if (self.log_handler is not None): self.log_handler.error(handled_exception, context = "pas_file_store")
								#
							#
						#

						if (loop_entries_deleted == 0): break
						entries_deleted += loop_entries_deleted
					#
				#
			#

			if (entries_deleted > 0): connection.optimize_random(_DbStoredFile)
		#
	#

	def delete(self):
	#
		"""
Deletes this entry from the database.

:return: (bool) True on success
:since:  v0.2.00
		"""

		if (self.store_path is None): raise IOException("Invalid file instance state for deletion")

		with self:
		#
			stored_file_path_name = path.join(self.store_path, self.local.db_instance.file_location)

			_return = Instance.delete(self)

			if (_return and path.exists(stored_file_path_name)):
			#
				os.unlink(stored_file_path_name)
				if (self.log_handler is not None): self.log_handler.debug("{0!r} deleted file '{1}'", self, stored_file_path_name, context = "pas_file_store")
			#
		#

		return _return
	#

	def _ensure_store_exists(self):
	#
		"""
Checks and creates the file store directory.

:since: v0.2.00
		"""

		if (self.store_path is None): raise IOException("Invalid file instance state for file store access")
		if ((not Settings.get("pas_database_auto_maintenance", False)) and randrange(0, 30) < 1): self.db_cleanup()

		if (path.exists(self.store_path)):
		#
			if ((not path.isdir(self.store_path))
			    or (not os.access(self.store_path, os.W_OK))
			   ): raise IOException("File store directory '{0}' not writable".format(self.store_path))
		#
		else: self._create_writable_directory(self.store_path)
	#

	def _ensure_stored_file_instance(self):
	#
		"""
Checks or creates a new instance for the stored file.

:since: v0.2.00
		"""

		self._ensure_store_exists()

		if (self.stored_file_path_name is None):
		#
			with self:
			#
				resource = self.get_resource()
				if (resource is None): raise IOException("Can't create stored file instance without a resource URL")

				url_elements = urlsplit(resource)

				if (url_elements.path in ( "", "/", "/{0}".format(self.db_id) )): file_name = self.db_id
				else:
				#
					( _, file_name ) = path.split(url_elements.path)

					file_name = "{0}_{1}".format(self.db_id,
					                             file_name
					                            )
				#

				file_name = re.sub("\\W+", "_", file_name)

				file_location = file_name

				if (self.subdirectory_length > 0):
				#
					subdirectory_name = file_name[:self.subdirectory_length]
					file_name = (file_name[self.subdirectory_length:] if (self.subdirectory_length < 32) else file_name[33:])

					subdirectory_path_name = path.join(self.store_path, subdirectory_name)
					if (not path.exists(subdirectory_path_name)): self._create_writable_directory(subdirectory_path_name)

					file_location = "{0}/{1}".format(subdirectory_name, file_name)
				#

				file_path_name = path.join(self.store_path, path.normpath(file_location))

				self.stored_file = File()
				if (not self.stored_file.open(file_path_name, file_mode = "w+b")): raise IOException("Failed to create stored file instance")

				self.stored_file_path_name = file_path_name
				self.set_data_attributes(file_location = file_location)
			#
		#
		elif (self.stored_file is None):
		#
			file_path_name = path.join(self.store_path, self.stored_file_path_name)

			self.stored_file = File()
			if (not self.stored_file.open(file_path_name, file_mode = "r+b")): raise IOException("Failed to open stored file instance")
		#
	#

	def flush(self):
	#
		"""
python.org: Flush the write buffers of the stream if applicable.

:since: v0.2.00
		"""

		self._ensure_stored_file_instance()
		self.stored_file.flush()
	#

	def get_path_name(self):
	#
		"""
Returns the path and name of the stored file.

:return: (str) Path and name of the stored file
:since:  v0.2.00
		"""

		self._ensure_stored_file_instance()
		return path.abspath(path.join(self.store_path, self.stored_file_path_name))
	#

	get_id = Instance._wrap_getter("id")
	"""
Returns the stored file ID.

:return: (str) Stored file ID
:since:  v0.2.00
	"""

	get_resource = Instance._wrap_getter("resource")
	"""
Returns the stored file resource.

:return: (str) Stored file resource
:since:  v0.2.00
	"""

	def get_size(self):
	#
		"""
Returns the stored file resource size.

:return: (int) Stored file resource size
:since:  v0.2.00
		"""

		return (self.get_data_attributes("size")['size']
		        if (self.stored_file is None) else
		        self.stored_file.get_size()
		       )
	#

	def get_store_id(self):
	#
		"""
Returns the file store ID.

:return: (str) File store ID
:since:  v0.2.00
		"""

		_return = self.get_data_attributes("store_id")['store_id']
		if (_return == ""): _return = self.__class__.STORE_ID

		return _return
	#

	def get_vfs_url(self):
	#
		"""
Returns the VFS URL of this instance.

:return: (str) Stored file VFS URL; None if undefined
:since:  v0.2.00
		"""

		return "x-file-store:///{0}".format(self.get_id())
	#

	def is_eof(self):
	#
		"""
Checks if the pointer is at EOF.

:return: (bool) True if EOF
:since:  v0.2.00
		"""

		self._ensure_stored_file_instance()
		return self.stored_file.is_eof()
	#

	def is_up_to_date(self, timestamp):
	#
		"""
Checks if the stored version timestamp is the same or newer than the given
one.

:param timestamp: External timestamp to compare with

:return: (bool) True if up-to-date
:since:  v0.2.00
		"""

		with self: return (self.local.db_instance.time_stored >= timestamp)
	#

	def is_valid(self):
	#
		"""
Returns true if the stored file instance is valid.

:return: (bool) True if valid
:since:  v0.2.00
		"""

		with self:
		#
			return (self.local.db_instance.timeout is None
			        or self.local.db_instance.timeout >= int(time())
			       )
		#
	#

	def _load_data(self):
	#
		"""
Loads the StoredFile instance and populates variables.

:since: v0.2.00
		"""

		if (self.log_handler is not None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}._load_data()- (#echo(__LINE__)#)", self, context = "pas_tasks_store")

		with self:
		#
			self.db_id = self.local.db_instance.id
			self.local.db_instance.time_last_accessed = time()

			self._load_settings()

			self.stored_file_path_name = path.join(self.store_path,
			                                       path.normpath(self.get_data_attributes("file_location")['file_location'])
			                                      )
		#
	#

	def _load_settings(self):
	#
		"""
Loads settings based on the store ID of the StoredFile instance.

:since: v0.2.00
		"""

		store_id = self.get_store_id()

		if (not Settings.is_defined("pas_file_store_default_path")): Settings.read_file("{0}/settings/pas_file_store.json".format(Settings.get("path_data")))

		self.store_path = Settings.get("pas_file_store_{0}_path".format(store_id))
		if (self.store_path is None): raise ValueException("File store directory has not been configured for ID '{0}'".format(store_id))

		self.subdirectory_length = int(Settings.get("pas_file_store_{0}_subdirectory_length".format(store_id), self.__class__.STORE_SUBDIRECTORY_LENGTH))
		if (self.subdirectory_length > 32): raise ValueException("File store subdirectory length is invalid ID '{0}'".format(store_id))
	#

	def read(self, n = 0):
	#
		"""
python.org: Read up to n bytes from the object and return them.

:param n: How many bytes to read from the current position (0 means until
          EOF)

:return: (bytes) Data; None if EOF
:since:  v0.2.00
		"""

		with self:
		#
			self._ensure_stored_file_instance()
			self.set_data_attributes(time_last_accessed = time())

			return self.stored_file.read(n)
		#
	#

	def save(self):
	#
		"""
Saves changes of the database task instance.

:since: v0.2.00
		"""

		with self:
		#
			if (self.stored_file is not None
			    and hasattr(self.stored_file, "flush")
			   ): self.stored_file.flush()

			if (self.local.db_instance.time_stored is None): self.local.db_instance.time_stored = time()
			if (self.local.db_instance.time_last_accessed is None): self.local.db_instance.time_last_accessed = time()

			if (self.local.db_instance.size is None
			    and self.store_path is not None
			   ): self.local.db_instance.size = path.getsize(self.get_path_name())

			Instance.save(self)
		#
	#

	def seek(self, offset):
	#
		"""
python.org: Change the stream position to the given byte offset.

:param offset: Seek to the given offset

:return: (int) Return the new absolute position.
:since:  v0.2.00
		"""

		self._ensure_stored_file_instance()
		return self.stored_file.seek(offset)
	#

	def set_data_attributes(self, **kwargs):
	#
		"""
Sets values given as keyword arguments to this method.

:since: v0.2.00
		"""

		with self:
		#
			if (self.db_id is None): self.db_id = self.local.db_instance.id
			is_store_id_changed = (self.local.db_instance.store_id is None)

			if ("time_stored" in kwargs): self.local.db_instance.time_stored = int(kwargs['time_stored'])
			if ("time_last_accessed" in kwargs): self.local.db_instance.time_last_accessed = int(kwargs['time_last_accessed'])
			if ("timeout" in kwargs): self.local.db_instance.timeout = int(kwargs['timeout'])
			if ("resource" in kwargs): self.local.db_instance.resource = Binary.utf8(kwargs['resource'])

			if ("store_id" in kwargs):
			#
				self.local.db_instance.store_id = Binary.utf8(kwargs['store_id'])
				is_store_id_changed = True
			#
			elif (self.local.db_instance.store_id is None): self.local.db_instance.store_id = self.__class__.STORE_ID

			if (is_store_id_changed): self._load_settings()

			if ("file_location" in kwargs): self.local.db_instance.file_location = Binary.utf8(kwargs['file_location'])
		#
	#

	set_resource = Instance._wrap_setter("resource")
	"""
Sets the stored file resource.

:param value: Stored file resource

:since: v0.2.00
	"""

	def tell(self):
	#
		"""
python.org: Return the current stream position as an opaque number.

:return: (int) Stream position
:since:  v0.2.00
		"""

		self._ensure_stored_file_instance()
		return self.stored_file.tell()
	#

	def write(self, b):
	#
		"""
python.org: Write the given bytes or bytearray object, b, to the underlying
raw stream and return the number of bytes written.

:param b: (Over)write file with the given data at the current position

:return: (int) Number of bytes written
:since:  v0.2.00
		"""

		with self:
		#
			self._ensure_stored_file_instance()
			self.local.db_instance.size = None
		#

		return self.stored_file.write(b)
	#

	@staticmethod
	def _load(cls, db_instance):
	#
		"""
Load File entry from database.

:param cls: Expected encapsulating database instance class
:param db_instance: SQLAlchemy database instance

:return: (object) File instance on success
:since:  v0.2.00
		"""

		_return = None

		if (db_instance is not None):
		#
			with Connection.get_instance():
			#
				Instance._ensure_db_class(cls, db_instance)

				_return = StoredFile(db_instance)
				if (not _return.is_valid()): _return = None
			#
		#

		return _return
	#

	@classmethod
	def load_id(cls, _id):
	#
		"""
Load File by ID.

:param cls: Expected encapsulating database instance class
:param _id: File ID

:return: (object) File instance on success
:since:  v0.2.00
		"""

		if (_id is None): raise NothingMatchedException("File ID is invalid")

		with Connection.get_instance(): _return = StoredFile._load(cls, Instance.get_db_class_query(cls).get(_id))

		if (_return is None): raise NothingMatchedException("File ID '{0}' not found".format(_id))
		return _return
	#

	@classmethod
	def load_resource(cls, resource):
	#
		"""
Load File by the resource.

:param cls: Expected encapsulating database instance class
:param resource: File resource

:return: (object) File instance on success
:since:  v0.2.00
		"""

		if (resource is None): raise NothingMatchedException("File resource is invalid")

		with Connection.get_instance():
		#
			db_instance = Instance.get_db_class_query(cls).filter(_DbStoredFile.resource == resource).first()
			_return = StoredFile._load(cls, db_instance)
		#

		if (_return is None): raise NothingMatchedException("File resource '{0}' not found".format(resource))
		return _return
	#
#

##j## EOF