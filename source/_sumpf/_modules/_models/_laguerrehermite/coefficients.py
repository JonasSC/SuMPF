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

class LaguerreHermiteCoefficients(object):
	"""
	This
	class
	is not
	properly
	documented
	"""
	def __init__(self, weighting_coefficients=({(): 0.0},), scaling_factors=(1.0,), generalization_orders=(0,), excitation_variances=(1.0,)):
		self.__weighting_coefficients = tuple(weighting_coefficients)
		self.__scaling_factors = tuple(scaling_factors)
		self.__generalization_orders = tuple(generalization_orders)
		self.__excitation_variances = tuple(excitation_variances)

	def GetWeightingCoefficients(self):
		return self.__weighting_coefficients

	def GetScalingFactors(self):
		return self.__scaling_factors

	def GetGeneralizationOrders(self):
		return self.__generalization_orders

	def GetExcitationVariances(self):
		return self.__excitation_variances

	def GetNumberOfChannels(self):
		return len(self.__scaling_factors)

	def IsEmpty(self):
		return len(self.__weighting_coefficients) == 0 or \
		       self.__weighting_coefficients[0] == {} or \
		       min(self.__weighting_coefficients[0].values()) == max(self.__weighting_coefficients[0].values()) == 0.0

	def GetOrders(self):
		channels = []
		for c in self.__weighting_coefficients:
			orders = [0]
			for key in c:
				if key != ():
					while len(orders) < len(key):
						orders.append(0)
					orders[len(key) - 1] = max(orders[len(key) - 1], max(key) + 1)
			channels.append(tuple(orders))
		return tuple(channels)

	def __str__(self):
		"""
		This method returns a string that describes the set of coefficients roughly.
		It is called by str() or print().
		@retval : an informal string representation of the set of coefficients
		"""
		module = self.__module__
		channels = len(self.GetWeightingCoefficients())
		number_of_coefficients = len(self.GetWeightingCoefficients()[0])
		nonlinear_order = 0
		for c in self.GetWeightingCoefficients():
			for s in c:
				nonlinear_order = max(nonlinear_order, len(s))
		scaling_factors = "(" + ", ".join(["%.2f" % i for i in self.GetScalingFactors()]) + ")"
		generalization_orders = "(" + ", ".join(["%i" % i for i in self.GetGeneralizationOrders()]) + ")"
		variances = "(" + ", ".join(["%.2f" % i for i in self.GetExcitationVariances()]) + ")"
		address = id(self)
		replacements = (module, channels, number_of_coefficients, nonlinear_order, scaling_factors, generalization_orders, variances, address)
		return "<%s.LaguerreHermiteCoefficients object (channels: %i, number of coefficients: %s, max nonlinear order: %i, scaling factors: %s, generalization orders: %s, excitation variances: %s) at 0x%x>" % replacements

