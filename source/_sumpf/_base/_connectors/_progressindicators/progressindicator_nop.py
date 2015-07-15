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

class ProgressIndicator_NOP(object):
    """
    This class emulates a ProgressIndicator. It is used as the default progress
    indicator in the Connectors, which is used, when the progress is not tracked.
    """
    def Announce(self, connector):
        """
        Does nothing.
        """
        pass

    def Report(self, connector):
        """
        Does nothing.
        """
        pass

nop_progress_indicator = ProgressIndicator_NOP()

