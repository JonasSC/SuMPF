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


class TestConjugateSpectrum(unittest.TestCase):
    """
    A test case for the ConjugateSpectrum module.
    """
    def test_some_values(self):
        """
        Tests if some values are conjugated correctly.
        """
        spectrum = sumpf.Spectrum(channels=((1.0 + 1.0j, -4j, 12.3),), resolution=37.4, labels=("some values",))
        conjugate = sumpf.Spectrum(channels=((1.0 - 1.0j, 4j, 12.3),), resolution=37.4, labels=("some values",))
        cnj = sumpf.modules.ConjugateSpectrum()
        self.assertEqual(cnj.GetOutput(), sumpf.Spectrum())
        cnj.SetInput(spectrum)
        self.assertEqual(cnj.GetOutput(), conjugate)
        cnj = sumpf.modules.ConjugateSpectrum(spectrum=spectrum)
        self.assertEqual(cnj.GetOutput(), conjugate)

    def test_double_conjugate(self):
        """
        Tests the conjugation of a conjugation is the original Spectrum.
        """
        spectrum = sumpf.Spectrum(channels=((0.0 + 1.0j, 1.0 - 0.0j), (1 + 2j, 3 - 4j)), resolution=66.6, labels=("two", "channels"))
        cnj1 = sumpf.modules.ConjugateSpectrum()
        cnj2 = sumpf.modules.ConjugateSpectrum()
        sumpf.connect(cnj1.GetOutput, cnj2.SetInput)
        cnj1.SetInput(spectrum)
        self.assertEqual(cnj2.GetOutput(), spectrum)

    def test_connectors(self):
        """
        Tests if the connectors are properly decorated.
        """
        cnj = sumpf.modules.ConjugateSpectrum()
        self.assertEqual(cnj.SetInput.GetType(), sumpf.Spectrum)
        self.assertEqual(cnj.GetOutput.GetType(), sumpf.Spectrum)
        common.test_connection_observers(testcase=self,
                                         inputs=[cnj.SetInput],
                                         noinputs=[],
                                         output=cnj.GetOutput)

