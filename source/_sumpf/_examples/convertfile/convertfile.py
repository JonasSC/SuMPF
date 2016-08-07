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
import sumpf

def convert_file(input="", output="", file_format="AUTO"):
    """
    The main method for the ConvertFile example.
    See the sumpf.examples.ConvertFile function for more documentation
    @param input: the filename of the input file
    @param output: the optional filename of the output file
    @param file_format: the file format of the output file. This can be one of the following: AUTO,
    """
    # load the input file
    input = sumpf.helper.normalize_path(input)
    if not os.path.exists(input):
        raise IOError("The given input file does not exist")
    input_filename, input_ending = os.path.splitext(input)
    input_ending = input_ending.lstrip(".")
    input_is_signal = True
    signal_loader = sumpf.modules.LoadSignal(filename=input)
    if signal_loader.GetSuccess():
        input_data = signal_loader.GetSignal()
    else:
        spectrum_loader = sumpf.modules.LoadSpectrum(filename=input)
        if spectrum_loader.GetSuccess():
            input_data = spectrum_loader.GetSpectrum()
            input_is_signal = False
        else:
            raise IOError("The given input file cannot be loaded: %s" % input)
    # get the output file's format and filename
    output_filename = None
    output_format = None
    output_is_signal = input_is_signal
    if file_format == "AUTO":
        if output == "":
            if input_is_signal:
                if input_ending == "wav":
                    output_format = sumpf.modules.SaveSpectrum.GetFormats()[0]
                else:
                    output_format = sumpf.modules.SaveSignal.WAV_FLOAT
                    output_is_signal = True
            else:
                output_format = sumpf.modules.SaveSignal.WAV_FLOAT
                output_is_signal = True
            output_filename = input_filename
        else:
            output_filename, output_ending = os.path.splitext(sumpf.helper.normalize_path(output))
            output_ending = output_ending.lstrip(".")
            if input_ending == output_ending:
                output_is_signal = not input_is_signal
            formats = [sumpf.modules.SaveSignal.GetFormats(), sumpf.modules.SaveSpectrum.GetFormats()]
            if not output_is_signal:
                formats.reverse()
            for f in formats[0]:
                if f.ending == output_ending:
                    output_format = f
                    break
            if output_format is None:
                for f in formats[1]:
                    if f.ending == output_ending:
                        output_format = f
                        output_is_signal = not output_is_signal
                        break
            if output_format is None:
                raise IOError("The format of the output file could not be determined automatically")
    else:
        if output == "":
            output_filename = input_filename
        else:
            output_filename = os.path.splitext(sumpf.helper.normalize_path(output))[0]
        formats = [sumpf.modules.SaveSignal.GetFormats(), sumpf.modules.SaveSpectrum.GetFormats()]
        if not output_is_signal:
            formats.reverse()
        for f in formats[0]:
            if f.__name__ == file_format:
                output_format = f
                break
        if output_format is None:
            for f in formats[1]:
                if f.__name__ == file_format:
                    output_format = f
                    output_is_signal = not output_is_signal
                    break
        if output_format is None:
            raise IOError("The format of the output file could not be determined")
    if not output_filename.endswith(output_format.ending):
        output_filename = "%s.%s" % (output_filename, output_format.ending)
    # save the output file
    output_data = input_data
    if output_is_signal and not input_is_signal:
        output_data = sumpf.modules.InverseFourierTransform(spectrum=input_data).GetSignal()
    elif not output_is_signal and input_is_signal:
        output_data = sumpf.modules.FourierTransform(signal=input_data).GetSpectrum()
    if output_is_signal:
        sumpf.modules.SaveSignal(filename=output_filename, signal=output_data, file_format=output_format)
    else:
        sumpf.modules.SaveSpectrum(filename=output_filename, spectrum=output_data, file_format=output_format)

