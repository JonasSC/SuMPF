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

import unittest
import re
import os
import sumpf
import _common as common

from .process import MissingLibProcess


@unittest.skipUnless(sumpf.config.get("run_long_tests"), "Long tests are skipped")
@unittest.skipUnless(common.lib_available("numpy"), "These tests require the library 'numpy' to be available.")
class TestMissingLibs(unittest.TestCase):
    """
    Tests if SuMPF still works, if the external libs are missing and if it limits
    its functionality accordingly, by hiding classes that rely on these libs.
    """
    def test_signal_formats(self):
        """
        Tests if the correct signal formats are unavailable when audiolab and
        oct2py are missing.
        """
        process = MissingLibProcess(libnames=["soundfile", "scikits", "oct2py"],
                                    function=MissingLibProcess.FILE_FORMATS,
                                    formats=["AIFF_FLOAT", "AIFF_INT", "FLAC", "WAV_DOUBLE", "WAV_FLOAT", "WAV_INT", "ITA_AUDIO", "MATLAB"],
                                    data_type="Signal")
        process.start()
        process.join()
        result = process.namespace.result
        not_unavailable = process.namespace.not_unavailable
        if "soundfile" in not_unavailable:
            self.fail("PySoundFile could not be made unavailable")
        elif "scikits" in not_unavailable:
            self.fail("scikits could not be made unavailable")
        elif "oct2py" in not_unavailable:
            self.fail("oct2py could not be made unavailable")
        elif True in list(result.values()):
            format_name = list(result.keys())[list(result.values()).index(True)]
            self.fail(format_name + " is still available, when PySoundFile, scikits and oct2py are not available")

    def test_spectrum_formats(self):
        """
        Tests if the correct spectrum formats are unavailable when oct2py is missing.
        """
        process = MissingLibProcess(libnames=["oct2py"],
                                    function=MissingLibProcess.FILE_FORMATS,
                                    formats=["ITA_AUDIO", "MATLAB"],
                                    data_type="Spectrum")
        process.start()
        process.join()
        result = process.namespace.result
        not_unavailable = process.namespace.not_unavailable
        if "oct2py" in not_unavailable:
            self.fail("oct2py could not be made unavailable")
        elif True in list(result.values()):
            format_name = list(result.keys())[list(result.values()).index(True)]
            self.fail(format_name + " is still available, when oct2py is not available")

    def test_missing_libs(self):
        """
        Tests that SuMPF does not crash if libs are missing
        and that classes which use missing libs will not show up in the module.
        """
        libs = {}
        libs["jack"] = None
        libs["matplotlib"] = None
        libs["numpy"] = "sumpf.helper.numpydummy"
        libs["oct2py"] = None
        libs["scikits"] = None  # both scikits.audiolab and scikits.samplerate
        libs["soundfile"] = None
        libs["wx"] = None
        exceptions = [("ResampleSignal", "scikits")]
        for l in libs:
            c = self.__GetLibClasses(l, libs[l])
            process = MissingLibProcess(libnames=[l], function=MissingLibProcess.MISSING_LIBS, classnames=c)
            process.start()
            process.join()
            result = process.namespace.result
            not_unavailable = process.namespace.not_unavailable
            if result is not None:
                if not_unavailable == []:
                    if (result, l) not in exceptions:
                        self.fail(result + " is still available, when " + l + " is not available")
                else:
                    print("%s could not be made unavailable for testing." % not_unavailable[0])
                    print("  These attributes should have been unavailable: %s" % str(result))

    def __GetLibClasses(self, libname, replacement=None):
        """
        Returns the classes that use the lib
        """
        regex_import = re.compile("^\s*import\s+" + libname + "\W*")
        regex_from = re.compile("^\s*from\s+" + libname + "\s+import\s+\w+")
        regex_class = re.compile("^\s*class\s+\w+\s*\(\s*[\w\.]+\s*\)\s*\:")
        regex_replace = None
        if replacement is not None:
            regex_replace = re.compile(replacement)
        result = []
        for root, dirs, files in os.walk(sumpf.config.get("source_dir")):
            for filename in files:
                if filename.endswith(".py"):
                    file = os.path.join(root, filename)
                    f = open(file, 'r')
                    lines = f.readlines()
                    f.close()
                    classes = []
                    lib_used = False
                    replacement_given = False
                    for line in lines:
                        if regex_import.match(line) or regex_from.match(line):
                            lib_used = True
                        if replacement is not None:
                            if regex_replace.search(line):
                                replacement_given = True
                        if regex_class.match(line):
                            classname = line.strip().rstrip(":").strip().split("class")[1].split("(")[0].strip()
                            classes.append(classname)
                    if lib_used and not replacement_given:
                        for c in classes:
                            result.append(c)
        return result

