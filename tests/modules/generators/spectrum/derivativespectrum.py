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


class TestDerivativeSpectrumGenerator(unittest.TestCase):
    """
    A TestCase for the DerivativeSpectrumGenerator module.
    """
    @unittest.skipUnless(common.lib_available("numpy"), "This test requires the library 'numpy' to be available.")
    def test_function(self):
        """
        Tests the generator's output.
        """
        # set up a processing chain to calculate a derivative in the frequency domain.
        properties = sumpf.modules.ChannelDataProperties(signal_length=2 ** 9, samplingrate=11025)
        generator = sumpf.modules.SweepGenerator(start_frequency=1.0, stop_frequency=4000.0)
        sumpf.connect(properties.GetSamplingRate, generator.SetSamplingRate)
        sumpf.connect(properties.GetSignalLength, generator.SetLength)
        fft = sumpf.modules.FourierTransform()
        sumpf.connect(generator.GetSignal, fft.SetSignal)
        filtergenerator = sumpf.modules.DerivativeSpectrumGenerator()
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

    def test_connectors(self):
        """
        Tests if the connectors are properly decorated.
        """
        gen = sumpf.modules.DerivativeSpectrumGenerator()
        self.assertEqual(gen.SetLength.GetType(), int)
        self.assertEqual(gen.SetResolution.GetType(), float)
        self.assertEqual(gen.SetMaximumFrequency.GetType(), float)
        self.assertEqual(gen.GetSpectrum.GetType(), sumpf.Spectrum)
        common.test_connection_observers(testcase=self,
                                         inputs=[gen.SetLength, gen.SetResolution, gen.SetMaximumFrequency],
                                         noinputs=[],
                                         output=gen.GetSpectrum)

