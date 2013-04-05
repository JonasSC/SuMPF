# SuMPF - Sound using a Monkeyforest-like processing framework
# Copyright (C) 2012-2013 Jonas Schulte-Coerne
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

from . import algebra
from . import signalalgebrabase


class AddSignals(signalalgebrabase.SignalAlgebra, algebra.Add):
	"""
	A module for adding two Signals.

	The input Signals must have the same length and sampling rate.
	If one Signal has more channels than the other, the surplus channels will be
	left out of the resulting Signal.

	The two input Signals will be added channel per channel and sample per sample:
		signal1 = sumpf.Signal(channels = ((1, 2), (3, 4)))
		signal2 = sumpf.Signal(channels = ((5, 6), (7, 8)))
		signal1 + signal2 == sumpf.Signal(channels=((1+5, 2+6), (3+7, 4+8)))
	"""
	pass



class SubtractSignals(signalalgebrabase.SignalAlgebra, algebra.Subtract):
	"""
	A module for subtracting two Signals.
	The second Signal will be subtracted from the first one.

	The input Signals must have the same length and sampling rate.
	If one Signal has more channels than the other, the surplus channels will be
	left out of the resulting Signal.

	The two input Signals will be subtracted channel per channel and sample per sample:
		signal1 = sumpf.Signal(channels = ((1, 2), (3, 4)))
		signal2 = sumpf.Signal(channels = ((5, 6), (7, 8)))
		signal1 - signal2 == sumpf.Signal(channels=((1-5, 2-6), (3-7, 4-8)))
	"""
	pass



class MultiplySignals(signalalgebrabase.SignalAlgebra, algebra.Multiply):
	"""
	A module for multiplying two Signals.

	The input Signals must have the same length and sampling rate.
	If one Signal has more channels than the other, the surplus channels will be
	left out of the resulting Signal.

	The two input Signals will be multiplied channel per channel and sample per sample:
		signal1 = sumpf.Signal(channels = ((1, 2), (3, 4)))
		signal2 = sumpf.Signal(channels = ((5, 6), (7, 8)))
		signal1 * signal2 == sumpf.Signal(channels=((1*5, 2*6), (3*7, 4*8)))
	"""
	pass



class DivideSignals(signalalgebrabase.SignalAlgebra, algebra.Divide):
	"""
	A module for dividing two Signals.
	The first Signal will be divided by the second one.

	The input Signals must have the same length and sampling rate.
	If one Signal has more channels than the other, the surplus channels will be
	left out of the resulting Signal.

	A ZeroDivisionError is raised only, if a non zero channel (not all samples
	are 0.0) is divided by a zero channel.
	If a zero channel is divided by another zero channel, the resulting channel
	will be a channel of which all samples are 1.0. This avoids ZeroDivisionErrors
	with empty Signals, which cannot always be avoided during the initialization
	of a processing chain.

	The two input Signals will be divided channel per channel and sample per sample:
		signal1 = sumpf.Signal(channels = ((1, 2), (3, 4)))
		signal2 = sumpf.Signal(channels = ((5, 6), (7, 8)))
		signal1 / signal2 == sumpf.Signal(channels=((1/5, 2/6), (3/7, 4/8)))
	"""
	pass



class CompareSignals(signalalgebrabase.SignalAlgebra, algebra.Compare):
	"""
	A comparator for two Signals.
	This works a bit like an open loop operational amplifier with the first Signal
	being connected to the +input and the second Signal to the -input. If the
	first input Signal is greater than the second Signal, the respective sample
	of the output Signal will be 1.0. If it is smaller, the sample will be -1.0.
	And wherever both input Signals have an equal value, the output will be 0.0.

	The input Signals must have the same length and sampling rate.
	If one Signal has more channels than the other, the surplus channels will be
	left out of the resulting Signal.

	The two input Signals will be compared channel per channel and sample per sample:
		signal1 = sumpf.Signal(channels = ((0, 2), (3, 4)))
		signal2 = sumpf.Signal(channels = ((1, 2), (2, 5)))
		compare(signal1, signal2) == sumpf.Signal(channels=((-1, 0), (1, -1)))
	"""
	pass

