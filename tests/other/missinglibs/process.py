# SuMPF - Sound using a Monkeyforest-like processing framework
# Copyright (C) 2012-2013 Jonas Schulte-Coerne
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import multiprocessing
from _common import unload_lib, unload_sumpf, make_lib_unavailable


class MissingLibProcess(multiprocessing.Process):
	def __init__(self, libnames, function, **kwargs):
		"""
		@param libpath: the path of the lib, that has to be removed
		@param classnames: the class names that may no longer be available, when the lib cannot be imported
		"""
		self.__libnames = libnames
		self.__function = function
		self.__kwargs = kwargs
		self.__manager = multiprocessing.Manager()
		self.namespace = self.__manager.Namespace()
		self.namespace.result = None
		self.namespace.not_unavailable = []
		multiprocessing.Process.__init__(self)

	def run(self):
		for l in self.__libnames:
			if not make_lib_unavailable(l):
				nu = self.namespace.not_unavailable
				nu.append(l)
				self.namespace.not_unavailable = nu
			unload_lib(l)
		unload_sumpf()
		import sumpf
		self.namespace.result = self.__function(sumpf, **self.__kwargs)

