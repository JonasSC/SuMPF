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
This name space contains classes that are used by SuMPF internally.
These classes are mainly abstract base classes that are needed for type checks.
Normally they should not be needed elsewhere.
"""

from _sumpf._base._connectors.baseconnectors import Connector, TypedConnector
from _sumpf._base._connectors.connectorproxy import ConnectorProxy

from _sumpf._data.channeldata import ChannelData

from _sumpf._modules._generators._signal.signalgenerator import SignalGenerator
from _sumpf._modules._generators._spectrum.spectrumgenerator import SpectrumGenerator

from _sumpf._modules._generators._spectrum.filtergenerator import FilterFunction

try:
    from _sumpf._modules._generators._signal.noisegenerator import Distribution
except ImportError:
    pass

try:
    from _sumpf._modules._generators._signal.windowgenerator import WindowFunction
except ImportError:
    pass

