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

import unittest
import sumpf
import _common as common

try:
    import numpy
except ImportError:
    pass


class TestMath(unittest.TestCase):
    """
    A TestCase for the mathematical helper functions.
    """

    def test_binomial_coefficient(self):
        """
        Tests the sumpf.helper.binomial_coefficient function.
        """
        pascal = ((1,),
                  (1, 1),
                  (1, 2, 1),
                  (1, 3, 3, 1),
                  (1, 4, 6, 4, 1),
                  (1, 5, 10, 10, 5, 1))
        for n in range(len(pascal)):
            for k in range(len(pascal[n])):
                self.assertEqual(sumpf.helper.binomial_coefficient(n, k), pascal[n][k])

    def test_differentiate(self):
        """
        Tests the sumpf.helper.differentiate function.
        """
        tests = []
        tests.append(([1.0, 1.0, 1.0], [0.0, 0.0, 0.0]))    # test constant input
        tests.append(([0.0, 1.0, 2.0], [1.0, 1.0, 1.0]))    # test constant raise
        tests.append(([1.4, 2.5, 3.6], [1.1, 1.1, 1.1]))    # test constant raise with offset
        tests.append(([5.0, 1.0, 5.0], [-4.0, -4.0, 4.0]))  # test symmetric V
        tests.append(([5.0, 1.0, 3.0], [-4.0, -4.0, 2.0]))  # test asymmetric V
        tests.append(([5, 1, 2], [-4.0, -4.0, 1.0]))        # test integer input
        tests.append(([], []))                              # test empty input
        tests.append(([5.0], [0.0]))                        # test input with length 1
        tests.append(([1.0, 3.0], [2.0, 2.0]))              # test input with length 2
        for test, result in tests:
            self.assertEqual(sumpf.helper.differentiate(test), result)

    @unittest.skipUnless(common.lib_available("numpy"), "This test requires the library 'numpy' to be available.")
    def test_differentiate_spline(self):
        """
        Tests the sumpf.helper.differentiate_spline function.
        """
        sequence = [0.4, 2.3, 8.5, 3.5, 7.6, 2.5, 1.4, 2.8, 6.6]
        self.assertRaises(ValueError, sumpf.helper.differentiate_spline, **{"sequence": sequence, "degree": 0})
        # Test the results for very short sequences
        for d in [1, 2, 3, 5, 27]:
            self.assertEqual(sumpf.helper.differentiate_spline(sequence=[], degree=d), [])
            self.assertEqual(sumpf.helper.differentiate_spline(sequence=[sequence[0]], degree=d), [0.0])
            self.assertEqual(sumpf.helper.differentiate_spline(sequence=sequence[0:2], degree=d), [sequence[1] - sequence[0]] * 2)
        # Test if the differentiation algorithm with linear approximation gives
        # the same results as the standard algorithm in the differentiate function.
        self.assertEqual(sumpf.helper.differentiate_spline(sequence=sequence, degree=1), sumpf.helper.differentiate(sequence))
        # Test if the simplified differentiation algorithm with second degree polynomials
        # gives the same results as the slower, but more straight forward implementation.
        result = [sequence[1] - sequence[0]]
        for i in range(1, len(sequence) - 1):
            matrix = [[1.0, -1.0, 1.0],
                      [0.0, 0.0, 1.0],
                      [1.0, 1.0, 1.0]]
            vector = [sequence[i - 1], sequence[i], sequence[i + 1]]
            result.append(numpy.linalg.solve(matrix, vector)[1])
        result.append(sequence[-1] - sequence[-2])
        derivative = sumpf.helper.differentiate_spline(sequence=sequence, degree=2)
        self.assertEqual(len(derivative), len(sequence))
        self.assertEqual(derivative, result)
        # Test if the differentiation algorithm with third degree polynomials gives
        # the same results as with a precalculated solution of the equation system.
        result = [sequence[1] - sequence[0]]
        result.append((sequence[2] - sequence[0]) / 2.0)
        for i in range(2, len(sequence) - 1):
            result.append(sequence[i] / 2.0 + sequence[i + 1] / 3.0 - sequence[i - 1] + sequence[i - 2] / 6.0)
        result.append((3.0 * sequence[-1] - 4.0 * sequence[-2] + sequence[-3]) / 2.0)
        derivative = sumpf.helper.differentiate_spline(sequence=sequence, degree=3)
        self.assertEqual(len(derivative), len(sequence))
        for i in range(len(derivative)):
            self.assertAlmostEqual(derivative[i], result[i])

    @unittest.skipUnless(sumpf.config.get("run_long_tests"), "Long tests are skipped")
    @unittest.skipUnless(common.lib_available("numpy"), "This test requires the library 'numpy' to be available.")
    def test_differentiate_fft(self):
        """
        Tests the sumpf.helper.differentiate_fft function.
        """
        self.assertEqual(sumpf.helper.differentiate_fft(sequence=[]), [])
        self.assertEqual(sumpf.helper.differentiate_fft(sequence=[5.8]), [0.0])
        sweep = sumpf.modules.SweepGenerator(start_frequency=20.0,
                                             stop_frequency=20000.0,
                                             function=sumpf.modules.SweepGenerator.Linear,
                                             samplingrate=44100,
                                             length=2 ** 16).GetSignal()
        diff = sumpf.Signal(channels=(sumpf.helper.differentiate(sweep.GetChannels()[0]),
                                      sumpf.helper.differentiate_fft(sweep.GetChannels()[0])),
                            samplingrate=sweep.GetSamplingRate(),
                            labels=sweep.GetLabels())
        spectrum = sumpf.modules.FourierTransform(signal=diff).GetSpectrum()
        # compare magnitude
        magnitude = spectrum.GetMagnitude()
        for i in range(int(5660.0 / spectrum.GetResolution())):
            self.assertAlmostEqual(magnitude[0][i], magnitude[1][i], -1)
        for i in range(int(5660.0 / spectrum.GetResolution()), int(13080.0 / spectrum.GetResolution())):
            self.assertAlmostEqual(magnitude[0][i], magnitude[1][i], -2)
        for i in range(int(13080.0 / spectrum.GetResolution()), len(spectrum)):
            self.assertAlmostEqual(magnitude[0][i], magnitude[1][i], -3)
        for i in range(int(5000.0 / spectrum.GetResolution()), int(20000.0 / spectrum.GetResolution())):
            self.assertLess(magnitude[0][i], magnitude[1][i])
        # compare phase
        continous_phase = spectrum.GetContinuousPhase()
        for i in range(int(38.0 / spectrum.GetResolution())):
            self.assertAlmostEqual(continous_phase[0][i], continous_phase[1][i], -1)
        for i in range(int(38.0 / spectrum.GetResolution()), int(6950.0 / spectrum.GetResolution())):
            self.assertAlmostEqual(continous_phase[0][i], continous_phase[1][i], 0)
        for i in range(int(6950.0 / spectrum.GetResolution()), len(spectrum)):
            self.assertAlmostEqual(continous_phase[0][i], continous_phase[1][i], -1)

