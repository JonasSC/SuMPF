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

from .modules import *


def factory(playbackchannels=1, recordchannels=1):
    """
    A factory function that creates and returns an instance of an appropriate
    module that exchanges data with the sound card.
    @param playbackchannels: the number of channels for playback
    @param recordchannels: the number of channels for recording
    """
    if JACK_IS_AVAILABLE:
        import jack
        try:
            return JackIO(playbackchannels=playbackchannels, recordchannels=recordchannels)
        except jack.NotConnectedError:
            pass
    return DummyIO(playbackchannels=playbackchannels, recordchannels=recordchannels)

