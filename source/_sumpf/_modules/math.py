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

from ._math.algebra import *
from ._math.statistics import *

from ._math.amplify import AmplifySignal, AmplifySpectrum
from ._math.average import AverageSignals, AverageSpectrums
from ._math.conjugatespectrum import ConjugateSpectrum
from ._math.differentiatesignal import DifferentiateSignal
from ._math.integratesignal import IntegrateSignal
from ._math.logarithmsignal import LogarithmSignal
from ._math.rectifysignal import RectifySignal

try:
    from ._math.convolvesignals import ConvolveSignals
except ImportError:
    pass
try:
    from ._math.correlatesignals import CorrelateSignals
except ImportError:
    pass
try:
    from ._math.fouriertransform import FourierTransform, InverseFourierTransform
except ImportError:
    pass
try:
    from ._math.resamplesignal import ResampleSignal
except ImportError:
    pass
try:
    from ._math.rootmeansquare import RootMeanSquare
except ImportError:
    pass
try:
    from ._math.shortfouriertransform import ShortFourierTransform
except ImportError:
    pass

