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

import os
import unittest
import shutil
import tempfile

import sumpf
import _common as common

@unittest.skipUnless(sumpf.config.get("write_to_disk"), "Tests that write to disk are skipped")
@unittest.skipUnless(common.lib_available("numpy"), "These tests require the library 'numpy' to be available.")
class TestConvertFile(unittest.TestCase):
    """
    Tests the ConvertFile Example.
    """

    @unittest.skipUnless(sumpf.config.get("run_long_tests"), "Long tests are skipped")
    @unittest.skipUnless(common.lib_available("scikits.audiolab"), "This test requires the library 'scikits.audiolab'")
    def test_convert_file(self):
        """
        Tests if the ConvertFile example works as documented.
        """
        filename = "file"
        tempdir = tempfile.mkdtemp()
        try:
            pathT = os.path.join(tempdir, filename) + "T"
            pathF = os.path.join(tempdir, filename) + "F"
            gen = sumpf.modules.SineWaveGenerator()
            amp = sumpf.modules.AmplifySignal(input=gen.GetSignal(), factor=0.6)
            mrg = sumpf.modules.MergeSignals()
            mrg.AddInput(gen.GetSignal())
            mrg.AddInput(amp.GetOutput())
            signal = mrg.GetOutput()
            fft = sumpf.modules.FourierTransform(signal=signal)
            ifft = sumpf.modules.InverseFourierTransform(spectrum=fft.GetSpectrum())
            # create some test files and read their data
            sumpf.modules.SignalFile(filename=pathT, signal=signal, format=sumpf.modules.SignalFile.NUMPY_NPZ)
            npz_T = sumpf.modules.SignalFile(filename=pathT, format=sumpf.modules.SignalFile.NUMPY_NPZ).GetSignal()
            sumpf.modules.SignalFile(filename=pathT, signal=signal, format=sumpf.modules.SignalFile.WAV_FLOAT)
            wav_f = sumpf.modules.SignalFile(filename=pathT, format=sumpf.modules.SignalFile.WAV_FLOAT).GetSignal()
            os.remove(pathT + ".wav")
            sumpf.modules.SignalFile(filename=pathT, signal=signal, format=sumpf.modules.SignalFile.WAV_INT)
            wav_i = sumpf.modules.SignalFile(filename=pathT, format=sumpf.modules.SignalFile.WAV_INT).GetSignal()
            os.remove(pathT + ".wav")
            sumpf.modules.SpectrumFile(filename=pathF, spectrum=fft.GetSpectrum(), format=sumpf.modules.SpectrumFile.NUMPY_NPZ)
            npz_F = sumpf.modules.SpectrumFile(filename=pathF, format=sumpf.modules.SpectrumFile.NUMPY_NPZ).GetSpectrum()
            os.remove(pathF + ".npz")
            # test converting a npz Signal file to floating point wav
            sumpf.examples.ConvertFile(input=pathT + ".npz", output=pathT + ".wav")
            output = sumpf.modules.SignalFile(filename=pathT, format=sumpf.modules.SignalFile.WAV_FLOAT).GetSignal()
            self.assertEqual(output, wav_f)
            # test converting a npz Signal file to integer wav
            os.remove(pathT + ".wav")
            sumpf.examples.ConvertFile(input=pathT + ".npz", format="WAV_INT")
            output = sumpf.modules.SignalFile(filename=pathT, format=sumpf.modules.SignalFile.WAV_INT).GetSignal()
            self.assertEqual(output, wav_i)
            # test converting a npz Signal file to a npz Spectrum file
            sumpf.examples.ConvertFile(input=pathT + ".npz", output=pathF + ".npz")
            output = sumpf.modules.SpectrumFile(filename=pathF, format=sumpf.modules.SpectrumFile.NUMPY_NPZ).GetSpectrum()
            self.assertEqual(output, npz_F)
            # test converting a npz Spectrum file to a npz Signal file
            sumpf.examples.ConvertFile(input=pathF + ".npz", output=pathT + ".npz")
            output = sumpf.modules.SignalFile(filename=pathT, format=sumpf.modules.SignalFile.NUMPY_NPZ).GetSignal()
            self.assertEqual(output, ifft.GetSignal())
            # test converting a wav Signal file to a npz Signal file
            sumpf.examples.ConvertFile(input=pathT + ".wav", output=pathT + ".npz")
            output = sumpf.modules.SignalFile(filename=pathT, format=sumpf.modules.SignalFile.NUMPY_NPZ).GetSignal()
            self.assertEqual(output, wav_i)
        finally:
            shutil.rmtree(tempdir)

    @unittest.skipUnless(sumpf.config.get("run_long_tests"), "Long tests are skipped")
    def test_errors(self):
        """
        tests if all errors are raised as expected
        """
        tempdir = tempfile.mkdtemp()
        try:
            path1 = os.path.join(tempdir, "file1")
            path2 = os.path.join(tempdir, "file2")
            with open(path2, "w") as f:
                f.write("test")
            gen = sumpf.modules.SineWaveGenerator()
            # create a test file
            sumpf.modules.SignalFile(filename=path1, signal=gen.GetSignal(), format=sumpf.modules.SignalFile.NUMPY_NPZ)
            self.assertRaises(IOError, sumpf.examples.ConvertFile, **{"input": path1 + "X.npz"})
            self.assertRaises(IOError, sumpf.examples.ConvertFile, **{"input": path2})
            self.assertRaises(IOError, sumpf.examples.ConvertFile, **{"input": path1 + ".npz", "output": "_GARBAGE_"})
            self.assertRaises(IOError, sumpf.examples.ConvertFile, **{"input": path1 + ".npz", "format": "_GARBAGE_"})
        finally:
            shutil.rmtree(tempdir)

