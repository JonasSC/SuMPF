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

class ChannelData(object):
    """
    A class for storing data in multiple channels.
    Each channel is a tuple of samples.
    All channels have the same length.
    The channels can have a label.
    """
    def __init__(self, channels, labels=()):
        """
        @param channels: a tuple of tuples of samples
        @param labels: a tuple of string labels for the channels
        """
        if len(channels) == 0 or len(channels[0]) < 2:
            raise ValueError("The new data set would be empty")
        tmpchannels = [tuple(channels[0])]
        for i in range(1, len(channels)):
            if len(channels[i]) != len(channels[0]):
                raise ValueError("The channels have different length")
            else:
                tmpchannels.append(tuple(channels[i]))
        self.__channels = tuple(tmpchannels)
        tmplabels = []
        for i in range(len(self.__channels)):
            if i < len(labels):
                if labels[i] is not None and not isinstance(labels[i], str):
                    raise TypeError("The labels have to be string values or None, not %s" % str(type(labels[i])))
                tmplabels.append(labels[i])
            else:
                tmplabels.append(None)
        self.__labels = tuple(tmplabels)

    def GetChannels(self):
        """
        Returns the channels of of the instance.
        @retval : the channel data. A tuple of channels, which themselves are a tuple of samples
        """
        return self.__channels

    def GetLabels(self):
        """
        Returns a tuple of string labels, one label for each channel.
        @retval : a tuple of string labels
        """
        return self.__labels

    def IsEmpty(self):
        """
        Returns if the data set is empty (all channels == (0.0, 0.0))
        @retval : True, if data set is empty, False otherwise
        """
        if len(self) == 2:
            for c in self.__channels:
                for s in c:
                    if s != 0.0:
                        return False
            return True
        return False

    def __eq__(self, other):
        """
        This method is called when two data sets are compared with ==. It returns
        True, when both data sets are equal and False otherwise.
        @param other: the data set to which this data set shall be compared
        @retval : True if data sets are equal, False otherwise
        """
        if self.GetChannels() != other.GetChannels():
            return False
        elif self.GetLabels() != other.GetLabels():
            return False
        else:
            return True

    def __ne__(self, other):
        """
        This method is called when two data sets are compared with !=. It returns
        True, when both data sets are not equal and False otherwise.
        @param other: the data set to which this data set shall be compared
        @retval : True if data sets are not equal, False otherwise
        """
        return not self == other

    def __len__(self):
        """
        Returns the number of samples per channel. All channels have the same length.
        @retval : the number of samples per channel
        """
        return len(self.__channels[0])

    def __div__(self, other):
        """
        This method is for compatibility with Python 2. The division of two data
        sets is implemented and documented in the __truediv__ method.
        """
        return self.__truediv__(other)

