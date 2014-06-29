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

import os
import numpy
import sumpf
from .coefficients import LaguerreHermiteCoefficients


class LaguerreHermiteCoefficientsFile(object):
	"""
	This class can save an instance of LaguerreHermiteCoefficients to a file. It
	can also load such a file and create an instance from that.
	The coefficients are stored in NumPy's npz format.
	"""
	def __init__(self, filename=None, coefficients=LaguerreHermiteCoefficients()):
		"""
		If the filename is not None, the file exists and the initial data set is
		empty, the data set will be automatically be loaded from the file.
		If the filename is not None and the initial data set is not empty, the
		initial data set will be saved to the file, even if the file exists
		already.
		@param filename: None or a string value of a path and filename with the file ending
		@param coefficients: the LaguerreHermiteCoefficients instance that shall be stored in the file
		"""
		self.__coefficients = coefficients
		if filename is None:
			self.__filename = None
		else:
			self.SetFilename(filename)

	@sumpf.Output(LaguerreHermiteCoefficients)
	def GetCoefficients(self):
		"""
		Loads a set of  LaguerreHermiteCoefficients from the file and returns it.
		@retval : the loaded LaguerreHermiteCoefficients
		"""
		self.__Load()
		return self.__coefficients

	@sumpf.Input(LaguerreHermiteCoefficients, "GetCoefficients")
	def SetCoefficients(self, coefficients):
		"""
		Saves the set of  LaguerreHermiteCoefficients to the file.
		@param coefficients: the instance of LaguerreHermiteCoefficients that shall be saved
		"""
		self.__coefficients = coefficients
		self.__Save()

	@sumpf.Input(str, "GetCoefficients")
	def SetFilename(self, filename):
		"""
		Sets the filename under which the data shall be saved or from which the
		data shall be loaded.
		If the file specified by the filename and the format exists and the
		current data set is empty, the file will be loaded. Otherwise the
		current data will be saved to that file.
		@param filename: a string value of a path and filename with the file ending
		"""
		filename = sumpf.helper.normalize_path(filename)
		self.__filename = filename
		if os.path.exists(self.__filename) and self.__coefficients.IsEmpty():
			self.__Load()
		else:
			self.__Save()

	def __Load(self):
		"""
		Causes the current coefficients to be loaded from the file, if the file exists.
		"""
		if self.__filename is not None:
			if os.path.exists(self.__filename):
				data = numpy.load(self.__filename)
				self.__coefficients = LaguerreHermiteCoefficients(weighting_coefficients=data["weighting_coefficients"],
				                                                  scaling_factors=data["scaling_factors"],
				                                                  generalization_orders=data["generalization_orders"],
				                                                  excitation_variances=data["excitation_variances"])

	def __Save(self):
		"""
		Causes the current coefficients to be saved to the file, if a filename has
		been specified.
		"""
		if self.__filename is not None:
			numpy.savez_compressed(self.__filename,
			                       weighting_coefficients=self.__coefficients.GetWeightingCoefficients(),
			                       scaling_factors=self.__coefficients.GetScalingFactors(),
			                       generalization_orders=self.__coefficients.GetGeneralizationOrders(),
			                       excitation_variances=self.__coefficients.GetExcitationVariances())

