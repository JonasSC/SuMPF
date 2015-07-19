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
import inspect
import os
import sys
import numpy
import sumpf
from .fileformat import FileFormat

oct2py_available = False
if sys.version_info.major == 2:
    import imp
    try:
        imp.find_module("oct2py")
        oct2py_available = True
    except ImportError:
        pass
else:
    import importlib.util
    if importlib.util.find_spec("oct2py") is not None:
        oct2py_available = True
    basestring = str


spectrumformats = []


class NUMPY_NPZ(FileFormat):
    """
    File format class for the numpy npz-format for Spectrums.
    http://docs.scipy.org/doc/numpy/reference/generated/numpy.savez.html
    """
    ending = "npz"
    @classmethod
    def Load(cls, filename):
        def to_string(label):
            if label is None:
                return None
            else:
                return str(label)
        channels = []
        resolution = 1.0
        labels = None
        with numpy.load(filename + "." + cls.ending) as data:
            for c in data["channels"]:
                channels.append(tuple(c))
            resolution = data["resolution"]
            labels = tuple([to_string(l) for l in data["labels"]])
        return sumpf.Spectrum(channels=channels, resolution=resolution, labels=labels)

    @classmethod
    def Save(cls, filename, data):
        numpy.savez_compressed(filename + "." + cls.ending,
                    channels=data.GetChannels(),
                    resolution=data.GetResolution(),
                    labels=data.GetLabels())

spectrumformats.append(NUMPY_NPZ)



if oct2py_available:
    class ITA_AUDIO(FileFormat):
        """
        File format class for the format used by the ITA-Toolbox from the Institute
        of Technical Acoustics, RWTH Aachen University.
        http://www.ita-toolbox.org
        This class can only read itaAudio files. Writing is not possible.

        Importing itaAudio files is done with the help of the oct2py library.
        In the current Implementation, SuMPF closes oct2py's convenience instance,
        if it has not been created before reading or writing a file. This has
        the side effect, that the convenience instance has to be restarted before
        it is usable, when a file was read or written with oct2py, before oct2py
        had been imported anywhere else.
        Sadly this is necessary, because if the convenience instance were not closed,
        a probably unused process of Octave would remain active until the Python
        interpreter is closed.
        """
        ending = "ita"
        read_only = True

        @classmethod
        def Load(cls, filename):
            filename = "%s.%s" % (filename, cls.ending)
            # retrieve the Matlab data through octave
            path_of_this_file = sumpf.helper.normalize_path(inspect.getfile(inspect.currentframe()))
            terminate_convenience_instance = "oct2py" not in sys.modules
            import oct2py
            with oct2py.Oct2Py() as octave:
                octave.addpath(os.sep.join(path_of_this_file.split(os.sep)[0:-1]))
                samples, samplingrate, domain, names, units = octave.read_ita_file(filename)
            if terminate_convenience_instance:
                oct2py.octave.exit()                    # stop the convenience instance to avoid an unused instance of Octave
            channels = tuple(numpy.transpose(samples))
            # create channel labels
            labels = []
            for i in range(len(names)):
                if i < len(units):
                    labels.append(str("%s [%s]" % (names[i], units[i])))
                else:
                    labels.append(str(names[i]))
            # transform to the frequency domain, if necessary
            if domain == "freq":
                return sumpf.Spectrum(channels=channels,
                                      resolution=sumpf.modules.ChannelDataProperties(spectrum_length=len(channels[0]), samplingrate=samplingrate).GetResolution(),
                                      labels=labels)
            elif domain == "time":
                signal = sumpf.Signal(channels=channels, samplingrate=samplingrate, labels=labels)
                return sumpf.modules.FourierTransform(signal=signal).GetSpectrum()
            else:
                raise RuntimeError("Unknown domain: %s" % domain)

    spectrumformats.append(ITA_AUDIO)



    class MATLAB(FileFormat):
        """
        File format class for the import and export of Octave/Matlab mat-files.
        This class tries its best to guess, how the data has to be interpreted
        as a Spectrum:
          - It searches for a value for the resolution in the following variables:
              resolution, frequency_resolution, frequencyresolution, delta_f, deltaf, d_f, df
            This search is performed in that order. The resolution is taken from
            the first variable that is found. The variable names are case insensitive.
            If none of these variables is found, the default resolution is taken.
          - The channels are taken from the longest (most rows or most columns)
            array that contains numbers. If the longest array has more columns
            than rows, all arrays are transposed, so that their rows are interpreted
            as channels and their columns are interpreted as samples.
            If multiple arrays have the same length as the longest array, their
            channels are added to the channels of the output Spectrum. If it is
            possible to add multiple arrays to the output Spectrum's channels by
            transposing all arrays, this transposing is done.
          - If an array with the name 'labels' (case insensitive), that contains
            strings, is found, the Signal's labels are taken from that array.
            Otherwise the labels are created from the channel array's variable
            name.

        Reading/writing Matlab files is done with the help of the oct2py library.
        In the current Implementation, SuMPF closes oct2py's convenience instance,
        if it has not been created before reading or writing a file. This has
        the side effect, that the convenience instance has to be restarted before
        it is usable, when a file was read or written with oct2py, before oct2py
        had been imported anywhere else.
        Sadly this is necessary, because if the convenience instance were not closed,
        a probably unused process of Octave would remain active until the Python
        interpreter is closed.
        """
        ending = "mat"
        read_only = False

        @classmethod
        def Load(cls, filename):
            filename = "%s.%s" % (filename, cls.ending)
            # retrieve the Matlab data through octave
            path_of_this_file = sumpf.helper.normalize_path(inspect.getfile(inspect.currentframe()))
            terminate_convenience_instance = "oct2py" not in sys.modules
            import oct2py
            with oct2py.Oct2Py() as octave:
                octave.addpath(os.sep.join(path_of_this_file.split(os.sep)[0:-1]))
                data = octave.read_mat_file(filename)
            if terminate_convenience_instance:
                oct2py.octave.exit()                    # stop the convenience instance to avoid an unused instance of Octave
            # get sampling rate
            resolution = None
            for searched in ["resolution", "frequency_resolution", "frequencyresolution", "delta_f", "deltaf", "d_f", "df"]:
                for found in data:
                    if searched.lower() == found.lower() and isinstance(data[found], (int, float)):
                        resolution = data[found]
                if resolution is not None:
                    break
            # get channels
            channels = []
            labels = []
            for v in data:
                variable = data[v]
                if isinstance(variable, numpy.ndarray) and 0 < len(variable):
                    if isinstance(variable[0], (int, float, complex)):
                        if channels == [] or len(channels[0]) < len(variable):
                            channels = [tuple(variable)]
                            labels = [v]
                        elif len(channels[0]) == len(variable):
                            channels.append(tuple(variable))
                            labels.append(v)
                    elif isinstance(variable[0][0], (int, float, complex)):
                        if channels == []:
                            if len(variable[0]) < len(variable):
                                channels = list(numpy.transpose(variable))
                            else:
                                channels = list(variable)
                            labels = [v] * len(variable[0])
                        elif len(channels[0]) == len(variable[0]):
                            channels.extend(variable)
                            labels.extend([v] * len(variable))
                        elif 2 <= len(channels) and len(channels) == len(variable):
                            labels = [labels[0]] * len(channels[0]) + [v] * len(variable[0])
                            channels = list(numpy.transpose(channels)) + list(numpy.transpose(variable))
                        elif len(channels[0]) < len(variable[0]):
                            channels = list(variable)
                            labels = [v] * len(variable)
            if len(channels) == 0:
                channels = ((0.0, 0.0),)
                labels = [None]
            # get labels
            for found in data:
                if found.lower() == "labels":
                    if isinstance(data[found], collections.Iterable) and \
                       0 < len(data[found]) and \
                       isinstance(data[found][0], basestring):
                        for i in range(min(len(labels), len(data[found]))):
                            if data[found][i] in [[], ()]:
                                labels[i] = None
                            else:
                                labels[i] = str(data[found][i])
                        break
                    elif data[found] in [[], (), 0]:
                        labels[0] = None
            # get a default value for the resolution, if it has not been specified before
            if resolution is None:
                resolution = sumpf.modules.ChannelDataProperties(spectrum_length=len(channels[0])).GetResolution()
            return sumpf.Spectrum(channels=channels, resolution=resolution, labels=labels)

        @classmethod
        def Save(cls, filename, data):
            filename = "%s.%s" % (filename, cls.ending)
            labels = list(data.GetLabels())
            # avoid labels that are None
            for i, l in enumerate(labels):
                if l is None:
                    labels[i] = 0
            path_of_this_file = sumpf.helper.normalize_path(inspect.getfile(inspect.currentframe()))
            terminate_convenience_instance = "oct2py" not in sys.modules
            import oct2py
            with oct2py.Oct2Py() as octave:
                octave.addpath(os.sep.join(path_of_this_file.split(os.sep)[0:-1]))
                octave.write_mat_file(filename,
                                      data.GetChannels(),
                                      0.0,  # this does not write a Signal, so the sampling rate is 0.0
                                      data.GetResolution(),
                                      labels)
            if terminate_convenience_instance:
                oct2py.octave.exit()                    # stop the convenience instance to avoid an unused instance of Octave

    spectrumformats.append(MATLAB)

