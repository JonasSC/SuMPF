# SuMPF - Sound using a Monkeyforest-like processing framework
# Copyright (C) 2012-2014 Jonas Schulte-Coerne
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

import sumpf

import unittest

class TestAttributes(unittest.TestCase):
	"""
	Tests if certain attributes of SuMPF or its classes are set correctly.
	"""
	def test_licence_variable(self):
		"""
		Tests if SuMPF has the license-attribute.
		"""
		self.assertTrue(hasattr(sumpf, "license"))
		self.assertEqual(sumpf.license.split("\n")[0], "					GNU GENERAL PUBLIC LICENSE")
		self.assertEqual(sumpf.license.split("\n")[1], "					   Version 3, 29 June 2007")
		self.assertEqual(len(sumpf.license), 34798)

	def test_class_documentation(self):
		"""
		Tests if every class is sufficiently documented
		"""
		def format_name(classpath, classname):
			return ".".join([m.__name__ for m in classpath] + [classname])
		fails = []
		short_is_enough = ["AverageSpectrums", "ConjugateSpectrum",
		                   "RelabelSignal", "RelabelSpectrum",
		                   "LogarithmSignal",
		                   "SignalMean", "SpectrumMean",
		                   "SignalVariance", "SpectrumVariance"]
		for p, m, c, f, v in sumpf.helper.walk_module(sumpf):
			for cls in c:
				if cls.__doc__ is None:
					fails.append(format_name(classpath=p, classname=cls.__name__))
				else:
					doclines = len(cls.__doc__.strip().split("\n"))
					if cls.__name__ in short_is_enough:
						if doclines < 1:
							fails.append(format_name(classpath=p, classname=cls.__name__))
						elif doclines >= 3:
							self.fail("The class " + cls.__name__ + " is properly documented and should not be in the short_is_enough list.")
					elif doclines < 3:
						fails.append(format_name(classpath=p, classname=cls.__name__))
		if fails != []:
			self.fail("The following " + str(len(fails)) + " classes are not sufficiently documented: " + str(fails))

