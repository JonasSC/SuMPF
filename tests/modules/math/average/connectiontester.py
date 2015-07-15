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

import sumpf


class ConnectionTester(object):
    def __init__(self):
        self.i = 0

    @sumpf.Input(int, ["GetSignal", "GetSpectrum"])
    def Start(self, index):
        self.i = index

    @sumpf.Output(sumpf.Signal)
    def GetSignal(self):
        return sumpf.Signal(channels=((1.0 * self.i, 2.0 * self.i, 3.0 * self.i),), samplingrate=42.0)

    @sumpf.Output(sumpf.Spectrum)
    def GetSpectrum(self):
        return sumpf.Spectrum(channels=((1.0 * self.i, 2.0 * self.i, 3.0 * self.i),), resolution=42.0)

