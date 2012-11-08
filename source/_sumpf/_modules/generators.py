# SuMPF - Sound using a Monkeyforest-like processing framework
# Copyright (C) 2012 Jonas Schulte-Coerne
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

from ._generators.impulsegenerator import ImpulseGenerator
from ._generators.silencegenerator import SilenceGenerator
from ._generators.sinewavegenerator import SineWaveGenerator
from ._generators.squarewavegenerator import SquareWaveGenerator
from ._generators.sweepgenerator import SweepGenerator

from ._generators.filtergenerator import FilterGenerator

try:
	from ._generators.noisegenerator import NoiseGenerator
except ImportError:
	pass
try:
	from ._generators.windowgenerator import WindowGenerator
except ImportError:
	pass

