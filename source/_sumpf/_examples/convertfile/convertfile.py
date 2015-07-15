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
import sumpf

def convert_file(input="", output="", format="AUTO"):
    """
    The main method for the ConvertFile example.
    See the sumpf.examples.ConvertFile function for more documentation
    @param input: the filename of the input file
    @param output: the optional filename of the output file
    @param format: the file format of the output file. This can be one of the following: AUTO,
    """
    # load the input file
    input = sumpf.helper.normalize_path(input)
    if not os.path.exists(input):
        raise IOError("The given input file does not exist")
    input_split = split_filename_and_ending(input)
    input_filename = input_split[0]
    input_ending = input_split[1]
    input_is_signal = True
    input_data = None
    for f in sumpf.modules.SignalFile.GetFormats():
        if f.ending == input_ending:
            try:
                input_data = sumpf.modules.SignalFile(filename=input_filename, format=f).GetSignal()
                break
            except KeyError:
                pass
    if input_data is None:
        for f in sumpf.modules.SpectrumFile.GetFormats():
            if f.ending == input_ending:
                try:
                    input_data = sumpf.modules.SpectrumFile(filename=input_filename, format=f).GetSpectrum()
                    input_is_signal = False
                    break
                except KeyError:
                    pass
    if input_data is None:
        raise IOError("The given input file cannot be loaded")
    # get the output file's format and filename
    output_filename = None
    output_format = None
    output_is_signal = input_is_signal
    if format == "AUTO":
        if output == "":
            if input_is_signal:
                if input_ending == "wav":
                    output_format = sumpf.modules.SpectrumFile.GetFormats()[0]
                else:
                    output_format = sumpf.modules.SignalFile.WAV_FLOAT
                    output_is_signal = True
            else:
                output_format = sumpf.modules.SignalFile.WAV_FLOAT
                output_is_signal = True
            output_filename = input_filename
        else:
            output_split = split_filename_and_ending(sumpf.helper.normalize_path(output))
            output_filename = output_split[0]
            output_ending = output_split[1]
            if input_ending == output_ending:
                output_is_signal = not input_is_signal
            formats = [sumpf.modules.SignalFile.GetFormats(), sumpf.modules.SpectrumFile.GetFormats()]
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
                raise IOError("The format of the output file could not be determined")
    else:
        if output == "":
            output_filename = input_filename
        else:
            output_filename = split_filename_and_ending(sumpf.helper.normalize_path(output))[0]
        formats = [sumpf.modules.SignalFile.GetFormats(), sumpf.modules.SpectrumFile.GetFormats()]
        if not output_is_signal:
            formats.reverse()
        for f in formats[0]:
            if f.__name__ == format:
                output_format = f
                break
        if output_format is None:
            for f in formats[1]:
                if f.__name__ == format:
                    output_format = f
                    output_is_signal = not output_is_signal
                    break
        if output_format is None:
            raise IOError("The format of the output file could not be determined")
    # save the output file
    output_data = input_data
    if output_is_signal and not input_is_signal:
        output_data = sumpf.modules.InverseFourierTransform(spectrum=input_data).GetSignal()
    elif not output_is_signal and input_is_signal:
        output_data = sumpf.modules.FourierTransform(signal=input_data).GetSpectrum()
    if output_is_signal:
        sumpf.modules.SignalFile(filename=output_filename, signal=output_data, format=output_format)
    else:
        sumpf.modules.SpectrumFile(filename=output_filename, spectrum=output_data, format=output_format)


def split_filename_and_ending(path):
    """
    Splits the filename from the file ending and returns them as a tuple.
    @param path: the path that shall be splitted
    @retval : a tuple (filename, ending)
    """
    split = path.split(".")
    filename = ".".join(split[0:-1])
    ending = split[-1]
    return (filename, ending)

