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

import inspect
import os
import shutil
import tempfile
import unittest

import sumpf
import _common as common

@unittest.skipUnless(common.lib_available("numpy"), "These tests require the library 'numpy' to be available.")
class TestFileIO(unittest.TestCase):
    """
    A TestCase for the SignalFile and SpectrumFile modules.
    """
    @unittest.skipUnless(sumpf.config.get("write_to_disk"), "Tests that write to disk are skipped")
    def test_signal_file(self):
        """
        Tests if the SignalFile module works as expected.
        """
        tempdir = tempfile.mkdtemp()
        filename1 = os.path.join(tempdir, "TestFileIO1")
        filename2 = os.path.join(tempdir, "TestFileIO2")
        signal1 = sumpf.Signal(channels=((0.0, 0.1, 0.2, 0.3), (0.4, 0.5, 0.6, 0.7)), samplingrate=23.0, labels=("one", "two"))
        signal2 = sumpf.Signal(channels=((-0.1, -0.2, -0.3), (-0.4, -0.5, -0.6), (-0.7, -0.8, -0.9)), samplingrate=25.0, labels=("three", "four", "five"))
        formats = {}#                                 exact,labels,float samplingrate
        formats[sumpf.modules.SignalFile.NUMPY_NPZ] = (True, True, True)
        if common.lib_available("soundfile"):
            formats[sumpf.modules.SignalFile.AIFF_FLOAT] = (False, False, False)
            formats[sumpf.modules.SignalFile.AIFF_INT] = (False, False, False)
            formats[sumpf.modules.SignalFile.FLAC] = (False, False, False)
            formats[sumpf.modules.SignalFile.WAV_DOUBLE] = (True, False, False)
            formats[sumpf.modules.SignalFile.WAV_INT] = (False, False, False)
            formats[sumpf.modules.SignalFile.WAV_FLOAT] = (False, False, False)
        elif common.lib_available("scikits.audiolab"):
            formats[sumpf.modules.SignalFile.AIFF_FLOAT] = (False, False, False)
            formats[sumpf.modules.SignalFile.AIFF_INT] = (False, False, False)
            formats[sumpf.modules.SignalFile.FLAC] = (False, False, False)
            formats[sumpf.modules.SignalFile.WAV_INT] = (False, False, False)
            formats[sumpf.modules.SignalFile.WAV_FLOAT] = (False, False, False)
        if common.lib_available("oct2py", dont_import=True):
            if sumpf.config.get("run_long_tests"):
                formats[sumpf.modules.SignalFile.MATLAB] = (True, True, True)
        else:
            self.assertNotIn("MATLAB", vars(sumpf.modules.SpectrumFile))
            self.assertNotIn("ITA_AUDIO", vars(sumpf.modules.SpectrumFile))
        self.assertTrue(set(formats.keys()).issubset(sumpf.modules.SignalFile.GetFormats()))
        for f in set(formats.keys()) - set(sumpf.modules.SignalFile.GetFormats()):
            self.assertTrue(f.read_only)
        fileio = sumpf.modules.SignalFile(format=list(formats.keys())[0])
        self.assertEqual(os.listdir(tempdir), [])                                           # if no filename was provided, no file should have been written
        try:
            for f in formats:
                format_info = formats[f]
                filename1e = filename1 + "." + f.ending
                filename2e = filename2 + "." + f.ending
                fileio = sumpf.modules.SignalFile(filename=filename1, format=f)
                self.assertTrue(f.Exists(filename1))                                        # with a filename provided, a file should have been created
                output = fileio.GetSignal()
                self.assertEqual(fileio.GetLength(), len(output))
                self.assertEqual(fileio.GetSamplingRate(), output.GetSamplingRate())
                self.__CompareSignals(output, sumpf.Signal(), format_info, "TestFileIO1")   # this file should contain an empty data set
                fileio = sumpf.modules.SignalFile(filename=filename1, signal=signal1, format=f)
                fileio = sumpf.modules.SignalFile(filename=filename1, format=f)
                output = fileio.GetSignal()
                self.assertEqual(fileio.GetLength(), len(output))
                self.assertEqual(fileio.GetSamplingRate(), output.GetSamplingRate())
                self.__CompareSignals(output, signal1, format_info, "TestFileIO1")          # the existent file should be overwritten when a data set is provided
                fileio.SetSignal(signal2)                                                   # changing the data set should have triggered a rewrite of the file
                fileio = sumpf.modules.SignalFile()
                fileio.SetFilename(filename1)
                fileio.SetFormat(f)
                output = fileio.GetSignal()
                self.__CompareSignals(output, signal2, format_info, "TestFileIO1")          # creating an empty file module and the giving it the filename and the format should have loaded the file into the empty module
                tmpio = sumpf.modules.SignalFile(filename=filename2e, signal=signal1, format=f)
                fileio.SetFilename(filename2e)
                output = fileio.GetSignal()
                self.__CompareSignals(output, signal2, format_info, "TestFileIO2")          # both the constructor and the SetFilename method should have cropped the file ending from the filename
                output = tmpio.GetSignal()
                self.__CompareSignals(output, signal2, format_info, "TestFileIO2")          # both fileio and tmpio have loaded the same file. fileio has changed it, so it should also have changed in tmpio
                os.remove(filename1e)
                os.remove(filename2e)
        finally:
            shutil.rmtree(tempdir)

    @unittest.skipUnless(sumpf.config.get("write_to_disk"), "Tests that write to disk are skipped")
    def test_spectrum_file(self):
        """
        Tests if the SpectrumFile module works as expected.
        """
        tempdir = tempfile.mkdtemp()
        filename1 = os.path.join(tempdir, "TestFileIO1")
        filename2 = os.path.join(tempdir, "TestFileIO2")
        spectrum1 = sumpf.Spectrum(channels=((1.1 + 1.4j, 2.0 + 3.0j), (3.0, 4.0)), resolution=23.0, labels=("one", "two"))
        spectrum2 = sumpf.Spectrum(channels=((5.0, 6.0), (7.0, 8.2 + 2.7j)), resolution=25.0, labels=("three", "four"))
        formats = []
        formats.append(sumpf.modules.SpectrumFile.NUMPY_NPZ)
        if common.lib_available("oct2py", dont_import=True):
            if sumpf.config.get("run_long_tests"):
                formats.append(sumpf.modules.SpectrumFile.MATLAB)
        else:
            self.assertNotIn("MATLAB", vars(sumpf.modules.SpectrumFile))
            self.assertNotIn("ITA_AUDIO", vars(sumpf.modules.SpectrumFile))
        try:
            for f in formats:
                filename1e = filename1 + "." + f.ending
                filename2e = filename2 + "." + f.ending
                fileio = sumpf.modules.SpectrumFile(format=f)
                self.assertEqual(os.listdir(tempdir), [])                                       # if no filename was provided, no file should have been written
                fileio = sumpf.modules.SpectrumFile(filename=filename1, format=f)
                self.assertTrue(f.Exists(filename1))                                            # with a filename provided, a file should have been created
                output = fileio.GetSpectrum()
                self.assertEqual(fileio.GetLength(), len(output))
                self.assertEqual(fileio.GetResolution(), output.GetResolution())
                self.assertEqual(output.GetChannels(), sumpf.Spectrum().GetChannels())          # this file should contain an empty data set
                self.assertEqual(output.GetResolution(), sumpf.Spectrum().GetResolution())      #
                self.assertEqual(output.GetLabels(), sumpf.Spectrum().GetLabels())              #
                fileio = sumpf.modules.SpectrumFile(filename=filename1, spectrum=spectrum1, format=f)
                fileio = sumpf.modules.SpectrumFile(filename=filename1, format=f)
                output = fileio.GetSpectrum()
                self.assertEqual(fileio.GetLength(), len(output))
                self.assertEqual(fileio.GetResolution(), output.GetResolution())
                self.assertEqual(output.GetChannels(), spectrum1.GetChannels())                 # the existent file should be overwritten when a data set is provided
                self.assertEqual(output.GetResolution(), spectrum1.GetResolution())             # ...and then loaded when no data set, but a filename has been provided
                self.assertEqual(output.GetLabels(), spectrum1.GetLabels())                     #
                fileio.SetSpectrum(spectrum2)
                fileio = sumpf.modules.SpectrumFile()
                fileio.SetFilename(filename1)
                fileio.SetFormat(f)
                output = fileio.GetSpectrum()
                self.assertEqual(output.GetChannels(), spectrum2.GetChannels())                 # changing the data set should have triggered a rewrite of the file
                self.assertEqual(output.GetResolution(), spectrum2.GetResolution())             # creating an empty file module and the giving it the filename and the format should have loaded the file into the empty module
                self.assertEqual(output.GetLabels(), spectrum2.GetLabels())                     #
                tmpio = sumpf.modules.SpectrumFile(filename=filename2e, spectrum=spectrum1, format=f)
                fileio.SetFilename(filename2e)
                output = fileio.GetSpectrum()
                self.assertEqual(output.GetChannels(), spectrum2.GetChannels())                 # both the constructor and the SetFilename method should have cropped the file ending from the filename
                self.assertEqual(output.GetResolution(), spectrum2.GetResolution())             #
                self.assertEqual(output.GetLabels(), spectrum2.GetLabels())                     #
                output = tmpio.GetSpectrum()
                self.assertEqual(output.GetChannels(), spectrum2.GetChannels())                 # both fileio and tmpio have loaded the same file
                self.assertEqual(output.GetResolution(), spectrum2.GetResolution())             # fileio has changed it
                self.assertEqual(output.GetLabels(), spectrum2.GetLabels())                     # so it should also have changed in tmpio
                os.remove(filename1e)
                os.remove(filename2e)
        finally:
            shutil.rmtree(tempdir)

    @unittest.skipUnless(sumpf.config.get("run_long_tests"), "Long tests are skipped")
    @unittest.skipUnless(common.lib_available("oct2py", dont_import=True), "This test requires the library 'oct2py' to be available.")
    def test_read_ita_audio(self):
        path_of_this_file = sumpf.helper.normalize_path(inspect.getfile(inspect.currentframe()))
        data_path = os.path.join(os.sep.join(path_of_this_file.split(os.sep)[0:-1]), "data")
        timedata_file = os.path.join(data_path, "time.ita")
        freqdata_file = os.path.join(data_path, "freq.ita")
        signalreader = sumpf.modules.SignalFile(filename=timedata_file, format=sumpf.modules.SignalFile.ITA_AUDIO)
        spectrumreader = sumpf.modules.SpectrumFile(filename=freqdata_file, format=sumpf.modules.SpectrumFile.ITA_AUDIO)
        reference_signal = sumpf.Signal(channels=((0.125, 0.375, 0.375, 0.125), (1.0, -1.0, 1.0, -1.0)), samplingrate=44100.000000, labels=('Lowpass [V]', 'Shah [Pa]'))
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
            sumpf.modules.SignalFile(filename=signalfilename, signal=sumpf.Signal(), format=sumpf.modules.SignalFile.MATLAB)
            self.assertEqual(get_running_octave_instances(), original_octave_instances) # check if no octave processes have been left over
            sumpf.modules.SignalFile(filename=signalfilename, format=sumpf.modules.SignalFile.MATLAB).GetSignal()
            self.assertEqual(get_running_octave_instances(), original_octave_instances) # check if no octave processes have been left over
            sumpf.modules.SpectrumFile(filename=spectrumfilename, spectrum=sumpf.Spectrum(), format=sumpf.modules.SpectrumFile.MATLAB)
            self.assertEqual(get_running_octave_instances(), original_octave_instances) # check if no octave processes have been left over
            sumpf.modules.SpectrumFile(filename=spectrumfilename, format=sumpf.modules.SpectrumFile.MATLAB).GetSpectrum()
            self.assertEqual(get_running_octave_instances(), original_octave_instances) # check if no octave processes have been left over
            os.remove(signalfilename + ".mat")
            os.remove(spectrumfilename + ".mat")
            # test with oct2py being loaded before
            import oct2py
#           self.assertIsNotNone(oct2py.octave._session)    # check if the convenience instance is still active
            octave = oct2py.octave
            current_octave_instances = get_running_octave_instances()
            sumpf.modules.SignalFile(filename=signalfilename, signal=sumpf.Signal(), format=sumpf.modules.SignalFile.MATLAB)
            self.assertIs(oct2py.octave, octave)            # check if the convenience octave instance of oct2py is exactly the same as before saving the file
#           self.assertIsNotNone(oct2py.octave._session)    # check if the convenience instance is still active
            self.assertEqual(get_running_octave_instances(), current_octave_instances)  # check if no octave processes have been left over
            sumpf.modules.SignalFile(filename=signalfilename, format=sumpf.modules.SignalFile.MATLAB).GetSignal()
            self.assertIs(oct2py.octave, octave)            # check if the convenience octave instance of oct2py is exactly the same as before saving the file
#           self.assertIsNotNone(oct2py.octave._session)    # check if the convenience instance is still active
            self.assertEqual(get_running_octave_instances(), current_octave_instances)  # check if no octave processes have been left over
            sumpf.modules.SpectrumFile(filename=spectrumfilename, spectrum=sumpf.Spectrum(), format=sumpf.modules.SpectrumFile.MATLAB)
            self.assertIs(oct2py.octave, octave)            # check if the convenience octave instance of oct2py is exactly the same as before saving the file
#           self.assertIsNotNone(oct2py.octave._session)    # check if the convenience instance is still active
            self.assertEqual(get_running_octave_instances(), current_octave_instances)  # check if no octave processes have been left over
            sumpf.modules.SpectrumFile(filename=spectrumfilename, format=sumpf.modules.SpectrumFile.MATLAB).GetSpectrum()
            self.assertIs(oct2py.octave, octave)            # check if the convenience octave instance of oct2py is exactly the same as before saving the file
#           self.assertIsNotNone(oct2py.octave._session)    # check if the convenience instance is still active
            self.assertEqual(get_running_octave_instances(), current_octave_instances)  # check if no octave processes have been left over
            octave.exit()
            os.remove(signalfilename + ".mat")
            os.remove(spectrumfilename + ".mat")
        finally:
            shutil.rmtree(tempdir)
        self.assertEqual(get_running_octave_instances(), original_octave_instances) # check if no octave processes have been left over

    def test_connectors(self):
        """
        Tests if the connectors are properly decorated.
        This is only a shallow test, so it does not write to the disk.
        """
        # SignalFile
        sf = sumpf.modules.SignalFile()
        self.assertEqual(sf.SetSignal.GetType(), sumpf.Signal)
        self.assertEqual(sf.SetFilename.GetType(), str)
#       self.assertEqual(sf.SetFormat.GetType(), type(sumpf.modules.SignalFile.GetFormats()[0]))
        self.assertEqual(sf.GetSignal.GetType(), sumpf.Signal)
        self.assertEqual(sf.GetLength.GetType(), int)
        self.assertEqual(sf.GetSamplingRate.GetType(), float)
        self.assertEqual(set(sf.SetSignal.GetObservers()), set([sf.GetSignal, sf.GetLength, sf.GetSamplingRate]))
        self.assertEqual(set(sf.SetFilename.GetObservers()), set([sf.GetSignal, sf.GetLength, sf.GetSamplingRate]))
        self.assertEqual(set(sf.SetFormat.GetObservers()), set([sf.GetSignal, sf.GetLength, sf.GetSamplingRate]))
        # SignalFile
        sf = sumpf.modules.SpectrumFile()
        self.assertEqual(sf.SetSpectrum.GetType(), sumpf.Spectrum)
        self.assertEqual(sf.SetFilename.GetType(), str)
#       self.assertEqual(sf.SetFormat.GetType(), type(sumpf.modules.SpectrumFile.GetFormats()[0]))
        self.assertEqual(sf.GetSpectrum.GetType(), sumpf.Spectrum)
        self.assertEqual(sf.GetLength.GetType(), int)
        self.assertEqual(sf.GetResolution.GetType(), float)
        self.assertEqual(set(sf.SetSpectrum.GetObservers()), set([sf.GetSpectrum, sf.GetLength, sf.GetResolution]))
        self.assertEqual(set(sf.SetFilename.GetObservers()), set([sf.GetSpectrum, sf.GetLength, sf.GetResolution]))
        self.assertEqual(set(sf.SetFormat.GetObservers()), set([sf.GetSpectrum, sf.GetLength, sf.GetResolution]))

    def __CompareSignals(self, signal1, signal2, format_info, filename):
        if format_info[0]:
            self.assertEqual(signal1.GetChannels(), signal2.GetChannels())
        else:
            for c in range(len(signal1.GetChannels())):
                for s in range(len(signal1.GetChannels()[c])):
                    self.assertAlmostEqual(signal1.GetChannels()[c][s], signal2.GetChannels()[c][s], 6)
        if format_info[2]:
            self.assertEqual(signal1.GetSamplingRate(), signal2.GetSamplingRate())
        else:
            self.assertEqual(signal1.GetSamplingRate(), round(signal2.GetSamplingRate()))
        if format_info[1]:
            self.assertEqual(signal1.GetLabels(), signal2.GetLabels())
        else:
            for l in signal1.GetLabels():
                self.assertTrue(l.startswith(filename))

