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

from .amplify import *
from .algebra import *
from .average import *
from .statistics import *

from .conjugatespectrum import TestConjugateSpectrum
from .convolvesignals import TestConvolveSignals
from .correlatesignals import TestCorrelateSignals
from .differentiatesignal import TestDifferentiateSignal
from .fouriertransform import TestFourierTransform
from .integratesignal import TestIntegrateSignal
from .logarithmsignal import TestLogarithmSignal
from .rectifysignal import TestRectifySignal
from .resamplesignal import TestResampleSignal
from .rootmeansquare import TestRootMeanSquare
from .shortfouriertransform import TestShortFourierTransform

