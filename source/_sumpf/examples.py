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

"""
This name space contains examples that demonstrate the functionality of SuMPF.
Maybe these examples are even useful programs.

These examples can also be installed as separate programs in addition to SuMPF.
"""

def RecordTransferFunction():
    """
    Shows a window in which it is possible to record and plot the transfer
    function between a jack-Input and a jack-Output.
    An Impulse response for the given transfer function is calculated as well.
    After recording it is possible to apply some filtering to clean up the
    resulting transfer function or impulse response from unwanted noise or
    harmonic distortion.
    """
    from ._examples import recordtransferfunction
    recordtransferfunction.mainfunction()

def ConvertFile(input="", output="", format="AUTO"):
    """
    Converts an input file to an output file with the given format.
    Depending on the input and output formats, a (inverse) fourier transformation
    will be performed to be able to save the data in the correct output file format.
    This way a saved transfer function can easily be converted to an impulse
    response file.
    If no output file name is given, the file name will be guessed from the input
    file and the format.
    If the given format is AUTO, the format will be guessed from the output file
    name.
    If the filenames end with wav or aif and the format is AUTO, the output file
    will consist of floating point values.
    The file format NUMPY_NPZ (*.npz) can be used for both Signals and Spectrums.
    So if the file format is NUMPY_NPZ (because of either the file ending or the
    given format), a (inverse) fourier transformation will be performed if the
    input file has the format NUMPY_NPZ too. If the input file has another format,
    the output data will be in the same domain as the input data.
    @param input: the filename of the input file
    @param output: the optional filename of the output file
    @param format: the file format of the output file. This can be one of the following: AUTO,
    """
    from ._examples import convertfile
    convertfile.convert_file(input=input, output=output, format=format)

