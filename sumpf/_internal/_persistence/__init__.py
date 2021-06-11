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

"""Contains classes and functions, that implement saving data sets to files or loading them."""

from ._functions import *
from . import _filter_readers as filter_readers
from . import _filter_writers as filter_writers
from . import _signal_readers as signal_readers
from . import _signal_writers as signal_writers
from . import _spectrum_readers as spectrum_readers
from . import _spectrum_writers as spectrum_writers
from . import _spectrogram_readers as spectrogram_readers
from . import _spectrogram_writers as spectrogram_writers
