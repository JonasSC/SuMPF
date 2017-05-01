# SuMPF - Sound using a Monkeyforest-like processing framework
# Copyright (C) 2012-2017 Jonas Schulte-Coerne
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
import math

import sumpf
from .channeldata import ChannelData

try:
    import numpy
except ImportError:
    numpy = sumpf.helper.numpydummy



class Spectrum(ChannelData):
    """
    A class whose instances store magnitude and phase data over a frequency range.
    The length of all channel tuples has to be the same.
    The frequency resolution has to be valid for every channel
    """
    def __init__(self, channels=((0.0, 0.0),), resolution=24000.0, labels=()):
        """
        @param channels: a tuple of tuples of complex-samples
        @param resolution: the frequency resolution of the spectrum
        """
        ChannelData.__init__(self, channels, labels)
        self.__resolution = float(resolution)

    def GetMagnitude(self):
        """
        @retval : a tuple of channels which are a tuple of samples which represent the magnitude of the spectrum
        """
        result = []
        for c in self.GetChannels():
            result.append(tuple(numpy.abs(c)))
        return tuple(result)

    def GetPhase(self):
        """
        @retval : a tuple of channels which are a tuple of samples which represent the phase of the spectrum
        """
        result = []
        for c in self.GetChannels():
            result.append(tuple(numpy.angle(c)))
        return tuple(result)

    def GetReal(self):
        """
        @retval : a tuple of channels which are a tuple of samples which represent the real part of the spectrum
        """
        return tuple(tuple(numpy.real(c)) for c in self.GetChannels())

    def GetImaginary(self):
        """
        @retval : a tuple of channels which are a tuple of samples which represent the imaginary part of the spectrum
        """
        return tuple(tuple(numpy.imag(c)) for c in self.GetChannels())

    def GetGroupDelay(self):
        """
        @retval : a tuple of channels which are a tuple of samples which represent the group delay of the spectrum
        """
        result = []
        for c in self.GetContinuousPhase():
            derivative = sumpf.helper.differentiate(c)
            group_delay = tuple(numpy.multiply(derivative, -0.5 / math.pi))
            result.append(group_delay)
        return result

    def GetContinuousPhase(self):
        """
        This method tries to calculate the samples for a continuous phase that
        does not oscillate between -pi and pi.
        For random phase spectrums like those of noise, the algorithm may not be
        able to calculate reasonable values.
        @retval : a tuple of channels which are a tuple of samples which represent the continuous phase of the spectrum
        """
        result = []
        for c in self.GetPhase():
            continuous_phase = [c[0]]
            offset = 0.0
            diff = 0.0
            for i in range(1, len(c)):
                if c[i] - (c[i - 1] + diff) > math.pi:
                    offset -= 2.0 * math.pi
                elif c[i] - (c[i - 1] + diff) < -math.pi:
                    offset += 2.0 * math.pi
                continuous_phase.append(c[i] + offset)
                diff = continuous_phase[-1] - continuous_phase[-2]
            result.append(continuous_phase)
        return result

    def GetResolution(self):
        """
        @retval : the frequency resolution of the spectrum in Hz
        """
        return self.__resolution

    def __repr__(self):
        """
        This method returns a string that is a valid Python expression to instantiate
        a Spectrum with the same values as this one.
        This method is called by the repr() built-in function or when the Spectrum
        instance is called in backquotes.
        @retval : the string of a valid Python expression to instantiate a Spectrum like this one.
        """
        return "Spectrum(channels=%s, resolution=%f, labels=%s)" % (repr(self.GetChannels()), self.GetResolution(), repr(self.GetLabels()))

    def __str__(self):
        """
        This method returns a string that describes the Spectrum roughly.
        It is called by str() or print().
        @retval : an informal string representation of the Spectrum
        """
        return "<%s.Spectrum object (length: %i, resolution: %.2f, channel count: %i) at 0x%x>" % (self.__module__, len(self), self.GetResolution(), len(self.GetChannels()), id(self))

    def __eq__(self, other):
        """
        This method is called when two Spectrums are compared with ==. It returns
        True, when both Spectrums are equal and False otherwise.
        @param other: the Spectrum to which this Spectrum shall be compared
        @retval : True if Spectrums are equal, False otherwise
        """
        if not isinstance(other, Spectrum):
            return False
        elif self.GetResolution() != other.GetResolution():
            return False
        else:
            return ChannelData.__eq__(self, other)

    def __add__(self, other):
        """
        A method for adding this Spectrum and another one.
        The result will be a newly created Spectrum instance. Neither this Spectrum
        nor the other Spectrum will be modified.
        The Spectrums must have the same length and resolution. The channel count
        of both Spectrums has to be equal or one Spectrum has to have a channel
        count of one.
        The two Spectrums will be added channel per channel and sample per sample:
            self = sumpf.Spectrum(channels = ((1, 2), (3, 4)))
            other = sumpf.Spectrum(channels = ((5, 6), (7, 8)))
            self + other == sumpf.Spectrum(channels=((1+5, 2+6), (3+7, 4+8)))
        """
        if isinstance(other, (int, float, complex)):
            channels = numpy.add(self.GetChannels(), other)
            labels = self.GetLabels()
        elif isinstance(other, collections.Iterable):
            if len(other) != len(self.GetChannels()):
                raise ValueError("The given tuple's length does not equal the number of channels")
            channels = [numpy.add(a, c) for a, c in zip(self.GetChannels(), other)]
            labels = self.GetLabels()
        else:
            self.__CheckOtherSpectrum(other)
            channels = numpy.add(self.GetChannels(), other.GetChannels())
            labels = tuple(["Sum %i" % (i + 1) for i in range(len(channels))])
        return Spectrum(channels=channels, resolution=self.GetResolution(), labels=labels)

    def __radd__(self, other):
        """
        This method is for adding a scalar value to this Spectrum's samples.
        @param other: a value which shall be added to the Spectrum
        @retval : a Spectrum instance whose samples are this Spectrum's samples added with the value
        """
        return self +other

    def __sub__(self, other):
        """
        A method for subtracting another Spectrum from this one.
        The result will be a newly created Spectrum instance. Neither this Spectrum
        nor the other Spectrum will be modified.
        The Spectrums must have the same length and resolution. The channel count
        of both Spectrums has to be equal or one Spectrum has to have a channel
        count of one.
        The two Spectrums will be subtracted channel per channel and sample per sample:
            self = sumpf.Spectrum(channels = ((1, 2), (3, 4)))
            other = sumpf.Spectrum(channels = ((5, 6), (7, 8)))
            self - other == sumpf.Spectrum(channels=((1-5, 2-6), (3-7, 4-8)))
        """
        if isinstance(other, (int, float, complex)):
            channels = numpy.subtract(self.GetChannels(), other)
            labels = self.GetLabels()
        elif isinstance(other, collections.Iterable):
            if len(other) != len(self.GetChannels()):
                raise ValueError("The given tuple's length does not equal the number of channels")
            channels = [numpy.subtract(a, c) for a, c in zip(self.GetChannels(), other)]
            labels = self.GetLabels()
        else:
            self.__CheckOtherSpectrum(other)
            channels = numpy.subtract(self.GetChannels(), other.GetChannels())
            labels = tuple(["Difference %i" % (i + 1) for i in range(len(channels))])
        return Spectrum(channels=channels, resolution=self.GetResolution(), labels=labels)

    def __rsub__(self, other):
        """
        This method is for subtracting this Spectrum's samples from a scalar value.
        @param other: a value from which this Spectrum's samples shall be subtracted
        @retval : a Spectrum instance whose samples are the value minus this Spectrum's samples
        """
        if isinstance(other, collections.Iterable):
            if len(other) != len(self.GetChannels()):
                raise ValueError("The given tuple's length does not equal the number of channels")
            channels = [numpy.subtract(c, a) for a, c in zip(self.GetChannels(), other)]
        else:
            channels = numpy.subtract(other, self.GetChannels())
        return Spectrum(channels=channels, resolution=self.GetResolution(), labels=self.GetLabels())

    def __mul__(self, other):
        """
        A method for multiplying this Spectrum and another one or a scalar factor.
        The result will be a newly created Spectrum instance. Neither this Spectrum
        nor the other Spectrum will be modified.
        The Spectrums must have the same length and resolution. The channel count
        of both Spectrums has to be equal or one Spectrum has to have a channel
        count of one.
        The two Spectrums will be multiplied channel per channel and sample per sample:
            self = sumpf.Spectrum(channels = ((1, 2), (3, 4)))
            other = sumpf.Spectrum(channels = ((5, 6), (7, 8)))
            self * other == sumpf.Spectrum(channels=((1*5, 2*6), (3*7, 4*8)))
        If the other factor is a scalar value, the Spectrum will be amplified accordingly.
        @param other: the Spectrum or a factor that shall be multiplied with this one
        @retval : a Spectrum instance that is the product of this Spectrum and the other one
        """
        if isinstance(other, (int, float, complex)):
            channels = numpy.multiply(self.GetChannels(), other)
            labels = self.GetLabels()
        elif isinstance(other, collections.Iterable):
            if len(other) != len(self.GetChannels()):
                raise ValueError("The given tuple's length does not equal the number of channels")
            channels = [numpy.multiply(a, c) for a, c in zip(self.GetChannels(), other)]
            labels = self.GetLabels()
        else:
            self.__CheckOtherSpectrum(other)
            channels = numpy.multiply(self.GetChannels(), other.GetChannels())
            labels = tuple(["Product %i" % (i + 1) for i in range(len(channels))])
        return Spectrum(channels=channels, resolution=self.GetResolution(), labels=labels)

    def __rmul__(self, other):
        """
        This method is for multiplying a scalar factor with this Spectrum.
        @param other: a factor by which this Spectrum shall be amplified
        @retval : a Spectrum instance whose samples are this Spectrum's samples amplified by the factor
        """
        return self * other

    def __truediv__(self, other):
        """
        A method for dividing this Spectrum by another one.
        The result will be a newly created Spectrum instance. Neither this Spectrum
        nor the other Spectrum will be modified.
        The Spectrums must have the same length and resolution. The channel count
        of both Spectrums has to be equal or one Spectrum has to have a channel
        count of one.
        The two Spectrums will be divided channel per channel and sample per sample:
            self = sumpf.Spectrum(channels = ((1, 2), (3, 4)))
            other = sumpf.Spectrum(channels = ((5, 6), (7, 8)))
            self / other == sumpf.Spectrum(channels=((1/5, 2/6), (3/7, 4/8)))
        """
        selfvalue = self.GetChannels()
        if isinstance(other, (int, float, complex)):
            if other == 0.0:
                raise ZeroDivisionError("Spectrum division by zero")
            labels = self.GetLabels()
            channels = numpy.true_divide(selfvalue, other)
        elif isinstance(other, collections.Iterable):
            if len(other) != len(self.GetChannels()):
                raise ValueError("The given tuple's length does not equal the number of channels")
            for f in other:
                if f == 0:
                    raise ZeroDivisionError("Signal division by a zero")
            channels = [numpy.true_divide(a, c) for a, c in zip(self.GetChannels(), other)]
            labels = self.GetLabels()
        else:
            self.__CheckOtherSpectrum(other)
            if len(other) != len(self):
                raise ValueError("The other Spectrum has a different length")
            for c in other.GetChannels():
                if numpy.prod(numpy.shape(numpy.nonzero(c))) == 0:
                    raise ZeroDivisionError("Spectrum division by a Spectrum with only 0.0-samples")
            channels = numpy.true_divide(selfvalue, other.GetChannels())
            labels = tuple(["Quotient %i" % (i + 1) for i in range(max(len(self.GetChannels()), len(other.GetChannels())))])
        return Spectrum(channels=channels, resolution=self.GetResolution(), labels=labels)

    def __rtruediv__(self, other):
        """
        This method is for dividing a scalar value by the samples of this Spectrum.
        @param other: a value which shall be divided
        @retval : a Spectrum instance whose samples are the value divided by this Spectrum's samples
        """
        for c in self.GetChannels():
            if numpy.prod(numpy.shape(numpy.nonzero(c))) == 0:
                raise ZeroDivisionError("Signal division by a Signal with only 0.0-samples")
        if isinstance(other, collections.Iterable):
            if len(other) != len(self.GetChannels()):
                raise ValueError("The given tuple's length does not equal the number of channels")
            channels = [numpy.true_divide(c, a) for a, c in zip(self.GetChannels(), other)]
        else:
            channels = numpy.true_divide(other, self.GetChannels())
        return Spectrum(channels=channels, resolution=self.GetResolution(), labels=self.GetLabels())

    def __rdiv__(self, other):
        """
        The same as __rtruediv__. For backwards compatibility with Python 2.
        """
        return self.__rtruediv__(other)

    def __pow__(self, other):
        """
        A method for computing the power of a Spectrum, in which the other Spectrum
        is the exponent.
        The result will be a newly created Spectrum instance. Neither this Spectrum
        nor the other Spectrum will be modified.
        The Spectrums must have the same length and resolution. The channel count
        of both Spectrums has to be equal or one Spectrum has to have a channel
        count of one.
        The power will be computed channel per channel and sample per sample:
            self = sumpf.Spectrum(channels = ((1, 2), (3, 4)))
            other = sumpf.Spectrum(channels = ((5, 6), (7, 8)))
            self ** other == sumpf.Spectrum(channels=((1**5, 2**6), (3**7, 4**8)))
        @param other: the Spectrum that contains the exponents for the power
        @retval : a Spectrum instance that is the power
        """
        if isinstance(other, (int, float)):
            if int(other) != other:
                try:
                    if numpy.min(self.GetChannels()) < 0.0:
                        channels = numpy.power(numpy.complex_(self.GetChannels()), other)
                    else:
                        channels = numpy.power(self.GetChannels(), other)
                except TypeError:   # computing the minimum of a complex spectrum can raise a TypeError, because complex numbers have no order
                    channels = numpy.power(self.GetChannels(), other)
            else:
                channels = numpy.power(self.GetChannels(), other)
            labels = self.GetLabels()
        elif isinstance(other, complex):
            for c in self.GetChannels():
                if numpy.prod(numpy.shape(numpy.nonzero(c))) == 0:
                    raise ZeroDivisionError("Cannot compute the power of a Spectrum with only 0.0-samples to a complex exponent")
            channels = numpy.power(self.GetChannels(), other)
            labels = self.GetLabels()
        elif isinstance(other, collections.Iterable):
            if len(other) != len(self.GetChannels()):
                raise ValueError("The given tuple's length does not equal the number of channels")
            elif any(isinstance(f, complex) for f in other):
                for c in self.GetChannels():
                    if numpy.prod(numpy.shape(numpy.nonzero(c))) == 0:
                        raise ZeroDivisionError("Cannot compute the power of a Spectrum with only 0.0-samples to a complex exponent")
            elif any(int(f) != f for f in other):
                try:
                    if numpy.min(self.GetChannels()) < 0.0:
                        channels = [numpy.power(a, c) for a, c in zip(numpy.complex_(self.GetChannels()), other)]
                    else:
                        channels = [numpy.power(a, c) for a, c in zip(self.GetChannels(), other)]
                except TypeError:   # computing the minimum of a complex spectrum can raise a TypeError, because complex numbers have no order
                    channels = [numpy.power(a, c) for a, c in zip(self.GetChannels(), other)]
            else:
                channels = [numpy.power(a, c) for a, c in zip(self.GetChannels(), other)]
            labels = self.GetLabels()
        else:
            self.__CheckOtherSpectrum(other)
            for c in self.GetChannels():
                if numpy.prod(numpy.shape(numpy.nonzero(c))) == 0:
                    raise ZeroDivisionError("Cannot compute the power of a Spectrum with only 0.0-samples to a complex exponent")
            try:
                if numpy.min(self.GetChannels()) < 0.0:
                    channels = numpy.power(numpy.complex_(self.GetChannels()), other.GetChannels())
                else:
                    channels = numpy.power(self.GetChannels(), other.GetChannels())
            except TypeError:   # computing the minimum of a complex spectrum can raise a TypeError, because complex numbers have no order
                channels = numpy.power(self.GetChannels(), other.GetChannels())
            labels = tuple(["Power %i" % (i + 1) for i in range(max(len(self.GetChannels()), len(other.GetChannels())))])
        return Spectrum(channels=channels, resolution=self.GetResolution(), labels=labels)

    def __rpow__(self, other):
        """
        This method is for computing the power of a scalar value, where the exponent
        is this Spectrum.
        @param other: the base for the computation of the power
        @retval : a Spectrum instance whose samples are the power of the given value to this Spectrum's samples
        """
        if isinstance(other, collections.Iterable):
            if len(other) != len(self.GetChannels()):
                raise ValueError("The given tuple's length does not equal the number of channels")
            elif numpy.prod(numpy.shape(numpy.nonzero(other))) == 0:
                raise ZeroDivisionError("Cannot compute the power of a Spectrum with only 0.0-samples to a complex exponent")
            if not any(isinstance(f, complex) for f in other) and min(other) < 0.0:
                channels = [numpy.power(c, a) for a, c in zip(self.GetChannels(), numpy.complex_(other))]
            else:
                channels = [numpy.power(c, a) for a, c in zip(self.GetChannels(), other)]
        else:
            if other == 0.0:
                raise ZeroDivisionError("Cannot compute the power of a Spectrum with only 0.0-samples to a complex exponent")
            if not isinstance(other, complex) and other < 0.0:
                channels = numpy.power(complex(other), self.GetChannels())
            else:
                channels = numpy.power(other, self.GetChannels())
        return Spectrum(channels=channels, resolution=self.GetResolution(), labels=self.GetLabels())

    def __CheckOtherSpectrum(self, other):
        """
        Checks if the other Spectrum is compatible to this one, by comparing the
        length and the resolution.
        An error is raised, when the Spectrums are not compatible.
        @param other: the other Spectrum that shall be compared to this one
        """
        if other.GetResolution() != self.GetResolution():
            raise ValueError("The other Spectrum has a different resolution")
        if len(other.GetChannels()) != len(self.GetChannels()) and 1 not in (len(other.GetChannels()), len(self.GetChannels())):
            raise ValueError("The other Spectrum has a different number of channels")
        if len(other) != len(self):
            raise ValueError("The other Spectrum has a different length (expected %s, got %s)" % (len(self), len(other)))

