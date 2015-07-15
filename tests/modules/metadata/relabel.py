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
import unittest

import sumpf
import _common as common


class TestRelabel(unittest.TestCase):
    """
    A TestCase for the RelabelSignal and RelabelSpectrum modules.
    """
    def test_relabel_signal(self):
        """
        Tests if the RelabelSignal module works as expected.
        """
        signal1 = sumpf.Signal(channels=((1.0, 2.0, 3.0),), samplingrate=17.0, labels=("label 1",))
        signal2 = sumpf.Signal(channels=((3.0, 2.0, 1.0),), samplingrate=13.0, labels=("label 2",))
        rel = sumpf.modules.RelabelSignal()
        self.assertEqual(rel.GetOutput().GetChannels(), sumpf.Signal().GetChannels())
        self.assertEqual(rel.GetOutput().GetSamplingRate(), sumpf.Signal().GetSamplingRate())
        self.assertEqual(rel.GetOutput().GetLabels(), sumpf.Signal().GetLabels())
        rel = sumpf.modules.RelabelSignal(input=signal1)
        self.assertEqual(rel.GetOutput().GetChannels(), signal1.GetChannels())
        self.assertEqual(rel.GetOutput().GetSamplingRate(), signal1.GetSamplingRate())
        self.assertEqual(rel.GetOutput().GetLabels(), signal1.GetLabels())                  # If no labels have been specified, the labels shall be taken from the input
        rel = sumpf.modules.RelabelSignal(labels=("labels 3",))
        self.assertEqual(rel.GetOutput().GetChannels(), sumpf.Signal().GetChannels())
        self.assertEqual(rel.GetOutput().GetSamplingRate(), sumpf.Signal().GetSamplingRate())
        self.assertEqual(rel.GetOutput().GetLabels(), ("labels 3",))
        rel = sumpf.modules.RelabelSignal(input=signal1, labels=("labels 4",))
        self.assertEqual(rel.GetOutput().GetChannels(), signal1.GetChannels())
        self.assertEqual(rel.GetOutput().GetSamplingRate(), signal1.GetSamplingRate())
        self.assertEqual(rel.GetOutput().GetLabels(), ("labels 4",))
        rel.SetInput(signal2)
        self.assertEqual(rel.GetOutput().GetChannels(), signal2.GetChannels())
        self.assertEqual(rel.GetOutput().GetSamplingRate(), signal2.GetSamplingRate())
        self.assertEqual(rel.GetOutput().GetLabels(), ("labels 4",))
        rel.SetLabels(("labels 5",))
        self.assertEqual(rel.GetOutput().GetChannels(), signal2.GetChannels())
        self.assertEqual(rel.GetOutput().GetSamplingRate(), signal2.GetSamplingRate())
        self.assertEqual(rel.GetOutput().GetLabels(), ("labels 5",))

    def test_relabel_spectrum(self):
        """
        Tests if the RelabelSpectrum module works as expected.
        """
        spectrum1 = sumpf.Spectrum(channels=((1.0, 2.0, 3.0),), resolution=17.0, labels=("label 1",))
        spectrum2 = sumpf.Spectrum(channels=((3.0, 2.0, 1.0),), resolution=13.0, labels=("label 2",))
        rel = sumpf.modules.RelabelSpectrum()
        self.assertEqual(rel.GetOutput().GetChannels(), sumpf.Spectrum().GetChannels())
        self.assertEqual(rel.GetOutput().GetResolution(), sumpf.Spectrum().GetResolution())
        self.assertEqual(rel.GetOutput().GetLabels(), sumpf.Spectrum().GetLabels())
        rel = sumpf.modules.RelabelSpectrum(input=spectrum1)
        self.assertEqual(rel.GetOutput().GetChannels(), spectrum1.GetChannels())
        self.assertEqual(rel.GetOutput().GetResolution(), spectrum1.GetResolution())
        self.assertEqual(rel.GetOutput().GetLabels(), spectrum1.GetLabels())                    # If no labels have been specified, the labels shall be taken from the input
        rel = sumpf.modules.RelabelSpectrum(labels=("labels 3",))
        self.assertEqual(rel.GetOutput().GetChannels(), sumpf.Spectrum().GetChannels())
        self.assertEqual(rel.GetOutput().GetResolution(), sumpf.Spectrum().GetResolution())
        self.assertEqual(rel.GetOutput().GetLabels(), ("labels 3",))
        rel = sumpf.modules.RelabelSpectrum(input=spectrum1, labels=("labels 4",))
        self.assertEqual(rel.GetOutput().GetChannels(), spectrum1.GetChannels())
        self.assertEqual(rel.GetOutput().GetResolution(), spectrum1.GetResolution())
        self.assertEqual(rel.GetOutput().GetLabels(), ("labels 4",))
        rel.SetInput(spectrum2)
        self.assertEqual(rel.GetOutput().GetChannels(), spectrum2.GetChannels())
        self.assertEqual(rel.GetOutput().GetResolution(), spectrum2.GetResolution())
        self.assertEqual(rel.GetOutput().GetLabels(), ("labels 4",))
        rel.SetLabels(("labels 5",))
        self.assertEqual(rel.GetOutput().GetChannels(), spectrum2.GetChannels())
        self.assertEqual(rel.GetOutput().GetResolution(), spectrum2.GetResolution())
        self.assertEqual(rel.GetOutput().GetLabels(), ("labels 5",))

    def test_connectors(self):
        """
        Tests if the connectors are properly decorated.
        """
        # SelectSpectrum
        rel = sumpf.modules.RelabelSignal()
        self.assertEqual(rel.SetInput.GetType(), sumpf.Signal)
        self.assertEqual(rel.SetLabels.GetType(), collections.Iterable)
        self.assertEqual(rel.GetOutput.GetType(), sumpf.Signal)
        common.test_connection_observers(testcase=self,
                                         inputs=[rel.SetInput, rel.SetLabels],
                                         noinputs=[],
                                         output=rel.GetOutput)
        # SelectSpectrum
        rel = sumpf.modules.RelabelSpectrum()
        self.assertEqual(rel.SetInput.GetType(), sumpf.Spectrum)
        self.assertEqual(rel.SetLabels.GetType(), collections.Iterable)
        self.assertEqual(rel.GetOutput.GetType(), sumpf.Spectrum)
        common.test_connection_observers(testcase=self,
                                         inputs=[rel.SetInput, rel.SetLabels],
                                         noinputs=[],
                                         output=rel.GetOutput)

