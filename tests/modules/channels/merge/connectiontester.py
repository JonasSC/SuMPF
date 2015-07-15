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
        self.triggered = False
        self.samplingrate = 48000
        self.channels = [((1.0, 1.0, 1.0), (2.0, 2.0, 2.0)),
                         ((3.0, 3.0, 3.0), (4.0, 4.0, 4.0))]
        self.index = 0

    @sumpf.Trigger()
    def Trigger(self):
        self.triggered = True

    @sumpf.Trigger(["GetSignal", "GetSpectrum"])
    def ChangeChannels(self):
        self.index = 1 - self.index

    @sumpf.Output(sumpf.Signal)
    def GetSignal(self):
        return sumpf.Signal(channels=self.channels[self.index], samplingrate=self.samplingrate)

    @sumpf.Output(sumpf.Spectrum)
    def GetSpectrum(self):
        return sumpf.Spectrum(channels=self.channels[self.index], resolution=1.0 / self.samplingrate)

    @sumpf.Input(float, ["GetSignal", "GetSpectrum"])
    def SetSamplingRate(self, samplingrate):
        self.samplingrate = float(samplingrate)

