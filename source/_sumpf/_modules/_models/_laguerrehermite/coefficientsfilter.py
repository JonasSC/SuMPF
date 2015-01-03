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

import sumpf
from .coefficients import LaguerreHermiteCoefficients


class LaguerreHermiteCoefficientsFilter(object):
	"""
	This
	class
	is not
	properly
	documented
	"""
	def __init__(self, coefficients=LaguerreHermiteCoefficients(), channels=None, orders=None, number=None, weight_with_variance=True):
		self.__coefficients = coefficients
		self.__channels = channels
		self.__orders = orders
		self.__number = number
		self.__weight_with_variance = weight_with_variance

	@sumpf.Output(LaguerreHermiteCoefficients)
	def GetOutput(self):
		filtered_coefficients = []
		filtered_scaling_factors = []
		filtered_generalization_orders = []
		filtered_exciation_variances = []
		# filter by channels
		channels = self.__channels
		if channels is None:
			channels = tuple(range(self.__coefficients.GetNumberOfChannels()))
		for c in channels:
			all_coefficients = self.__coefficients.GetWeightingCoefficients()[c]
			filtered_scaling_factors.append(self.__coefficients.GetScalingFactors()[c])
			filtered_generalization_orders.append(self.__coefficients.GetGeneralizationOrders()[c])
			filtered_exciation_variances.append(self.__coefficients.GetExcitationVariances()[c])
			# filter by orders
			orders = self.__orders
			order_filtered = all_coefficients
			if orders is not None:
				order_filtered = {}
				for key in all_coefficients:
					if len(key) < len(orders) + 1 and max(key) < orders[len(key) - 1]:
						order_filtered[key] = all_coefficients[key]
			# filter by number of coefficients
			number_filtered = order_filtered
			if self.__number is not None and self.__number < len(order_filtered):
				number_filtered = {}
				key_function = lambda key: order_filtered[key]
				if self.__weight_with_variance:
					variance = self.__coefficients.GetExcitationVariances()[c]
					key_function = lambda key: order_filtered[key] * (variance ** len(key))
				for k in sorted(order_filtered, key=key_function)[-self.__number:]:
					number_filtered[k] = order_filtered[k]
			filtered_coefficients.append(number_filtered)
		return LaguerreHermiteCoefficients(weighting_coefficients=filtered_coefficients,
		                                   scaling_factors=filtered_scaling_factors,
		                                   generalization_orders=filtered_generalization_orders,
		                                   excitation_variances=filtered_exciation_variances)

	@sumpf.Input(LaguerreHermiteCoefficients, "GetOutput")
	def SetInput(self, coefficients):
		self.__coefficients = coefficients

	@sumpf.Input(tuple, "GetOutput")
	def SetChannels(self, channels):
		self.__channels = channels

	@sumpf.Input(tuple, "GetOutput")
	def SetOrders(self, orders):
		self.__orders = orders

	@sumpf.Input(int, "GetOutput")
	def SetNumber(self, number):
		self.__number = number

	@sumpf.Input(bool, "GetOutput")
	def SetWeightWithVariance(self, weight_with_variance):
		self.__weight_with_variance = weight_with_variance

