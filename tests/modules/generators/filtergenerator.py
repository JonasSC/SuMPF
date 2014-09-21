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

import unittest
import fractions
import math
import sumpf
import _common as common


class TestFilterGenerator(unittest.TestCase):
	"""
	A TestCase for the FilterGenerator module.
	"""
	def test_passthrough(self):
		"""
		Tests the filter generator for the case that no filters are added. In
		this case, it shall produce a Spectrum with only 1.0 samples.
		"""
		gen = sumpf.modules.FilterGenerator(resolution=20.0, length=10)
		expected_result = ((1.0,) * 10,)
		self.assertEqual(gen.GetSpectrum().GetResolution(), 20.0)			# resolution should have been copied correctly
		self.assertEqual(gen.GetSpectrum().GetChannels(), expected_result)	# all samples should be 1.0
		self.assertEqual(gen.GetSpectrum().GetLabels(), ("Filter",))		# the label of the channel should be as expected

	def test_constant(self):
		"""
		Tests the constant filter.
		"""
		# test a floating point factor
		gen = sumpf.modules.FilterGenerator(filterfunction=sumpf.modules.FilterGenerator.CONSTANT(value=0.7),
		                                    resolution=0.5,
		                                    length=10)
		result = sumpf.Spectrum(channels=((0.7,) * 10,), resolution=0.5, labels=("Filter",))
		self.assertEqual(gen.GetSpectrum(), result)
		# test an integer factor
		gen.SetFilter(sumpf.modules.FilterGenerator.CONSTANT(value=4))
		result = sumpf.Spectrum(channels=((4.0,) * 10,), resolution=0.5, labels=("Filter",))
		# test a complex factor
		gen.SetFilter(sumpf.modules.FilterGenerator.CONSTANT(value=3.4j))
		result = sumpf.Spectrum(channels=((3.4j,) * 10,), resolution=0.5, labels=("Filter",))

	def test_rectangle(self):
		"""
		Tests the rectangle filter.
		"""
		spectrum = sumpf.modules.FilterGenerator(filterfunction=sumpf.modules.FilterGenerator.RECTANGLE(start_frequency=5.0, stop_frequency=7.0),
		                                         resolution=0.1,
		                                         length=100).GetSpectrum()
		self.assertEqual(spectrum.GetChannels()[0][0:50], (0.0,) * 50)
		self.assertEqual(spectrum.GetChannels()[0][50:70], (1.0,) * 20)
		self.assertEqual(spectrum.GetChannels()[0][70:], (0.0,) * 30)

	def test_lowpass_highpass(self):
		"""
		Tests the IIR filters, namely Butterworth-, Bessel- and Chebychev-filters
		for both the lowpass and the highpass application.
		"""
		gen = sumpf.modules.FilterGenerator(resolution=200.0, length=100)
		# lowpasses
		lowpasses = []
		lowpasses.append(sumpf.modules.FilterGenerator.BUTTERWORTH_LOWPASS(frequency=100.0, order=4))
		lowpasses.append(sumpf.modules.FilterGenerator.BESSEL_LOWPASS(frequency=92.0, order=4))
		lowpasses.append(sumpf.modules.FilterGenerator.CHEBYSHEV_LOWPASS(frequency=100.0, order=4, ripple=3.0))
		for l in lowpasses:
			gen.SetFilter(l)
			channel = gen.GetSpectrum().GetMagnitude()[0]
			self.assertAlmostEqual(channel[0], 1.0)						# a lowpass should have a gain of 1 at low frequencies
			self.assertAlmostEqual(channel[-1], 0.0)					# a lowpass should have a gain of 0 at high frequencies
		# highpasses
		highpasses = []
		highpasses.append(sumpf.modules.FilterGenerator.BUTTERWORTH_HIGHPASS(frequency=100.0, order=4))
		highpasses.append(sumpf.modules.FilterGenerator.BESSEL_HIGHPASS(frequency=100.0, order=4))
		highpasses.append(sumpf.modules.FilterGenerator.CHEBYSHEV_HIGHPASS(frequency=100.0, order=4, ripple=3.0))
		for h in highpasses:
			gen.SetFilter(h)
			channel = gen.GetSpectrum().GetMagnitude()[0]
			self.assertAlmostEqual(channel[0], 0.0)						# a highpass should have a gain of 0 at low frequencies
			self.assertAlmostEqual(channel[-1], 1.0, 3)					# a highpass should have a gain of 1 at high frequencies

	def test_bandpass_bandstop(self):
		"""
		Tests the bandpass and bandstop filters.
		"""
		gen = sumpf.modules.FilterGenerator(resolution=10.0, length=100)
		# bandpass
		gen.SetFilter(sumpf.modules.FilterGenerator.BANDPASS(frequency=500, q_factor=5.0))
		channel = gen.GetSpectrum().GetMagnitude()[0]
		self.assertAlmostEqual(channel[50], 1.0)							# gain at resonant frequency should be 1
		self.assertAlmostEqual(channel[45], 1.0 / math.sqrt(2.0), 1)		# gain at lower cutoff frequency should be sqrt(2)
		self.assertAlmostEqual(channel[55], 1.0 / math.sqrt(2.0), 1)		# gain at upper cutoff frequency should be sqrt(2)
		# bandstop
		gen.SetFilter(sumpf.modules.FilterGenerator.BANDSTOP(frequency=500, q_factor=5.0))
		channel = gen.GetSpectrum().GetMagnitude()[0]
		self.assertAlmostEqual(channel[50], 0.0)							# gain at resonant frequency should be almost 0
		self.assertAlmostEqual(channel[45], 1.0 / math.sqrt(2.0), 1)		# gain at lower cutoff frequency should be sqrt(2)
		self.assertAlmostEqual(channel[55], 1.0 / math.sqrt(2.0), 1)		# gain at upper cutoff frequency should be sqrt(2)

	def test_laguerre(self):
		"""
		Tests the generation of the Laguerre functions.
		"""
		# create some Laguerre functions
		gen = sumpf.modules.FilterGenerator(resolution=0.1, length=100)
		gen.SetFilter(sumpf.modules.FilterGenerator.LAGUERRE_FUNCTION(order=0, scaling_factor=1.0))
		laguerre0 = gen.GetSpectrum()
		gen.SetFilter(sumpf.modules.FilterGenerator.LAGUERRE_FUNCTION(order=1, scaling_factor=1.0))
		laguerre1 = gen.GetSpectrum()
		gen.SetFilter(sumpf.modules.FilterGenerator.LAGUERRE_FUNCTION(order=2, scaling_factor=1.0))
		laguerre2 = gen.GetSpectrum()
		m0 = laguerre0.GetMagnitude()[0]
		m1 = laguerre1.GetMagnitude()[0]
		m2 = laguerre2.GetMagnitude()[0]
		p0 = laguerre0.GetContinuousPhase()[0]
		p1 = laguerre1.GetContinuousPhase()[0]
		p2 = laguerre2.GetContinuousPhase()[0]
		# compare the generated functions
		self.assertAlmostEqual(m0[0], 2.0 ** 0.5)
		self.assertAlmostEqual(m1[0], 2.0 ** 0.5)
		self.assertAlmostEqual(m2[0], 2.0 ** 0.5)
		for i in range(1, len(m0)):
			self.assertAlmostEqual(m0[i], m1[i])
			self.assertAlmostEqual(m1[i], m2[i])
			self.assertGreater(p0[i], p1[i])
			self.assertGreater(p1[i], p2[i])

	def test_slopes(self):
		"""
		Tests the filter functions which generate a spectrum that falls with
		rising frequency according to a given slope.
		"""
		res = 20
		gen = sumpf.modules.FilterGenerator(resolution=res, length=int(20000 / res) + 1)
		# pink slope (1/f)
		gen.SetFilter(sumpf.modules.FilterGenerator.PINK_SLOPE(start=5.0 * res))
		channel = gen.GetSpectrum().GetChannels()[0]
		self.assertEqual(channel[0:5], (1.0,) * 5)
		integral1 = 0.0
		for i in range(200 // res, 2000 // res + 1):
			integral1 += channel[i]
		integral2 = 0.0
		for i in range(2000 // res, 20000 // res + 1):
			integral2 += channel[i]
		self.assertLess(abs((integral1 - integral2) / integral2), 0.03)
		# red slope (1/f**2)
		gen.SetFilter(sumpf.modules.FilterGenerator.RED_SLOPE(start=5.0 * res))
		channel = gen.GetSpectrum().GetChannels()[0]
		self.assertEqual(channel[0:5], (1.0,) * 5)
		integral1 = 0.0
		self.assertAlmostEqual(channel[200 // res] / channel[400 // res], 4.0)

	@unittest.skipUnless(common.lib_available("numpy"), "This test requires the library 'numpy' to be available.")
	def test_derivative(self):
		"""
		Tests the derivative filter function.
		"""
		# set up a processing chain to calculate a derivative in the frequency domain.
		properties = sumpf.modules.ChannelDataProperties(signal_length=2 ** 9, samplingrate=11025)
		generator = sumpf.modules.SweepGenerator(start_frequency=1.0, stop_frequency=4000.0)
		sumpf.connect(properties.GetSamplingRate, generator.SetSamplingRate)
		sumpf.connect(properties.GetSignalLength, generator.SetLength)
		fft = sumpf.modules.FourierTransform()
		sumpf.connect(generator.GetSignal, fft.SetSignal)
		filtergenerator = sumpf.modules.FilterGenerator(filterfunction=sumpf.modules.FilterGenerator.DERIVATIVE())
		sumpf.connect(properties.GetResolution, filtergenerator.SetResolution)
		sumpf.connect(properties.GetSpectrumLength, filtergenerator.SetLength)
		multiply = sumpf.modules.MultiplySpectrums()
		sumpf.connect(fft.GetSpectrum, multiply.SetInput1)
		sumpf.connect(filtergenerator.GetSpectrum, multiply.SetInput2)
		ifft = sumpf.modules.InverseFourierTransform()
		sumpf.connect(multiply.GetOutput, ifft.SetSpectrum)
		# compare the result with the helper.differentiate_fft method
		filterderivative = ifft.GetSignal().GetChannels()[0]
		functionderivative = sumpf.helper.differentiate_fft(generator.GetSignal().GetChannels()[0])
		self.assertEqual(len(filterderivative), len(functionderivative))
		for i in range(len(filterderivative)):
			self.assertAlmostEqual(filterderivative[i], functionderivative[i])
		# change the sampling rate and length and test again
		properties.SetSamplingRate(22050)
		properties.SetSignalLength(2 ** 10)
		filterderivative = ifft.GetSignal().GetChannels()[0]
		functionderivative = sumpf.helper.differentiate_fft(generator.GetSignal().GetChannels()[0])
		self.assertEqual(len(filterderivative), len(functionderivative))
		for i in range(len(filterderivative)):
			self.assertAlmostEqual(filterderivative[i], functionderivative[i], 15)

	@unittest.skipUnless(sumpf.config.get("run_long_tests"), "Long tests are skipped")
	def test_weighting(self):
		"""
		Compares the magnitude of the output Spectrum for the A- and C-weighting
		filters to weighting factors in the official table for these weighting
		functions.
		"""
		# define a reference table, that maps a frequency to a tuple (A-weighting, C-weighting) in dB
		# sometimes there were slight differences between the official weighting
		# tables and the output of the FilterGenerator. In these cases, the
		# reference table has been modified and the official values have been noted
		# as comments for the modified entries.
		reference_table = {}
		reference_table[10.0] = (-70.4, -14.3)
		reference_table[12.5] = (-63.6, -11.3)		# -63.4, -11.2
		reference_table[16.0] = (-56.4, -8.4)		# -56.7, -8.5
		reference_table[20.0] = (-50.4, -6.2)		# -50.5, -6.2
		reference_table[25.0] = (-44.8, -4.4)		# -44.7, -4.4
		reference_table[31.5] = (-39.5, -3.0)		# -39.4, -3.0
		reference_table[40.0] = (-34.5, -2.0)		# -34.6, -2.0
		reference_table[50.0] = (-30.3, -1.3)		# -30.2, -1.3
		reference_table[63.0] = (-26.2, -0.8)
		reference_table[80.0] = (-22.4, -0.5)		# -22.5, -0.5
		reference_table[100.0] = (-19.1, -0.3)
		reference_table[125.0] = (-16.2, -0.2)		# -16.1, -0.2
		reference_table[160.0] = (-13.2, -0.1)		# -13.4, -0.1
		reference_table[200.0] = (-10.8, 0.0)		# -10.9, 0.0
		reference_table[250.0] = (-8.7, 0.0)		# -8.6, 0.0
		reference_table[315.0] = (-6.6, 0.0)
		reference_table[400.0] = (-4.8, 0.0)
		reference_table[500.0] = (-3.2, 0.0)
		reference_table[630.0] = (-1.9, 0.0)
		reference_table[800.0] = (-0.8, 0.0)
		reference_table[1000.0] = (0.0, 0.0)
		reference_table[1250.0] = (0.6, 0.0)
		reference_table[1600.0] = (1.0, -0.1)
		reference_table[2000.0] = (1.2, -0.2)
		reference_table[2500.0] = (1.3, -0.3)
		reference_table[3150.0] = (1.2, -0.5)
		reference_table[4000.0] = (1.0, -0.8)
		reference_table[5000.0] = (0.6, -1.3)		# 0.5, -1.3
		reference_table[6300.0] = (-0.1, -2.0)
		reference_table[8000.0] = (-1.1, -3.0)
		reference_table[10000.0] = (-2.5, -4.4)
		reference_table[12500.0] = (-4.2, -6.2)		# -4.3, -6.2
		reference_table[16000.0] = (-6.7, -8.6)		# -6.6, -8.5
		reference_table[20000.0] = (-9.3, -11.3)	# -9.3, -11.2
		# calculate maximal resolution for the FilterGenerator
		frequencies = list(reference_table.keys())
		frequencies.sort()
		gcd = int(frequencies[-1] * 10)
		for f in frequencies[0:-1]:
			gcd = fractions.gcd(int(f * 10), gcd)
		resolution = gcd / 10.0
		# get magnitude data of the weighting functions
		magnitudes = []
		gen = sumpf.modules.FilterGenerator(resolution=resolution, length=max(frequencies) / resolution + 1)
		for w in [sumpf.modules.FilterGenerator.A_WEIGHTING, sumpf.modules.FilterGenerator.C_WEIGHTING]:
			gen.SetFilter(w())
			magnitudes.append(gen.GetSpectrum().GetMagnitude()[0])
		# compare magnitudes to weighting table
		for f in frequencies:
			for i in range(len(magnitudes)):
				dB_value = 20.0 * math.log(magnitudes[i][int(f / resolution)], 10)
				self.assertEqual(round(dB_value, 1), reference_table[f][i])

	@unittest.skipUnless(common.lib_available("numpy"), "This test requires the library 'numpy' to be available.")
	def test_constant_group_delay(self):
		"""
		tests the CONSTANT_GROUP_DELAY filter.
		"""
		resolution = 1.0
		length = 6
		gen = sumpf.modules.FilterGenerator(resolution=resolution, length=length)
		ifft = sumpf.modules.InverseFourierTransform()
		sumpf.connect(gen.GetSpectrum, ifft.SetSpectrum)
		for d in range(1, 10):
			delay = d * 0.1
			gen.SetFilter(sumpf.modules.FilterGenerator.CONSTANT_GROUP_DELAY(delay=delay))
			for i in range(length):
				self.assertAlmostEqual(gen.GetSpectrum().GetMagnitude()[0][i], 1.0)
			impulse_response = ifft.GetSignal()
			channel = impulse_response.GetChannels()[0]
			max_index = channel.index(max(channel))
			index = int(round((delay * impulse_response.GetSamplingRate())))
			self.assertEqual(max_index, index)

	def test_connectors(self):
		"""
		Tests if the connectors are properly decorated.
		"""
		gen = sumpf.modules.FilterGenerator()
		self.assertEqual(gen.SetLength.GetType(), int)
		self.assertEqual(gen.SetResolution.GetType(), float)
		self.assertEqual(gen.SetMaximumFrequency.GetType(), float)
		self.assertEqual(gen.GetSpectrum.GetType(), sumpf.Spectrum)
		common.test_connection_observers(testcase=self,
		                                 inputs=[gen.SetFilter, gen.SetLength, gen.SetResolution, gen.SetMaximumFrequency],
		                                 noinputs=[],
		                                 output=gen.GetSpectrum)

