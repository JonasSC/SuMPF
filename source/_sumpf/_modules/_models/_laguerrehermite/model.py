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

import time
import sumpf
from .coefficients import LaguerreHermiteCoefficients
from .helper import normalize_permutation, get_powers_of_laguerre_representations
from .laguerre import generate_laguerre_functions, convolve_with_laguerre_functions
from .hermite import calculate_combination


class LaguerreHermiteModel(object):
	"""
	This
	class
	is not
	properly
	documented
	"""
	RAISE_ERROR = 0
	COPY = 1
	CROP = 2

	def __init__(self, coefficients=LaguerreHermiteCoefficients(), input_signal=None, on_channel_conflict=COPY):
		self.__coefficients = coefficients
		self.__input_signal = input_signal
		if self.__input_signal is None:
			self.__input_signal = sumpf.Signal()
		self.__on_channel_conflict = on_channel_conflict

	@sumpf.Output(sumpf.Signal)
	def GetOutput(self):
		number_of_channels = self.__coefficients.GetNumberOfChannels()
		if number_of_channels != len(self.__input_signal.GetChannels()):
			if self.__on_channel_conflict == LaguerreHermiteModel.RAISE_ERROR:
				raise ValueError("Expected an input Signal with %i channels, but the given Signal has %i" % (number_of_channels, len(self.__input_signal.GetChannels())))
			elif self.__on_channel_conflict == LaguerreHermiteModel.COPY:
				number_of_channels = max(number_of_channels, len(self.__input_signal.GetChannels()))
				self.__input_signal = sumpf.modules.CopySignalChannels(input=self.__input_signal, channelcount=number_of_channels).GetOutput()
			elif self.__on_channel_conflict == LaguerreHermiteModel.CROP:
				number_of_channels = min(number_of_channels, len(self.__input_signal.GetChannels()))
			else:
				raise ValueError("Unknown flag for resolving a channel count conflict")
		# synthesize the output Signal
		orders = self.__coefficients.GetOrders()
		merger = sumpf.modules.MergeSignals()
		for c in range(number_of_channels):
			print(time.ctime(), "synthesizing the output signal")
			# select the correct channel
			coefficients_index = c % self.__coefficients.GetNumberOfChannels()
			weighting_coefficients = self.__coefficients.GetWeightingCoefficients()[coefficients_index]
			input_signal = sumpf.modules.SplitSignal(data=self.__input_signal, channels=[c]).GetOutput()
			dc_offset = 0.0
			if () in weighting_coefficients:
				dc_offset = weighting_coefficients[()]
			response = sumpf.modules.ConstantSignalGenerator(value=dc_offset, samplingrate=input_signal.GetSamplingRate(), length=len(input_signal)).GetSignal()
			for nonlinear_order in range(1, len(orders[coefficients_index]) + 1):
				max_linear_order = orders[coefficients_index][nonlinear_order - 1]
				# prepare the Laguerre functions
				laguerre_functions = generate_laguerre_functions(scaling_factor=self.__coefficients.GetScalingFactors()[coefficients_index],
				                                                 generalization_order=self.__coefficients.GetGeneralizationOrders()[coefficients_index],
				                                                 order=max_linear_order,
				                                                 samplingrate=input_signal.GetSamplingRate() * nonlinear_order,
				                                                 length=len(input_signal) * nonlinear_order)
				laguerred_input = convolve_with_laguerre_functions(signal=input_signal, laguerre_functions=laguerre_functions)
				powers = get_powers_of_laguerre_representations(laguerred_input=laguerred_input, order=nonlinear_order)
				# add up the weighted functions
				print(time.ctime(), "  synthesizing permutations of order %i" % nonlinear_order)
				singleorder_response = sumpf.modules.SilenceGenerator(samplingrate=input_signal.GetSamplingRate() * nonlinear_order,
				                                                      length=len(input_signal) * nonlinear_order).GetSignal()
				for permutation in weighting_coefficients:
					if len(permutation) == nonlinear_order:
						normalized_permutation = normalize_permutation(permutation)
						combination = calculate_combination(normalized_permutation=normalized_permutation,
						                                    excitation_powers=powers,
						                                    excitation_variance=self.__coefficients.GetExcitationVariances()[coefficients_index])
						weighted = combination * weighting_coefficients[permutation]
						singleorder_response = singleorder_response + weighted
				resampled = sumpf.modules.ResampleSignal(signal=singleorder_response,
				                                         samplingrate=input_signal.GetSamplingRate(),
				                                         algorithm=sumpf.modules.ResampleSignal.SPECTRUM).GetOutput()
				response = response + resampled
				# make sure, the memory is freed
				del laguerre_functions
				del laguerred_input
				del powers
				del singleorder_response
				del resampled
				sumpf.collect_garbage()
			merger.AddInput(response)
		# relabel and return the output Signal
		labels = []
		for i in range(1, number_of_channels + 1):
			labels.append("Synthesized %i" % i)
		return sumpf.modules.RelabelSignal(input=merger.GetOutput(), labels=labels).GetOutput()

	@sumpf.Input(LaguerreHermiteCoefficients, "GetOutput")
	def SetCoefficients(self, coefficients):
		self.__coefficients = coefficients

	@sumpf.Input(sumpf.Signal, "GetOutput")
	def SetInput(self, signal):
		self.__input_signal = signal

	@sumpf.Input(int, "GetOutput")
	def SetChannelConflictResolution(self, on_channel_conflict):
		if on_channel_conflict in [LaguerreHermiteModel.RAISE_ERROR, LaguerreHermiteModel.COPY, LaguerreHermiteModel.CROP]:
			self.__on_channel_conflict = on_channel_conflict
		else:
			raise ValueError("Unknown flag for resolving a channel count conflict")

