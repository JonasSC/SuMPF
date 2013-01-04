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
		fails = []
		short_is_enough = ["AverageSpectrums",
		                   "RelabelSignal", "RelabelSpectrum",
		                   "DifferentiateSignal", "LogarithmSignal"]
		for p, m, c, f, v in sumpf.helper.walk_module(sumpf):
			for cls in c:
				if cls.__doc__ is None:
					fails.append(cls.__name__)
				else:
					doclines = len(cls.__doc__.strip().split("\n"))
					if cls.__name__ in short_is_enough:
						if doclines < 1:
							fails.append(cls.__name__)
					elif doclines < 3:
						fails.append(cls.__name__)
		if fails != []:
			self.fail("The following " + str(len(fails)) + " classes are not sufficiently documented: " + str(fails))

