# SuMPF - Sound using a Monkeyforest-like processing framework
# Copyright (C) 2012-2016 Jonas Schulte-Coerne
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
    @unittest.skipUnless(common.lib_available("soundfile") or common.lib_available("scikits.audiolab"), "This test requires the library 'scikits.audiolab'")
    def test_convert_file(self):
        """
        Tests if the ConvertFile example works as documented.
        """
        filename = "file"
        tempdir = tempfile.mkdtemp()
        try:
            pathT = os.path.join(tempdir, filename + "T")
            pathF = os.path.join(tempdir, filename + "F")
            gen = sumpf.modules.SineWaveGenerator(length=4)
            amp = sumpf.modules.Multiply(value1=gen.GetSignal(), value2=0.6)
            mrg = sumpf.modules.MergeSignals()
            mrg.AddInput(gen.GetSignal())
            mrg.AddInput(amp.GetResult())
            signal = mrg.GetOutput()
            fft = sumpf.modules.FourierTransform(signal=signal)
            ifft = sumpf.modules.InverseFourierTransform(spectrum=fft.GetSpectrum())
            # create some test files and read their data
            sumpf.modules.SaveSignal(filename=pathT + ".npz", signal=signal, file_format=sumpf.modules.SaveSignal.NUMPY_NPZ)
            sumpf.modules.SaveSignal(filename=pathT + ".asc", signal=signal, file_format=sumpf.modules.SaveSignal.TEXT)
            sumpf.modules.SaveSignal(filename=pathT + ".wav", signal=signal, file_format=sumpf.modules.SaveSignal.WAV_FLOAT)
            sumpf.modules.SaveSpectrum(filename=pathF + ".asc", spectrum=fft.GetSpectrum(), file_format=sumpf.modules.SaveSpectrum.TEXT_I)
            wav_f = sumpf.modules.LoadSignal(filename=pathT + ".wav").GetSignal()
            os.remove(pathT + ".wav")
            sumpf.modules.SaveSignal(filename=pathT + ".wav", signal=signal, file_format=sumpf.modules.SaveSignal.WAV_INT)
            wav_i = sumpf.modules.LoadSignal(filename=pathT + ".wav").GetSignal()
            os.remove(pathT + ".wav")
            # test converting a npz Signal file to floating point wav
            sumpf.examples.ConvertFile(input=pathT + ".npz", output=pathT + ".wav")
            output = sumpf.modules.LoadSignal(filename=pathT + ".wav").GetSignal()
            self.assertEqual(output, wav_f)
            os.remove(pathT + ".wav")
            # test converting a npz Signal file to integer wav
            sumpf.examples.ConvertFile(input=pathT + ".npz", file_format="WAV_INT")
            output = sumpf.modules.LoadSignal(filename=pathT + ".wav").GetSignal()
            self.assertEqual(output, wav_i)
            # test converting a npz Signal file to a npz Spectrum file
            sumpf.examples.ConvertFile(input=pathT + ".npz", output=pathF + ".npz")
            output = sumpf.modules.LoadSpectrum(filename=pathF + ".npz").GetSpectrum()
            self.assertEqual(output, fft.GetSpectrum())
            # test converting a npz Spectrum file to a npz Signal file
            sumpf.examples.ConvertFile(input=pathF + ".npz", output=pathT + ".npz")
            output = sumpf.modules.LoadSignal(filename=pathT + ".npz").GetSignal()
            self.assertEqual(output, ifft.GetSignal())
            # test converting a wav Signal file to a npz Signal file
            sumpf.examples.ConvertFile(input=pathT + ".wav", output=pathT + ".npz")
            output = sumpf.modules.LoadSignal(filename=pathT + ".npz").GetSignal()
            self.assertEqual(output, wav_i)
            # test converting a text Signal to a text Spectrum
            sumpf.examples.ConvertFile(input=pathT + ".asc", output=pathF + ".asc")
            output = sumpf.modules.LoadSpectrum(filename=pathF + ".asc").GetSpectrum()
            self.assertEqual(output, fft.GetSpectrum())
            # test converting a npz Signal to a text Signal
            os.remove(pathT + ".asc")
            sumpf.modules.SaveSignal(filename=pathT + ".npz", signal=signal, file_format=sumpf.modules.SaveSignal.NUMPY_NPZ)
            sumpf.examples.ConvertFile(input=pathT + ".npz", output=pathT + ".asc")
            output = sumpf.modules.LoadSignal(filename=pathT + ".asc").GetSignal()
            self.assertEqual(output, signal)
            # test converting a text Spectrum to a npz Spectrum
            sumpf.examples.ConvertFile(input=pathF + ".asc", output=pathF + ".npz")
            output = sumpf.modules.LoadSpectrum(filename=pathF + ".npz").GetSpectrum()
            self.assertEqual(output, fft.GetSpectrum())
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
            sumpf.modules.SaveSignal(filename=path1, signal=gen.GetSignal(), file_format=sumpf.modules.SaveSignal.NUMPY_NPZ)
            self.assertRaises(IOError, sumpf.examples.ConvertFile, **{"input": path1 + "X.npz"})
            self.assertRaises(IOError, sumpf.examples.ConvertFile, **{"input": path2})
            self.assertRaises(IOError, sumpf.examples.ConvertFile, **{"input": path1 + ".npz", "output": "_GARBAGE_"})
            self.assertRaises(IOError, sumpf.examples.ConvertFile, **{"input": path1 + ".npz", "file_format": "_GARBAGE_"})
        finally:
            shutil.rmtree(tempdir)

