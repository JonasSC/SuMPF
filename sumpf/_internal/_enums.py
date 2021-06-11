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

"""Contains enumeration classes."""

import enum

__all__ = ("ConvolutionMode",
           "MergeMode",
           "ShiftMode",
           "NuttallWindows", "FlatTopWindows",
           "Interpolations")


class ConvolutionMode(enum.Enum):
    """An enumeration of flags, which define a mode, in which a convolution or
    a correlation shall be computed:

    * ``FULL`` corresponds to the `full` mode of :func:`numpy.convolve` or :func:`numpy.correlate`.
    * ``SAME`` corresponds to the `same` mode of :func:`numpy.convolve`.
    * ``VALID`` corresponds to the `valid` mode of :func:`numpy.convolve` or :func:`numpy.correlate`.
    * ``SPECTRUM`` performs a multiplication in the frequency domain. If one signal
      shorter is shorter than the other, it will be padded with zeros prior to
      the Fourier transformation.
    * ``SPECTRUM_PADDED`` also a multiplication in the frequency domain, but the
      zero padding of both signals will be long enough to avoid the effects of
      circular convolution/correlation.
    """
    FULL = enum.auto()
    SAME = enum.auto()
    VALID = enum.auto()
    SPECTRUM = enum.auto()
    SPECTRUM_PADDED = enum.auto()


class MergeMode(enum.Enum):
    """An enumeration of flags, with which the merging strategy can be defined:

    * with ``FIRST_DATASET_FIRST``, the first channels of the merged data set will
      be the channels of the first data set, that was added to the merger.
    * with ``FIRST_CHANNELS_FIRST``, the first channels of the merged data set will
      be the first channel of each added data set. After that, the second channels
      of each data set will be added and so on, until all channels have been added
      to the result data set.
    """
    FIRST_DATASET_FIRST = enum.auto()
    FIRST_CHANNELS_FIRST = enum.auto()


class ShiftMode(enum.Enum):
    """An enumeration of flags, that define how the :meth:`~sumpf.Signal.shift`
    method shall operate:

    * in mode ``OFFSET``, the shifting will be performed by adjusting the shifted
      signal's offset parameter. The signal's channels remain the same.
    * in mode ``CROP``, the signal's samples will be shifted, while now the empty
      samples at the beginning or the end of the signal will be filled with zeros.
      In this mode, the shape of the signal's channels array remains the same as in
      the original signal, so that the samples, that are shifted over the signal's
      boundaries are cropped. The signal's offset remains the same.
    * in mode ``PAD``, the signal will be shifted and padded, just like in mode
      ``CROP``, but the channel's are extended, so that no samples are cropped.
      The signal's offset also remains the same.
    * in mode ``CYCLE``, the shift will be performed in a cyclic manner, which means,
      that the samples, that are shifted over the signal's boundaries, are inserted
      at the other end. The signal's offset and shape remain the same and no zeros
      are added.
    """
    OFFSET = enum.auto()
    CROP = enum.auto()
    PAD = enum.auto()
    CYCLE = enum.auto()


class NuttallWindows(enum.Enum):
    """This enumeration defines flags to specify the variant of Nuttall window,
    when instantiating the :class:`~sumpf.NuttallWindow` class.

    The names of this enumeration's flags are taken from the paper `Spectrum and
    spectral density estimation by the Discrete Fourier transform (DFT), including
    a comprehensive list of window functions and some new flat-top windows
    <https://holometer.fnal.gov/GH_FFT.pdf#page=33>`__ by G. Heinzel, A. Rüdiger and
    R. Schilling, which was published by the Max-Planck-Institut für Gravitationsphysik
    in February 2002.

    * ``NUTTALL3`` is a three-term cosine-sum window with maximum decay of the side
      lobes of 30dB per octave, which comes at the cost of having a high side lobe
      level of -46.7dB to begin with.
    * ``NUTTALL3A`` is also a three-term cosine-sum window, that has a reduced
      maximum side lobe level of -64.2dB, but also a reduced side lobe decay of
      only 18dB per octave in comparison to ``NUTTALL3``.
    * ``NUTTALL3B`` is a three-term cosine-sum window, that has a side lobe decay
      of only 6dB per octave, but maximally suppressed side lobes -71.5dB.
    * ``NUTTALL4`` is a four-term cosine-sum window with maximum decay of the side
      lobes of 42dB per octave, which comes at the cost of having a relatively
      high side lobe level of -60.9dB.
    * ``NUTTALL4A`` is also a four-term cosine-sum window, that has a reduced
      maximum side lobe level of -82.6dB, but also a slightly reduced side lobe
      decay of only 30dB per octave in comparison to ``NUTTALL4``.
    * ``NUTTALL4B`` is also a four-term cosine-sum window, that has a further reduced
      maximum side lobe level of -93.3dB, but also a reduced side lobe decay of
      only 18dB per octave in comparison to ``NUTTALL4`` and ``NUTTALL4A``.
    * ``NUTTALL4C`` is a four-term cosine-sum window, that has a side lobe decay
      of only 6dB per octave, but maximally suppressed side lobes -98.1dB.
    """
    NUTTALL3 = enum.auto()
    NUTTALL3A = enum.auto()
    NUTTALL3B = enum.auto()
    NUTTALL4 = enum.auto()
    NUTTALL4A = enum.auto()
    NUTTALL4B = enum.auto()
    NUTTALL4C = enum.auto()


class FlatTopWindows(enum.Enum):
    """This enumeration defines flags to specify the flat top window, when instantiating
    the :class:`~sumpf.FlatTopWindow` class.

    Due to advances in optimization techniques, there are some flat top windows,
    which have been optimized with the same target, but have different functions,
    nevertheless. For example, the ``HFT`` windows tend to be better optimized
    than the ``SFT`` family of windows.

    Most names and functions of this enumeration's flags are taken from the paper
    `Spectrum and spectral density estimation by the Discrete Fourier transform
    (DFT), including a comprehensive list of window functions and some new flat-top
    windows <https://holometer.fnal.gov/GH_FFT.pdf#page=38>`__ by G. Heinzel,
    A. Rüdiger and R. Schilling, which was published by the Max-Planck-Institut
    für Gravitationsphysik in February 2002.

    * ``DEFAULT`` uses the :func:`scipy.signal.windows.flattop` function.
    * ``SFT3F`` is a three-term cosine-sum window, which is optimized for a fast
      decay of the side lobes.
    * ``SFT4F`` is a four-term cosine-sum window, which is optimized for a fast
      decay of the side lobes.
    * ``SFT5F`` is a five-term cosine-sum window, which is optimized for a fast
      decay of the side lobes.
    * ``SFT3M`` is a three-term cosine-sum window, which is optimized for maximum
      side lobe suppression.
    * ``SFT4M`` is a four-term cosine-sum window, which is optimized for maximum
      side lobe suppression.
    * ``SFT5M`` is a five-term cosine-sum window, which is optimized for maximum
      side lobe suppression.
    * ``FTNI`` is a flat top window, that has been published by National Instruments.
    * ``FTHP`` is a flat top window, that has been used in older HP spectrum analyzers.
    * ``FTSRS`` is a flat top window, that is used in the Stanford Research SR785
      spectrum analyzer.
    * ``HFT70`` is a four-term cosine-sum window, which is optimized for maximum
      side lobe suppression.
    * ``HFT90D`` is a five-term cosine-sum window, which is optimized for maximum
      side lobe suppression, while having a 18dB per octave decay of the side lobes.
    * ``HFT95`` is a five-term cosine-sum window, which is optimized for maximum
      side lobe suppression.
    * ``HFT116D`` is a six-term cosine-sum window, which is optimized for maximum
      side lobe suppression, while having a 18dB per octave decay of the side lobes.
    * ``HFT144D`` is a seven-term cosine-sum window, which is optimized for maximum
      side lobe suppression, while having a 18dB per octave decay of the side lobes.
    * ``HFT169D`` is a eight-term cosine-sum window, which is optimized for maximum
      side lobe suppression, while having a 18dB per octave decay of the side lobes.
    * ``HFT196D`` is a nine-term cosine-sum window, which is optimized for maximum
      side lobe suppression, while having a 18dB per octave decay of the side lobes.
    * ``HFT223D`` is a ten-term cosine-sum window, which is optimized for maximum
      side lobe suppression, while having a 18dB per octave decay of the side lobes.
    * ``HFT248D`` is a eleven-term cosine-sum window, which is optimized for maximum
      side lobe suppression, while having a 18dB per octave decay of the side lobes.
    """
    DEFAULT = enum.auto()
    SFT3F = enum.auto()
    SFT4F = enum.auto()
    SFT5F = enum.auto()
    SFT3M = enum.auto()
    SFT4M = enum.auto()
    SFT5M = enum.auto()
    FTNI = enum.auto()
    FTHP = enum.auto()
    FTSRS = enum.auto()
    HFT70 = enum.auto()
    HFT90D = enum.auto()
    HFT95 = enum.auto()
    HFT116D = enum.auto()
    HFT144D = enum.auto()
    HFT169D = enum.auto()
    HFT196D = enum.auto()
    HFT223D = enum.auto()
    HFT248D = enum.auto()


class Interpolations(enum.IntEnum):     # must be an IntEnum in order to allow serializing a Bands-Filter to JSON
    """This enumeration defines flags to specify an interpolation function.

    * ``ZERO`` fills the unknown places with zeros. The result of this interpolation
      will be an all-zero sequence, if none of the samples falls exactly on one
      of the supporting points of the interpolated function.
    * ``ONE`` fills the unknown places with ones. The result of this interpolation
      will be an all-ones sequence, if none of the samples falls exactly on one
      of the supporting points of the interpolated function.
    * ``LINEAR`` specifies a linear interpolation between two neighboring supporting
      points. If this interpolation is used as extrapolation, the straight line
      through the two nearest supporting points is used.
    * ``LOGARITHMIC`` specifies a logarithmic interpolation between two neighboring
      supporting points. For this, the logarithms of both the x-values and the
      y-values of the supporting points are used for a linear interpolation.
    * ``LOG_X`` specifies a semi-logarithmic interpolation between two neighboring
      supporting points. For this, the logarithm of the x-values and the linear
      y-values of the supporting points are used for a linear interpolation. This
      interpolation might be useful to interpolate dB-representations of n-th octave
      analyses. When such data sets are plotted with a logarithmic frequency axis
      and a linear magnitude axis (since the magnitudes are already in dB), the
      interpolation will yield a straight line in the plot.
    * ``LOG_Y`` specifies a semi-logarithmic interpolation between two neighboring
      supporting points. For this, the linear x-values and the linear of the supporting
      points and logarithmic y-values are used for a linear interpolation.
    * ``STAIRS_LIN`` will use the supporting point with the nearest x-value as
      the interpolation value.
    * ``STAIRS_LOG`` will use the supporting point with the nearest x-value on a
      logarithmic x-axis as the interpolation value.
    """
    ZERO = enum.auto()
    ONE = enum.auto()
    LINEAR = enum.auto()
    LOGARITHMIC = enum.auto()
    LOG_X = enum.auto()
    LOG_Y = enum.auto()
    STAIRS_LIN = enum.auto()
    STAIRS_LOG = enum.auto()
