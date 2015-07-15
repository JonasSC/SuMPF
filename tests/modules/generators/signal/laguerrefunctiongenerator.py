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


class TestLaguerreFunctionGenerator(unittest.TestCase):
    """
    A TestCase for the LaguerreFunctionGenerator module.
    """
    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)
        self.__laguerre = []
        self.__ordinary_laguerre = []

    @unittest.skipUnless(sumpf.config.get("run_long_tests"), "Long tests are skipped")
    def test_orthonormality(self):
        """
        Tests the orthonormality of the generated Laguerre functions.
        """
        laguerre = self.__GetLaguerreFunctions()
        for g in range(len(laguerre)):
            for s in range(len(laguerre[g])):
                for o1 in range(len(laguerre[g][s])):
                    for o2 in range(o1, len(laguerre[g][s])):
                        product = laguerre[g][s][o1] * laguerre[g][s][o2]
                        integral = sum(product.GetChannels()[0]) / product.GetSamplingRate()
                        if o1 == o2:
                            self.assertAlmostEqual(integral, 1.0, 0)
                        else:
                            self.assertAlmostEqual(integral, 0.0, 0)

    @unittest.skipUnless(sumpf.config.get("run_long_tests"), "Long tests are skipped")
    def test_scaling_factor(self):
        """
        Tests if the amplitude of the generated Laguerre functions raises with
        raising scaling factor and the time stretch falls with raising scaling
        factor.
        """
        laguerre = self.__GetLaguerreFunctions()
        for g in range(len(laguerre)):
            for s in range(len(laguerre[g]) - 1):
                for o in range(1, len(laguerre[g][s])):
                    channel1 = laguerre[g][s][o].GetChannels()[0]
                    channel2 = laguerre[g][s + 1][o].GetChannels()[0]
                    index1 = 0
                    index2 = 0
                    if o % 2 == 0:
                        index1 = channel1.index(min(channel1))
                        index2 = channel2.index(min(channel2))
                    else:
                        index1 = channel1.index(max(channel1))
                        index2 = channel2.index(max(channel2))
                    self.assertGreater(index1, index2)
                    self.assertLess(abs(channel1[index1]), abs(channel2[index2]))

    @unittest.skipUnless(sumpf.config.get("run_long_tests"), "Long tests are skipped")
    def test_generalization_order(self):
        """
        Tests if the function is shifted by the order of generalization as expected.
        """
        laguerre = self.__GetLaguerreFunctions()
        for g in range(len(laguerre) - 1):
            for s in range(len(laguerre[g])):
                for o in range(len(laguerre[g][s])):
                    p = 10.0 * (s + 1)
                    channel = laguerre[g][s][o].GetChannels()[0]
                    if g == 0:
                        self.assertAlmostEqual(abs(channel[0]), ((2.0 * p) ** 0.5))
                    else:
                        self.assertEqual(channel[0], 0.0)
                        channel2 = laguerre[g + 1][s][o].GetChannels()[0]
                        index1 = 0
                        index2 = 0
                        if o % 2 == 0:
                            index1 = channel.index(max(channel))
                            index2 = channel2.index(max(channel2))
                            if o > 0:
                                index1 = min(index1, channel.index(min(channel)))
                                index2 = min(index2, channel2.index(min(channel2)))
                        else:
                            index1 = channel.index(min(channel))
                            index2 = channel2.index(min(channel2))
                            if o > 0:
                                index1 = min(index1, channel.index(max(channel)))
                                index2 = min(index2, channel2.index(max(channel2)))
                        self.assertLess(index1, index2)
                        self.assertGreater(abs(channel[index1]), abs(channel2[index2]))

    @unittest.skipUnless(sumpf.config.get("run_long_tests"), "Long tests are skipped")
    @unittest.skipUnless(common.lib_available("numpy"), "This test requires the library 'numpy' to be available.")
    def test_compare_with_filter(self):
        """
        Compares the Laguerre functions from this generator with those that have
        been created in the frequency domain.
        """
        time_laguerre = self.__GetOrdinaryLaguerreFunctions()
        properties = sumpf.modules.ChannelDataProperties(signal_length=len(time_laguerre[0][0]), samplingrate=time_laguerre[0][0].GetSamplingRate())
        frequency_laguerre = []
        gen = sumpf.modules.LaguerreFilterGenerator(resolution=properties.GetResolution(), length=properties.GetSpectrumLength())
        for s in range(3):
            frequency_laguerre.append([])
            for o in [0, 1, 4]:
                gen.SetOrder(o)
                gen.SetScalingFactor(scaling_factor=10.0 * (s + 1.0))
                function = sumpf.modules.InverseFourierTransform(spectrum=gen.GetSpectrum()).GetSignal()
                frequency_laguerre[s].append(function * function.GetSamplingRate())
        for a in range(len(time_laguerre)):
            for b in range(len(time_laguerre[a])):
                common.compare_signals_almost_equal(testcase=self,
                                                    signal1=time_laguerre[a][b][1500:-1500],
                                                    signal2=frequency_laguerre[a][b][1500:-1500],
                                                    places=3,
                                                    compare_labels=False)

    def test_labels(self):
        """
        Tests if the labels for the generated Laguerre functions are set correctly.
        """
        expected_labels = ((0, "0th order Laguerre"),
                           (1, "1st order Laguerre"),
                           (2, "2nd order Laguerre"),
                           (3, "3rd order Laguerre"),
                           (11, "11th order Laguerre"),
                           (12, "12th order Laguerre"),
                           (13, "13th order Laguerre"),
                           (14, "14th order Laguerre"),
                           (111, "111th order Laguerre"),
                           (122, "122nd order Laguerre"))
        gen = sumpf.modules.LaguerreFunctionGenerator(scaling_factor=1.0, generalization_order=0, samplingrate=1.0, length=2)
        for l in expected_labels:
            gen.SetOrder(l[0])
            self.assertEqual(gen._GetLabel(), l[1])

    def test_connectors(self):
        """
        Tests if the connectors are properly decorated.
        """
        gen = sumpf.modules.LaguerreFunctionGenerator()
        self.assertEqual(gen.SetOrder.GetType(), int)
        self.assertEqual(gen.SetScalingFactor.GetType(), float)
        self.assertEqual(gen.SetGeneralizationOrder.GetType(), int)
        self.assertEqual(gen.SetLength.GetType(), int)
        self.assertEqual(gen.SetSamplingRate.GetType(), float)
        self.assertEqual(gen.GetSignal.GetType(), sumpf.Signal)
        common.test_connection_observers(testcase=self,
                                         inputs=[gen.SetOrder, gen.SetScalingFactor, gen.SetGeneralizationOrder, gen.SetLength, gen.SetSamplingRate],
                                         noinputs=[],
                                         output=gen.GetSignal)

    def __GetLaguerreFunctions(self):
        if self.__laguerre == []:
            gen = sumpf.modules.LaguerreFunctionGenerator(order=0,
                                                          scaling_factor=1.0,
                                                          generalization_order=0,
                                                          samplingrate=200,
                                                          length=10000)
            self.__laguerre.append(self.__GetOrdinaryLaguerreFunctions())
            for g in range(1, 3):
                self.__laguerre.append([])
                for s in range(3):
                    self.__laguerre[g].append([])
                    for o in [0, 1, 4]:
                        gen.SetOrder(o)
                        gen.SetScalingFactor(10.0 * (s + 1))
                        gen.SetGeneralizationOrder(3 * g)
                        self.__laguerre[g][s].append(gen.GetSignal())
        return self.__laguerre

    def __GetOrdinaryLaguerreFunctions(self):
        if self.__ordinary_laguerre == []:
            gen = sumpf.modules.LaguerreFunctionGenerator(order=0,
                                                          scaling_factor=1.0,
                                                          generalization_order=0,
                                                          samplingrate=200,
                                                          length=10000)
            for s in range(3):
                self.__ordinary_laguerre.append([])
                for o in [0, 1, 4]:
                    gen.SetOrder(o)
                    gen.SetScalingFactor(10.0 * (s + 1))
                    self.__ordinary_laguerre[s].append(gen.GetSignal())
        return self.__ordinary_laguerre

