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

import math
import unittest

import sumpf
import _common as common


class TestThieleSmallParameterAuralization(unittest.TestCase):
	"""
	A TestCase for the ThieleSmallParameterAuralizationLinear and
	ThieleSmallParameterAuralizationNonlinear modules.
	"""
	@unittest.skipUnless(sumpf.config.get("run_long_tests"), "Long tests are skipped")
	@unittest.skipUnless(common.lib_available("numpy"), "This test requires the library 'numpy' to be available.")
	def test_frequency_response(self):
		"""
		Compares the frequency responses of the two auralization methods.
		"""
		thiele_small_parameters = sumpf.ThieleSmallParameters()
		ts_int = sumpf.modules.ThieleSmallParameterInterpretation(thiele_small_parameters=thiele_small_parameters)
		resonance_frequency = ts_int.GetResonanceFrequency()
		q_factor = ts_int.GetTotalQFactor()
		delta_f = resonance_frequency / (2.0 * q_factor)
		length = 2 ** 14
		samplingrate = 44100.0
		sweep = sumpf.modules.SweepGenerator(samplingrate=samplingrate, length=length).GetSignal()
		sine_low = sumpf.modules.SineWaveGenerator(frequency=resonance_frequency - delta_f, samplingrate=samplingrate, length=length).GetSignal()
		sine_resonance = sumpf.modules.SineWaveGenerator(frequency=resonance_frequency, samplingrate=samplingrate, length=length).GetSignal()
		sine_high = sumpf.modules.SineWaveGenerator(frequency=resonance_frequency + delta_f, samplingrate=samplingrate, length=length).GetSignal()
		excitation_voltage = sumpf.modules.MergeSignals(signals=[sweep, sine_low, sine_resonance, sine_high]).GetOutput()
		auralization_linear = sumpf.modules.ThieleSmallParameterAuralizationLinear(thiele_small_parameters=thiele_small_parameters, voltage_signal=excitation_voltage)
		auralization_nonlinear = sumpf.modules.ThieleSmallParameterAuralizationNonlinear(thiele_small_parameters=thiele_small_parameters, voltage_signal=excitation_voltage)
		# compare auralization with calculated Q factor
		for a in [auralization_linear, auralization_nonlinear]:
			rms = sumpf.modules.RootMeanSquare(signal=a.GetVelocity(), integration_time=sumpf.modules.RootMeanSquare.FULL).GetOutput()
			lower_corner = rms.GetChannels()[1][0]
			resonance = rms.GetChannels()[2][0]
			higher_corner = rms.GetChannels()[3][0]
			self.assertAlmostEqual(resonance / ((lower_corner + higher_corner) / 2.0), 2.0 ** 0.5, 1)
		# compare magnitude
		spectrum_linear = sumpf.modules.FourierTransform(signal=auralization_linear.GetSoundPressure()).GetSpectrum()
		spectrum_nonlinear = sumpf.modules.FourierTransform(signal=auralization_nonlinear.GetSoundPressure()).GetSpectrum()
		magnitude_linear = spectrum_linear.GetMagnitude()[0]
		magnitude_nonlinear = spectrum_nonlinear.GetMagnitude()[0]
		for i in range(2, int(round(2205.0 / spectrum_linear.GetResolution()))):
			dB_difference = 20.0 * math.log(magnitude_linear[i] / magnitude_nonlinear[i], 10.0)
			self.assertLess(abs(dB_difference), 0.08)
		for i in range(int(round(2205.0 / spectrum_linear.GetResolution())), int(round(5512.0 / spectrum_linear.GetResolution()))):
			dB_difference = 20.0 * math.log(magnitude_linear[i] / magnitude_nonlinear[i], 10.0)
			self.assertLess(abs(dB_difference), 0.49)
		for i in range(int(round(5512.0 / spectrum_linear.GetResolution())), len(spectrum_nonlinear) - 92):
			self.assertLess(magnitude_nonlinear[i], magnitude_linear[i])
		# compare phase
		phase_linear = spectrum_linear.GetPhase()[0]
		phase_nonlinear = spectrum_nonlinear.GetPhase()[0]
		for i in range(1, len(phase_linear) - 2):
			difference = abs(phase_linear[i] - phase_nonlinear[i])
			if difference < math.pi:
				self.assertLess(difference, 0.2)

	@unittest.skipUnless(sumpf.config.get("run_long_tests"), "Long tests are skipped")
	@unittest.skipUnless(common.lib_available("numpy"), "This test requires the library 'numpy' to be available.")
	def test_nonlinearities(self):
		"""
		Tests if the nonlinearities are produced as expected.
		"""
		def force_factor(frequency=0.0, membrane_displacement=0.0, membrane_velocity=0.0, voicecoil_temperature=20.0):
			return 10.0 + 1000.0 * membrane_displacement - 1000000.0 * membrane_displacement ** 2
		ts = sumpf.ThieleSmallParameters(force_factor=force_factor)
		sine = sumpf.modules.SineWaveGenerator(frequency=73.0, samplingrate=44100, length=2 ** 14).GetSignal()
		linear = sumpf.modules.ThieleSmallParameterAuralizationLinear(thiele_small_parameters=ts, voltage_signal=sine).GetSoundPressure()
		nonlinear = sumpf.modules.ThieleSmallParameterAuralizationNonlinear(thiele_small_parameters=ts, voltage_signal=sine).GetSoundPressure()
		linear_spectrum = sumpf.modules.FourierTransform(signal=linear).GetSpectrum()
		nonlinear_spectrum = sumpf.modules.FourierTransform(signal=nonlinear).GetSpectrum()
		linear_magnitude = linear_spectrum.GetMagnitude()[0]
		nonlinear_magnitude = nonlinear_spectrum.GetMagnitude()[0]
		linear_peaks = []
		for i in range(1, len(linear_magnitude) - 1):
			if linear_magnitude[i - 1] < linear_magnitude[i] > linear_magnitude[i + 1]:
				linear_peaks.append(i)
		self.assertEqual(linear_peaks, [int(round(73.0 / linear_spectrum.GetResolution()))])
		nonlinear_peaks = []
		for i in range(1, len(nonlinear_magnitude) - 1):
			if nonlinear_magnitude[i - 1] < nonlinear_magnitude[i] > nonlinear_magnitude[i + 1]:
				nonlinear_peaks.append(i)
		self.assertEqual(nonlinear_peaks, [int(round(73.0 * (i + 1) / linear_spectrum.GetResolution())) for i in range(3)])

	def test_connectors(self):
		"""
		Tests if the connectors are properly decorated.
		"""
		class_list = [sumpf.modules.ThieleSmallParameterAuralizationNonlinear]
		if common.lib_available("numpy"):
			class_list.append(sumpf.modules.ThieleSmallParameterAuralizationLinear)
		for cls in class_list:
			aur = cls()
			self.assertEqual(aur.SetThieleSmallParameters.GetType(), sumpf.ThieleSmallParameters)
			self.assertEqual(aur.SetVoltage.GetType(), sumpf.Signal)
			self.assertEqual(aur.SetListenerDistance.GetType(), float)
			self.assertEqual(aur.SetMediumDensity.GetType(), float)
			self.assertEqual(aur.GetDisplacement.GetType(), sumpf.Signal)
			self.assertEqual(aur.GetVelocity.GetType(), sumpf.Signal)
			self.assertEqual(aur.GetAcceleration.GetType(), sumpf.Signal)
			self.assertEqual(aur.GetCurrent.GetType(), sumpf.Signal)
			self.assertEqual(aur.GetSoundPressure.GetType(), sumpf.Signal)
			for getter in [aur.GetDisplacement, aur.GetVelocity, aur.GetAcceleration, aur.GetCurrent, aur.GetSoundPressure]:
				common.test_connection_observers(testcase=self,
				                                 inputs=[aur.SetThieleSmallParameters, aur.SetVoltage, aur.SetListenerDistance, aur.SetMediumDensity],
				                                 noinputs=[],
				                                 output=getter)

