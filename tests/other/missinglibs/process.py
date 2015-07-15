# SuMPF - Sound using a Monkeyforest-like processing framework
# Copyright (C) 2012-2015 Jonas Schulte-Coerne
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

import inspect
import multiprocessing
from _common import unload_lib, unload_sumpf, make_lib_unavailable


class MissingLibProcess(multiprocessing.Process):
    FILE_FORMATS = 0
    MISSING_LIBS = 1

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
        unload_sumpf()
        for l in self.__libnames:
            if not make_lib_unavailable(l):
                nu = self.namespace.not_unavailable
                nu.append(l)
                self.namespace.not_unavailable = nu
            unload_lib(l)
        import sumpf
        function = None
        if self.__function == MissingLibProcess.FILE_FORMATS:
            function = self.__CheckFileFormats
        elif self.__function == MissingLibProcess.MISSING_LIBS:
            function = self.__CheckMissingLibs
        self.namespace.result = function(sumpf, **self.__kwargs)

    def __CheckFileFormats(self, sumpf_module, formats, data_type):
        file_class = None
        if data_type == "Signal":
            file_class = sumpf_module.modules.SignalFile
        elif data_type == "Spectrum":
            file_class = sumpf_module.modules.SpectrumFile
        result = {}
        for f in formats:
            result[f] = hasattr(file_class, f)
        return result

    def __CheckMissingLibs(self, sumpf_module, classnames):
        for r in sumpf_module.helper.walk_module(sumpf_module):
            for c in r[2]:
                for s in inspect.getmro(c):
                    if s.__name__ in classnames:
                        return s.__name__
        return None

