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



@unittest.skipUnless(common.lib_available("numpy"), "These tests require the library 'numpy' to be available.")
class TestNoiseGenerator(unittest.TestCase):
    """
    A TestCase for the NoiseGenerator module.
    """
    def test_general_stuff(self):
        """
        Tests some general stuff of the NoiseGenerator class
        """
        gen = sumpf.modules.NoiseGenerator()
        self.assertIsInstance(gen._NoiseGenerator__distribution, sumpf.modules.NoiseGenerator.WhiteNoise)   # the default distribution should generate white noise

    @unittest.skipUnless(sumpf.config.get("run_time_variant_tests"), "Tests which are testing random numbers are skipped")
    def test_white_noise(self):
        """
        Tests the white noise generation.
        """
        gen = sumpf.modules.NoiseGenerator(distribution=sumpf.modules.NoiseGenerator.WhiteNoise(), samplingrate=48000)
        fft = sumpf.modules.FourierTransform()
        sumpf.connect(gen.GetSignal, fft.SetSignal)
        rms = sumpf.modules.RootMeanSquare(integration_time=sumpf.modules.RootMeanSquare.FULL)
        sumpf.connect(gen.GetSignal, rms.SetInput)
        avg = sumpf.helper.average.SumList()
        rmss = []
        for i in range(6, 10):
            length = 2 ** i
            gen.SetLength(length)
            magnitude = fft.GetSpectrum().GetMagnitude()[0]
            self.assertAlmostEqual(magnitude[0], 0.0)                           # there should only be a very small dc offset
            self.assertAlmostEqual(min(magnitude[1:-1]), max(magnitude[1:-1]))  # the magnitude of the spectrum should be fairly constant
            output = rms.GetOutput()
            self.assertEqual(output.GetLabels()[0], "White Noise")              # the label for the channel has to be "White Noise"
            self.assertEqual(len(output), length)                               # the length of the generated sequence should be set correctly
            value = output.GetChannels()[0][0]
            rmss.append(value)
            avg.Add(value)
        average = avg.GetAverage()
        for i in rmss:
            self.assertAlmostEqual(i, average, 2)                               # the RMS value of the noise should not change with different signal lengths
        self.assertGreater(average, 0.4)                                        # the RMS value of the noise should be between 0.4 and 0.5
        self.assertLess(average, 0.5)                                           # the RMS value of the noise should be between 0.4 and 0.5

    @unittest.skipUnless(sumpf.config.get("run_time_variant_tests"), "Tests which are testing random numbers are skipped")
    def test_pink_noise(self):
        """
        Tests the pink noise generation.
        """
        gen = sumpf.modules.NoiseGenerator(distribution=sumpf.modules.NoiseGenerator.PinkNoise(), samplingrate=48000)
        fft = sumpf.modules.FourierTransform()
        sumpf.connect(gen.GetSignal, fft.SetSignal)
        rms = sumpf.modules.RootMeanSquare(integration_time=sumpf.modules.RootMeanSquare.FULL)
        sumpf.connect(gen.GetSignal, rms.SetInput)
        avg = sumpf.helper.average.SumList()
        rmss = []
        for i in range(6, 10):
            length = 2 ** i
            gen.SetLength(length)
            magnitude = fft.GetSpectrum().GetMagnitude()[0]
            self.assertAlmostEqual(magnitude[0], 0.0)                   # there should only be very little dc offset
            invmagnitude = tuple(numpy.divide(1.0, magnitude[1:-1]))
            derivative = sumpf.helper.differentiate(invmagnitude)
            self.assertAlmostEqual(min(derivative), max(derivative))    # the magnitude of the spectrum should fall with a rate of 1/f
            output = rms.GetOutput()
            self.assertEqual(output.GetLabels()[0], "Pink Noise")       # the label for the channel has to be "Pink Noise"
            self.assertEqual(len(output), length)                       # the length of the generated sequence should be set correctly
            value = output.GetChannels()[0][0]
            rmss.append(value)
            avg.Add(value)
        average = avg.GetAverage()
        for i in rmss:
            self.assertAlmostEqual(i, average, 2)                       # the RMS value of the noise should not change with different signal lengths
        self.assertGreater(average, 0.4)                                # the RMS value of the noise should be between 0.4 and 0.5
        self.assertLess(average, 0.5)                                   # the RMS value of the noise should be between 0.4 and 0.5

    @unittest.skipUnless(sumpf.config.get("run_time_variant_tests"), "Tests which are testing random numbers are skipped")
    def test_red_noise(self):
        """
        Tests the red noise generation.
        """
        gen = sumpf.modules.NoiseGenerator(distribution=sumpf.modules.NoiseGenerator.RedNoise(), samplingrate=48000)
        fft = sumpf.modules.FourierTransform()
        sumpf.connect(gen.GetSignal, fft.SetSignal)
        rms = sumpf.modules.RootMeanSquare(integration_time=sumpf.modules.RootMeanSquare.FULL)
        sumpf.connect(gen.GetSignal, rms.SetInput)
        avg = sumpf.helper.average.SumList()
        rmss = []
        for i in range(6, 10):
            length = 2 ** i
            gen.SetLength(length)
            magnitude = fft.GetSpectrum().GetMagnitude()[0]
            self.assertAlmostEqual(magnitude[0], 0.0)                   # there should only be very little dc offset
            invmagnitude = numpy.divide(1.0, magnitude[1:-1])
            sqrtinvmagnitude = tuple(numpy.sqrt(invmagnitude))
            derivative = sumpf.helper.differentiate(sqrtinvmagnitude)
            self.assertAlmostEqual(min(derivative), max(derivative))    # the magnitude of the spectrum should fall with a rate of 1/f^2
            output = rms.GetOutput()
            self.assertEqual(output.GetLabels()[0], "Red Noise")        # the label for the channel has to be "Red Noise"
            self.assertEqual(len(output), length)                       # the length of the generated sequence should be set correctly
            value = output.GetChannels()[0][0]
            rmss.append(value)
            avg.Add(value)
        average = avg.GetAverage()
        for i in rmss:
            self.assertAlmostEqual(i, average, 2)                       # the RMS value of the noise should not change with different signal lengths
        self.assertGreater(average, 0.4)                                # the RMS value of the noise should be between 0.4 and 0.5
        self.assertLess(average, 0.5)                                   # the RMS value of the noise should be between 0.4 and 0.5

    @unittest.skipUnless(sumpf.config.get("run_time_variant_tests"), "Tests which are testing random numbers are skipped")
    def test_uniform_distribution(self):
        """
        Tests the noise with uniform distribution.
        """
        length = 1000
        gen = sumpf.modules.NoiseGenerator(distribution=sumpf.modules.NoiseGenerator.UniformDistribution(), samplingrate=48000, length=length)
        minimum = -1.0  # the default interval should be (-1.0, 1.0)
        maximum = 1.0   #   "
        for r in range(2):
            intervals_count = 5
            intervals = [0] * intervals_count
            signal = gen.GetSignal()
            self.assertEqual(len(signal), length)                                   # the length of the generated sequence should be set correctly
            self.assertEqual(signal.GetLabels()[0], "Noise")                        # the label for the channel has to be "Noise"
            for s in signal.GetChannels()[0]:
                self.assertGreater(s, minimum)                                      # all samples must be in the interval (minimum, maximum)
                self.assertLess(s, maximum)                                         # all samples must be in the interval (minimum, maximum)
                for i in range(1, intervals_count + 1):
                    if s < minimum + i * ((maximum - minimum) / intervals_count):
                        intervals[i - 1] += 1
                        break
            normalized = tuple(numpy.multiply(intervals, float(intervals_count) / float(length)))
            self.assertGreater(min(normalized) / max(normalized), 0.5 ** 0.5)
            minimum = 3.7
            maximum = 5.4
            gen.SetDistribution(sumpf.modules.NoiseGenerator.UniformDistribution(minimum, maximum))

    @unittest.skipUnless(sumpf.config.get("run_time_variant_tests"), "Tests which are testing random numbers are skipped")
    def test_gaussian_distribution(self):
        """
        Tests the noise with gaussian distribution.
        """
        length = 2 ** 18
        gen = sumpf.modules.NoiseGenerator(distribution=sumpf.modules.NoiseGenerator.GaussianDistribution(), samplingrate=48000, length=length)
        mean = 0.0                  # the default mean should be 0.0
        standard_deviation = 1.0    # the default standard deviation should be 1.0
        for r in range(0, 2):
            meansum = 0.0
            devisum = 0.0
            signal = gen.GetSignal()
            self.assertEqual(len(signal), length)                                       # the length of the generated sequence should be set correctly
            self.assertEqual(signal.GetLabels()[0], "Noise")                            # the label for the channel has to be "Noise"
            for s in signal.GetChannels()[0]:
                meansum += s
                devisum += (s - mean) ** 2
            self.assertAlmostEqual(meansum / length, mean, 2)                           # setting the mean should have worked
            self.assertAlmostEqual((devisum / length) ** 0.5, standard_deviation, 2)    # setting the standard deviation should have worked
            mean = -1.4
            standard_deviation = 0.6
            gen.SetDistribution(sumpf.modules.NoiseGenerator.GaussianDistribution(mean=mean, standard_deviation=standard_deviation))

    def test_seed(self):
        """
        Tests if seeding the random number generator works.
        """
        gen = sumpf.modules.NoiseGenerator(distribution=sumpf.modules.NoiseGenerator.UniformDistribution(), seed=1337, samplingrate=48000, length=5)
        channel = gen.GetSignal().GetChannels()[0]
        self.assertEqual(channel, (0.23550571390294128, 0.06653114721000164, -0.26830328150124894, 0.1715747078045431, -0.6686254326224383))
        gen.SetDistribution(sumpf.modules.NoiseGenerator.GaussianDistribution())
        gen.Seed(42)
        channel = gen.GetSignal().GetChannels()[0]
        self.assertEqual(channel, (-0.14409032957792836, -0.1729036003315193, -0.11131586156766246, 0.7019837250988631, -0.12758828378288709))

    def test_caching(self):
        """
        Tests if the noise is recalculated according to the caching settings for
        the output connector.
        """
        gen = sumpf.modules.NoiseGenerator(distribution=sumpf.modules.NoiseGenerator.GaussianDistribution(), samplingrate=48000, length=10)
        noise1 = gen.GetSignal()
        noise2 = gen.GetSignal()
        gen.Recalculate()
        noise3 = gen.GetSignal()
        if sumpf.config.get("caching"):
            self.assertEqual(noise1, noise2)
        else:
            self.assertNotEqual(noise1, noise2)
        self.assertNotEqual(noise1, noise3)
        self.assertNotEqual(noise2, noise3)

    def test_connectors(self):
        """
        Tests if the connectors are properly decorated.
        """
        gen = sumpf.modules.NoiseGenerator()
        self.assertEqual(gen.SetLength.GetType(), int)
        self.assertEqual(gen.SetSamplingRate.GetType(), float)
        self.assertEqual(gen.SetDistribution.GetType(), sumpf.internal.Distribution)
        self.assertEqual(gen.GetSignal.GetType(), sumpf.Signal)
        common.test_connection_observers(testcase=self,
                                         inputs=[gen.SetLength, gen.SetSamplingRate, gen.SetDistribution, gen.Recalculate],
                                         noinputs=[],
                                         output=gen.GetSignal)

