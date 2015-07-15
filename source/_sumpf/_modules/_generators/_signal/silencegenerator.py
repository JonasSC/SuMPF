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

from .signalgenerator import SignalGenerator


class SilenceGenerator(SignalGenerator):
    """
    Generates a Signal whose data is a sequence of 0.0 samples with the given
    length and the given sampling rate.
    The resulting Signal will have one channel.
    """
    def _GetSamples(self):
        """
        Generates the samples of a Signal which are all 0.0 and returns them as a tuple.
        @retval : a tuple of samples
        """
        return (0.0,) * self._length

    def _GetLabel(self):
        """
        Returns the label for the output Signal's channel.
        @retval : a string label
        """
        return "Silence"

