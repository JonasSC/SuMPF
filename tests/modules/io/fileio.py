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

import hashlib
import inspect
import os
import shutil
import tempfile
import time
import unittest

import sumpf
import _common as common


class Tester(object):
    def __init__(self):
        self.triggered = False

    @sumpf.Trigger()
    def Trigger(self):
        self.triggered = True



class TestFileIO(unittest.TestCase):
    """
    A TestCase for saving and loading Signals and Spectrums.
    """
    @unittest.skipUnless(sumpf.config.get("write_to_disk"), "Tests that write to disk are skipped")
    def test_signal_files(self):
        """
        Tests if the SaveSignal and LoadSignal classes work as expected.
        """
        tempdir = tempfile.mkdtemp()
        filename = "TestFileIO1"
        signal1 = sumpf.Signal(channels=((0.0, 0.1, 0.2, 0.3), (0.4, 0.5, 0.6, 0.7)), samplingrate=23.0, labels=("one", "two"))
        signal2 = sumpf.Signal(channels=((-0.1, -0.2, -0.3), (-0.4, -0.5, -0.6), (-0.7, -0.8, -0.9)), samplingrate=25.0, labels=("three", "four", "five"))
        formats = {}    #                        exact,labels,exact samplingrate
        formats[sumpf.modules.SaveSignal.TEXT] = (True, True, None)
        if common.lib_available("numpy"):
            formats[sumpf.modules.SaveSignal.NUMPY_NPZ] = (True, True, True)
            if common.lib_available("scikits.audiolab") or common.lib_available("soundfile"):
                formats[sumpf.modules.SaveSignal.AIFF_FLOAT] = (False, False, False)
                formats[sumpf.modules.SaveSignal.AIFF_INT] = (False, False, False)
                formats[sumpf.modules.SaveSignal.FLAC] = (False, False, False)
                formats[sumpf.modules.SaveSignal.WAV_DOUBLE] = (True, False, False)
                formats[sumpf.modules.SaveSignal.WAV_INT] = (False, False, False)
                formats[sumpf.modules.SaveSignal.WAV_FLOAT] = (False, False, False)
            if common.lib_available("oct2py", dont_import=True):
                if sumpf.config.get("run_long_tests"):
                    formats[sumpf.modules.SaveSignal.MATLAB] = (True, True, True)
        else:
            self.assertNotIn("MATLAB", vars(sumpf.modules.SaveSignal))
        self.assertTrue(set(formats.keys()).issubset(sumpf.modules.SaveSignal.GetFormats()))
        for f in set(formats.keys()) - set(sumpf.modules.SaveSignal.GetFormats()):
            self.assertTrue(f.read_only)
        try:
            for f in formats:
                if sumpf.config.get("run_long_tests"):
                    full_filename = os.path.join(tempdir, filename)
                else:
                    full_filename = os.path.join(tempdir, "%s.%s" % (filename, f.ending))
                format_info = formats[f]
                sumpf.modules.SaveSignal(file_format=f)
                self.assertEqual(os.listdir(tempdir), [])                                               # if no filename was provided, no file should have been written
                sumpf.modules.SaveSignal(filename=full_filename, file_format=f)
                self.assertTrue(os.path.isfile(full_filename))                                          # with a filename provided, a file should have been created
                loaded = sumpf.modules.LoadSignal(filename=full_filename).GetSignal()
                self.__CompareSignals(loaded, sumpf.Signal(), format_info, filename)                    # this file should contain an empty data set
                save = sumpf.modules.SaveSignal(filename=full_filename, signal=signal1, file_format=f)
                load = sumpf.modules.LoadSignal()
                self.assertFalse(load.GetSuccess())
                self.assertEqual(load.GetSignal(), sumpf.Signal())                                      # if no filename was provided, the "loaded" file should be empty
                self.assertFalse(load.GetSuccess())
                load.SetFilename(full_filename)
                self.assertTrue(load.GetSuccess())
                loaded = load.GetSignal()
                self.assertTrue(load.GetSuccess())
                self.__CompareSignals(loaded, signal1, format_info, filename)                           # the existent file should be overwritten
                if sumpf.config.get("run_long_tests"):
                    # test the file monitoring
                    time.sleep(1.01)
                    save.SetSignal(signal2)                                                             # changing the data set should trigger a rewrite of the file
                    self.__CompareSignals(load.GetSignal(), signal1, format_info, filename)             # the file should not be reloaded, because the monitoring for file changes is still deactivated
                    load.SetMonitorFile(True)
                    time.sleep(1.0)
                    self.__CompareSignals(load.GetSignal(), signal2, format_info, filename)             # the file should be reloaded, because it has changed
                os.remove(full_filename)
        finally:
            shutil.rmtree(tempdir)

    @unittest.skipUnless(sumpf.config.get("write_to_disk"), "Tests that write to disk are skipped")
    def test_spectrum_files(self):
        """
        Tests if the SaveSpectrum and LoadSpectrum classes work as expected.
        """
        tempdir = tempfile.mkdtemp()
        filename = os.path.join(tempdir, "TestFileIO1")
        spectrum1 = sumpf.Spectrum(channels=((1.1 + 1.4j, 2.0 + 3.0j), (3.0, 4.0)), resolution=23.0, labels=("one", "two"))
        spectrum2 = sumpf.Spectrum(channels=((5.0, 6.0), (7.0, 8.2 + 2.7j)), resolution=25.0, labels=("three", "four"))
        formats = [sumpf.modules.SaveSpectrum.TEXT_I,
                   sumpf.modules.SaveSpectrum.TEXT_J]
        if common.lib_available("numpy"):
            formats.append(sumpf.modules.SaveSpectrum.NUMPY_NPZ)
            if common.lib_available("oct2py", dont_import=True):
                if sumpf.config.get("run_long_tests"):
                    formats.append(sumpf.modules.SaveSpectrum.MATLAB)
        else:
            self.assertNotIn("MATLAB", vars(sumpf.modules.SaveSpectrum))
        self.assertTrue(set(formats).issubset(sumpf.modules.SaveSpectrum.GetFormats()))
        for f in set(formats) - set(sumpf.modules.SaveSpectrum.GetFormats()):
            self.assertTrue(f.read_only)
        try:
            for f in formats:
                if sumpf.config.get("run_long_tests"):
                    full_filename = filename
                else:
                    full_filename = "%s.%s" % (filename, f.ending)
                sumpf.modules.SaveSpectrum(file_format=f)
                self.assertEqual(os.listdir(tempdir), [])                                           # if no filename was provided, no file should have been written
                sumpf.modules.SaveSpectrum(filename=full_filename, file_format=f)
                self.assertTrue(os.path.isfile(full_filename))                                      # with a filename provided, a file should have been created
                loaded = sumpf.modules.LoadSpectrum(filename=full_filename).GetSpectrum()
                self.assertEqual(loaded, sumpf.Spectrum())                                          # this file should contain an empty data set
                save = sumpf.modules.SaveSpectrum(filename=full_filename, spectrum=spectrum1, file_format=f)
                load = sumpf.modules.LoadSpectrum()
                self.assertFalse(load.GetSuccess())
                self.assertEqual(load.GetSpectrum(), sumpf.Spectrum())                              # if no filename was provided, the "loaded" file should be empty
                self.assertFalse(load.GetSuccess())
                load.SetFilename(full_filename)
                self.assertTrue(load.GetSuccess())
                loaded = load.GetSpectrum()
                self.assertTrue(load.GetSuccess())
                self.assertEqual(loaded, spectrum1)
                if sumpf.config.get("run_long_tests"):
                    time.sleep(1.01)
                    save.SetSpectrum(spectrum2)                                                     # changing the data set should trigger a rewrite of the file
                    self.assertEqual(load.GetSpectrum(), spectrum1)
                    load.SetMonitorFile(True)
                    time.sleep(1.0)
                    self.assertEqual(load.GetSpectrum(), spectrum2)                                 # the file should be reloaded, because it has changed
                os.remove(full_filename)
        finally:
            shutil.rmtree(tempdir)

    @unittest.skipUnless(sumpf.config.get("write_to_disk"), "Tests that write to disk are skipped")
    @unittest.skipUnless(sumpf.config.get("run_long_tests"), "Long tests are skipped")
    @unittest.skipUnless(common.lib_available("numpy"), "This test requires the library 'numpy' to be available.")
    @unittest.skipUnless(common.lib_available("scikits.audiolab"), "Writing lossily compressed files is only available with external libraries")
    def test_lossy_signal_formats(self):
        tempdir = tempfile.mkdtemp()
        try:
            for f in (sumpf.modules.SaveSignal.OGG_VORBIS,):
                if sumpf.config.get("run_long_tests"):
                    ending = "unknown"
                else:
                    ending = f.ending
                # test a rather short signal with more than two channels
                filename = os.path.join(tempdir, "short.%s" % ending)
                reference = sumpf.modules.SineWaveGenerator().GetSignal()
                reference = sumpf.Signal(channels=((0.1, 0.2, 0.3), (0.4, 0.5, 0.6), (0.7, 0.8, 0.9)), samplingrate=44100.0)
                sumpf.modules.SaveSignal(filename=filename, signal=reference, file_format=f)
                self.assertTrue(os.path.isfile(filename))
                loader = sumpf.modules.LoadSignal(filename=filename)
                self.assertTrue(loader.GetSuccess())
                signal = loader.GetSignal()
                relative_error = (signal - reference) / reference
                for c in sumpf.modules.RootMeanSquare(signal=relative_error, integration_time=sumpf.modules.RootMeanSquare.FULL).GetOutput().GetChannels():
                    self.assertLess(c[0], 0.12)
                os.remove(filename)
                # test a loud signal with amplitudes above 1.0 and below -1.0
                filename = os.path.join(tempdir, "loud.%s" % ending)
                reference = sumpf.Signal(channels=((0.1, -2.0, 0.3, 4.0, -0.5, -6.0, 0.7, 8.0, -0.9),), samplingrate=44100.0)
                sumpf.modules.SaveSignal(filename=filename, signal=reference, file_format=f)
                signal = sumpf.modules.LoadSignal(filename=filename).GetSignal()
                relative_error = (signal - reference) / reference
                for s in (relative_error * relative_error).GetChannels()[0]:
                    self.assertLess(s, 0.45)
                os.remove(filename)
        finally:
            shutil.rmtree(tempdir)

    @unittest.skipUnless(sumpf.config.get("write_to_disk"), "Tests that write to disk are skipped")
    def test_load_text_formats(self):
        tempdir = tempfile.mkdtemp()
        try:
            # test a signal, to which zeros must be prepended
            content = "\n".join(("# LABELS:\tfoo\tbar", # labels with a tab after LABELS:
                                 "2.5\t9.3\t-3.3",
                                 " # full line comment",
                                 "2.0\t-23.1\t2.1 # comment after data",
                                 "",
                                 "1.5\t4.3\t9.3",
                                 "   ",
                                 "3.0\t-7.7\t-1.9"))
            signal = 1.0 * sumpf.Signal(channels=((0.0, 0.0, 0.0, 4.3, -23.1, 9.3, -7.7), (0.0, 0.0, 0.0, 9.3, 2.1, -3.3, -1.9)), samplingrate=2.0, labels=("foo", "bar"))  # multiply with 1.0, so the same rounding errors occur as when loading
            filename = os.path.join(tempdir, "signal1.asc")
            with open(filename, "w") as f:
                f.write(content)
            loaded = sumpf.modules.LoadSignal(filename).GetSignal()
            self.assertEqual(loaded, 1.0 * signal)
            # test a signal, from which the first samples must be dropped, because they are in the negative time domain
            content = "\n".join(("-0.5\t9.3",# no labels
                                 "-0.25\t-23.1\t# comment after data",  # tab before comment
                                 "0.25\t-7.7\t",    # trailing tab
                                 "0.5\t2.5",
                                 "0.0\t4.3"))
            signal = 1.0 * sumpf.Signal(channels=((4.3, -7.7, 2.5),), samplingrate=4.0, labels=())  # multiply with 1.0, so the same rounding errors occur as when loading
            filename = os.path.join(tempdir, "signal2.asc")
            with open(filename, "w") as f:
                f.write(content)
            loaded = sumpf.modules.LoadSignal(filename).GetSignal()
            self.assertEqual(loaded, 1.0 * signal)
            # test a spectrum file with j as imaginary unit
            content = "\n".join(("# LABELS: foo\tbar", # labels with a space after LABELS:
                                 " # full line comment",
                                 "",
                                 "2.0\t-23.1-4.7j # comment after data",
                                 "2.5\t9.3+4.9j\t ",                        # trailing tab
                                 "1.5\t4.3-6.3j \t# comment after data",    # comment after tab
                                 "   ",
                                 "3.0\t-7.7+4.3j"))
            spectrum = 1.0 * sumpf.Spectrum(channels=((0.0, 0.0, 0.0, 4.3 - 6.3j, -23.1 - 4.7j, 9.3 + 4.9j, -7.7 + 4.3j),), resolution=0.5, labels=("foo",))  # multiply with 1.0, so the same rounding errors occur as when loading
            filename = os.path.join(tempdir, "spectrum1.asc")
            with open(filename, "w") as f:
                f.write(content)
            loaded = sumpf.modules.LoadSpectrum(filename).GetSpectrum()
            self.assertEqual(loaded, 1.0 * spectrum)
            # test a spectrum file with i as imaginary unit
            content = "\n".join(("# LABELS: foo\tbar", # labels with a space after LABELS:
                                 " # full line comment",
                                 "",
                                 "2.5\t9.3+4.9i\t-3.3-1.2i\t# comment after data",          # comment after tab
                                 "1.5\t4.3-6.3i\t9.3-8.8i\t",                               # trailing tab
                                 "2.0\t-23.1-4.7i\t2.1+2.0i# comment directly after data",  # no space before comment
                                 "3.0\t-7.7+4.3i\t-1.9+4.8i",
                                 "   "))
            spectrum = 1.0 * sumpf.Spectrum(channels=((0.0, 0.0, 0.0, 4.3 - 6.3j, -23.1 - 4.7j, 9.3 + 4.9j, -7.7 + 4.3j), (0.0, 0.0, 0.0, 9.3 - 8.8j, 2.1 + 2.0j, -3.3 - 1.2j, -1.9 + 4.8j)), resolution=0.5, labels=("foo", "bar"))  # multiply with 1.0, so the same rounding errors occur as when loading
            filename = os.path.join(tempdir, "spectrum1.asc")
            with open(filename, "w") as f:
                f.write(content)
            loaded = sumpf.modules.LoadSpectrum(filename).GetSpectrum()
            self.assertEqual(loaded, 1.0 * spectrum)
        finally:
            shutil.rmtree(tempdir)

    @unittest.skipUnless(sumpf.config.get("write_to_disk"), "Tests that write to disk are skipped")
    @unittest.skipUnless(sumpf.config.get("run_long_tests"), "Long tests are skipped")
    def test_unloadable_files(self):
        tempdir = tempfile.mkdtemp()
        try:
            filename = "Unloadable"
            full_filename = os.path.join(tempdir, filename)
            # LoadSignal
            load = sumpf.modules.LoadSignal(full_filename)
            self.assertFalse(load.GetSuccess())
            loaded = load.GetSignal()
            self.assertFalse(load.GetSuccess())
            self.assertEqual(loaded, sumpf.Signal())    # if the file does not exist, an empty data set should be returned
            with open(full_filename, "w") as f:
                f.write("this is not an audio file")
            self.assertFalse(load.GetSuccess())
            loaded2 = load.GetSignal()
            self.assertFalse(load.GetSuccess())
            self.assertIsNot(loaded, loaded2)           # since the file could not be read before, each call of GetSignal should attempt to load the file again
            self.assertIsNot(loaded, load.GetSignal())  # since the file could not be read before, each call of GetSignal should attempt to load the file again
            self.assertEqual(loaded, sumpf.Signal())    # if the file is not an audio file, an empty data set should be returned
            os.remove(full_filename)
            # LoadSpectrum
            load = sumpf.modules.LoadSpectrum(full_filename)
            self.assertFalse(load.GetSuccess())
            loaded = load.GetSpectrum()
            self.assertFalse(load.GetSuccess())
            self.assertEqual(loaded, sumpf.Spectrum())      # if the file does not exist, an empty data set should be returned
            with open(full_filename, "w") as f:
                f.write("this is not an audio file")
            self.assertFalse(load.GetSuccess())
            loaded2 = load.GetSpectrum()
            self.assertFalse(load.GetSuccess())
            self.assertIsNot(loaded, loaded2)               # since the file could not be read before, each call of GetSignal should attempt to load the file again
            self.assertIsNot(loaded, load.GetSpectrum())    # since the file could not be read before, each call of GetSignal should attempt to load the file again
            self.assertEqual(loaded, sumpf.Spectrum())      # if the file is not an audio file, an empty data set should be returned
            os.remove(full_filename)
        finally:
            shutil.rmtree(tempdir)

    @unittest.skipUnless(sumpf.config.get("write_to_disk"), "Tests that write to disk are skipped")
    @unittest.skipUnless(sumpf.config.get("run_long_tests"), "Long tests are skipped")
    def test_watchdog_signal(self):
        """
        Tests the file monitoring functionality of the LoadSignal class.
        """
        sumpf.collect_garbage()
        tempdir = tempfile.mkdtemp()
        signal1 = sumpf.modules.ConstantSignalGenerator(value=1.0, length=4).GetSignal()
        signal2 = sumpf.modules.ConstantSignalGenerator(value=2.0, length=4).GetSignal()
        signal3 = sumpf.modules.ConstantSignalGenerator(value=3.0, length=4).GetSignal()
        try:
            # test modifying a file with monitoring disabled
            filename = os.path.join(tempdir, "signalfile.asc")
            loader = sumpf.modules.LoadSignal(filename)
            tester = Tester()
            sumpf.connect(loader.GetSignal, tester.Trigger)
            self.assertEqual(loader.GetSignal(), sumpf.Signal())
            sumpf.modules.SaveSignal(filename=filename, signal=signal1, file_format=sumpf.modules.SaveSignal.TEXT)
            self.assertEqual(loader.GetSignal(), signal1)
            self.assertFalse(tester.triggered)
            sumpf.modules.SaveSignal(filename=filename, signal=signal2, file_format=sumpf.modules.SaveSignal.TEXT)
            self.assertEqual(loader.GetSignal(), signal1)
            self.assertFalse(tester.triggered)
            loader.SetFilename(filename)
            self.assertEqual(loader.GetSignal(), signal2)
            self.assertTrue(tester.triggered)
            tester.triggered = False
            # test modifying a file with monitoring enabled
            loader.SetMonitorFile(True)
            time.sleep(1.0)
            sumpf.modules.SaveSignal(filename=filename, signal=signal3, file_format=sumpf.modules.SaveSignal.TEXT)
            time.sleep(1.0)
            if common.lib_available("watchdog"):
                self.assertTrue(tester.triggered)
            self.assertEqual(loader.GetSignal(), signal3)
            self.assertTrue(tester.triggered)
            tester.triggered = False
            # test deleting a file with monitoring enabled
            loader2 = sumpf.modules.LoadSignal(filename, monitor_file=True)
            tester2 = Tester()
            sumpf.connect(loader2.GetSignal, tester2.Trigger)
            os.remove(filename)
            time.sleep(1.0)
            if common.lib_available("watchdog"):
                self.assertTrue(tester.triggered)
                self.assertTrue(tester2.triggered)
            self.assertEqual(loader.GetSignal(), sumpf.Signal())
            self.assertEqual(loader2.GetSignal(), sumpf.Signal())
            # test for memory leaks
            sumpf.disconnect_all(loader)
            del loader, tester
            sumpf.disconnect_all(loader2)
            del loader2, tester2
            self.assertEqual(sumpf.collect_garbage(), 0)
        finally:
            shutil.rmtree(tempdir)

    @unittest.skipUnless(sumpf.config.get("write_to_disk"), "Tests that write to disk are skipped")
    @unittest.skipUnless(sumpf.config.get("run_long_tests"), "Long tests are skipped")
    def test_watchdog_spectrum(self):
        """
        Tests the file monitoring functionality of the LoadSpectrum class.
        """
        sumpf.collect_garbage()
        tempdir = tempfile.mkdtemp()
        spectrum1 = sumpf.modules.ConstantSpectrumGenerator(value=1.0 + 1.0j, length=4).GetSpectrum()
        spectrum2 = sumpf.modules.ConstantSpectrumGenerator(value=2.0 + 2.0j, length=4).GetSpectrum()
        spectrum3 = sumpf.modules.ConstantSpectrumGenerator(value=3.0 + 3.0j, length=4).GetSpectrum()
        try:
            # test modifying a file with monitoring disabled
            filename = os.path.join(tempdir, "spectrumfile.asc")
            loader = sumpf.modules.LoadSpectrum(filename)
            tester = Tester()
            sumpf.connect(loader.GetSpectrum, tester.Trigger)
            self.assertEqual(loader.GetSpectrum(), sumpf.Spectrum())
            sumpf.modules.SaveSpectrum(filename=filename, spectrum=spectrum1, file_format=sumpf.modules.SaveSpectrum.TEXT_J)
            self.assertEqual(loader.GetSpectrum(), spectrum1)
            self.assertFalse(tester.triggered)
            sumpf.modules.SaveSpectrum(filename=filename, spectrum=spectrum2, file_format=sumpf.modules.SaveSpectrum.TEXT_J)
            self.assertEqual(loader.GetSpectrum(), spectrum1)
            self.assertFalse(tester.triggered)
            loader.SetFilename(filename)
            self.assertEqual(loader.GetSpectrum(), spectrum2)
            self.assertTrue(tester.triggered)
            tester.triggered = False
            # test modifying a file with monitoring enabled
            loader.SetMonitorFile(True)
            time.sleep(1.0)
            sumpf.modules.SaveSpectrum(filename=filename, spectrum=spectrum3, file_format=sumpf.modules.SaveSpectrum.TEXT_J)
            time.sleep(1.0)
            if common.lib_available("watchdog"):
                self.assertTrue(tester.triggered)
            self.assertEqual(loader.GetSpectrum(), spectrum3)
            self.assertTrue(tester.triggered)
            tester.triggered = False
            # test deleting a file with monitoring enabled
            loader2 = sumpf.modules.LoadSpectrum(filename, monitor_file=True)
            tester2 = Tester()
            sumpf.connect(loader2.GetSpectrum, tester2.Trigger)
            os.remove(filename)
            time.sleep(1.0)
            if common.lib_available("watchdog"):
                self.assertTrue(tester.triggered)
                self.assertTrue(tester2.triggered)
            self.assertEqual(loader.GetSpectrum(), sumpf.Spectrum())
            self.assertEqual(loader2.GetSpectrum(), sumpf.Spectrum())
            # test for memory leaks
            sumpf.disconnect_all(loader)
            del loader, tester
            sumpf.disconnect_all(loader2)
            del loader2, tester2
            self.assertEqual(sumpf.collect_garbage(), 0)
        finally:
            shutil.rmtree(tempdir)

    @unittest.skipUnless(sumpf.config.get("run_long_tests"), "Long tests are skipped")
    @unittest.skipUnless(common.lib_available("numpy"), "This test requires the library 'numpy' to be available.")
    @unittest.skipUnless(common.lib_available("oct2py", dont_import=True), "This test requires the library 'oct2py' to be available.")
    def test_read_ita_audio(self):
        path_of_this_file = sumpf.helper.normalize_path(inspect.getfile(inspect.currentframe()))
        data_path = os.path.join(os.sep.join(path_of_this_file.split(os.sep)[0:-1]), "data")
        timedata_file = os.path.join(data_path, "time.ita")
        freqdata_file = os.path.join(data_path, "freq.ita")
        signalreader = sumpf.modules.LoadSignal(filename=timedata_file)
        spectrumreader = sumpf.modules.LoadSpectrum(filename=freqdata_file)
        reference_signal = sumpf.Signal(channels=((0.125, 0.375, 0.375, 0.125), (1.0, -1.0, 1.0, -1.0)), samplingrate=44100.0, labels=('Lowpass [V]', 'Shah [Pa]'))
        reference_spectrum = sumpf.Spectrum(channels=(((0.25 + 0j), (-0.088388347648318447 - 0.088388347648318447j), 0j), (0j, 0j, (0.70710678118654746 + 0j))), resolution=11025.000000, labels=('Lowpass [V]', 'Shah [Pa]'))
        # compare with reference data
        signal_from_time = signalreader.GetSignal()
        self.assertEqual(signal_from_time, reference_signal)
        spectrum_from_freq = spectrumreader.GetSpectrum()
        self.assertEqual(spectrum_from_freq, reference_spectrum)
        # test if automatic transformation works as expected
        reference_transformed_signal = sumpf.modules.FourierTransform(signal=signal_from_time).GetSpectrum()
        spectrumreader.SetFilename(timedata_file)
        self.assertEqual(spectrumreader.GetSpectrum(), reference_transformed_signal)
        reference_transformed_spectrum = sumpf.modules.InverseFourierTransform(spectrum=spectrum_from_freq).GetSignal()
        signalreader.SetFilename(freqdata_file)
        self.assertEqual(signalreader.GetSignal(), reference_transformed_spectrum)

    @unittest.skipUnless(sumpf.config.get("run_incomplete_tests"), "Incomplete tests are skipped")
    @unittest.skipUnless(sumpf.config.get("write_to_disk"), "Tests that write to disk are skipped")
    @unittest.skipUnless(sumpf.config.get("run_long_tests"), "Long tests are skipped")
    @unittest.skipUnless(sumpf.config.get("run_time_variant_tests"), "Tests which might show a non deterministic behavior are skipped")
    @unittest.skipUnless(common.lib_available("oct2py", dont_import=True), "This test requires the library 'oct2py' to be available.")
    @unittest.skipUnless(common.lib_available("psutil"), "This test requires the library 'psutil' to be available.")
    def test_octave_termination(self):
        """
        tests if all octave processes that have been started to read/write files
        are closed as expected and if the convenience instance of oct2py remains
        unaltered.

        In the current Implementation, SuMPF closes oct2py's convenience instance,
        if it has not been created before reading or writing a file. This has
        the side effect, that the convenience instance has to be restarted before
        it is usable, when a file was read or written with oct2py, before oct2py
        had been imported anywhere else.
        Sadly this is necessary, because if the convenience instance were not closed,
        a probably unused process of Octave would remain active until the Python
        interpreter is closed.
        Some assertions in this test have been disabled by commenting. These
        assertions test, if SuMPF treats the oct2py convenience instance like it
        is supposed to, which is obviously not the case.
        """
        import psutil   # import this here, so it is only imported, when it's available
        def get_running_octave_instances():
            result = []
            for p in psutil.process_iter():
                process_name = None
                try:
                    process_name = p.name()
                except psutil.AccessDenied:
                    pass
                if process_name in ["octave", "octave-cli"]:
                    result.append(p.pid)
            return set(result)
        original_octave_instances = get_running_octave_instances()
        tempdir = tempfile.mkdtemp()
        signalfilename = os.path.join(tempdir, "signal")
        spectrumfilename = os.path.join(tempdir, "spectrum")
        try:
            # test without oct2py being loaded before
            sumpf.modules.SaveSignal(filename=signalfilename, signal=sumpf.Signal(), file_format=sumpf.modules.SaveSignal.MATLAB)
            self.assertEqual(get_running_octave_instances(), original_octave_instances) # check if no octave processes have been left over
            sumpf.modules.LoadSignal(filename=signalfilename).GetSignal()
            self.assertEqual(get_running_octave_instances(), original_octave_instances) # check if no octave processes have been left over
            sumpf.modules.SaveSpectrum(filename=spectrumfilename, spectrum=sumpf.Spectrum(), file_format=sumpf.modules.SaveSpectrum.MATLAB)
            self.assertEqual(get_running_octave_instances(), original_octave_instances) # check if no octave processes have been left over
            sumpf.modules.LoadSpectrum(filename=spectrumfilename).GetSpectrum()
            self.assertEqual(get_running_octave_instances(), original_octave_instances) # check if no octave processes have been left over
            os.remove(signalfilename)
            os.remove(spectrumfilename)
            # test with oct2py being loaded before
            import oct2py
            self.assertIsNotNone(oct2py.octave._session)    # check if the convenience instance is still active
            octave = oct2py.octave
            current_octave_instances = get_running_octave_instances()
            sumpf.modules.SaveSignal(filename=signalfilename, signal=sumpf.Signal(), file_format=sumpf.modules.SaveSignal.MATLAB)
            self.assertIs(oct2py.octave, octave)            # check if the convenience octave instance of oct2py is exactly the same as before saving the file
            self.assertIsNotNone(oct2py.octave._session)    # check if the convenience instance is still active
            self.assertEqual(get_running_octave_instances(), current_octave_instances)  # check if no octave processes have been left over
            sumpf.modules.LoadSignal(filename=signalfilename).GetSignal()
            self.assertIs(oct2py.octave, octave)            # check if the convenience octave instance of oct2py is exactly the same as before saving the file
            self.assertIsNotNone(oct2py.octave._session)    # check if the convenience instance is still active
            self.assertEqual(get_running_octave_instances(), current_octave_instances)  # check if no octave processes have been left over
            sumpf.modules.SaveSpectrum(filename=spectrumfilename, spectrum=sumpf.Spectrum(), file_format=sumpf.modules.SaveSpectrum.MATLAB)
            self.assertIs(oct2py.octave, octave)            # check if the convenience octave instance of oct2py is exactly the same as before saving the file
            self.assertIsNotNone(oct2py.octave._session)    # check if the convenience instance is still active
            self.assertEqual(get_running_octave_instances(), current_octave_instances)  # check if no octave processes have been left over
            sumpf.modules.LoadSpectrum(filename=spectrumfilename).GetSpectrum()
            self.assertIs(oct2py.octave, octave)            # check if the convenience octave instance of oct2py is exactly the same as before saving the file
            self.assertIsNotNone(oct2py.octave._session)    # check if the convenience instance is still active
            self.assertEqual(get_running_octave_instances(), current_octave_instances)  # check if no octave processes have been left over
            octave.exit()
            os.remove(signalfilename)
            os.remove(spectrumfilename)
        finally:
            shutil.rmtree(tempdir)
        self.assertEqual(get_running_octave_instances(), original_octave_instances) # check if no octave processes have been left over

    @unittest.skipUnless(sumpf.config.get("write_to_disk"), "Tests that write to disk are skipped")
    @unittest.skipUnless(sumpf.config.get("run_long_tests"), "Long tests are skipped")
    @unittest.skipUnless(common.lib_available("numpy"), "This test requires the library 'numpy' to be available.")
    @unittest.skipUnless(common.lib_available("scikits.audiolab") or common.lib_available("soundfile"), "Writing lossily compressed files is only available with external libraries")
    def test_autodetect_fileformat_on_save(self):
        """
        Tests if the automatic detection of the format, when saving works as expected.
        """
        def compare_files(filename1, filename2):
            hashes = []
            for n in (filename1, filename2):
                sha1 = hashlib.sha1()
                with open(n, "rb") as f:
                    read = f.read(sha1.block_size)
                    sha1.update(read)
                    while len(read) > 0:
                        read = f.read(sha1.block_size)
                        sha1.update(read)
                hashes.append(sha1.hexdigest())
            self.assertEqual(*hashes)
        tempdir = tempfile.mkdtemp()
        try:
            test_filename = os.path.join(tempdir, "test")
            reference_filename = os.path.join(tempdir, "reference")
            signal = sumpf.modules.SineWaveGenerator().GetSignal()
            spectrum = sumpf.modules.FilterGenerator().GetSpectrum()
            # signal file with file ending
            sumpf.modules.SaveSignal(filename=test_filename + ".aif", signal=signal)
            sumpf.modules.SaveSignal(filename=reference_filename + ".aif", signal=signal, file_format=sumpf.modules.SaveSignal.AIFF_FLOAT)
            compare_files(test_filename + ".aif", reference_filename + ".aif")
            # signal file without file ending
            sumpf.modules.SaveSignal(filename=test_filename, signal=signal)
            sumpf.modules.SaveSignal(filename=reference_filename, signal=signal, file_format=sumpf.modules.SaveSignal.GetFormats()[0])
            compare_files(test_filename, reference_filename)
            # spectrum file with file ending
            sumpf.modules.SaveSpectrum(filename=test_filename + ".asc", spectrum=spectrum)
            sumpf.modules.SaveSpectrum(filename=reference_filename + ".asc", spectrum=spectrum, file_format=sumpf.modules.SaveSpectrum.TEXT_I)
            compare_files(test_filename + ".asc", reference_filename + ".asc")
            # signal file without file ending
            sumpf.modules.SaveSpectrum(filename=test_filename, spectrum=spectrum)
            sumpf.modules.SaveSpectrum(filename=reference_filename, spectrum=spectrum, file_format=sumpf.modules.SaveSpectrum.GetFormats()[0])
            compare_files(test_filename, reference_filename)
        finally:
            shutil.rmtree(tempdir)

    def test_connectors(self):
        """
        Tests if the connectors are properly decorated.
        This is only a shallow test, so it does not write to the disk.
        """
        # LoadSignal
        ls = sumpf.modules.LoadSignal()
        self.assertEqual(ls.GetSignal.GetType(), sumpf.Signal)
        self.assertEqual(ls.GetSuccess.GetType(), bool)
        self.assertEqual(ls.SetFilename.GetType(), str)
        self.assertEqual(ls.SetMonitorFile.GetType(), bool)
        self.assertEqual(set(ls.SetFilename.GetObservers()), set((ls.GetSignal, ls.GetSuccess)))
        self.assertEqual(set(ls.SetMonitorFile.GetObservers()), set())
        # SaveSignal
        ss = sumpf.modules.SaveSignal()
        self.assertEqual(ss.SetSignal.GetType(), sumpf.Signal)
        self.assertEqual(ss.SetFilename.GetType(), str)
        self.assertEqual(ss.SetFormat.GetType(), sumpf.modules.SaveSignal.GetFormats()[0].__mro__[-2])
        self.assertEqual(set(ss.SetSignal.GetObservers()), set())
        self.assertEqual(set(ss.SetFilename.GetObservers()), set())
        self.assertEqual(set(ss.SetFormat.GetObservers()), set())
        # LoadSpectrum
        ls = sumpf.modules.LoadSpectrum()
        self.assertEqual(ls.GetSpectrum.GetType(), sumpf.Spectrum)
        self.assertEqual(ls.GetSuccess.GetType(), bool)
        self.assertEqual(ls.SetFilename.GetType(), str)
        self.assertEqual(ls.SetMonitorFile.GetType(), bool)
        self.assertEqual(set(ls.SetFilename.GetObservers()), set((ls.GetSpectrum, ls.GetSuccess)))
        self.assertEqual(set(ls.SetMonitorFile.GetObservers()), set())
        # SaveSpectrum
        ss = sumpf.modules.SaveSpectrum()
        self.assertEqual(ss.SetSpectrum.GetType(), sumpf.Spectrum)
        self.assertEqual(ss.SetFilename.GetType(), str)
        self.assertEqual(ss.SetFormat.GetType(), sumpf.modules.SaveSpectrum.GetFormats()[0].__mro__[-2])
        self.assertEqual(set(ss.SetSpectrum.GetObservers()), set())
        self.assertEqual(set(ss.SetFilename.GetObservers()), set())
        self.assertEqual(set(ss.SetFormat.GetObservers()), set())

    def __CompareSignals(self, signal1, signal2, format_info, filename):
        if format_info[0]:
            self.assertEqual(signal1.GetChannels(), signal2.GetChannels())
        else:
            for c in range(len(signal1.GetChannels())):
                for s in range(len(signal1.GetChannels()[c])):
                    self.assertAlmostEqual(signal1.GetChannels()[c][s], signal2.GetChannels()[c][s], 6)
        if format_info[2] is None:
            self.assertAlmostEqual(signal1.GetSamplingRate(), signal2.GetSamplingRate(), 10)
        elif format_info[2]:
            self.assertEqual(signal1.GetSamplingRate(), signal2.GetSamplingRate())
        else:
            self.assertEqual(signal1.GetSamplingRate(), round(signal2.GetSamplingRate()))
        if format_info[1]:
            self.assertEqual(signal1.GetLabels(), signal2.GetLabels())
        else:
            for l in signal1.GetLabels():
                self.assertTrue(l.startswith(filename))

