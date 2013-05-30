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

import inspect
import unittest
import re
import os
import sumpf

from .process import MissingLibProcess


@unittest.skipUnless(sumpf.config.get("run_long_tests"), "Long tests are skipped")
@unittest.skipIf(sumpf.config.get("unload_numpy"), "Testing modules that require the full featured numpy are skipped")
class TestMissingLibs(unittest.TestCase):
	"""
	Tests if SuMPF still works, if the external libs are missing and if it limits
	its functionality accordingly, by hiding classes that rely on these libs.
	"""
	def test_signal_formats(self):
		"""
		Tests if the correct signal formats are unavailable if audiolab is missing.
		"""
		def function(sumpf_module):
			formats = ["AIFF_FLOAT", "AIFF_INT", "FLAC", "WAV_FLOAT", "WAV_INT"]
			result = {}
			for f in formats:
				result[f] = hasattr(sumpf_module.modules.SignalFile, f)
			return result
		process = MissingLibProcess(libnames=["scikits"], function=function)
		process.start()
		process.join()
		result = process.namespace.result
		not_unavailable = process.namespace.not_unavailable
		if "scikits" in not_unavailable:
			self.fail("scikits could not be made unavailable")
		elif True in list(result.values()):
			format = list(result.keys())[list(result.values()).index(True)]
			self.fail(format + " is still available, when scikits is not available")

	def test_missing_libs(self):
		"""
		Tests that SuMPF does not crash if libs are missing
		and that classes which use missing libs will not show up in the module.
		"""
		libs = {}
		libs["jack"] = None
		libs["matplotlib"] = None
		libs["numpy"] = "sumpf.helper.numpydummy"
		libs["scikits"] = None	# both scikits.audiolab and scikits.samplerate
		libs["wx"] = None
		def function(sumpf_module, classnames):
			for r in sumpf_module.helper.walk_module(sumpf_module):
				for c in r[2]:
					for s in inspect.getmro(c):
						if s.__name__ in classnames:
							return s.__name__
			return None
		for l in libs:
			c = self.__GetLibClasses(l, libs[l])
			process = MissingLibProcess(libnames=[l], function=function, classnames=c)
			process.start()
			process.join()
			result = process.namespace.result
			not_unavailable = process.namespace.not_unavailable
			if result is not None:
				if not_unavailable == []:
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

