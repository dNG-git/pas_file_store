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

from dNG.data.cache.file import File
from dNG.data.logging.log_line import LogLine
from dNG.database.connection import Connection
from dNG.database.nothing_matched_exception import NothingMatchedException
from dNG.runtime.io_exception import IOException
from dNG.runtime.not_implemented_exception import NotImplementedException

try:
    from dNG.data.tasks.persistent import Persistent as PersistentTasks
    from dNG.tasks.persistent_lrt_hook import PersistentLrtHook
except ImportError: PersistentTasks = None

from .implementation import Implementation

class CachedImplementation(Implementation):
    """
"CachedImplementation" provides implementation independent methods to access
VFS objects that might be cached locally.

:author:     direct Netware Group et al.
:copyright:  direct Netware Group - All rights reserved
:package:    pas
:subpackage: file_store
:since:      v0.2.00
:license:    https://www.direct-netware.de/redirect?licenses;mpl2
             Mozilla Public License, v. 2.0
    """

    @staticmethod
    def cache_vfs_url(vfs_url, cached_data = None):
        """
Stores a given VFS URL in cache using the given cache data. It will be
scheduled as a background task.

:param vfs_url: VFS URL
:param cached_data: Cache data for the VFS URL

:since: v0.2.00
        """

        persistent_tasks = None

        try:
            if (PersistentTasks is not None): persistent_tasks = PersistentTasks.get_instance()
        except NotImplementedException: pass

        if (persistent_tasks is None):
            LogLine.warning("pas.file_store vfs.CachedImplementation requested to cache VFS URL '{0}' but 'pas.tasks' is not available", vfs_url, context = "pas_file_store")
        else:
            persistent_tasks_data = { "vfs_url": vfs_url }

            if (cached_data is not None
                and len(persistent_tasks_data) > 0
               ): persistent_tasks_data['cached_data'] = cached_data

            persistent_tasks.add("dNG.pas.vfs.CachedObject.storeVfsUrl.{0}".format(vfs_url),
                                 PersistentLrtHook("dNG.pas.vfs.CachedObject.storeVfsUrl",
                                                   **persistent_tasks_data
                                                  ),
                                 1
                                )
        #
    #

    @Connection.wrap_callable
    @staticmethod
    def cache_vfs_url_if_changed(vfs_url, cached_data = None):
        """
Stores a given VFS URL in cache using the given cache data. It will be
scheduled as a background task.

:param vfs_url: VFS URL
:param cached_data: Cache data for the VFS URL

:since: v0.2.00
        """

        cached_file = None
        is_cached_vfs_url_up_to_date = False
        vfs_object = None

        try:
            vfs_object = Implementation.load_vfs_url(vfs_url, True)

            try:
                cached_file = File.load_resource(vfs_url)

                vfs_object_time_updated = (vfs_object.get_time_updated()
                                           if (vfs_object.is_supported("time_updated")) else
                                           None
                                          )

                is_cached_vfs_url_up_to_date = (cached_file.is_valid()
                                                and (vfs_object_time_updated is None
                                                     or cached_file.is_up_to_date(vfs_object_time_updated)
                                                    )
                                               )
            except NothingMatchedException: pass
        finally:
            if (cached_file is not None): cached_file.close()
            if (vfs_object is not None): vfs_object.close()
        #

        if (not is_cached_vfs_url_up_to_date):
            CachedImplementation.cache_vfs_url(vfs_url, cached_data)
        #
    #

    @staticmethod
    def load_vfs_url(vfs_url, readonly = False):
        """
Returns the initialized object instance for the given VFS URL.

:param vfs_url: VFS URL
:param readonly: Open object in readonly mode

:return: (object) VFS object instance
:since:  v0.2.00
        """

        if (readonly):
            try:
                cached_file = File.load_resource(vfs_url)
                vfs_url = cached_file.get_vfs_url()
            except NothingMatchedException: pass
        #

        return Implementation.load_vfs_url(vfs_url, readonly)
    #

    @staticmethod
    def store_cached_vfs_url(vfs_url, cached_data = None):
        """
Stores a given VFS URL in cache using the given cache data.

:param vfs_url: VFS URL
:param cached_data: Cache data for the VFS URL

:since: v0.2.00
        """

        if (cached_data is None): cached_data = { }

        vfs_object = Implementation.load_vfs_url(vfs_url, True)

        try:
            if (not vfs_object.is_file()): raise IOException("VFS URL given is not a cacheable file")

            cached_file = File()
            vfs_object.copy_data(cached_file)
        finally: vfs_object.close()

        cached_data['resource'] = vfs_url

        cached_file.set_data_attributes(**cached_data)
        cached_file.save()
    #
#
