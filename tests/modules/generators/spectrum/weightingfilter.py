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

import collections
import fractions
import math
import unittest
import sumpf
import _common as common


class TestWeightingFilterGenerator(unittest.TestCase):
    """
    A TestCase for the WeightingFilterGenerator module.
    """
    @unittest.skipUnless(sumpf.config.get("run_long_tests"), "Long tests are skipped")
    def test_function(self):
        """
        Tests the generator's output.
        """
        # define a reference table, that maps a frequency to a tuple (A-weighting, C-weighting) in dB
        # sometimes there were slight differences between the official weighting
        # tables and the output of the FilterGenerator. In these cases, the
        # reference table has been modified and the official values have been noted
        # as comments for the modified entries.
        reference_table = {}
        reference_table[10.0] = (-70.4, -14.3)
        reference_table[12.5] = (-63.6, -11.3)      # -63.4, -11.2
        reference_table[16.0] = (-56.4, -8.4)       # -56.7, -8.5
        reference_table[20.0] = (-50.4, -6.2)       # -50.5, -6.2
        reference_table[25.0] = (-44.8, -4.4)       # -44.7, -4.4
        reference_table[31.5] = (-39.5, -3.0)       # -39.4, -3.0
        reference_table[40.0] = (-34.5, -2.0)       # -34.6, -2.0
        reference_table[50.0] = (-30.3, -1.3)       # -30.2, -1.3
        reference_table[63.0] = (-26.2, -0.8)
        reference_table[80.0] = (-22.4, -0.5)       # -22.5, -0.5
        reference_table[100.0] = (-19.1, -0.3)
        reference_table[125.0] = (-16.2, -0.2)      # -16.1, -0.2
        reference_table[160.0] = (-13.2, -0.1)      # -13.4, -0.1
        reference_table[200.0] = (-10.8, 0.0)       # -10.9, 0.0
        reference_table[250.0] = (-8.7, 0.0)        # -8.6, 0.0
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
        reference_table[5000.0] = (0.6, -1.3)       # 0.5, -1.3
        reference_table[6300.0] = (-0.1, -2.0)
        reference_table[8000.0] = (-1.1, -3.0)
        reference_table[10000.0] = (-2.5, -4.4)
        reference_table[12500.0] = (-4.2, -6.2)     # -4.3, -6.2
        reference_table[16000.0] = (-6.7, -8.6)     # -6.6, -8.5
        reference_table[20000.0] = (-9.3, -11.3)    # -9.3, -11.2
        # calculate maximal resolution for the FilterGenerator
        frequencies = list(reference_table.keys())
        frequencies.sort()
        gcd = int(frequencies[-1] * 10)
        for f in frequencies[0:-1]:
            gcd = fractions.gcd(int(f * 10), gcd)
        resolution = gcd / 10.0
        # get magnitude data of the weighting functions
        magnitudes = []
        gen = sumpf.modules.WeightingFilterGenerator(resolution=resolution, length=max(frequencies) / resolution + 1)
        for w in [sumpf.modules.WeightingFilterGenerator.A, sumpf.modules.WeightingFilterGenerator.C]:
            gen.SetWeighting(w)
            magnitudes.append(gen.GetSpectrum().GetMagnitude()[0])
        # compare magnitudes to weighting table
        for f in frequencies:
            for i in range(len(magnitudes)):
                dB_value = 20.0 * math.log(magnitudes[i][int(f / resolution)], 10)
                self.assertEqual(round(dB_value, 1), reference_table[f][i])

    def test_connectors(self):
        """
        Tests if the connectors are properly decorated.
        """
        gen = sumpf.modules.WeightingFilterGenerator()
        self.assertEqual(gen.SetWeighting.GetType(), collections.Callable)
        self.assertEqual(gen.SetLength.GetType(), int)
        self.assertEqual(gen.SetResolution.GetType(), float)
        self.assertEqual(gen.SetMaximumFrequency.GetType(), float)
        self.assertEqual(gen.GetSpectrum.GetType(), sumpf.Spectrum)
        common.test_connection_observers(testcase=self,
                                         inputs=[gen.SetWeighting, gen.SetLength, gen.SetResolution, gen.SetMaximumFrequency],
                                         noinputs=[],
                                         output=gen.GetSpectrum)

