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


class TestSelect(unittest.TestCase):
    """
    A test case for the SelectSignal and SelectSpectrum modules.
    """
    def test_select_signal(self):
        """
        Tests the SelectSignal module.
        """
        signal1 = sumpf.Signal(channels=((1.0, 1.0),))
        signal2 = sumpf.Signal(channels=((2.0, 2.0),))
        sls = sumpf.modules.SelectSignal()
        self.assertEqual(sls.GetOutput().GetChannels(), sumpf.Signal().GetChannels())   # when created without parameters, the first Signal shall be an empty Signal
        sls.SetSelection(2)
        self.assertEqual(sls.GetOutput().GetChannels(), sumpf.Signal().GetChannels())   # when created without parameters, the second Signal shall be an empty Signal
        sls = sumpf.modules.SelectSignal(input1=signal1, input2=signal2)
        self.assertEqual(sls.GetOutput().GetChannels(), signal1.GetChannels())          # the first Signal shall be selected by default
        sls.SetSelection(2)
        self.assertEqual(sls.GetOutput().GetChannels(), signal2.GetChannels())          # setting the selection should have worked
        sls.SetInput1(signal2)
        sls.SetInput2(signal1)
        self.assertEqual(sls.GetOutput().GetChannels(), signal1.GetChannels())          # setting the second Signal should have worked
        sls.SetSelection(1)
        self.assertEqual(sls.GetOutput().GetChannels(), signal2.GetChannels())          # setting the first Signal should have worked
        sls = sumpf.modules.SelectSignal(input1=signal1, input2=signal2, selection=2)
        self.assertEqual(sls.GetOutput().GetChannels(), signal2.GetChannels())          # setting the selection by constructor parameter should also be possible
        self.assertRaises(ValueError, sls.SetSelection, 3)                              # setting an invalid selection via SetSelection should raise an error
        self.assertRaises(ValueError, sumpf.modules.SelectSignal, signal1, signal2, 3)          # setting an invalid selection via the constructor should raise an error

    def test_select_spectrum(self):
        """
        Tests the SelectSpectrum module.
        """
        spectrum1 = sumpf.Spectrum(channels=((1.0, 1.0),))
        spectrum2 = sumpf.Spectrum(channels=((2.0, 2.0),))
        sls = sumpf.modules.SelectSpectrum()
        self.assertEqual(sls.GetOutput().GetChannels(), sumpf.Spectrum().GetChannels()) # if created without parameters, the first Spectrum shall be an empty Spectrum
        sls.SetSelection(2)
        self.assertEqual(sls.GetOutput().GetChannels(), sumpf.Spectrum().GetChannels()) # if created without parameters, the second Spectrum shall be an empty Spectrum
        sls = sumpf.modules.SelectSpectrum(input1=spectrum1, input2=spectrum2)
        self.assertEqual(sls.GetOutput().GetChannels(), spectrum1.GetChannels())        # the first Spectrum shall be selected by default
        sls.SetSelection(2)
        self.assertEqual(sls.GetOutput().GetChannels(), spectrum2.GetChannels())        # setting the selection should have worked
        sls.SetInput1(spectrum2)
        sls.SetInput2(spectrum1)
        self.assertEqual(sls.GetOutput().GetChannels(), spectrum1.GetChannels())        # setting the second Spectrum should have worked
        sls.SetSelection(1)
        self.assertEqual(sls.GetOutput().GetChannels(), spectrum2.GetChannels())        # setting the first Spectrum should have worked
        sls = sumpf.modules.SelectSpectrum(input1=spectrum1, input2=spectrum2, selection=2)
        self.assertEqual(sls.GetOutput().GetChannels(), spectrum2.GetChannels())        # setting the selection by constructor parameter should also be possible
        self.assertRaises(ValueError, sls.SetSelection, 3)                              # setting an invalid selection via SetSelection should raise an error
        self.assertRaises(ValueError, sumpf.modules.SelectSpectrum, spectrum1, spectrum2, 3)    # setting an invalid selection via the constructor should raise an error

    def test_connectors(self):
        """
        Tests if the connectors are properly decorated.
        """
        # SelectSignal
        sls = sumpf.modules.SelectSignal()
        self.assertEqual(sls.SetInput1.GetType(), sumpf.Signal)
        self.assertEqual(sls.SetInput2.GetType(), sumpf.Signal)
        self.assertEqual(sls.SetSelection.GetType(), int)
        self.assertEqual(sls.GetOutput.GetType(), sumpf.Signal)
        common.test_connection_observers(testcase=self,
                                         inputs=[sls.SetInput1, sls.SetInput2, sls.SetSelection],
                                         noinputs=[],
                                         output=sls.GetOutput)
        # SelectSpectrum
        sls = sumpf.modules.SelectSpectrum()
        self.assertEqual(sls.SetInput1.GetType(), sumpf.Spectrum)
        self.assertEqual(sls.SetInput2.GetType(), sumpf.Spectrum)
        self.assertEqual(sls.SetSelection.GetType(), int)
        self.assertEqual(sls.GetOutput.GetType(), sumpf.Spectrum)
        common.test_connection_observers(testcase=self,
                                         inputs=[sls.SetInput1, sls.SetInput2, sls.SetSelection],
                                         noinputs=[],
                                         output=sls.GetOutput)

