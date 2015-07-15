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

import math
import unittest
import sumpf
import _common as common

try:
    import numpy
except ImportError:
    numpy = sumpf.helper.numpydummy


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
        for i in range(1, len(phase_linear) - 716):
            difference = abs(phase_linear[i] - phase_nonlinear[i])
            if difference < math.pi:
                self.assertLess(difference, 0.1)

    @unittest.skipUnless(sumpf.config.get("run_long_tests"), "Long tests are skipped")
    @unittest.skipUnless(common.lib_available("numpy"), "This test requires the library 'numpy' to be available.")
    def test_warp_frequency(self):
        """
        Tests if setting a warp frequency can minimize the auralization errors at
        given frequencies.
        """
        thiele_small_parameters = sumpf.ThieleSmallParameters()
        properties = sumpf.modules.ChannelDataProperties(spectrum_length=20000, resolution=1.0)
        excitation_voltage = sumpf.modules.SweepGenerator(start_frequency=1.0, stop_frequency=19000.0, function=sumpf.modules.SweepGenerator.Linear)
        sumpf.connect(properties.GetSamplingRate, excitation_voltage.SetSamplingRate)
        sumpf.connect(properties.GetSignalLength, excitation_voltage.SetLength)
        auralization_linear = sumpf.modules.ThieleSmallParameterAuralizationLinear(thiele_small_parameters=thiele_small_parameters)
        sumpf.connect(excitation_voltage.GetSignal, auralization_linear.SetVoltage)
        auralization_nonlinear = sumpf.modules.ThieleSmallParameterAuralizationNonlinear(thiele_small_parameters=thiele_small_parameters)
        sumpf.connect(excitation_voltage.GetSignal, auralization_nonlinear.SetVoltage)
        linear_fft = sumpf.modules.FourierTransform()
        sumpf.connect(auralization_linear.GetSoundPressure, linear_fft.SetSignal)
        nonlinear_fft = sumpf.modules.FourierTransform()
        sumpf.connect(auralization_nonlinear.GetSoundPressure, nonlinear_fft.SetSignal)
        difference = sumpf.modules.SubtractSpectrums()
        sumpf.connect(linear_fft.GetSpectrum, difference.SetInput1)
        sumpf.connect(nonlinear_fft.GetSpectrum, difference.SetInput2)
        square = sumpf.modules.MultiplySpectrums()
        sumpf.connect(difference.GetOutput, square.SetInput1)
        sumpf.connect(difference.GetOutput, square.SetInput2)
        channel = tuple(numpy.abs(square.GetOutput().GetChannels()[0]))
        self.assertLess(channel.index(min(channel[0:300])), 50)             # the simulation should be precise at 0Hz
        auralization_nonlinear.SetWarpFrequency(4000.0)
        channel = tuple(numpy.abs(square.GetOutput().GetChannels()[0]))
        self.assertLessEqual(channel.index(min(channel)), 5)                # the simulation should still be precise at 0Hz
        self.assertLess(abs(4000 - channel.index(min(channel[50:]))), 20)   # the error should have a minimum around 4000Hz

    @unittest.skipUnless(sumpf.config.get("run_long_tests"), "Long tests are skipped")
    @unittest.skipUnless(common.lib_available("numpy"), "This test requires the library 'numpy' to be available.")
    def test_regularization(self):
        """
        Tests if the regularization helps stabilizing the instability of the bilinear
        transform at half the sampling frequency.
        """
        thiele_small_parameters = sumpf.ThieleSmallParameters()
        excitation_voltage = sumpf.modules.SweepGenerator(start_frequency=10.0, stop_frequency=10000.0, function=sumpf.modules.SweepGenerator.Linear, samplingrate=44100.0, length=2 ** 16).GetSignal()
        auralization_nonregularized = sumpf.modules.ThieleSmallParameterAuralizationNonlinear(voltage_signal=excitation_voltage, thiele_small_parameters=thiele_small_parameters, regularization=0.0).GetSoundPressure()
        nonregularized_spectrum = sumpf.modules.FourierTransform(signal=auralization_nonregularized).GetSpectrum()
        auralization_regularized = sumpf.modules.ThieleSmallParameterAuralizationNonlinear(voltage_signal=excitation_voltage, thiele_small_parameters=thiele_small_parameters, regularization=0.01).GetSoundPressure()
        regularized_spectrum = sumpf.modules.FourierTransform(signal=auralization_regularized).GetSpectrum()
        self.assertLess(regularized_spectrum.GetMagnitude()[0][-1], nonregularized_spectrum.GetMagnitude()[0][-1])
        derivative_regularized = sumpf.helper.differentiate(regularized_spectrum.GetMagnitude()[0])
        derivative_nonregularized = sumpf.helper.differentiate(nonregularized_spectrum.GetMagnitude()[0])
        self.assertLess(derivative_regularized[-1], derivative_nonregularized[-1])

    def test_nonlinear_concatenation(self):
        """
        Tests if saving the last samples of the recently auralized signal works as expected.
        """
        thiele_small_parameters = sumpf.ThieleSmallParameters()
        sweep1 = sumpf.modules.SweepGenerator(start_frequency=10.0, stop_frequency=10000.0, function=sumpf.modules.SweepGenerator.Linear, samplingrate=44100.0, length=2 ** 8).GetSignal()
        sweep2 = sumpf.modules.ConcatenateSignals(signal1=sweep1, signal2=sweep1).GetOutput()
        auralization = sumpf.modules.ThieleSmallParameterAuralizationNonlinear(thiele_small_parameters=thiele_small_parameters,
                                                                               voltage_signal=sweep1,
                                                                               save_samples=False)
        auralized1_0 = auralization.GetCurrent()
        auralized1_1 = auralization.GetCurrent()
        self.assertEqual(auralized1_0, auralized1_1)
        auralization.SetSaveSamples(True)
        auralized1_2 = auralization.GetCurrent()
        auralized1_3 = auralization.GetCurrent()
        self.assertEqual(auralized1_2, auralized1_3)
        auralization.ResetSavedSamples()
        auralization.SetVoltage(sweep2)
        auralized2_0 = auralization.GetCurrent()
        auralized2_1 = sumpf.modules.ConcatenateSignals(signal1=auralized1_0, signal2=auralized1_2).GetOutput()
        self.assertEqual(auralized2_0.GetChannels(), auralized2_1.GetChannels())
        auralization.SetVoltage(sweep1)
        auralization.SetSaveSamples(False)
        auralized1_2 = auralization.GetCurrent()
        self.assertEqual(auralized1_0, auralized1_2)

    @unittest.skipUnless(common.lib_available("cython"), "This test requires the library 'cython' to be available.")
    def test_cython(self):
        thiele_small_parameters = sumpf.ThieleSmallParameters()
        sweep = sumpf.modules.SweepGenerator(start_frequency=10.0, stop_frequency=10000.0, function=sumpf.modules.SweepGenerator.Linear, samplingrate=44100.0, length=2 ** 2).GetSignal()
        python = sumpf.modules.ThieleSmallParameterAuralizationNonlinear(thiele_small_parameters=thiele_small_parameters,
                                                                         voltage_signal=sweep,
                                                                         listener_distance=2.9,
                                                                         medium_density=1.5,
                                                                         warp_frequency=33.2,
                                                                         regularization=0.1,
                                                                         save_samples=True,
                                                                         use_cython=False)
        cython = sumpf.modules.ThieleSmallParameterAuralizationNonlinear(thiele_small_parameters=thiele_small_parameters,
                                                                         voltage_signal=sweep,
                                                                         listener_distance=2.9,
                                                                         medium_density=1.5,
                                                                         warp_frequency=33.2,
                                                                         regularization=0.1,
                                                                         save_samples=True,
                                                                         use_cython=True)
        self.assertEqual(python.GetCurrent(), cython.GetCurrent())
        sine = sumpf.modules.SineWaveGenerator(frequency=443.9, samplingrate=48000.0, length=2 ** 7).GetSignal()
        python.SetVoltage(sine)
        cython.SetVoltage(sine)
        common.compare_signals_almost_equal(self, signal1=python.GetSoundPressure(), signal2=cython.GetSoundPressure(), places=11)

    @unittest.skipUnless(sumpf.config.get("run_long_tests"), "Long tests are skipped")
    @unittest.skipUnless(common.lib_available("numpy"), "This test requires the library 'numpy' to be available.")
    def test_nonlinearities(self):
        """
        Tests if the nonlinearities are produced as expected.
        """
        def force_factor(f=0.0, x=0.0, v=0.0, T=20.0):
            return 10.0 + 1000.0 * x - 1000000.0 * x ** 2
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
        for i in range(1, int(round(10000.0 / nonlinear_spectrum.GetResolution()))):
            if nonlinear_magnitude[i - 1] < nonlinear_magnitude[i] > nonlinear_magnitude[i + 1]:
                nonlinear_peaks.append(i)
        self.assertEqual(nonlinear_peaks, [int(round(73.0 * (i + 1) / nonlinear_spectrum.GetResolution())) for i in range(3)])

    def test_connectors(self):
        """
        Tests if the connectors are properly decorated.
        """
        if common.lib_available("numpy"):
            aur = sumpf.modules.ThieleSmallParameterAuralizationLinear()
            self.assertEqual(aur.SetThieleSmallParameters.GetType(), sumpf.ThieleSmallParameters)
            self.assertEqual(aur.SetVoltage.GetType(), sumpf.Signal)
            self.assertEqual(aur.SetListenerDistance.GetType(), float)
            self.assertEqual(aur.SetMediumDensity.GetType(), float)
            self.assertEqual(aur.GetExcursion.GetType(), sumpf.Signal)
            self.assertEqual(aur.GetVelocity.GetType(), sumpf.Signal)
            self.assertEqual(aur.GetAcceleration.GetType(), sumpf.Signal)
            self.assertEqual(aur.GetCurrent.GetType(), sumpf.Signal)
            self.assertEqual(aur.GetSoundPressure.GetType(), sumpf.Signal)
            for getter in [aur.GetExcursion, aur.GetVelocity, aur.GetAcceleration, aur.GetCurrent, aur.GetSoundPressure]:
                common.test_connection_observers(testcase=self,
                                                 inputs=[aur.SetThieleSmallParameters, aur.SetVoltage, aur.SetListenerDistance, aur.SetMediumDensity],
                                                 noinputs=[],
                                                 output=getter)
        aur = sumpf.modules.ThieleSmallParameterAuralizationNonlinear()
        self.assertEqual(aur.SetThieleSmallParameters.GetType(), sumpf.ThieleSmallParameters)
        self.assertEqual(aur.SetVoltage.GetType(), sumpf.Signal)
        self.assertEqual(aur.SetListenerDistance.GetType(), float)
        self.assertEqual(aur.SetMediumDensity.GetType(), float)
        self.assertEqual(aur.SetWarpFrequency.GetType(), float)
        self.assertEqual(aur.SetRegularization.GetType(), float)
        self.assertEqual(aur.SetSaveSamples.GetType(), bool)
        self.assertEqual(aur.SetUseCython.GetType(), bool)
        self.assertEqual(aur.GetExcursion.GetType(), sumpf.Signal)
        self.assertEqual(aur.GetVelocity.GetType(), sumpf.Signal)
        self.assertEqual(aur.GetAcceleration.GetType(), sumpf.Signal)
        self.assertEqual(aur.GetCurrent.GetType(), sumpf.Signal)
        self.assertEqual(aur.GetSoundPressure.GetType(), sumpf.Signal)
        for getter in [aur.GetExcursion, aur.GetVelocity, aur.GetAcceleration, aur.GetCurrent, aur.GetSoundPressure]:
            common.test_connection_observers(testcase=self,
                                             inputs=[aur.SetThieleSmallParameters, aur.SetVoltage, aur.SetListenerDistance, aur.SetMediumDensity, aur.SetWarpFrequency, aur.SetRegularization],
                                             noinputs=[aur.SetSaveSamples, aur.SetUseCython, aur.ResetSavedSamples],
                                             output=getter)

