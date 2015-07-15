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

from ._signal.arbitrarysignalgenerator import ArbitrarySignalGenerator
from ._signal.constantsignalgenerator import ConstantSignalGenerator
from ._signal.impulsegenerator import ImpulseGenerator
from ._signal.laguerrefunctiongenerator import LaguerreFunctionGenerator
from ._signal.silencegenerator import SilenceGenerator
from ._signal.sinewavegenerator import SineWaveGenerator
from ._signal.squarewavegenerator import SquareWaveGenerator
from ._signal.sweepgenerator import SweepGenerator
from ._signal.trianglewavegenerator import TriangleWaveGenerator

try:
    from ._signal.noisegenerator import NoiseGenerator
except ImportError:
    pass
try:
    from ._signal.windowgenerator import WindowGenerator
except ImportError:
    pass

