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

class ChannelDataAlgebra(object):
	"""
	Abstract base class for calculations with two ChannelData instances.
	"""
	def __init__(self, dataset1, dataset2):
		"""
		All parameters should be made optional by derived classes.
		@param dataset1: the first data set
		@param dataset2: the second data set
		"""
		self.__dataset1 = dataset1
		self.__dataset2 = dataset2

	def _SetDataset1(self, dataset):
		"""
		Sets the first data set.
		For calculations where the order is important, this data set will be used
		as the first one, e.g.:
			Subtraction: result = dataset1 - dataset2
			Division: result = dataset1 / dataset2
		@param dataset1: the first data set
		"""
		self.__dataset1 = dataset

	def _SetDataset2(self, dataset):
		"""
		Sets the second data set.
		For calculations where the order is important, this data set will be used
		as the second one, e.g.:
			Subtraction: result = dataset1 - dataset2
			Division: result = dataset1 / dataset2
		@param dataset1: the first data set
		"""
		self.__dataset2 = dataset

	def _GetDataset1(self):
		"""
		Returns the first data set for derived classes.
		@retval : the first data set
		"""
		return self.__dataset1

	def _GetDataset2(self):
		"""
		Returns the second data set for derived classes.
		@retval : the second data set
		"""
		return self.__dataset2

	def _GetChannels(self):
		"""
		Performs the calculation and returns the channels of the resulting data set.
		@retval : a tuple of channels which themselves are a tuple of samples
		"""
		channels1 = self._GetDataset1().GetChannels()
		channels2 = self._GetDataset2().GetChannels()
		maxc = 0
		if self._GetDataset1().IsEmpty():
			maxc = len(channels2)
			channels1 = ((0.0,) * len(self._GetDataset2()),) * maxc
		elif self._GetDataset2().IsEmpty():
			maxc = len(channels1)
			channels2 = ((0.0,) * len(self._GetDataset1()),) * maxc
		else:
			maxc = min(len(channels1), len(channels2))
		channels = []
		for c in range(maxc):
			channels.append(self._Calculate(channels1[c], channels2[c]))
		return channels

	def _GetLabels(self):
		result = []
		maxc = 0
		if self._GetDataset1().IsEmpty():
			maxc = len(self._GetDataset2().GetChannels())
		elif self._GetDataset2().IsEmpty():
			maxc = len(self._GetDataset1().GetChannels())
		else:
			maxc = min(len(self._GetDataset1().GetChannels()), len(self._GetDataset2().GetChannels()))
		for c in range(maxc):
			result.append(self._GetLabel() + " " + str(c + 1))
		return result

#	These methods have to be overridden by derived classes.
#	Those classes may inherit it from a class which is not a subclass of
#	ChannelDataAlgebra to avoid multiple inheritance of the same base class.
#	For proper functionality these methods may not be implemented in this base
#	class.
#
#	def _Calculate(self, a, b):
#		"""
#		This method shall perform the calculation.
#		@param a,b: two tuples of float samples
#		@retval : a tuple of float samples that is the result of the calculation
#		"""
#		raise NotImplementedError("This method should have been overridden in a derived class")
#
#	def _GetLabel(self):
#		"""
#		@retval : a string label prefix. An index number will be appended to this prefix to form a label for each channel
#		"""
#		raise NotImplementedError("This method should have been overridden in a derived class")

