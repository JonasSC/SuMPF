# This file is a part of the "SuMPF" package
# Copyright (C) 2018-2021 Jonas Schulte-Coerne
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.

"""Contains implementations of signals for window functions, that require :mod:`scipy`."""

import math
import numpy
import scipy.signal
import sumpf._internal as sumpf_internal
from ._windows import Window

__all__ = ("BartlettHannWindow", "BlackmanHarrisWindow", "BohmanWindow",
           "DolphChebyshevWindow", "ExponentialWindow", "FlatTopWindow",
           "GaussianWindow", "NuttallWindow", "ParzenWindow", "SlepianWindow")


class BartlettHannWindow(Window):
    """The Bartlett-Hann window is an additive combination of the triangular
    Bartlett window and the cosine Hann window.
    """

    def _function(self, length):
        return scipy.signal.windows.barthann(length)

    def _label(self):
        return "Bartlett-Hann window"


class BlackmanHarrisWindow(Window):
    """The Blackman-Harris window is a four term sum of cosine window, which
    reduces the amplitude of the side lobes at the cost of a slow decay of
    the side lobes of only 6dB/octave. See the :class:`~sumpf.NuttallWindow`
    class for an optimized version of this window.
    """

    def _function(self, length):
        return scipy.signal.windows.blackmanharris(length)

    def _label(self):
        return "Blackman-Harris window"


class BohmanWindow(Window):
    """The Bohman window is computed from the auto-correlation of the cosine
    window. It seems to have slightly better side lobe rejection than the Hann
    window, while suffering from a slightly higher bandwidth.
    """

    def _function(self, length):
        return scipy.signal.windows.bohman(length)

    def _label(self):
        return "Bohman window"


class DolphChebyshevWindow(Window):
    """The Dolph-Chebyshev window is defined as a type 2 Chebyshev filter in
    the frequency domain and then transformed to the time domain. It has an
    adjustable attenuation of the side lobes, that has the side effect of increasing
    the window's bandwidth for larger attenuation values.

    Also, the window is neither guaranteed to be monotonic, nor are its first
    and last sample guaranteed to be zero. Especially for low attenuation values
    and small window lengths, this increases the possibility to have impulses
    at the beginning and the end of the window, which can cause (pre-)echo artifacts.

    The side lobes have constant maximums and do not decay for higher frequencies.

    The filter order is proportional to the window's length. In the time domain,
    this causes the window to have a consistent shape, that is independent of
    the window's length (except for the peaks at the beginning and end).All
    other window functions in *SuMPF* have a consistent shape, too. But with
    those, this is achieved by scaling the window function in the time domain.
    """

    def __init__(self, attenuation=150.0, plateau=0, sampling_rate=48000.0, length=8192, symmetric=True):
        """
        :param attenuation: the attenuation of the side lobes in dB as a positive float
        :param plateau: an integer length or a float factor for the signal length,
                        that specifies, how many samples in the middle of the signal
                        shall be 1.0 without being affected by the window's fade
                        in and fade out.
        :param sampling_rate: the sampling rate of the resulting signal in Hz as
                              an integer or a float
        :param length: the number of samples of the window function
        :param symmetric: True, if the window's last sample shall be the same as
                          its first sample. False, if the window's last sample shall
                          be the same as its second sample. The latter is often
                          beneficial in segmentation applications, as it makes it
                          easier to meet the "constant overlap-add"-constraint.
        """
        self.__attenuation = attenuation
        Window.__init__(self, plateau=plateau, sampling_rate=sampling_rate, length=length, symmetric=symmetric)

    def _function(self, length):
        if length == 0:
            return numpy.empty(0)
        elif length <= 2:
            return numpy.ones(length)
        else:
            non_normalized = scipy.signal.windows.chebwin(length, at=self.__attenuation)
            return non_normalized / non_normalized[length // 2]

    def _label(self):
        return "Dolph-Chebyshev window"


class ExponentialWindow(Window):
    """The exponential window is simply an exponential decay function.

    The window's shape can be influenced with the ``decay`` parameter,
    which is a positive value in dB, that describes how much the beginning
    and the end of the window is smaller than the center (which is 1.0). A
    decay value of 0.0dB will result in a rectangular window.
    """

    def __init__(self, decay=100.0, plateau=0, sampling_rate=48000.0, length=8192, symmetric=True):
        """
        :param decay: the attenuation of the window's corners in comparison
                      to its center in dB as a positive float
        :param plateau: an integer length or a float factor for the signal length,
                        that specifies, how many samples in the middle of the signal
                        shall be 1.0 without being affected by the window's fade
                        in and fade out.
        :param sampling_rate: the sampling rate of the resulting signal in Hz as
                              an integer or a float
        :param length: the number of samples of the window function
        :param symmetric: True, if the window's last sample shall be the same as
                          its first sample. False, if the window's last sample shall
                          be the same as its second sample. The latter is often
                          beneficial in segmentation applications, as it makes it
                          easier to meet the "constant overlap-add"-constraint.
        """
        self.__decay = decay
        Window.__init__(self, plateau=plateau, sampling_rate=sampling_rate, length=length, symmetric=symmetric)

    def _function(self, length):
        if length == 1 or self.__decay == 0.0:
            return numpy.ones(length)
        else:
            tau = -10.0 * (length - 1) / (math.log(10) * -self.__decay)
            return scipy.signal.windows.exponential(length, tau=tau)

    def _label(self):
        return "Exponential window"


class FlatTopWindow(Window):
    """Flat top windows achieve a small scalloping loss by allowing negative values
    in the window function. Because of this, they tend to have a relatively high
    bandwidth and recommended overlap.

    The exact window function can be specified with the ``function`` parameter,
    that accepts a flag from the :attr:`~sumpf.FlatTopWindow.functions` enumeration.
    The different flat top windows are explained in the documentation of the enumeration
    class. The default function is that of :func:`scipy.signal.windows.flattop`.

    The coefficients of most flat top windows are taken from the paper `Spectrum
    and spectral density estimation by the Discrete Fourier transform (DFT),
    including a comprehensive list of window functions and some new flat-top windows
    <https://holometer.fnal.gov/GH_FFT.pdf#page=38>`__ by G. Heinzel, A. Rüdiger
    and R. Schilling, which was published by the Max-Planck-Institut für Gravitationsphysik
    in February 2002.
    """

    functions = sumpf_internal.FlatTopWindows

    def __init__(self,
                 function=sumpf_internal.FlatTopWindows.DEFAULT,
                 plateau=0,
                 sampling_rate=48000.0,
                 length=8192,
                 symmetric=True):
        """
        :param function: a flag from the :attr:`~sumpf.FlatTopWindow.functions`
                         enumeration.
        :param plateau: an integer length or a float factor for the signal length,
                        that specifies, how many samples in the middle of the signal
                        shall be 1.0 without being affected by the window's fade
                        in and fade out.
        :param sampling_rate: the sampling rate of the resulting signal in Hz as
                              an integer or a float
        :param length: the number of samples of the window function
        :param symmetric: True, if the window's last sample shall be the same as
                          its first sample. False, if the window's last sample shall
                          be the same as its second sample. The latter is often
                          beneficial in segmentation applications, as it makes it
                          easier to meet the "constant overlap-add"-constraint.
        """
        self.__function = function
        Window.__init__(self, plateau=plateau, sampling_rate=sampling_rate, length=length, symmetric=symmetric)

    def _function(self, length):    # noqa: C901; the method is not complex, it's just a long switch case
        # pylint: disable=line-too-long; the coefficient lists may become long
        # pylint: disable=too-many-branches,too-many-return-statements; this is basically a large switch-statement
        if self.__function == FlatTopWindow.functions.DEFAULT:
            return scipy.signal.windows.flattop(length)
        elif self.__function == FlatTopWindow.functions.SFT3F:
            return scipy.signal.windows.general_cosine(length, (0.26526, 0.5, 0.23474))
        elif self.__function == FlatTopWindow.functions.SFT4F:
            return scipy.signal.windows.general_cosine(length, (0.21706, 0.42103, 0.28294, 0.07897))
        elif self.__function == FlatTopWindow.functions.SFT5F:
            return scipy.signal.windows.general_cosine(length, (0.1881, 0.36923, 0.28702, 0.13077, 0.02488))
        elif self.__function == FlatTopWindow.functions.SFT3M:
            return scipy.signal.windows.general_cosine(length, (0.28235, 0.52105, 0.19659))
        elif self.__function == FlatTopWindow.functions.SFT4M:
            return scipy.signal.windows.general_cosine(length, (0.241906, 0.460841, 0.255381, 0.041872))
        elif self.__function == FlatTopWindow.functions.SFT5M:
            return scipy.signal.windows.general_cosine(length, (0.209671, 0.407331, 0.281225, 0.092669, 0.0091036))
        elif self.__function == FlatTopWindow.functions.FTNI:
            return scipy.signal.windows.general_cosine(length, (0.2810639, 0.5208972, 0.1980399))
        elif self.__function == FlatTopWindow.functions.FTHP:
            return scipy.signal.windows.general_cosine(length, (1.0, 1.912510941, 1.079173272, 0.1832630879)) / 4.1749473009
        elif self.__function == FlatTopWindow.functions.FTSRS:
            return scipy.signal.windows.general_cosine(length, (1.0, 1.93, 1.29, 0.388, 0.028)) / 4.635999999999999
        elif self.__function == FlatTopWindow.functions.HFT70:
            return scipy.signal.windows.general_cosine(length, (1.0, 1.90796, 1.07349, 0.18199)) / 4.1634400000000005
        elif self.__function == FlatTopWindow.functions.HFT90D:
            return scipy.signal.windows.general_cosine(length, (1.0, 1.942604, 1.340318, 0.440811, 0.043097)) / 4.766830000000001
        elif self.__function == FlatTopWindow.functions.HFT95:
            return scipy.signal.windows.general_cosine(length, (1.0, 1.9383379, 1.3045202, 0.4028270, 0.0350665)) / 4.680751600000001
        elif self.__function == FlatTopWindow.functions.HFT116D:
            return scipy.signal.windows.general_cosine(length, (1.0, 1.9575375, 1.4780705, 0.6367431, 0.1228389, 0.0066288)) / 5.2018188
        elif self.__function == FlatTopWindow.functions.HFT144D:
            return scipy.signal.windows.general_cosine(length, (1.0, 1.96760033, 1.57983607, 0.81123644, 0.22583558, 0.02773848, 0.00090360)) / 5.6131505
        elif self.__function == FlatTopWindow.functions.HFT169D:
            return scipy.signal.windows.general_cosine(length, (1.0, 1.97441842, 1.65409888, 0.95788186, 0.33673420, 0.06364621, 0.00521942, 0.00010599)) / 5.99210498
        elif self.__function == FlatTopWindow.functions.HFT196D:
            return scipy.signal.windows.general_cosine(length, (1.0, 1.979280420, 1.710288951, 1.081629853, 0.448734314, 0.112376628, 0.015122992, 0.000871252, 0.000011896)) / 6.348316306
        elif self.__function == FlatTopWindow.functions.HFT223D:
            return scipy.signal.windows.general_cosine(length, (1.0, 1.98298997309, 1.75556083063, 1.19037717712, 0.56155440797, 0.17296769663, 0.03233247087, 0.00324954578, 0.00013801040, 0.00000132725)) / 6.69917143974
        elif self.__function == FlatTopWindow.functions.HFT248D:
            return scipy.signal.windows.general_cosine(length, (1.0, 1.985844164102, 1.791176438506, 1.282075284005, 0.667777530266, 0.240160796576, 0.056656381764, 0.008134974479, 0.000624544650, 0.000019808998, 0.000000132974)) / 7.032470056319999
        else:
            raise ValueError(f"unknown flat top window function: {self.__function}")

    def _label(self):
        return "Flat top window"


class GaussianWindow(Window):
    """The Gaussian window is simply a Gaussian function. Since the Gaussian function
    never reaches zero, this window has jumps at its end, which reduce the decay
    of the side lobes.

    For the window to have a consistent shape, that is independent of the window's
    length, the ``standard_deviation`` parameter is scaled with the window's length.
    """

    def __init__(self, standard_deviation=1.0, plateau=0, sampling_rate=48000.0, length=8192, symmetric=True):
        """
        :param standard_deviation: the standard deviation of the Gaussian window
                                   function, that is normalized by the length of
                                   the window. This makes the shape of the window
                                   independent of its length. The actual standard
                                   deviation, that is used, will be ``standard_deviation * (length - 1) / 2.0``
        :param plateau: an integer length or a float factor for the signal length,
                        that specifies, how many samples in the middle of the signal
                        shall be 1.0 without being affected by the window's fade
                        in and fade out.
        :param sampling_rate: the sampling rate of the resulting signal in Hz as
                              an integer or a float
        :param length: the number of samples of the window function
        :param symmetric: True, if the window's last sample shall be the same as
                          its first sample. False, if the window's last sample shall
                          be the same as its second sample. The latter is often
                          beneficial in segmentation applications, as it makes it
                          easier to meet the "constant overlap-add"-constraint.
        """
        self.__standard_deviation = standard_deviation
        Window.__init__(self, plateau=plateau, sampling_rate=sampling_rate, length=length, symmetric=symmetric)

    def _function(self, length):
        std = self.__standard_deviation * (length - 1) / 2.0
        return scipy.signal.windows.gaussian(length, std=std)

    def _label(self):
        return "Gaussian window"


class NuttallWindow(Window):
    """The family of Nuttall windows was proposed by Albert Nuttall in his paper
    "Some windows with very good side lobe behavior" from 1981. All of them are
    cosine-sum windows, that differ in the number of coefficients and the optimization
    constraints.

    The exact window function can be specified with the ``function`` parameter,
    that accepts a flag from the :attr:`~sumpf.NuttallWindow.functions` enumeration.
    The different flat top windows are explained in the documentation of the enumeration
    class. The default function is the four-term version, that is optimized for
    minimum side lobe level, which comes at the cost of having a slow decay of the
    side lobes with increasing frequency.
    """

    functions = sumpf_internal.NuttallWindows

    def __init__(self,
                 function=sumpf_internal.NuttallWindows.NUTTALL4C,
                 plateau=0,
                 sampling_rate=48000.0,
                 length=8192,
                 symmetric=True):
        """
        :param function: a flag from the :attr:`~sumpf.NuttallWindow.functions`
                         enumeration.
        :param plateau: an integer length or a float factor for the signal length,
                        that specifies, how many samples in the middle of the signal
                        shall be 1.0 without being affected by the window's fade
                        in and fade out.
        :param sampling_rate: the sampling rate of the resulting signal in Hz as
                              an integer or a float
        :param length: the number of samples of the window function
        :param symmetric: True, if the window's last sample shall be the same as
                          its first sample. False, if the window's last sample shall
                          be the same as its second sample. The latter is often
                          beneficial in segmentation applications, as it makes it
                          easier to meet the "constant overlap-add"-constraint.
        """
        self.__function = function
        Window.__init__(self, plateau=plateau, sampling_rate=sampling_rate, length=length, symmetric=symmetric)

    def _function(self, length):    # pylint: disable=too-many-return-statements; this is basically a large switch-statement
        if self.__function == NuttallWindow.functions.NUTTALL3:
            return scipy.signal.windows.general_cosine(length, (0.375, 0.5, 0.125))
        elif self.__function == NuttallWindow.functions.NUTTALL3A:
            return scipy.signal.windows.general_cosine(length, (0.40897, 0.5, 0.09103))
        elif self.__function == NuttallWindow.functions.NUTTALL3B:
            return scipy.signal.windows.general_cosine(length, (0.4243801, 0.4973406, 0.0782793))
        elif self.__function == NuttallWindow.functions.NUTTALL4:
            return scipy.signal.windows.general_cosine(length, (0.3125, 0.46875, 0.1875, 0.03125))
        elif self.__function == NuttallWindow.functions.NUTTALL4A:
            return scipy.signal.windows.general_cosine(length, (0.338946, 0.481973, 0.161054, 0.018027))
        elif self.__function == NuttallWindow.functions.NUTTALL4B:
            return scipy.signal.windows.general_cosine(length, (0.355768, 0.487396, 0.144232, 0.012604))
        elif self.__function == NuttallWindow.functions.NUTTALL4C:
            return scipy.signal.windows.general_cosine(length, (0.3635819, 0.4891775, 0.1365995, 0.0106411))
        else:
            raise ValueError(f"unknown Nuttall window: {self.__function}")

    def _label(self):
        return "Nuttall window"


class ParzenWindow(Window):
    """The Parzen window is is a piece-wise cubic approximation of the Gaussian
    window. But other than that, the Parzen window reaches zero at its ends, which
    gives it a side lobe decay of 24dB per octave.
    """

    def _function(self, length):
        return scipy.signal.windows.parzen(length)

    def _label(self):
        return "Parzen window"


class SlepianWindow(Window):
    """The Slepian window is the first order discrete prolate spheroidal sequence,
    which minimizes the energy of the side lobes in relation to the main lobe. It
    features a ``beta`` parameter, that allows to trade off side lobe suppression
    for a narrower bandwidth.
    """

    def __init__(self, beta=9.4248, plateau=0, sampling_rate=48000.0, length=8192, symmetric=True):
        """
        :param beta: the *beta* parameter for the Slepian window. Some literature
                     specifies an *alpha* parameter here, where *beta* = *pi* * *alpha*
        :param plateau: an integer length or a float factor for the signal length,
                        that specifies, how many samples in the middle of the signal
                        shall be 1.0 without being affected by the window's fade
                        in and fade out.
        :param sampling_rate: the sampling rate of the resulting signal in Hz as
                              an integer or a float
        :param length: the number of samples of the window function
        :param symmetric: True, if the window's last sample shall be the same as
                          its first sample. False, if the window's last sample shall
                          be the same as its second sample. The latter is often
                          beneficial in segmentation applications, as it makes it
                          easier to meet the "constant overlap-add"-constraint.
        """
        self.__beta = beta
        Window.__init__(self, plateau=plateau, sampling_rate=sampling_rate, length=length, symmetric=symmetric)

    def _function(self, length):
        if length <= 2:
            return numpy.ones(length)
        else:
            return scipy.signal.windows.dpss(length, NW=self.__beta / math.pi, norm="subsample")

    def _label(self):
        return "Slepian window"
