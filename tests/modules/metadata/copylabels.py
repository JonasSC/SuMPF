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


class ConnectionTester(object):
    @sumpf.Output(sumpf.Signal)
    def GetSignal(self):
        return sumpf.Signal(channels=((1.0, 2.0, 3.0), (3.0, 2.0, 1.0)), samplingrate=17.0, labels=("signal 1", "signal 2"))

    @sumpf.Output(sumpf.Spectrum)
    def GetSpectrum(self):
        return sumpf.Spectrum(channels=((1.0, 2.0, 3.0), (3.0, 2.0, 1.0)), resolution=17.0, labels=("spectrum 1", "spectrum 2"))

    @sumpf.Input(sumpf.Signal)
    def SetSignal(self, signal):
        self.signal = signal

    @sumpf.Input(sumpf.Spectrum)
    def SetSpectrum(self, spectrum):
        self.spectrum = spectrum



class TestCopyLabels(unittest.TestCase):
    """
    A TestCase for the CopyLabelsToSignal and CopyLabelsToSpectrum modules.
    """
    def test_copy_label_to_signal(self):
        """
        Tests if the CopyLabelsToSignal module works as expected.
        """
        data_signal = sumpf.Signal(channels=((1.0, 2.0, 3.0), (3.0, 2.0, 1.0)), samplingrate=17.0, labels=("data 1", "data 2"))
        label_signal1 = sumpf.Signal(channels=((3.0, 2.0, 1.0), (1.0, 2.0, 3.0)), samplingrate=17.0, labels=("label 1.1", "label 1.2"))
        label_signal2 = sumpf.Signal(channels=((3.0, 2.0), (1.0, 0.0)), samplingrate=13.0, labels=("label 2.1", "label 2.2"))
        label_signal3 = sumpf.Signal(channels=((3.0, 2.0, 1.0), (0.0, -1.0, 0.0), (1.0, 2.0, 3.0)), samplingrate=17.0, labels=("label 3.1", "label 3.2", "label 3.3"))
        label_signal4 = sumpf.Signal(channels=((3.0, 2.0, 1.0),), samplingrate=17.0, labels=("label 4.1",))
        label_signal5 = sumpf.Signal(channels=((3.0, 2.0, 1.0),), samplingrate=17.0, labels=())
        label_spectrum = sumpf.Spectrum(channels=((1.0, 0.0, 0.0), (1.0, 0.0, 1.0)), resolution=42.0, labels=("spectrum 1", "spectrum 2"))
        clts = sumpf.modules.CopyLabelsToSignal()
        self.assertEqual(clts.GetOutput().GetChannels(), sumpf.Signal().GetChannels())          # if no signal has been given, everything shall be set to default
        self.assertEqual(clts.GetOutput().GetSamplingRate(), sumpf.Signal().GetSamplingRate())
        self.assertEqual(clts.GetOutput().GetLabels(), sumpf.Signal().GetLabels())
        clts.SetDataInput(data_signal)
        self.assertEqual(clts.GetOutput().GetChannels(), data_signal.GetChannels())             # if no label signal has been given, everything shall be taken from the data signal
        self.assertEqual(clts.GetOutput().GetSamplingRate(), data_signal.GetSamplingRate())
        self.assertEqual(clts.GetOutput().GetLabels(), data_signal.GetLabels())
        clts.SetLabelInput(label_signal1)
        self.assertEqual(clts.GetOutput().GetChannels(), data_signal.GetChannels())             # if a label signal has been given, the data shall still be taken from the data signal
        self.assertEqual(clts.GetOutput().GetSamplingRate(), data_signal.GetSamplingRate())
        self.assertEqual(clts.GetOutput().GetLabels(), label_signal1.GetLabels())               # the labels shall be taken from the label signal
        clts.SetLabelInput(label_signal2)
        self.assertEqual(clts.GetOutput().GetLabels(), label_signal2.GetLabels())               # the label signal has not to be compatible to the data signal
        clts.SetLabelInput(label_signal3)
        self.assertEqual(clts.GetOutput().GetLabels(), label_signal3.GetLabels()[0:2])          # if the label signal has more labels than the data signal has channels, only the first labels shall be taken
        clts.SetLabelInput(label_signal4)
        self.assertEqual(clts.GetOutput().GetLabels(), (label_signal4.GetLabels()[0], None))    # if the label signal less labels than the data signal has channels, only the first channels of the relabeled signal shall be labeled. The other channel's labels shall not be labeled by the data signal's label
        clts.SetLabelInput(label_signal5)
        self.assertEqual(clts.GetOutput().GetLabels(), (None, None))                            # if the label signal no labels, the output signal shall have no labels aswell
        clts.SetLabelInput(label_spectrum)
        self.assertEqual(clts.GetOutput().GetLabels(), label_spectrum.GetLabels())              # other ChannelData instances shall also be allowed as label input
        clts = sumpf.modules.CopyLabelsToSignal(data_input=data_signal)
        self.assertEqual(clts.GetOutput().GetChannels(), data_signal.GetChannels())             # setting the data signal via the constructor should be possible
        self.assertEqual(clts.GetOutput().GetSamplingRate(), data_signal.GetSamplingRate())
        self.assertEqual(clts.GetOutput().GetLabels(), data_signal.GetLabels())
        clts = sumpf.modules.CopyLabelsToSignal(label_input=label_signal1)
        self.assertEqual(clts.GetOutput().GetChannels(), sumpf.Signal().GetChannels())          # setting the label signal via the constructor should be possible
        self.assertEqual(clts.GetOutput().GetSamplingRate(), sumpf.Signal().GetSamplingRate())
        self.assertEqual(clts.GetOutput().GetLabels(), label_signal1.GetLabels()[0:1])
        clts = sumpf.modules.CopyLabelsToSignal(data_input=data_signal, label_input=label_signal1)
        self.assertEqual(clts.GetOutput().GetChannels(), data_signal.GetChannels())             # setting both the data signal and the label signal via the constructor should be possible
        self.assertEqual(clts.GetOutput().GetSamplingRate(), data_signal.GetSamplingRate())
        self.assertEqual(clts.GetOutput().GetLabels(), label_signal1.GetLabels())

    def test_copy_label_to_spectrum(self):
        """
        Tests if the CopyLabelsToSpectrum module works as expected.
        """
        data_spectrum = sumpf.Spectrum(channels=((1.0, 2.0, 3.0), (3.0, 2.0, 1.0)), resolution=17.0, labels=("data 1", "data 2"))
        label_spectrum1 = sumpf.Spectrum(channels=((3.0, 2.0, 1.0), (1.0, 2.0, 3.0)), resolution=17.0, labels=("label 1.1", "label 1.2"))
        label_spectrum2 = sumpf.Spectrum(channels=((3.0, 2.0), (1.0, 0.0)), resolution=13.0, labels=("label 2.1", "label 2.2"))
        label_spectrum3 = sumpf.Spectrum(channels=((3.0, 2.0, 1.0), (0.0, -1.0, 0.0), (1.0, 2.0, 3.0)), resolution=17.0, labels=("label 3.1", "label 3.2", "label 3.3"))
        label_spectrum4 = sumpf.Spectrum(channels=((3.0, 2.0, 1.0),), resolution=17.0, labels=("label 4.1",))
        label_spectrum5 = sumpf.Spectrum(channels=((3.0, 2.0, 1.0),), resolution=17.0, labels=())
        label_signal = sumpf.Signal(channels=((1.0, 0.0, 0.0), (1.0, 0.0, 1.0)), samplingrate=42.0, labels=("spectrum 1", "spectrum 2"))
        clts = sumpf.modules.CopyLabelsToSpectrum()
        self.assertEqual(clts.GetOutput().GetChannels(), sumpf.Spectrum().GetChannels())        # if no signal has been given, everything shall be set to default
        self.assertEqual(clts.GetOutput().GetResolution(), sumpf.Spectrum().GetResolution())
        self.assertEqual(clts.GetOutput().GetLabels(), sumpf.Spectrum().GetLabels())
        clts.SetDataInput(data_spectrum)
        self.assertEqual(clts.GetOutput().GetChannels(), data_spectrum.GetChannels())           # if no label signal has been given, everything shall be taken from the data signal
        self.assertEqual(clts.GetOutput().GetResolution(), data_spectrum.GetResolution())
        self.assertEqual(clts.GetOutput().GetLabels(), data_spectrum.GetLabels())
        clts.SetLabelInput(label_spectrum1)
        self.assertEqual(clts.GetOutput().GetChannels(), data_spectrum.GetChannels())           # if a label signal has been given, the data shall still be taken from the data signal
        self.assertEqual(clts.GetOutput().GetResolution(), data_spectrum.GetResolution())
        self.assertEqual(clts.GetOutput().GetLabels(), label_spectrum1.GetLabels())             # the labels shall be taken from the label signal
        clts.SetLabelInput(label_spectrum2)
        self.assertEqual(clts.GetOutput().GetLabels(), label_spectrum2.GetLabels())             # the label signal has not to be compatible to the data signal
        clts.SetLabelInput(label_spectrum3)
        self.assertEqual(clts.GetOutput().GetLabels(), label_spectrum3.GetLabels()[0:2])        # if the label signal has more labels than the data signal has channels, only the first labels shall be taken
        clts.SetLabelInput(label_spectrum4)
        self.assertEqual(clts.GetOutput().GetLabels(), (label_spectrum4.GetLabels()[0], None))  # if the label signal less labels than the data signal has channels, only the first channels of the relabeled signal shall be labeled. The other channel's labels shall not be labeled by the data signal's label
        clts.SetLabelInput(label_spectrum5)
        self.assertEqual(clts.GetOutput().GetLabels(), (None, None))                            # if the label signal no labels, the output signal shall have no labels aswell
        clts.SetLabelInput(label_signal)
        self.assertEqual(clts.GetOutput().GetLabels(), label_signal.GetLabels())                # other ChannelData instances shall also be allowed as label input
        clts = sumpf.modules.CopyLabelsToSpectrum(data_input=data_spectrum)
        self.assertEqual(clts.GetOutput().GetChannels(), data_spectrum.GetChannels())           # setting the data signal via the constructor should be possible
        self.assertEqual(clts.GetOutput().GetResolution(), data_spectrum.GetResolution())
        self.assertEqual(clts.GetOutput().GetLabels(), data_spectrum.GetLabels())
        clts = sumpf.modules.CopyLabelsToSpectrum(label_input=label_spectrum1)
        self.assertEqual(clts.GetOutput().GetChannels(), sumpf.Spectrum().GetChannels())        # setting the label signal via the constructor should be possible
        self.assertEqual(clts.GetOutput().GetResolution(), sumpf.Spectrum().GetResolution())
        self.assertEqual(clts.GetOutput().GetLabels(), label_spectrum1.GetLabels()[0:1])
        clts = sumpf.modules.CopyLabelsToSpectrum(data_input=data_spectrum, label_input=label_spectrum1)
        self.assertEqual(clts.GetOutput().GetChannels(), data_spectrum.GetChannels())           # setting both the data signal and the label signal via the constructor should be possible
        self.assertEqual(clts.GetOutput().GetResolution(), data_spectrum.GetResolution())
        self.assertEqual(clts.GetOutput().GetLabels(), label_spectrum1.GetLabels())

    def test_connections(self):
        tester1 = ConnectionTester()
        tester2 = ConnectionTester()
        cl_sig = sumpf.modules.CopyLabelsToSignal()
        cl_spk = sumpf.modules.CopyLabelsToSpectrum()
        sumpf.connect(tester1.GetSignal, cl_sig.SetDataInput)
        sumpf.connect(tester1.GetSpectrum, cl_sig.SetLabelInput)
        sumpf.connect(tester1.GetSpectrum, cl_spk.SetDataInput)
        sumpf.connect(tester1.GetSignal, cl_spk.SetLabelInput)
        sumpf.connect(cl_sig.GetOutput, tester2.SetSignal)
        sumpf.connect(cl_spk.GetOutput, tester2.SetSpectrum)
        self.assertEqual(tester2.signal.GetLabels(), tester1.GetSpectrum().GetLabels())
        self.assertEqual(tester2.spectrum.GetLabels(), tester1.GetSignal().GetLabels())

