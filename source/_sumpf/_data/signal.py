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

import collections
import sumpf
from .channeldata import ChannelData

try:
    import numpy
except ImportError:
    numpy = sumpf.helper.numpydummy



class Signal(ChannelData):
    """
    A class for storing data over time, like Audio Data.
    The data is stored in a tuple of channels, which themselves are a tuple of samples.
    The length of all channel tuples has to be the same.
    The sampling rate has to be valid for every channel
    """
    def __init__(self, channels=((0.0, 0.0),), samplingrate=None, labels=()):
        """
        @param channels: a tuple of tuples of float-samples
        @param samplingrate: the rate in Hz in which the samples have been recorded
        """
        if samplingrate is None:
            samplingrate = sumpf.config.get("default_samplingrate")
        ChannelData.__init__(self, channels, labels)
        self.__samplingrate = float(samplingrate)

    def GetSamplingRate(self):
        """
        @retval : the sampling rate of the signal
        """
        return self.__samplingrate

    def GetDuration(self):
        """
        Returns the duration of the Signal in seconds.
        @retval : a float that is the duration of the Signal in seconds
        """
        return len(self) / self.GetSamplingRate()

    def __repr__(self):
        """
        This method returns a string that is a valid Python expression to instantiate
        a Signal with the same values as this one.
        This method is called by the repr() built-in function or when the Signal
        instance is called in backquotes.
        @retval : the string of a valid Python expression to instantiate a Signal like this one.
        """
        return "Signal(channels=%s, samplingrate=%f, labels=%s)" % (repr(self.GetChannels()), self.GetSamplingRate(), repr(self.GetLabels()))

    def __str__(self):
        """
        This method returns a string that describes the Signal roughly.
        It is called by str() or print().
        @retval : an informal string representation of the Signal
        """
        return "<%s.Signal object (length: %i, sampling rate: %.2f, channel count: %i) at 0x%x>" % (self.__module__, len(self), self.GetSamplingRate(), len(self.GetChannels()), id(self))

    def __eq__(self, other):
        """
        This method is called when two Signals are compared with ==. It returns
        True, when both Signals are equal and False otherwise.
        @param other: the Signal to which this Signal shall be compared
        @retval : True if Signals are equal, False otherwise
        """
        if not isinstance(other, Signal):
            return False
        elif self.GetSamplingRate() != other.GetSamplingRate():
            return False
        else:
            return ChannelData.__eq__(self, other)

    def __getitem__(self, key):
        """
        This method is for slicing the Signal. It returns a Signal with the specified
        subset of this Signal's channels with the same sampling rate and labels.
        This method is only for slicing, not for accessing the samples of the
        Signal. Because of this a call like "signal[1]" raises an error.
        @param key: a slice object. Normally this method is called like "signal[2:5]", in which case the slice object is automatically generated from the "2:5"
        @retval : a Signal instance whose channels are the specified subset of this Signal's channels
        """
        if not isinstance(key, slice):
            raise ValueError("The [] operator for Signals is only for slicing. Access the samples through GetChannels()")
        elif key.step not in [None, 1]:
            raise ValueError("The [] operator for Signals does not support steps which are other than 1.")
        channels = []
        for c in self.GetChannels():
            channels.append(c[key.start:key.stop])
        return Signal(channels=tuple(channels), samplingrate=self.GetSamplingRate(), labels=self.GetLabels())

    def __add__(self, other):
        """
        A method for adding this Signal and another one.
        The result will be a newly created Signal instance. Neither this Signal
        nor the other Signal will be modified.
        The Signals must have the same length, sampling rate and channel count.
        The two Signals will be added channel per channel and sample per sample:
            self = sumpf.Signal(channels = ((1, 2), (3, 4)))
            other = sumpf.Signal(channels = ((5, 6), (7, 8)))
            self + other == sumpf.Signal(channels=((1+5, 2+6), (3+7, 4+8)))
        @param other: the Signal that shall be added to this one
        @retval : a Signal instance that is the sum of this Signal and the other one
        """
        if isinstance(other, (int, float)):
            channels = numpy.add(self.GetChannels(), other)
            labels = self.GetLabels()
        elif isinstance(other, collections.Iterable):
            if len(other) != len(self.GetChannels()):
                raise ValueError("The given tuple's length does not equal the number of channels")
            channels = [numpy.add(a, c) for a, c in zip(self.GetChannels(), other)]
            labels = self.GetLabels()
        else:
            self.__CheckOtherSignal(other)
            if other.IsEmpty():
                channels = self.GetChannels()
            else:
                channels = numpy.add(self.GetChannels(), other.GetChannels())
            labels = tuple(["Sum %i" % (i + 1) for i in range(len(channels))])
        return Signal(channels=channels, samplingrate=self.GetSamplingRate(), labels=labels)

    def __radd__(self, other):
        """
        This method is for adding a scalar value to this Signal's samples.
        @param other: a value which shall be added to the Signal
        @retval : a Signal instance whose samples are this Signal's samples added with the value
        """
        return self +other

    def __sub__(self, other):
        """
        A method for subtracting another Signal from this one.
        The result will be a newly created Signal instance. Neither this Signal
        nor the other Signal will be modified.
        The Signals must have the same length, sampling rate and channel count.
        The two Signals will be subtracted channel per channel and sample per sample:
            self = sumpf.Signal(channels = ((1, 2), (3, 4)))
            other = sumpf.Signal(channels = ((5, 6), (7, 8)))
            self - other == sumpf.Signal(channels=((1-5, 2-6), (3-7, 4-8)))
        @param other: the Signal that shall be subtracted from this one
        @retval : a Signal instance that is the difference of this Signal and the other one
        """
        if isinstance(other, (int, float)):
            channels = numpy.subtract(self.GetChannels(), other)
            labels = self.GetLabels()
        elif isinstance(other, collections.Iterable):
            if len(other) != len(self.GetChannels()):
                raise ValueError("The given tuple's length does not equal the number of channels")
            channels = [numpy.subtract(a, c) for a, c in zip(self.GetChannels(), other)]
            labels = self.GetLabels()
        else:
            self.__CheckOtherSignal(other)
            if other.IsEmpty():
                channels = self.GetChannels()
            else:
                if self.IsEmpty():
                    channels = numpy.subtract(0.0, other.GetChannels())
                else:
                    channels = numpy.subtract(self.GetChannels(), other.GetChannels())
                labels = tuple([" %i" % (i + 1) for i in range(max(len(self.GetChannels()), len(other.GetChannels())))])
            labels = tuple(["Difference %i" % (i + 1) for i in range(len(channels))])
        return Signal(channels=channels, samplingrate=self.GetSamplingRate(), labels=labels)

    def __rsub__(self, other):
        """
        This method is for subtracting this Signal's samples from a scalar value.
        @param other: a value from which this Signal's samples shall be subtracted
        @retval : a Signal instance whose samples are the value minus this Signal's samples
        """
        if isinstance(other, collections.Iterable):
            if len(other) != len(self.GetChannels()):
                raise ValueError("The given tuple's length does not equal the number of channels")
            channels = [numpy.subtract(c, a) for a, c in zip(self.GetChannels(), other)]
        else:
            channels = numpy.subtract(other, self.GetChannels())
        return Signal(channels=channels, samplingrate=self.GetSamplingRate(), labels=self.GetLabels())

    def __mul__(self, other):
        """
        A method for multiplying this Signal and another one or a scalar factor.
        The result will be a newly created Signal instance. Neither this Signal
        nor the other Signal will be modified.
        The Signals must have the same length, sampling rate and channel count.
        The two Signals will be multiplied channel per channel and sample per sample:
            self = sumpf.Signal(channels = ((1, 2), (3, 4)))
            other = sumpf.Signal(channels = ((5, 6), (7, 8)))
            self * other == sumpf.Signal(channels=((1*5, 2*6), (3*7, 4*8)))
        If the other factor is a scalar value, the Signal will be amplified accordingly.
        @param other: the Signal or a factor that shall be multiplied with this one
        @retval : a Signal instance that is the product of this Signal and the other one
        """
        if isinstance(other, (int, float)):
            channels = numpy.multiply(self.GetChannels(), other)
            labels = self.GetLabels()
        elif isinstance(other, collections.Iterable):
            if len(other) != len(self.GetChannels()):
                raise ValueError("The given tuple's length does not equal the number of channels")
            channels = [numpy.multiply(a, c) for a, c in zip(self.GetChannels(), other)]
            labels = self.GetLabels()
        else:
            self.__CheckOtherSignal(other)
            if other.IsEmpty():
                channels = self.GetChannels()
            else:
                channels = numpy.multiply(self.GetChannels(), other.GetChannels())
            labels = tuple(["Product %i" % (i + 1) for i in range(len(channels))])
        return Signal(channels=channels, samplingrate=self.GetSamplingRate(), labels=labels)

    def __rmul__(self, other):
        """
        This method is for multiplying a scalar factor with this Signal.
        @param other: a factor by which this Signal shall be amplified
        @retval : a Signal instance whose samples are this Signal's samples amplified by the factor
        """
        return self * other

    def __truediv__(self, other):
        """
        A method for dividing this Signal by another one.
        The result will be a newly created Signal instance. Neither this Signal
        nor the other Signal will be modified.
        The Signals must have the same length, sampling rate and channel count.
        The two Signals will be divided channel per channel and sample per sample:
            self = sumpf.Signal(channels = ((1, 2), (3, 4)))
            other = sumpf.Signal(channels = ((5, 6), (7, 8)))
            self / other == sumpf.Signal(channels=((1/5, 2/6), (3/7, 4/8)))
        @param other: the Signal by that this one shall be divided
        @retval : a Signal instance that is the quotient of this Signal and the other one
        """
        selfvalue = self.GetChannels()
        if isinstance(other, (int, float)):
            if other == 0.0:
                raise ZeroDivisionError("Signal division by zero")
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
            self.__CheckOtherSignal(other)
            if self.IsEmpty():
                selfvalue = 0.0
            elif len(other) != len(self):
                raise ValueError("The other Signal has a different length")
            for c in other.GetChannels():
                if numpy.prod(numpy.shape(numpy.nonzero(c))) == 0:
                    raise ZeroDivisionError("Signal division by a Signal with only 0.0-samples")
            channels = numpy.true_divide(selfvalue, other.GetChannels())
            labels = tuple(["Quotient %i" % (i + 1) for i in range(max(len(self.GetChannels()), len(other.GetChannels())))])
        return Signal(channels=channels, samplingrate=self.GetSamplingRate(), labels=labels)

    def __rtruediv__(self, other):
        """
        This method is for dividing a scalar value by the samples of this Signal.
        @param other: a value which shall be divided
        @retval : a Signal instance whose samples are the value divided by this Signal's samples
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
        return Signal(channels=channels, samplingrate=self.GetSamplingRate(), labels=self.GetLabels())

    def __rdiv__(self, other):
        """
        The same as __rtruediv__. For backwards compatibility with Python 2.
        """
        return self.__rtruediv__(other)

    def __CheckOtherSignal(self, other):
        """
        Checks if the other Signal is compatible to this one, by comparing the
        length and the sampling rate.
        An error is raised, when the Signals are not compatible.
        @param other: the other Signal that shall be compared to this one
        """
        if other.GetSamplingRate() != self.GetSamplingRate():
            raise ValueError("The other Signal has a different sampling rate")
        if len(other.GetChannels()) != len(self.GetChannels()) and 1 not in (len(other.GetChannels()), len(self.GetChannels())):
            raise ValueError("The other Signal has a different number of channels")
        if not (self.IsEmpty() or other.IsEmpty()):
            if len(other) != len(self):
                raise ValueError("The other Signal has a different length")

