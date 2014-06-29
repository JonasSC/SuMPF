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

from __future__ import print_function

import copy
import time
import sumpf
from .coefficients import LaguerreHermiteCoefficients
from .helper import get_permutations, normalize_permutation, get_powers_of_laguerre_representations
from .laguerre import get_scaling_factors_and_generalization_orders, generate_laguerre_functions, convolve_with_laguerre_functions
from .hermite import calculate_combination, calculate_weighting_coefficient


class LaguerreHermiteIdentification(object):
	"""
	This
	class
	is not
	properly
	documented
	"""
	def __init__(self, excitation=None, response=None, orders=(1,), generalized_laguerre=False, impulse_response=None, known_coefficients=None):
		self.__excitation = excitation
		if self.__excitation is None:
			self.__excitation = sumpf.Signal(channels=((1.0, 0.0),))
		self.__response = response
		if self.__response is None:
			self.__response = sumpf.Signal(channels=((1.0, 0.0),))
		self.__orders = orders
		self.__generalzed_laguerre = generalized_laguerre
		self.__impulse_response = impulse_response
		self.__known_coefficients = known_coefficients

	@sumpf.Output(LaguerreHermiteCoefficients)
	def GetCoefficients(self):
		# check for incompatible input Signals
		if len(self.__excitation) != len(self.__response):
			raise ValueError("The given excitation has a different length than the given response")
		elif self.__excitation.GetSamplingRate() != self.__response.GetSamplingRate():
			raise ValueError("The given excitation has a different sampling rate than the given response")
		elif len(self.__excitation.GetChannels()) != len(self.__response.GetChannels()):
			if len(self.__excitation.GetChannels()) == 1:
				self.__excitation = sumpf.modules.CopySignalChannels(input=self.__excitation, channelcount=len(self.__response.GetChannels())).GetOutput()
			else:
				raise ValueError("The given excitation has a different number of channels than the given response")
		if self.__impulse_response is not None:
			if len(self.__impulse_response) != len(self.__response):
				raise ValueError("The given impulse response has a different length than the given response")
			elif self.__impulse_response.GetSamplingRate() != self.__response.GetSamplingRate():
				raise ValueError("The given impulse response has a different sampling rate than the given response")
			elif len(self.__impulse_response.GetChannels()) != len(self.__response.GetChannels()):
				raise ValueError("The given impulse response has a different number of channels than the given response")
		# calculate some necessary values
		excitation_variances = sumpf.modules.SignalVariance(signal=self.__excitation).GetVariance()
		scaling_factors, generalization_orders = get_scaling_factors_and_generalization_orders(excitation=self.__excitation,
		                                                                                       response=self.__response,
		                                                                                       generalized_laguerre=self.__generalzed_laguerre,
		                                                                                       impulse_response=self.__impulse_response)
		# check the known coefficients
		known_coefficients = self.__known_coefficients
		if known_coefficients is None:
			known_coefficients = LaguerreHermiteCoefficients(weighting_coefficients=({},),
			                                                 scaling_factors=scaling_factors,
			                                                 generalization_orders=generalization_orders,
			                                                 excitation_variances=excitation_variances)
		elif known_coefficients.GetScalingFactors() != scaling_factors:
			raise ValueError("The given known coefficients have different scaling factors than those for current system: %s != %s" % (str(known_coefficients.GetScalingFactors()), str(scaling_factors)))
		elif known_coefficients.GetGeneralizationOrders() != generalization_orders:
			raise ValueError("The given known coefficients have different orders of generalization than those for current system: %s != %s" % (str(known_coefficients.GetGeneralizationOrders()), str(generalization_orders)))
		elif known_coefficients.GetExcitationVariances() != excitation_variances:
			raise ValueError("The given known coefficients have different excitation variances than those for current system: %s != %s" % (str(known_coefficients.GetExcitationVariances()), str(excitation_variances)))
		elif known_coefficients.GetNumberOfChannels() != len(self.__excitation.GetChannels()):
			raise ValueError("The given known coefficients have a different number of channels than the current system: %i != %i" % (known_coefficients.GetNumberOfChannels(), len(self.__excitation.GetChannels())))
		# calculate the coefficients for each channel
		weighting_coefficients = []
		for c in range(len(self.__excitation.GetChannels())):
			print(time.ctime(), "calculating the weighting coefficients")
			single_excitation = sumpf.modules.SplitSignal(data=self.__excitation, channels=[c]).GetOutput()
			single_response = sumpf.modules.SplitSignal(data=self.__response, channels=[c]).GetOutput()
			single_weighting_coefficients = copy.copy(known_coefficients.GetWeightingCoefficients()[c])
			for nonlinear_order in range(1, len(self.__orders) + 1):
				max_linear_order = self.__orders[nonlinear_order - 1]
				if max_linear_order == 0:
					continue
				resampled_response = sumpf.modules.ResampleSignal(signal=single_response,
				                                                  samplingrate=single_response.GetSamplingRate() * nonlinear_order * 2.0,
				                                                  algorithm=sumpf.modules.ResampleSignal.SPECTRUM).GetOutput()
				# calculate the convolution of the excitation Signal and the Laguerre functions
				laguerre_functions = generate_laguerre_functions(scaling_factor=scaling_factors[c],
				                                                 generalization_order=generalization_orders[c],
				                                                 order=max_linear_order,
				                                                 samplingrate=single_excitation.GetSamplingRate() * nonlinear_order,
				                                                 length=len(single_excitation) * nonlinear_order)
				laguerred_excitation = convolve_with_laguerre_functions(signal=single_excitation, laguerre_functions=laguerre_functions)
				powers = get_powers_of_laguerre_representations(laguerred_input=laguerred_excitation, order=nonlinear_order)
				# calculate the coefficients
				print(time.ctime(), "  calculating the weighting coefficients for order %i:" % nonlinear_order, end=" ")
				for permutation in get_permutations(nonlinear_order=nonlinear_order, max_linear_order=max_linear_order):
					if min(permutation) == max(permutation):
						print(permutation[0], end=" ")
					if permutation not in single_weighting_coefficients:
						normalized_permutation = normalize_permutation(permutation)
						combination = calculate_combination(normalized_permutation=normalized_permutation,
						                                    excitation_powers=powers,
						                                    excitation_variance=excitation_variances[c])
						w = calculate_weighting_coefficient(combination=combination,
						                                    resampled_response=resampled_response,
						                                    nonlinear_order=nonlinear_order,
						                                    normalized_permutation=normalized_permutation,
						                                    excitation_variance=excitation_variances[c])
						single_weighting_coefficients[permutation] = w
				print()
				# make sure, the memory is freed
				del resampled_response
				del laguerre_functions
				del laguerred_excitation
				del powers
				sumpf.collect_garbage()
			weighting_coefficients.append(single_weighting_coefficients)
		return LaguerreHermiteCoefficients(weighting_coefficients=weighting_coefficients,
		                                   scaling_factors=scaling_factors,
		                                   generalization_orders=generalization_orders,
		                                   excitation_variances=excitation_variances)

	@sumpf.Input(sumpf.Signal, "GetCoefficients")
	def SetExcitation(self, excitation):
		self.__excitation = excitation

	@sumpf.Input(sumpf.Signal, "GetCoefficients")
	def SetResponse(self, response):
		self.__response = response

	@sumpf.Input(tuple, "GetCoefficients")
	def SetOrders(self, orders):
		self.__orders = orders

	@sumpf.Input(bool, "GetCoefficients")
	def SetGeneralizedLaguerre(self, generalized_laguerre):
		self.__generalzed_laguerre = generalized_laguerre

	@sumpf.Input(sumpf.Signal, "GetCoefficients")
	def SetImpulseResponse(self, impulse_response):
		self.__impulse_response = impulse_response

	@sumpf.Input(LaguerreHermiteCoefficients, "GetCoefficients")
	def SetKnownCoefficients(self, coefficients):
		self.__known_coefficients = coefficients

