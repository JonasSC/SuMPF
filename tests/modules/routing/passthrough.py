# SuMPF - Sound using a Monkeyforest-like processing framework
# Copyright (C) 2012-2018 Jonas Schulte-Coerne
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


class TestPassThrough(unittest.TestCase):
    """
    A test case for the SelectSignal and SelectSpectrum modules.
    """
    def test_pass_through_signal(self):
        """
        Tests the PassThroughSignal class.
        """
        signal1 = sumpf.Signal(channels=((1.0, 1.0),))
        signal2 = sumpf.Signal(channels=((2.0, 2.0),))
        pt = sumpf.modules.PassThroughSignal()
        self.assertEqual(pt.GetSignal(), sumpf.Signal())
        pt.SetSignal(signal1)
        self.assertIs(pt.GetSignal(), signal1)
        self.assertIs(sumpf.modules.PassThroughSignal(signal=signal2).GetSignal(), signal2)

    def test_pass_through_spectrum(self):
        """
        Tests the PassThroughSpectrum class.
        """
        spectrum1 = sumpf.Spectrum(channels=((1.0, 1.0),))
        spectrum2 = sumpf.Spectrum(channels=((2.0, 2.0),))
        pt = sumpf.modules.PassThroughSpectrum()
        self.assertEqual(pt.GetSpectrum(), sumpf.Spectrum())
        pt.SetSpectrum(spectrum1)
        self.assertIs(pt.GetSpectrum(), spectrum1)
        self.assertIs(sumpf.modules.PassThroughSpectrum(spectrum=spectrum2).GetSpectrum(), spectrum2)

    def test_connectors(self):
        """
        Tests if the connectors are properly decorated.
        """
        # PassThroughSignal
        pt = sumpf.modules.PassThroughSignal()
        self.assertEqual(pt.SetSignal.GetType(), sumpf.Signal)
        self.assertEqual(pt.GetSignal.GetType(), sumpf.Signal)
        common.test_connection_observers(testcase=self,
                                         inputs=[pt.SetSignal],
                                         noinputs=[],
                                         output=pt.GetSignal)
        # PassThroughSpectrum
        pt = sumpf.modules.PassThroughSpectrum()
        self.assertEqual(pt.SetSpectrum.GetType(), sumpf.Spectrum)
        self.assertEqual(pt.GetSpectrum.GetType(), sumpf.Spectrum)
        common.test_connection_observers(testcase=self,
                                         inputs=[pt.SetSpectrum],
                                         noinputs=[],
                                         output=pt.GetSpectrum)

