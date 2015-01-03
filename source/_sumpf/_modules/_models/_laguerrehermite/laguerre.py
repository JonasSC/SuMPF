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

from __future__ import print_function

import time
import sumpf

def get_scaling_factors_and_generalization_orders(excitation, response, generalized_laguerre=False, impulse_response=None):
	# if necessary, get the impulse response of the system
	if impulse_response is None:
		excitation_spectrum = sumpf.modules.FourierTransform(signal=excitation).GetSpectrum()
		response_spectrum = sumpf.modules.FourierTransform(signal=response).GetSpectrum()
		transfer_function = response_spectrum / excitation_spectrum
		impulse_response = sumpf.modules.InverseFourierTransform(spectrum=transfer_function).GetSignal()
	d_impulse_response = sumpf.modules.DifferentiateSignal(signal=impulse_response).GetOutput()
	# calculate different moments of the impulse response
	number_of_channels = len(impulse_response.GetChannels())
	t_single = sumpf.modules.ArbitrarySignalGenerator(function=lambda t: t, samplingrate=impulse_response.GetSamplingRate(), length=len(impulse_response)).GetSignal()
	t = sumpf.modules.CopySignalChannels(input=t_single, channelcount=number_of_channels).GetOutput()
	def ft_1(t):
		if t == 0.0:
			return 2.0 * impulse_response.GetSamplingRate()
		else:
			return 1.0 / t
	t_1_single = sumpf.modules.ArbitrarySignalGenerator(function=ft_1, samplingrate=impulse_response.GetSamplingRate(), length=len(impulse_response)).GetSignal()
	t_1 = sumpf.modules.CopySignalChannels(input=t_1_single, channelcount=number_of_channels).GetOutput()
	s_m_1 = impulse_response * impulse_response * t_1
	s_m0 = impulse_response * impulse_response
	s_m1 = impulse_response * impulse_response * t
	s_m2 = d_impulse_response * d_impulse_response * t
	# calculate the scaling factor and generalization order
	scaling_factors = []
	generalization_orders = []
	for i in range(number_of_channels):
		m_1 = sum(s_m_1.GetChannels()[i])
		m1 = sum(s_m1.GetChannels()[i])
		m2 = sum(s_m2.GetChannels()[i])
		generalization_order = 0
		if generalized_laguerre:
			m0 = sum(s_m0.GetChannels()[i])
			sigma = (m_1 * m2 / abs(m_1 * m1 - m0 ** 2)) ** 0.5
#			sigma = 20000.0
			generalization_order = int(round(sigma * m0 / m_1))
		sigma = ((m_1 * generalization_order ** 2 + 4.0 * m2) / m1) ** 0.5
#		sigma = 20000.0
		scaling_factor = sigma / 2.0
		scaling_factors.append(scaling_factor)
		generalization_orders.append(generalization_order)
	return tuple(scaling_factors), tuple(generalization_orders)

def generate_laguerre_functions(scaling_factor, generalization_order, order, samplingrate, length, normalize=True):
	print(time.ctime(), "  generating the Laguerre functions", end=" ")
	laguerre_merger = sumpf.modules.MergeSignals()
	for o in range(0, order):
		print(o, end=" ")
		function = sumpf.modules.LaguerreFunctionGenerator(order=o, scaling_factor=scaling_factor, generalization_order=generalization_order, samplingrate=samplingrate, length=length).GetSignal()
		laguerre_merger.AddInput(function)
	functions = laguerre_merger.GetOutput()
	if normalize:
		print("normalize")
		functions = functions * (1.0 / samplingrate) ** 0.5
	return functions

def convolve_with_laguerre_functions(signal, laguerre_functions):
	print(time.ctime(), "  convolving the Laguerre functions with the input signal")
	spectrum = sumpf.modules.FourierTransform(signal=signal).GetSpectrum()
	laguerre_spectrum = sumpf.modules.FourierTransform(signal=laguerre_functions).GetSpectrum()
	length = len(laguerre_spectrum)
	channels = []
	for c in spectrum.GetChannels():
		channel = c + ((0.0,) * (length - len(spectrum)))
		channels.append(channel)
	resampled_spectrum = sumpf.Spectrum(channels=tuple(channels), resolution=spectrum.GetResolution(), labels=spectrum.GetLabels())
	copied_spectrum = sumpf.modules.CopySpectrumChannels(input=resampled_spectrum, channelcount=len(laguerre_functions.GetChannels())).GetOutput()
	filtered = copied_spectrum * laguerre_spectrum
	return sumpf.modules.InverseFourierTransform(spectrum=filtered).GetSignal()

