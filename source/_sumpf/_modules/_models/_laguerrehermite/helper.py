# SuMPF - Sound using a Monkeyforest-like processing framework
# Copyright (C) 2012-2014 Jonas Schulte-Coerne
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

from __future__ import print_function

import time
import sumpf

def get_powers_of_laguerre_representations(laguerred_input, order):
	print(time.ctime(), "  calculating the powers of the Laguerre functions")
	powers = []
	for c in range(len(laguerred_input.GetChannels())):
		channel = sumpf.modules.SplitSignal(data=laguerred_input, channels=[c]).GetOutput()
		powers.append([channel])
	for o in range(1, order):
		for p in powers:
			power = p[-1] * p[0]
			p.append(power)
	return powers

def get_permutations(nonlinear_order, max_linear_order):
	def recursion(order, minimum, maximum):
		result = []
		if order == 1:
			for i in range(minimum, maximum):
				result.append((i,))
		else:
			for i in range(minimum, maximum):
				lower = recursion(order=order - 1, minimum=i, maximum=maximum)
				for l in lower:
					result.append((i,) + l)
		return result
	return recursion(order=nonlinear_order, minimum=0, maximum=max_linear_order)

def normalize_permutation(permutation):
	normalized = {}
	for i in permutation:
		if i in normalized:
			normalized[i] += 1
		else:
			normalized[i] = 1
	return normalized

